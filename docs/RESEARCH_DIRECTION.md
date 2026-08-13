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
