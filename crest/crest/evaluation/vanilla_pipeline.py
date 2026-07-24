"""Phase 3.1: vanilla NL -> Llama -> FOL -> Prover9 pipeline.

Translates FOLIO premises + conclusion with LlamaHarness, grounds the result
with the same Prover9 grounder Phase 2.1 verified against gold FOL, and
classifies every example into the three-way bin (correct / loud failure /
silent failure) defined in silent_failure_metrics.py.

Default mode is "story" (prompt v2): the whole problem in one prompt,
matching standard practice (Logic-LM, LINC, FOLIO). The per-premise variant
(prompt v1) is retained as mode="per_premise" but is an ABLATION ONLY --
see the `mode` docstring in run_vanilla_pipeline for why reporting it as the
vanilla baseline would be measuring an artefact of our own design.

Per docs/MASTER_PLAN.md Phase 3.1: run on a 50-100 example subset first
(--limit 50) and sanity-check the output before scaling to the full
validation split (n=203). Use the default --sample random, not --sample
head: FOLIO is story-ordered, so a sequential slice clusters into very few
stories (first 50 = 18 stories vs 35 for a seeded random 50).

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
import random
import sys
import time
from pathlib import Path

# Windows consoles default to cp1252 and crash printing FOL symbols (∀, ∧).
# Guarded because this module also runs inside a Jupyter/Kaggle kernel, where
# sys.stdout is an ipykernel OutStream with no .reconfigure() -- an unguarded
# call there raises AttributeError at import time and kills the run.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Anchor every default path to the project root rather than the cwd -- this
# gets called both as `python -m` from crest/ and inline from a Kaggle
# notebook whose cwd is the repo root one level up, and a cwd-relative
# default silently wrote results to the wrong place in the second case.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from data.loaders.folio_loader import load_folio
from crest.inference.llama_harness import LlamaHarness, StoryFormatError
from crest.evaluation.silent_failure_metrics import (
    ClassifiedResult,
    classify_example,
    summarize,
)


def subsample(data, limit: int, strategy: str = "random", seed: int = 42):
    """Pick a `limit`-sized dev subset.

    FOLIO is ordered by story: consecutive examples share the same premises
    and differ only in their conclusion. Taking data[:limit] therefore gives a
    sample clustered into very few stories -- the first 5 validation examples
    cover just 2 stories, and 3 of them come from story 380, whose gold FOL
    Phase 2.1 already identified as malformed. Any prevalence measured that
    way is dominated by whichever handful of stories happens to sort first.

    "random" (default) samples across stories with a fixed seed, so the subset
    is representative *and* reproducible. "head" keeps the old sequential
    behaviour, useful only for quick plumbing checks where coverage is
    irrelevant.

    Note for later statistics: examples within a story are not independent
    (shared premises), so confidence intervals over these results should
    account for story-level clustering rather than treating n as n
    independent trials.
    """
    if strategy == "head":
        return data[:limit]
    if strategy != "random":
        raise ValueError(f"unknown sample strategy {strategy!r}; expected 'random' or 'head'")
    if limit >= len(data):
        return data
    rng = random.Random(seed)
    picked = rng.sample(range(len(data)), limit)
    # Keep dataset order so logs stay readable and diffable across runs.
    return [data[i] for i in sorted(picked)]


def run_vanilla_pipeline(
    split: str = "validation",
    limit: int = None,
    timeout: int = 60,
    log_path: str = None,
    out_path: str = None,
    harness: LlamaHarness = None,
    mode: str = "story",
    few_shot: bool = True,
    sample: str = "random",
    sample_seed: int = 42,
):
    """`harness` lets a caller pass an already-loaded LlamaHarness. Loading
    Llama-3.1-8B twice (once for a notebook smoke test, once here) wastes
    several GB of VRAM for no reason and risks OOM on a single T4 -- the
    Kaggle notebook loads it once and passes it in.

    `mode`:
      "story"       -- PRIMARY baseline (prompt v2). All premises plus the
                       conclusion in one prompt, matching standard practice
                       (Logic-LM, LINC, FOLIO).
      "per_premise" -- ABLATION ONLY (prompt v1). Each premise translated in
                       isolation. Do not report this as the vanilla
                       silent-failure prevalence: with no shared context the
                       model cannot keep predicate names consistent across
                       formulas, so it manufactures the very failure class
                       CREST claims to detect. Its legitimate use is the
                       contrast "inconsistency with vs. without context".
    """
    if mode not in ("story", "per_premise"):
        raise ValueError(f"unknown mode {mode!r}; expected 'story' or 'per_premise'")

    data = load_folio(split=split)
    if limit:
        data = subsample(data, limit, strategy=sample, seed=sample_seed)

    if log_path is None:
        log_path = PROJECT_ROOT / "experiments" / "logs" / "llama_harness_calls.jsonl"
    if harness is None:
        harness = LlamaHarness(log_path=str(log_path))

    classified = []
    records = []
    for i, ex in enumerate(data):
        start = time.time()
        format_error = None
        if mode == "story":
            try:
                translated_premises, translated_conclusion = harness.translate_story(
                    ex.premises, ex.conclusion, few_shot=few_shot
                )
            except StoryFormatError as e:
                # Unparseable output is a LOUD failure -- visibly broken
                # without needing the gold label -- but it's a different
                # cause than malformed FOL, so tag the stage rather than
                # letting it masquerade as an FOL syntax error.
                translated_premises, translated_conclusion = None, None
                format_error = e
        else:
            translated_premises = [harness.translate(p) for p in ex.premises]
            translated_conclusion = harness.translate(ex.conclusion)

        if format_error is not None:
            result = ClassifiedResult(
                example_id=ex.example_id,
                gold_label=ex.label,
                predicted_label=None,
                outcome="loud_failure",
                error=f"StoryFormatError: {format_error}",
                # Truncation is a harness budget problem, not a model
                # translation failure -- keep them in separate bins so a
                # misconfiguration can never inflate a reported rate.
                failure_stage=("translation_truncated"
                               if getattr(format_error, "truncated", False)
                               else "translation_format"),
            )
        else:
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
            "failure_stage": result.failure_stage,
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
    print(f"\n=== Vanilla pipeline on {split} (n={summary['n']}, mode={mode}) ===")
    print(f"correct: {summary['correct']} ({summary['accuracy']:.1%})")
    print(f"loud_failure: {summary['loud_failure']} ({summary['loud_failure_rate']:.1%})")
    print(f"  - translation_format:    {summary['loud_failure_translation_format']}")
    print(f"  - translation_truncated: {summary['loud_failure_translation_truncated']}"
          f"   (harness token budget, NOT a model error)")
    print(f"  - fol_parse:             {summary['loud_failure_fol_parse']}")
    print(f"silent_failure: {summary['silent_failure']} ({summary['silent_failure_rate']:.1%})")
    print(
        f"silent_failure_rate_excluding_loud: "
        f"{summary['silent_failure_rate_excluding_loud']:.1%} "
        f"(NOT the Phase 3.2 strict number -- see silent_failure_metrics.py)"
    )

    if out_path is None:
        suffix = f"_n{limit}" if limit else ""
        # Mode is in the filename: a "story" run and a "per_premise" ablation
        # of the same split are different experiments and must not overwrite
        # each other.
        shot = "fewshot" if few_shot else "zeroshot"
        out_path = (PROJECT_ROOT / "experiments" / "logs"
                    / f"vanilla_pipeline_{mode}_{shot}_{split}{suffix}.json")
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"split": split, "limit": limit, "mode": mode,
                   "few_shot": few_shot,
                   "sample": sample, "sample_seed": sample_seed,
                   "summary": summary, "results": records}, f, indent=2, ensure_ascii=False)
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
    parser.add_argument("--zero-shot", action="store_true",
                        help="ablation: use the v2 zero-shot prompt instead of v3 few-shot")
    parser.add_argument(
        "--sample", default="random", choices=["random", "head"],
        help="random = seeded representative subset across stories (default); "
             "head = first N sequentially, clustered into few stories",
    )
    parser.add_argument("--sample-seed", type=int, default=42)
    parser.add_argument(
        "--mode", default="story", choices=["story", "per_premise"],
        help="story = primary baseline (whole-story prompt); "
             "per_premise = ablation only, do not report as vanilla prevalence",
    )
    args = parser.parse_args()
    run_vanilla_pipeline(
        split=args.split,
        limit=args.limit,
        timeout=args.timeout,
        log_path=args.log_path,
        out_path=args.out_path,
        mode=args.mode,
        few_shot=not args.zero_shot,
        sample=args.sample,
        sample_seed=args.sample_seed,
    )
