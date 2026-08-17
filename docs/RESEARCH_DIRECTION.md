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
