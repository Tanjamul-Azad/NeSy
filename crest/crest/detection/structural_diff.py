"""CREST-D, signal 2: structural divergence between a sentence and its formula.

Signal 1 (`predicate_checker`) is high-precision but narrow -- it flags 11.3%
of silent failures, and almost none outside the legal domain. It can only see
the FOL. This module adds the missing half: it compares each formula against
**the sentence it was translated from**, which is where meaning-level loss
becomes visible.

WHY THESE FOUR CHECKS AND NOT AN ARBITRARY BAG OF HEURISTICS
============================================================
Each one targets a failure class our own annotation study measured, with the
case counts that justify it (crest/annotation/, docs/RESEARCH_DIRECTION.md):

  QUANTIFIER   The largest category in the step-2 taxonomy (6/19, 32%) is
               generic/bare-plural failure: English "Plungers suck" or
               "Cupcakes are baked sweets" states a rule about a class, and
               the model emits a ground fact about one individual -- no
               quantifier at all. A universal cue in the sentence with no
               quantifier in the formula is exactly that error, visible
               without a gold label.
  NEGATION     Dropped negation is the flagship danger case and the reason
               Phase 7.1 exists at all. C017 is the worked example: gold
               ~JumpWhenShooting(x) -> CanBlock(...), model wrote
               CanJumpWhenShooting(x) -> CanBlock(...). PARITY is what matters
               (odd vs even count), because two negations cancel and a raw
               count difference would fire on correct De Morgan rewrites.
  CONDITIONAL  Rule-shaped sentences ("if", "unless", "only ... if") that
               arrive as flat conjunctions lose the implication entirely.
  EXCLUSIVITY  FOLIO's XOR cases: "either A or B (but not both)" translated as
               inclusive OR weakens the constraint silently. Measured at 3/19
               (16%) in the step-2 classification.

WHAT THIS MODULE DELIBERATELY DOES NOT DO
=========================================
It does not claim a mismatch is an error. English cues are noisy: "any" is
universal in "any student may apply" and existential in "if any student
applies"; a sentence can be correctly formalised with the quantifier implicit
in a predicate. So every output here is a RISK SIGNAL with a named type, never
a proof -- unlike signal 1's unreachable-goal verdict, which is sound.

That asymmetry is deliberate and is the reason the attributor combines the two
rather than averaging them into one score: one signal proves, the other
suspects, and a framework that conflates the two would inherit the weaker
guarantee everywhere.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Natural-language cues. Word-boundary matched, lowercase input assumed.
# Kept small and literal on purpose: a large hand-tuned lexicon would be
# unfalsifiable engineering, and every entry here maps to a documented failure
# class rather than to whatever improved a number.
# ---------------------------------------------------------------------------

_UNIVERSAL_CUES = re.compile(
    r"\b(all|every|each|any|anyone|anything|always|everyone|everything|"
    r"no|none|nobody|nothing|never|whoever|whenever|those who)\b")

_EXISTENTIAL_CUES = re.compile(
    r"\b(some|someone|something|a few|at least one|there is|there are|"
    r"there exists|certain)\b")

# "no/none/never" are BOTH universal-shaped and negative, which is correct:
# "No bird swims" is a universal with an embedded negation.
_NEGATION_CUES = re.compile(
    r"\b(not|n't|no|none|nobody|nothing|never|neither|nor|without|"
    r"cannot|can't|fails? to|unable|except)\b")

_CONDITIONAL_CUES = re.compile(
    r"\b(if|unless|whenever|provided that|in case|when|only if|"
    r"as long as|implies|therefore|thus|hence|so that)\b")

_EXCLUSIVE_CUES = re.compile(
    r"(either\b.*\bor\b|\bbut not both\b|\bexactly one\b|\bonly one of\b)")

# ---------------------------------------------------------------------------
# FOL surface features. The formulas use the Unicode convention fixed by the
# prompt (see llama_harness.FEWSHOT_PROMPT_TEMPLATE); ASCII fallbacks are
# accepted because the grounder normalises them too.
# ---------------------------------------------------------------------------

_FOL_FORALL = re.compile(r"[∀]|\ball\s+[a-z]\b")
_FOL_EXISTS = re.compile(r"[∃]|\bexists\s+[a-z]\b")
_FOL_NEG = re.compile(r"[¬~]|\b-(?=[A-Za-z(])")
_FOL_IMPLIES = re.compile(r"[→⇒]|->")
_FOL_XOR = re.compile(r"[⊕]")


@dataclass
class StructuralMismatch:
    """One named divergence between a sentence and its formula."""

    kind: str          # quantifier_missing | negation_parity | ...
    sentence: str
    formula: str
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.detail}"


@dataclass
class StructuralReport:
    mismatches: List[StructuralMismatch] = field(default_factory=list)
    n_pairs: int = 0

    @property
    def flagged(self) -> bool:
        return bool(self.mismatches)

    @property
    def kinds(self) -> List[str]:
        return sorted({m.kind for m in self.mismatches})

    def summary(self) -> str:
        if not self.mismatches:
            return "no_structural_objection"
        return " | ".join(f"{k}x{sum(m.kind == k for m in self.mismatches)}"
                          for k in self.kinds)


def _cues(pattern: re.Pattern, text: str) -> int:
    return len(pattern.findall((text or "").lower()))


def compare_one(sentence: str, formula: str) -> List[StructuralMismatch]:
    """Structural divergences for a single (sentence, formula) pair."""
    out = []
    s, f = sentence or "", formula or ""
    s_low = s.lower()

    has_forall = bool(_FOL_FORALL.search(f))
    has_exists = bool(_FOL_EXISTS.search(f))
    n_univ = _cues(_UNIVERSAL_CUES, s_low)
    n_exist = _cues(_EXISTENTIAL_CUES, s_low)

    # 1. A class-level statement rendered without any quantifier. This is the
    #    generic/bare-plural failure, the largest category in our taxonomy.
    if n_univ and not has_forall and not has_exists:
        out.append(StructuralMismatch(
            "quantifier_missing", s, f,
            f"sentence carries {n_univ} universal cue(s) but the formula has "
            f"no quantifier at all"))
    # 2. Universal cue rendered as an existential, or vice versa. Weaker than
    #    (1) -- English "any" genuinely swings both ways -- so it is reported
    #    separately rather than merged into one bucket.
    elif n_univ and has_exists and not has_forall:
        out.append(StructuralMismatch(
            "quantifier_substituted", s, f,
            "universal cue in the sentence, existential quantifier in the formula"))
    elif n_exist and has_forall and not has_exists and not n_univ:
        out.append(StructuralMismatch(
            "quantifier_substituted", s, f,
            "existential cue in the sentence, universal quantifier in the formula"))

    # 3. Negation PARITY, not count: two negations cancel, so a correct De
    #    Morgan rewrite must not fire. Only an odd/even disagreement indicates
    #    the polarity of the statement changed.
    n_neg_nl, n_neg_fol = _cues(_NEGATION_CUES, s_low), len(_FOL_NEG.findall(f))
    if (n_neg_nl % 2) != (n_neg_fol % 2):
        out.append(StructuralMismatch(
            "negation_parity", s, f,
            f"{n_neg_nl} negation cue(s) in the sentence vs {n_neg_fol} in the "
            f"formula -- parity differs, so the polarity may have flipped"))

    # 4. Rule-shaped sentence arriving without an implication.
    if _cues(_CONDITIONAL_CUES, s_low) and not _FOL_IMPLIES.search(f):
        out.append(StructuralMismatch(
            "conditional_lost", s, f,
            "conditional cue in the sentence but no implication in the formula"))

    # 5. Exclusive disjunction flattened to inclusive or conjunctive form.
    if _EXCLUSIVE_CUES.search(s_low) and not _FOL_XOR.search(f):
        out.append(StructuralMismatch(
            "exclusivity_lost", s, f,
            "sentence states an exclusive choice but the formula has no XOR"))

    return out


def check(
    premises_nl: List[str],
    premises_fol: List[str],
    conclusion_nl: Optional[str] = None,
    conclusion_fol: Optional[str] = None,
) -> StructuralReport:
    """Compare every sentence against the formula produced for it.

    Premise lists must be aligned; the pipeline guarantees this because
    `parse_story_output` rejects any output whose label set is not exactly
    P1..Pn plus C, rather than padding or truncating (see llama_harness).
    """
    report = StructuralReport()
    pairs: List[Tuple[str, str]] = list(zip(premises_nl or [], premises_fol or []))
    if conclusion_nl is not None and conclusion_fol is not None:
        pairs.append((conclusion_nl, conclusion_fol))

    report.n_pairs = len(pairs)
    for sent, form in pairs:
        report.mismatches.extend(compare_one(sent, form))
    return report
