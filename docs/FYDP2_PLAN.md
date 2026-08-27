# FYDP-2 — The Plan (authoritative, set 2026-08-27)

**This is the single plan of record for FYDP-2.** It supersedes every earlier
plan fragment: `RESEARCH_DIRECTION.md` §2 (the 2026-08-03 seven-step plan), the
"Sequential plan, updated 2026-08-17" section, §3.9 (P1–P5), and §3.96's
programme sketch (P-A–P-E). Those sections remain in the record as history —
they are **not** to be followed. If this document and any of them disagree,
this one wins.

**Exit condition:** `docs/DEFINITION_OF_DONE.md` (ten conditions).
**Operating rules:** `docs/RESEARCH_STANDARDS.md`.
**Live obligations:** `docs/GAPS.md` (5 gaps + 19 edges; every one is assigned
to a stage below — nothing is left unplaced).

---

## The shape of it

Seven stages, strictly gated: **no stage starts before the previous stage's
exit gate is met and pointed at.** The writing track runs in parallel from
Stage 0, not at the end.

```
S0 Formulation freeze ──► S1 Construct validation ──► S2 Measurement hygiene
                                                            │
                                    ┌───────────────────────┘
                                    ▼
      S3 Resource build ──► S4 Attributor ──► S5 Selective repair ──► S6 Scale & ablate
                                                                              │
                                                     (only if core survives)  ▼
                                                                     S7 Cross-formalism
```

Framework maturation maps onto this: **v0** = end of S0, **v1** = end of S4,
**v2** = end of S5.

---

## Stage 0 — Formulation freeze  *(now; no data collection)*

Nothing is measured until the things being measured are defined. Four of our
definitions are currently wrong or under-specified, and all four were caught by
review rather than by us.

| Work | Closes |
|---|---|
| Rewrite the "guarantee" language: derive a formal property, or rename to empirical non-degradation with a CI | **E15** |
| Split pre-solver *risk prediction* from post-execution *causal diagnosis*; decide whether the pre-solver constraint has any motivation at all | **E16** |
| Fix F/T/S as independent axes with a stated repair trigger (`T=0` fires only when `F=1`) | **E17** |
| Freeze `Formalizable(x; Φ, C)`; every figure indexed to a named contract | **E19** (done: `PREREG_E1_formalizability.md`) |
| Rewrite §3.95/§3.96 to remove the four flagged claims rather than footnote them | G4 re-freeze |

**Exit gate:** §3.95 and §3.96 contain no claim currently flagged as under
correction, and `docs/GAPS.md` shows E15/E16/E17/E19 CLOSED. **Framework v0.**

---

## Stage 1 — Construct validation  *(the E1 study; needs 5 external people)*

Tests whether the frozen definition is usable by someone without our priors.
Fully preregistered in `docs/PREREG_E1_formalizability.md`.

| Step | Work |
|---|---|
| 1a | Recruit exactly 3 formalizers + 2 fidelity reviewers, all external |
| 1b | Contract pilot on the 3 drawn train cases (`573_nda-17`, `614_nda-13`, `388_nda-3`); comprehension quiz at 100% |
| 1c | If ambiguity: contract v2 → **fresh** draw → re-pilot. Audit-10 never used for tuning |
| 1d | Blind audit on the 10 cases, both contracts, A/B/C/D outcomes |
| 1e | Report `r_case@3`, `r_individual`, raw agreement **before** reconciliation |

**Closes:** E1, and the H2 half of E18.

**Exit gate (either outcome proceeds, but to different places):**
- Contract applicable + recoverability low under `C_L` → the formalizability
  finding replicates; continue to S2.
- **Contract not reliably applicable** → S3 is blocked. Return to S0 and repair
  the definition. *Scaling annotation past an unreliable construct is
  explicitly forbidden* (DoD condition 3).
- Recoverability ≥70% under `C_L` → the ContractNLI barrier hypothesis is
  narrowed or retracted (preregistered).

---

## Stage 2 — Measurement hygiene  *(cheap; mostly no new model runs)*

Every number that survives into the paper gets audited first. Doing this before
S3–S5 means results are computed once, not recomputed after a contamination
discovery.

| Work | Closes | Cost |
|---|---|---|
| Timeout audit; fix N-way XOR encoding; recompute **affected arms only** (ProofWriter × Llama) | **E8** | free |
| Domain-matched few-shot ablation on ContractNLI | **E3** | ~$0.4 |
| Hand-classify ~30 overlap-group cases into blockers | **E6** | free |
| Determinism repeat on an API model, report the disagreement rate | **E10** | ~$0.1 |
| Verify ProofWriter/PrOntoQA splits against Logic-LM's published samples | **E11** | free |
| Verify the pricing table before any cost figure is quoted | **E12** | free |
| Raise FOLIO's example-1414 gold-label issue with the supervisor | **E7** | free |
| State the model-snapshot limitation for historical runs | **E4** | free |

**Exit gate:** every row above CLOSED or ACCEPTED, and `RESULTS_SNAPSHOT.md`
regenerated from `make_tables.py`.

---

## Stage 3 — Resource build  *(the moat; the biggest execution risk)*

| Work |
|---|
| Recruitment + scheduling plan **before** annotation starts (DoD addition B) |
| Annotation guidelines for the F/T/S axes, per-axis, multi-label |
| 300–500+ examples across multiple datasets |
| Per-axis raw agreement reported **before** any reconciliation |

**Closes:** E18 (fully), E2 (fresh un-reconciled cases under the tightened
definitions), and **G1** — not by finding another dataset, but by producing the
resource that explains why naive single-dataset evaluation was unsound.

**Exit gate:** raw per-axis κ ≥ 0.60. **Below that, annotation stops and the
schema is redesigned** — the target is not met by annotating more.

---

## Stage 4 — Attributor  *(framework v1)*

| Work |
|---|
| Attribution model over F/T/S, evaluated against the S3 human labels |
| Calibration (ECE/Brier) |
| Attribution baselines, including an oracle-attribution upper bound |
| Evaluate against the 72 annotated FOLIO cases, not only solver behaviour |

**Closes:** **G2** fully (signals 1–2 measured; combiner + calibration
outstanding).

**Exit gate (the corrected one — coverage alone gates nothing):** lift > 1.0
with a 95% CI whose lower bound excludes 1.0, at a practically useful precision
(~≥70% on the attribution decision). Below that, the paper reframes around
detection quality and S5 does not start.

**Known constraint carried in from measurement:** both cheap deterministic
signals failed on naturalistic text (reachability 11.3% coverage; structural
divergence lift ≈1.0). A learned semantic component is an empirical
requirement here, not a design preference.

---

## Stage 5 — Selective repair  *(framework v2)*

| Work |
|---|
| Resolve compute budget **before** starting (**E13**) |
| Corrector size as an **ablation variable** (1B/3B/8B), not a hardware-driven choice |
| Distillation warm-start → DPO on `T=0 ∧ F=1` cases only |
| Acceptance/verification step; endpoint is derivability restored, never raw accuracy |
| Baselines: repair-all, and Self-Refine **at parity** (our repair model, conditioning removed) |

**Closes:** **G3**, and the empirical half of E15.

**Exit gate — three ways this can fail, all preregistered:**
1. Diagnosis-conditioned ≈ repair-all → selectivity is decoration; report it.
2. Repair corrupts previously-correct cases → non-degradation narrowed or
   retracted, never relabelled.
3. Parity baseline matches us → we have a repair model, not a framework.

---

## Stage 6 — Scale and ablate

Multi-seed everywhere stochasticity exists; additional open models (Qwen 2.5,
Mistral — free on Kaggle); full clustered statistics; per-component ablations;
error analysis. **Closes E5.** Scale is targeted where intervals are too wide
to support a claim — never for the size of the number.

---

## Stage 7 — Cross-formalism  *(conditional; the ceiling-raiser)*

SMT via Z3, or LTL. **Starts only if S4 and S5 both pass.** If attribution
precision collapses on a second formalism, that is reported as a scoped result,
not stretched. **This is the first thing dropped under the descope rule.**

---

## The writing track — parallel, from now

Per DoD: `preregister → run → analyze → update claim/retraction → immediately
write the corresponding paper and thesis subsection`.

| Stage | What becomes writable |
|---|---|
| S0 | Problem formulation, definitions, framework v0 spec |
| S1 | Annotation protocol; formalizability study |
| S2 | Datasets; measurement methodology; the two detector negative results |
| S3 | Resource description; reliability reporting |
| S4 | Attribution results |
| S5 | Repair results, ablations |
| S6 | Full results tables, error analysis |
| any | Limitations — generated from `GAPS.md` sections B and D |

**G5 (literature recheck) is recurring, not a stage** — re-run at the start of
each stage and again before submission. No "first"/"novel"/"no prior work"
without a dated search behind it.

All tables come from `make_tables.py`. A number that cannot be regenerated from
the repo does not enter either document.

---

## Every tracked item has a home

| Stage | Items |
|---|---|
| S0 | E15, E16, E17, E19, G4 |
| S1 | E1, E18 (H2) |
| S2 | E3, E4, E6, E7, E8, E10, E11, E12 |
| S3 | E2, E18, G1 |
| S4 | G2 |
| S5 | E13, G3 |
| S6 | E5 |
| recurring | G5 |
| accepted limitations, stated not fixed | E9 (binary vs 3-way), E5/E4 residue |

---

## What this plan refuses to do

- Start S3's large annotation before S1 says the construct is usable.
- Start S5 before S4's lift gate passes.
- Add datasets, models or formalisms while the core mechanism is unproven.
- Report any figure that `make_tables.py` cannot regenerate.
- Keep the word "guarantee", or any unindexed formalizability number, in a
  draft while E15/E19 are open.

**Immediate next action:** Stage 0 — rewrite §3.95/§3.96 to close E15/E16/E17,
which is the only thing standing between us and framework v0.
