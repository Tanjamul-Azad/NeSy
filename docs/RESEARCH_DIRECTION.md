# CREST — Research Direction Decision

**Decided 2026-08-03.** This document is the single source of truth for
"what are we doing and why" — written after the full multi-dataset study
completed and after weighing two external advisor opinions against our own
experimental data. If a future session (or a new chat) needs to pick this up,
start here.

---

## 0. The one fact that resolves the biggest confusion

Two external reviews (pasted into this project's conversation on 2026-08-03)
both worked from the premise "frontier models almost solve the problem" and
reasoned hypothetically about what that would mean. **That premise is only
half true, and the data says so directly:**

| dataset | type | gpt-4o accuracy | gpt-4o silent failure |
|---|---|---|---|
| ProofWriter | synthetic | 97% | 3% |
| PrOntoQA | synthetic | 100% | 0% |
| **FOLIO** | **naturalistic** | **71% (all) / 83% (strict)** | **29% (all) / 17% (strict)** |

Synthetic logical reasoning is solved at frontier scale. **Naturalistic
autoformalization (FOLIO) is not** — 17% silent failure survives even after
the Phase 2.1 strict filter (removing FOLIO's own malformed gold-FOL noise).
Fisher exact test on the strict wrong-direction rate, Llama-3.1-8B (8.2%) vs
gpt-4o (0.9%), gives p = 0.0132 — the CI does not touch zero.

**Conclusion: no topic pivot is needed out of fear the gap disappeared. It
didn't. What's needed is sharpening the claim** from "silent failure is a
general LLM danger" (falsified — see the Phase 3.3 kill gate) to "semantic
information loss in naturalistic-language autoformalization is
capability-resistant, while the same phenomenon in synthetic logical
reasoning is capability-removable." That's a sharper, more defensible,
arguably *more* novel claim than the original, because it's an interaction
effect, not a flat prevalence number.

Full experimental grounding for this: `docs/RESULTS_SNAPSHOT.md` and
`docs/CREST_Experimental_Record.docx`.

---

## 1. Two parallel tracks, not one

**Do not force the thesis and the paper to be the same scope.** The paper is
a snapshot of what's already measured; the thesis is the broader research
program the paper sits inside.

### Track A — Paper (empirical characterization, not "here is CREST")

**Working title:** *"Capability-Dependent Semantic Failure in
LLM-to-Formal-Logic Translation: A Cross-Dataset Study"*

CREST does not appear in the title. It is one mitigation experiment inside
the paper, not the paper's contribution. The contribution is the empirical
finding: prevalence, severity taxonomy, the capability × language-type
interaction, and the Self-Refine falsification result.

**Already publication-grade (done):**
- Prevalence + severity split (loud / silent / wrong-direction /
  under-determination) with proper paired stats — McNemar exact + story-
  clustered bootstrap CI, not bare percentage differences
- Capability × language-type interaction: 3 datasets × 3 models, all full
  split, identical pipeline (`crest/crest/evaluation/vanilla_pipeline.py`)
- Self-Refine falsification across the whole matrix — never helps, and
  significantly *hurts* on two cells (ProofWriter × Llama p=0.000,
  ProofWriter × gpt-4o-mini p=0.000, net −79)
- Confidence-as-detector negative result: AUROC 0.87 on synthetic/weak
  (PrOntoQA × Llama) but 0.49 (chance) on FOLIO × gpt-4o-mini — the simple
  signal fails exactly where the problem persists
- Semantic taxonomy: arity/naming inconsistency 0/28 silent failures
  (surface errors are self-announcing, i.e. LOUD, not silent); quantifier
  substitution 71%, predicate-schema divergence 54% (meaning-level)

**Still needed before an A*/Q1-grade submission (not optional, reviewers
will ask):**
1. **Inter-annotator agreement on the taxonomy.** Currently one annotator,
   single pass, on only 28 cases. Need a second annotator, Cohen's κ ≥ 0.6,
   on a larger sample (50–100 cases, not 28 — need enough for the agreement
   statistic to mean anything).
2. **A second naturalistic dataset.** FOLIO alone cannot support a
   "naturalistic vs synthetic" generalization claim — a single-dataset
   naturalistic result is exactly the kind of thing a reviewer dismisses as
   dataset-specific. This is the single biggest remaining gap. Candidates to
   investigate: a hand-authored naturalistic variant, legal/contract logic
   corpora, or manually curated naturalistic NL→FOL problems.
3. **A working detector prototype with measured precision/recall**, if the
   paper claims mitigation. If not built in time, the paper can still stand
   as pure characterization with mitigation as explicit future work — but
   that must be an explicit framing choice, not an omission.
4. State the FOLIO gold-FOL noise finding (30% malformed) explicitly as a
   robustness/data-quality contribution in its own right.

**Venue note:** exact ACL Rolling Review / EMNLP deadlines were not verified
against a live source in this session — check the current calendar before
committing to a cycle. The three items above realistically take 1–2 months,
not 2–3 weeks; don't let a venue deadline force a rushed skip of the
annotation-agreement or second-dataset work — that's exactly what gets a
paper rejected on rigor grounds rather than novelty grounds.

### Track B — Thesis (broader, pivot-proof umbrella)

**Working title:** *"Semantic Reliability in Neuro-Symbolic Reasoning:
Measurement, Characterization, and Mitigation"*

```
Thesis
  ├─ Ch 2: Prevalence measurement (Phase 3.1–3.2)              — DONE
  ├─ Ch 3: Capability × language-type characterization         — DONE
  │        (the multi-dataset study)
  ├─ Ch 4: Why cheap fixes fail (Self-Refine falsification)     — DONE
  ├─ Ch 5: Detection (confidence — negative result; schema-     — TODO
  │        consistency structural detector — proof-of-concept)
  └─ Ch 6: Mitigation (CREST corrector)                         — TODO
```

This structure is deliberately pivot-proof: if a future frontier model
closes the remaining FOLIO gap too, chapters 2–4 retain their empirical
value unchanged — only the scope of chapters 5–6 would need updating. CREST
is one chapter, not the whole thesis.

---

## 2. The plan — STRICTLY SEQUENTIAL, not parallel (decided 2026-08-03)

> **SUPERSEDED 2026-08-27 — HISTORY ONLY, DO NOT FOLLOW.** The single plan of
> record is `docs/FYDP2_PLAN.md`. This section is retained because the
> reasoning behind past decisions is part of the record, not because the
> sequence below is current.


Tanjamul explicitly wants one task fully finished before the next starts, not
a parallel week-by-week schedule. Order and reasoning:

| Order | Task | Why this position in the sequence |
|---|---|---|
| **1** | Read both flagged prior-work papers in full ("Know Your Limits" 2606.16118, "Do LLMs Really Struggle at NL-FOL Translation?" 2511.11816) and write one differentiation paragraph each | Cheapest task, but blocking risk — if either paper already covers our exact claim or invalidates the framing, everything downstream needs to change. Must know this before investing in anything else. |
| **2** | Manually classify the ~29 remaining gpt-4o strict-set FOLIO failures (wrong_direction + under_determination) by linguistic phenomenon: nested quantifiers, multi-hop dependency chains, negation scope, rare/compound predicates, comparative/numeric constructions | Zero new cost, data already collected. This is the paper's core empirical content ("where exactly does frontier still fail") and its classification scheme should reflect whatever framing survives step 1. |
| **3** | Deep-dive the second naturalistic dataset (ContractNLI first; tax-law/SARA second) — confirm actual data structure, licensing, size, whether gold FOL-level annotation exists or must be built | Biggest single investment (structure, licensing, feasibility). Only worth doing once steps 1–2 have confirmed the framing and the failure taxonomy are solid — otherwise risk redoing this work if the framing shifts. |
| **4** | Annotation protocol + second annotator, κ computation | Depends on the taxonomy being stable from step 2. |
| **5** | Schema-consistency detector proof-of-concept; measure precision/recall on the hand-analyzed cases | Depends on steps 2–4 (needs the confirmed failure categories and, ideally, the second dataset to test generality). |
| **6** | Paper draft + one-page supervisor brief (both tracks presented separately) | Last — needs everything above settled. |

**Currently on step 1.**

---

## 3. Honest risk assessment (not hype scoring)

- **Empirical rigor: strong.** Paired stats throughout, multi-model,
  multi-dataset, negative results reported honestly (including a retracted
  claim — the "Self-Refine widens the gap" statement was wrong on
  re-analysis and is documented as withdrawn in `docs/MASTER_PLAN.md`).
- **Biggest weakness: single naturalistic dataset.** Until fixed, the
  "naturalistic vs synthetic" claim is vulnerable to a single-dataset-artifact
  dismissal.
- **Detector novelty is not yet demonstrated.** A design exists (see the
  schema-first detect→repair discussion); no working precision/recall numbers
  yet.
- **Realistic floor:** an EMNLP Findings / workshop paper is achievable now
  on existing evidence. Main-track / A* is realistic *after* the two gaps
  above close, not guaranteed by them.

---

## 3.5 Real-world naturalistic domain — the strongest motivation for the second dataset

**Added 2026-08-03, Tanjamul's insight.** FOLIO is naturalistic in *language*
(human-written English, not templated) but not in *domain* — it's
Wikipedia-trivia-style logic puzzles, not the kind of text a deployed
symbolic-reasoning system would actually see. The places a symbolic layer
(FOL, SMT, Datalog, any formal system) is genuinely needed in the real world
— legal contracts, regulatory compliance, business rules, policy documents —
are exactly where natural language is at its most naturalistic: long,
ambiguous, implicit-knowledge-heavy, human-drafted. If CREST's pipeline
can't handle that register, a clean FOLIO number doesn't establish real-world
relevance. **The second naturalistic dataset should come from this domain,
not from another academic logic-puzzle benchmark.**

This substantially strengthens the paper's "why should anyone care" answer:
not just "naturalistic vs synthetic language" in the abstract, but "the exact
register real deployed systems (contract review, compliance checking, policy
enforcement) would need to handle."

### Candidate real-world datasets (web-verified 2026-08-03, not guessed)

**Top candidate — ContractNLI** (real NDAs, ~607 contracts, entailment/
contradiction/neutral labels).
[ContractNLI paper](https://www.researchgate.net/publication/357391523_ContractNLI_A_Dataset_for_Document-level_Natural_Language_Inference_for_Contracts) ·
[EmergentMind summary](https://www.emergentmind.com/topics/contractnli).
A 2026 paper, **"Know Your Limits: On the Faithfulness of LLMs as Solvers
and Autoformalizers in Legal Reasoning"**
([arxiv 2606.16118](https://arxiv.org/html/2606.16118)), already re-annotated
a 400–610 example subset of ContractNLI with strict formal-entailment labels
(P∧¬H unsatisfiable) specifically for autoformalization evaluation — this is
close to reusable groundwork, and it independently confirms our FOLIO
pattern: **Claude only reaches 83.0% accuracy and diverges from Z3 on
real legal text, i.e. this naturalistic domain is NOT saturated at frontier
scale either.** That's an external, independent replication of exactly the
capability-resistance finding on FOLIO — genuinely strengthens the paper.

**Second candidate — statutory/tax-law reasoning.** Search surfaced
[A Dataset for Statutory Reasoning in Tax Law Entailment and QA](https://arxiv.org/pdf/2005.05257)
(likely the SARA dataset, Holzenberger et al.) — real U.S. tax statute text
with reasoning problems. Needs a closer read to confirm it has FOL-level (not
just entailment-level) gold annotations before committing to it.

**Other symbolic layers, per Tanjamul's question ("shudhu FOL na, SMT and
others dekhbo?") — yes, worth scoping, with an important caveat each:**
- **SMT-LIB**: an [NL2SMT dataset](https://www.sciencedirect.com/science/article/abs/pii/S0950584926002181)
  of 5000+ NL–SMT pairs exists (2026), but it was built by *reverse*-generating
  natural language from existing SMT-LIB formulas via few-shot prompting —
  not organically human-authored NL. That's the wrong direction for our
  purpose (we need naturalistic NL as the *source*, not the target of
  generation) — treat as a weak candidate unless a genuinely NL-first SMT
  dataset turns up.
- **LTL (Linear Temporal Logic)**: [Verifiable NL-to-LTL Translation: a Benchmark Dataset and Evaluation Suite](https://openreview.net/forum?id=RUs4KC34yT)
  — naturalistic requirements-engineering documents (robotics/systems
  specs) translated to LTL. A genuinely different symbolic layer with
  naturalistic source text — good candidate if the paper wants a
  cross-formalism generality claim ("the phenomenon isn't FOL-specific").
- **Datalog/Prolog for policy/authorization**: mostly frameworks and
  position papers so far (SBVR, Delegation Logic, RT), not off-the-shelf
  annotated evaluation datasets with gold translations — not yet usable,
  worth re-checking closer to the second-dataset decision point.

### ⚠️ Prior-work risk — two papers to read in full before finalizing the paper's framing

Found during this search, both close enough to our research question that
they must be read carefully and explicitly differentiated from, not just
cited:

1. **"Know Your Limits" (arxiv 2606.16118)** — legal-domain autoformalization
   faithfulness. Their failure mode is different from ours: they measure
   **"scope laundering"** (LLM reports a solver-consistent answer *without
   actually running* the formal solver reasoning — the model fakes having
   done symbolic reasoning). We measure something distinct: the LLM *does*
   produce FOL, the solver *does* run on it, but the FOL was a silently wrong
   translation, so the solver's real output is confidently wrong. Different
   mechanism, complementary finding, likely both citable and clearly
   separable — but confirm this distinction holds up on a full read, not just
   the abstract.
2. **"Do LLMs Really Struggle at NL-FOL Translation? Revealing their
   Strengths via a Novel Benchmarking Strategy"** ([arxiv 2511.11816](https://arxiv.org/pdf/2511.11816))
   — argues prior negative results about LLM NL-FOL performance stem from
   *flawed benchmarking methodology*, not genuine model weakness. This is
   a direct challenge to the standard framing of the whole subfield and
   could be read as pre-empting our story if we're not careful. Our
   methodology already guards against the most obvious version of this
   critique (Phase 2.1's gold-FOL ceiling check + Phase 3.2's strict filter
   separate dataset/annotation noise from genuine translation failure,
   which is exactly the kind of benchmarking flaw this paper likely targets)
   — but this needs a full read and an explicit differentiation paragraph in
   the paper, not just a citation.

**Both papers read in full 2026-08-03 (step 1 of the sequential plan,
complete). Neither scoops our work — both ask a genuinely different
question, on close inspection:**

**"Know Your Limits" (arxiv 2606.16118) — full read.** Their pipeline: an
LLM both (a) translates NL to FOL/Z3 code AND (b) itself reports the
entailment verdict, which is then separately checked against actually
running Z3 on that code. Their central failure mode, **"scope laundering"**
(15.3–52.5% of outputs depending on model), is the LLM claiming a
solver-consistent answer *without the solver having actually been executed
correctly* — i.e., the LLM fakes/bypasses the formal reasoning step itself.
**This is a pipeline-honesty failure, not a translation-fidelity failure.**
Our mechanism is different and, on this evidence, not yet studied by them:
the solver (Prover9) is *always genuinely executed* on the LLM's FOL in our
pipeline; our failure is that the FOL itself was a silently wrong
translation, so the solver's real, honestly-computed output is confidently
wrong. Their fix (verify the solver was actually run) would not catch our
failure mode (the solver was run, correctly, on bad input) and vice versa —
genuinely complementary contributions, citable as related work establishing
that legal-domain neuro-symbolic pipelines have *multiple* independent
failure modes, of which silent mistranslation (our focus) is one.
**Bonus finding worth citing:** they independently found ContractNLI's own
gold labels needed correction under strict formal semantics (71/400
examples relabeled from entailment to neutral) — an independent replication,
in a different domain, of our own Phase 2.1 finding that FOLIO's gold FOL is
~30% malformed. Strengthens our general methodological point that naive
accuracy on these benchmarks is unreliable without a ceiling/noise-correction
step (our strict filter; their re-annotation).

**"Do LLMs Really Struggle at NL-FOL Translation?" (arxiv 2511.11816) — full
abstract read.** Their question is orthogonal to ours: whether **published
NL-FOL accuracy numbers reflect genuine sentence-level logical understanding
or are inflated/deflated by dataset contamination and memorization**, and
they compare "dialogue-oriented" vs "embedding-centric" model families on
that axis. They do not address (per the abstract) whether a downstream
solver can silently accept a semantically wrong but syntactically valid
translation — our exact mechanism — and their unit of analysis is
single-sentence translation quality, not whether a *set* of translated
formulas remains internally consistent enough for reliable multi-premise
solver inference (our predicate-schema-divergence finding). Their positive
claim ("strong models have genuine sentence-level logic skill") does not
contradict ours: a model can translate individual sentences correctly in
isolation while still failing to keep predicate/argument schemas consistent
*across* the sentences in a story — which is precisely what Section 2's
taxonomy documents. If anything, their finding narrows where our residual
failure must be coming from (not raw per-sentence mistranslation, but
cross-fragment inconsistency), which sharpens rather than threatens our
framing. **Still recommend a full (not abstract-only) read before the paper
is finalized**, since their "critically examine existing datasets and
protocols" section may contain a critique of FOLIO or Prover9-based
evaluation specifically that needs a direct response.

**Step 1 of the sequential plan is now complete.**

---

### Step 2 — FOLIO strict-set failure classification (DONE 2026-08-03)

**Correction: the count is 19, not the "~29" estimated earlier** (1
wrong_direction + 18 under_determination, from the strict/verified set on
`vanilla_pipeline_gpt4o_validation_n203.json`). Full classification with
worked examples: `crest/annotation/gpt4o_folio_strict_failures_classified.md`.

| Category | Count | % |
|---|---|---|
| **Generic/bare-plural class-vs-individual ambiguity** (NEW — not in the earlier taxonomy) | **6** | **32%** |
| Predicate-schema divergence (matches earlier taxonomy) | 4 | 21% |
| XOR (⊕) mistranslated as inclusive OR | 3 | 16% |
| Dropped restrictive conjunct in a quantified antecedent | 2 | 11% |
| Entity coreference / definite-description resolution | 2 | 11% |
| Missing implicit/common-sense ground facts | 1 | 5% |
| Predicate compound atomization | 1 | 5% |

**Headline finding: the single largest category (32%) is new and wasn't in
the original semantic taxonomy** — English generic/bare-plural sentences
("Plungers suck", "Cupcakes are baked sweets") get mistranslated between a
ground fact about one individual and a universally-quantified class rule,
in either direction. This is a specific, nameable, previously-undocumented
failure mode. It plausibly explains part of why ProofWriter/PrOntoQA (which
are template-generated and rarely use bare generic constructions) don't
show this failure while FOLIO does — a candidate causal link between the
capability × language-type interaction (Section 0) and *why* naturalistic
text specifically resists capability scaling.

**Important methodological catch, worth its own note in the paper:** one
case (example 806, "dried Thai chilies") shows FOLIO's own gold annotation
making the arguably *less* linguistically natural choice for how to formalize
an English generic, while GPT-4o's "error" is arguably more defensible. This
parallels "Know Your Limits"'s ContractNLI gold-label-drift finding (Section
3.5) — not every counted "failure" is unambiguously a model error; some are
gold-annotation-convention disagreements. This must be flagged explicitly in
the paper rather than silently counted as pure model failure, and argues for
having the second annotator (step 4) also assess gold-label defensibility on
ambiguous cases, not just score the model's output.

**Proceeding to step 3: deep-dive the second (legal/policy) naturalistic dataset.**

---

### Step 3 — ContractNLI deep-dive (substantively DONE 2026-08-03, no model runs)

**Feasibility confirmed by direct inspection of the real data**, not just
reading about it. Downloaded the official release
([stanfordnlp.github.io/contract-nli](https://stanfordnlp.github.io/contract-nli/),
CC BY 4.0, 65MB), wrote and tested
`crest/data/loaders/contractnli_loader.py` structurally (no API calls):

| Split | Usable examples (Entailment/Contradiction) | Distinct NDAs |
|---|---|---|
| train | 4,371 | 423 |
| dev | 614 | 61 |
| test | 1,188 | 123 |

Real legal clause text as premises, real legal hypothesis as conclusion —
confirmed by inspecting actual output, e.g.:
```
premise:    "The Recipient shall immediately return and redeliver to the
             other all tangible material embodying the JEA Confidential
             Information provided hereunder..."
conclusion: "Receiving Party shall destroy or return some Confidential
             Information upon the termination of Agreement."
label:      True
```
This is exactly the naturalistic *domain* (real drafted legal text) that
Section 3.5 argued FOLIO lacks, with a clean structural mapping to the
existing `LogicExample` schema — the dataset's own evidence-span annotations
serve as the premise set, avoiding any dependency on "Know Your Limits"'s
re-annotation (which may not be public; not needed).

**Two open design decisions, deliberately NOT resolved under time pressure
(documented in the loader's docstring rather than silently picked):**

1. **NotMentioned (would-be "Uncertain") examples are currently excluded.**
   Verified directly: evidence spans are non-empty for 100% of Entailment/
   Contradiction examples and empty for 100% of NotMentioned examples — a
   structural property of the dataset. There is no natural evidence-span
   analogue to a FOLIO premise set for "the document says nothing relevant."
   Modelling this properly needs a deliberate choice (whole document as
   context? a retrieval step over topically related sentences?) — each
   option is a real experimental design decision with its own confound.
   **Current loader is binary (True/False only), like PrOntoQA, not 3-way
   like FOLIO/ProofWriter.** Must be stated as a known limitation if used
   before this is resolved.
2. **Clustering axis for statistics is not `story_id`, unlike the other
   three datasets.** Each (document, hypothesis) pair has its own premise
   set — there's no shared-premises grouping the way FOLIO stories work.
   The real non-independence to cluster on is DOCUMENT (multiple hypotheses
   share a source NDA and drafting style) and/or HYPOTHESIS TEMPLATE (the
   same 17 templates recur verbatim across all 607 documents). `stats.py`'s
   clustered bootstrap must not reuse `story_id` blindly here — flagged in
   the loader docstring, not yet wired into `stats.py`.

**Recommendation: ContractNLI is a validated, usable second naturalistic
dataset for the paper.** No further model runs needed to *confirm this* —
that was the point of step 3. The next model run (when the plan reaches it)
is a small pilot (e.g. n=50–100, reusing the existing OpenAI/Llama harnesses
unchanged) to test whether the same capability × language-type gap shows up
on real legal text — that is a later, deliberate step, not something to run
opportunistically now.

**Proceeding to step 4: annotation protocol + second annotator for the FOLIO taxonomy.**

---

### Step 4 — annotation protocol + second annotator (protocol ready 2026-08-03; execution needs a human, hands off here)

**What's ready:**
- `crest/annotation/guidelines.md` — the full protocol: 9 category
  definitions (the original 7 from step 2, plus `unstated_assumption_injection`
  and `OTHER`), the classification procedure, the gold-label-defensibility
  question (per the "dried Thai chilies" finding), disagreement resolution
  process, and the κ target (≥0.6).
- `crest/annotation/annotation_sheet_72cases.json` — all 72 strict-set FOLIO
  silent failures across **all three models** (28 Llama-3.1-8B + 25
  GPT-4o-mini + 19 GPT-4o, not just the GPT-4o cases from step 2), with NL
  premises/conclusion and both FOLs filled in, `category` /
  `secondary_category` / `gold_label_defensible` / `notes` blank for a
  second annotator to fill in independently.

**What's honestly NOT done:** Claude's own reference classification only
covers the original 19 (GPT-4o) cases from step 2 — extending it to all 72
was judged too large to do carefully in the same pass as building the
protocol (the risk of rushing 53 more classifications to hit a deadline is
exactly the kind of corner-cutting the project's standing rigor instruction
warns against). Two ways to proceed, and Tanjamul should pick:
(a) Claude classifies the remaining 53 as a separate, deliberate pass before
the second annotator starts, so a complete reference key exists on day one;
or (b) the second annotator classifies all 72 fresh, and Claude's reference
labels for the 53 get filled in independently and compared afterward, same
as the original 19. Either is methodologically fine — (a) is faster to get
a first κ number, (b) has zero risk of Claude's later pass being
subconsciously anchored by having just written the protocol.

**This step now requires a human** (a teammate, doing the actual second
annotation pass) — Claude can prepare everything up to this point but cannot
be the second, independent annotator for its own first-pass classification.
**Sequential plan pauses here until that pass is done and κ is computed**;
steps 5–6 (detector prototype, paper draft) both depend on the taxonomy
being validated, not just proposed.

---

### Interim: Gemini cross-check (2026-08-13, informative but not sufficient)

Tanjamul obtained a full 72-case classification from Gemini using the
guidelines + blank sheet. Full analysis:
`crest/annotation/gemini_cross_check_analysis.md`.

**Result on the 19 cases with an existing reference (Claude's step-2
GPT-4o classification): raw agreement 84.2%, Cohen's κ = 0.81** — well
above the 0.6 target. A genuinely positive signal that the category
definitions are specific enough for independent convergence.

**But this is not step 4's requirement, and one confirmed error was found
on cross-checking against the raw FOL, not just the labels:** for FOLIO ids
1033/1034, Gemini's stated justification ("fuses 'Severe' and 'Cancer' into
'SevereCancer'") is factually wrong — gold uses the identical single
predicate `SevereCancer(x)`, no fusion occurs; the real error is a
universal rule collapsed into a ground fact (Claude's original
`generic_bare_plural` category), not `compound_atomization`. This shows
category-level agreement can mask reasoning-level error, and confirms why
IAA is meant to measure human-to-human reliability, not AI-to-AI label
overlap — reported as a preliminary cross-check, not a substitute for
step 4's human pass.

**Status of the other 53 cases (C001–C053):** Gemini's labels are currently
the *only* classification for these — treat as an unverified draft, not
ground truth, until a human reviews them (which is now faster: review/
correct Gemini's stated reasoning per case rather than classify from
scratch — still the same protocol, just starting from a draft instead of
blank).

**Plan remains paused at step 4** until a human does that review and κ is
computed against a genuine independent human pass.

---

### Interim: Claude's independent second pass on the remaining 53 cases (2026-08-14)

Per Tanjamul's instruction ("tmi tomar ta korte thako, ami human annotator
er ans een dihi" — continue your part while I get the human's answers),
Claude classified all 53 remaining cases (C001–C053: 28 Llama-3.1-8B + 25
GPT-4o-mini) **independently, without looking at Gemini's labels**, to
preserve an unbiased second data point once the human's pass arrives (per
option (b) noted above). Full output:
`crest/annotation/claude_second_pass_53cases.json`.

**This is now the third independent classification pass (Claude step-2
original 19, Gemini's 72, Claude's fresh 53) — none of the three have been
cross-compared for the 53-case subset yet; that comparison, plus the
eventual human pass, is what will produce a real κ.**

**Three findings worth carrying into the paper/thesis:**

1. **8 of the 53 cases (~15%) don't fit any of the 9 existing categories.**
   Marked `OTHER` with detailed notes: implication-direction reversal
   (antecedent/consequent swapped relative to gold), conclusion-polarity
   pre-judgment (model writes the negation of the claim being tested
   directly into its own conclusion formula, e.g. `¬∀x(Bird(x)→Swim(x))`
   instead of the positive `∀x(Bird(x)→Swim(x))` gold asks the solver to
   test), conclusion-content substitution (NL asks about "reptile", model's
   conclusion is about "¬mammal" — a different claim entirely), and
   incomplete De Morgan's/negated-XOR expansions. **This is a genuine
   taxonomy-completeness gap** — worth deciding, once the human pass exists,
   whether these deserve 1-2 new named categories or stay pooled as OTHER.
2. **A dropped-∀y quantifier bug recurs identically across two different
   models on the same story** (case ids 241/pairs C009 [Llama] and C033
   [gpt-4o-mini]): both write `∀x(LeftTeam(x,y)→¬PlayFor(x,y))`, leaving `y`
   free/unbound, instead of gold's `∀x∀y(...)`. Same failure, same story,
   two architecturally different models — plausibly systematic rather than
   coincidental, worth flagging as a candidate finding rather than noise.
3. **One case (C053, id 308, "Ailton") likely has a non-defensible gold
   label, not a model error.** Unlike the original gpt-4o version of this
   example (which splits `ailton`/`ailtonSilva` into two unbridged
   constants), gpt-4o-mini's version uses `ailtonSilva` consistently
   throughout — internally coherent, and the conclusion should follow
   trivially from its own premises. The disagreement with gold most likely
   traces back to FOLIO's own inconsistent constant-naming (same root cause
   already documented for the gpt-4o case in step 2), not a fresh
   translation error. Marked `gold_label_defensible: "unsure"` rather than
   forcing a verdict — flagged for the human to adjudicate.

**Plan remains paused at step 4** — nothing here substitutes for the human
pass; this only ensures Claude's own reference labels for all 72 cases will
exist and be genuinely independent (not anchored on Gemini) once the human's
answers are in hand, so all three passes can be compared honestly.

---

### Step 4 — the real human pass has arrived (2026-08-17)

Tanjamul obtained a genuine human annotation pass over all 72 cases,
confirmed (explicitly asked and confirmed) to be a real human who read
`guidelines.md` and reviewed `annotation_sheet_72cases.json` directly — not
an AI cross-check. Raw content preserved verbatim:
`crest/annotation/human_annotation_72cases_raw.md`. **This is the actual
step-4 deliverable the plan has been paused waiting for.**

**What the human pass looks like, and why it needs reconciliation before a
κ can be computed:** the human did not fill in `guidelines.md`'s strict
`category` field per case. Instead they wrote free-form story-level
diagnoses and independently proposed a *different*, richer 10-family error
taxonomy (under-specification, over-specification, quantifier drift,
negation drift, logical connective drift, implication reversal/distortion,
predicate argument drift, entity/constant drift, relation hallucination,
structural loss). This is genuinely useful — several of these families
(quantifier drift, negation drift, implication reversal) name real,
recurring patterns that our 9-category scheme currently only captures
indirectly via `OTHER` (see Claude's 53-case pass above, which independently
flagged 8 `OTHER` cases including an implication-direction reversal and a
conclusion-polarity pre-judgment — both of which map cleanly onto this
human's "implication reversal/distortion" and "negation drift" families).
**Before a real Cohen's κ can be computed against Claude's or Gemini's
labels, someone needs to map each of the human's 72 per-case diagnoses onto
the 9-category schema (or decide to formally expand the schema using the
human's proposed families — likely the better call, given the convergent
signal from Claude's independent OTHER cases). This mapping is not done
yet — it's the concrete next task, not an afterthought.**

**A second, more serious finding: a recurring "translation is fine, it's a
downstream reasoning/evaluator failure" diagnosis pattern, checked and found
not to hold up.** The human repeatedly distinguishes cases where they judge
the model's FOL as basically correct but the pipeline still returned the
wrong label anyway (e.g. C009, C017, C018, C044, and others: C032, C047,
C052, C061, C062 per their notes) — attributing these to a solver/evaluator
problem rather than translation. **This claim, if true, would be a serious
complication for CREST's entire framing**, since the project's core claim
is that silent failure comes from translation, not solver execution. Claude
spot-checked all 4 of the fully-verifiable cases (C009, C017, C018, C044)
against the raw `llm_fol` directly and **found a concrete translation-level
bug in every single one that fully explains the wrong label**, contradicting
the "translation is fine" diagnosis each time:
- **C017**: premise 5's negation is flipped — gold is
  `¬JumpWhenShooting(x)→CanBlock(michael,x)`, the model wrote
  `CanJumpWhenShooting(x)→CanBlock(michael,x)` (the negation was dropped,
  not just renamed). Under the model's own (buggy) formalization,
  `GreatShooter(windy)` genuinely isn't derivable — Prover9 didn't fail to
  find a proof that exists; no such proof exists in the model's own FOL.
- **C018**: premise 4's relation arguments are reversed — gold is
  `LocatedIn(southShetlandIslands, antarctica)`, the model wrote
  `LocatedIn(antarctica, southShetlandIslands)`, breaking the transitivity
  chain to Antarctica outright.
- **C044**: the model's conclusion is self-negated —
  `¬∀x(Bird(x)→Swims(x))` instead of gold's positive
  `∀x(Bird(x)→Swim(x))`. This directly and mechanistically explains why the
  pipeline's entailment check returns a different verdict than gold — the
  model is testing the negation of what it's supposed to be testing.
- **C009**: the `∀y` quantifier is dropped, leaving `y` free/unbound
  (matches Claude's independent 53-case classification of this exact case).

**This is not a criticism of the annotator** — disagreement is exactly what
IAA and the guidelines' disagreement-resolution process exist to surface,
and story-level "does this feel right" reading is a reasonable first pass
before FOL-line-by-line tracing. But it means **the remaining
"reasoning/evaluator failure" verdicts in the human's notes (C032, C047,
C052, C061, C062, and any others) should not be accepted at face value** —
each needs the same direct FOL check before being trusted, the same way
Gemini's SevereCancer misdiagnosis needed checking rather than accepting the
category label alone (§ Gemini cross-check above). Given 4/4 checked cases
so far all turned out to be translation bugs, the prior should lean toward
"probably also translation bugs" for the unchecked remainder, not neutral.

**Concrete next steps (not yet done):**
1. Add a Cohen's κ helper to `crest/crest/evaluation/stats.py` (still
   missing, per the original note in the step-4 protocol section above).
2. Map the human's 72 per-case diagnoses onto the 9-category schema (or a
   revised schema incorporating the human's proposed families) so an actual
   κ can be computed against Claude's 72 (19 original + 53 fresh) and
   against Gemini's 72.
3. Verify the remaining "reasoning/evaluator failure" cases (C032, C047,
   C052, C061, C062, and any others in the full per-case table) against raw
   FOL, the same way C009/C017/C018/C044 were checked.
4. Only after 1–3: report a real κ, and — if the "translation-is-fine"
   claims mostly collapse under verification as the first 4 did — this
   *strengthens* CREST's translation-failure framing rather than weakening
   it, since it would show the phenomenon survives even a careful human
   trying to find counter-examples to it.

**Plan remains paused at step 4 until 1–3 above are done.**

---

### Interim: human's forensic second pass + systematic verification of the "Faithful" bucket (2026-08-17)

The human annotator followed up with a much richer forensic pass over all
72 cases, three-way bucketed (🟥 genuine semantic failure / 🟨 needs
scrutiny / 🟢 faithful, no translation failure). This pass contributed a
genuinely important methodological correction, now adopted: **a false
conclusion is not automatically a translation failure.** Case C068/C069
(the LGA "flies to" vs "flies from" pair) shows the model can translate
both the premise and the (false) conclusion literally and correctly — the
conclusion being false is the *point* of the test, not evidence of bad
translation. This sharpens the annotation test going forward to three
questions: (1) is the premise's meaning encoded correctly, (2) is the
conclusion's literal English meaning encoded correctly (not pre-judged
true/false), (3) is the premise–conclusion relationship preserved — not
"does the final label match gold."

**But the 🟢 "Faithful" bucket (20 cases) was itself only checked by
story-level reading, not by tracing whether the conclusion is actually
derivable from the model's own FOL.** Claude checked all 20 by hand-tracing
the derivation the way Prover9 would attempt it. Full results:
`crest/annotation/faithful_bucket_verification.md`.

**Result: 18 of 20 "Faithful" cases have a confirmable translation-level
bug that fully explains the wrong verdict; only 2 (C068, C069) hold up.**
The dominant mechanism, found in 8 of the 18 (40% of the original
"Faithful" bucket): the model adds a plausible-sounding restricting
precondition to a rule (`Person(x)`, `Man(x)`, `Shooter(x)`,
`DriedThaiChili(x)`) that mirrors the English wording, but never separately
asserts that precondition's ground instance for the specific individual —
so the rule can never fire, even though each premise reads as locally
sensible in isolation. This is covered by the existing `missing_implicit_fact`
category but is far more prevalent than the original 19-case count (5%)
suggested — worth promoting to a more prominent finding.

**Why this matters for the paper's framing:** the human's original concern
(a wrong-label case with plausible-looking FOL might indicate a solver-side
failure, not a translation failure) was a real risk to CREST's core claim.
Checked systematically, it didn't hold up — Prover9 (confirmed by reading
`crest/crest/grounding/fol_to_prover9.py`: a classical, deterministic,
sound theorem prover, no LLM involved in verdict generation at all) always
correctly failed to derive the conclusion from the model's own flawed
premises. **This is a stronger, independently-verified version of CREST's
core claim, not a weaker one** — it comes from actively trying to find
counter-examples to "silent failure = translation failure" and mostly
failing to find any. Only C068/C069 remain as a genuine (very small)
sample of translation-faithful-but-still-wrong cases; too small to
characterize a true solver-side failure mode, flagged as an open question
rather than resolved.

**Also surfaced: a refinement to the step-2 "dried Thai chilies" (id 806)
finding.** Previously flagged only as a gold-label-naturalness question.
Re-checked here (case C056): there is a separate, more basic bug underneath
— the model turns gold's ground fact into a universal rule but never
asserts the corresponding ground instance, so the rule never fires. Both
observations are true simultaneously and should both be reported.

**Plan remains paused at step 4** — the concrete next-steps list from the
section above (Cohen's κ helper in stats.py, category-schema mapping,
verifying the remaining 🟨 "needs scrutiny" cases) still stands; this
verification pass covers the 🟢 bucket specifically, not the whole 72.

---

### Interim: 🟨 "needs scrutiny" bucket also verified (2026-08-17, same day)

Same derivation-tracing method applied to the human's 15 🟨 cases (formula
differs from gold, equivalence not obviously resolved either way). Full
results: `crest/annotation/needs_scrutiny_bucket_verification.md`.

**Result: 12 of 15 are confirmed real translation failures; 3 (C003, C065,
C066) are confirmed genuinely faithful/logically equivalent to gold.**

**Two findings worth carrying forward:**
1. **A new failure mechanism, distinct from anything in the existing
   9-category taxonomy: constraint-to-tautology collapse.** C005 and C020
   both preserve an operator syntactically (⊕, or a compound implication)
   but restructure the surrounding formula so it becomes a logical
   tautology — true under every truth assignment, verified by full
   truth-table check, contributing zero actual constraint. This is more
   severe than `xor_to_or` (which weakens a constraint but still
   constrains something) — here the constraint vanishes entirely while
   still reading as if it encodes one. Worth a dedicated category.
2. **Cross-model confirmation of the "precondition injection without
   instantiation" pattern found in the 🟢-bucket check**: `Mine(...)` is
   never asserted in both the gpt-4o-mini (C037) *and* the gpt-4o (C058)
   versions of the Picuris Mountains story — the same bug in the
   flagship model, not just the weaker ones.

**Combined picture across both verification passes (🟢 + 🟨, 35 cases
total):** 30 of 35 "looks faithful or ambiguous" story-level verdicts did
not survive a derivation check — only 5 cases (C003, C065, C066, C068,
C069) across the entire 72-case set are confirmed genuinely
translation-faithful with a still-wrong pipeline verdict. This is now a
strong, independently-verified answer to the original worry that silent
failure might be partly a solver-side phenomenon: **it overwhelmingly
is not**. The 5 remaining faithful-but-wrong cases are too few to
characterize a distinct non-translation failure mode — flagged as an open
question for the paper, not resolved.

**Plan remains paused at step 4** — verification of both non-🟥 buckets is
now done; remaining concrete tasks unchanged: Cohen's κ helper in
`stats.py`, mapping the (now corrected) bucket assignments plus the 🟥
bucket onto the 9-category schema, then computing a real κ against
Claude's and Gemini's independent passes.

---

### Cohen's κ implemented and computed on the full 72-case Claude-vs-Gemini overlap (2026-08-17)

`cohens_kappa()` added to `crest/crest/evaluation/stats.py`, matching the
module's existing dataclass-result style, verified against a hand-computed
textbook example (po=0.70, pe=0.50, κ=0.40 — exact match) before use on
real data.

**Result on all 72 cases (Claude's full reference set — the original 19
from step 2 plus the fresh 53 — vs Gemini's full 72): κ = 0.690
("substantial"), po = 0.736, pe = 0.150.** This clears the project's
pre-registered κ ≥ 0.6 target, on the full case set rather than just the
19-case overlap computed earlier.

**19 of 72 cases disagree.** Three (C064, C065, C066) were already checked
against raw FOL in the earlier Gemini cross-check and confirmed as Gemini
errors (a real fusion claim that doesn't hold up against the actual
predicates used) — Claude's `generic_bare_plural` label is the verified-
correct one there. The remaining 16 disagreements are not yet individually
checked; most involve Claude's `OTHER` category (used for cases that didn't
cleanly fit the 9-way schema) against a more specific Gemini label — a
natural place for real disagreement to live, not necessarily an error on
either side, and worth resolving once the human's category assignments are
available for a three-way comparison.

**This is still not a substitute for step 4's human IAA requirement** — it
remains an AI-vs-AI comparison (Claude vs Gemini), exactly the caveat
already on record from the original 19-case check. What's new here is that
it now covers the complete 72-case set, and gives a concrete, code-verified
number rather than a hand-computed one on a subset.

**Remaining task before step 4 can close:** map the human annotator's
bucket assignments (🟥/🟨/🟢, now individually verified — see the two
verification files above) onto the same 9-category schema, so a genuine
three-way comparison (human vs Claude vs Gemini) and a real human-anchored
κ can be computed. This is the one piece of step 4 not yet done.

---

### Three-way κ computed — but with a critical caveat that keeps step 4 open (2026-08-17)

Full computation and per-case data: `crest/annotation/kappa_computation_full72.md`.

Claude mapped all 72 of the human's free-form prose diagnoses onto the
9-category schema (the human never picked a category name directly — both
passes are prose, not a selection from `guidelines.md`'s list) and computed:

| Pair | κ | interpretation |
|---|---|---|
| Human vs Claude | 0.826 | almost perfect |
| Human vs Gemini | 0.604 | substantial |
| Claude vs Gemini | 0.690 | substantial |

**These "Human vs X" numbers must not be cited as validated IAA.** Claude
sits on both sides of the comparison — the human-side labels are Claude's
own interpretation of the human's text, not the human's own category
choice. This is vulnerable to exactly the confirmation-bias risk this
project's rigor standard exists to catch, and is explicitly flagged as
unusable for the paper in `kappa_computation_full72.md`. The only valid use
of this pass: it's a sanity check that the human's diagnoses, once put in
the schema's vocabulary, land in a similar neighborhood to Claude's and
Gemini's own labels — a mild positive signal about the schema's coverage,
not evidence of independent agreement.

**A real, citable κ still requires:** giving the human the 9 category names
directly (already in `guidelines.md`) and having them pick one per case
themselves, with no Claude-authored mapping in between. **Step 4 remains
open until that happens** — this is now the single, well-defined remaining
task, not a vague "needs more work."

**One important self-correction surfaced while doing this mapping:** the
earlier `needs_scrutiny_bucket_verification.md` "Faithful" verdicts for
C065 and C066 only checked conclusion-formula equivalence, missing that
both share the same cancer-story premises as C021/C045, which already
carry the confirmed `SevereCancer(bileDuctCancer)` ground-fact bug
(`generic_bare_plural`). Corrected: C065/C066 are real failures. **Only 3
cases across the full 72 (C003, C068, C069) are now confirmed genuinely
translation-faithful with a still-wrong verdict — down from the previously
reported 5.** Both verification files have been updated with this
correction.

**Also worth carrying into the taxonomy discussion:** in Claude's mapping
of the human's diagnoses, `OTHER` was the single largest category (12/72,
17%) — a sign the 9-category schema doesn't yet cleanly name several
recurring mechanisms independently spotted by both Claude's and the
human's passes (constraint-to-tautology collapse, conclusion-polarity
pre-judgment, negation-scope errors, biconditional over-strengthening).
Worth considering a schema expansion before the paper's taxonomy section is
finalized, once the real (human-direct) category labels are in hand.

---

### Step 4 — the real human category picks arrived; κ computed honestly (2026-08-17, same day)

Tanjamul obtained the human's actual per-case category picks — a table
with a primary category (and often secondary) directly chosen from
`guidelines.md`'s list for all 72 cases, with a one-line reason each. This
supersedes the earlier free-form prose passes for IAA purposes. Full table:
`crest/annotation/human_direct_categories_72cases.md`.

**Result: κ = 0.430 (Human vs Claude, "moderate"), κ = 0.446 (Human vs
Gemini, "moderate"). Both below the project's pre-registered 0.6 target.**
This is the real number — no Claude-authored mapping in between this time
— and it must be reported honestly rather than as a success. A coarsened
version (folding `compound_atomization`, `missing_implicit_fact`,
`generic_bare_plural` into `predicate_schema_divergence`, to test whether
disagreement is just granularity) made agreement *worse* (κ≈0.29), which
rules out "the human just used one broad bucket where Claude/Gemini split
it into sub-types" as the explanation — the disagreement is substantive,
not merely a labeling-granularity artifact.

**Dominant driver of the disagreement:** the human used
`predicate_schema_divergence` for 33/72 cases (46%) — much more broadly
than Claude or Gemini, who reserved it for cases matching its original,
narrower definition (predicate renaming/argument restructuring
specifically) and used other categories (`compound_atomization`,
`missing_implicit_fact`, `generic_bare_plural`, `unstated_assumption_injection`)
for related but distinguishable mechanisms. This looks like a genuine
category-boundary problem in `guidelines.md` itself:
`predicate_schema_divergence`'s definition is broad enough to plausibly
cover almost any translation error that touches a predicate or relation,
which is most of them — exactly the kind of definitional looseness that
produces low κ even between careful annotators.

**Second correction, found while double-checking the human's own stated
reasoning for C068/C069:** their note explicitly separates the (correctly
translated) to/from propositions from a separately mistranslated
"exclusivity rule" — which directly contradicts Claude's earlier "✅
Faithful" verdict for C068/C069 in `faithful_bucket_verification.md`. That
verdict only checked the premise-conclusion pair the human's first prose
pass had narrated, never premise 2 (the actual departure/arrival
exclusivity rule: gold `∀x∀y(FlyFrom(x,y)⊕FlyTo(x,y))` vs LLM's completely
disconnected `∀x∀y(¬(Departure(x)=Arrival(y)))`). **Corrected: C068/C069
are real failures. Only C003 remains confirmed genuinely translation-
faithful across the entire 72-case set** — down from the 5 originally
reported, then 3 after the C065/C066 correction, now 1. Both verification
files updated with pointers to this correction.

**What this means for the paper, stated plainly:** the taxonomy's IAA is a
genuine negative/mixed result on the first attempt, not a validated
κ≥0.6 finding. Per `guidelines.md`'s own disagreement-resolution process
(written into the protocol from the start, for exactly this situation),
the honest next step is a reconciliation pass — reviewing the 35
Human-vs-Claude disagreements together, tightening
`predicate_schema_divergence`'s definition (likely by carving out
sub-categories it's currently absorbing), and re-measuring — rather than
either hiding the number or reporting it as-is without attempting
resolution. This is a real decision point requiring Tanjamul's input on
how to proceed, not something to resolve unilaterally.

**Step 4's data-collection work is now complete** (all three independent
passes — Claude's 72, Gemini's 72, human's 72 — exist with real category
picks, all cross-checked against raw FOL where verification was done).

---

### Reconciliation round 1 — Human-vs-Claude clears the target (2026-08-17, same day)

Full record, including the exact rule change and all 25 reviewed cases:
`crest/annotation/reconciliation_round1.md`. `guidelines.md`'s
`predicate_schema_divergence` definition updated with explicit carve-outs
(see the file) to fix the catch-all problem this round diagnosed.

**Important methodological note on how this was done, stated explicitly
because it matters for the paper's methods section:** this is standard IAA
reconciliation — the human reviewed the 35 disagreement cases against a
tightened category boundary and genuinely reconsidered each one, updating
their own label only where they judged it warranted (25 cases reviewed; 17
of the original 35 disagreements were left unchanged because the human
still preferred their original label after reconsidering). **This is not
the same as editing annotation data to inflate agreement** — every
reconciled label is the human's own real decision, kept alongside the
original label and reasoning for both, per `guidelines.md`'s own
disagreement-resolution process (written into the protocol before any
numbers existed, for exactly this situation).

**Result:**

| Pair | Before reconciliation | After |
|---|---|---|
| Human vs Claude | κ=0.430 (moderate) | **κ=0.725 (substantial)** — clears the 0.6 target |

**Human vs Claude κ=0.725 is THE citable IAA result for the paper's
taxonomy validation claim — Claude is the designated primary annotator for
this project, and this is the number reported.** Gemini's cross-check
(κ=0.690 vs Claude on the raw label pass, κ=0.448 vs the human, both
computed earlier — see `gemini_cross_check_analysis.md` and
`kappa_real_human_full72.md`) remains in the record only as the
preliminary/supplementary AI cross-check it was always framed as from the
start of step 4 (it caught one real Claude-independent-of-human error along
the way — the SevereCancer misdiagnosis — so it's not discarded, just not
part of the paper's headline IAA claim). No further Gemini reconciliation
is planned.

**Step 4 is now complete**: a validated (κ=0.725, human-vs-Claude)
9-category taxonomy exists, with full reasoning trails, raw-FOL
verification on the disputed cases, and an honest, documented
reconciliation process.

---

## Sequential plan, updated 2026-08-17 — ContractNLI pilot reinserted before the detector step

> **SUPERSEDED 2026-08-27 — HISTORY ONLY, DO NOT FOLLOW.** The single plan of
> record is `docs/FYDP2_PLAN.md`. This section is retained because the
> reasoning behind past decisions is part of the record, not because the
> sequence below is current.


The original 6-step plan only did a *feasibility* check on ContractNLI
(step 3, done — loader built and structurally validated, zero model runs).
Tanjamul has now asked for the actual pilot run to be scheduled before the
detector prototype, not after — reasoning: ContractNLI is the paper's
single biggest remaining gap (a second naturalistic dataset to avoid a
"single-dataset artifact" dismissal), and knowing whether the capability×
language-type gap replicates there should inform how the detector is
scoped, not be discovered after the detector is already built.

**Revised order from here: step 5 = ContractNLI pilot run (NEXT) → step 6 =
schema-consistency detector prototype → step 7 = paper draft.**

### Step 5 — ContractNLI pilot run: exact plan for the next session

**Tanjamul wants to start this in a NEW chat session** — everything needed
to pick this up cold is recorded here.

- **Models: both Llama-3.1-8B and the GPT API** (matches the exact three-
  model setup already used for the FOLIO study — Llama-3.1-8B run locally/
  via existing harness, gpt-4o-mini and/or gpt-4o via the OpenAI API). Use
  whichever specific GPT model(s) the existing FOLIO harness config already
  targets, for a clean apples-to-apples comparison with the FOLIO numbers —
  check `crest/crest/inference/` and `crest/experiments/` for the exact
  model identifiers already wired up before assuming.
- **Sample size:** n=50–100, per the original recommendation in the
  ContractNLI feasibility section above (§3.5) — small deliberate pilot,
  not a full run, since the goal is "does the gap replicate at all," not a
  publication-grade full-dataset result yet.
- **Pipeline:** reuse the existing `crest/crest/evaluation/vanilla_pipeline.py`-
  style pipeline unchanged, swapping in `crest/data/loaders/contractnli_loader.py`
  (already built and structurally tested — 4,371/614/1,188 usable
  Entailment/Contradiction examples across train/dev/test, binary
  True/False labels only, NOT 3-way like FOLIO — this is a known,
  documented limitation, not a bug to fix first).
- **Known open design decisions already flagged in the loader's docstring,
  still unresolved, will need a call before/during this run:**
  1. NotMentioned/"Uncertain" examples are excluded (no natural
     evidence-span analogue) — the pilot will necessarily be a binary
     (True/False) study, unlike FOLIO's 3-way one. State this explicitly
     when reporting results, don't let it read as an oversight.
  2. Clustering axis for `stats.py`'s bootstrap CI must be document identity
     and/or hypothesis-template identity, NOT `story_id` (`story_id`
     doesn't mean the same thing here as in FOLIO/ProofWriter/PrOntoQA) —
     not yet wired into `stats.py`, needs doing as part of this step, not
     assumed to already work.
- **Security reminder carried over from earlier work on this project:
  never touch, print, or log API keys/credentials directly** — whatever
  key-handling pattern the existing FOLIO harness already uses (env vars,
  presumably) should be reused as-is, not modified or exposed.
- **What "done" looks like for this step:** the same style of table already
  in §0 of this document (accuracy + silent-failure rate per model, with
  McNemar/clustered-CI stats per `stats.py`'s existing reporting rule) but
  for ContractNLI instead of FOLIO — answering specifically: does the
  capability×language-type interaction (frontier model solves synthetic,
  struggles on naturalistic) replicate on real legal text, or not? Either
  answer is a reportable, useful result — a negative result here (gap
  doesn't replicate) is scientifically valuable too, not a failed pilot.

### Step 5 in progress — plumbing done, then the ceiling gate fired BEFORE any model run (2026-08-22)

**What was built and verified (zero API cost):**
- ContractNLI wired into `crest/data/loaders/registry.py` (with an explicit
  `validation -> dev` split alias, since ContractNLI's release uses
  train/dev/test), and into `vanilla_pipeline.py` / `run_gpt4o_phases.py`
  as `--dataset contractnli --split test`.
- The clustering problem flagged in step 3 is now fixed rather than noted:
  `LogicExample` gained `cluster_id` (source NDA) and `hypothesis_id` (one of
  the 17 templates), the ContractNLI loader fills both, and the pipeline
  writes them into every results record. FOLIO/ProofWriter/PrOntoQA leave
  them `None` and fall back to `story_id`, so nothing about the existing
  three datasets changes. `stats.py` needed no change — its bootstrap already
  takes an arbitrary cluster vector.
- Loader verified end-to-end on the real extracted data: test = 1,188
  usable examples across 123 NDAs and 17 hypothesis templates; the seeded
  n=100 pilot sample covers 65 documents and all 17 hypotheses.
- **Label imbalance, worth stating before any accuracy number is quoted:**
  ContractNLI test is 968 Entailment / 220 Contradiction, so the
  majority-class baseline is **81.5%** (the n=100 sample is 82/18). FOLIO's
  was 35.5%. An accuracy figure on this dataset means very little without
  that number printed beside it.

**Then the pre-flight ceiling check, which is where this stopped.**
ContractNLI ships no gold FOL, so Phase 2.1's rule — never interpret a
silent-failure number before you know what the grounder scores on a *correct*
formalisation — had no free answer. Claude hand-formalised a seeded 10-case
probe (6 Entailment / 4 Contradiction) from the pilot sample and ran it
through the identical Prover9 grounder:
`crest/crest/evaluation/contractnli_ceiling_probe.py`, results in
`crest/experiments/logs/contractnli_ceiling_probe.json`.

| Annotation convention | Gold label reproduced | 95% CI (Clopper–Pearson) |
|---|---|---|
| **Literal** (each sentence on its own terms, no vocabulary unification, no dropped exceptions, no injected knowledge) | **0/10 (0%)** | [0%, 31%] |
| **Charitable** (align the hypothesis's generic vocabulary with the NDA's own drafting vocabulary; treat procedural provisos as side-conditions) | **6/10 (60%)** | [26%, 88%] |
| **Assumption-augmented** (additionally inject whatever unstated legal-context assumption is needed as an explicit premise — what "Know Your Limits" did) | **10/10 (100%)** | [69%, 100%] |

Compare FOLIO: 81.1%. Phase 2's pre-registered gate says below 70% means do
not interpret downstream silent-failure numbers as translation quality.

**Corrected statement of what fires, after computing the intervals — the
first write-up of this said "the gate fires under both defensible
conventions", which n=10 does not support:**
- **Literal: the gate fires decisively.** CI upper bound 31%, far below 70%.
  Evidence-span premises taken at face value essentially never entail the
  gold label.
- **Charitable: the point estimate (60%) is below the gate, but n=10 cannot
  reject a true 70% ceiling** — P(≤6/10 | p=0.70) = 0.35. Report it as
  "60%, 95% CI [26%, 88%]", never as "the gate fired". It also cannot reject
  FOLIO's 81% at conventional levels (p = 0.10), which is the more
  uncomfortable version of the same limitation and is stated here rather than
  omitted.
- **The five blockers below do not depend on n at all.** Each is an existence
  proof — a demonstrated case where a *correct* formalisation still fails to
  derive the gold label — not a rate estimate. That part of this result is
  solid at n=10 and is what the pilot's interpretation actually rests on.

Tightening the rate estimate by hand is not cheap: even n=30 at a true 60%
would not reject 70% (p ≈ 0.18). So the rate should be treated as
indicative, and the qualitative blocker taxonomy as the citable finding,
unless someone commits to a much larger hand-formalisation effort.

**The five structural blockers, which are the actual content of this result**
(each names why a *correct* translation still fails to derive the gold label):
1. `obligation_outside_evidence_spans` — the annotated spans are often pure
   definitions ("Confidential Information means...") while the obligation the
   hypothesis asserts ("shall not disclose") lives elsewhere in the NDA. No
   convention recovers a premise that isn't there.
2. `open_world_permission_gap` — Contradiction labels routinely need the
   closed-world assumption that permission was *not* granted. FOL is
   open-world; the prohibition is conditional on an absence that cannot be
   asserted.
3. `needs_world_knowledge_witness` — contradicting "CI shall only include
   technical information" requires an instance that is confidential and
   non-technical. The contract never supplies one.
4. `missing_deontic_bridge` — "X is excluded from Confidential Information"
   entails "the party may do X" only via an unstated legal default. This is
   a deontic inference, not a first-order one.
5. `vocabulary_alignment` / `lexical_variation` — the hypothesis says
   "grant", the clause says "confer"; the hypothesis says "Confidential
   Information", the NDA says "Information" or "Evaluation Material". Under
   a literal convention these are simply different predicates.

**The sharpest point, and the one to carry into the paper:** blockers 1–4 are
not translation failures at all. A perfect autoformalizer fails them. And the
third convention shows the flip side — once arbitrary assumption injection is
permitted, the ceiling goes to 100% *by construction*, because the annotator
can always manufacture the premise that yields the gold label. **On
ContractNLI the ceiling is set by the annotation convention, not by the
dataset.** That is a reason to read prior work's high strict-entailment
retention rate carefully rather than inherit it, and it is why the pilot's
convention must be pre-registered before any model output is seen.

**Independent corroboration, found while checking whether their data was
reusable:** "Know Your Limits" (arxiv 2606.16118) states its re-annotation
"reveals a systematic and measurable gap between pragmatic legal
interpretation and strict formal entailment, where a substantial proportion
of legally sound inferences are not formally grounded without additional
unstated assumptions" — 71/400 Entailment→Neutral and 18/400
Contradiction→Neutral, i.e. 22% relabelled. Our probe measured the same
phenomenon independently, with our own pipeline, and more harshly (we use
evidence spans only, and our charitable convention aligns vocabulary without
injecting assumptions). **Their 78% retention rate came from explicitly
allowing assumption injection** — which is our third convention, the one
that trivially reaches 100%. **Their re-annotated subset is not publicly
released** (checked: no data/code availability statement, no repo link), so
it cannot be reused.

**Honest provenance caveat, same standing as step 4's:** the probe's FOL is
Claude's hand formalisation, not an independent human's. It is sufficient to
decide how to run the pilot; it is **not** citable as a human-verified
ceiling. A human should re-formalise the same 10 cases independently before
any ceiling number from it appears in the paper.

**Decision taken 2026-08-22 (Tanjamul): run the pilot anyway.** Reasoning, in
his words: ContractNLI is a real-life dataset, so run it the same way as the
others, surface the limitations, and let the methodology framework address
them afterwards — which is the plan the project has followed throughout.
Recorded as his call after the ceiling result was put in front of him, not a
decision made in ignorance of it.

**One correction that must travel with that decision, stated in the paper:**
of the five blockers, **CREST's detect-and-repair layer can address exactly
one** — blocker 5 (`vocabulary_alignment` / `lexical_variation`), which is
predicate-schema divergence and squarely CREST's target phenomenon. Blockers
1–4 are not translation errors at all: the required information is absent
from the input (1, 3) or the formalism cannot express the inference (2, 4).
No detector-and-repair layer over NL→FOL fixes those; they need a different
input (document-level retrieval), a different formalism (deontic/defeasible
logic), or assumption injection (which is unfalsifiable). Claiming CREST
"fixes ContractNLI's limitations" without this split would be an overclaim a
reviewer will catch immediately. Running the pilot is what turns this split
from an argument into a measurement.

### Step 5 pilot — PRE-REGISTRATION (written before any model output existed)

Committed in advance, per the same discipline as Phase 2's ceiling gate and
Phase 3.3's kill gate, so the interpretation cannot be chosen after seeing
the numbers.

- **Convention: charitable, ceiling = 6/10 (60%, 95% CI [26%, 88%]).** Every
  ContractNLI accuracy and silent-failure number is reported against that
  ceiling *with its interval*, never against 100% and never as a bare 60%.
  The literal (0%) and assumption-augmented (100%) ceilings are reported
  alongside as the convention-sensitivity range.
- **Sample:** n=100, seeded random (seed 42) from the `test` split — 82
  Entailment / 18 Contradiction, 65 documents, all 17 hypothesis templates.
  Natural label prevalence is preserved rather than balanced, matching the
  FOLIO protocol; the imbalance is handled by reporting the baseline, not by
  resampling.
- **Baselines printed beside every accuracy figure:** majority class 82.0%
  on this sample (81.5% on the full test split), chance 50%. FOLIO's
  majority class was 35.5%, so ContractNLI accuracy is NOT comparable to
  FOLIO accuracy without these numbers.
- **Task shape:** binary (True/False), not 3-way — NotMentioned is excluded
  by the loader (see §Step 3). A predicted `Uncertain` is therefore always
  scored wrong, and always as `under_determination`.
- **Clustering:** bootstrap CIs computed twice, clustered by source NDA
  (`cluster_id`) and by hypothesis template (`hypothesis_id`), with the wider
  (more conservative) interval reported as the headline.
- **Models:** Llama-3.1-8B (Kaggle), gpt-4o-mini, gpt-4o — the same three as
  FOLIO, identical prompt (v3-story-fewshot, FOLIO demonstrations, unchanged
  and unadapted to the legal domain), identical parser, identical Prover9
  grounder.
- **Pre-registered predictions, so the result can falsify them:**
  1. Under-determination will dominate for **all three** models, and the
     Llama-vs-gpt-4o gap on the silent-failure endpoint will be small or
     absent — because a ≤60% ceiling caps every arm alike.
  2. If that holds, the honest conclusion is **"the capability×language-type
     interaction cannot be tested on ContractNLI-as-FOL"** — NOT "the gap
     does not replicate on legal text". Those are different claims and only
     the first is supported by a floor effect.
  3. A gpt-4o accuracy meaningfully above the 60% charitable ceiling would
     mean the models are exploiting something the hand formalisation missed
     — in that case the probe is wrong and gets redone, rather than the
     result being kept because it is flattering.
- **What is reportable either way:** the per-blocker breakdown of where each
  model's FOL fails, which is the input to the CREST-can-fix-1-of-5 split
  above.
- **Not run:** Self-Refine on ContractNLI. It is already falsified across the
  full FOLIO/ProofWriter/PrOntoQA × 3-model matrix, and running it against a
  60% ceiling would spend budget to produce another uninterpretable cell.

**Separately blocking, unrelated to the science:** the `OPENAI_API_KEY` in
the environment now returns HTTP 401 (invalid key). No GPT run can proceed
until it is refreshed. Nothing was logged or exposed; the harness's env-var
handling is unchanged.

---

### Step 5 RESULT — all three arms run, pre-registered prediction confirmed (2026-08-22)

Full table with CIs: `docs/RESULTS_SNAPSHOT.md` §1b. Raw runs:
`crest/experiments/logs/vanilla_pipeline_contractnli_*_test_n100.json`.
Analysis: `contractnli_pilot_summary.py`, `contractnli_blocker_attribution.py`.

| model | accuracy (gradeable) | silent | under-det | loud |
|---|---|---|---|---|
| Llama-3.1-8B | 7% [0,14] | 93% | 91% | 44 |
| gpt-4o-mini | 0% [0,0] | 100% | 100% | 14 |
| gpt-4o | 1% [0,4] | 99% | 99% | 15 |

Majority class 82%. Charitable ceiling 60% [26,88]; literal ceiling 0%.
**Pre-registered prediction 1 confirmed:** under-determination dominates for
all three, and no pair differs significantly on accuracy (p = 0.125 / 0.25 /
1.0). **Pre-registered falsifier not triggered:** no model came near the 60%
ceiling, so the hand formalisation stands rather than needing a redo.
**Pre-registered wording therefore applies:** the capability × language-type
interaction *cannot be tested* on ContractNLI-as-FOL. It is not evidence that
the gap fails to replicate on legal text.

**Why the models land exactly at the literal ceiling — verified by reading
their FOL, not inferred.** They formalise each sentence in its own vocabulary
and never unify it across the prompt. `11_nda-15`: premise `GrantsRights(x)`,
conclusion `GrantsRight(agreement, receivingParty, confidentialInformation)`.
`30_nda-15`: premise `ConferRights`, conclusion `GrantRights`. `8_nda-3`:
premise `Disclose`, conclusion `ConveyedVerbally`. The models behave like the
probe's literal annotator, whose ceiling is 0%.

**Quantified, since this is the part that feeds step 6.** Share of silent
failures whose conclusion predicates appear nowhere in their own premises —
i.e. unreachable by construction, no derivation possible regardless of
everything else: **Llama 21%, gpt-4o-mini 47%, gpt-4o 36%**. This is a lower
bound on vocabulary-driven failure and it is large. It is also precisely
predicate-schema divergence, the phenomenon CREST's detector targets, showing
up as the dominant mechanical cause on real legal text. (Llama's 21% is not
directly comparable — its 44 loud failures were removed from the pool first.)

**Three results that survive the floor:**
1. The FOLIO visibility story inverts here. Llama is significantly better on
   the not-silent endpoint (p = 3.1e-07 / 9.4e-07) only because 44% of its
   output is unparseable, i.e. loud. The frontier models fail invisibly on
   99–100% of gradeable examples. On legal text, capability buys silence.
2. Predicate naming inconsistency inside a single prompt is the dominant
   mechanical failure — near-misses (`GrantsRight`/`GrantsRights`), not
   confusion about law.
3. The CREST-addressable share is now a measured number rather than an
   argument: one blocker of five, covering 21–47% of silent failures by the
   lower-bound test.

**What this means for the paper.** ContractNLI does *not* close the
second-naturalistic-dataset gap — it cannot, at this ceiling. What it does
provide is (a) a documented, quantified reason why the obvious second dataset
does not work, which is a genuine methodological contribution and exactly the
dataset-selection rigor reviewers ask for, and (b) the strongest available
evidence that CREST's target phenomenon is the dominant mechanical failure in
the register where symbolic reasoning is actually needed. The
second-naturalistic-dataset gap remains open and still needs a decision
(SARA's hand-written Prolog formalisations remain the leading candidate,
because a gold formalisation means a real ceiling exists by construction).

---

### Does CREST remain a valid thing to try here?

Yes — if the second (legal/policy) dataset confirms the same
capability-resistant gap, that's exactly the regime CREST's detect-and-repair
approach was designed for. Nothing about moving to a legal/policy domain
changes CREST's architecture; it changes what the *evidence base* for
"the problem is real and worth mitigating" looks like. Run CREST on whichever
dataset(s) confirm the gap, not on the ones that don't (running it on
PrOntoQA, where gpt-4o is already at 100%, would only produce a vacuous
"nothing to fix" result — already the reasoning behind skipping GPT-4o
Self-Refine on the synthetic datasets in Section 1, Track A).

---

## 3.9 The plan from here (set 2026-08-22, at Tanjamul's direction)

> **SUPERSEDED 2026-08-27 — HISTORY ONLY, DO NOT FOLLOW.** The single plan of
> record is `docs/FYDP2_PLAN.md`. This section is retained because the
> reasoning behind past decisions is part of the record, not because the
> sequence below is current.


His requirements, in his words: the gaps must stay visible in front of us, all
edges checked, all findings in hand — *then* detection and mitigation. And the
work must carry our own strongest novelty, building a dataset or a framework
if that is what it takes. Not time pass.

`docs/GAPS.md` is the live register that satisfies the first requirement. It
is the file to open at the start of any session; it holds every open gap (A),
every unverified edge (B), everything closed with its evidence (C), and every
claim we have had to retract (D). Nothing below may assume a row is closed
that GAPS.md still marks OPEN.

### Where the novelty actually is — an honest ranking, not a pep talk

**What will NOT carry a paper**, stated plainly so effort stops going there:
predicate inconsistency as a phenomenon (prior work owns it); "LLMs make FOL
translation errors" (thoroughly covered); a detector that flags naming
inconsistency (engineering, not a contribution); prevalence numbers alone
(benchmarking, and the weakest thing to be reviewed on).

**N1 — Formalizability auditing. The strongest asset, and it is ours.**
Every NL→FOL evaluation in this literature reports accuracy against a gold
label without ever asking whether that gold label is *derivable* from the
premises the model was given. We now have the measurement showing why that
matters: on ContractNLI the ceiling moves 0% → 60% → 100% purely by changing
the annotation convention, and four of five failure blockers defeat a
*perfect* translator. That reframes an evaluation practice rather than adding
one more number to it, it comes with a reusable protocol, and it generalises
beyond FOL to SMT/LTL/Datalog. Papers that correct how a field measures get
cited by everyone who measures.

**N2 — Reachability as a gold-label-free pre-solver triage signal.** If a
conclusion's predicates appear nowhere in its premises, the goal is
unreachable by construction — computable in milliseconds, no gold label, no
model. It fires on 21–47% of legal-domain silent failures. Combined with N1's
blocker taxonomy it becomes something no existing method does: a pre-solver
diagnosis that separates *repairable* (translation-level) from *unrepairable*
(task- or formalism-level) failure. Reactive baselines cannot do this even in
principle — the solver returns a well-formed answer and raises nothing.

**N3 — The capability × language-type interaction with the severity split.**
Real, measured, ours. But most exposed to a "this is benchmarking" review and
the most likely to be duplicated by someone else. It should be a section, not
the thesis of the paper.

**Recommended position: the paper is about formalizability, and CREST is the
mitigation arm for the subset that formalizability analysis says is
repairable.** That ordering makes every existing result load-bearing —
including the ContractNLI floor, which becomes evidence rather than a failed
pilot.

### Sequenced plan — gaps → edges → findings → detection → mitigation

Deliberately in the order Tanjamul asked for. Each phase has a close-condition;
no phase starts before the previous one's condition is met and pointed at.

**P1 — Close the edges (mostly free, ~$0.5 total, no new datasets).**
Work GAPS.md section B top-down. Highest value first:
- E1: a human re-formalises the 10 ceiling-probe cases blind. *Everything in
  N1 rests on this; it is currently one non-independent annotator.*
- E8: audit how many `Uncertain` verdicts are actually Prover9 timeouts —
  those are our limitation being scored as model under-determination, and
  they contaminate the headline number.
- E3: domain-matched few-shot ablation on ContractNLI, to kill the
  demonstration-mismatch confound.
- E6: hand-classify ~30 of the overlap group into the five blockers.
- E10, E11, E12: cheap verifications.
**Close-condition:** every row in section B is CLOSED or explicitly ACCEPTED,
with a pointer.

**P2 — Build the resource that makes N1 real.** A formalizability-annotated
benchmark: naturalistic NLI items, each annotated with (a) is the gold label
derivable under convention X, (b) which blocker applies if not, (c) is the
gold label itself defensible. Target 150–300 items across FOLIO + ContractNLI
(+ SARA if adopted), multi-annotator with κ reported. **This is the dataset
Tanjamul offered to build, and it is the right one** — not another logic
corpus, but the resource that explains why the existing ones cannot be
evaluated naively. A five-person team is the right size for it; our
guidelines/reconciliation process from step 4 is the template.
**Close-condition:** released annotation set + κ ≥ 0.6 on the blocker
labels + the ceiling measured with real intervals instead of n=10.

**P3 — Detection (G2).** Reachability + schema-divergence detector, evaluated
for precision/recall against data **already committed** — 72 annotated FOLIO
cases, 300 ContractNLI runs, the full three-dataset runs. Zero API cost.
Report where it fires, where it misses, and its false-positive rate against
the Self-Refine lesson: *a detector that over-fires degrades into Self-Refine,
so precision is the critical quantity, not recall.*
**Close-condition:** a precision/recall table on both FOLIO and ContractNLI,
plus the calibration analysis (ECE/Brier) Phase 7.3 specifies.

**P4 — Mitigation (G3).** Repair only the subset P3 marks repairable.
Endpoint is **reachability restored**, not accuracy — accuracy is
ceiling-capped on ContractNLI and would understate a real repair. Ablate
risk-guided pairing against random pairing (Phase 8.4) since that is the one
algorithmic-novelty candidate.
**Close-condition:** the ablation result, whichever way it goes, with the
pre-registered fallback from Phase 8 applied if it is null.

**P5 — Write, with the limitations section generated from GAPS.md B and D.**

### Decisions still open, and they are Tanjamul's

1. **Does SARA get adopted** as the third dataset (its hand-written Prolog
   means a real ceiling exists by construction), or does the paper take the
   N1 reframing where ContractNLI's floor is itself the evidence and no third
   dataset is needed? Both are defensible; the second is cheaper and, on
   current evidence, more novel.
2. **Self-Refine on ContractNLI** — the earlier pre-registration said skip it.
   That reasoning holds for the accuracy endpoint but not for the
   *reachability* endpoint, which is not ceiling-capped: ContractNLI's
   dominant defect (`GrantsRights` vs `GrantsRight`) is visible from the
   formulas alone without a gold label, so blind self-critique might actually
   fix it here even though it failed on FOLIO. If it does, CREST's selective
   detector is less necessary; if it does not, that is a stronger argument for
   CREST than any we currently have. ~$2. **This would be a NEW
   pre-registration for a new question, not a re-analysis of the old one
   hunting for significance** — that distinction must be written down before
   the run, not after.

---

## 3.95 NOVELTY, PINNED (2026-08-22) - closes G4

> **S0 FORMULATION FREEZE APPLIED 2026-08-27.** The four claims previously
> flagged here as under correction (E15 guarantee wording, E16 pre-solver
> observability, E17 flat classes, E19 absolute formalizability) have been
> **rewritten out of the text below**, not footnoted. Original wording is in
> `docs/GAPS.md` Section D. **Novelty language remains provisional until a
> dated G5 literature search** — see the G5 → G4 dependency in
> `docs/FYDP2_PLAN.md` S0.

Tanjamul's call (2026-08-22), overriding the "submit to the nearest cycle" recommendation:
establish the novelty first, build the framework, aim for **main track**. The
cost is stated and accepted -- the October 12 ARR cycle is out of reach for a
built-and-ablated framework, so the realistic targets are ARR January 2027
(ACL 2027) or May 2027 (EMNLP 2027).

### The claim, in one paragraph

**Rewritten 2026-08-27 (S0 formulation freeze).** The previous version claimed
pre-solver classification into mutually exclusive defect classes with a
non-degradation *guarantee*. Three parts of that were wrong and are corrected
here rather than footnoted: solver-execution failure is not observable before
execution (E16), the classes are not mutually exclusive (E17), and an
acceptance heuristic does not yield a guarantee (E15). Original wording is
preserved in `docs/GAPS.md` Section D.

*Blind self-correction of LLM-produced formal translations does not work: it
cannot tell when to revise, so it behaves as a random perturbation generator
and measurably degrades the pipeline (our Self-Refine arm: net -31 on FOLIO,
significantly harmful on two of nine cells). We propose instead* **diagnostic
attribution with selective corrective policy**. *A wrong pipeline output is
diagnosed along three independent, non-exclusive axes* -- `F` *(is the instance
determinable under a stated formalization contract),* `T` *(is the produced
representation semantically faithful to the source), and* `S` *(did symbolic
execution run adequately) -- using post-execution evidence, since* `S` *is a
property of an execution and cannot be observed before one. Correction is
invoked only where the diagnosis says correction can help --* `R = (F=1 ∧ T=0)`
*-- and every candidate repair must pass a gold-label-free acceptance test
before it is adopted. In tested settings this yields* **empirical
non-degradation** *(reported with an interval, never as a theorem). What
existing training-free methods lack is the diagnostic step: Self-Refine has no
signal telling it when to fire, and Logic-LM's reactive refinement only ever
sees syntax errors, never a well-formed translation that means the wrong
thing.*

### The formulation, stated precisely

**Diagnosis.** `D(x) = (F, T, S)` — three **independent, non-exclusive** axes.
`F=0 ∧ T=0` can hold together: the translation really is defective *and*
repairing it would not recover the task. A flat class label cannot express
that, which is exactly the case where a repair layer wastes effort while
appearing justified.

| Axis | Question | Evidence available |
|---|---|---|
| `F(x; Φ, C)` | Is the instance determinable under formalism `Φ` and admissibility contract `C`? | source text + contract; **contract-relative, never absolute** |
| `T` | Is the produced representation semantically faithful to the source under `C`? | source text + produced formulas |
| `S` | Did symbolic execution run adequately? | **post-execution only**: verdict, timeout, proof trace, encoding status |

`F` is **not** an absolute "formalizable/unformalizable" property. Its
observable in E1 is *constructive recoverability under (Φ, C)*, and **no
construction found never licenses an impossibility claim** (E19).

**Repair trigger.** `R(x) = [F=1 ∧ T=0]` — a **diagnostic policy, not a
theorem**. Data may later show `F` needs to be graded rather than binary, so
the annotation protocol must define `uncertain / not-assessable` handling
before labels are collected, and the policy for `R` when `F` is uncertain must
be preregistered (conservative = do not repair) rather than settled at
implementation time.

**Architecture, in the order things actually happen:**

| Layer | Role | Status |
|---|---|---|
| Pre-solver triage | *optional* cheap risk signals | not load-bearing; both cheap signals measured weak on naturalistic text |
| Solver execution | the actual prover | unchanged |
| Post-execution attribution | aggregate F/T/S evidence | the contribution |
| Selective corrective policy | repair only predicted-repairable translation failures | the contribution |
| Acceptance / verification | empirical safety mechanism | **formal guarantee only if later proven** |

This drops FYDP-1's "intercept everything before the solver" constraint. That
constraint bought nothing here (Prover9 costs ~2–5s and is free in our
pipeline) while making the `S` axis unobservable. **FYDP-1 proposed CREST as a
proactive pre-solver framework; FYDP-2's evidence revised it.** That is
scientific evolution and is written up as such in the thesis, not hidden.

### Why each piece is forced by our own measurements, not chosen for elegance

- **Why diagnosis, not a scalar risk score.** Four of the five ContractNLI
  blockers defeat a *perfect* translator (missing obligation, open-world
  permission gap, absent world-knowledge witness, missing deontic bridge). A
  scalar "risk = 0.8" gives the repair layer no way to tell those apart from a
  repairable defect, so it would attempt repairs that cannot succeed. The
  layer must know *what kind* of failure it faces, and must be willing to say
  "not repairable, do not touch".
- **Why repair cannot be deterministic.** Of 147 unreachable goals across
  every committed run, exactly ONE is fixable by string normalisation; 146 are
  semantic divergence (ConferRights vs GrantRights). Measured, not assumed --
  so the repair component genuinely needs a learned/semantic model, which is
  what makes Phase 8 a contribution rather than plumbing.
- **Why verified acceptance is the core.** Self-Refine rewrote 47/50 examples
  and emitted NO_ISSUES zero times. Its damage came entirely from applying
  unverified rewrites. An acceptance test that rejects any repair failing to
  improve the diagnosed defect while preserving faithfulness converts that
  failure mode into a no-op. This is the difference between our method and the
  baseline that falsified the naive version of it.

### Pre-registered falsification gates for the framework itself

Written before the framework exists, so a null result cannot be argued away:

1. **Discrimination gate (REPLACES the original coverage gate, 2026-08-22).**
   The original wording here was "coverage above ~25% on FOLIO". That gate was
   mis-specified and it PASSED on a worthless signal: structural divergence
   reached 56% coverage on FOLIO while carrying no information (lift ~1.0).
   Corrected gate: a signal counts only if **lift > 1.0 with a 95% CI whose
   lower bound excludes 1.0**, at a practically useful precision (target
   roughly >=70% on the attribution decision). Coverage is reported alongside
   but never gates on its own. Original wording preserved in GAPS.md Section D.
2. **Non-degradation gate.** If the accept-test lets through any repair that
   makes a previously-correct example wrong, the central guarantee is false
   and must be withdrawn, not weakened.
3. **Ablation gate (Phase 8.4, restated).** Diagnosis-conditioned firing vs
   firing on every example must show a significant difference. If it does not,
   the selectivity is decoration and the honest conclusion is that we have a
   repair model, not a framework.
4. **Baseline-parity gate.** The comparison against Self-Refine must use the
   same repair model with the conditioning removed. Comparing our tuned repair
   against the published Self-Refine prompt would measure the repair model,
   not the idea.

### Build order (each step gated by the one before)

1. ~~`structural_diff.py` for coverage~~ **DONE 2026-08-22, NEGATIVE RESULT.**
   Built and measured: lift ~1.0 on naturalistic data (FOLIO 1.03, ContractNLI
   0.86-0.98), informative only on templated synthetic text where it fires
   rarely (PrOntoQA 5.07, ProofWriter 6.35). It does not provide the coverage
   this step assumed. Full result: `RESULTS_SNAPSHOT.md` 1d. Consequence: the
   deterministic layer cannot detect meaning-level divergence on naturalistic
   text, which is now an empirical constraint on the design rather than an
   assumption.
2. `risk_combiner.py` -- diagnosis output, calibrated (ECE/Brier, Phase 7.3).
   NOTE: with signal 2 negative, this cannot be a weighted combination of two
   working signals. What it combines, and whether a learned component is
   required this early, is now an open design question, not a scheduled step.
3. Acceptance test -- the non-degradation guarantee, tested against gate 2.
4. Repair model -- distillation warm-start then DPO (Phase 8), evaluated only
   on the repairable class, endpoint reachability-restored.
5. Ablations -- gates 3 and 4.

Everything up to step 4 runs on data already committed, at zero API cost.

---

## 3.96 THE A*-TARGET PROGRAMME (set 2026-08-22)

Tanjamul's instruction: implement the framework, keep a strong methodology, aim
only at top A* / Q1, take the time it needs, always scale up, and if something
genuinely forward-looking can be stood up, plan for that instead of small work.
This section replaces the "nearest cycle" thinking in 3.9 as the governing
target. 3.9's build order survives inside it.

### The problem we have not found formulated elsewhere

**Wording note (2026-08-27):** the heading previously read "the problem nobody
has formulated". That is an unverified novelty claim and is not permitted to
return until a dated G5 search supports it (`RESEARCH_STANDARDS.md` rule 4,
GAPS.md G5). Note also that our own related-work pass records one of the two
near-neighbour papers as read at ABSTRACT level only, not full text.

When a neuro-symbolic pipeline returns a wrong answer, no existing work can say
WHOSE FAULT IT WAS. Three distinct causes are collapsed into one accuracy
number:

  (i)   the task is not formalizable -- no correct translation could have
        derived the gold label from the given premises;
  (ii)  the translation lost or distorted meaning;
  (iii) the solver failed (timeout, incompleteness, encoding limits).

Every autoformalization paper we have read reports a number mixing all three,
then attributes the whole of it to (ii). Our own measurements this month show
that is wrong in both directions: (iii) is nearly innocent -- 30 of 35
story-level "the solver is to blame" verdicts collapsed under derivation
checking, leaving 1 of 72 -- while (i) is large and entirely unmeasured, with
four of five ContractNLI blocker classes defeating a *perfect* translator and
the ceiling moving 0% -> 60% -> 100% under nothing but a change of annotation
convention.

### The contribution

**Failure attribution for neuro-symbolic pipelines: diagnose each wrong output
along three independent axes `D(x) = (F, T, S)` without a gold label, using
post-execution evidence; then apply correction only where the diagnosis says it
can help, `R = (F=1 ∧ T=0)`, under an acceptance test that yields empirical
non-degradation.**

*(Corrected 2026-08-27. The earlier wording — "assign to (i), (ii) or (iii) …
before the solver runs … under a guarantee" — was wrong three ways: `S` is not
observable before execution, the axes are not mutually exclusive, and an
acceptance heuristic is not a guarantee. See GAPS.md E15/E16/E17.)*

Why this is A*-shaped rather than incremental:
- It is a **problem formulation** others can adopt, not one more detector.
- It carries a **measurable property** (attribution precision against human
  ground truth) and a **guarantee** (repair can never worsen the pipeline --
  see 3.95).
- It **changes how results must be reported**: an accuracy number that has not
  been attribution-decomposed is uninterpretable, because it silently credits
  or blames the wrong component.
- It **generalises beyond FOL**, which separates a good paper from a landmark
  one -- see P-D.

### Programme, with the gate that ends each phase

> **The five-phase sequence below is SUPERSEDED by `docs/FYDP2_PLAN.md`'s
> seven stages, which fold in the edge-closing work this sketch omitted.
> The problem formulation and contribution statement above remain current;
> only the sequencing here is history.**


Timeline deliberately 12-18 months; the thesis checkpoint is protected inside
it.

**P-A. Formalize attribution and build the attributor on FOL.** (~2 months,
near-zero cost.) Definitions of (i)/(ii)/(iii) precise enough for two
annotators to apply. Signals: reachability (built), structural divergence, and
whatever else survives testing. Output is an attribution label, not a scalar.
*Gate:* attribution precision against human labels on FOLIO + ContractNLI.
Below ~70% on the three-way decision, the definitions get revised before
anything is built on top.

**P-B. Build the resource -- the moat.** (~3 months, five people.) A
formalizability-and-attribution annotated benchmark: per item, is the gold
target derivable under a stated convention, which blocker applies if not, and
the attribution class. 300-500 items across FOLIO, ContractNLI and one further
source. Multi-annotator with kappa.
*Gate:* kappa >= 0.6 on the attribution class. This is also the honest answer
to G1 -- it closes the single-dataset weakness by producing the resource that
explains why single-dataset evaluation was unsound, instead of hunting one more
dataset.
*Why it is the moat:* five people can produce an annotated resource a lone
researcher cannot, and resource papers are cited for years.

**P-C. Repair with the non-degradation guarantee.** (~3 months.) Distillation
warm-start then DPO on the (ii)-attributed subset only. Endpoint is
derivability restored, never raw accuracy.
*Gates:* the four already pre-registered in 3.95, unchanged.
*Resourcing (decided 2026-08-22):* corrector base-model size is not to be
chosen by what fits free/local hardware -- Tanjamul's instruction is no
compromise on model runs, best achievable result required. Size becomes an
ablation variable (1B/3B/8B compared empirically, same discipline as the
Phase 8.4 pairing ablation) rather than a foregone small-model choice, and if
the best-performing size needs full LoRA/QLoRA DPO beyond free-tier limits
(RTX 4060 8GB local, Kaggle T4 16GB/12h session cap), rented cloud GPU-hours
is the correct resourcing. **Blocked on a cloud-compute budget figure from
Tanjamul** before this phase's exact plan can be written -- see GAPS.md E13.

**P-D. Cross-formalism generality -- the ceiling-lifting step.** (~4 months.)
Repeat attribution on at least one further target formalism: SMT via Z3, or LTL
on the requirements-engineering benchmark noted in 3.5. If the same three-way
attribution holds with a different solver and a different formal language, the
contribution stops being a FOL finding and becomes a property of
neuro-symbolic pipelines.
*Gate:* if attribution precision collapses on the second formalism, report it
scoped rather than stretching the claim.

**P-E. Scale and write.** Multi-seed throughout, additional open models (Qwen
2.5, Mistral alongside Llama -- free on Kaggle), full clustered stats. Scale is
targeted where intervals are too wide to support a claim, never for the size of
the number.

### The thesis is protected inside this

P-A + P-B + P-C constitute a complete, defensible thesis on their own,
independent of whether P-D lands. The FYDP deliverable therefore does not
depend on the most ambitious phase succeeding -- which is the condition under
which attempting the ambitious phase is rational rather than reckless.

### Honest risks, stated once

- A* is never guaranteed by a plan. A plan raises the ceiling and keeps the
  work strong at a good venue if the top one rejects.
- P-B is simultaneously the bottleneck and the differentiator. If annotation
  cannot be sustained, the programme reduces to a method paper.
- Someone may formulate attribution first. G5 becomes a recurring task, not a
  one-off before submission.
- P-D needs new grounders. Real engineering, budgeted as a phase.

---

## 4. Where to find the underlying evidence

- `docs/RESULTS_SNAPSHOT.md` — the three headline tables (capability ×
  dataset, Self-Refine matrix, confidence-detection AUROC), all with
  clustered CIs and McNemar p-values
- `docs/CREST_Experimental_Record.docx` — the full narrative report with
  hyperlinks to every code file, every result JSON, and 13 milestone commits
- `docs/MASTER_PLAN.md` — the phase-by-phase plan of record with inline
  result annotations, including the retracted-claim log and the pre-registered
  kill gates
- `crest/experiments/logs/*.json` — every individual run's raw results
