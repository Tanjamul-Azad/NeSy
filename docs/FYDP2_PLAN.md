# FYDP-2 — The Plan (authoritative, set 2026-08-27)

**This is the single plan of record for FYDP-2.** It supersedes every earlier
plan fragment: `RESEARCH_DIRECTION.md` §2 (the 2026-08-03 seven-step plan), the
"Sequential plan, updated 2026-08-17" section, §3.9 (P1–P5), and §3.96's
programme sketch (P-A–P-E). Those sections remain in the record as history —
they are **not** to be followed. If this document and any of them disagree,
this one wins.

**Exit condition:** `docs/DEFINITION_OF_DONE.md` (ten conditions).
**Operating rules:** `docs/RESEARCH_STANDARDS.md`.
**Live obligations:** `docs/GAPS.md` (5 gaps + 22 edges; every one is assigned
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
| Rewrite §3.95/§3.96 to remove the four flagged claims rather than footnote them | E15/E16/E17 |
| **Dated G5 literature search** — required *before* novelty wording is re-frozen | **G5** (this round) |
| Re-freeze the contribution wording, provisionally, only after that search | **G4** |

**Dependency, made explicit:** `S0 definitions freeze → dated G5 search → G4
provisional novelty freeze`. Until that search exists, **"first", "no prior
work" and "the problem nobody has formulated" may not appear anywhere** — and
our own related-work pass records one of the two near-neighbour papers as read
at *abstract* level only, which is not verification.

**Exit gate:** §3.95/§3.96 carry no claim flagged as under correction;
`docs/GAPS.md` shows E15/E16/E17/E19 CLOSED; a dated G5 search exists; novelty
wording is marked provisional. **Framework v0.**

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
definitions).

**G1 — conditionally, and the condition matters.** The earlier wording said
this stage closes G1 by producing the resource rather than by finding another
dataset. That was too fast. **S3 closes G1 only if it supplies a second
defensible naturalistic evaluation source under the frozen formalization
contract.** If the naturalistic evidence ends up resting essentially on FOLIO,
the external-validity problem remains and **G1 is narrowed and accepted as a
stated limitation, not closed** — and note that ContractNLI's own formalization
compatibility is itself under test in S1, so it cannot be assumed to supply
that second source. A methodological resource is a real contribution; it does
not substitute for dataset diversity.

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

**Exit gate — rewritten 2026-08-27; the old gate was inherited, not designed.**
The previous gate ("lift > 1.0 with CI excluding 1.0, ~≥70% attribution
precision") was carried over mechanically from the *binary silent-failure
detector*. Lift was introduced to replace the broken coverage gate for a
one-dimensional signal; it does not define adequacy for a **multi-axis**
attributor. The gate is now stated per-axis plus on the operational decision:

| Quantity | Gate |
|---|---|
| Per-axis `F`, `T`, `S` | precision/recall reported **separately per axis**, each against the S3 human labels |
| **`R = (F=1 ∧ T=0)`** — the operational repair decision | **primary gate**: PR-AUC, plus precision/recall at the deployed operating point |
| Calibration | ECE/Brier on the `R` score |
| Lift | **secondary diagnostic only** — retained for comparability with the detector results, never as the central gate |

**Two measurement subtleties that must be built into the evaluation, not
discovered during it:**

1. **`R` is defined over true `F`/`T` but computed over estimated `F̂`/`T̂`.**
   Errors on the two axes compound. The evaluation therefore reports both the
   achieved `R` decision quality **and an oracle-`R` upper bound** computed
   from the true axes, so the loss attributable to attribution error is
   separable from the loss attributable to repair. Without that split, a weak
   repair and a weak attributor are indistinguishable.
2. **`F` may be `uncertain / not-assessable`.** `R` is then undefined. The
   policy for that case is **preregistered before labels are collected** —
   default: conservative, do not repair — and reported as a rate, since a
   method that abstains on half its inputs is a different product from one
   that abstains on 5%.

**If the primary gate fails,** the paper reframes around attribution quality
and S5 does not start.

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
| Acceptance/verification step |
| Baselines: repair-all, and Self-Refine **at parity** (our repair model, conditioning removed) |

**Endpoint — three levels, corrected 2026-08-27.** The earlier wording
("derivability restored, never raw accuracy") was overly exclusive and
exploitable: a repair that injects wrong semantics can accidentally make the
desired verdict derivable and would have scored as a success. Evaluation
therefore reports all three:

| Level | Measures | Why it alone is insufficient |
|---|---|---|
| **1. Targeted repair success** | was the diagnosed defect actually fixed; derivability restored | gameable by wrong-but-lucky repairs |
| **2. Semantic fidelity of the repaired representation** | does the repaired formula still faithfully represent the source | *only where assessable* — see the resource dependency below |
| **3. End-to-end outcome** | task accuracy **and** regression on previously-correct cases | ceiling-capped on some datasets, so never reported alone |

"Not raw accuracy alone" is right; "never report accuracy" was wrong. **A
framework contribution has to show downstream benefit**, so level 3 is reported
with its ceiling stated, not omitted.

**Resource dependency, named now rather than discovered in S5:** level 2's
"where assessable" is load-bearing. Automated fidelity signals have already
been measured to fail on naturalistic text (structural divergence, lift ≈1.0),
so fidelity assessment here is **human work that is not currently in S3's
annotation budget**. Either S3's scope grows to cover repaired-formula fidelity
review, or level 2 is reported only on a declared subsample. Decide in S3, not
in S5.

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

## The writing track — corrected 2026-08-27

**The earlier version of this section said "immediately write the corresponding
paper subsection" after every gate. That conflicts with the agreed workflow and
is withdrawn.** Writing paper prose against claims that are still moving means
rewriting it each time a claim is corrected — and this project corrects claims
often, by design.

**What accumulates from S0 onward (canonical, machine-checkable):**

| Artefact | Contents | Updated |
|---|---|---|
| `docs/CLAIMS_EVIDENCE.md` | every claim we intend to make, with the exact file/number/commit that supports it, and its current status (supported / provisional / retracted) | after every gate |
| Related-work matrix | each near-neighbour paper: what it claims, what it measures, how we differ, **and whether we read the full paper or only the abstract** | at every G5 search |
| Tables/figures requirements | which table each claim needs, generated by `make_tables.py` | after every gate |
| `docs/GAPS.md` sections B and D | the limitations section, written continuously | continuously |
| Thesis `.md` sections | periodic sync from the canonical evidence | per stage |

**Paper prose begins only when the contribution is stable** — realistically
after S4's gate, since a failed S4 reframes the paper around attribution
quality and would invalidate prose written earlier.

**Thesis is not deferred**, because thesis chapters can absorb evolution
(including retracted claims, which are part of its scientific narrative) in a
way a fixed-length paper cannot.

| Stage | What becomes canonical evidence |
|---|---|
| S0 | problem formulation, F/T/S definitions, framework v0 spec |
| S1 | annotation protocol; constructive-recoverability results |
| S2 | dataset descriptions; measurement methodology; two detector negative results |
| S3 | resource description; per-axis reliability |
| S4 | attribution results — **paper prose may start here** |
| S5 | repair results at all three endpoint levels; ablations |
| S6 | full results tables; error analysis |

**G5 is recurring, not a stage** — re-run at the start of every stage and again
before submission, each time with a date. No novelty word survives without one.

All tables come from `make_tables.py`. A number that cannot be regenerated from
the repo does not enter either document.

---

## Every tracked item has a home

| Stage | Items |
|---|---|
| S0 | E15, E16, E17 *(closed 2026-08-27)*, E19, G4, G5 *(this round)* |
| S1 | E1, E18 (H2) |
| S2 | E3, E4, E6, E7, E8, E10, E11, E12 |
| S3 | E2, E18, E21, E22, G1 *(conditional)* |
| S4 | G2, E20 |
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
