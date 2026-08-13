# GPT-4o FOLIO strict-set silent failures — manual classification

**19 cases** (1 wrong_direction + 18 under_determination), from
`vanilla_pipeline_gpt4o_validation_n203.json` filtered to the strict/verified
set (`ceiling_check_validation.json`: `malformed_gold_fol=False, match=True`).
One analyst, single pass — **needs a second annotator + κ before citing in a
paper** (per the 4-week plan, step 4). This document is that first pass.

Each case's full text (NL premises, conclusion, gold FOL, LLM FOL) is in
`experiments/logs/vanilla_pipeline_gpt4o_validation_n203.json` +
`crest/data/loaders/folio_loader.py` gold data — cross-reference by
`example_id`.

## Category counts

| # | Category | Cases (example_id) | Count | % of 19 |
|---|---|---|---|---|
| 1 | **Generic/bare-plural class-vs-individual ambiguity** — English generic sentences ("Plungers suck", "X are deadly diseases") mistranslated as a ground fact about one individual instead of a universally-quantified rule over a class (or, in one case, the reverse) | 0, 1033, 1034, 389, 578, 806 | **6** | 32% |
| 2 | **XOR (⊕) mistranslated as inclusive OR (∨)** — drops mutual exclusivity | 370, 372, 724 | 3 | 16% |
| 3 | **Predicate-schema divergence** — wholesale predicate substitution or argument-merging that disconnects premises from each other | 442, 443, 361, 441 | 4 | 21% |
| 4 | **Dropped restrictive conjuncts in a quantified antecedent** — universal rule silently over-generalized by dropping a restricting condition | 527, 528 | 2 | 11% |
| 5 | **Entity coreference / definite-description resolution failure** — two names for the same entity not bridged, or a definite description ("the last summer Olympics") not resolved to its known referent | 308, 149 | 2 | 11% |
| 6 | **Missing implicit/common-sense ground facts** — added precondition never explicitly instantiated | 172 | 1 | 5% |
| 7 | **Predicate compound atomization** (matches the earlier taxonomy's dominant category) | 1317 | 1 | 5% |

**Category 1 is the single largest and most novel finding** — not in the
original semantic taxonomy (Section 2 of `docs/CREST_Experimental_Record.docx`),
which focused on quantifier substitution / compound atomization / negation.
This is a *specific, nameable linguistic construction* (English generics and
bare plurals — "Plungers suck", "Cupcakes are baked sweets") that GPT-4o
systematically mishandles at the individual-vs-class level.

## Worked examples (one per category)

### Category 1 — generic/bare-plural ambiguity (example 578, "Space sucks")
```
NL   : Plungers suck. / Vacuums suck. / Vampires suck. / Space is a vacuum.
gold : ∀x (Plunger(x) → Suck(x))
LLM  : Sucks(plunger)                    ← "plunger" treated as ONE individual,
                                            not "for all plungers"
```
Gold label True (space, being a vacuum, sucks by the universal rule). LLM's
ground-fact version can't fire the chain, so Prover9 returns Uncertain.

**Reverse direction, same phenomenon (example 806, "dried Thai chilies")**
```
NL   : Dried Thai chilies are spicy or mala hotpots or not baked sweets.
gold : Spicy(driedThaiChili) ∨ MalaHotpot(driedThaiChili) ∨ ¬BakedSweet(driedThaiChili)
LLM  : ∀x (DriedThaiChili(x) → Spicy(x) ∨ MalaHotpot(x) ∨ ¬BakedSweet(x))
```
Here gold treats "dried Thai chilies" as a single named individual (an
idiosyncratic FOLIO annotation choice, arguably the linguistically *less*
natural reading of an English bare plural), while GPT-4o universally
quantifies it — arguably the more linguistically defensible choice. **This
case is not simply "LLM wrong" — it exposes a genuine annotation-convention
ambiguity in FOLIO's own gold labels for how English generics should be
formalized**, parallel to the ContractNLI gold-label-drift finding in "Know
Your Limits" (71/400 examples relabeled under strict semantics). Worth a
methodological note in the paper: some of the surviving "failures" are
gold-annotation-convention disagreements, not unambiguous model errors — this
should be flagged explicitly rather than silently counted as pure model
failure, and argues for the second annotator pass (step 4) to also review
gold-label defensibility on cases like this one, not just the model's output.

### Category 2 — XOR→OR (example 724)
```
NL   : Events are either happy or sad. / At least one event is happy.
gold : ∀x (Event(x) → Happy(x) ⊕ Sad(x))
LLM  : ∀x (Event(x) → Happy(x) ∨ Sad(x))
```

### Category 3 — predicate-schema divergence (example 442)
```
NL   : The departure and arrival can not be at the same airport.
gold : ∀x∀y (FlyFrom(x,y) ⊕ FlyTo(x,y))
LLM  : ∀x∀y (¬(Departure(x) = Arrival(y)))    ← unrelated predicates,
                                                  disconnected from FlyFrom/FlyTo
```

### Category 4 — dropped restrictive conjunct (example 527/528)
```
NL   : Michael is a man who is taller than everyone else in his class.
gold : ∀x (Man(x) ∧ SameClass(x,michael) ∧ ¬(x=michael) → Taller(michael,x))
LLM  : ∀y (Man(y) → TallerThan(michael,y))    ← "everyone in his class" widened
                                                  to "every man in the world"
```

### Category 5 — coreference (example 308)
```
NL   : Ailton Silva ... commonly known as Ailton. / ... loaned out to Braga.
gold conclusion : ∃x (FootballClub(x) ∧ LoanedTo(ailtonSilva, x))
LLM  conclusion : ∃x (FootballClub(x) ∧ LoanedTo(ailton, x))
```
Interesting edge case: the LLM's FOL is internally *consistent with itself*
(its own premise 2 uses "ailton", and its own conclusion uses "ailton" too —
no self-contradiction), but disagrees with gold's constant-naming choice.
This is genuinely gold=Uncertain (not True) because neither gold's own
premises formally bridge "ailton" and "ailtonSilva" either — so this case is
subtle and worth a second annotator's eyes.

### Category 6 — missing implicit facts (example 172)
```
NL   : When a person reads a book, that person gains knowledge. ...
        Harry read the book "Walden" by Henry Thoreau.
gold : ReadBook(harry, walden) ∧ Book(walden)          ← explicit Book(walden) fact
LLM  : Reads(harry, walden)                             ← Book(walden) never asserted,
                                                             chain rule needs it
```

## What this means for the paper

Category 1 (generics/bare-plurals) deserves its own discussion — it's a
concrete, teachable, previously-undocumented failure mode specific to
naturalistic English, plausibly generalizable beyond FOLIO (any domain with
generic statements: legal clauses like "Employees who violate policy X are
subject to termination" have exactly this class-vs-individual structure).
This is a strong candidate for the paper's "where exactly does frontier still
fail" section, and directly explains part of why synthetic benchmarks
(ProofWriter/PrOntoQA, which are template-generated and rarely use bare
generic constructions) don't show this failure mode while FOLIO does.
