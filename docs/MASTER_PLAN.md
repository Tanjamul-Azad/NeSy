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

> **Standing rule (2026-07-18):** this document is the single source of truth for what the plan actually is, across every session and every chat. Whenever a real plan change happens — a phase's approach changes, a tool/library decision changes, a gate's threshold changes, something gets unblocked or reblocked — update this document immediately, in the same session, not as a followup. Don't let the plan drift out of sync with what's actually being done.

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
| 1.1 | Local Llama-3.1-8B-Instruct, 4-bit quantized, fixed seed, `temperature=0`, single frozen prompt template, full JSON logging of every call | Reproducibility is itself a claim in the paper. A "training-free, deterministic detector" claim is meaningless if the same input can produce different outputs | A wrapper function: NL premise in → FOL string out, every call logged. Code: `crest/crest/inference/llama_harness.py`. **Unblocked 2026-07-16** on the Meta-gating question: weights pulled from `NousResearch/Meta-Llama-3.1-8B-Instruct` (verified byte-identical safetensors shards against the official repo). **Compute moved to Kaggle 2026-07-18**: 4-bit loading via bitsandbytes segfaulted reproducibly on the local Windows machine — same exact tensor, every time, across two CUDA versions and multiple `device_map` configs, strongly indicating a Windows-specific bitsandbytes bug rather than a config issue. Local hardware is also genuinely tight (8GB VRAM, ~16GB system RAM). GPU-heavy work (loading, inference, later training) now runs on Kaggle (free T4x2/P100, 16GB VRAM, Linux) via `crest/scripts/crest_kaggle.ipynb`, which clones the GitHub repo fresh each session — GitHub remains the single source of truth, not the Kaggle notebook itself. **Working end-to-end as of 2026-07-24**, confirmed on Kaggle: P100 initially hit a `named symbol not found` bitsandbytes CUDA error (likely Pascal architecture/compute-capability 6.0 too old for the precompiled 4-bit kernels) — switched accelerator to T4 x2, resolved. Then hit one more real bug: `apply_chat_template()` returns a `BatchEncoding` (no `.shape`) in the transformers version Kaggle has unless `return_dict=True` is passed explicitly — was being used positionally and indexed like a tensor, both wrong. Fixed by requesting `return_dict=True` and unpacking with `**inputs` into `generate()`. First real translation confirmed correct: "All students who study hard pass their exams." → `∀x (Student(x) ∧ StudyHard(x) → PassExam(x))` |
| 1.2 | FOLIO loader (`tasksource/folio`) — load, then **print actual field names**, do not assume schema | An assumed schema that's wrong silently corrupts every downstream number | A converted, common-schema dataset object. **Done 2026-07-16**: `crest/data/loaders/folio_loader.py`. Confirmed schema: `story_id, example_id, premises, premises-FOL, conclusion, conclusion-FOL, label` (train=1001, validation=203). Found and fixed a real data-quality wrinkle: 14/1204 rows have leading/trailing blank lines in `premises`/`premises-FOL` that shift naive `.split("\n")` alignment — filtered, not a genuine content mismatch |
| 1.3 | Clone `teacherpeterpan/Logic-LLM` repo, locate its FOL→solver grounding code, attempt reuse | Logic-LM is our baseline; reusing its grounding logic keeps comparisons apples-to-apples and avoids reinventing a bug-prone parser | **Verdict reached 2026-07-16: not reusable, adaptation not viable either.** Logic-LM's Z3 module (`code_translator.py`, `sat_problem_solver.py`) targets its own custom pseudo-code DSL (`ForAll([x:Type], ...)`, `# Declarations`/`# Constraints`/`# Options` blocks) built for AR-LSAT/LogicalDeduction — it doesn't parse FOLIO's actual `∀x (P(x) → Q(x))` notation at all. Logic-LM's real FOLIO-specific code (`solver_examples/folio_prover9.py`) uses **Prover9 via NLTK, not Z3** — and it's one hardcoded example, not a general parser. This also confirms directly (not just via secondhand notes) that FOLIO's own gold-FOL labels were verified with Prover9 |
| 1.4 | ~~Finalize the FOL→Z3 grounder~~ **Changed 2026-07-16: grounder uses Prover9, not Z3** (see 1.3 — no ready Z3 path existed anyway, and Prover9 matches both FOLIO's own gold-label verification and Logic-LM's FOLIO precedent, strengthening ceiling-accuracy comparability). This is a single, consistent choice for **both** the Phase 2.1 ceiling check and the main experimental pipeline — mixing solvers between phases would defeat the point of the ceiling gate. Report chapters (`report/3.design.tex`) still describe Z3 as "the current implementation" and need updating in Phase 11 to avoid a thesis/code mismatch. | This is the single biggest bottleneck component — everything downstream depends on it | **Done and validated 2026-07-16**: `crest/crest/grounding/fol_to_prover9.py`. NLTK parses FOLIO's Unicode FOL notation (after symbol normalization + custom paren-aware XOR/⊕ expansion, since NLTK has no native XOR), Prover9 checks entailment. Windows can't run the vendored Prover9 binary directly (Linux ELF) — routed through WSL (`wsl -d Ubuntu -- ...`), which is a **new team-wide setup requirement**, not just this machine's quirk. Verified end-to-end on a real FOLIO example (including the ⊕ case) and on synthetic True/False/Uncertain cases — all three label branches confirmed correct |

---

## Phase 2 — Ceiling Validation
**Late Week 1 / early Week 2**

| Step | What | Why | Achieve |
|---|---|---|---|
| 2.1 | Run FOLIO **gold** FOL through the grounder, compare against gold labels | If the grounder mislabels *correct* FOL, the bug is in grounding, not in LLM translation. Every later "silent failure" number depends on knowing this first | Gold-FOL ceiling accuracy — an honest number, whatever it turns out to be. **In progress 2026-07-18**: `crest/crest/evaluation/ceiling_check.py` built (no GPU/Kaggle needed for this step — pure FOLIO loader + Prover9 grounder, both run locally). Confirmed some FOLIO gold-FOL entries are themselves malformed (e.g. example_id 1014/1015/1016 has an unbalanced extra `)` in the raw `premises-FOL` string) — a genuine FOLIO data issue, not a grounder bug, matching the LINC-era caveat already in this document; tagged separately (`MALFORMED_GOLD_FOL`) so it doesn't get conflated with real grounder failures. Also **found and fixed a real grounder bug**: `_expand_xor` in `fol_to_prover9.py` assumed `⊕` always sits inside its own dedicated enclosing parens (true in earlier tested examples), but example_id 1364 has a bare, unparenthesized `⊕` at the end of an implication (`¬(...) → Cute(rockie) ⊕ Skittish(rockie)`) — fixed by scanning for the actual adjacent FOL term on each side of `⊕` instead of assuming an enclosing paren exists. **Full validation split (n=203) run 2026-07-18, after two more real fixes:**
1. WSL/Prover9 stdout decode crashed on non-ASCII constants (e.g. "świątek") — fixed with lenient decoding (`errors="replace"`); cosmetic only, doesn't affect the actual proof search.
2. **Major bug, found via manual proof inspection (not just accuracy numbers):** Prover9's default naming convention treats any identifier starting with letters t-z as an *implicitly-quantified variable*, not a constant. FOLIO's camelCase constants routinely start with those letters (e.g. "unitedStatesCitizenship" starts with 'u') and were being silently corrupted into free variables mid-proof — confirmed by inspecting the actual clausified proof for example_id 1410, where "unitedStatesCitizenship" literally became a bare variable "y". Fixed by adding `set(prolog_style_variables)` to the Prover9 input (constants safe regardless of first letter; explicit `all x`/`exists y` quantifiers still bind correctly since that's determined by the quantifier keyword, not the naming convention).

Also broadened `MALFORMED_GOLD_FOL` tagging in `ceiling_check.py` to catch `ValueError` (our own paren-scan rejecting bad input) and `Prover9FatalException` (Prover9 itself rejecting input, e.g. a predicate used with two different arities across premises in the same story — example_id 819-821, `BoughtToEarnProfitFrom` used with both 2 and 3 arguments — a real FOLIO annotation inconsistency, and notably the *exact phenomenon CREST is built to detect*, found in the gold data itself) — previously these fell through to a generic, uninformative "ERROR" bucket.

**Result progression as fixes landed: 70.4% → 74.8% → 81.1% ceiling accuracy (excluding malformed gold FOL), 116/203 (57.1%) including it.** 60/203 (30%) of validation examples have confirmed-malformed gold FOL — notably higher than LINC's ~11% figure for the original release; worth flagging to the supervisor as either a real increase in this dataset version or a broader definition of "malformed" than LINC used.

**All 27 remaining non-malformed mismatches hand-reviewed 2026-07-18 (Tanjamul asked for a full check, not spot-checks).** Every single one traces to an identifiable cause, not an unexplained grounder bug:

- **21 cases: confirmed FOLIO annotation inconsistencies** — the same symbol spelled/cased differently between premise and conclusion (or across premises), so Prover9 correctly treats them as different symbols and correctly fails to connect them. Examples: `roderickStrong` vs `roderickstrong` (289/291), `longVacation` vs `longvacation` (456), `1984` vs `y1984` (905/906), `NaturalLanguageProcessingTask` vs `NaturalLanguageProcessingTasks` (546/547), `SpendTimePlayingWith` vs `SpendTimeplayingWith` (1012/1013), `ProvideTo`/`ets` vs `ProvidesFinancialAidTo`/`eTS` (560/561/562 — a severe case, completely different predicate name *and* arity), `NamedAfter` vs `NameAfter` (440), `PetersPet` vs `PeterSPet` (1349/1350), `HouseholdAppliance` vs `HouseHoldApp` (580), a nonsensical argument-type mix-up (1328/1329), and an unbound free variable typo (`y` used without any governing quantifier, 1244/1245/1247). **This is directly on-topic** — predicate/constant naming inconsistency is the exact phenomenon CREST is built to detect, and here it's turning up inside FOLIO's own gold-standard data, not just in LLM output.
- **4 cases: likely FOLIO annotation gaps or possible gold-label errors** (moderate confidence, based on manual FOL reasoning, not independently re-verified) — 608 and 388 both seem to be missing a premise the reasoning implicitly depends on; 254 seems to assume tom owns exactly one vehicle without stating it. **Example 1414 is the most interesting**: manual derivation (proof by cases over the disjunction in the premises) suggests the conclusion should actually be provable True, matching what our grounder said — meaning FOLIO's own gold label ("False") might itself be the error here, not our grounder. Worth flagging to the supervisor specifically, not just excluding quietly.
- **2 cases (663/665): a real, separate performance limitation in our grounder**, not a data issue — both involve a single premise with a 14-way chained `⊕` (residential college names). Our left-associative XOR expansion blows this up into a combinatorially large formula, and Prover9's search then takes 149s/239s (exceeding the 20s timeout) even for a trivial, unrelated goal that doesn't need that premise at all. **This is a known limitation to fix before scaling to ProofWriter/PrOntoQA or any story with a large XOR chain** — needs a smarter N-way-XOR encoding (e.g. a proper cardinality/exactly-one constraint) instead of naive pairwise left-to-right expansion. Tracked as a TODO, not yet fixed.

**Net honest conclusion:** on this validation split, once malformed gold FOL (60), confirmed/likely annotation inconsistencies (21+4=25), and the known XOR-chain performance limitation (2) are all properly separated out, the grounder produced **zero unexplained wrong answers** — every mismatch has an identified, specific cause. This is a genuinely strong result, but three caveats before treating it as the final Phase 2.1 number: (1) the 21+4 categorization above is Tanjamul's/this session's own manual judgment on a single pass, not independently verified by a second annotator — exactly the kind of judgment call Phase 5's inter-annotator-agreement process exists to validate at scale, so don't treat it as equivalent to human-annotated ground truth yet; (2) the XOR-chain performance issue is unresolved, not just documented — it will recur; (3) example 1414's possible gold-label error should be raised with the supervisor rather than silently resolved in our favor.

**Important distinction clarified 2026-07-18 (don't lose this when reading Phase 3/4 results later):** the malformed/inconsistent *FOL text* found here won't directly recur as noise in the vanilla/CREST/Self-Refine pipelines, since those involve the LLM translating fresh from natural language, not reusing FOLIO's own (sometimes flawed) gold FOL. But the **gold LABELS** (True/False/Uncertain) — the fixed comparison target for every downstream experiment — were themselves derived by applying Prover9 to that same sometimes-flawed gold FOL. Example 1414 is direct evidence that a gold *label*, not just gold FOL text, can be wrong. This means no method (vanilla, Self-Refine, or CREST, however good) can ever measure above roughly (100% − true label error rate) against these labels — that ceiling exists independent of LLM translation quality, and this Phase 2.1 exercise is the closest available estimate of it. Keep this in mind rather than treating any single downstream accuracy number as a clean measure of translation quality alone. Separately, and unaffected by this: the grounder itself is now verified correct on well-formed input — that part matters for real deployment too, since a deployed system has no gold label to fall back on and must rely entirely on the grounder/detector being correct |
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
| 3.3 | **Added 2026-07-24**: repeat the same vanilla measurement (3.1/3.2) on the same subset with a strong/modern proprietary model (e.g. GPT-4o or GPT-4o-mini), not just Llama-3.1-8B | Directly preempts the most likely reviewer objection: "why build a detection framework instead of just using a better model?" If silent-failure prevalence drops to ~0% with a strong model, that's important negative evidence reshaping the paper's framing (see the existing low-prevalence kill gate below). If it persists even at a lower rate, that's strong evidence the phenomenon isn't just a weak-model artifact — directly strengthened by an existing finding: Phase 2.1's ceiling check already found ~25 predicate/naming-inconsistency errors in FOLIO's own *human-written* gold FOL, suggesting this is a difficulty inherent to the NL→FOL task itself, not just an LLM-capability gap | Silent-failure prevalence compared across model capability (weak vs. strong), not just a single fixed model. Using GPT-4o/GPT-4o-mini here for a measurement/comparison experiment is consistent with the earlier "own model everywhere" clarification (Phase 8.2) — that constraint is about the *deployed* pipeline, not every experiment |

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
| Phase 3.3: strong model (GPT-4o/-mini) shows ~0% silent-failure prevalence where Llama shows meaningfully more | Don't ignore this — it means the phenomenon may be a weak-model artifact, not a general problem. Reframe the paper around a narrower, honestly-scoped claim (e.g. "safety layer for resource-constrained/open-weight deployments," not "silent failure is a general LLM problem") rather than overclaiming generality |
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
