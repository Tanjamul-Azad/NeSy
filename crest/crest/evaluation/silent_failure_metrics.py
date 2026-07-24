"""Three-way outcome classification and prevalence metrics (Phase 3.1/3.2).

Pre-registered definitions (docs/MASTER_PLAN.md Phase 3):
  - correct: the grounder accepts the LLM-produced FOL and its predicted
    label matches the gold label.
  - loud failure: the grounder/parser rejects the LLM-produced FOL outright
    (unbalanced parens, arity clash, etc. -- the same exception classes
    Phase 2.1's ceiling check tags as MALFORMED_GOLD_FOL, here applied to
    LLM output instead of gold). The pipeline visibly breaks; a downstream
    user would know something went wrong.
  - silent failure: the grounder accepts the LLM-produced FOL without error
    and returns a confident, well-formed answer, but that answer disagrees
    with gold. Nothing in the pipeline signals anything is wrong -- this is
    the exact failure mode CREST exists to catch.

Prover9LimitExceededException (timeout) is deliberately NOT a loud failure:
check_entailment() already catches it internally and reports "Uncertain"
rather than raising, so a timeout surfaces here as a normal label mismatch
(silent failure) or match (correct), same as any other prediction.

A predicted label of "Contradiction" (grounder proved both the goal and its
negation) is treated as silent failure, not loud failure, per the letter of
the definition above -- it's a well-formed run with no exception, just a
label gold never uses, so it's a *mismatch* rather than a break. Worth
flagging when reading results: this is a directionally different failure
(precondition/premise inconsistency) than a plain wrong-label prediction,
so keep Prover9's "Contradiction" cases visible in per-example output when
interpreting results rather than collapsing them into ordinary silent
failures.

NOTE on Phase 3.2: `summarize()` here only computes Phase 3.1's raw
three-way bin. Phase 3.2's *strict* silent-failure prevalence is a
different, narrower filter -- "count only among examples where gold-FOL
grounding was already verified correct" (docs/MASTER_PLAN.md) means joining
these results against experiments/logs/ceiling_check_validation.json by
example_id and keeping only rows with malformed_gold_fol=False and
match=True there. That join is Phase 3.2's job, not this module's; don't
mistake `silent_failure_rate_excluding_loud` below for the Phase 3.2 number.
"""

from dataclasses import dataclass
from typing import List, Optional

from nltk.sem.logic import LogicalExpressionException
from nltk.inference.prover9 import Prover9FatalException

from crest.grounding.fol_to_prover9 import EntailmentResult, check_entailment

# Same three exception classes Phase 2.1 established as "malformed input to
# the grounder", now applied to LLM-produced FOL rather than FOLIO's gold FOL.
LOUD_FAILURE_EXCEPTIONS = (LogicalExpressionException, ValueError, Prover9FatalException)


@dataclass
class ClassifiedResult:
    example_id: str
    gold_label: str
    predicted_label: Optional[str]
    outcome: str  # "correct" | "loud_failure" | "silent_failure"
    error: Optional[str] = None
    entailment: Optional[EntailmentResult] = None
    # Sub-reason for a loud failure. Both are loud (visibly broken, no gold
    # label needed to notice), but they mean different things and lumping
    # them together would hide which one dominates:
    #   "translation_format" -- the model's output couldn't be parsed into
    #       one formula per statement at all (refusal, truncation, wrong
    #       shape). A prompting/decoding problem, not an FOL problem.
    #   "fol_parse" -- formulas were extracted fine, but the grounder or
    #       Prover9 rejected the FOL itself.
    failure_stage: Optional[str] = None


def classify_example(
    example_id: str,
    premises_fol: List[str],
    conclusion_fol: str,
    gold_label: str,
    timeout: int = 60,
) -> ClassifiedResult:
    try:
        result = check_entailment(premises_fol, conclusion_fol, timeout=timeout)
    except LOUD_FAILURE_EXCEPTIONS as e:
        return ClassifiedResult(
            example_id=example_id,
            gold_label=gold_label,
            predicted_label=None,
            outcome="loud_failure",
            error=f"{type(e).__name__}: {e}",
            failure_stage="fol_parse",
        )

    outcome = "correct" if result.label == gold_label else "silent_failure"
    return ClassifiedResult(
        example_id=example_id,
        gold_label=gold_label,
        predicted_label=result.label,
        outcome=outcome,
        entailment=result,
    )


def summarize(results: List[ClassifiedResult]) -> dict:
    n = len(results)
    correct = sum(r.outcome == "correct" for r in results)
    loud = sum(r.outcome == "loud_failure" for r in results)
    silent = sum(r.outcome == "silent_failure" for r in results)
    n_non_loud = n - loud
    return {
        "n": n,
        "correct": correct,
        "loud_failure": loud,
        "silent_failure": silent,
        # Split the loud bucket by cause -- a run dominated by
        # translation_format failures means the prompt/decoding needs fixing
        # before any prevalence number is meaningful, which a single combined
        # loud count would hide.
        "loud_failure_translation_format": sum(
            r.failure_stage == "translation_format" for r in results
        ),
        "loud_failure_translation_truncated": sum(
            r.failure_stage == "translation_truncated" for r in results
        ),
        "loud_failure_fol_parse": sum(r.failure_stage == "fol_parse" for r in results),
        "accuracy": correct / n if n else 0.0,
        "loud_failure_rate": loud / n if n else 0.0,
        # Overall prevalence (denominator = all examples run)
        "silent_failure_rate": silent / n if n else 0.0,
        # Convenience Phase 3.1 number, NOT the Phase 3.2 "strict" definition
        # (see module docstring) -- denominator excludes loud failures only,
        # doesn't join against the ceiling check.
        "silent_failure_rate_excluding_loud": silent / n_non_loud if n_non_loud else 0.0,
    }
