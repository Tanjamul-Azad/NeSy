# Gemini cross-check of the 72-case taxonomy — analysis

**2026-08-13.** Tanjamul obtained a full 72-case classification from Gemini
(external, via a separate chat) using `crest/annotation/guidelines.md` and
the blank sheet. This is **not** the human second-annotator pass step 4's
protocol calls for — see the validity caveat below — but it's a genuinely
useful pilot signal, and it surfaced two confirmed classification errors
worth recording. Raw responses: `crest/annotation/gemini_cross_check.json`.

## Agreement on the 19 cases Claude already classified (step 2)

The only cases where an independent reference exists are the 19 GPT-4o
cases (`C054`–`C072` in the 72-case numbering), classified by Claude in step
2 (`gpt4o_folio_strict_failures_classified.md`). Comparing those 19:

- **Raw agreement: 16/19 = 84.2%**
- **Cohen's κ = 0.81** (target was ≥ 0.6 — comfortably exceeded)
- **3 disagreements:** FOLIO ids 389, 1033, 1034 — all three are cases
  Claude labelled `generic_bare_plural`, Gemini labelled
  `predicate_schema_divergence` (389) or `compound_atomization` (1033, 1034)

## The disagreements were checked against the raw FOL, not just eyeballed

For ids 1033/1034, Gemini's note claims *"Fuses 'Severe' and 'Cancer' into
'SevereCancer'"*. Checked directly against the actual FOL:

```
gold: ∀x (BileDuctCancer(x) → SevereCancer(x))
llm : SevereCancer(bileDuctCancer)
```

**Gemini's note is factually wrong.** Gold uses `SevereCancer(x)` as a
single predicate too — there is no fusion happening anywhere in this pair.
The actual error is the universal rule being collapsed into a ground fact
that treats `bileDuctCancer` as an individual constant, which is exactly
`generic_bare_plural` (Claude's original category), not
`compound_atomization`. This is a **confirmed misreading of the FOL diff**,
not just a defensible difference in judgment — recorded inline in
`gemini_cross_check.json`'s notes for C065/C066.

id 389 is the same underlying pattern (`TrainedWith(model, x) →
MachineLearningAlgorithm(x)` collapsed to a ground fact
`TrainedWith(model, machineLearningAlgorithm)`) — Gemini called it
`predicate_schema_divergence`, which is at least not factually wrong (that
category is a legitimate broader umbrella this case could sit under), but
it obscures the more specific and, per step 2, most novel pattern (32% of
the original 19, the paper's strongest candidate finding) — a real
granularity disagreement, not an error, but worth flagging.

## Why this is not a substitute for step 4's actual requirement

Inter-annotator agreement exists to answer one question: **would an
independent human, reasoning without access to the first annotator's
labels, converge on similar categories?** That is a claim about whether the
taxonomy is intersubjectively reliable for people, not about whether a
second AI system's output pattern-matches the first's. Two considerations
cut in opposite directions here and both need to be held at once:

- The high κ (0.81) is a real, positive signal — it shows the category
  definitions in `guidelines.md` are specific enough that an independent
  reasoning process converges with them most of the time. That's worth
  reporting as a preliminary check.
- The confirmed factual error on 1033/1034 shows agreement-by-category-label
  can mask disagreement-by-reasoning — two annotators can pick different
  wrong justifications and still occasionally land on category names that
  happen to differ in traceable, checkable ways, which is exactly why the
  reasoning trail matters as much as the label (per the guidelines'
  `notes` field requirement).
- A reviewer evaluating the paper's methodology will not accept an
  AI-vs-AI comparison as inter-annotator agreement for a claim about human
  taxonomy reliability. This must be reported as what it is: a "preliminary
  LLM-based cross-check (κ=0.81 on the 19-case overlap; one clerical AI
  error confirmed against source data)" — a supplement to, not a
  replacement for, a human annotation pass.

## What to do with the other 53 cases (C001–C053)

Gemini's labels for these are the **only** classification that exists so
far — Claude never independently classified them (see step 2 in
`RESEARCH_DIRECTION.md`, which only covered the 19 GPT-4o cases). Given the
confirmed error rate found above (2/19 ≈ 10.5% of even the checked subset
had a wrong justification), **these 53 should be treated as an unverified
draft, not ground truth**, until either Claude does an independent pass or
a human reviews them — most efficiently, per the original protocol's option
(a): review Gemini's existing labels rather than classifying from scratch,
which is faster than a blind pass and still catches errors like the one
found here.

## Recommendation

1. Keep the κ=0.81 result — it is a genuine, positive, reportable finding
   (as a preliminary check, explicitly labelled as such).
2. Still get a human pass. It can now be framed as **reviewing/correcting
   Gemini's draft labels** (faster than annotating from scratch) rather than
   starting from zero — the guidelines' `notes` field means the human sees
   Gemini's stated reasoning and can agree, correct, or override case by
   case, which is a reasonable, faster version of the same protocol.
3. Do not cite the 53 unverified categories in any paper draft until that
   review happens.
