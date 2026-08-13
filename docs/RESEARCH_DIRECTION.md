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

**Step 1 of the sequential plan is now complete. Proceeding to step 2: the
FOLIO failure-case classification.**

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
