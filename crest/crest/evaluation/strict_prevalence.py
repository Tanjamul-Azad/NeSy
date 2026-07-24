"""Phase 3.2: strict silent-failure prevalence.

Phase 3.1 reports the raw three-way bin over every example. That number
conflates two different things, because an example can be "wrong" for
reasons that have nothing to do with the LLM's translation:

  - FOLIO's gold FOL is itself malformed (60/203 of the validation split),
    so the gold LABEL derived from it is unreliable; or
  - the gold FOL is well-formed but our grounder still disagrees with the
    gold label (27/203), meaning either FOLIO's annotation or our grounding
    is wrong for that example.

Phase 3.2's pre-registered definition (docs/MASTER_PLAN.md) is to count only
among examples where gold-FOL grounding was ALREADY VERIFIED CORRECT in
Phase 2.1 -- i.e. `malformed_gold_fol == False and match == True` in
ceiling_check_validation.json. On those examples the label is as trustworthy
as this dataset allows, so a disagreement is attributable to the LLM's
translation rather than to dataset noise.

This tightens the denominator; it does not change any per-example verdict.

Severity split (added 2026-07-24 after reading the n=203 results): silent
failures are NOT homogeneous, and reporting one aggregate number overclaims.
  - under_determination: gold is True/False but the pipeline predicted
    Uncertain. The translated FOL lost logical content, so the solver could
    not derive the conclusion either way. Still a genuine error -- FOLIO's
    "Uncertain" is a real label, and asserting it is a definite claim, not an
    abstention -- but it is a *degradation*, not a confident falsehood.
  - wrong_direction: the pipeline asserted a definite answer that contradicts
    gold (True<->False), or asserted a definite answer where gold is
    Uncertain. This is the failure the project's motivation is actually built
    on: the solver accepts the FOL and confidently returns the wrong
    conclusion with no error signal.
Report both. Collapsing them into a single "silent failure rate" is the kind
of overclaim a reviewer will (correctly) attack.

Run: python -m crest.evaluation.strict_prevalence
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

LOGS = PROJECT_ROOT / "experiments" / "logs"


def load_verified_ids(ceiling_path: Path) -> set:
    """example_ids whose gold FOL grounded to the gold label in Phase 2.1."""
    data = json.loads(ceiling_path.read_text(encoding="utf-8"))
    return {
        str(r["example_id"])
        for r in data["results"]
        if not r["malformed_gold_fol"] and r["match"]
    }


def classify_severity(record: dict) -> str:
    if record["outcome"] != "silent_failure":
        return None
    if record["gold_label"] in ("True", "False") and record["predicted_label"] == "Uncertain":
        return "under_determination"
    return "wrong_direction"


def strict_prevalence(vanilla_path: Path, ceiling_path: Path) -> dict:
    vanilla = json.loads(vanilla_path.read_text(encoding="utf-8"))
    verified = load_verified_ids(ceiling_path)

    all_records = vanilla["results"]
    kept = [r for r in all_records if str(r["example_id"]) in verified]

    def bins(records):
        n = len(records)
        correct = sum(r["outcome"] == "correct" for r in records)
        loud = sum(r["outcome"] == "loud_failure" for r in records)
        silent = sum(r["outcome"] == "silent_failure" for r in records)
        under = sum(classify_severity(r) == "under_determination" for r in records)
        wrong = sum(classify_severity(r) == "wrong_direction" for r in records)
        gradeable = n - loud
        return {
            "n": n,
            "correct": correct,
            "loud_failure": loud,
            "silent_failure": silent,
            "silent_under_determination": under,
            "silent_wrong_direction": wrong,
            "gradeable": gradeable,
            "accuracy_all": correct / n if n else 0.0,
            "accuracy_gradeable": correct / gradeable if gradeable else 0.0,
            "silent_rate_all": silent / n if n else 0.0,
            "silent_rate_gradeable": silent / gradeable if gradeable else 0.0,
            "under_determination_rate_gradeable": under / gradeable if gradeable else 0.0,
            "wrong_direction_rate_gradeable": wrong / gradeable if gradeable else 0.0,
        }

    return {
        "vanilla_file": vanilla_path.name,
        "ceiling_file": ceiling_path.name,
        "phase_3_1_all_examples": bins(all_records),
        "phase_3_2_strict_verified_gold_only": bins(kept),
        "n_verified_gold": len(verified),
        "n_dropped_by_strict_filter": len(all_records) - len(kept),
    }


def _print_block(title: str, b: dict) -> None:
    print(f"--- {title} ---")
    print(f"  n = {b['n']}   (gradeable, i.e. non-loud: {b['gradeable']})")
    print(f"  correct         {b['correct']:3d}   accuracy_all={b['accuracy_all']:.1%}  "
          f"accuracy_gradeable={b['accuracy_gradeable']:.1%}")
    print(f"  loud_failure    {b['loud_failure']:3d}")
    print(f"  silent_failure  {b['silent_failure']:3d}   "
          f"rate_all={b['silent_rate_all']:.1%}  rate_gradeable={b['silent_rate_gradeable']:.1%}")
    print(f"     under_determination (True/False -> Uncertain): "
          f"{b['silent_under_determination']:3d}  ({b['under_determination_rate_gradeable']:.1%} of gradeable)")
    print(f"     wrong_direction (confidently wrong)          : "
          f"{b['silent_wrong_direction']:3d}  ({b['wrong_direction_rate_gradeable']:.1%} of gradeable)")
    print()


def main():
    ceiling = LOGS / "ceiling_check_validation.json"
    vanilla = LOGS / "vanilla_pipeline_story_fewshot_validation.json"
    if not ceiling.exists() or not vanilla.exists():
        raise SystemExit(
            f"Missing input(s). Need both:\n  {ceiling}\n  {vanilla}\n"
            "Run ceiling_check.py locally and fetch the Kaggle vanilla results first."
        )

    out = strict_prevalence(vanilla, ceiling)
    print(f"=== Phase 3.2: strict silent-failure prevalence ===")
    print(f"vanilla: {out['vanilla_file']}")
    print(f"ceiling: {out['ceiling_file']}")
    print(f"examples with verified-correct gold grounding: {out['n_verified_gold']}")
    print(f"dropped by the strict filter: {out['n_dropped_by_strict_filter']}")
    print()
    _print_block("Phase 3.1 (all examples)", out["phase_3_1_all_examples"])
    _print_block("Phase 3.2 (STRICT: verified gold only)",
                 out["phase_3_2_strict_verified_gold_only"])

    out_path = LOGS / "strict_prevalence_validation.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
