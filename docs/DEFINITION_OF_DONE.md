# FYDP-2 — Definition of Done (frozen 2026-08-27)

**FYDP-2 ends when: the framework stands, the experiments are complete, the
paper is submission-ready, and the thesis is substantively complete.**

Not "future work: build the model / do the annotation / run the baselines /
write the paper." At the end of FYDP-2 the only remaining work is submission
polish, formatting, presentation, and reviewer-driven extras.

Agreed jointly by Tanjamul and both research assistants. Supersedes any earlier,
looser exit condition.

---

## The ten conditions

**1. Scientific formulation frozen.** F/T/S multidimensional diagnosis,
`Formalizable(x; Φ, C)`, post-execution diagnosis, and the repairability
definition are all mathematically/operationally precise. **The framework does
not freeze while E1, E17, E18 or E19 are unresolved.**

**2. CREST implemented end to end** — not a diagram. Input → translation →
diagnosis/attribution → repairability decision → selective repair →
verification/acceptance → solver → final output. Every module has a stated
mechanism and a measurable role. **A component that ablates to no effect is
removed from the final framework**, not retained for completeness.

**3. Human ground truth complete.** The axes are reliable under *fresh,
independent* annotation, with pre-reconciliation reliability reported. Then
300–500+ defensible annotated examples across multiple datasets. **If raw κ is
unacceptable, large-scale annotation stops and the schema is redesigned** —
scale is never used to paper over an unreliable construct.

**4. Full experiment suite complete.** Vanilla baselines; stronger models;
Self-Refine parity baseline; attribution baselines; the final attributor;
oracle attribution; diagnosis-conditioned repair; repair-all baseline;
ablations; confidence/calibration; solver audit; multi-dataset × multi-model
evaluation; paired statistics with CIs; multi-seed wherever stochasticity
exists. E8 contamination resolved and affected arms recomputed.

**5. Selective repair must earn its place.** If the same repair model without
diagnosis conditioning performs equally well, the diagnosis-conditioned
contribution is dead and is reported as such. If repair materially corrupts
previously-correct cases, the non-degradation claim is narrowed or retracted.
**Empirical zero-regression is never called a theorem** (GAPS.md E15).

**6. Reproducibility package complete.** Exact prompts, seeds, resolved model
IDs/snapshots, dataset split IDs, prover version and config, raw generations,
annotation files, scripts, statistics, environment — all committed. **No table
cell is typed from memory** (see the canonical-table rule below).

**7. Paper submission-ready.** Abstract, introduction, related work, formal
problem formulation, framework, datasets, annotation protocol, experiments,
results, ablations, error analysis, limitations, ethics/reproducibility
appendix — all written. Not a skeleton with "results go here". The target is a
draft that could be uploaded to a submission portal as it stands.

**8. Thesis 90–95% substantively complete.** Introduction, literature review,
methodology, framework, experimental design, results, discussion, limitations,
conclusion — core content finished. Remaining: university formatting,
supervisor edits, viva slides, minor expansion. Paper methodology and results
are reused systematically in the thesis so nothing is written twice.

**9. Novelty externally verified.** The final contribution wording does not
freeze without a literature search. **"First", "no prior work", and "novel" are
not written without evidence** (GAPS.md G5).

**10. Retraction/change log preserved.** Every reversed claim stays on record —
the silent-failure generalization, the Self-Refine wording, the coverage gate,
the reachability soundness claim, the causal wording, the formalizability
ceiling wording. The final paper carries only currently defensible claims; the
history stays in `docs/GAPS.md` Section D.

---

## Scope discipline — the rule that makes this achievable

**Finish all central work, not all possible work.** Cross-formalism
generalization, a fourth dataset, additional models: these are ceiling-raising
extensions that happen *after* the core contribution survives. **Scope is never
widened while the core mechanism is weak.**

A new experiment is authorized only if it (a) tests a preregistered central
claim, (b) closes a reviewer-critical confound, or (c) materially raises the
publication ceiling. Otherwise it goes to the backlog.

---

## Two additions to the agreed list

These are not disagreements with the ten conditions; they are what the list
needs to survive contact with a calendar.

### A. Quarterly checkpoints with a declared descope rule

The DoD has no interim milestones, which risks discovering at month 14 that the
project is at 40%. Every three months, each of the ten conditions is assessed
as on-track / at-risk / behind, in writing.

**Declared now, so it is not improvised under deadline pressure:** if at the
month-12 checkpoint conditions 3 and 4 are not on track, the descope order is
fixed — first drop additional datasets beyond the core, then reduce the
annotation target from 500 toward 300, then narrow the model matrix. **Never
descope the reliability requirements (raw κ, blinding, pre-registration) or the
non-degradation honesty requirements.** Those are what the work is *for*.

### B. Condition 3 is the execution risk, and it is an operational problem

Recruiting and coordinating external annotators for 300–500 examples — with
blinding, fidelity review, and pre-reconciliation reliability — is the largest
non-research burden in the plan, and it is the one that cannot be solved by
working harder in the last month. **A recruitment and scheduling plan exists
before P-B begins**, not after. The E1 pilot (5 external people) is also the
dry run for that logistics chain, and should be treated as such.

---

## Framework maturation — three stages, no premature diagram lock

| Stage | Contents |
|---|---|
| **v0 — scientific specification** | F/T/S diagnosis, formalizability contract, repairability policy, verification semantics |
| **v1 — attribution system** | human-validated axes + working attributor + calibrated decision rule |
| **v2 — full CREST** | attribution + selective repair + acceptance/verification + solver integration |

**v2 is the final framework for both paper and thesis.** This removes any
obligation to preserve the FYDP-1 architecture: the components that survive the
evidence are the components CREST ends up with.

---

## Two parallel tracks, starting now

**Research track:** the seven gated stages in `docs/FYDP2_PLAN.md` (S0 formulation
freeze → S1 construct validation → S2 measurement hygiene → S3 resource → S4
attributor → S5 selective repair → S6 scale/ablate, with S7 cross-formalism
conditional).

**Writing track:** paper v0.1 and thesis skeleton **now**, then both updated
after every completed gate.

The research loop is: **preregister → run → analyze → update claim/retraction →
immediately write the corresponding paper and thesis subsection.** Writing is
not a phase at the end; when the last experiment finishes, the manuscript is
nearly finished too.

### The canonical-table rule (enforces condition 6)

Every experimental table in the paper and the thesis is **generated by script
from the committed result JSONs** — never typed by hand, never copied from a
chat message. One canonical source, two rendered outputs. A number that cannot
be regenerated from the repository does not appear in either document.

---

## The concrete endpoint

At the end of FYDP-2 there exists:

- a **git tag** from which the final CREST experiments reproduce;
- a **frozen results table**, script-generated;
- a **submission-ready manuscript** targeting an A*/Q1 venue;
- **thesis scientific chapters essentially complete**.

After FYDP-2 the work is to *submit and strengthen* the paper — not to start
writing it.

**What this standard can and cannot promise:** it cannot guarantee A*/Q1
acceptance; no plan can. It can guarantee that at submission time no obvious
foundational experiment is missing. That is the part within our control, and it
is the part being enforced.
