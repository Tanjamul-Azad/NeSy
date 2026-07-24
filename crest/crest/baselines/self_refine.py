"""Phase 4: Self-Refine baseline (Madaan et al., 2023) for NL -> FOL.

This is the project's central falsification gate. Self-Refine is published,
training-free, model-agnostic, and needs no extra machinery: translate, let
the model critique its own output, let it revise. If that alone closes the
silent-failure gap measured in Phase 3, CREST's detector+corrector has no
justification and the framing has to change. See docs/MASTER_PLAN.md
Phase 4 and the kill-gate table.

Because the point is to *try to falsify our own thesis*, several choices
here deliberately favour the baseline rather than us:

  1. The round-0 translation uses the IDENTICAL prompt, seed and decoding as
     the vanilla pipeline (few-shot v3, greedy, seed 42). Self-Refine
     therefore starts from exactly the vanilla output -- any difference in
     the final numbers is attributable to refinement alone, not to a
     different starting point. The runner verifies this empirically rather
     than trusting it.
  2. If a refinement round produces unparseable output, we KEEP THE PREVIOUS
     round's FOL instead of scoring the broken text. The literal published
     method would just take the new output; falling back makes Self-Refine
     strictly no-worse-than-vanilla on parse failures. That is more generous
     than the paper and is the right direction for a kill gate -- if CREST
     still beats a baseline we have propped up, the result is robust.
  3. The critique step sees the natural-language statements alongside its own
     formulas, i.e. everything needed in principle to spot a mistranslation.

What Self-Refine deliberately does NOT get, because giving it these would
make the comparison meaningless rather than generous:

  - the gold label (that is an oracle; no deployed system has it);
  - the Prover9 result or any solver error (that is a *different*, reactive
    baseline -- Logic-LM-style error-triggered refinement -- which by
    construction cannot fire on a silent failure, since a silent failure
    produces no error. Worth running separately as its own condition; do not
    conflate it with Self-Refine).

Also deliberately generic: the critique prompt asks the model to check its
formulas against the sentences, but does NOT enumerate the specific error
classes CREST targets (predicate/constant naming consistency, dropped
negation). Listing those would be implementing CREST's detector inside the
baseline via prompting. That "targeted critique" variant is a genuinely
stronger threat and is worth running as a follow-up condition, but it is not
Self-Refine and must not be reported as it.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from crest.inference.llama_harness import (
    LlamaHarness,
    StoryFormatError,
    parse_story_output,
)

SELF_REFINE_VERSION = "selfrefine-v1"

# Sentinel the critique must emit when it finds nothing wrong. Checked as a
# substring on the first non-empty line so trailing chatter doesn't defeat it.
NO_ISSUES = "NO_ISSUES"

CRITIQUE_PROMPT_TEMPLATE = (
    "You are reviewing a translation from natural language into First-Order "
    "Logic (FOL).\n\n"
    "Below are numbered natural language statements and the FOL formula "
    "produced for each one.\n\n"
    "Check each formula against its sentence. Consider whether the formula "
    "says the same thing as the sentence, whether quantifiers and variables "
    "are used correctly, whether the logical connectives match the meaning, "
    "and whether the formulas fit together as a coherent set.\n\n"
    "If you find problems, list them briefly, one per line, naming the label "
    "(P1, P2, ..., C) each problem belongs to.\n"
    f"If every formula is correct, reply with exactly {NO_ISSUES} and nothing else.\n\n"
    "Statements and formulas:\n"
    "{paired}\n\n"
    "Review:\n"
)

REFINE_PROMPT_TEMPLATE = (
    "You previously translated these natural language statements into "
    "First-Order Logic (FOL), and a review identified problems.\n\n"
    "Statements and your current formulas:\n"
    "{paired}\n\n"
    "Review:\n"
    "{critique}\n\n"
    "Write the corrected FOL translation. Use standard FOL syntax: "
    "quantifiers (∀, ∃), connectives (∧, ∨, ¬, →, ↔, ⊕), and predicates in "
    "the form Predicate(arg1, arg2, ...). Write constants in lowerCamelCase "
    "and variables as x, y, z.\n\n"
    "Output exactly one line per statement, in the same order, each line "
    "starting with the label shown (P1, P2, ..., C). Output only these "
    "lines — no explanations, no commentary, no markdown.\n\n"
    "Corrected FOL translations:\n"
)


@dataclass
class RefineRound:
    round_index: int
    critique: str
    stopped_no_issues: bool
    refined_ok: bool
    parse_error: Optional[str] = None
    premises_fol: Optional[List[str]] = None
    conclusion_fol: Optional[str] = None


@dataclass
class SelfRefineResult:
    premises_fol: Optional[List[str]]
    conclusion_fol: Optional[str]
    # Round-0 (vanilla) output, kept so the runner can verify Self-Refine
    # really did start from the same place as the vanilla pipeline.
    initial_premises_fol: Optional[List[str]]
    initial_conclusion_fol: Optional[str]
    initial_error: Optional[str]
    rounds: List[RefineRound] = field(default_factory=list)
    n_rounds_run: int = 0
    changed_from_initial: bool = False


def _pair(statements: List[str], conclusion: str,
          premises_fol: List[str], conclusion_fol: str) -> str:
    lines = []
    for i, (nl, fol) in enumerate(zip(statements, premises_fol), start=1):
        lines.append(f"P{i} sentence: {nl}")
        lines.append(f"P{i} formula:  {fol}")
    lines.append(f"C sentence: {conclusion}")
    lines.append(f"C formula:  {conclusion_fol}")
    return "\n".join(lines)


def _says_no_issues(critique: str) -> bool:
    for line in critique.split("\n"):
        stripped = line.strip()
        if stripped:
            return NO_ISSUES in stripped.upper()
    # Empty critique: nothing to act on, treat as "no issues" rather than
    # feeding an empty review into the refine step.
    return True


def run_self_refine(
    harness: LlamaHarness,
    premises: List[str],
    conclusion: str,
    max_rounds: int = 2,
) -> SelfRefineResult:
    """Translate, then self-critique and revise up to `max_rounds` times.

    Stops early when the critique reports no issues -- that is the published
    method's behaviour, and it matters for the comparison: a baseline that
    always rewrites would be a different (and worse) method.
    """
    # Round 0 == the vanilla pipeline, byte for byte.
    try:
        premises_fol, conclusion_fol = harness.translate_story(
            premises, conclusion, few_shot=True
        )
    except StoryFormatError as e:
        # Nothing to refine. Report it exactly as vanilla would -- inventing
        # a recovery here would flatter the baseline in a way the published
        # method does not.
        return SelfRefineResult(
            premises_fol=None, conclusion_fol=None,
            initial_premises_fol=None, initial_conclusion_fol=None,
            initial_error=f"StoryFormatError: {e}",
        )

    initial_p, initial_c = list(premises_fol), conclusion_fol
    result = SelfRefineResult(
        premises_fol=premises_fol, conclusion_fol=conclusion_fol,
        initial_premises_fol=initial_p, initial_conclusion_fol=initial_c,
        initial_error=None,
    )

    for k in range(max_rounds):
        paired = _pair(premises, conclusion, result.premises_fol, result.conclusion_fol)
        critique, _ = harness._generate(
            CRITIQUE_PROMPT_TEMPLATE.format(paired=paired), max_new_tokens=400
        )

        if _says_no_issues(critique):
            result.rounds.append(RefineRound(k, critique, True, False))
            break

        refine_prompt = REFINE_PROMPT_TEMPLATE.format(paired=paired, critique=critique)
        raw, hit_cap = harness._generate(
            refine_prompt, max_new_tokens=180 * (len(premises) + 1) + 200
        )
        try:
            new_p, new_c = parse_story_output(raw, len(premises))
        except StoryFormatError as e:
            # Keep the previous round's FOL (see module docstring, choice 2).
            result.rounds.append(
                RefineRound(k, critique, False, False,
                            parse_error=f"{'truncated: ' if hit_cap else ''}{e}")
            )
            result.n_rounds_run = k + 1
            break

        result.premises_fol, result.conclusion_fol = new_p, new_c
        result.rounds.append(
            RefineRound(k, critique, False, True,
                        premises_fol=new_p, conclusion_fol=new_c)
        )
        result.n_rounds_run = k + 1

    result.changed_from_initial = (
        result.premises_fol != initial_p or result.conclusion_fol != initial_c
    )
    return result
