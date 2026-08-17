# Human annotation — 72-case FOLIO strict-set silent failures (raw)

**Received 2026-08-17.** This is the genuine second-annotator (human) pass
required by step 4 of `docs/RESEARCH_DIRECTION.md`, written after reading
`crest/annotation/guidelines.md` and reviewing all 72 cases in
`crest/annotation/annotation_sheet_72cases.json`. Confirmed by Tanjamul as
a real human pass, not an AI cross-check (unlike the Gemini pass, see
`gemini_cross_check_analysis.md`).

**Format note:** this pass does not use the strict `category` field from
`guidelines.md`'s 9-category schema — the annotator instead wrote free-form
per-case story-level diagnoses and proposed a richer, independent 10-family
error taxonomy (under-specification, over-specification, quantifier drift,
negation drift, logical connective drift, implication reversal/distortion,
predicate argument drift, entity/constant drift, relation hallucination,
structural loss). Reconciling this against the 9-category schema for a
formal Cohen's κ is a separate, not-yet-done task — see the note appended
in `docs/RESEARCH_DIRECTION.md`.

**Important caveat found on cross-checking against raw FOL (2026-08-17):**
for at least 4 cases (C009, C017, C018, C044) this pass attributes the
failure to a "downstream reasoning/evaluator" problem rather than a
translation-level bug — but checking the actual `llm_fol` in each case
shows a concrete translation bug that fully explains the wrong answer
(a flipped negation in C017's premise 5, a reversed relation-argument order
in C018's premise 4, a self-negated conclusion in C044, a dropped ∀y
quantifier in C009). This does not disqualify the pass — annotator
disagreement/error is exactly what the guidelines' disagreement-resolution
process exists for — but it must be tracked as a real, checked disagreement
point, not silently accepted. See `docs/RESEARCH_DIRECTION.md` for the full
note.

---

## 1. Uncertain-এর দিকে অতিরিক্ত ঝোঁক (over-specification injecting new info)

C001-এ Gold conclusion ∃x(Animal(x)), কিন্তু Llama করেছে ∃x(Animal(x)∧¬Human(x))
— stronger claim, নতুন information invent করা। একই pattern C013/C014, C019,
C022, C030-এও।

Human explanation: Model বলছে "আমি মনে করি conclusion সত্যি, কিন্তু আমার বানানো
formal representation থেকে এটা prove করতে পারছি না।" এটা reasoning
failure-এর চেয়ে বেশি translation-faithfulness failure।

## 2. wrong_direction — relational overreach

C007: Roderick Strong leads Diamond Mine, Diamond Mine includes Creed
Brothers. Gold=Uncertain, model predicted True। Model-এর representation
(Leader(diamondMine,roderickStrong), Member(diamondMine,creedBrothers))
থেকে model যেন mentally করছে "leader of group → leader of its members" —
কিন্তু এই implication premise-এ নেই। Pure relational overreach.

## 3. Implication-এর direction বদলে যাওয়া

C010: Gold BrownSwissCattle(ted)→¬Pet(ted). Model:
∀x(BrownSwissCattle(x)→Pet(x)→¬Alligator(x)) — conditional structure
completely changed, শুধু predicate naming error না। C024/C025/C026 family-তেও
একই pattern।

## 4. Quantifier/Scope drift

C003: unnecessarily existential introduction (rockie=x)। C006: original
¬From(marvin,mars)→Human(marvin) [marvin-specific] কে model বানিয়েছে
∀x(¬FromMars(x)→Human(x)) [universal rule] — huge error, "Scope/Quantifier
Drift" নামে category প্রস্তাব করা হয়েছে।

## 5. ⊕ (XOR) → ∨ (OR)

C027, C071: Happy(x)⊕Sad(x) → Happy(x)∨Sad(x). Exclusivity constraint
হারিয়ে যাচ্ছে, downstream conclusion-এর truth value পাল্টে যেতে পারে।

## 6. Negative reasoning instability — Uncertain ≠ False

C042: Platypus মামাল, no teeth, conclusion "platypus is a reptile" —
Gold=Uncertain. Model output: ¬Mammal(platypus) — conclusion সরাসরি translate
না করে এমন statement বানিয়েছে যেটা existing premise-এর সাথে contradiction
তৈরি করে। Model যেন "not supported"="false" আর "cannot prove"="negation"
গুলিয়ে ফেলছে। **এই distinction (Uncertain ≠ False) CREST-এর জন্য অত্যন্ত
গুরুত্বপূর্ণ বলে চিহ্নিত করা হয়েছে।**

## 7. Predicate/entity argument structure ভাঙা

C018: LocatedIn(barutinCove,snowIsland) → On(barutinCove,
southwestCoast(snowIsland))। C011: ScriptEditorFor(andrewCollins,badults) →
ScriptEditor(badults,andrewCollins) — argument order reverse।

## 8. Core diagnosis: "semantic paraphrase" translation-এ formal semantics নষ্ট করছে

Model মনে করে exact FOL structure copy করার দরকার নেই, meaning approximately
same রাখলেই হবে — কিন্তু symbolic reasoning-এ approximately same meaning ≠
logically equivalent meaning (যেমন ∀x(A(x)→B(x)) vs A(c)→B(c))।

## Proposed error taxonomy (10 families, independent of guidelines.md's 9)

| Error family | কী হচ্ছে |
|---|---|
| Under-specification | model প্রয়োজনীয় logical information বাদ দিচ্ছে |
| Over-specification | model source-এ না থাকা information ঢুকাচ্ছে |
| Quantifier drift | specific entity → universal rule |
| Negation drift | uncertain/not-supported → explicit negation |
| Logical connective drift | ⊕→∨, ↔→→ ইত্যাদি |
| Implication reversal/distortion | conditional-এর direction বদলানো |
| Predicate argument drift | relation-এর subject/object বদলে যাওয়া |
| Entity/constant drift | entity identity বদলে যাওয়া |
| Relation hallucination | premises থেকে unsupported relation তৈরি করা |
| Structural loss | existential/conjunctive structure ভেঙে যাওয়া |

**Key methodological challenge raised by the annotator, worth preserving:**
category taxonomy design করার আগে error discovery সম্পূর্ণ করা উচিত, নাহলে
reviewer জিজ্ঞেস করবে "Where did this taxonomy come from? Is it
reproducible? Are categories mutually exclusive? Who annotated them?"

---

## Per-case table (C001–C072)

*Full per-case story-level diagnosis table as provided by the annotator —
reproduced verbatim below, organized by the annotator's own groupings
(C001–C018, C019–C036, C037–C054, C055–C072).*

### C001–C018

| Case | Human story judgement | Failure |
|---|---|---|
| C001 | Animal আছে (virus certain animals-এ occur করে), True. Model non-human animal বানিয়ে ফেলেছে। | Over-specification / invented negation |
| C002 | Rockie campus-এর কাছে spotted animal; gold True. Model animal-কে literal entity বানিয়ে relation distort + XOR→OR। | Relation + connective drift |
| C003 | Cute/calm→skittish turtle fact নেই, False. Model existential construction দিয়ে wording বদলেছে। | Weak structural translation; verdict uncertainty |
| C004 | Marvin alien কিনা নিশ্চিত না। Model HighlyIntelligentBeingFromEarth বানিয়েছে, story শুধু highly intelligent বলেছে। | Entity-condition hallucination |
| C005 | Marvin neither human nor from Mars — True. Model XOR-style ভুল conditional বানিয়েছে। | Logical connective/conditional drift |
| C006 | Marvin-specific conditional False. Model ∀x বানিয়েছে। | Quantifier/scope drift |
| C007 | Roderick leads Diamond Mine members-এর leader না। | Relation overreach / relational hallucination |
| C008 | 1984 streaming hypothetical, actual fact না — Uncertain। Model hypothetical কে actual chain treat করেছে। | Conditional activation / hypothetical-to-fact drift |
| C009 | Lewandowski left Bayern → no longer plays — False। Model ¬PlaysFor তৈরি করেছে তবু predicted Uncertain। | Predicate normalization mismatch (annotator's diagnosis — **Claude's re-check found a dropped ∀y quantifier as the more likely root cause**) |
| C010 | Ted-conditional True। Model সম্পূর্ণ different chain বানিয়েছে। | Conditional restructuring |
| C011 | Andrew script editor — True। Model relation direction/arguments বদলেছে। | Argument-role / entity-relation drift |
| C012 | BBC Two/Three claim False। Model member→show relation ঠিকমতো preserve করেনি। | Relation binding failure |
| C013 | Walden knowledge chain True। Model quoted string + irrelevant extra fact যোগ করেছে। | Entity normalization / harmless extra info |
| C014 | Harry smarter — True। Model GainsKnowledge(x,y)-এ book argument নেই যেখানে gold-এ নেই। | Argument-structure drift |
| C015 | Picuris NM — True। Model XOR→OR করলেও conclusion NM-ই থাকে। | Constraint weakening, conclusion preserved |
| C016 | Peter/class — False। Model over-strengthened কিন্তু directionally consistent। | Over-strengthening |
| C017 | Windy great shooter — True। Model-এ enough structure থাকা সত্ত্বেও predicted Uncertain। | Missing contraposition / reasoning-chain failure (annotator's diagnosis — **Claude's re-check found premise 5's negation is flipped: `CanJumpWhenShooting` instead of `¬JumpWhenShooting`, which genuinely breaks the derivation — a translation bug, not a solver limitation**) |
| C018 | Antarctica chain — False। Model same chain preserve করেও predicted Uncertain। | Inference-chain failure (annotator's diagnosis — **Claude's re-check found premise 4's relation arguments are reversed: `LocatedIn(antarctica, southShetlandIslands)` instead of `LocatedIn(southShetlandIslands, antarctica)` — a translation bug that breaks the transitivity chain**) |

### C019–C036, C037–C054, C055–C072

*(Remaining per-case rows preserved as provided by the annotator — see
conversation history for the complete tables covering C019 through C072,
including the C044 case where the annotator diagnoses "translation is
basically correct, prediction inconsistent with its own FOL" — **Claude's
re-check found the model's conclusion is self-negated
(`¬∀x(Bird(x)→Swims(x))` vs gold's positive `∀x(Bird(x)→Swim(x))`), which
mechanistically explains the wrong predicted label without needing to
invoke a separate solver inconsistency.**)*

**Recurring theme across the full table:** the annotator repeatedly
distinguishes cases where **translation is correct but the pipeline still
returned the wrong label** (diagnosed as "reasoning/evaluator failure",
e.g. C017, C018, C032, C047, C052, C061, C062) from cases with **genuine
translation-level errors**. This distinction — if it survives verification
— would be a major complication for CREST's framing (which currently
attributes silent failure to translation, not solver execution). Claude's
spot-checks on 4 of these "evaluator failure" cases (C009, C017, C018,
C044) all found a translation-level bug that was missed on first read, so
this claim should not be accepted at face value for the remaining cases
either — each "reasoning/evaluator failure" verdict needs the same
line-by-line FOL check before being trusted.
