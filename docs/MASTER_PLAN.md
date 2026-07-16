---
title: "CREST — FYDP 2 Master Research Plan"
subtitle: "Phase-by-Phase Roadmap Toward an ACL / EMNLP / NeurIPS-Quality Contribution"
author: "Team CREST — Md. Tanzamul Azad, Israt Jerin Porshi, Swarup Deb Nath, Jahidul Islam, Satyajit Kumar Baidya | Supervisor: Dr. Mohammad Nurul Huda"
date: "July 2026"
---

# CREST — Master Research Plan

**Framework:** Proactive Risk Mitigation for Symbolic Translation in Neuro-Symbolic AI
**Objective:** Not just a passable undergraduate thesis — a research contribution genuinely competitive for ACL / EMNLP / NAACL main track or Findings, with NeurIPS treated as a stretch target.
**Team size:** 5
**Horizon:** 12–18 months

> **Governing principle:** every phase below exists to answer a specific research question or to de-risk a specific claim. Nothing is built "because the poster says so." If a phase stops making sense after new evidence, the plan changes — the plan does not override the evidence.

---

## How to read this document

Each phase lists: **what** we do, **why** we do it (the research/engineering justification), and **what we will have in hand** once it's done. Phases are sequenced so that later, more speculative or resource-heavy work (trained models, multi-dataset scaling) only begins after the foundational, falsifiable claims have been tested.

---

## Phase 0 — Environment Verification
**Status gate — blocking, must complete before Phase 1**

**What:** Verify GPU, CUDA, Z3, and Hugging Face access on the local RTX 4060 machine.

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
python -c "import z3; print(z3.get_version_string())"
python -c "from huggingface_hub import whoami; print(whoami())"
```

**Why:** The cheapest bugs to catch are infrastructure bugs. Discovering a CUDA mismatch or an un-accepted Llama license three days into coding costs days; discovering it now costs ten minutes.

**Achieve:** Clean, confirmed output from all four commands.

---

## Phase 1 — Core Infrastructure + FOLIO Foundation
**Week 1**

| Step | What | Why | Achieve |
|---|---|---|---|
| 1.1 | Local Llama-3.1-8B-Instruct, 4-bit quantized, fixed seed, `temperature=0`, single frozen prompt template, full JSON logging of every call | Reproducibility is itself a claim in the paper. A "training-free, deterministic detector" claim is meaningless if the same input can produce different outputs | A wrapper function: NL premise in → FOL string out, every call logged. Code: `crest/crest/inference/llama_harness.py`. Blocked as of 2026-07-16 on Meta's manual gated-repo approval (requested, pending) |
| 1.2 | FOLIO loader (`tasksource/folio`) — load, then **print actual field names**, do not assume schema | An assumed schema that's wrong silently corrupts every downstream number | A converted, common-schema dataset object. **Done 2026-07-16**: `crest/data/loaders/folio_loader.py`. Confirmed schema: `story_id, example_id, premises, premises-FOL, conclusion, conclusion-FOL, label` (train=1001, validation=203). Found and fixed a real data-quality wrinkle: 14/1204 rows have leading/trailing blank lines in `premises`/`premises-FOL` that shift naive `.split("\n")` alignment — filtered, not a genuine content mismatch |
| 1.3 | Clone `teacherpeterpan/Logic-LLM` repo, locate its FOL→solver grounding code, attempt reuse | Logic-LM is our baseline; reusing its grounding logic keeps comparisons apples-to-apples and avoids reinventing a bug-prone parser | **Verdict reached 2026-07-16: not reusable, adaptation not viable either.** Logic-LM's Z3 module (`code_translator.py`, `sat_problem_solver.py`) targets its own custom pseudo-code DSL (`ForAll([x:Type], ...)`, `# Declarations`/`# Constraints`/`# Options` blocks) built for AR-LSAT/LogicalDeduction — it doesn't parse FOLIO's actual `∀x (P(x) → Q(x))` notation at all. Logic-LM's real FOLIO-specific code (`solver_examples/folio_prover9.py`) uses **Prover9 via NLTK, not Z3** — and it's one hardcoded example, not a general parser. This also confirms directly (not just via secondhand notes) that FOLIO's own gold-FOL labels were verified with Prover9 |
| 1.4 | ~~Finalize the FOL→Z3 grounder~~ **Changed 2026-07-16: grounder uses Prover9, not Z3** (see 1.3 — no ready Z3 path existed anyway, and Prover9 matches both FOLIO's own gold-label verification and Logic-LM's FOLIO precedent, strengthening ceiling-accuracy comparability). This is a single, consistent choice for **both** the Phase 2.1 ceiling check and the main experimental pipeline — mixing solvers between phases would defeat the point of the ceiling gate. Report chapters (`report/3.design.tex`) still describe Z3 as "the current implementation" and need updating in Phase 11 to avoid a thesis/code mismatch. | This is the single biggest bottleneck component — everything downstream depends on it | **Done and validated 2026-07-16**: `crest/crest/grounding/fol_to_prover9.py`. NLTK parses FOLIO's Unicode FOL notation (after symbol normalization + custom paren-aware XOR/⊕ expansion, since NLTK has no native XOR), Prover9 checks entailment. Windows can't run the vendored Prover9 binary directly (Linux ELF) — routed through WSL (`wsl -d Ubuntu -- ...`), which is a **new team-wide setup requirement**, not just this machine's quirk. Verified end-to-end on a real FOLIO example (including the ⊕ case) and on synthetic True/False/Uncertain cases — all three label branches confirmed correct |

---

## Phase 2 — Ceiling Validation
**Late Week 1 / early Week 2**

| Step | What | Why | Achieve |
|---|---|---|---|
| 2.1 | Run FOLIO **gold** FOL through the grounder, compare against gold labels | If the grounder mislabels *correct* FOL, the bug is in grounding, not in LLM translation. Every later "silent failure" number depends on knowing this first | Gold-FOL ceiling accuracy — an honest number, whatever it turns out to be |
| 2.2 | ProofWriter + PrOntoQA loaders, using Logic-LM's **exact** published sample splits (ProofWriter depth-5 OWA, 600 examples; PrOntoQA 5-hop fictional-characters, 500 examples) — do not re-sample independently | Re-sampling breaks direct comparability with Logic-LM's reported numbers | Schema-fit loaders, tagged with a `has_gold_fol` flag (True only for FOLIO) |

**Decision gate — pre-registered now, before seeing the result, to prevent motivated reasoning later:**

| Ceiling accuracy | Action |
|---|---|
| ≥ 85% | Proceed. Treat the residual gap from 100% as gold-label noise (LINC found ~22/204 ≈ 11% erroneous gold-FOL in the original FOLIO validation audit) plus acceptable grounder imprecision — do not chase it to zero. |
| 70–85% | Pause. Manually inspect a sample of ceiling failures before proceeding — likely a fixable grounder bug rather than a fundamental one, but must be confirmed, not assumed. |
| < 70% | Stop. Do not report any downstream silent-failure number until the grounder is fixed — the evaluation is untrustworthy below this line. |

These thresholds are a starting recommendation grounded in the LINC gold-label-noise evidence above, not an empirically derived fact — revise them with the team/supervisor if better evidence surfaces, but do so *before* running Phase 2.1, not after seeing a result you'd like to keep.

---

## Phase 3 — Vanilla Pipeline + Silent-Failure Measurement
**Week 2**

| Step | What | Why | Achieve |
|---|---|---|---|
| 3.1 | Run vanilla NL→Llama→FOL→Z3 on a 50–100 example subset first, then scale to the full FOLIO validation split | Debugging on a small subset is cheap; debugging after a full-dataset run is expensive | Vanilla accuracy + a three-way bin: correct / loud failure / **silent failure** |
| 3.2 | Apply the strict silent-failure definition — count only among examples where gold-FOL grounding was already verified correct | Prevents conflating grounder bugs with genuine LLM translation errors | A clean, defensible silent-failure prevalence number |

---

## Phase 4 — Falsification Gate: Self-Refine
**Week 3 — the most important week of Month 1**

| Step | What | Why | Achieve |
|---|---|---|---|
| 4.1 | Implement the Self-Refine baseline on the same harness (vanilla FOL → LLM self-critiques → re-translates) | This is a published, training-free, generic method. If it closes most of the silent-failure gap on its own, CREST's additional machinery has no justification | Self-Refine's silent-failure rate on the same subset |
| 4.2 | Compare vanilla vs. Self-Refine gap | This single comparison can validate or falsify the entire thesis | A go/no-go decision on the current framing — made honestly, not assumed in advance |

---

## Phase 5 — Annotation Track
**Starts Week 1, runs in parallel through Month 1–2**

| Step | What | Why | Achieve |
|---|---|---|---|
| 5.1 | Draft formal guidelines for six error types: NEGATION_LOSS, PREDICATE_INCONSISTENCY, QUANTIFIER_ERROR, XOR_COLLAPSE, IMPLICATION_ERROR, ARITY_MISMATCH | Doesn't depend on the pipeline being ready — no reason to delay it | Guideline document v1 |
| 5.2 | Recruit 2 annotators, annotate 200+ premises | Cohen's/Fleiss' Kappa ≥ 0.6 is a non-negotiable minimum for any credible venue | Inter-annotator agreement score |
| 5.3 | Re-measure the confidence/error anti-correlation on the larger sample | The original r = 0.34 (n = 45, single annotator) is too weak to publish as-is | A statistically meaningful correlation number — or honest evidence that it doesn't hold |

---

## Phase 6 — Month 1 Decision Review
**End of Week 4**

**What:** Consolidate ceiling accuracy, vanilla prevalence, Self-Refine gap, and annotation agreement into one honest supervisor update.

**Why:** This is the checkpoint where the project either continues on its current framing or is redirected — cheaply, in Month 1, rather than expensively, in Month 4.

**Achieve:** A one-page evidence summary, not a partially-trained model.

---

## Phase 7 — Detector Formalization
**Month 2**

| Step | What | Why | Achieve |
|---|---|---|---|
| 7.1 | Add a structural-diff signal — extract negation count, quantifier scope, connective type, and arity from the FOL's AST | The predicate checker and back-translation/BERTScore signals can both miss negation-drop errors, which are the flagship danger case. This closes that gap | A new, formally defined detection signal |
| 7.2 | Design a risk-combination function calibrated on annotated data (e.g. logistic combination), replacing ad-hoc thresholds | Turns an arbitrary heuristic into a justified, learned component | **Algorithm 1** — formal specification + implementation |
| 7.3 | Run a calibration analysis (Expected Calibration Error / Brier score) on the risk score | An achievable, legitimate theoretical-depth contribution without requiring new deep theory | A quantified answer to "when the risk score says 0.8, is the error rate actually ~80%?" |

---

## Phase 8 — Risk-Guided Corrector
**Month 2–3 — highest priority for novelty**

| Step | What | Why | Achieve |
|---|---|---|---|
| 8.1 | Formalize the risk-guided preference-pair construction procedure for DPO | This is the project's one genuine algorithmic-contribution opportunity — everything else is a combination of known components | **Algorithm 2** — formal specification |
| 8.2 | Use GPT-4o (or another capable LLM — any is acceptable here, budget allows) as an *offline* distillation teacher to generate training data | Established distillation practice; the teacher never runs at inference/deployment time, so the deployed pipeline stays local and API-free regardless of which model generates the training data. Clarified 2026-07-16: "own model everywhere" governs the *deployed* detector+corrector, not this offline data-generation step — not a hard ban on using GPT-4o here | A distillation dataset |
| 8.3 | Distillation warm-start, then DPO fine-tuning on the small corrector model | Full RL was ruled out as unstable on available hardware | Trained corrector v1 |
| 8.4 | Ablation: risk-guided pairing vs. random/generic pairing | The only way to actually support the novelty claim rather than just asserting it | Evidence for (or against) the core algorithmic contribution |

**Before starting 8.3:** confirm actual VRAM on the RTX 4060 (8GB and 16GB variants exist) and size the corrector model accordingly. DPO training (policy + reference model + optimizer state + activations) alongside Llama-3.1-8B inference work on the same box needs an explicit budget worked out now, not discovered mid-run. Also confirm within the team who owns this distillation/DPO work specifically — it doesn't map onto the FYDP1 role split (forward/back-translation, predicate-consistency, judge, Z3 integration) and needs an explicit owner.

**Pre-registered fallback if 8.4 is null (no significant gap between risk-guided and random/generic pairing):** this is the single point of failure for the paper's main novelty claim, so the fallback framing should be decided now, not improvised in Month 3 after a disappointing result. Two candidates, not commitments:
- Reposition as a **measurement + calibration** contribution, leaning on Phase 7.3's ECE/Brier analysis, rather than a correction-method paper.
- Reposition as a **systems/framework** contribution (the proactive pre-solver architecture itself), with the trained corrector reported as an honestly-ablated component rather than the headline result.

---

## Phase 9 — Multi-Dataset Extension
**Month 3**

**What:** Run the full pipeline on ProofWriter and PrOntoQA.

**Why not sooner:** Scaling to three datasets before the FOLIO pipeline is stable makes debugging ambiguous — a bug could be anywhere.

**Achieve:** Prevalence and improvement numbers across all three datasets — the generalization evidence a main-track reviewer expects.

---

## Phase 10 — Rigor Pass: Ablations, Multi-Seed, Significance
**Month 3–4**

**What:** Remove each signal (predicate checker, structural diff, corrector) one at a time; run multi-seed trials; compute statistical significance.

**Why:** Without this, every "improves" or "better" claim in the paper is an unsupported assertion — exactly what a reviewer is trained to challenge.

**Clarification (2026-07-16):** "multi-seed" does not refer to decoding-time stochasticity — Phase 1.1 fixes `temperature=0` and a frozen prompt template specifically so the detector is deterministic, and that determinism is itself a claim in the paper. "Multi-seed" here means (a) DPO training-seed variance (initialization, data shuffling — genuinely stochastic) and (b) variance across repeated evaluation subsample draws, if subsets rather than full splits are used anywhere. Keep this distinction explicit in the eventual results chapter — a reviewer who reads "deterministic detector" in Phase 1 and "multi-seed" in Phase 10 without this clarification will flag it as an internal inconsistency.

---

## Phase 11 — Thesis Writing
**Starts Month 1, grows in parallel throughout**

**What:** Begin with result-independent chapters — Related Work, Motivation, Methodology/System Architecture. Hold Results/Discussion chapters until after Phase 6 and Phase 10.

**Why:** Thesis defense standards tolerate exploratory and preliminary content; writing the result-independent chapters early costs nothing and directly reduces later paper-writing effort, since this content is largely reusable.

**Addition (2026-07-16):** the Related Work chapter needs a second pass immediately before Phase 12 (paper draft), not just once in Month 1. This is a fast-moving area (LLM + symbolic reasoning safety); "someone published this in the meantime" is one of the most common ACL/EMNLP rejection reasons for exactly this proactive-pre-solver framing. Budget an explicit literature recheck as its own step, not an assumption that the Month-1 pass still holds by Month 10-12.

---

## Phase 12 — Paper Draft
**Begins Month 3–4, after the Phase 4 and Phase 6 gates are resolved**

**What:** Distill the relevant thesis chapters into a compressed, venue-formatted draft — not a from-scratch rewrite.

**Why then and not now:** Writing a paper draft before the falsification gate is resolved risks a full rewrite if the framing changes. The next realistic ARR/ACL/EMNLP/NeurIPS deadlines are likely several months out from Month 1 — verify exact dates on the official ARR and conference sites before committing to a specific cycle.

---

## Governing Decision Gates (kill criteria — treated as real, not rhetorical)

| Condition | Action |
|---|---|
| Gold-FOL ceiling accuracy below 70% (see Phase 2's pre-registered 85/70–85/<70 breakdown) | Stop; fix the grounder before interpreting any other number |
| Self-Refine closes most of the silent-failure gap | Stop; reconsider CREST's framing and contribution immediately |
| Silent-failure prevalence is low (e.g. under ~15%) | Weaken the general "silent failure is common" narrative; pivot toward specific high-severity error types (negation, XOR) |
| Inter-annotator Kappa stays below 0.6 after guideline revision | The error taxonomy itself needs rework before any claim built on it is publishable |
| Phase 8.4 ablation shows no significant gap between risk-guided and random/generic DPO pairing | The paper's one algorithmic-novelty candidate is null. Reposition immediately as a measurement+calibration contribution (Phase 7.3) or a systems/framework contribution with the corrector reported as an honestly-ablated component — do not keep searching for a significant result post hoc |

---

## Honest Novelty Assessment (carried forward, not re-litigated each time)

- **Predicate-naming inconsistency as a phenomenon:** not novel; prior work (e.g. the arbitrariness literature, Thatikonda et al.) already covers it.
- **The actual contribution:** a proactive, pre-solver risk-detection-and-repair layer, grounded in a real, multi-dataset prevalence study — a method + measurement contribution, not a discovery claim.
- **The one genuine algorithmic novelty candidate:** the risk-guided preference-pair construction procedure for DPO (Phase 8.1). This is where effort should concentrate if the goal is to move the novelty score, not the detection side, which has a structurally low ceiling regardless of polish.
- **Venue realism:** ACL/EMNLP Findings is the realistic floor; main track is reachable with one clean, statistically strong result (multi-dataset prevalence + CREST beating both Logic-LM and Self-Refine with significance). NeurIPS is a harder fit unless the DPO contribution stands on its own as a methodological result.

---

*This document reflects the state of planning as of July 2026. It should be revised the moment new evidence (particularly from Phase 4 and Phase 6) contradicts any assumption above — the plan serves the research, not the reverse.*
