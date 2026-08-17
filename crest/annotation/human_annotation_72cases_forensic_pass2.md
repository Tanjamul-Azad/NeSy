# Human annotator — forensic second pass, 3-way bucketed (2026-08-17)

**Follow-up to `human_annotation_72cases_raw.md`.** Same human annotator,
same 72 cases, much more careful per-case derivation-style reasoning this
time, organized into three buckets instead of free-form notes. This pass
introduced a key methodological correction (see below) now adopted project-
wide.

**IMPORTANT — see `faithful_bucket_verification.md` for a systematic check
of the 🟢 bucket below.** Claude hand-traced all 20 "Faithful" cases against
the model's own FOL and found 18 have a genuine, locatable translation bug
that the story-level reading in this document missed (missing precondition
instantiation, predicate-name mismatches, reversed relation arguments,
self-negated conclusions). Only C068 and C069 hold up as genuinely
faithful. This does not diminish the value of this pass — the 🟥 and 🟨
bucket assignments, and especially the C068/C069 methodological insight
below, remain sound and important — but the 🟢 bucket specifically should
not be used as-is; use the verified version in `faithful_bucket_verification.md`.

---

## The key methodological correction: false conclusion ≠ translation failure

C068 (Susan/LGA) and C069 (John/LGA) are the clearest examples. Story:
"Susan flies to LGA." Conclusion: "Susan flies from LGA." Gold keeps these
as two distinct, unconnected predicates (`FlyTo`/`FlyFrom`) — the
conclusion doesn't follow, and isn't meant to. The model translates both
sentences correctly and literally (`FliesTo(susan,lga)` /
`FliesFrom(susan,lga)`), matching gold's structure. The conclusion being
false is the point of the test case, not evidence the model mistranslated
anything.

**This means the correct annotation test is three questions, not one:**
1. Is the premise's meaning encoded correctly?
2. Is the conclusion's literal English meaning encoded correctly (not
   pre-judged true/false by the model itself)?
3. Has the premise–conclusion relationship been changed?

Never: "does the final pipeline label match gold" — that conflates
translation quality with the actual entailment question the solver is
supposed to answer.

## Bucket summary (as originally assigned by the human; see verification note above for 🟢)

**🟥 Genuine semantic translation failure (confirmed):**
C001, C004, C006, C007, C009, C010, C011, C012, C015, C016, C018, C024,
C026, C027, C028, C031, C032, C034, C038, C042, C043, C048, C049, C051,
C053, C055, C059, C062, C064, C067, C070, C071, C072

**🟨 Needs semantic scrutiny / partial (formula differs, meaning-equivalence
not yet fully resolved):**
C002, C003, C005, C020, C021, C022, C025, C030, C037, C039, C045, C046,
C058, C065, C066

**🟢 Faithful / no semantic translation failure (as originally claimed —
see verification file, 18/20 do not survive a derivation check):**
C013, C014, C017, C019, C023, C029, C033, C035, C036, C040, C041, C044,
C047, C054, C056, C057, C061, C063, C068, C069

## Selected per-case reasoning (representative examples, not exhaustive)

**C001** — Model adds `¬Human(x)` to `∃x(Animal(x))`, inventing information
the story never states ("animal" could include humans; the story never
restricts it). Over-specification / negation insertion.

**C007** — `Leader(diamondMine, roderickStrong)` + `Member(diamondMine,
creedBrothers)` conjoined in the conclusion as if leadership transfers to
members — an unsupported relational inference the premises never license.

**C009** — Predicate schema (`LeftTeam`/`PlayFor` vs gold's `Left`/
`PlaysFor`) and variable binding (`y` in the rule) both unstable; "this
can't just be called a solver issue" — the annotator's own words, matching
Claude's earlier finding on this case.

**C015 / C037 / C058** — Picuris Mountains: exclusive-or (New Mexico XOR
Texas) weakened to inclusive-or throughout, though the final conclusion
sometimes still comes out right by coincidence — flagged as "the final
conclusion happening to match doesn't mean the constraint was translated
correctly."

**C043 / C064** — Unsupervised-learning ML story: model inserts the literal
conclusion (`UsedToTrain(unsupervisedLearning, ...)`) as if it were a given
premise, rather than a fact to be derived. "The model has effectively
written the answer into the translation" — conclusion leakage.

**C045 / C066** — Cancer conjunction/disjunction restructuring: annotator's
explicit rule here is important — check what worlds satisfy the formula,
don't just eyeball whether it "looks" different from gold. Some
restructurings turn out to be logically redundant (harmless), others
genuinely change which worlds satisfy the formula (real failure). Case-by-
case, not formula-length-based.

**C048 / C049 / C070** — Yuri American-basketball-player story: negation
moved inside a conjunction (`¬(A∧B∧C)` became `¬A ∧ B ∧ C`), a "classic
negation-scope failure" that changes the proposition rather than merely
restating it.

**C053 / C072** — Ailton/Ailton Silva: the story is deliberately testing
whether the annotator (human or model) will collapse a stated
"commonly known as" relationship into full identity. The model collapses
it; the annotator explicitly warns not to make the same collapse when
grading.

**C068 / C069** — see methodological correction section above.
