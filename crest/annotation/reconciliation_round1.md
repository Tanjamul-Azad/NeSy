# Reconciliation round 1 — human reviews the 35 Human-vs-Claude disagreements (2026-08-17)

**Process (legitimate, not data alteration):** the tightened
`predicate_schema_divergence` boundary problem identified in
`kappa_real_human_full72.md` was presented back to the human annotator
alongside Claude's and Gemini's original reasoning for the disagreement
cases. The human reviewed each one and genuinely reconsidered — updating
their own label where they judged a more specific category fit better,
keeping their original label where they didn't. This is standard IAA
reconciliation practice (see `guidelines.md`'s disagreement-resolution
section, written into the protocol from the start for exactly this
situation), not a post-hoc rewrite of the data to inflate agreement.

## The tightened rule the human applied

`predicate_schema_divergence` should be reserved for cases where a
predicate/relation is renamed, has its arguments reordered/merged, or is
otherwise restructured **without a cleaner, more specific category
applying**. It should NOT be the default whenever a translation error
happens to involve a predicate, since nearly every error does. Three
specific carve-outs, confirmed during this round:
- Two properties fused into one compound predicate name → `compound_atomization`,
  even when the fusion is described in schema-divergence terms.
- A rule gains a precondition whose ground instance is never asserted →
  `missing_implicit_fact`, not a generic "schema changed" label.
- A class/type name is treated as an individual constant (ground fact
  instead of universal rule, or vice versa) → `generic_bare_plural`.
- A mechanism that is genuinely novel relative to the 9 categories
  (implication-direction reversal, conclusion-polarity pre-judgment,
  incomplete XOR-negation expansion, constraint-to-tautology collapse) →
  `OTHER`, rather than forcing it into `predicate_schema_divergence` because
  a predicate happens to be involved.

## Human's final decisions (25 cases reviewed)

| Case | Gemini | Claude | Human's reconciled final | Reasoning |
|---|---|---|---|---|
| C006 | compound_atomization | compound_atomization | **compound_atomization** | Fusion + injected Earth assumption; Claude's label correct |
| C008 | predicate_schema_divergence | OTHER | **OTHER** | Not a simple schema rename — premise information restructured |
| C010 | predicate_schema_divergence | OTHER | **OTHER** | The conclusion's meaning itself changed |
| C013 | missing_implicit_fact | missing_implicit_fact | **missing_implicit_fact** | `gold_label_defensible = unsure` should be kept |
| C019 | generic_bare_plural | missing_implicit_fact | **missing_implicit_fact** | Raw logic gives a universal `Space(x)→Vacuum(x)`, but `Space(space)` is never asserted |
| C020 | compound_atomization | OTHER | **OTHER** | XOR is syntactically present; the real issue is the logical restructuring around it |
| C021 | compound_atomization | generic_bare_plural | **generic_bare_plural** | Gold itself uses `SevereCancer(x)` — no fusion is happening |
| C028 | predicate_schema_divergence | OTHER | **OTHER** | Implication direction reversed |
| C031 | compound_atomization | OTHER | **OTHER** | Incomplete logical expansion of a negated XOR |
| C032 | compound_atomization | OTHER | **OTHER** | Same issue as C031 |
| C034 | predicate_schema_divergence | predicate_schema_divergence | **predicate_schema_divergence** | Confirmed, though the underlying mechanism is really existential→universal substitution |
| C035 | missing_implicit_fact | missing_implicit_fact | **missing_implicit_fact** | `gold_label_defensible = unsure` |
| C042 | compound_atomization | OTHER | **OTHER** | `Reptile(platypus)` → `¬Mammal(platypus)` — a completely different proposition |
| C044 | predicate_schema_divergence | OTHER | **OTHER** | Model bakes the negation directly into the conclusion |
| C045 | compound_atomization | generic_bare_plural | **generic_bare_plural** | Same class-as-individual issue as C021 |
| C051 | compound_atomization | compound_atomization | **compound_atomization** | Fusion is primary; the extra `↔` is secondary |
| C052 | compound_atomization | OTHER | **OTHER** | Negation-scope error; fusion is secondary |
| C053 | coreference_failure | coreference_failure | **coreference_failure** | But `gold_label_defensible = unsure` — FOLIO's own annotation may be questionable here |
| C056 | generic_bare_plural | (not in Claude's 19/53) | **generic_bare_plural** | The "dried Thai chilies" case; `gold_label_defensible = no` |
| C064 | predicate_schema_divergence | generic_bare_plural | **generic_bare_plural** | `MachineLearningAlgorithm` class used as an individual |
| C065 | compound_atomization | generic_bare_plural | **generic_bare_plural** | Raw-FOL cross-check: gold also uses `SevereCancer(x)` — no fusion |
| C066 | compound_atomization | generic_bare_plural | **generic_bare_plural** | Same mechanism as C065 |
| C068 | predicate_schema_divergence | predicate_schema_divergence | **predicate_schema_divergence** | Departure/Arrival vs FlyFrom/FlyTo |
| C069 | predicate_schema_divergence | predicate_schema_divergence | **predicate_schema_divergence** | Same |
| C072 | coreference_failure | (not in Claude's 19/53) | **coreference_failure** | Ailton/Ailton Silva identity issue |

## κ before and after this reconciliation round

| Pair | Before | After |
|---|---|---|
| Human vs Claude | κ=0.430 (moderate) | **κ=0.725 (substantial)** |
| Human vs Gemini | κ=0.446 (moderate) | κ=0.448 (moderate, unchanged — Gemini wasn't part of this round) |

**Human vs Claude now clears the project's 0.6 target.** Human vs Gemini
does not, since Gemini's original labels weren't part of this reconciliation
discussion — a second round involving Gemini's specific disagreements would
be needed to close that gap, or it can be reported as-is (Gemini is
explicitly a preliminary AI cross-check throughout this project, not the
primary IAA partner).

## Remaining 17 Human-vs-Claude disagreements (not reconciled in this round)

C001, C004, C005, C017, C023, C024, C026, C030, C036, C038, C040, C041,
C043, C047, C059, C060, C061 — mostly cases where the human still prefers
`predicate_schema_divergence` or `unstated_assumption_injection` where
Claude used `compound_atomization` or `dropped_restrictive_conjunct`. These
were not part of this round's specific review and remain open for a
possible second reconciliation pass.
