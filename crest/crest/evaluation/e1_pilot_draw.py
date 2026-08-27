"""E1 pilot case draw -- executes the selection rule frozen in commit 89e821a.

The rule (three script-computable strata, seed `E1PILOT_001`, three distinct
documents, three distinct hypothesis templates) is specified in
`docs/PREREG_E1_formalizability.md` and was committed to git BEFORE this script
was written or run. That ordering is the point: it is what distinguishes a
preregistered draw from a hand-pick rationalised afterwards.

Nothing here may be re-run with a different seed, a different stratum
definition, or a "that one looks unsuitable" override. The output is the pilot
set. If the contract is later revised, the protocol requires a FRESH draw with
a NEW seed on cases not previously used -- not a re-roll of this one.

Run: python -m crest.evaluation.e1_pilot_draw
"""

import hashlib
import json
import random
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

SEED_STRING = "E1PILOT_001"

# The audit-10, fixed in contractnli_ceiling_probe.py. Pilot cases must not
# share a source document with any of these.
AUDIT_10 = ["165_nda-12", "49_nda-4", "227_nda-5", "23_nda-10", "30_nda-15",
            "493_nda-15", "48_nda-2", "446_nda-5", "46_nda-2", "564_nda-1"]

# Surface cues, exactly as frozen in the preregistration.
_DEONTIC = re.compile(r"\b(may|shall|must|permitted|entitled)\b", re.I)
_CONDITIONAL = re.compile(r"\b(if|unless|provided|subject to)\b", re.I)
_NEG_EXC = re.compile(r"\b(not|no|nothing|except|unless)\b", re.I)


def stratum_of(premise_text: str, gold: str) -> str:
    """S3 -> S2 -> S1 priority, making the strata mutually exclusive."""
    if _DEONTIC.search(premise_text) and _CONDITIONAL.search(premise_text):
        return "S3"
    if gold == "False" or _NEG_EXC.search(premise_text):
        return "S2"
    if gold == "True":
        return "S1"
    return "UNASSIGNED"


def main():
    from data.loaders.registry import load_dataset_by_name

    audit_docs = {c.rsplit("_", 1)[0] for c in AUDIT_10}
    train = load_dataset_by_name("contractnli", split="train")

    # Assert the disjointness the preregistration relies on rather than trust it.
    train_docs = {e.cluster_id for e in train}
    overlap = train_docs & audit_docs
    assert not overlap, f"train/audit document overlap: {sorted(overlap)}"
    print(f"eligibility check passed: {len(train)} train examples, "
          f"{len(train_docs)} documents, 0 shared with the audit-10")

    buckets = {"S1": [], "S2": [], "S3": []}
    for e in train:
        st = stratum_of(" ".join(e.premises), e.label)
        if st in buckets:
            buckets[st].append(e)
    for k in ("S3", "S2", "S1"):
        print(f"  {k}: {len(buckets[k])} eligible")

    # Seed derived from the frozen seed string, so the draw is reproducible
    # from the preregistration text alone.
    seed_int = int(hashlib.sha256(SEED_STRING.encode()).hexdigest()[:16], 16)

    picked, used_docs, used_hyps, notes = [], set(), set(), []
    for st in ("S3", "S2", "S1"):  # priority order, as frozen
        pool = sorted(buckets[st], key=lambda e: e.example_id)
        if not pool:
            notes.append(f"{st}: no eligible cases; fallback triggered")
            continue
        rng = random.Random(seed_int + sum(ord(c) for c in st))
        order = rng.sample(range(len(pool)), len(pool))
        chosen = None
        for idx in order:
            cand = pool[idx]
            if cand.cluster_id in used_docs or cand.hypothesis_id in used_hyps:
                continue  # distinctness constraint: skip to next in permutation
            chosen = cand
            break
        if chosen is None:
            notes.append(f"{st}: no case satisfied the distinctness constraint")
            continue
        picked.append((st, chosen))
        used_docs.add(chosen.cluster_id)
        used_hyps.add(chosen.hypothesis_id)

    print("\n" + "=" * 78)
    print("E1 PILOT SET -- drawn under the rule frozen in commit 89e821a")
    print("=" * 78)
    out = []
    for st, e in picked:
        print(f"\n[{st}]  example_id = {e.example_id}   (document {e.cluster_id}, "
              f"hypothesis {e.hypothesis_id})")
        for i, prem in enumerate(e.premises, 1):
            print(f"    P{i}: {' '.join(prem.split())[:220]}")
        print(f"    C : {e.conclusion}")
        out.append({
            "stratum": st, "example_id": e.example_id,
            "document": e.cluster_id, "hypothesis_template": e.hypothesis_id,
            "premises": e.premises, "conclusion": e.conclusion,
            # Gold label is recorded here for the RESULTS side only. It must be
            # stripped before anything reaches a formalizer -- see the
            # instruction-sheet builder.
            "gold_label_DO_NOT_SHOW_ANNOTATORS": e.label,
        })

    if notes:
        print("\nFallback notes:", *notes, sep="\n  ")

    payload = {
        "seed_string": SEED_STRING,
        "rule_frozen_in_commit": "89e821a",
        "distinct_documents": sorted(used_docs),
        "distinct_hypothesis_templates": sorted(used_hyps),
        "fallback_notes": notes,
        "cases": out,
    }
    dest = PROJECT_ROOT / "annotation" / "e1_pilot_cases.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {dest}")
    print("This set is final. Re-running with a different seed is a protocol violation.")


if __name__ == "__main__":
    main()
