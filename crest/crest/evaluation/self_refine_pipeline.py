"""Phase 4 runner: Self-Refine vs vanilla on identical examples.

Produces the single comparison docs/MASTER_PLAN.md calls the most important
of Month 1. Reports the paired, per-example transition matrix, not just two
aggregate rates, because a baseline that repairs 6 examples and breaks 6 has
no effect and "repaired 6" alone would be a dishonest way to describe it.

Run on Kaggle (needs the GPU): imported by the notebook, or
    python -m crest.evaluation.self_refine_pipeline --limit 50
"""

import json
import sys
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from data.loaders.folio_loader import load_folio
from crest.inference.llama_harness import LlamaHarness
from crest.baselines.self_refine import run_self_refine, SELF_REFINE_VERSION
from crest.evaluation.silent_failure_metrics import (
    ClassifiedResult,
    classify_example,
    summarize,
)
from crest.evaluation.vanilla_pipeline import subsample


def _severity(gold, predicted, outcome):
    if outcome != "silent_failure":
        return None
    if gold in ("True", "False") and predicted == "Uncertain":
        return "under_determination"
    return "wrong_direction"


def run(
    split: str = "validation",
    limit: int = None,
    timeout: int = 30,
    max_rounds: int = 2,
    harness: LlamaHarness = None,
    sample: str = "random",
    sample_seed: int = 42,
    out_path: str = None,
):
    data = load_folio(split=split)
    if limit:
        data = subsample(data, limit, strategy=sample, seed=sample_seed)

    if harness is None:
        harness = LlamaHarness(
            log_path=str(PROJECT_ROOT / "experiments" / "logs" / "llama_harness_calls.jsonl")
        )

    refined_classified, vanilla_classified, records = [], [], []

    for i, ex in enumerate(data):
        start = time.time()
        sr = run_self_refine(harness, ex.premises, ex.conclusion, max_rounds=max_rounds)

        # Score BOTH the round-0 output and the refined output on the same
        # example, in the same process. This is the paired comparison: it
        # removes any doubt about the two arms seeing different inputs.
        def _score(p_fol, c_fol, err):
            if err is not None or p_fol is None:
                return ClassifiedResult(
                    example_id=ex.example_id, gold_label=ex.label,
                    predicted_label=None, outcome="loud_failure",
                    error=err, failure_stage="translation_format",
                )
            return classify_example(
                example_id=ex.example_id, premises_fol=p_fol,
                conclusion_fol=c_fol, gold_label=ex.label, timeout=timeout,
            )

        van = _score(sr.initial_premises_fol, sr.initial_conclusion_fol, sr.initial_error)
        ref = _score(sr.premises_fol, sr.conclusion_fol, sr.initial_error)
        vanilla_classified.append(van)
        refined_classified.append(ref)

        elapsed = time.time() - start
        records.append({
            "example_id": ex.example_id,
            "story_id": ex.story_id,
            "gold_label": ex.label,
            "vanilla_predicted": van.predicted_label,
            "vanilla_outcome": van.outcome,
            "vanilla_severity": _severity(ex.label, van.predicted_label, van.outcome),
            "refined_predicted": ref.predicted_label,
            "refined_outcome": ref.outcome,
            "refined_severity": _severity(ex.label, ref.predicted_label, ref.outcome),
            "changed_from_initial": sr.changed_from_initial,
            "n_rounds_run": sr.n_rounds_run,
            "stopped_no_issues": any(r.stopped_no_issues for r in sr.rounds),
            "initial_premises_fol": sr.initial_premises_fol,
            "initial_conclusion_fol": sr.initial_conclusion_fol,
            "refined_premises_fol": sr.premises_fol,
            "refined_conclusion_fol": sr.conclusion_fol,
            "rounds": [asdict(r) for r in sr.rounds],
            "elapsed_sec": round(elapsed, 2),
        })
        print(f"[{i+1}/{len(data)}] id={ex.example_id} gold={ex.label} "
              f"vanilla={van.outcome}/{van.predicted_label} -> "
              f"refined={ref.outcome}/{ref.predicted_label} "
              f"changed={sr.changed_from_initial} rounds={sr.n_rounds_run} ({elapsed:.1f}s)")

    van_sum = summarize(vanilla_classified)
    ref_sum = summarize(refined_classified)

    transitions = Counter(
        (r["vanilla_outcome"], r["refined_outcome"]) for r in records
    )
    helped = sum(n for (a, b), n in transitions.items()
                 if a != "correct" and b == "correct")
    hurt = sum(n for (a, b), n in transitions.items()
               if a == "correct" and b != "correct")

    def sev_counts(recs, key):
        return dict(Counter(r[key] for r in recs if r[key]))

    print()
    print("=" * 66)
    print(f"PHASE 4 FALSIFICATION GATE -- Self-Refine vs vanilla "
          f"(n={len(records)}, max_rounds={max_rounds})")
    print("=" * 66)
    for name, s in (("vanilla (round 0)", van_sum), ("self-refine", ref_sum)):
        grade = s["n"] - s["loud_failure"]
        print(f"  {name:18s}  correct={s['correct']:3d}  loud={s['loud_failure']:3d}  "
              f"silent={s['silent_failure']:3d}   "
              f"acc_gradeable={s['correct']/grade if grade else 0:.1%}  "
              f"silent_gradeable={s['silent_failure']/grade if grade else 0:.1%}")
    print()
    print(f"  severity vanilla    : {sev_counts(records, 'vanilla_severity')}")
    print(f"  severity self-refine: {sev_counts(records, 'refined_severity')}")
    print()
    print(f"  examples changed by refinement: "
          f"{sum(r['changed_from_initial'] for r in records)}/{len(records)}")
    print(f"  critique said NO_ISSUES at some round: "
          f"{sum(r['stopped_no_issues'] for r in records)}/{len(records)}")
    print()
    print(f"  HELPED (non-correct -> correct): {helped}")
    print(f"  HURT   (correct -> non-correct): {hurt}")
    print(f"  NET                            : {helped - hurt:+d}")
    print()
    print("  transition matrix (vanilla -> self-refine):")
    for (a, b), n in sorted(transitions.items(), key=lambda kv: -kv[1]):
        arrow = "  <-- unchanged" if a == b else ""
        print(f"    {a:15s} -> {b:15s}: {n:3d}{arrow}")

    payload = {
        "version": SELF_REFINE_VERSION,
        "split": split, "limit": limit, "max_rounds": max_rounds,
        "sample": sample, "sample_seed": sample_seed,
        "vanilla_summary": van_sum,
        "self_refine_summary": ref_sum,
        "helped": helped, "hurt": hurt, "net": helped - hurt,
        "transitions": {f"{a}->{b}": n for (a, b), n in transitions.items()},
        "results": records,
    }
    if out_path is None:
        suffix = f"_n{limit}" if limit else ""
        out_path = (PROJECT_ROOT / "experiments" / "logs"
                    / f"self_refine_{split}{suffix}.json")
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out_file}")
    return payload


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="validation", choices=["train", "validation"])
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-rounds", type=int, default=2)
    parser.add_argument("--sample", default="random", choices=["random", "head"])
    parser.add_argument("--sample-seed", type=int, default=42)
    args = parser.parse_args()
    run(split=args.split, limit=args.limit, timeout=args.timeout,
        max_rounds=args.max_rounds, sample=args.sample, sample_seed=args.sample_seed)
