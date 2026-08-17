# Verification of the human annotator's 🟨 "Needs semantic scrutiny" bucket (2026-08-17)

**Follow-up to `faithful_bucket_verification.md`.** Same method, applied to
the other bucket the human explicitly flagged as uncertain: 15 cases where
"the formula differs from gold but isn't obviously wrong, needs equivalence
checking." The human's own proposed test for this bucket was exactly
right — "check what worlds satisfy the formula, don't just eyeball whether
it looks different" — it was applied here rigorously, case by case.

## ⚠️ Correction (2026-08-17, later same day): C065/C066 verdict was too narrow

The table below originally marked C065 and C066 "✅ Faithful" based only on
checking whether their *conclusion* formulas are logically equivalent to
gold's. That check was correct as far as it went, but incomplete: both
cases share the same cancer-story premises as C021/C045, which were already
confirmed elsewhere to contain the `SevereCancer(bileDuctCancer)`
ground-fact-instead-of-universal-rule bug (`generic_bare_plural`). That
premise-level bug is present in C065's and C066's own premises too — a
conclusion-only equivalence check cannot catch a bug that lives in the
premises. **Corrected verdict: C065 and C066 are real `generic_bare_plural`
failures, not faithful translations.** See
`crest/annotation/kappa_computation_full72.md` for where this was caught.
Only C003, C068, and C069 remain confirmed genuinely faithful across the
entire 72-case set (not 5, as originally reported here and in
`faithful_bucket_verification.md`).

## Result: 12 of 15 are confirmed real failures; 3 are genuinely faithful/equivalent (see correction above — now effectively 13/15, with C065/C066 reclassified)

| Case | Model | Story | Verdict | Reasoning |
|---|---|---|---|---|
| C002 | Llama | Rockie/campus | 🟥 FAIL | Conclusion uses `Turtle(x)`/`Squirrel(x)` as bare unary predicates, but every other premise only ever asserts `SpotNearCampus(x, turtle)`/`(x, squirrel)` — a different predicate entirely. The conclusion's predicates are never grounded by anything in the premise set. |
| C003 | Llama | Rockie/campus (2nd conclusion) | ✅ Faithful | `∃x(Turtle(x) ∧ x=rockie)` is logically equivalent to `Turtle(rockie)` by existential instantiation — an awkward paraphrase, not a meaning change. |
| C005 | Llama | Marvin | 🟥 FAIL | LLM's premise `(A∧B)∨(A→¬B)` is a **tautology** — true under all 4 truth assignments of A,B (verified by full truth-table check). The intended "either both Earth+Mars or neither" constraint is completely eliminated, not just weakened. |
| C020 | Llama | Hydrocarbon mixture | 🟥 FAIL | Same mechanism as C005: `A⊕B → ¬(A∧B)` is a tautology (exclusive-or already implies not-both), so this premise constrains nothing. The "both or neither" state constraint is silently discarded. |
| C021 | Llama | Cancer | 🟥 FAIL | Conclusion is `Cancer(cc) ∧ (Cholangiocarcinoma(cc) ∨ BileDuctCancer(cc) ∨ ∀x(DeadlyDisease(x)→LowSurvivalRate(x)))` — embeds an already-true universal rule as one of the conclusion's own disjuncts, making the whole conclusion trivially satisfied as soon as `Cancer(cc)` holds, regardless of the actual disease-type facts. |
| C022 | Llama | Olympics | 🟥 FAIL | Conclusion `∀x(LastSummerOlympicGames(x)→WonMostMedals(US,x))` over-generalizes a single fact (Tokyo) into a universal law with no supporting rule — not entailed by the premises (a Herbrand model can have another `x` satisfying the antecedent without the consequent). |
| C025 | Llama | Yuri | 🟥 FAIL | Conclusion `∀x(ProfessionalBasketballPlayer(x)∧AmericanNational(x)→¬AmericanNational(yuri))` — a universal rule whose consequent is a fixed claim about a specific individual (Yuri), structurally incoherent relative to gold's simple ground negated-conjunction; not derivable from the premises (nothing connects an arbitrary x's properties to Yuri's own nationality). |
| C030 | gpt-4o-mini | Stranger Things | 🟥 FAIL | `NetflixShow(strangerThings)` is never asserted anywhere in the LLM's premises (only `NetflixShow(blackMirror)` is, about a different show) — rule 2 (`NetflixShow(x)∧PopularShow(x)→BingeWatch`) can never fire for Stranger Things, breaking the whole chain to the conclusion. |
| C037 | gpt-4o-mini | Picuris Mountains | 🟥 FAIL | `Mine(hardingPegmatiteMine)` is never asserted — only `Donated(...)` and `LocatedIn(...)` are. The elimination rule needs `∃y(Mine(y)∧Donated(y))` to derive a contradiction; without the `Mine(...)` fact, Prover9 has no instance to match. |
| C039 | gpt-4o-mini | Peter/classmates | 🟥 FAIL | Conclusion asserts `∃z(...∧TallerThan(z,peter))` — but tracing the premises (Peter > Michael > every classmate, by transitivity) shows Peter is actually taller than *every* classmate, meaning no such `z` exists. This isn't a cosmetic direction swap as first guessed — it flips which side is actually provable. |
| C045 | gpt-4o-mini | Cancer | 🟥 FAIL | Conclusion is `(A∧(B∨C)) ∨ (B∧C)` where gold is `A∧(B∨C)`. The second disjunct omits `A` (`Cholangiocarcinoma`), so when `B∧C` holds but `A` is false, the LLM's formula is true while gold's is false — a genuine weakening, not the harmless redundancy it resembles at a glance. |
| C046 | gpt-4o-mini | Olympics | 🟥 FAIL | Three separate, mutually disconnected constants used for what should be one entity: `LastSummerOlympicGames(wasInTokyo)` (premise), `WonMostMedals(unitedStates, tokyo)` (premise), `WonMostMedals(unitedStates, lastSummerOlympicGames)` (conclusion) — worse than the coreference failure already known for this story (C022/C046/C067 family); this version has three ungrounded symbols instead of two. |
| C058 | gpt-4o | Picuris Mountains | 🟥 FAIL | Same missing-fact bug as C037 (`Mine(hardingPegmatiteMine)` never asserted), confirmed present even in the flagship gpt-4o model on this story — cross-model recurrence of the "precondition injection without instantiation" pattern already dominant in the 🟢 bucket. |
| C065 | gpt-4o | Cancer (conditional variant) | 🟥 FAIL (corrected) | Conclusion formula alone is logically identical to gold's via `A→B≡¬A∨B` — but the shared cancer-story **premises** include `SevereCancer(bileDuctCancer)` as a ground fact (same bug as C021/C045), so the case as a whole is a real `generic_bare_plural` failure. Original "Faithful" verdict only checked the conclusion, missing the premise-level bug — see correction note above. |
| C066 | gpt-4o | Cancer (same story as C045/C021) | 🟥 FAIL (corrected) | Conclusion formula reduces to exactly gold's via a redundant disjunct — but same premise-level `SevereCancer(bileDuctCancer)` bug as C065/C021/C045 makes the case a real failure overall. Original "Faithful" verdict was conclusion-only; see correction note above. |

## Cross-cutting notes

**The "Mine(hardingPegmatiteMine) never asserted" bug appears in both the
gpt-4o-mini (C037) and gpt-4o (C058) versions of the same story** — the
first cross-model confirmation of the "precondition injection without
instantiation" pattern (already dominant in the 🟢-bucket verification)
outside the Llama/mini pairing. This strengthens the case that this is a
general LLM autoformalization failure mode, not specific to weaker models.

**The tautology pattern (C005, C020)** is a new, distinct failure mechanism
from anything previously catalogued: the model preserves an operator
(`⊕`, or a compound implication) syntactically but restructures the
surrounding formula so the whole premise becomes logically vacuous — true
under every assignment, contributing zero constraint. This is worse than
`xor_to_or` (which weakens a constraint) — it eliminates the constraint
entirely while still *looking* like it encodes one. Worth a dedicated
category or at minimum a prominent sub-note; `OTHER` in the current 9-way
schema covers it only by default.

## Combined picture across both verification passes

- 🟢 "Faithful" bucket (20 cases): 18 real failures, 2 confirmed faithful
- 🟨 "Needs scrutiny" bucket (15 cases): 13 real failures, 2 confirmed faithful (corrected — see note above)
- **Combined: 31 of 35 story-level "looks okay" verdicts did not survive a
  derivation-level check.** Only 3 cases across both buckets (C003, C068,
  C069) are confirmed genuinely translation-faithful with a
  still-wrong pipeline verdict — the actual, small set of candidates for a
  non-translation (solver-side or otherwise unexplained) silent failure, if
  any exist at all in this dataset.
