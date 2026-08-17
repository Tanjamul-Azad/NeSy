"""Phase 3.3 + 4.2 in one pass, on a strong proprietary model.

One script answers both open high-severity threats from Phase 4:

  3.3  Does silent failure persist at higher model capability, or is it a
       weak-model artefact?
  4.2  Does Self-Refine close the gap when the critic is actually competent?
       (Phase 4 found it net-harmful on Llama-3.1-8B, but published work
       reports small models cannot self-correct, so that result may be about
       scale rather than about the task.)

Runs LOCALLY -- no GPU, no Kaggle. Uses the same prompts, the same parser and
the same Prover9 grounder as every previous phase, by importing rather than
copying them.

Requires OPENAI_API_KEY in the environment. The key is never logged or
written to any output file.

Usage:
    python scripts/run_gpt4o_phases.py --model gpt-4o-mini --limit 50 --phase both
    python scripts/run_gpt4o_phases.py --model gpt-4o --limit 203 --phase vanilla
"""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from crest.inference.openai_harness import OpenAIHarness, PRICING_PER_1M
from crest.evaluation.vanilla_pipeline import run_vanilla_pipeline
from crest.evaluation import self_refine_pipeline

# Rough per-example token costs, measured from the Llama runs. Used only for
# the pre-flight estimate; the harness reports actual spend as it goes.
EST_TOKENS = {
    "vanilla": {"in": 2600, "out": 350},
    # self-refine issues up to 5 calls/example and the critique prompts are
    # long, so this is deliberately a pessimistic estimate.
    "self_refine": {"in": 9000, "out": 1400},
}


def estimate(model: str, phase: str, n: int) -> float:
    p = PRICING_PER_1M.get(model)
    if not p:
        return float("nan")
    total = 0.0
    for key in (["vanilla", "self_refine"] if phase == "both" else [
            "vanilla" if phase == "vanilla" else "self_refine"]):
        t = EST_TOKENS[key]
        total += n * (t["in"] / 1e6 * p["input"] + t["out"] / 1e6 * p["output"])
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-4o-mini",
                    help="gpt-4o-mini (cheap, capability midpoint) or gpt-4o (strongest test)")
    ap.add_argument("--dataset", default="folio",
                    choices=["folio", "proofwriter", "prontoqa", "contractnli"])
    ap.add_argument("--split", default="validation",
                    choices=["train", "validation", "test"],
                    help="ContractNLI only: its release uses train/dev/test; "
                         "registry.py maps 'validation' -> 'dev'")
    ap.add_argument("--limit", type=int, default=50,
                    help="use the full split (203/600/500) by passing 0 or the exact size")
    ap.add_argument("--phase", default="both", choices=["vanilla", "self_refine", "both"])
    ap.add_argument("--timeout", type=int, default=30, help="Prover9 timeout (seconds)")
    ap.add_argument("--max-rounds", type=int, default=2)
    ap.add_argument("--sample-seed", type=int, default=42)
    ap.add_argument("--yes", action="store_true", help="skip the cost confirmation prompt")
    args = ap.parse_args()

    n = args.limit or 203
    est = estimate(args.model, args.phase, n)

    print("=" * 68)
    print(f"Phase 3.3 / 4.2  |  dataset={args.dataset}  model={args.model}  n={n}  phase={args.phase}")
    print("=" * 68)
    print(f"Estimated cost: ~${est:.2f}  (rough; pricing table may be stale — verify)")
    print("Same prompts, parser and Prover9 grounder as the Llama arm (imported, not copied).")
    print()

    if not args.yes:
        # A wrong flag here spends real money, so make the operator confirm.
        reply = input(f"Proceed and spend ~${est:.2f}? [y/N] ").strip().lower()
        if reply not in ("y", "yes"):
            print("Aborted; nothing was sent to the API.")
            return

    harness = OpenAIHarness(
        model=args.model,
        log_path=str(PROJECT_ROOT / "experiments" / "logs"
                     / f"openai_harness_calls_{args.model}.jsonl"),
    )

    tag = args.model.replace(".", "").replace("-", "")
    nsuffix = f"_n{args.limit}" if args.limit else ""

    if args.phase in ("vanilla", "both"):
        print("\n" + "#" * 68)
        print(f"# PHASE 3.3 — vanilla silent-failure prevalence on {args.model} / {args.dataset}")
        print("#" * 68)
        run_vanilla_pipeline(
            dataset=args.dataset,
            split=args.split,
            limit=args.limit,
            timeout=args.timeout,
            harness=harness,
            mode="story",
            few_shot=True,
            sample="random",
            sample_seed=args.sample_seed,
            out_path=str(PROJECT_ROOT / "experiments" / "logs"
                         / f"vanilla_pipeline_{args.dataset}_{tag}_validation{nsuffix}.json"),
        )
        print(f"\n  cost so far: {harness.cost_report()}")

    if args.phase in ("self_refine", "both"):
        print("\n" + "#" * 68)
        print(f"# PHASE 4.2 — Self-Refine falsification gate on {args.model} / {args.dataset}")
        print("#" * 68)
        self_refine_pipeline.run(
            dataset=args.dataset,
            split=args.split,
            limit=args.limit,
            timeout=args.timeout,
            max_rounds=args.max_rounds,
            harness=harness,
            sample="random",
            sample_seed=args.sample_seed,
            out_path=str(PROJECT_ROOT / "experiments" / "logs"
                         / f"self_refine_{args.dataset}_{tag}_validation{nsuffix}.json"),
        )

    print("\n" + "=" * 68)
    print(f"DONE  |  {harness.cost_report()}")
    print("=" * 68)


if __name__ == "__main__":
    main()
