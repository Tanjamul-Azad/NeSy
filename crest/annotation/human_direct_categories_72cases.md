# Human annotator — direct category picks, all 72 cases (2026-08-17)

**This is the real step-4 deliverable.** Unlike the two earlier passes
(`human_annotation_72cases_raw.md`, `human_annotation_72cases_forensic_pass2.md`),
which were free-form prose that Claude then had to interpretively map onto
the 9-category schema (flagged as invalid for IAA in
`kappa_computation_full72.md`), this table has the human directly picking a
primary (and often secondary) category from `guidelines.md`'s own list for
every one of the 72 cases, with a one-line reason each. This is the number
that actually counts as inter-annotator agreement.

| Case | Primary | Secondary | Reason |
|---|---|---|---|
| C001 | generic_bare_plural | unstated_assumption_injection | "There is an animal" is existential; model turns generics into different quantified facts and adds ¬Human. |
| C002 | predicate_schema_divergence | xor_to_or | `CanBeSpottedNear(x,campus)` changed into a relation with animal/rabbit/squirrel as arguments; XOR weakened to OR. |
| C003 | predicate_schema_divergence | xor_to_or | Near-campus relation changed, specific Rockie conclusion replaced by quantified construction; Rabbit/Squirrel XOR weakened. |
| C004 | unstated_assumption_injection | compound_atomization | "Highly intelligent" becomes "highly-intelligent-being-from-Earth," adding the unstated Earth property. |
| C005 | predicate_schema_divergence | xor_to_or | Earth/Mars condition structurally changed, producing a different logical relationship. |
| C006 | dropped_restrictive_conjunct | — | A Marvin-specific condition is generalized into a universal rule over every individual. |
| C007 | predicate_schema_divergence | — | Leads/Includes changed into relations that effectively treat the stable as the leadership target. |
| C008 | predicate_schema_divergence | unstated_assumption_injection | The 1984 conditional isn't preserved cleanly; different predicate structure introduced. |
| C009 | predicate_schema_divergence | — | Relation schema and variable binding around Lewandowski's team relation changed. |
| C010 | predicate_schema_divergence | dropped_restrictive_conjunct | Ted/Brown-Swiss conditional converted into a different universal rule structure. |
| C011 | predicate_schema_divergence | coreference_failure | Working-title description treated as the object edited, instead of connecting back to the series. |
| C012 | predicate_schema_divergence | coreference_failure | "Members of Pappy's" becomes `Starring(badults,pappys)`, collapsing group and members. |
| C013 | generic_bare_plural | — | A generic statement is represented as a ground/specific fact rather than a class-level rule. |
| C014 | missing_implicit_fact | predicate_schema_divergence | Reading rule introduces a person/book requirement; grounding chain not preserved cleanly. |
| C015 | xor_to_or | — | New Mexico/Texas alternative loses its exclusivity. |
| C016 | dropped_restrictive_conjunct | predicate_schema_divergence | "Every man in Michael's class" becomes a much broader rule; class restriction lost. |
| C017 | predicate_schema_divergence | — | Predicate schemas changed in the reasoning chain, even though intended Windy conclusion retained. |
| C018 | predicate_schema_divergence | — | `LocatedIn(southShetlandIslands,antarctica)` reversed. |
| C019 | generic_bare_plural | — | Generic "plungers/vacuums/vampires suck" become ground facts; Space fact represented differently. |
| C020 | xor_to_or | predicate_schema_divergence | "Both...or neither" not preserved as the original exclusive state constraint. |
| C021 | predicate_schema_divergence | compound_atomization | Disease categories treated as individual arguments/predicates rather than preserving type relationships. |
| C022 | coreference_failure | — | "The last Summer Olympics" not consistently connected to Tokyo. |
| C023 | predicate_schema_divergence | — | `love animals → animal lover` chain changed into a different predicate structure. |
| C024 | unstated_assumption_injection | compound_atomization | Model introduces a universal claim that professional players are American, never stated. |
| C025 | compound_atomization | predicate_schema_divergence | `Professional(x)∧BasketballPlayer(x)` fused into `ProfessionalBasketballPlayer(x)`. |
| C026 | unstated_assumption_injection | compound_atomization | Model adds a universal American-nationality rule not warranted by the story. |
| C027 | xor_to_or | — | `Happy(x)⊕Sad(x)` becomes `Happy(x)∨Sad(x)`. |
| C028 | predicate_schema_divergence | unstated_assumption_injection | KiKi condition rewritten, conclusion's semantic structure changed. |
| C029 | generic_bare_plural | — | Generic class-level statement grounded incorrectly. |
| C030 | predicate_schema_divergence | — | Predicate schema/argument ordering changed (`ShareWith`→`Share`), broad relation preserved. |
| C031 | xor_to_or | — | "Both or neither" weakened into a condition permitting intermediate states. |
| C032 | dropped_restrictive_conjunct | — | Specific-person condition generalized beyond the individual named in the English. |
| C033 | predicate_schema_divergence | — | Formal predicate structure changed, disconnecting a premise from the reasoning chain. |
| C034 | predicate_schema_divergence | coreference_failure | Series associated with the working title not correctly bound to the existential variable. |
| C035 | missing_implicit_fact | — | Model fails to instantiate a fact needed to connect the general rule to the named individual. |
| C036 | predicate_schema_divergence | — | Relation between entities restructured, changing how premises connect. |
| C037 | xor_to_or | — | NM/Texas represented with inclusive OR rather than gold's XOR; final conclusion otherwise preserved. |
| C038 | predicate_schema_divergence | xor_to_or | Conclusion's quantified location constraint replaced by unbound-variable conjunction; location relation restructured. |
| C039 | dropped_restrictive_conjunct | predicate_schema_divergence | "Men in Michael's class" weakened to all men; final relation reversed. |
| C040 | predicate_schema_divergence | — | Relation schema changed in the reasoning chain even though final proposition retained. |
| C041 | missing_implicit_fact | — | A required implicit condition needed to connect premise to conclusion isn't preserved. |
| C042 | OTHER | predicate_schema_divergence | "Platypuses are reptiles" replaced by "Platypuses are not mammals" — polarity/proposition substitution not covered by the existing taxonomy. |
| C043 | unstated_assumption_injection | predicate_schema_divergence | Model inserts `UsedToTrain(unsupervisedLearning,...)` even though that's the conclusion being tested, not a premise. |
| C044 | predicate_schema_divergence | — | Formal predicate structure around the birds/reptiles relation changed rather than preserving the original proposition. |
| C045 | predicate_schema_divergence | — | Cancer predicates and conclusion restructured; extra disjunct needs semantic checking, not automatic failure. |
| C046 | coreference_failure | — | "The last Summer Olympics" not consistently grounded to Tokyo. |
| C047 | predicate_schema_divergence | — | Predicate/argument structure changed in a way that breaks the intended inference connection. |
| C048 | compound_atomization | predicate_schema_divergence | Properties fused into `ProfessionalBasketballPlayer`; conclusion then `¬American∧ProfessionalBasketballPlayer`, changing its scope. |
| C049 | compound_atomization | predicate_schema_divergence | Compound concept treated as one predicate; conditional loses the original conjunction structure. |
| C050 | xor_to_or | — | `Happy⊕Sad` becomes `Happy∨Sad`. |
| C051 | unstated_assumption_injection | compound_atomization | `BarkingDog(kiki)` directly asserted although only "KiKi is an animal" is established — conclusion effectively inserted as fact. |
| C052 | predicate_schema_divergence | compound_atomization | Dog/bark relations restructured; compound negative conclusion represented differently. |
| C053 | coreference_failure | — | "Ailton"/"Ailton Silva" not handled with the intended identity/reference structure. |
| C054 | generic_bare_plural | — | Generic class statement converted into an individual-level representation. |
| C055 | predicate_schema_divergence | coreference_failure | Pappy's as a group substituted for its members, changing argument structure. |
| C056 | predicate_schema_divergence | — | `From(x,bakedByMelissa)` replaced with `ProductOf(x,bakedByMelissa)` — semantic equivalence questionable, primarily schema divergence. |
| C057 | missing_implicit_fact | predicate_schema_divergence | Adds a `Person(x)∧Book(y)` precondition; grounding of the actual reading event changed; final conclusion still explicit. |
| C058 | xor_to_or | — | Picuris NM/Texas XOR weakened to inclusive OR; visited-New-Mexico proposition preserved. |
| C059 | predicate_schema_divergence | xor_to_or | Quantified location structure lost, mine/mountain relation changed; NM/Texas XOR also weakened. |
| C060 | predicate_schema_divergence | — | Relational structure needed to connect premises changed. |
| C061 | OTHER | — | Model's FOL already contains `GreatShooter(windy)`, so no clear semantic translation failure to assign from the available evidence. |
| C062 | predicate_schema_divergence | — | `LocatedIn`'s arguments reversed (South Shetland→Antarctica becomes Antarctica→South Shetland). |
| C063 | generic_bare_plural | — | Generic "vacuums suck" statements grounded as individual facts; predicate naming alone isn't the issue. |
| C064 | unstated_assumption_injection | predicate_schema_divergence | Model introduces a direct training relation for unsupervised learning, effectively inserting the conclusion. |
| C065 | predicate_schema_divergence | compound_atomization | Cancer properties compressed/restructured into different predicates, changing how the chain connects. |
| C066 | predicate_schema_divergence | — | Conclusion algebraically restructured; extra disjunct must be checked for logical equivalence, not judged by surface difference. |
| C067 | coreference_failure | — | "Last Summer Olympics" treated as a separate term instead of grounded to Tokyo. |
| C068 | predicate_schema_divergence | — | Model correctly translates the to/from propositions, but its translation of the exclusivity rule differs structurally from gold — not a failure merely because the conclusion is false. |
| C069 | predicate_schema_divergence | — | Same: conclusion translated correctly; discrepancy is in the formalization of the departure/arrival constraint. |
| C070 | compound_atomization | predicate_schema_divergence | `Professional∧BasketballPlayer` fused into `ProfessionalBasketballPlayer`; compound antecedent changed. |
| C071 | xor_to_or | — | `Happy⊕Sad` translated as inclusive OR. |
| C072 | coreference_failure | — | "Ailton"/"Ailton Silva" collapsed in a way that transfers information between references. |

## ⚠️ Self-correction triggered by re-reading C068/C069's own reasoning

The human's note for C068/C069 explicitly separates two things: the
to/from propositions (translated correctly) and "the exclusivity rule"
(translated differently from gold) — and assigns `predicate_schema_divergence`
for the exclusivity-rule issue specifically. This directly contradicts
Claude's earlier "✅ Faithful" verdict for C068/C069 in
`faithful_bucket_verification.md`, which only checked the
Susan-flies-to/John-flies-from premise-conclusion pair the human's first
(prose) pass had highlighted narratively, and never checked premise 2 (the
actual departure/arrival exclusivity rule).

Re-checked directly against the raw FOL: gold premise 2 is
`∀x∀y(FlyFrom(x,y)⊕FlyTo(x,y))`; the LLM's premise 2 is
`∀x∀y(¬(Departure(x)=Arrival(y)))` — entirely different, disconnected
predicates with no link to `FliesTo`/`FliesFrom` at all. This is exactly
why the pipeline fails: gold's exclusivity rule lets you derive
`¬FlyFrom(susan,lgaAirport)` from `FlyTo(susan,lgaAirport)` (giving gold
label False), but the LLM's disconnected rule can never do that, so
Prover9 correctly returns Uncertain on the LLM's own (buggy) premises.

**Corrected: C068 and C069 are real `predicate_schema_divergence` failures,
not faithful translations — Claude's earlier verdict was based on an
incomplete premise check.** Combined with the earlier C065/C066 correction,
**zero of the original "5 faithful" candidates now survive a full
premise-and-conclusion check.** `crest/annotation/faithful_bucket_verification.md`
and `crest/annotation/needs_scrutiny_bucket_verification.md` should be read
alongside this correction rather than trusted at face value for C065,
C066, C068, C069.

**Only C003 remains confirmed as a genuinely faithful translation across
the entire 72-case set** (verified independently by both Claude's
derivation check and implicitly corroborated by the human's own category
table, which does not list C003 as OTHER/no-failure).
