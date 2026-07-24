"""Phase 3.1: vanilla NL -> Llama -> FOL -> Prover9 pipeline.

Runs FOLIO premises/conclusion through LlamaHarness's frozen Phase 1.1
prompt (one sentence in, one FOL formula out -- each premise and the
conclusion are translated independently, there's no separate "conclusion"
prompt) and grounds the result with the same Prover9 grounder Phase 2.1
verified against gold FOL. Classifies every example into the three-way bin
(correct / loud failure / silent failure) defined in silent_failure_metrics.py.

Per docs/MASTER_PLAN.md Phase 3.1: run on a 50-100 example subset first
(--limit 50) and sanity-check the output before scaling to the full
validation split (n=203).

**Needs a GPU** (LlamaHarness loads Llama-3.1-8B-Instruct in 4-bit via
bitsandbytes) -- run this on Kaggle via
crest/scripts/kaggle_kernel/crest_kaggle.ipynb, not locally on Windows.
4-bit loading segfaulted reproducibly on the local Windows box (Phase 1.1);
that's why compute moved to Kaggle in the first place. Kaggle is Linux, so
the grounder's `get_prover9()` picks the native LinuxProver9 path there
automatically -- no WSL involved, see fol_to_prover9.py.

This is Phase 3.1 only: the raw three-way bin. Phase 3.2's *strict* silent-
failure prevalence (restricted to examples where gold-FOL grounding was
already verified correct in Phase 2.1) is a separate join against
experiments/logs/ceiling_check_validation.json, done in a later script --
see the NOTE in silent_failure_metrics.py.
"""

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Anchor every default path to the project root rather than the cwd -- this
# gets called both as `python -m` from crest/ and inline from a Kaggle
# notebook whose cwd is the repo root one level up, and a cwd-relative
# default silently wrote results to the wrong place in the second case.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from data.loaders.folio_loader import load_folio
from crest.inference.llama_harness import LlamaHarness
from crest.evaluation.silent_failure_metrics import classify_example, summarize


def run_vanilla_pipeline(
    split: str = "validation",
    limit: int = None,
    timeout: int = 60,
    log_path: str = None,
    out_path: str = None,
    harness: LlamaHarness = None,
):
    """`harness` lets a caller pass an already-loaded LlamaHarness. Loading
    Llama-3.1-8B twice (once for a notebook smoke test, once here) wastes
    several GB of VRAM for no reason and risks OOM on a single T4 -- the
    Kaggle notebook loads it once and passes it in.
    """
    data = load_folio(split=split)
    if limit:
        data = data[:limit]

    if log_path is None:
        log_path = PROJECT_ROOT / "experiments" / "logs" / "llama_harness_calls.jsonl"
    if harness is None:
        harness = LlamaHarness(log_path=str(log_path))

    classified = []
    records = []
    for i, ex in enumerate(data):
        start = time.time()
        # Translate each premise independently, then the conclusion, through
        # the same single-sentence NL->FOL prompt (Phase 1.1) -- mirrors how
        # FOLIO's own gold premises-FOL is one formula per premise line.
        translated_premises = [harness.translate(p) for p in ex.premises]
        translated_conclusion = harness.translate(ex.conclusion)

        result = classify_example(
            example_id=ex.example_id,
            premises_fol=translated_premises,
            conclusion_fol=translated_conclusion,
            gold_label=ex.label,
            timeout=timeout,
        )
        classified.append(result)

        elapsed = time.time() - start
        record = {
            "example_id": ex.example_id,
            "story_id": ex.story_id,
            "gold_label": ex.label,
            "predicted_label": result.predicted_label,
            "outcome": result.outcome,
            "error": result.error,
            "translated_premises": translated_premises,
            "translated_conclusion": translated_conclusion,
            "elapsed_sec": round(elapsed, 2),
        }
        records.append(record)
        print(
            f"[{i+1}/{len(data)}] example_id={ex.example_id} gold={ex.label} "
            f"predicted={result.predicted_label} outcome={result.outcome} ({elapsed:.1f}s)"
        )

    summary = summarize(classified)
    print(f"\n=== Vanilla pipeline on {split} (n={summary['n']}) ===")
    print(f"correct: {summary['correct']} ({summary['accuracy']:.1%})")
    print(f"loud_failure: {summary['loud_failure']} ({summary['loud_failure_rate']:.1%})")
    print(f"silent_failure: {summary['silent_failure']} ({summary['silent_failure_rate']:.1%})")
    print(
        f"silent_failure_rate_excluding_loud: "
        f"{summary['silent_failure_rate_excluding_loud']:.1%} "
        f"(NOT the Phase 3.2 strict number -- see silent_failure_metrics.py)"
    )

    if out_path is None:
        suffix = f"_n{limit}" if limit else ""
        out_path = PROJECT_ROOT / "experiments" / "logs" / f"vanilla_pipeline_{split}{suffix}.json"
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"split": split, "limit": limit, "summary": summary, "results": records}, f, indent=2, ensure_ascii=False)
    print(f"Full results written to {out_file}")

    return summary, records


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="validation", choices=["train", "validation"])
    parser.add_argument("--limit", type=int, default=50, help="Phase 3.1: start with a 50-100 example subset")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--log-path", default=None)
    parser.add_argument("--out-path", default=None)
    args = parser.parse_args()
    run_vanilla_pipeline(
        split=args.split,
        limit=args.limit,
        timeout=args.timeout,
        log_path=args.log_path,
        out_path=args.out_path,
    )
