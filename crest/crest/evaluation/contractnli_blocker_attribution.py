"""Step 5: how much of the ContractNLI failure is the one blocker CREST could fix?

The ceiling probe named five reasons a *correct* formalisation still fails to
derive ContractNLI's gold label. Only one of them -- blocker 5, the
hypothesis and the clause using disconnected predicate vocabularies
(`GrantsRights(x)` vs `GrantsRight(agreement, receivingParty, ...)`) -- is a
translation-level defect, and therefore the only one a detect-and-repair layer
over NL->FOL could address. The other four are absent input or formalism
mismatch.

That split was an argument. This module turns it into a number, using a check
that needs no hand annotation and no gold FOL:

    A conclusion predicate that appears NOWHERE in the premises cannot
    participate in any derivation. If the conclusion's predicates are wholly
    disjoint from the premises', the proof was unreachable from the moment
    the translation was written -- regardless of how good the rest of it is.

This is a sound but INCOMPLETE test, and both halves of that matter:

  - Sound: full disjointness genuinely guarantees non-derivability (with no
    shared predicate there is no resolution step connecting goal to
    assumptions; equality reasoning over constants cannot bridge it either,
    since our grounder introduces no equality axioms).
  - Incomplete: partial overlap does NOT imply derivability. A formula can
    share every predicate and still fail for any of the other four blockers,
    or for an ordinary translation bug. So the disjoint count is a LOWER
    BOUND on vocabulary-driven failure, and the overlap count is an UPPER
    bound on what CREST could conceivably repair -- not a target it would hit.

Reported per model, over gradeable (non-loud) failures only.

Run: python -m crest.evaluation.contractnli_blocker_attribution
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

# A predicate application: a capitalised identifier immediately followed by
# "(". Deliberately case-sensitive -- our prompt's convention is Predicate(...)
# with lowerCamelCase constants, so a lowercase identifier before "(" is a
# constant or a malformed term, not a predicate.
_PRED_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s*\(")


def predicates(formula: str) -> set:
    return set(_PRED_RE.findall(formula or ""))


def analyse(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    model = payload.get("model", path.stem)
    if "Llama" in model:
        model = "Llama-3.1-8B"

    disjoint, overlap, examples = 0, 0, []
    for r in payload["results"]:
        if r["outcome"] != "silent_failure":
            continue
        prem = set()
        for f in (r.get("translated_premises") or []):
            prem |= predicates(f)
        conc = predicates(r.get("translated_conclusion") or "")
        if not conc:
            continue
        shared = conc & prem
        if not shared:
            disjoint += 1
            if len(examples) < 3:
                examples.append({
                    "example_id": r["example_id"],
                    "conclusion_predicates": sorted(conc),
                    "premise_predicates": sorted(prem)[:6],
                })
        else:
            overlap += 1

    total = disjoint + overlap
    return {
        "model": model, "file": path.name,
        "n_silent_analysed": total,
        "disjoint_vocabulary": disjoint,
        "shares_some_vocabulary": overlap,
        "disjoint_rate": disjoint / total if total else 0.0,
        "examples": examples,
    }


def main():
    logs = PROJECT_ROOT / "experiments" / "logs"
    files = sorted(logs.glob("vanilla_pipeline_contractnli_*_test_n100.json"))
    if not files:
        print("No ContractNLI pilot runs found.")
        return

    order = {"Llama-3.1-8B": 0, "gpt-4o-mini": 1, "gpt-4o": 2}
    rows = sorted((analyse(p) for p in files), key=lambda r: order.get(r["model"], 9))

    print("=" * 78)
    print("ContractNLI: is the failure vocabulary disconnect (CREST-addressable)")
    print("or something a translation repair layer cannot touch?")
    print("=" * 78)
    print("Counted over silent failures only. Disjoint = no conclusion predicate")
    print("appears in any premise, so no derivation was ever possible.\n")

    for r in rows:
        print(f"--- {r['model']}   (silent failures analysed: {r['n_silent_analysed']})")
        print(f"    conclusion vocabulary DISJOINT from premises: "
              f"{r['disjoint_vocabulary']} ({r['disjoint_rate']:.1%})")
        print(f"    shares at least one predicate:                "
              f"{r['shares_some_vocabulary']} ({1 - r['disjoint_rate']:.1%})")
        for ex in r["examples"]:
            print(f"      e.g. {ex['example_id']}: conclusion uses "
                  f"{ex['conclusion_predicates']}, premises use "
                  f"{ex['premise_predicates']}...")
        print()

    print("READING THIS HONESTLY:")
    print("  The disjoint count is a LOWER bound on vocabulary-driven failure -- those")
    print("  cases are unreachable by construction, and a schema-alignment repair is")
    print("  exactly the intervention that would help them.")
    print("  The remainder is an UPPER bound on what else CREST might fix, NOT a set it")
    print("  would succeed on: sharing a predicate does not make a conclusion derivable,")
    print("  and the other four blockers (missing obligation, open-world permission,")
    print("  absent world-knowledge witness, missing deontic bridge) live in that group")
    print("  alongside ordinary translation bugs. Separating those needs hand analysis.")

    out = logs / "contractnli_blocker_attribution.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
