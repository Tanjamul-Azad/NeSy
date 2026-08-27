# CREST — Multi-Dataset Results Snapshot

**Saved 2026-07-27.** All numbers from committed runs in `crest/experiments/logs/`.
Config: whole-story few-shot prompt (v3), greedy, seed 42, Prover9 grounder.
Stats: story-clustered bootstrap 95% CIs; McNemar exact for paired tests.

Total API spend to date ≈ $27 of the $50 credit.

---

## 1. Capability × Dataset — vanilla silent-failure prevalence

Gradeable = non-loud examples. `wrong_dir` = confidently wrong; `under_det` =
gold True/False but predicted Uncertain (translation lost content).

| dataset | model | n | accuracy | silent | wrong_dir | under_det |
|---|---|---|---|---|---|---|
| folio | Llama-3.1-8B | 171 | 60% [52,67] | **40%** [33,48] | 7% [3,12] | 33% [26,41] |
| folio | gpt-4o-mini | 184 | 61% [53,70] | **39%** [30,47] | 9% [3,15] | 30% [22,38] |
| folio | gpt-4o | 188 | 71% [64,79] | **29%** [21,36] | 3% [1,7] | 26% [18,33] |
| proofwriter | Llama-3.1-8B | 585 | 85% [82,89] | 15% [11,18] | 6% [4,9] | 8% [6,11] |
| proofwriter | gpt-4o-mini | 591 | 96% [95,98] | 4% [2,5] | 3% [1,4] | 1% [0,2] |
| proofwriter | gpt-4o | 600 | 97% [96,98] | **3%** [2,4] | 2% [1,4] | 0% [0,1] |
| prontoqa | Llama-3.1-8B | 481 | 64% [59,68] | **36%** [32,41] | 5% [3,7] | 31% [27,35] |
| prontoqa | gpt-4o-mini | 500 | 90% [87,92] | 10% [8,13] | 1% [0,3] | 9% [7,12] |
| prontoqa | gpt-4o | 500 | 100% [100,100] | **0%** [0,0] | 0% [0,0] | 0% [0,0] |

**Headline finding — a capability × language-type interaction.** PrOntoQA and
FOLIO have near-identical weak-model prevalence (36–40% silent) but opposite
responses to scale: gpt-4o eliminates it on synthetic PrOntoQA (36%→0%) yet
leaves a large residue on naturalistic FOLIO (40%→29%). The phenomenon is
capability-**removable** on synthetic logical reasoning but capability-
**resistant** on naturalistic autoformalization. The confidently-wrong class
specifically collapses on frontier scale everywhere (kill gate fired);
under-determination is what persists on FOLIO.

**CAUSAL WORDING CORRECTED 2026-08-22.** This paragraph previously said the
synthetic datasets "act as controls isolating the cause as naturalistic
language complexity, not logical depth." That is a causal claim the design
does not support, and it is the first thing a reviewer would attack. FOLIO and
ProofWriter/PrOntoQA differ on many axes at once (dataset construction
procedure, ontology, proof structure, label distribution, annotation
convention, lexical diversity), so language naturalism is confounded with all
of them. Defensible wording: **a dataset-type interaction consistent with a
naturalistic-language hypothesis**. Establishing naturalism as the cause needs
a controlled intervention or a matched benchmark that varies naturalism while
holding the other axes fixed. Tracked as GAPS.md E14.

---

## 1b. ContractNLI pilot (added 2026-08-22) — real NDAs, and a floor, not a data point

**Read this table only with its ceiling.** ContractNLI ships no gold FOL, so
`crest/crest/evaluation/contractnli_ceiling_probe.py` hand-formalised 10 cases
to measure what a *correct* translation scores: **0% under a literal
convention, 60% [26%, 88%] under a charitable one, 100% if unstated legal
assumptions may be injected**. FOLIO's comparable ceiling is 81.1%. Majority
class here is 82% (FOLIO's was 35.5%); the task is binary, so `Uncertain` is
always wrong and always under-determination.

| dataset | model | n grade | accuracy | silent | wrong_dir | under_det | loud |
|---|---|---|---|---|---|---|---|
| contractnli | Llama-3.1-8B | 56 | 7% [0,14] | **93%** [86,100] | 2% | 91% | 44 |
| contractnli | gpt-4o-mini | 86 | 0% [0,0] | **100%** [100,100] | 0% | 100% | 14 |
| contractnli | gpt-4o | 85 | 1% [0,4] | **99%** [96,100] | 0% | 99% | 15 |

n=100 seeded from the test split, 65 NDAs, all 17 hypothesis templates. CIs are
the wider of document-clustered and hypothesis-clustered bootstraps. Paired
McNemar on accuracy finds no significant difference between any pair
(p=0.125 / 0.25 / 1.0).

**Pre-registered conclusion, and the wording matters:** all three models sit at
the *literal* ceiling, so **the capability × language-type interaction cannot
be tested on ContractNLI-as-FOL** — which is NOT the same claim as "the gap
does not replicate on legal text". A floor effect licenses only the first.

**Three findings that survive the floor and are worth reporting:**

1. **The failure inverts the FOLIO visibility story.** Llama is *significantly*
   better on the not-silent endpoint (p=3.1e-07 vs gpt-4o-mini, 9.4e-07 vs
   gpt-4o) — but purely because 44% of its output is unparseable and therefore
   loud. The frontier models fail **invisibly** on 99–100% of gradeable
   examples. On legal text the capable models are the quiet ones.
2. **The dominant mechanical cause is intra-example predicate naming
   inconsistency** — CREST's exact target phenomenon. Measured in
   `contractnli_blocker_attribution.py`: the share of silent failures whose
   conclusion predicates appear *nowhere* in their own premises, making a
   proof unreachable by construction, is **21% (Llama) / 47% (gpt-4o-mini) /
   36% (gpt-4o)**. The pairs are near-misses, not confusions about law:
   `GrantsRights` vs `GrantsRight`, `ConferRights` vs `GrantRights`,
   `VerballyConveyed` vs `ConveyedVerbally` — the same relation named two ways
   inside a single prompt. **Corrected 2026-08-22 after building the
   detector:** these were first described as "near-misses", implying string
   variants. Measured across all 147 unreachable goals in every committed run,
   exactly **one** is a normalisation-detectable variant; the other 146 are
   *semantic* divergence (a different relation chosen, not a different
   spelling). So the defect is real and it is vocabulary divergence, but
   string normalisation repairs ~0.7% of it — the repair needs semantics.
3. **Of the five blockers the ceiling probe identified, exactly one is
   translation-level** and therefore addressable by a detect-and-repair layer.
   The other four (obligation outside the evidence spans, open-world permission
   gap, absent world-knowledge witness, missing deontic bridge) defeat a
   *perfect* translation. Any claim that CREST "fixes ContractNLI" must be
   scoped to the first.

Caveat on comparing the disjointness rates across models: Llama's 21% is
computed over a pool from which its 44 loud failures have already been
removed, so it is not directly comparable to the frontier models' rates.

Cost: $0.32 total (gpt-4o-mini $0.02, gpt-4o $0.30); the Llama arm ran on
Kaggle.

### 1c. CREST-D, first component built and measured (2026-08-22)

`crest/crest/detection/predicate_checker.py` — deterministic, no model call,
no gold label, runs before the solver. Evaluated on every committed run
(4 datasets × 3 models) at zero additional cost:
`crest/crest/evaluation/schema_detector_eval.py`.

| Claim | Flags | Precision |
|---|---|---|
| `will_return_uncertain` (goal unreachable: no conclusion predicate occurs in any premise) | 147, of which 130 reached the solver | **98.5%** |
| `will_fail_loudly` (one predicate used with conflicting arities) | 55 | **100%** |

Coverage of actual silent failures is **11.3% pooled**, and it is
domain-concentrated: 21–47% on ContractNLI, ~0–7% on FOLIO, ~0% on
ProofWriter/PrOntoQA. This is a high-precision triage signal, not an oracle,
and both halves must be reported.

**The 1.5% residue is not noise and is now named in the module:** both
exceptions are inconsistent premise sets, from which any goal follows —
including one sharing no vocabulary. The module's original docstring claimed
100% soundness with no carve-out; that was wrong and is corrected in place.

**What this component cannot do:** repair. Only 1 of 147 unreachable goals is
fixable by string normalisation. That result moves repair out of the
deterministic layer and into the trained corrector (Phase 8), and it is a
measured argument for that component rather than an assumed one.

### 1d. CREST-D signal 2 (structural divergence) — a NEGATIVE result (2026-08-22)

Signal 1 sees only the FOL, so signal 2 compares each formula against **the
sentence it came from**: quantifier presence, negation parity, conditional
presence, exclusivity. Five rules, each targeting a failure class our own
annotation study measured. Evaluated on every committed run by re-joining the
source sentences from the datasets — no new model calls
(`crest/crest/evaluation/attributor_eval.py`).

**It does not work on the text that matters, and the aggregate nearly hid it.**
The metric is *lift* = P(silent | flagged) / P(silent); lift 1.0 means the
signal carries no information regardless of how good its recall looks.

| dataset | flag rate | recall | **lift** |
|---|---|---|---|
| proofwriter (synthetic) | 96.8% | 100% | **1.03** |
| folio (naturalistic) | ~50–58% | 48–64% | **1.03–1.16** |
| contractnli (real legal) | 64–80% | 44–64% | **0.86–0.98** |
| prontoqa (synthetic) | 1.4–4.8% | 11–14% | **2.26–9.62** |

Aggregate coverage on FOLIO reached 56%, which *passed* the coverage gate
pre-registered in §3.96 — while carrying almost no information. **The gate was
mis-specified and is corrected: coverage alone is not a gate; lift must clear
1.0 with an interval excluding it.** Recorded because a gate that passes a
worthless signal is worse than no gate.

**Per-rule decomposition, done before discarding the module:**

| rule | PrOntoQA | ProofWriter | FOLIO | ContractNLI |
|---|---|---|---|---|
| `negation_parity` | **5.07** | **6.35** | 1.09 | 0.92 |
| `quantifier_missing` | **5.38** | — | 1.17 | 1.07 |
| `quantifier_substituted` | — | 1.01 (fires on 96%) | 1.09 | 0.90 |
| `conditional_lost` | — | 0.00 | **0.14** | 1.07 |
| `exclusivity_lost` | — | — | 1.16 | 0.86 |

Two rules are genuinely informative — but only where they fire rarely, on
**templated synthetic** text. On naturalistic text English cues are ambiguous
("any" is universal or existential depending on context), the rules fire on
half of everything, and lift collapses. `conditional_lost` on FOLIO has lift
**0.14**, i.e. it is anti-correlated — it fires on examples that are more often
*correct*.

**Why this matters more than a failed component.** This is the *second*
independent cheap detector to show the same shape: generation confidence gave
AUROC 0.87 on synthetic/weak and 0.49 (chance) on FOLIO × gpt-4o-mini; surface
structural cues give lift 5–6 on synthetic and ~1.0 on naturalistic. **Cheap
signals systematically fail in exactly the regime where the failure persists.**
Combined with the earlier finding that only 1 of 147 unreachable goals is
repairable by string normalisation, the deterministic layer can neither detect
nor repair meaning-level divergence on naturalistic text. The framework's need
for a learned semantic component is now an empirical result, not a design
preference.

---

## 2. Self-Refine falsification gate (paired, McNemar exact)

Endpoint p is on the not-silent-failure outcome; p > 0.05 = Self-Refine does
not significantly change the silent-failure rate. `net` = helped − hurt on
accuracy.

| dataset | model | n | vanilla silent | refined silent | net (acc) | McNemar p |
|---|---|---|---|---|---|---|
| folio | Llama-3.1-8B | 203 | 40% | 49% | **−31** | 1.000 |
| folio | gpt-4o-mini | 203 | 39% | 42% | −10 | 0.690 |
| folio | gpt-4o | 203 | 29% | 29% | −3 | 1.000 |
| proofwriter | Llama-3.1-8B | 100 | 16% | 38% | **−29** | **0.000** |
| proofwriter | gpt-4o-mini | 600 | 4% | 16% | **−79** | **0.000** |
| prontoqa | Llama-3.1-8B | 100 | 40% | 39% | −5 | 0.392 |
| prontoqa | gpt-4o-mini | 500 | 11% | 13% | −10 | 0.397 |

**Finding.** Self-Refine never helps. It ranges from neutral (frontier, where
there is little to fix) to significantly harmful — on both ProofWriter cells it
significantly *increases* silent failure (Llama 16%→38% and gpt-4o-mini 4%→16%,
both p = 0.000), and at full n the FOLIO/Llama accuracy damage is net −31. This
is a robust falsification-gate result across the whole matrix: a free,
training-free critique-and-revise loop does not close the silent-failure gap
and often widens it, because the model cannot tell *when* to revise.

Matrix is complete. gpt-4o Self-Refine on the synthetic datasets was
deliberately skipped: gpt-4o already solves them, so there is no gap for
Self-Refine to close (no headroom).

---

## 3. Internal reasoning — does generation confidence detect silent failure?

Token-level logprob confidence of the whole-story translation, as a gold-label-
free risk signal. AUROC for separating silent failures from correct among
gradeable examples (0.5 = chance), clustered bootstrap CI.

| dataset | model | n grade | silent | AUROC (mean logprob) | flag-top-20%: precision / recall |
|---|---|---|---|---|---|
| prontoqa | Llama-3.1-8B | 481 | 174 | **0.871** [0.836, 0.904] | 83.5% / 46.6% |
| proofwriter | Llama-3.1-8B | 585 | 85 | 0.682 [0.616, 0.743] | 22.2% / 30.6% |
| folio | gpt-4o-mini | 184 | 71 | **0.492** [0.399, 0.588] | 43.2% / 22.5% |
| proofwriter | gpt-4o | 600 | 17 | 0.391 [0.241, 0.541] | — (17 silent) |
| prontoqa | gpt-4o | 500 | 0 | n/a (no silent) | — |

**Critical finding for the detector direction.** Generation confidence is a
strong silent-failure detector on synthetic reasoning with a weak model
(PrOntoQA/Llama AUROC 0.87) but is **at chance on naturalistic FOLIO** (mini
AUROC 0.49) — i.e. it works where the problem is capability-removable anyway,
and fails exactly where the problem persists at frontier scale. A confidence-
based detector is therefore **not sufficient for the durable (FOLIO) case**;
the cross-fragment predicate-schema-consistency signals (see the semantic
taxonomy) are the direction to pursue there, not raw generation confidence.

---

## What this means for direction (data-driven, not assumed)

1. The general "silent failure everywhere" claim is dead; the honest, stronger
   claim is the **capability × language-type interaction** above.
2. The durable, unsolved core is **naturalistic autoformalization** (FOLIO),
   where scale, self-refinement, and confidence-based detection all fail.
3. A real detector for the FOLIO case must use structural cross-fragment
   consistency, not generation confidence.
4. Single naturalistic dataset (FOLIO) remains a limitation — a second
   naturalistic autoformalization dataset would strengthen the claim.
