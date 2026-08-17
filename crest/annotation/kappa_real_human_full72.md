# The real step-4 κ — human's direct category picks vs Claude vs Gemini (2026-08-17)

**This supersedes `kappa_computation_full72.md`.** That earlier file used
Claude's own interpretation of the human's free-form prose as the
"human" side of the comparison — explicitly flagged there as invalid for
citing as IAA. This file uses the human's actual direct category picks
(`human_direct_categories_72cases.md`), with no Claude-authored mapping in
between. **This is the number that counts.**

## Results

| Pair | n | categories | po | pe | κ | interpretation |
|---|---|---|---|---|---|---|
| **Human vs Claude** | 72 | 9 | 0.514 | 0.147 | **0.430** | **moderate — below the 0.6 target** |
| **Human vs Gemini** | 72 | 9 | 0.542 | 0.172 | **0.446** | **moderate — below the 0.6 target** |
| Claude vs Gemini (reference, AI-vs-AI) | 72 | 8 | 0.736 | 0.150 | 0.690 | substantial |

**35 of 72 cases (49%) disagree between the human and Claude.** This is
the honest result and should be reported as such — a genuine mixed/negative
finding on the taxonomy's first IAA attempt, not a validated κ≥0.6 claim.

## Ruling out "it's just granularity"

A natural first hypothesis: the human used broad categories where
Claude/Gemini split the same phenomena into narrower sub-types, and
collapsing those sub-types back together would raise agreement. Tested by
folding `compound_atomization`, `missing_implicit_fact`, and
`generic_bare_plural` into `predicate_schema_divergence` on the Claude/
Gemini side and re-computing:

| Pair (coarsened) | po | pe | κ |
|---|---|---|---|
| Human vs Claude (coarsened) | 0.500 | 0.300 | 0.286 |
| Human vs Gemini (coarsened) | 0.542 | 0.350 | 0.295 |

**Coarsening made agreement worse, not better** (raw agreement barely
moved, while chance-agreement pe rose sharply because one category now
dominates the distribution). This rules out pure granularity as the
explanation — the disagreement is substantive, not a labeling-resolution
artifact.

## The likely real driver: `predicate_schema_divergence` is being used inconsistently

The human assigned `predicate_schema_divergence` as the primary category
for **33 of 72 cases (46%)** — far more than Claude (19/72) or Gemini
(29/72). Looking at the specific disagreements, the human used it for
cases Claude/Gemini instead called `compound_atomization` (predicate
fusion), `missing_implicit_fact` (a precondition never instantiated),
`generic_bare_plural` (class treated as individual), and even
`unstated_assumption_injection` (an unwarranted fact added). All of these
mechanisms technically involve "the predicate structure changed from
gold's," which is `predicate_schema_divergence`'s literal definition — so
the human's usage is not unreasonable given the category's current wording,
it's just broader than how Claude and Gemini independently chose to apply
it. **This points to a definitional-looseness problem in
`guidelines.md`, not an annotator error on either side.**

## Second correction surfaced by this pass

Re-reading the human's own stated reasoning for C068/C069 (they explicitly
separate the correctly-translated to/from propositions from a separately
mistranslated "exclusivity rule") revealed that Claude's earlier "✅
Faithful" verdict for these two cases
(`faithful_bucket_verification.md`) was based on an incomplete check — it
only examined the premise-conclusion pair the human's *first* (prose) pass
had narrated, and never checked premise 2 (the actual departure/arrival
exclusivity rule: gold `∀x∀y(FlyFrom(x,y)⊕FlyTo(x,y))` vs the LLM's
completely disconnected `∀x∀y(¬(Departure(x)=Arrival(y)))`).

**Corrected: C068 and C069 are real `predicate_schema_divergence`
failures.** Combined with the earlier C065/C066 correction, **only C003
remains confirmed genuinely translation-faithful across the entire
72-case set** (down from 5 originally reported, to 3, to 1 now).

## Recommendation (decision needed, not made unilaterally here)

Per `guidelines.md`'s own disagreement-resolution process, the honest next
step is a reconciliation pass: review the 35 disagreements together
(starting with the `predicate_schema_divergence` cluster, since it's the
dominant driver), tighten the category's definition — likely by explicitly
carving out "predicate fusion" (→ `compound_atomization`), "missing
ground instantiation" (→ `missing_implicit_fact`), and "class-as-individual"
(→ `generic_bare_plural`) as cases that should NOT default to
`predicate_schema_divergence` even though they technically involve a
predicate — and re-measure κ on the reconciled labels. This is a real
research decision (resolve now vs. report the moderate κ honestly as a
first-round finding and move on) that needs Tanjamul's call, not something
resolved automatically here.
