# Verification of the human annotator's 🟢 "Faithful" bucket (2026-08-17)

**Why this exists.** The human's forensic second pass over all 72 cases
(`human_annotation_72cases_raw.md` — the follow-up, richer version with the
🟥/🟨/🟢 three-way bucketing, pasted directly into conversation, not yet
saved as its own file since it arrived as a continuation of the same raw
document) made a genuinely important methodological correction: a false
conclusion is not automatically a translation failure (see C068/C069, the
LGA example — the model literally translates "Susan flies to LGA" and
"Susan flies from LGA" as two different, unconnected predicates, exactly
matching gold's structure; the conclusion being false is not evidence of a
bad translation).

But the same pass also placed 20 cases in a 🟢 "Faithful / no semantic
translation failure" bucket based on story-level reading — "each premise
looks locally sensible, and the intended fact appears somewhere in the
list." That is not sufficient evidence. A translation can read as locally
sensible sentence-by-sentence while still not actually *entailing* the
conclusion once you trace the derivation through — missing ground facts,
predicate-name mismatches between where a rule is stated and where it's
used, and reversed relation arguments all produce exactly this symptom.

**Method:** every one of the 20 "Faithful" cases was checked by hand-tracing
whether the conclusion is actually derivable from the model's own listed
FOL (not gold's), the same way Prover9 would attempt it — looking
specifically for (a) predicate names that don't match between where a fact
is established and where a rule needs it, (b) added preconditions
(`Person(x)`, `Man(x)`, etc.) whose ground instance is never asserted, and
(c) reversed relation-argument order.

## Result: 18 of 20 have a confirmable translation-level bug; 2 are genuinely faithful

| Case | Model | Story | Bug found |
|---|---|---|---|
| C013 | Llama | Walden/knowledge | `Person(harry)` never asserted (rule requires it); `Book(walden)` never asserted either (premise 1's rule also can't fire) |
| C014 | Llama | Harry smarter | `Person(harry)` never asserted |
| C017 | Llama | Windy/great shooter | Premise 5's negation flipped (`CanJumpWhenShooting` instead of `¬JumpWhenShooting`) **and** the rule now requires `Man(windy)`, never asserted |
| C019 | Llama | Space sucks | `Space(space)` never asserted, so `∀x(Space(x)→Vacuum(x))` never fires |
| C023 | Llama | Tom pet owner | Rule needs `AnimalLover(x)`; pet-owner premise asserts `LovesAnimals(x)` instead — different predicate, never connects |
| C029 | gpt-4o-mini | Wild turkey | `∃x(WildTurkeyType(x)∧...)` never bound to `WildTurkey(tom)` — says nothing about Tom |
| C033 | gpt-4o-mini | Lewandowski | Conclusion is self-negated (`¬PlaysFor` instead of literal `PlaysFor`); `∀y` also dropped, free variable |
| C035 | gpt-4o-mini | Walden/knowledge | Same as C013: `Person(harry)` and `Book(walden)` never asserted |
| C036 | gpt-4o-mini | Harry smarter | `Person(harry)` never asserted |
| C040 | gpt-4o-mini | Windy/great shooter | Predicate renamed mid-chain: rule 5 concludes `Jumping(windy)`, rule 7 requires `CanJump(windy)` — different names, never connect |
| C041 | gpt-4o-mini | Barutin Cove/Antarctica | `LocatedIn(antarctica, southShetlandIslands)` — arguments reversed (same bug as C018/C062), breaks the transitivity chain |
| C044 | gpt-4o-mini | Birds/hawks | Conclusion is self-negated (`¬∀x(Bird→Swims)` instead of literal `∀x(Bird→Swim)`) |
| C047 | gpt-4o-mini | Tom pet owner | Same `AnimalLover`/`LovesAnimals` mismatch as C023 |
| C054 | gpt-4o | Wild turkey | Triple predicate mismatch: rule uses `WildTurkeyType`, ground facts use `IsType(tom,...)`, and neither connects to the given `WildTurkey(tom)` |
| C056 | gpt-4o | Dried Thai chili | Gold's ground disjunctive fact about the specific chili became a universal rule (`∀x(DriedThaiChili(x)→...)`), but `DriedThaiChili(driedThaiChili)` is never asserted — rule never fires. **New finding**, refines the step-2 note (which only flagged this case for a gold-annotation-naturalness question, missing this separate, more basic translation bug.) |
| C057 | gpt-4o | Harry smarter | Rule requires `Person(harry)` and `Book(walden)`; neither ever asserted |
| C061 | gpt-4o | Windy/great shooter | Rule 5 requires `Person(windy)` (never asserted); rule 7 requires `Shooter(windy)` (also never asserted) — two independent missing facts |
| C063 | gpt-4o | Space sucks | `Sucks(vacuum)` is a ground fact about an individual literally named "vacuum", not a universal rule — has no connection at all to `Vacuum(space)` |
| C068 | gpt-4o | Susan/LGA | **Confirmed faithful.** Two distinct, unconnected predicates (`FliesTo`/`FliesFrom`) translated literally from two distinct NL sentences, matching gold's own structure exactly. |
| C069 | gpt-4o | John/LGA | **Confirmed faithful**, same structure as C068 (mirror case). |

## The dominant pattern: precondition injection without instantiation

**8 of the 18 confirmed bugs** (C013, C014, C019, C035, C036, C056, C057,
C061) share one specific mechanism: the model adds a plausible-sounding
restricting condition to a rule (`Person(x)`, `Man(x)`, `Shooter(x)`,
`DriedThaiChili(x)`) that is not wrong on its own — it often mirrors the
English ("when a *person* reads a book...") — but the model then never
separately asserts that condition's ground instance for the specific
individual in question (`Person(harry)`, `Man(windy)`, `Shooter(windy)`,
`DriedThaiChili(driedThaiChili)`). Each premise reads as locally sensible;
the chain is broken only when you actually try to fire the rule. This
already falls under the `missing_implicit_fact` category in
`guidelines.md`, but its prevalence here (8/20 "faithful" cases, i.e. 40%)
is new information — it's a much more common failure shape than the
original 19-case classification (5%, 1/19) suggested, and worth surfacing
prominently rather than leaving it as the smallest category.

## What this means for CREST's framing

The human's original worry (relayed 2026-08-17) was that several cases
looked like the FOL translation was fine but the "solver" still returned
the wrong answer — a finding that, if it held up, would seriously
complicate CREST's core claim (silent failure = translation failure, not
solver failure). Checked systematically: **18 of 20 "solver must be at
fault" candidates turned out to have a real, locatable translation bug**,
and Prover9 (confirmed by reading `crest/crest/grounding/fol_to_prover9.py`
to be a classical, deterministic, sound theorem prover with no LLM
involvement in verdict generation) correctly failed to derive the
conclusion from the model's own flawed premises in every one of them. This
is not a weaker version of CREST's claim — **it is a stronger,
independently-verified version of it**, since it comes from actively trying
to find counter-examples and mostly failing to.

**Remaining honest gap:** only 2 cases (C068, C069) were confirmed as
genuinely translation-faithful with a still-wrong verdict — too small a
sample to characterize what a true solver-side (non-translation) silent
failure would look like, if one exists at all in this dataset. This should
be stated as an open question, not resolved either way, in the paper.
