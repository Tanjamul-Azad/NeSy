# Related Work Matrix — G5 Pass A (2026-08-27; extended 2026-08-30)

**Update 2026-08-30.** The team handbook (`CREST_Research_Learning_Book_v2_Bangla.docx`)
surfaced four further papers our own Pass A missed. Each was **re-verified at source**
before entry here rather than trusted from the handbook — the same rule the handbook
itself states. One of them (FormalRx, ICML 2026) threatens our annotation work more
than anything in the original pass.

**Verification discipline (RESEARCH_STANDARDS rule 2).** Every row records how
the claim about that paper was verified. A paper reported by a collaborator —
human or model — is **not** verified until its existence and content are checked
against the source. Nothing in this matrix may drive a contribution change while
marked UNVERIFIED.

| Status | Meaning |
|---|---|
| **VERIFIED-FULL** | full text read |
| **VERIFIED-ABS** | existence and abstract confirmed at source; full text NOT read |
| **UNVERIFIED** | reported to us, existence not confirmed |
| **NOT-FOUND** | searched, no matching academic work located |

---

## Tier 0 — threats to the contribution formulation itself

### T0-1. Faithful Autoformalization via Roundtrip Verification and Repair
**[arXiv:2604.25031](https://arxiv.org/abs/2604.25031)** · Amrollahi, Lopez,
Barrett · submitted 2026-04-27, rev. 2026-05-09 · **VERIFIED-ABS**

| | |
|---|---|
| **Problem** | Is an LLM formalization faithful, *without ground-truth annotations*? |
| **Method** | Roundtrip: formalize → back-translate to NL → re-formalize → check logical equivalence with a formal tool. Agreement = evidence of faithfulness. |
| **Diagnosis** | Disagreement triggers **stage-level diagnosis localizing the error to a specific translation step** (formalize / back-translate / re-formalize). |
| **Repair** | **Scoped repair operator** targeting the diagnosed step. |
| **Domain** | Statutory legal text — Texas Transportation Code, Texas Parks & Wildlife Code. Claude Opus 4.6, GPT-5.2. |
| **Stated limitation** | "effectiveness contingent on the reliability of the diagnosis function". |

**What this kills for us:** *"diagnosis-guided scoped repair for autoformalization"*
as a novelty claim. They do it, they claim it, they publish it, and they do it
**in the legal domain** — which also pressures our ContractNLI framing on top of
Know Your Limits.

**What appears to remain (abstract-level only, must be confirmed full-text):**
their diagnosis answers *"which stage of my pipeline drifted?"* Per the
abstract there is **no** notion of (a) whether a faithful, task-sufficient
formalization exists to repair *toward*, (b) a decision **not** to repair
because repair cannot help, or (c) solver/execution failure as a separate
category. **This is the load-bearing distinction for our F/T/S formulation and
it currently rests on an abstract. Full-text read is mandatory before any
differentiation paragraph is written.**

### T0-2. "SymDiag (KDD 2026)" — **NOT-FOUND**

Reported to us as a Tier-0 threat: structured failure diagnosis separating
TranslationError vs ReasoningError, diagnosis-guided repair, human-audited
diagnostic dataset. **Four searches returned only the Symantec Diagnostic Tool**
(commercial antivirus utility). No academic work located.

**This does not mean it does not exist** — it may be too recent to index, or
the title may differ. But per rule 2 it **cannot drive a contribution change
until a source is produced.** *Action: whoever reported it supplies a DOI,
arXiv ID, or proceedings link.* If it is real, it is likely the single largest
threat on this list, since TranslationError-vs-ReasoningError is adjacent to
our `T` vs `S` split.

### T0-3. FormalRx: Rectify and eXamine Semantic Failures in Autoformalization ⚠️ **NEW, ICML 2026**
**[arXiv:2607.04655](https://arxiv.org/abs/2607.04655)** · Haocheng Wang, Baiyu
Huang, Yingjia Wan, Xiao Zhu, Xiaoyang Liu, Yinya Huang, Zhijiang Guo ·
**accepted ICML 2026** · **VERIFIED-ABS** (2026-08-30)

Surfaced by the team handbook, not by our own Pass A. Verified at source.

| | |
|---|---|
| **Taxonomy** | "SCI Error Taxonomy", hierarchical, **28 distinct categories** of autoformalization error |
| **Capabilities** | alignment **verdict**, error **categorization**, error **localization**, **correction** |
| **Training data** | **56,287** NL-FL pairs with fine-grained diagnostic annotations |
| **Results** | FormalRx-8B: F1 0.88 (verdict), 0.71 (categorization); accuracy 0.75 (localization), 0.73 (correction) |

**This is the most serious threat on the list, and larger than T0-1 for our
annotation work.** Our 9-category mechanism taxonomy validated at kappa=0.725 on
72 cases now sits in space occupied by a 28-category taxonomy with 56k
annotated pairs, a trained diagnostic model, and an ICML acceptance. **"Our
contribution is a fine-grained taxonomy of NL-to-FOL translation errors" is
dead.** What is not obviously occupied: their unit of diagnosis is the
translation itself (is this formalization aligned, where is it wrong, fix it) —
per abstract there is no task-level question of whether a faithful
formalization exists to repair toward, and no decision to withhold repair.
**Full-text read required before relying on that distinction.**

### T1-5. LeanMarathon — long-horizon Lean autoformalization
**[arXiv:2606.05400](https://arxiv.org/abs/2606.05400)** · Yuanhe Zhang, Yuekai
Sun, Taiji Suzuki, Jason D. Lee, Fanghui Liu · **VERIFIED-ABS** (2026-08-30)

Evolving-blueprint architecture, four agents, adversarial fidelity review, then
parallel proof discharge; 258 lemmas/theorems formalized across Erdos-problem
papers with no `sorry`. Failure modes named in the abstract: "statements drift,
dependencies tangle, context decays, and local repairs corrupt distant work."

**Care needed.** The handbook describes this as distinguishing *blueprint drift
from source gaps*, which would threaten our F-vs-T separation. **The abstract
does not say that in those terms.** Treat the threat as plausible but
**unconfirmed until full text is read** — this is exactly the kind of
second-hand characterisation our own rules say not to act on.

### T1-6. From Errors to Proofs: Minimal-Core-Guided Repair
**[arXiv:2608.14771](https://arxiv.org/abs/2608.14771)** · Dipankar Sarkar ·
2026-08-14 · **VERIFIED-ABS** (2026-08-30)

Extracts a **minimal unsatisfiable core** over the model's own constraints to
localize translation faults and guide repair; reports solution fabrication
falling from 79% to 7%. Adjacent to our `S`-axis evidence: it uses solver
output as diagnostic signal, which is the same move we make for `S`.

### T1-7. Agentic Requirement Formalization / VERIMED — **REPORTED, NOT YET VERIFIED BY US**
[arXiv:2604.18228], [arXiv:2605.13817] — reported in the handbook as covering
formalism-compatibility filtering before translation, and ambiguity /
underspecification auditing of NL requirements with SMT evidence. **Not checked
at source in this pass.** If accurate, the second is close to our `F` axis in a
different vocabulary and must be read in Pass B.

### Cross-cutting observation (not in the handbook)

**Daneshvar Amrollahi is first author of T0-1 (arXiv:2604.25031) and third
author of T1-4 "Know Your Limits" (arXiv:2606.16118)** — verified author lists
2026-08-30. The same group is working legal-domain autoformalization
faithfulness from two directions: pipeline honesty, and roundtrip repair. This
is not a coincidence to note in passing; it is an active, well-resourced group
occupying our exact territory, and Pass B should track their subsequent output
specifically.

---

## Tier 1 — threats to specific findings

### T1-1. Fixing FOLIO and MALLS ⚠️ **FOUND BY OUR OWN SEARCH, NOT ON THE HANDED LIST**
**[arXiv:2606.02837](https://arxiv.org/abs/2606.02837)** · Brunello, Curaba,
Geatti, Mignani, Montanari, Saccomanno · submitted 2026-06-01 · **VERIFIED-ABS**

| Finding | Their number |
|---|---|
| FOLIO items with **incorrect FOL formalizations** | **39%** |
| FOLIO items with ambiguous NL sentences | 16.4% |
| FOLIO items with **wrong NLI labels** | 8.4% |
| MALLS incorrect FOL | 36% |

They **release corrected ground truths**, and report **+9 to +22 pp** accuracy
gains for three SOTA LLMs when evaluated against corrected labels.

**Impact on us — two things, one bad and one actionable:**

1. **Our FOLIO data-quality finding is superseded.** Our Phase 2.1 result
   ("~30% of FOLIO validation gold FOL is malformed") is now convergent
   evidence for someone else's published, systematic, corrected-resource
   contribution. It cannot be presented as our finding. It remains usable as
   independent corroboration and as motivation for our ceiling methodology.
2. **Every FOLIO number we hold uses the ORIGINAL labels.** A reviewer will ask
   why we did not use the corrected release. Our strict filter was our
   workaround for exactly this noise; theirs is a public resource that
   supersedes it. **Action: re-run the FOLIO arms against the corrected ground
   truth and report both.** This strengthens rather than weakens us — it
   removes the gold-noise confound from our capability×dataset result.

Per the abstract they do **not** address unformalizable/under-specified items
as distinct from mislabeled ones, so the `F` axis is not directly hit.

### T1-2. ReForm: Reflective Autoformalization
**[arXiv:2510.24592](https://arxiv.org/pdf/2510.24592)** · **VERIFIED-ABS**

Semantic-consistency evaluation integrated into generation, iterative
self-correction, trained with Prospective Bounded Sequence Optimization.
ConsistencyCheck: 859 expert-annotated items. Reports **16.4% of miniF2F and
38.5% of ProofNet human-written formal statements contain semantic errors.**

**Threat:** moderate. Domain is **mathematical theorem formalization (Lean,
miniF2F/ProofNet)**, not NL→FOL entailment. But "semantic self-validation +
iterative correction" overlaps our repair loop, and their gold-quality finding
parallels ours in a different corpus.

### T1-3. Decompose, Structure, and Repair (DSR)
**[arXiv:2604.19000](https://arxiv.org/abs/2604.19000)** · **VERIFIED-ABS**

Operator-tree decomposition to "precisely localize and repair errors via
sub-tree refinement". PRIME benchmark, 156 theorems, Lean 4.

**Note:** the handed list named this *"Decompose-and-Formalise"*. No paper of
that title was found; DSR (and possibly DRIFT,
[arXiv:2510.10815](https://arxiv.org/pdf/2510.10815)) is the likely referent.
**Title corrected here rather than propagated.** Domain is again theorem
formalization, not NLI.

### T1-4. Know Your Limits (legal autoformalization)
**[arXiv:2606.16118](https://arxiv.org/html/2606.16118v1)** · **VERIFIED-FULL**
(read 2026-08-03)

Already in our record. Re-annotated ContractNLI under strict formal entailment;
71/400 Entailment→Neutral, 18/400 Contradiction→Neutral. Their failure mode is
*scope laundering* (the LLM reports a solver-consistent answer without the
solver having actually run) — a pipeline-honesty failure, distinct from our
translation-fidelity failure.

**Combined with T0-1, the "legal text resists formalization" observation is now
occupied by at least two groups.** Our angle must be the operationalized,
human-validated, contract-relative construct — not the observation itself.

---

## Tier 2 — reported but unverified

Listed for completeness; **none may be cited or used to narrow our claims until
verified at source.**

| Reported as | Status |
|---|---|
| PrefRAG (ACL Findings 2026) — syntactic/semantic error detection and repair for autoformalization, FOLIO | **UNVERIFIED** |
| NL2Logic (EACL Findings 2026) — semantic correctness + solver executability, FOLIO/ProofWriter | **UNVERIFIED** |
| LogicLLaMA / MALLS (ACL 2024) — NL→FOL error analysis and correction model | **UNVERIFIED** here (widely known, but not checked in this pass) |
| Do LLMs Really Struggle at NL-FOL Translation? ([arXiv:2511.11816](https://arxiv.org/pdf/2511.11816)) | **VERIFIED-ABS** — our own record notes it was read at *abstract level only*; full read still owed |

---

## Claim-by-claim verdict (Pass A)

| Our candidate claim | Closest verified prior work | Verdict |
|---|---|---|
| Diagnosis-guided **selective repair** for autoformalization | T0-1 (does exactly this, incl. legal domain) | **KILL** — cannot be our novelty |
| **Fine-grained taxonomy of NL→FOL translation errors** (our 9 categories, κ=0.725, 72 cases) | **T0-3 FormalRx** — 28 categories, 56k annotated pairs, trained model, ICML 2026 | **KILL** — added 2026-08-30 |
| Using solver output as diagnostic evidence for the `S` axis | T1-6 (minimal unsat cores guide repair) | **NARROW** — the move is not ours; the axis framing may survive |
| **FOLIO gold FOL is ~30% malformed** as our data-quality contribution | T1-1 (39%, systematic, corrected release) | **KILL** — demote to corroboration |
| **Legal text resists formalization** | T0-1 + T1-4 | **NARROW** — the observation is occupied; only an operationalized construct survives |
| Semantic-consistency checking + iterative correction | T1-2 | **KILL** as novelty |
| Error localization within a translation pipeline | T0-1, T1-3 | **KILL** as novelty |
| **`F` as a contract-relative construct** — does a faithful, task-sufficient formalization *exist to repair toward*, with `no construction found ≠ impossible` | none found in Pass A | **KEEP, PROVISIONAL** |
| **`F`/`T`/`S` as independent non-exclusive axes**, with `F=0 ∧ T=0` expressible | none found in Pass A | **KEEP, PROVISIONAL** |
| **`R = (F=1 ∧ T=0)`** — deciding *not* to repair because repair cannot recover the task | none found in Pass A (T0-1 abstract shows no such decision) | **KEEP, PROVISIONAL — the strongest remaining candidate** |
| Solver adequacy `S` as a diagnostic axis alongside translation | none found in Pass A; T0-2 would threaten this if real | **KEEP, PROVISIONAL** |

**"Provisional" is load-bearing.** Every KEEP rests on abstract-level reading
plus absence-of-evidence in one search pass. Absence of evidence in one pass is
weak evidence of absence, and **G4 does not freeze on it.**

---

## What Pass A did not do — required before G4

1. **Full text of T0-1**, specifically: do they anywhere ask whether a correct
   formalization exists, or decline to repair? This single question decides
   whether our strongest remaining claim survives.
2. **A source for T0-2**, or its removal from consideration.
3. **Pass B — adversarial search**, deliberately hunting our own remaining
   claims: *task formalizability*, *specification vs translation vs solver
   failure*, *repairability attribution*, *unformalizable input detection*,
   *contract-relative formalization*, *root-cause-based selective repair* —
   and **adjacent literatures we have not touched: formal methods,
   software fault localization, program repair (where "is this bug fixable"
   and "fault localization vs repair" are long-standing distinctions).**
   Our claim may already exist there under different vocabulary.
4. Verification of the Tier-2 rows.

**Until 1–4 are done, no "first", "novel", or "no prior work" appears anywhere,
and G4 stays open.**
