# Formalization Task — Instructions

Thank you for helping with this task. Please read this sheet fully before
starting. It should take about 10 minutes to read.

**Please do not search online for this task, these clauses, or this dataset,
and please do not discuss the task with anyone else who is doing it.** If you
recognise any of the material from previous work, tell the coordinator before
continuing.

---

## What you are doing

You will be given short excerpts from **non-disclosure agreements** (legal
contracts) and, for each excerpt, a single **statement** about what the
contract says.

Your job: **write first-order logic (FOL) formulas that faithfully represent
the excerpt and the statement**, following one of two sets of rules given
below.

You are **not** being asked whether the statement is true or false. You are
being asked to represent the meaning in logic. Whether the statement follows
from the excerpt is determined afterwards by an automated theorem prover, not
by you, and not by anything you write.

There is no expected answer. Writing "I could not produce a faithful
formalization under these rules" is a legitimate and useful outcome — please
use it whenever it is honest, rather than forcing a formula you do not believe
represents the text.

---

## Notation

Use standard FOL notation:

| Symbol | Meaning | ASCII alternative |
|---|---|---|
| `∀x` | for all x | `all x` |
| `∃x` | there exists an x | `exists x` |
| `∧` | and | `&` |
| `∨` | or | `\|` |
| `¬` | not | `-` |
| `→` | implies | `->` |
| `↔` | if and only if | `<->` |
| `⊕` | exclusive or | (no ASCII form; use the symbol) |

Conventions:
- **Predicates** start with a capital letter: `Discloses(x, y)`,
  `ConfidentialInformation(x)`.
- **Constants** are lowerCamelCase: `receivingParty`, `disclosingParty`.
- **Variables** are `x`, `y`, `z`.
- Write **one formula per numbered line**, matching the numbering you are
  given (`P1`, `P2`, …, and `C` for the statement).

Example of the expected shape (not from this task):

```
P1: ∀x (Employee(x) → SignsAgreement(x))
P2: Employee(alice)
C : SignsAgreement(alice)
```

**Available machinery:** plain first-order logic only. No arithmetic, no
equality axioms, no set theory, no modal or temporal operators. If the text
genuinely needs something outside plain FOL to be represented faithfully, say
so in the notes field rather than approximating it silently.

---

## The two rule sets

You will do **each case twice** — once under Rule Set A, once under Rule Set B.
Do A first for all cases, then B. They differ only in what you are permitted to
assume.

### Rule Set A (strict)

1. Formalize each sentence **on its own terms**, using the relation and
   argument structure that sentence actually uses.
2. **Do not unify vocabulary across sentences** unless the text itself makes
   the connection explicit. A pronoun referring back to something, or an
   explicit definition ("'Information' means …"), counts as explicit. Merely
   being about the same topic does not.
3. **Exceptions and provisos in the text must be represented.** If a clause
   says something holds "except when …", the exception belongs in the formula.
4. **Do not add any premise that is not stated in the given text**, even if it
   is obviously true in the real world.
5. **No world knowledge** beyond ordinary dictionary word meaning.

### Rule Set B (charitable)

Everything in Rule Set A, **plus** the following two relaxations:

6. Where the statement uses general vocabulary and the contract uses its own
   drafting vocabulary, you **may treat them as the same relation** if a
   competent reader of that contract would take them to refer to the same
   thing (for example, a clause that says "Information" and a statement that
   says "Confidential Information").
7. Procedural provisos that describe **how** something must be done (rather
   than **whether** it may be done) may be treated as side conditions instead
   of as conditions inside the rule.

Rules 4 and 5 still apply in Rule Set B. **You may never invent a premise or
import outside knowledge, under either rule set.**

---

## For each case, record

1. **The formulas** (`P1`…`Pn`, `C`), or the explicit statement that you could
   not produce a faithful formalization under that rule set.
2. **Notes** — anything that was difficult, ambiguous, or that the rules did
   not tell you how to handle. This field matters as much as the formulas.
3. **Rule questions** — if you found yourself unsure *what the rules permit*
   (as opposed to unsure what the text means), flag it explicitly. That
   distinction is important to us: uncertainty about the contract's meaning is
   expected and fine; uncertainty about the rules is a defect in our
   instructions that we need to fix.

---

## Comprehension check

Please answer these before starting. They are about the **rules**, not about
any legal text. All must be correct before you begin.

1. Under Rule Set A, a clause says obligations apply "except in the case of
   information already public". May you omit the exception? **(yes / no)**
2. Under Rule Set A, one sentence says "Information" and another says
   "Confidential Information", with no definition connecting them. May you use
   the same predicate for both? **(yes / no)**
3. Under Rule Set B, same situation as question 2 — may you use the same
   predicate? **(yes / no)**
4. Under either rule set, may you add a premise stating something obviously
   true that the text does not say (for example, "an employee is a person")?
   **(yes / no)**
5. You believe the statement is clearly false given the excerpt. Should you
   adjust your formulas so the theorem prover reaches that conclusion?
   **(yes / no)**
6. You cannot represent the text faithfully under Rule Set A. What should you
   do? **(free text)**

<details>
<summary>Coordinator's key — do not show to annotators before they answer</summary>

1. No — exceptions must be represented (rule 3).
2. No — no cross-sentence unification without explicit textual warrant (rule 2).
3. Yes — rule 6 permits it where a competent reader would take them as the
   same relation.
4. No — rules 4 and 5 forbid added premises and outside knowledge under both
   rule sets.
5. No — you are representing meaning, not steering the outcome. The prover's
   verdict is not your target.
6. Record explicitly that no faithful formalization was possible under that
   rule set, and explain why in the notes. This is a legitimate outcome, not a
   failure.

</details>

---

# Reviewer Instructions (separate role — for the two fidelity reviewers)

You will be shown: an excerpt, a statement, one rule set, and **a candidate set
of formulas written by someone else**. You will not be told who wrote them.

Your job is a single judgement per candidate:

> **Under this rule set, do these formulas faithfully represent the excerpt and
> the statement?** (yes / no / unsure, plus a one-line reason)

Points that matter:

- Judge **faithfulness to the text under the stated rules** — not elegance,
  not whether you would have written it the same way, and not whether the
  statement seems true.
- A formalization that is faithful but expressed differently from your own
  preference is **faithful**. Say yes.
- A formalization that quietly drops an exception, adds an unstated premise,
  merges vocabulary the rule set does not permit merging, or changes the
  polarity of a statement is **not faithful**. Say no, and name which rule.
- You will **not** be shown what the theorem prover concludes, and you should
  not try to work it out. Faithfulness is judged on the text alone.

If the two reviewers disagree, the candidate is treated as not admissible. That
is deliberate and conservative; disagreements are recorded, not resolved by
discussion.

---

## What we are studying (deliberately not detailed here)

We are studying how reliably these rule sets can be applied by different
people. We have withheld our specific expectations, and the dataset's own
labels, on purpose — knowing them would change how you annotate, which would
invalidate the measurement. You will be told the full picture afterwards, and
you are welcome to ask any question about the task itself at any point.
