# Annotation protocol — silent-failure semantic taxonomy

**Purpose:** a second annotator independently classifies the same cases the
first pass (Claude, 2026-08-03) already classified, so an inter-annotator
agreement statistic (Cohen's κ, target ≥ 0.6) can be computed before this
taxonomy is used in the paper. Until κ is measured, the taxonomy is a
single-analyst hypothesis, not a validated finding — treat it that way in
any writing that cites it before this process completes.

## What you are classifying

Each case is one FOLIO example where a model's whole-story FOL translation
led to a **silent failure**: the solver accepted the translated formulas
without error, but the resulting label disagreed with the gold label. Your
job is not to re-judge whether the model was right or wrong (the label
disagreement is already established) — it is to identify **which specific
translation error caused the disagreement**, by comparing the gold FOL to
the model's FOL line-by-line against the natural-language premises.

## Procedure

1. Read the NL premises and conclusion first, form your own understanding
   of what they mean.
2. Compare gold FOL to model FOL, premise by premise, then the conclusion.
3. Identify the primary category (below) that explains the disagreement. If
   more than one category applies, pick the one that is the *root cause* —
   the one that, if fixed, would most likely have fixed the outcome — and
   note the secondary category in the `secondary_category` field.
4. **Separately from the category**, answer one more question for every
   case: **is the gold label itself defensible, or does this case look like
   a FOLIO annotation-convention issue** (see category 1's worked example,
   "dried Thai chilies", for what this looks like)? Mark
   `gold_label_defensible: yes/no/unsure`. This is not optional — the first
   pass already found one case where the answer is plausibly "no", and
   silently assuming every gold label is correct would bias the whole
   taxonomy.
5. If a case doesn't cleanly fit any category, use `category: OTHER` and
   describe it in `notes` rather than forcing a fit — a forced-fit label is
   worse than an honest "doesn't fit," and new categories emerging from your
   pass are a legitimate and expected outcome, not a failure of the
   protocol.

## Category definitions (from the first pass, 19 FOLIO×GPT-4o cases)

Full worked examples for each: `crest/annotation/gpt4o_folio_strict_failures_classified.md`.

1. **generic_bare_plural** — an English generic/bare-plural sentence
   ("Plungers suck", "Cupcakes are baked sweets") gets mistranslated between
   a ground fact about one named individual and a universally-quantified
   rule over a class, in either direction.
2. **predicate_schema_divergence** — the model substitutes, merges, or
   restructures predicates/arguments in a way that disconnects premises from
   each other (e.g. a type name moved from predicate position into an
   argument position; two predicates fused into one with a different arity).
3. **xor_to_or** — FOLIO's `⊕` (exclusive or) is translated as `∨`
   (inclusive or), dropping mutual exclusivity. Check carefully: a `⊕`
   inside a negation sometimes has a *correct* DNF expansion that looks
   different from the source but is logically equivalent — verify it's
   actually wrong before tagging this category (the first pass found at
   least one case where an apparent XOR-flavoured rewrite was actually
   correct).
4. **dropped_restrictive_conjunct** — a universally-quantified rule's
   antecedent silently loses a restricting condition (e.g. "every man in
   Michael's class" becomes "every man"), over-generalizing the rule.
5. **coreference_failure** — two different names/descriptions for what the
   text treats as the same entity (or a definite description like "the last
   summer Olympics") are not bridged to a shared constant.
6. **missing_implicit_fact** — the model's rule correctly adds a
   precondition the English implies (e.g. "person" in "when a person reads a
   book"), but never explicitly instantiates that precondition for the
   specific individual in the story, breaking the inference chain.
7. **compound_atomization** — two or more separate properties get fused
   into one compound predicate name (e.g. `ProfessionalBasketballPlayer(x)`
   instead of `Professional(x) ∧ BasketballPlayer(x)`), preventing that
   predicate from combining with other premises that only assert one of the
   fused properties.
8. **unstated_assumption_injection** — the model's translation adds a fact
   or constraint that is not warranted by the NL at all (the opposite
   direction from category 6 — here something is added, not omitted). Seen
   in the first pass but not yet given its own category there; flagged here
   as a category to watch for, since a second annotator may find more of
   these.
9. **OTHER** — doesn't fit the above; describe in `notes`.

## Disagreement resolution

Where your category differs from the first pass's, do not silently defer
to whichever came first. Both analysts state their reasoning in one or two
sentences; a third party (Tanjamul, or by discussion between the two
annotators) makes the final call for that case, and the reasoning is kept
in the record rather than only the final label — a disagreement that gets
resolved without keeping the reasoning trail is a disagreement that will
recur.

## Computing agreement

Cohen's κ over the `category` field (9 possible categories, treat OTHER as
its own category for this calculation). Target κ ≥ 0.6 ("substantial
agreement" on the standard Landis & Koch scale) before citing the taxonomy
as validated in the paper. If κ is lower, that is a real, reportable result
— it means the category definitions need tightening, not that the
disagreement should be hidden. `crest/crest/evaluation/stats.py` does not
currently have a κ function; a straightforward implementation (agreement
matrix, no chance-correction subtleties needed for two raters on nominal
categories) should be added there before this is computed, not done
ad hoc in a notebook that isn't checked in.

## Data files

- **Cases to annotate:** `crest/annotation/annotation_sheet_72cases.json`
  — 72 cases (28 Llama-3.1-8B + 25 GPT-4o-mini + 19 GPT-4o), all drawn from
  FOLIO's strict/verified set (gold-FOL-grounding already confirmed correct
  in Phase 2.1), across all three models so the taxonomy is checked at every
  capability level, not just frontier. Each has NL premises, NL conclusion,
  gold FOL, and the model's FOL already filled in; `category`,
  `secondary_category`, `gold_label_defensible`, and `notes` are blank for
  you to fill in.
- **First pass reference (19 cases, GPT-4o only):**
  `crest/annotation/gpt4o_folio_strict_failures_classified.md` — has the
  worked examples for each category. **Do not look at this file's specific
  case-by-case labels before doing your own pass on those same 19 cases** —
  read it for the category definitions and examples only, then classify
  independently, or the agreement statistic measures nothing.
