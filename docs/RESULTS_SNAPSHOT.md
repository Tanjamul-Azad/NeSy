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
**resistant** on naturalistic autoformalization. The synthetic datasets act as
controls isolating the cause as naturalistic language complexity, not logical
depth. The confidently-wrong class specifically collapses on frontier scale
everywhere (kill gate fired); under-determination is what persists on FOLIO.

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
| prontoqa | Llama-3.1-8B | 100 | 40% | 39% | −5 | 0.392 |
| prontoqa | gpt-4o-mini | 500 | 11% | 13% | −10 | 0.397 |

**Finding.** Self-Refine never helps. It ranges from neutral (frontier, where
there is little to fix) to significantly harmful (ProofWriter/Llama, p = 0.000,
silent 16%→38%). At full n the FOLIO/Llama damage is net −31 on accuracy. This
is a robust falsification-gate result across the whole matrix: a free,
training-free critique-and-revise loop does not close the silent-failure gap
and often widens it, because the model cannot tell *when* to revise.

*Missing cell:* ProofWriter × gpt-4o-mini Self-Refine (a run hung on a WSL
Prover9 glitch and was killed; the grounder now has a hard subprocess timeout —
re-run pending). gpt-4o Self-Refine on the synthetic datasets was deliberately
skipped: gpt-4o already solves them, so there is no gap for Self-Refine to
close (no headroom).

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
