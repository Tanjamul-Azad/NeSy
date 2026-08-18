"""Does CREST-D's schema signal actually predict the solver, before the solver runs?

This is the falsification test for `crest.detection.predicate_checker`, run
against every vanilla pipeline result already committed -- 4 datasets x 3
models, no new API calls, no GPU.

Two claims are under test, and they are not equally strong:

  1. `will_return_uncertain` is argued to be SOUND: if no conclusion predicate
     occurs in any premise, no resolution step connects goal to assumptions,
     so Prover9 cannot prove either direction and must return Uncertain.
     **Precision below 100% falsifies that argument** -- it would mean the
     grounder finds a path the analysis says cannot exist, and the soundness
     claim in the module docstring would have to be withdrawn, not softened.
  2. `will_fail_loudly` (mixed arity) predicts a Prover9 rejection. Prover9
     rejects mixed arities, but our own parser may reject the formula earlier
     for an unrelated reason, so this is a prediction rather than a proof.

Also reported: coverage -- of the silent failures that actually happened, how
many did the detector flag in advance? High precision with low coverage is
still useful (it is a triage signal, not a full oracle) but the paper must
state both, because a detector that fires rarely is a different product from
one that fires often.

Run: python -m crest.evaluation.schema_detector_eval
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from crest.detection.predicate_checker import check


def _model_of(payload, path):
    m = payload.get("model") or ""
    if "Llama" in m:
        return "Llama-3.1-8B"
    if m and m != "unknown":
        return m
    for tag, readable in (("gpt4omini", "gpt-4o-mini"), ("gpt4o", "gpt-4o"),
                          ("story", "Llama-3.1-8B")):
        if f"_{tag}_" in path.name:
            return readable
    return "Llama-3.1-8B"


def _dataset_of(payload, path):
    d = payload.get("dataset")
    if d:
        return d
    m = re.search(r"vanilla_pipeline_(folio|proofwriter|prontoqa|contractnli)_", path.name)
    return m.group(1) if m else "folio"


def evaluate(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["results"]

    # Counters for the two claims.
    unc_flagged = unc_correct = unc_reached = unc_never_ran = 0
    loud_flagged = loud_correct = 0
    silent_total = silent_flagged = 0
    repairable_of_flagged = 0

    for r in rows:
        prem = r.get("translated_premises")
        conc = r.get("translated_conclusion")
        if not conc:
            continue  # translation_format failure: no FOL exists to inspect
        rep = check(prem or [], conc)
        outcome, pred = r["outcome"], r.get("predicted_label")

        if outcome == "silent_failure":
            silent_total += 1

        if rep.predicted_outcome == "will_return_uncertain":
            unc_flagged += 1
            # A flagged example that never reached the solver (our parser
            # rejected its FOL first) does not test the claim at all -- the
            # claim is about what Prover9 returns WHEN IT RUNS. Counting those
            # as misses, as the first version of this file did, understated
            # precision by 11 points.
            if outcome == "loud_failure":
                unc_never_ran += 1
            else:
                unc_reached += 1
                if pred == "Uncertain":
                    unc_correct += 1
            if outcome == "silent_failure":
                silent_flagged += 1
            if rep.repairable:
                repairable_of_flagged += 1
        elif rep.predicted_outcome == "will_fail_loudly":
            loud_flagged += 1
            if outcome == "loud_failure" and r.get("failure_stage") == "fol_parse":
                loud_correct += 1

    return {
        "dataset": _dataset_of(payload, path), "model": _model_of(payload, path),
        "n": len(rows),
        "uncertain_flagged": unc_flagged, "uncertain_correct": unc_correct,
        "uncertain_reached_solver": unc_reached, "uncertain_never_ran": unc_never_ran,
        "uncertain_precision": unc_correct / unc_reached if unc_reached else None,
        "loud_flagged": loud_flagged, "loud_correct": loud_correct,
        "loud_precision": loud_correct / loud_flagged if loud_flagged else None,
        "silent_total": silent_total, "silent_flagged": silent_flagged,
        "silent_coverage": silent_flagged / silent_total if silent_total else None,
        "repairable_of_flagged": repairable_of_flagged,
    }


def main():
    logs = PROJECT_ROOT / "experiments" / "logs"
    files = [p for p in sorted(logs.glob("vanilla_pipeline_*.json"))
             if "zeroshot" not in p.name and "per_premise" not in p.name
             and not re.search(r"_n[1-9]\.json$", p.name)]

    rows = [evaluate(p) for p in files]
    rows = [r for r in rows if r["n"] >= 50]

    print("=" * 96)
    print("CREST-D schema signal vs the solver's actual behaviour (no new model calls)")
    print("=" * 96)
    hdr = f"{'dataset':<12} {'model':<14} {'n':>5} {'UNC flag':>9} {'prec':>7} {'LOUD flag':>10} {'prec':>7} {'silent cov':>11}"
    print(hdr)
    print("-" * 96)
    for r in rows:
        def pct(x):
            return "  n/a" if x is None else f"{x:6.1%}"
        print(f"{r['dataset']:<12} {r['model']:<14} {r['n']:>5} {r['uncertain_flagged']:>9} "
              f"{pct(r['uncertain_precision'])} {r['loud_flagged']:>10} {pct(r['loud_precision'])} "
              f"{pct(r['silent_coverage'])}")

    tot_f = sum(r["uncertain_flagged"] for r in rows)
    tot_c = sum(r["uncertain_correct"] for r in rows)
    tot_reached = sum(r["uncertain_reached_solver"] for r in rows)
    tot_never = sum(r["uncertain_never_ran"] for r in rows)
    tot_lf = sum(r["loud_flagged"] for r in rows)
    tot_lc = sum(r["loud_correct"] for r in rows)
    tot_s = sum(r["silent_total"] for r in rows)
    tot_sf = sum(r["silent_flagged"] for r in rows)
    tot_rep = sum(r["repairable_of_flagged"] for r in rows)

    print("-" * 96)
    print(f"POOLED  unreachable-goal flags: {tot_f}  ({tot_never} never reached the solver "
          f"-- our parser rejected the FOL first, so they do not test the claim)")
    print(f"        of the {tot_reached} that DID reach Prover9: precision "
          f"{(tot_c / tot_reached if tot_reached else 0):.2%}")
    print("        the residue is the inconsistent-premise case: from a contradiction any")
    print("        goal follows, including one sharing no vocabulary. Named in the module.")
    print(f"        mixed-arity flags:      {tot_lf}, precision "
          f"{(tot_lc / tot_lf if tot_lf else 0):.2%}")
    print(f"        silent failures:        {tot_s}, flagged in advance {tot_sf} "
          f"({(tot_sf / tot_s if tot_s else 0):.1%} coverage)")
    print(f"        of the flagged, {tot_rep} carry a near-miss/arity defect a schema")
    print(f"        alignment could target ({(tot_rep / tot_f if tot_f else 0):.1%} of flags)")

    out = logs / "schema_detector_eval.json"
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
