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

## 2. The 4-week plan (concrete, tied to actual project infra)

| Week | Task | How (with what we already have) |
|---|---|---|
| 1 | Manually classify the ~29 remaining gpt-4o strict-set failures on FOLIO (wrong_direction + under_determination) by linguistic phenomenon: nested quantifiers, multi-hop dependency chains, negation scope, rare/compound predicates, comparative/numeric constructions | Data already collected, zero new API cost — start immediately |
| 1–2 | Investigate feasibility of a second naturalistic dataset | Literature/dataset search |
| 2 | Write an annotation protocol and get a second annotator (teammate) to label 50–100 cases; compute Cohen's κ | `crest/annotation/guidelines.md` exists as a starting point, needs scaling |
| 3 | Build a schema-consistency detector proof-of-concept; measure precision/recall on the 28 hand-analyzed cases | Per the schema-first detect→repair design discussed earlier (predicate-role consistency, argument-type consistency, NL↔FOL content-mismatch signals) |
| 4 | Start the paper draft; prepare a one-page supervisor meeting brief covering both tracks separately | — |

**Recommended starting point: Week 1's task.** It's free, can start today, and
feeds both the paper (the "where exactly does frontier still fail" RQ) and
the thesis (Chapter 3/5 material) simultaneously.

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

**Action item added to the 4-week plan:** read both papers in full during
Week 1–2 (alongside the literature-currency check), and write one paragraph
each explaining precisely how CREST's methodology and claim differ.

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
