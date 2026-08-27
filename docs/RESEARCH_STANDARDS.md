# CREST — Research Standards (governing instruction, all sessions, all team members)

**Set 2026-08-27, at Tanjamul's explicit direction.** This document is what
every LLM session, every team member, and every future collaborator on this
project operates under. It is not aspiration — it is the operating rule. If
any instruction given in a session contradicts this document, this document
wins unless Tanjamul explicitly overrides it in writing, here.

**The goal, stated without hedging:** this work must become a genuinely
competitive paper at an A* venue (ACL / EMNLP / NAACL / NeurIPS / ICLR / ICML)
or a Q1 journal, and a strong thesis alongside it — not merely a completed
FYDP. Time, compute cost, and depth of study are **never** the constraint.
Correctness and real contribution are the only constraints that matter.

---

## Absolute rules — non-negotiable

**1. Never give a wrong, guessed, or fabricated answer.** If uncertain, say
"I don't know," "this is my best estimate," or "this needs verification" —
never fill a gap with something plausible-sounding. A wrong answer stated
confidently is worse than an honest "I don't know," because it costs the
project more to discover later.

**2. Never fabricate a citation, dataset, author, benchmark number, or
result.** Every claim about prior work must be checked against a real,
findable source before being stated. If it cannot be verified right now, say
so explicitly rather than asserting it. This applies to every literature
claim in every chapter, every related-work paragraph, every "X et al. showed
Y" — no exceptions for convenience.

**3. "No reviewer can flag this" is not a real target, and promising it would
itself be dishonest — no paper is flag-proof.** The honest version: **every
anticipated weakness has an already-written, evidence-backed answer before
submission**, prepared in advance, not improvised during rebuttal.
`docs/GAPS.md` is the mechanism for this — every open weakness, untested edge
case, and past mistake stays visible there until genuinely closed, never
hidden to make the work look cleaner than it is. A limitations section
written from GAPS.md is a strength, not an admission of failure.

**4. Every claimed contribution needs a name, a mechanism, and a
measurement — never just an adjective.** "Novel," "robust," "efficient,"
"better," "state-of-the-art" are banned words unless immediately followed by
the specific evidence that earns them. "Where is the evidence?" is asked of
every such claim, including ones made by Claude.

**5. Every result must be reproducible from what is actually committed to the
repo** — same seed, same prompt version, same code path, logged model
snapshot (not just an alias like "gpt-4o"). If it is not reproducible from
the repo, it is not a result yet, no matter how confident the number sounds.

**6. Depth and cost are never the reason to accept a weaker result.** If a
claim needs a bigger dataset, a second independent human annotator, a
stronger model, a rented cloud GPU, or a slower and more careful method to be
defensible, that is what gets done — regardless of budget or calendar time —
rather than reporting the cheaper, weaker version and hoping it survives
review. (See `docs/GAPS.md` E13: the standing example of this rule already in
force for P-C's compute resourcing.)

**7. Actively try to destroy our own claims before a reviewer does.** Every
finding gets an adversarial pass: what is the alternative explanation, what
is the confound, what would a hostile Reviewer 2 say, does the evidence
survive it. This project has already done this successfully more than once —
e.g. the ContractNLI "near-miss" claim and the P-A coverage gate were both
self-falsified this way, not by an external reviewer. That is the standard
going forward, not the exception.

**8. The contribution must be real and ours** — a genuine framework, a
genuine finding, a genuine mechanism — never a repackaging of an existing
method, pure benchmarking dressed as a system, or incremental parameter
tuning presented as novelty. If a direction is any of those, say so
immediately and propose the stronger alternative, even if it costs already-
invested time. The currently pinned claim (failure attribution +
diagnosis-conditioned repair with a non-degradation guarantee,
`docs/RESEARCH_DIRECTION.md` §3.95–3.96) is held to this same test, not
exempted from it because we already committed to it.

**9. Every reversal, correction, or retracted claim is recorded** with its
date and what triggered it, in `docs/GAPS.md` Section D, and that record
never shrinks or gets quietly cleaned up before submission.

**10. Nothing overrides the standing question: what is the actual scientific
question, and what does the field learn if we are right?** If that question
does not have a real answer at any point, stop and re-derive the direction
before writing another line of code or running another experiment. Building
a system before the research question is settled is the specific failure
mode this project has already had to catch itself doing once (CREST-D
modules were started before the novelty claim was pinned) — it will not be
repeated as a pattern.

---

## Citation and literature discipline

- Every related-work claim is checked against the actual paper, not against
  memory of what the paper "probably says." When a paper cannot be fetched or
  verified in a given session, the claim is marked unverified in the text and
  in `docs/GAPS.md`, not stated as settled.
- The related-work landscape is rechecked on a recurring basis, not once —
  this is `docs/GAPS.md` G5. A near-neighbour paper appearing after the last
  check is exactly the failure mode this rule exists to prevent.
- Every citation in the eventual paper must resolve to a real, specific,
  checkable source (arXiv ID, DOI, or equivalent) before submission. No
  placeholder citations survive to a draft that leaves the team's hands.

## How this is enforced day to day

- `docs/RESEARCH_DIRECTION.md`, `docs/RESULTS_SNAPSHOT.md`, and
  `docs/GAPS.md` are the source of truth. Any new finding, decision, or
  reversal is written into the relevant document and committed in the same
  session it happens, not left only in chat history — this is how five team
  members stay synchronized on one picture of the project rather than five.
- Every new experiment is pre-registered before it runs: the hypothesis, the
  metric, and the exact condition that would falsify it, written down before
  the result is seen. This project has already self-corrected twice this way
  (the ContractNLI ceiling claim, the P-A coverage gate) — that is the
  standard, not a one-off.
- No idea is scored on a subjective 1–10 scale. Instead, every proposed
  direction is required to state the specific, numeric, falsifiable gate that
  would kill it, checked against data already in hand before any new model
  run, dataset build, or GPU spend is authorized.

---

*This document updates the moment the claim, a phase's status, or the team's
direction changes — in the same session, the same way `docs/RESEARCH_
DIRECTION.md` already governs itself. It must never be allowed to drift out
of sync with what the project actually is.*
