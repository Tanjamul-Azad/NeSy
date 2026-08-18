"""CREST-D, signal 1: predicate schema consistency and goal reachability.

This is the first component of CREST that is a SYSTEM rather than a
measurement: it takes an LLM's FOL and returns a verdict BEFORE the solver
runs, with no gold label, no second model call, and no training.

Why this signal, justified by our own data rather than by intuition
(docs/RESULTS_SNAPSHOT.md 1b, contractnli_blocker_attribution.py): on real
legal text, 21-47% of silent failures have a conclusion whose predicates
appear NOWHERE in their own premises. The proof was unreachable the moment
the translation was written -- the model named the same relation two different
ways inside a single prompt (GrantsRights in the premise, GrantsRight in the
conclusion; ConferRights vs GrantRights; Disclose vs ConveyedVerbally).

Three checks, in increasing order of how much they claim:

  1. ARITY CONFLICT   -- one predicate name used with different arities.
                         Prover9 rejects this outright, so it is a LOUD
                         failure we can predict before paying for the call.
  2. UNREACHABLE GOAL -- no conclusion predicate occurs in any premise.
                         Sound EXCEPT when the premise set is itself
                         inconsistent: from a contradiction anything follows,
                         including a goal sharing no vocabulary. Measured on
                         our own 130 solver-reached flags: 128 Uncertain, 2
                         Contradiction, i.e. 98.5% -- and both exceptions were
                         exactly that case. The original docstring here
                         claimed 100% soundness with no carve-out; that was
                         wrong and is corrected rather than softened.
  3. NEAR-MISS PAIR   -- two distinct surface names normalise to the same
                         key (case, plural, word order). This is the
                         REPAIRABLE class: the model meant one relation and
                         spelled it two ways.

Deliberately NOT claimed: that overlap implies derivability. A formula can
share every predicate and still fail, for any of the four non-translation
blockers in docs/GAPS.md or for an ordinary bug. This module reports
UNREACHABLE as a proof and everything else as a risk signal, never as a
guarantee of correctness.

Synonym divergence (ConferRights vs GrantRights) is explicitly OUT of scope
here -- normalisation cannot see that two different words mean the same
relation. That gap is what the trained corrector (Phase 8) exists to close,
and keeping it out of this module is what keeps this module deterministic.

HOW BIG IS THAT OUT-OF-SCOPE GAP? Measured, not guessed: of 147 unreachable
goals across every committed run, exactly ONE is a normalisation-detectable
near-miss (GrantsRight vs GrantsRights). The other 146 are semantic
divergence -- ConferRights vs GrantRights, Disclose vs ConveyedVerbally --
where the model chose a different relation, not a different spelling. So this
module DETECTS well and REPAIRS almost nothing on its own, and any plan that
assumed string normalisation would fix the problem was wrong. It also
replicates the FOLIO finding that surface naming errors are self-announcing
(loud) while meaning-level divergence is what fails silently.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

# A predicate application: capitalised identifier immediately followed by "(".
# Case-sensitive on purpose -- the prompt's convention is Predicate(...) with
# lowerCamelCase constants, so a lowercase identifier before "(" is a term.
_PRED_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\s*\(")

# Split camelCase / PascalCase into words: "GrantsRights" -> ["Grants","Rights"]
_CAMEL_RE = re.compile(r"[A-Z][a-z0-9_]*|[A-Z]+(?![a-z])")


def _normalise(name: str) -> str:
    """Key under which two spellings of the same intended relation collide.

    Lowercases, strips a trailing plural "s" per word, and sorts the words so
    word order stops mattering. VerballyConveyed and ConveyedVerbally both
    become "convey verbal"; GrantsRights and GrantsRight both become
    "grant right".

    Sorting is a deliberate over-approximation: it will also collide genuinely
    different relations built from the same words in a different order. Those
    surface as near-misses, which a repair step must VERIFY rather than apply
    blindly -- see this module's stance on risk versus proof.
    """
    words = _CAMEL_RE.findall(name) or [name]
    stems = []
    for w in words:
        w = w.lower().strip("_")
        if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        if w:
            stems.append(w)
    return " ".join(sorted(stems))


def signatures(formula: str) -> Set[Tuple[str, int]]:
    """(predicate name, arity) pairs in one formula.

    Arity is counted by scanning the argument list while respecting nesting,
    so LocatedIn(f(a,b), c) is arity 2 rather than 3.
    """
    out = set()
    for m in _PRED_RE.finditer(formula or ""):
        name = m.group(1)
        i = m.end()  # just past "("
        depth, args, has_content = 1, 1, False
        while i < len(formula) and depth > 0:
            c = formula[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "," and depth == 1:
                args += 1
            elif not c.isspace() and depth == 1:
                has_content = True
            i += 1
        out.add((name, args if has_content else 0))
    return out


@dataclass
class SchemaReport:
    """What CREST-D knows before the solver runs."""

    unreachable_goal: bool
    arity_conflicts: Dict[str, Set[int]] = field(default_factory=dict)
    near_miss_pairs: List[Tuple[str, str]] = field(default_factory=list)
    conclusion_only_predicates: Set[str] = field(default_factory=set)
    premise_predicates: Set[str] = field(default_factory=set)
    conclusion_predicates: Set[str] = field(default_factory=set)

    @property
    def predicted_outcome(self) -> str:
        """The pre-solver verdict. Only two values are claims; the third is
        deliberately "no objection" rather than a prediction of correctness.
        """
        if self.arity_conflicts:
            return "will_fail_loudly"       # Prover9 rejects mixed arities
        if self.unreachable_goal:
            return "will_return_uncertain"  # sound: no shared predicate
        return "no_reachability_objection"

    @property
    def repairable(self) -> bool:
        """True when the defect is translation-level, i.e. the kind a schema
        alignment could fix. An unreachable goal with NO near-miss to align to
        is not repairable by renaming: it needs content the translation never
        produced, which is a different and mostly unfixable problem.
        """
        return bool(self.near_miss_pairs) or bool(self.arity_conflicts)

    def summary(self) -> str:
        bits = [self.predicted_outcome]
        if self.arity_conflicts:
            bits.append("arity:" + ",".join(
                f"{k}/{sorted(v)}" for k, v in sorted(self.arity_conflicts.items())))
        if self.near_miss_pairs:
            bits.append("near_miss:" + ",".join(f"{a}~{b}" for a, b in self.near_miss_pairs))
        if self.unreachable_goal:
            bits.append("unreachable:" + ",".join(sorted(self.conclusion_only_predicates)))
        return " | ".join(bits)


def check(premises_fol: List[str], conclusion_fol: str) -> SchemaReport:
    """The whole signal, on one example. Deterministic, no model, no network."""
    prem_sigs, conc_sigs = set(), signatures(conclusion_fol)
    for f in premises_fol or []:
        prem_sigs |= signatures(f)

    prem_names = {n for n, _ in prem_sigs}
    conc_names = {n for n, _ in conc_sigs}

    arities: Dict[str, Set[int]] = {}
    for name, ar in prem_sigs | conc_sigs:
        arities.setdefault(name, set()).add(ar)
    conflicts = {n: a for n, a in arities.items() if len(a) > 1}

    shared = conc_names & prem_names
    unreachable = bool(conc_names) and not shared

    prem_by_norm: Dict[str, Set[str]] = {}
    for n in prem_names:
        prem_by_norm.setdefault(_normalise(n), set()).add(n)

    near = []
    for n in sorted(conc_names - prem_names):
        for cand in sorted(prem_by_norm.get(_normalise(n), set())):
            near.append((n, cand))

    return SchemaReport(
        unreachable_goal=unreachable,
        arity_conflicts=conflicts,
        near_miss_pairs=near,
        conclusion_only_predicates=conc_names - prem_names,
        premise_predicates=prem_names,
        conclusion_predicates=conc_names,
    )
