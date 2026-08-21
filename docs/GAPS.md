# CREST — Live Gap & Edge Register

**This file exists so nothing hides.** Every open gap, every assumption we
have not verified, every edge we have not checked, and every claim we have
already had to retract — in one place, with a definite "what closes it" for
each. If a gap is not in here, it is not being tracked; if it is in here and
marked OPEN, no downstream claim may quietly assume it is closed.

**Rules for this file (agreed 2026-08-17):**
1. A gap closes only when its stated close-condition is *met and pointed at*
   (a file, a number, a commit) — never because it feels handled.
2. Anything discovered mid-work gets added here immediately, in the same
   session, even if it is inconvenient.
3. Section D (retracted claims) never shrinks. Corrections stay visible.
4. Status vocabulary: **OPEN** / **IN PROGRESS** / **CLOSED** / **ACCEPTED
   LIMITATION** (won't fix, stated in the paper instead).

Last updated: 2026-08-17.

---

## A. Open gaps that block publication

| ID | Gap | Why it blocks | What closes it | Status |
|---|---|---|---|---|
| **G1** | **Only one naturalistic dataset supports the headline claim.** FOLIO alone. ContractNLI was the intended second and cannot serve — its formalization ceiling is 0% (literal) / 60% (charitable), measured in `contractnli_ceiling_probe.py`. | A single-dataset naturalistic result is dismissible as a dataset artifact. This is the paper's biggest weakness and has been since 2026-08-03. | Either (a) a third dataset with a *verifiable* ceiling — SARA leads, since its hand-written Prolog gives a gold formalization by construction; or (b) reframe so the generalization claim does not need a second dataset (see N1 in the plan — the formalizability angle makes ContractNLI's failure itself the evidence). | **OPEN** |
| **G2** | **The detector has no measured precision/recall.** | The paper cannot claim mitigation, or even detection, on an unmeasured component. | Precision/recall on data already in hand. | **PARTLY CLOSED 2026-08-17** — signal 1 (schema/reachability) built and measured: 98.5% / 100% precision, 11.3% coverage (`RESULTS_SNAPSHOT.md` §1c). Still open: signals 2–3 (structural diff, risk combiner), calibration (ECE/Brier), and evaluation against the 72 annotated cases rather than only against solver behaviour. |
| **G3** | **No corrector/repair exists.** Phase 8 (distillation + DPO) unbuilt. | The "repair" half of "detect-and-repair" is currently an assertion. | A working repair on the *repairable* subset, with a ceiling-independent endpoint (reachability restored), not an accuracy claim. | **OPEN** |
| **G4** | **The novelty claim is not yet pinned to one defensible sentence.** | Everything else is measurement in search of a contribution. | A written, one-paragraph claim that survives the "who else has done this" check. | **CLOSED 2026-08-21** - pinned in `RESEARCH_DIRECTION.md` 3.95: diagnosis-conditioned repair with verified acceptance and a non-degradation guarantee, plus four pre-registered falsification gates. Differentiation paragraphs against the near-neighbour papers are still owed (tracked under G5). |
| **G5** | **Related-work recheck not done since 2026-08-03.** Two papers read then; the area moves fast. | "Someone published this meanwhile" is a top rejection cause for exactly this framing. | A fresh search immediately before submission, plus a differentiation paragraph per near-neighbour. | **OPEN** |

---

## B. Unverified assumptions and unchecked edges

These are not failures — they are the things that, if a reviewer poked them,
we could not currently answer. Ordered by how much damage a bad answer does.

| ID | Edge | Damage if wrong | What closes it | Status |
|---|---|---|---|---|
| **E1** | **The ContractNLI ceiling probe is Claude's own hand formalization, n=10.** Both the 0%/60%/100% numbers and the five-blocker taxonomy rest on it. | The entire step-5 interpretation, and the N1 novelty candidate, rest on a single non-independent annotator with a tiny sample. | A human re-formalises the same 10 cases independently, blind to Claude's FOL; agreement reported. Then scale (see the plan's P2). | **OPEN — highest priority** |
| **E2** | **The taxonomy's κ=0.725 came *after* a reconciliation round in which the human revised labels toward a definition Claude had just tightened.** The pre-reconciliation number was κ=0.430. | A reviewer can argue the agreement was manufactured. Both numbers are published in our own docs, which is the right call, but the framing must be airtight. | State both numbers and the full procedure in the paper's methods; ideally add a *fresh* set of cases annotated under the tightened definition with no reconciliation, to show the definition itself now produces agreement. | **OPEN** |
| **E3** | **Prompt v3's demonstrations are FOLIO examples, used unchanged on ProofWriter, PrOntoQA and ContractNLI.** | Cross-dataset comparisons could partly measure demonstration-domain mismatch rather than dataset difficulty — especially on legal text, where it is most severe. | One ablation: a domain-matched few-shot prompt on ContractNLI (demos built from its *train* split), comparing loud-failure and reachability rates. If it barely moves, the confound is dead and the comparison is clean. | **OPEN** — cheap, ~$0.4 |
| **E4** | **Model identity was not pinned.** Runs logged the alias `gpt-4o`, not the dated snapshot; 3 distinct `system_fingerprint`s already appear across our own logs. | The reported frontier-model numbers cannot be attributed to a specific model, and cannot be reproduced after OpenAI moves the alias. | Fixed forward 2026-08-17 (`resolved_model` now logged). For the *existing* runs, state the date range and fingerprint set as an explicit limitation — the information is not recoverable retroactively. | **PARTLY CLOSED** — fixed going forward, historical runs are an **ACCEPTED LIMITATION** |
| **E5** | **ContractNLI pilot is a single seed, single n=100 sample, single prompt.** | A floor effect is robust to this, but any *comparison* drawn from it is not. | Nothing, unless a comparison claim is made from it. Currently we make none — the pre-registered conclusion is "cannot be tested here". Keep it that way. | **ACCEPTED LIMITATION** |
| **E6** | **The blocker-attribution test is a lower bound.** Disjoint vocabulary proves non-derivability; overlap does not prove derivability. The "shares vocabulary" group is unexamined. | The 21/47/36% figure is sound, but the *complement* is not "what CREST can fix" — a reader could easily misread it that way. | Hand-classify a sample (~30) of the overlap group into the five blockers, giving a real split of repairable vs not. | **OPEN** |
| **E7** | **FOLIO's own gold labels contain at least one probable error (example 1414), never raised with the supervisor.** | Small effect on numbers, but it is a known-unreported data issue in a dataset we build claims on. | Raise it explicitly in the next supervisor update; state it in the paper's data-quality section alongside the 30% malformed-gold-FOL finding. | **OPEN** |
| **E8** | **The grounder's N-way XOR expansion blows up** (FOLIO 663/665: 149s/239s against a 20s timeout). Known since 2026-07-18, unfixed. | Recurs on any dataset with long exclusive-or chains; currently absorbed as timeouts, which are scored as `Uncertain` — i.e. as *model* under-determination when it is really *our* limitation. | Proper exactly-one/cardinality encoding instead of naive left-associative pairwise expansion. Also: audit how many current `Uncertain` verdicts are actually timeouts. | **OPEN** — the audit is cheap and should happen before any under-determination number is final |
| **E9** | **ContractNLI excludes the NotMentioned class**, making it binary while FOLIO is 3-way. | Stated in the loader and the pre-registration, so not hidden — but it makes the two datasets structurally different in a way that must never be silently compared. | Nothing, if it stays stated. Revisit only if ContractNLI is promoted beyond a case study. | **ACCEPTED LIMITATION** |
| **E10** | **Determinism asymmetry**: Llama is genuinely greedy-deterministic; OpenAI `seed` is best-effort. | Weakens "deterministic pipeline" claims for the API arms. | One repeat run of a small subset on an API model, reporting the observed disagreement rate — turns a caveat into a measured number. | **OPEN** — cheap (~$0.1) |
| **E11** | **Logic-LM's exact published splits** were the stated plan for ProofWriter/PrOntoQA (Phase 2.2). Never re-verified that the loaded splits match. | If they differ, direct comparability with Logic-LM's reported numbers is lost — one of the reasons those datasets were chosen. | Check the loaders against Logic-LM's published sample files; record the verdict either way. | **OPEN** |
| **E12** | **Pricing table in `openai_harness.py` is unverified** and cost figures appear in the docs. | Trivial, but a wrong cost figure in a thesis is an easy embarrassment. | Check against OpenAI's current pricing page before any cost number is quoted. | **OPEN** — trivial |

---

## C. Closed, with evidence

Kept visible so the register shows progress, not only debt.

| ID | Item | Evidence |
|---|---|---|
| C1 | Grounder is correct on well-formed input — every one of 27 non-malformed mismatches traced to an identified cause, zero unexplained | Phase 2.1, `ceiling_check_validation.json` |
| C2 | Self-Refine does not close the gap — falsified across 3 datasets × 3 models, significantly harmful on two cells | `RESULTS_SNAPSHOT.md` §2 |
| C3 | Generation confidence fails as a detector exactly where the problem persists (AUROC 0.87 synthetic/weak → 0.49 on FOLIO × gpt-4o-mini) | `RESULTS_SNAPSHOT.md` §3 |
| C4 | Capability × language-type interaction measured, full splits, paired stats | `RESULTS_SNAPSHOT.md` §1 |
| C5 | Taxonomy validated at κ=0.725 (human vs Claude, post-reconciliation) — see E2 for the caveat that travels with it | `reconciliation_round1.md` |
| C6 | ContractNLI feasibility, ceiling, and pilot — all three arms run | `RESULTS_SNAPSHOT.md` §1b |
| C7 | Silent failure is overwhelmingly a *translation* failure, not a solver failure — 30 of 35 "looks faithful" verdicts collapsed under derivation checking; only C003 survives | `faithful_bucket_verification.md`, `needs_scrutiny_bucket_verification.md` |

---

## D. Retracted or corrected claims — never delete a row

| Date | Claim as originally stated | Correction | Trigger |
|---|---|---|---|
| 2026-07-24 | `Contradiction` outcomes are a promising gold-label-free detector signal | Retracted — an artefact of the weak zero-shot prompt; dropped to ~0 under few-shot | Prompt v2→v3 comparison |
| 2026-07-24 | "Silent failure is a general danger in neuro-symbolic pipelines" | Narrowed — falsified in its strong form by gpt-4o; the kill gate fired and the framing was required to narrow | Phase 3.3 |
| 2026-08-03 | Self-Refine widens the gap | Withdrawn on re-analysis | Re-analysis |
| 2026-08-17 | C065/C066/C068/C069 are translation-faithful | All four are real failures; only C003 survives | Derivation re-checks |
| 2026-08-17 | "The ContractNLI ceiling gate fires under both defensible conventions" | Only the literal arm fires decisively (CI [0%, 31%]). The charitable arm's 6/10 cannot reject a 70% ceiling (p=0.35) | Computing the intervals |
| 2026-08-17 | ContractNLI's failures are "near-misses" — the same relation spelled two ways | Only 1 of 147 unreachable goals is a normalisation-detectable variant; 146 are semantic divergence. The phenomenon is vocabulary divergence, but it is meaning-level, so string normalisation repairs ~0.7% of it | Building the detector and measuring it |
| 2026-08-17 | The reachability check is SOUND (100%) | 98.5% on the 130 solver-reached flags. Inconsistent premise sets are a real exception: from a contradiction any goal follows | `schema_detector_eval.py` |

---

## How this file gets used

- Read section A + B at the start of any work session. If a task does not
  close a row here, ask why it is being done.
- Any new finding gets a row before the session ends, not "later".
- The paper's limitations section is written *from* B and D. Nothing in
  B or D may be omitted there.
