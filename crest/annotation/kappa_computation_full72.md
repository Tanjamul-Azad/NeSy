# Full 72-case Cohen's κ computation (2026-08-17)

**Script:** the computation lives in the conversation history; the raw
per-case category arrays for Claude, Gemini, and the human-interpreted
mapping are reproduced below for reproducibility. Uses `cohens_kappa()` from
`crest/crest/evaluation/stats.py`.

## Results

| Pair | n | categories | po | pe | κ | interpretation |
|---|---|---|---|---|---|---|
| Claude vs Gemini | 72 | 8 | 0.736 | 0.150 | **0.690** | substantial |
| Human vs Claude | 72 | 10 | 0.847 | 0.124 | **0.826** | almost perfect |
| Human vs Gemini | 72 | 10 | 0.653 | 0.124 | **0.604** | substantial |

## ⚠️ Critical caveat on "Human vs Claude" and "Human vs Gemini" — read before citing either number

**The human annotator never picked one of the 9 category names directly.**
Both rounds of the human's pass (`human_annotation_72cases_raw.md`,
`human_annotation_72cases_forensic_pass2.md`) are free-form prose diagnoses
("relation direction reversed", "quantifier/scope drift", "unsupported
relational inference"), not a selection from `guidelines.md`'s fixed
category list. **Claude mapped each of those 72 prose diagnoses onto the
9-category schema** to make this computation possible.

This means the "Human vs Claude" κ = 0.826 is not a genuine independent
inter-annotator statistic — it is closer to **Claude's own interpretation
of the human's text, measured against Claude's own labels**, with Claude
sitting on both sides of the comparison. It is vulnerable to exactly the
confirmation bias this project's rigor standard exists to catch, and **must
not be cited as a validated IAA result in the paper or thesis.** The "Human
vs Gemini" number carries the same caveat (same human-side mapping used).

**What this computation is actually useful for:**
- It's a sanity check that the human's underlying diagnoses, once
  translated into the schema's vocabulary, land in the same
  neighborhood as Claude's and Gemini's independent labels most of the
  time (only 11/72 disagreements against Claude, mapped by Claude) — a
  mild positive signal that the 9-category schema has enough resolution
  to capture what the human actually saw, not that annotators agree.
- It surfaces where Claude's own mapping was uncertain (see
  `Human vs Claude` disagreement list below) — several of these
  disagreements are Claude's own `OTHER` bucket catching genuinely novel
  mechanisms (constraint-to-tautology collapse in C005/C006, negation-scope
  errors) that the fixed 9-category schema doesn't yet name.

**What is still needed for a citable κ:** send the human the 9 category
names and definitions directly (already in `guidelines.md`) alongside the
72 cases, and have them pick one category per case themselves — no
Claude-authored intermediate mapping. Only that number is valid IAA.

## Self-correction made during this mapping pass

While building the human-side array, a gap was found in the earlier
`needs_scrutiny_bucket_verification.md`: C065 and C066 were marked
"✅ Faithful" there based on checking only the *conclusion* formula's
logical equivalence to gold. But both cases share the same cancer-story
premises as C021/C045, which were already confirmed to contain the
`SevereCancer(bileDuctCancer)` ground-fact-instead-of-rule bug
(`generic_bare_plural`). That premise-level bug is present in C065/C066's
premises too — the conclusion-only equivalence check was too narrow and
missed it. **Corrected: C065 and C066 are real `generic_bare_plural`
failures, not faithful translations.** Only 3 cases across the entire
72-case set are now confirmed genuinely translation-faithful with a
still-wrong pipeline verdict: **C003, C068, C069** (previously reported as
5; this correction removes C065/C066 from that count).

## Human category distribution (Claude's mapping)

| Category | Count |
|---|---|
| OTHER | 12 |
| compound_atomization | 11 |
| predicate_schema_divergence | 10 |
| missing_implicit_fact | 8 |
| generic_bare_plural | 8 |
| xor_to_or | 7 |
| dropped_restrictive_conjunct | 6 |
| coreference_failure | 5 |
| faithful_no_error | 3 |
| unstated_assumption_injection | 2 |

`OTHER` being the single largest bucket (12/72, 17%) is itself a finding:
the 9-category schema, even after two rounds of independent human
diagnosis, doesn't yet name several recurring mechanisms cleanly
(constraint-to-tautology collapse, conclusion-polarity pre-judgment,
negation-scope errors, biconditional over-strengthening). Expanding the
schema before the paper's taxonomy section is finalized is worth
considering, informed by these `OTHER` cases specifically.

## Human vs Claude disagreements (11/72)

| Case | Human (Claude's mapping) | Claude |
|---|---|---|
| C001 | unstated_assumption_injection | predicate_schema_divergence |
| C003 | faithful_no_error | predicate_schema_divergence |
| C005 | OTHER | compound_atomization |
| C006 | OTHER | compound_atomization |
| C030 | missing_implicit_fact | dropped_restrictive_conjunct |
| C033 | OTHER | predicate_schema_divergence |
| C037 | missing_implicit_fact | xor_to_or |
| C043 | unstated_assumption_injection | generic_bare_plural |
| C045 | compound_atomization | generic_bare_plural |
| C068 | faithful_no_error | predicate_schema_divergence |
| C069 | faithful_no_error | predicate_schema_divergence |

Most of these are defensible primary-vs-secondary disagreements (e.g. C045
has both a `compound_atomization` fusion in its rule and a
`generic_bare_plural`-adjacent structural issue in its conclusion — which
one is "primary" is a judgment call) rather than one side being flatly
wrong, consistent with the framing above: this comparison measures
schema-mapping consistency, not real inter-annotator agreement.
