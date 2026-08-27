# Preregistration — E1.0 (definition) and E1 (blind human replication)

**Written 2026-08-22, BEFORE any human data is collected.** Nothing in this
document may be changed after the first annotation is submitted; changes after
that point are recorded as amendments with their date and reason, never as
edits to the original text.

This preregistration exists because of `docs/GAPS.md` **E19**: "unformalizable"
is an asymmetric negative claim, and our own probe already demonstrated that
formalizability is contract-relative (0/10 literal, 6/10 charitable, 10/10
assumption-augmented — the last reached by allowing arbitrary assumption
injection). Collecting human data before freezing the definition would produce
an uninterpretable number.

---

## Part 0 — E1.0: the operational definition (must freeze first)

**Definition.** `Formalizable(x; Φ, C)` — instance `x` is *constructively
recoverable* under target formalism `Φ` and admissible-translation contract `C`
if there exists a formalization of `x`'s premises and hypothesis that (a) a
blind reviewer judges semantically faithful to the source text under `C`, and
(b) yields the dataset's gold relation under the frozen prover harness.

**Three consequences, all binding:**

1. **Every reported number is indexed to a named contract.** No unindexed
   "formalizability" figure appears in any document, slide, or draft. "60%"
   alone is meaningless; "60% under `C_charitable`" is a claim.
2. **Negative outcomes are reported as "not constructively recoverable under
   `C` in this audit"** — never as "proven unformalizable". Failure to
   construct is not proof of non-existence. An impossibility claim would need
   a separate criterion (e.g. a proof that no formula set over the admissible
   vocabulary entails the target), which this study does not attempt.
3. **`Φ` is fixed as: first-order logic, as accepted by our frozen Prover9
   harness** (`crest/crest/grounding/fol_to_prover9.py`, unchanged for the
   duration of the study). No equality axioms, no theory reasoning, no
   arithmetic.

### The two contracts, specified to be applicable

**`C_L` — literal contract.**
- Each sentence is formalized on its own terms, using the relation and
  argument structure that sentence actually uses.
- No unification of vocabulary across sentences beyond what the text itself
  makes explicit (an anaphor or an explicit definitional clause counts as
  explicit; a shared topic does not).
- Exception and proviso clauses present in the text must be represented.
- No premise may be added that is not stated in the given text.
- No world knowledge beyond dictionary-level word meaning.

**`C_C` — charitable contract.**
- Everything in `C_L`, plus:
- The hypothesis's generic vocabulary may be unified with the document's own
  drafting vocabulary where a competent reader of the document would take them
  to denote the same relation (e.g. "Information" in the clause and
  "Confidential Information" in the hypothesis).
- Procedural provisos that state *how* an action must be performed may be
  treated as side conditions rather than as antecedents of the rule.
- Still no added premises, and still no injected world knowledge.

**Deliberately excluded: the assumption-augmented contract.** Our own probe
showed it reaches 10/10 by construction. It is retained only as a documented
demonstration that unconstrained formalization trivializes the question — it
is not a condition in this study.

### Contract pilot — before the audit cases are touched

Both contracts are applied by all annotators to **2–3 pilot cases drawn from
ContractNLI's train split** (never the audit cases). Purpose: surface
ambiguities in the contract wording while it is still cheap to fix. The
contract may be revised after the pilot; it is frozen the moment the first
audit case is issued. Pilot disagreements and any resulting contract revision
are recorded in this document as a dated amendment.

---

## Part 1 — E1: the study

### Hypothesis

**H1.** Under the frozen literal contract `C_L`, independently produced,
blind-verified faithful formalizations will be constructively recoverable on
substantially fewer than 70% of the 10 audit cases.

**H2 (separate hypothesis, separate metric, separate falsification).** Human
annotators can apply the admissibility contracts reliably enough for the
construct to be operational.

These are **not** combined into one gate. H2 failing does not confirm or deny
H1 — it means the construct is not yet measurable, which is a different (and
more serious) result.

### Sample

The **same 10 ContractNLI cases** used in Claude's original probe
(`crest/crest/evaluation/contractnli_ceiling_probe.py`), so this is a direct
replication rather than a new sample. 6 Entailment / 4 Contradiction.

**Stated limitation, not discovered afterwards:** n=10 gives wide intervals.
0/10 yields a 95% CI of roughly [0%, 31%] and 6/10 roughly [26%, 88%]. This
study can therefore detect a *strong* effect (near-zero recoverability) but
cannot distinguish, say, 40% from 70%. It is a replication of direction, not a
precise ceiling estimate. If the direction replicates, a larger sample is the
next step — not a re-interpretation of this one.

### Annotators

**Exactly 3 independent human annotators.** Not "≥3": the primary metric below
is existence-shaped, so its value rises mechanically with annotator count, and
the number must be fixed in advance for the figure to mean anything.

### Blinding

Annotators see **only**: the source clause text, the hypothesis text, and the
contract they are applying.

They do **not** see: the gold label, Claude's formalization, any model output,
the previous blocker classification, the 0/10 result, or each other's work.

### Outcome space — four categories, not two

For each (case, annotator, contract), the formalization is classified as:

| Outcome | Meaning |
|---|---|
| **A. Faithful + yields gold** | Constructively recoverable under `C`. |
| **B. Faithful + yields the opposite of gold** | Evidence the **gold label is wrong**, not that the task resists formalization. Reported separately and never folded into failure. Precedent: our probe's case `493_nda-15`, where an exception clause makes the gold label arguably indefensible; and "Know Your Limits" relabelled 22% of its ContractNLI sample. |
| **C. Faithful + yields Uncertain** | Underdetermined *under this contract* — the honest core of the formalizability claim. |
| **D. No faithful formalization produced** | Annotator could not construct one they and the reviewers accept. Reported as a construction failure, explicitly not as impossibility. |

### Fidelity validation — the step that makes or breaks the study

A formalization **does not count as successful merely because Prover9 returns
the gold label.** An unfaithful formula can match by accident, and counting
those inflates the estimate.

Procedure:
1. Each formalization is reviewed for semantic fidelity by the **other two
   annotators**, blind to authorship.
2. **Fidelity is judged before the reviewer sees what the prover returns.**
   This ordering is mandatory — knowing the verdict contaminates the judgement.
3. A formalization is admissible only if **both** reviewers judge it faithful
   under the contract.

### Primary metric

**Case-level constructive recoverability under `C_L`:** the proportion of the
10 cases for which **at least one of the 3 annotators** produced a formalization
that (a) passed blind fidelity review and (b) yielded the gold relation.

Reported alongside, always:
- **Per-annotator recoverability rate** (so the existence-metric's dependence
  on annotator count is visible).
- The full A/B/C/D outcome distribution.
- The same figures under `C_C`.

This metric is a **lower bound on existence**, and it grows with the number of
annotators. That is stated wherever it is reported.

### Reliability reporting (H2)

- **Raw agreement is reported before any reconciliation**, always. The project
  has been burned by this before: raw human-vs-Claude κ was 0.430 and only
  reached 0.725 after a reconciliation round, and only the raw figure speaks to
  independent reliability.
- For the multidimensional diagnosis (see below), **no single global κ.**
  Report per-axis prevalence, per-axis raw agreement, and a per-axis
  reliability statistic.
- Reconciliation may follow, but is reported as taxonomy refinement evidence,
  never as independent agreement.

### Falsification conditions — written before the data exists

| Result | Consequence |
|---|---|
| Constructive recoverability under `C_L` is **≥70%** with defensible fidelity | The "ContractNLI exposes a formalizability barrier" hypothesis is **not supported by this replication**. It is narrowed or retracted — not rescued by switching contracts after the fact. |
| Annotators cannot apply the contract reliably (H2 fails) | E1 establishes **nothing about the dataset**. It establishes that the formalizability construct is not yet operationally reliable, which blocks P-B until the definition is repaired. |
| Outcome **B** is frequent | The finding shifts from "task resists formalization" to "gold labels are unreliable" — a different paper-level claim, and one that must not be presented as the first. |
| Recoverability is low under `C_L` and high under `C_C` | Supports the contract-relativity claim (E19), which is then the reportable finding — *not* an absolute ceiling. |

### What this study explicitly does NOT establish

- That any case is impossible to formalize.
- Any ceiling figure not indexed to a named contract.
- Anything about datasets other than ContractNLI.
- Anything about the attributor's precision — that is a separate study with a
  separate gate (see E18: raw human reliability on the attribution axes must be
  established before those labels can serve as the attributor's ground truth).

---

## Part 2 — the diagnosis is a state vector, not a class label

Adopted from external review 2026-08-22, superseding the flat three-class
framing in `RESEARCH_DIRECTION.md` §3.96 and refining `docs/GAPS.md` E17.

A diagnosis is **not** one of three mutually exclusive labels. It is a state
over three independent axes:

| Axis | Question |
|---|---|
| **F** — specification / formalizability adequacy | Is the instance determinable under contract `C`? |
| **T** — translation fidelity | Does the produced formalization faithfully represent the text? |
| **S** — solver execution adequacy | Did the prover run to a sound conclusion (no timeout, no encoding limit)? |

`F=0, T=0` can hold simultaneously: the translation error is real **and**
repairing it would not recover the end task. That case is invisible to a flat
label and is exactly where a repair layer would waste effort while appearing
justified.

This resolves three problems at once:
- **κ**: per-axis reliability replaces one global figure that would be
  depressed by multi-cause cases for reasons unrelated to annotator skill.
- **Metric**: "attribution precision" becomes per-axis, and does not presuppose
  a single correct label.
- **Repair policy**: repair fires on `T=0` **only when `F=1`** — the condition
  under which repair can actually recover the task.

---

## Sequence this preregistration sits inside

E1.0 contract freeze (this document) → contract pilot on non-audit cases →
E1 blind replication → E8 contamination audit and recompute of affected arms
only → **then** larger P-B annotation.

Rationale for this ordering: annotating 300–500 cases and then discovering the
taxonomy or the formalizability definition needs to change is the most
expensive methodological mistake available to this project. The three
formulation problems — multi-cause attribution (E17), human ground-truth
reliability (E18), and the formalizability definition (E19) — are frozen
before scale, not after.
