"""Phase 2.1: gold-FOL ceiling accuracy check.

Runs FOLIO's own gold-standard FOL (human-written, not LLM-generated)
through our Prover9 grounder and compares the result against FOLIO's gold
label. This isolates grounder bugs from LLM translation errors -- see
docs/MASTER_PLAN.md Phase 2 for the pre-registered decision thresholds
(>=85% proceed, 70-85% pause and inspect, <70% stop and fix the grounder).
"""

import json
import sys
import time
from pathlib import Path

# FOL text (and Prover9/nltk error messages that quote it) contains Unicode
# symbols (∧, ∀, etc.) that Windows' default console codepage (cp1252) can't
# encode -- reconfigure stdout so a crash while printing progress doesn't
# lose whatever results were already computed.
# Guarded: inside a Jupyter/Kaggle kernel sys.stdout is an ipykernel
# OutStream with no .reconfigure(), and an unguarded call raises
# AttributeError at import time.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from nltk.sem.logic import LogicalExpressionException

from data.loaders.folio_loader import load_folio
from crest.grounding.fol_to_prover9 import check_entailment
from nltk.inference.prover9 import Prover9FatalException

# Confirmed 2026-07-18: three distinct exception types all indicate the gold
# FOL itself is malformed, not a grounder bug --
#   LogicalExpressionException: NLTK's parser rejects it (e.g. unbalanced parens)
#   ValueError: our own paren-scanning code rejects it first (e.g. unbalanced
#     parens inside an XOR operand, caught before NLTK even sees it)
#   Prover9FatalException: Prover9 itself rejects the input (e.g. a predicate
#     used with two different arities across premises -- a real annotation
#     inconsistency found in FOLIO's gold data, example_id 819-821)
MALFORMED_DATA_EXCEPTIONS = (LogicalExpressionException, ValueError, Prover9FatalException)

# FOLIO labels are "True" / "False" / "Uncertain" -- matches our EntailmentResult.label
LABEL_MAP = {"True": "True", "False": "False", "Uncertain": "Uncertain"}


def run_ceiling_check(split: str = "validation", limit: int = None, timeout: int = 30):
    data = load_folio(split=split)
    if limit:
        data = data[:limit]

    results = []
    correct = 0
    malformed_gold = 0
    for i, ex in enumerate(data):
        start = time.time()
        malformed = False
        try:
            result = check_entailment(ex.premises_fol, ex.conclusion_fol, timeout=timeout)
            predicted = result.label
        except MALFORMED_DATA_EXCEPTIONS as e:
            predicted = "MALFORMED_GOLD_FOL"
            malformed = True
            malformed_gold += 1
        except Exception as e:
            predicted = f"ERROR: {type(e).__name__}: {str(e)[:200]}"

        gold = LABEL_MAP.get(ex.label, ex.label)
        is_match = predicted == gold
        correct += int(is_match)

        elapsed = time.time() - start
        record = {
            "example_id": ex.example_id,
            "story_id": ex.story_id,
            "gold_label": gold,
            "predicted_label": predicted,
            "match": is_match,
            "malformed_gold_fol": malformed,
            "elapsed_sec": round(elapsed, 2),
        }
        results.append(record)
        print(f"[{i+1}/{len(data)}] example_id={ex.example_id} gold={gold} predicted={predicted} match={is_match} ({elapsed:.1f}s)")

    accuracy = correct / len(data) if data else 0.0
    n_gradeable = len(data) - malformed_gold
    accuracy_excl_malformed = correct / n_gradeable if n_gradeable else 0.0
    print(f"\n=== Ceiling accuracy on {split} (n={len(data)}): {accuracy:.1%} ({correct}/{len(data)}) ===")
    print(f"=== Malformed gold FOL (data issue, not grounder bug): {malformed_gold}/{len(data)} ===")
    print(f"=== Ceiling accuracy excluding malformed gold FOL: {accuracy_excl_malformed:.1%} ({correct}/{n_gradeable}) ===")

    out_path = Path(__file__).resolve().parents[2] / "experiments" / "logs" / f"ceiling_check_{split}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "split": split,
            "n": len(data),
            "accuracy": accuracy,
            "malformed_gold_fol_count": malformed_gold,
            "accuracy_excluding_malformed": accuracy_excl_malformed,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print(f"Full results written to {out_path}")

    return accuracy, results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="validation", choices=["train", "validation"])
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    run_ceiling_check(split=args.split, limit=args.limit, timeout=args.timeout)
