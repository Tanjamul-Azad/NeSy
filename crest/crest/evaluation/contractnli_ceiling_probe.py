"""Step 5, pre-flight: a ceiling probe for ContractNLI.

WHY THIS EXISTS, BEFORE ANY MODEL RUN
=====================================
Phase 2.1 established the rule this project runs on: before any silent-failure
number from a dataset is interpretable, you must know what the *grounder*
scores when handed a correct formalisation. On FOLIO that was free -- FOLIO
ships gold FOL, and running it through Prover9 gave 81.1% (excluding
malformed gold), which is why every downstream FOLIO number means something.

ContractNLI ships NO gold FOL (`has_gold_fol=False` in the loader). So the
same question -- "can a *correct* translation of these evidence spans even
entail the gold label?" -- has no free answer, and without it a low pilot
accuracy is uninterpretable: it could mean the models translate legal text
badly (the finding we are looking for), or it could mean ContractNLI's
entailment relation is simply not first-order-derivable from the evidence
spans alone (in which case every model scores near zero and the pilot
measures the task, not the models).

This module answers it the only way available: by hand-formalising a small
probe sample and running it through the identical grounder
(`crest.grounding.fol_to_prover9.check_entailment`, WSL/Prover9, same as
Phase 2.1 and every vanilla run).

TWO CONVENTIONS, DELIBERATELY BOTH
==================================
Formalising ContractNLI forces a choice that FOLIO never did, because FOLIO's
gold FOL fixed the convention for us. ContractNLI's hypotheses are written in
generic contract vocabulary ("Confidential Information", "the purposes stated
in Agreement") while each NDA uses its own idiosyncratic drafting vocabulary
("Information", "the Purpose", "Evaluation Material"). So:

  LITERAL     -- each sentence formalised on its own terms, using the words
                 that sentence actually uses. No cross-sentence vocabulary
                 unification, no dropped exception clauses, no injected
                 world knowledge.
  CHARITABLE  -- the annotator additionally aligns the hypothesis's generic
                 vocabulary with the document's own (Information ==
                 Confidential Information, the Purpose == the purposes stated
                 in the Agreement), and treats procedural provisos as
                 side-conditions rather than as antecedents.
  ASSUMPTION- -- the annotator may further add whatever unstated legal-context
  AUGMENTED      assumption is needed as an explicit extra premise. This is
                 what "Know Your Limits" (arxiv 2606.16118) did: their
                 autoformalizer was "prompted to encode assumptions in legal
                 contract context as explicit logical statements", which is
                 how 78% of their 400 re-annotated examples survived strict
                 P AND NOT-H unsatisfiability.

The gap between the conventions IS the finding: it measures how much of
ContractNLI's "entailment" is legal-pragmatic alignment rather than
first-order derivation. Whichever convention the pilot adopts must be stated
in the paper, not left implicit -- an unstated convention here would silently
set the ceiling.

Note the third convention's cost, which is the sharpest point this probe
makes: once arbitrary assumption injection is allowed, the annotator can
always manufacture a premise that yields the gold label, so the ceiling
approaches 100% by construction and stops being a measurement of anything.
That is a reason to read prior work's high strict-entailment retention rate
with care, and a reason our pilot must pre-register which convention it uses
BEFORE seeing model output.

HONEST PROVENANCE -- READ BEFORE CITING
=======================================
The FOL below is CLAUDE's hand formalisation, not an independent human's.
It is a feasibility probe with the same standing as Claude's annotation
passes in step 4: usable to decide how to run the pilot, NOT citable as a
human-verified ceiling. n=10 (6 Entailment / 4 Contradiction), drawn with a
fixed seed from the same 100-example pilot sample. Before any ceiling number
from this file appears in the paper, a human should re-formalise the same
probe independently, exactly as step 4 required for the taxonomy.

Run: python -m crest.evaluation.contractnli_ceiling_probe
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scipy.stats import beta, binom

from crest.grounding.fol_to_prover9 import check_entailment


def _clopper_pearson(k: int, n: int, alpha: float = 0.05):
    """Exact binomial interval. Used instead of a normal approximation because
    n here is 10 and k can be 0 or n, where the approximation is meaningless.
    """
    lo = beta.ppf(alpha / 2, k, n - k + 1) if k > 0 else 0.0
    hi = beta.ppf(1 - alpha / 2, k + 1, n - k) if k < n else 1.0
    return float(lo), float(hi)

# Each entry: the hand-written FOL under both conventions, plus the note
# explaining what the charitable convention had to add. The `blocker` field
# names what stops the literal derivation -- that classification is the real
# output of this probe, more than the headline count.
PROBE = [
    {
        "example_id": "165_nda-12",
        "gold": "True",
        "literal": {
            "premises": [
                "∀x ((IndependentlyDevelopedBy(x, receivingParty) ∧ ¬DevelopedUsingReferenceTo(x, disclosingPartyConfidentialInformation)) → ¬ConfidentialInformation(x))",
            ],
            "conclusion": "∃x (SimilarTo(x, confidentialInformation) ∧ MayIndependentlyDevelop(receivingParty, x))",
        },
        # The charitable annotator still cannot bridge this: the premise says
        # what is NOT Confidential Information; the hypothesis asserts a
        # PERMISSION. Nothing in the evidence spans licenses "not confidential
        # => permitted" -- that is an unstated legal default, and adding it
        # would be injecting a premise, not aligning vocabulary.
        "charitable": {
            "premises": [
                "∀x ((IndependentlyDevelopedBy(x, receivingParty) ∧ ¬DevelopedUsingReferenceTo(x, disclosingPartyConfidentialInformation)) → ¬ConfidentialInformation(x))",
            ],
            "conclusion": "∃x (IndependentlyDevelopedBy(x, receivingParty) ∧ MayDevelop(receivingParty, x))",
        },
        # Injected: the unstated legal default (anything outside the
        # confidentiality obligation is unrestricted) plus a witness.
        "assumption_augmented": {
            "premises": [
                "∀x ((IndependentlyDevelopedBy(x, receivingParty) ∧ ¬DevelopedUsingReferenceTo(x, disclosingPartyConfidentialInformation)) → ¬ConfidentialInformation(x))",
                "∀x (¬ConfidentialInformation(x) → MayDevelop(receivingParty, x))",
                "IndependentlyDevelopedBy(w, receivingParty) ∧ ¬DevelopedUsingReferenceTo(w, disclosingPartyConfidentialInformation)",
            ],
            "conclusion": "∃x (IndependentlyDevelopedBy(x, receivingParty) ∧ MayDevelop(receivingParty, x))",
        },
        "blocker": "missing_deontic_bridge (exclusion from CI => permission is an unstated legal default)",
    },
    {
        "example_id": "49_nda-4",
        "gold": "True",
        # Literal: the premise governs "Information disclosed pursuant to this
        # Agreement" and "the Purpose"; the hypothesis speaks of "Confidential
        # Information" and "the purposes stated in Agreement". Different words,
        # therefore different predicates.
        "literal": {
            "premises": [
                "∀x (InformationDisclosedPursuantToAgreement(x) → GovernedByAgreement(x))",
                "∀x ∀y ((InformationDisclosedPursuantToAgreement(x) ∧ UsedFor(receivingParty, x, y)) → CarryingOutThePurpose(y))",
            ],
            "conclusion": "∀x ∀y ((ConfidentialInformation(x) ∧ UsedFor(receivingParty, x, y)) → PurposeStatedInAgreement(y))",
        },
        # Charitable: unify Information == Confidential Information and
        # the Purpose == the purposes stated in the Agreement.
        "charitable": {
            "premises": [
                "∀x (ConfidentialInformation(x) → GovernedByAgreement(x))",
                "∀x ∀y ((ConfidentialInformation(x) ∧ UsedFor(receivingParty, x, y)) → PurposeStatedInAgreement(y))",
            ],
            "conclusion": "∀x ∀y ((ConfidentialInformation(x) ∧ UsedFor(receivingParty, x, y)) → PurposeStatedInAgreement(y))",
        },
        "blocker": "vocabulary_alignment (document vocabulary vs generic hypothesis vocabulary)",
    },
    {
        "example_id": "227_nda-5",
        "gold": "True",
        # Literal: the hypothesis is existential ("may share SOME CI with SOME
        # employees"), the premises are universal permission rules with a
        # five-part proviso. Nothing asserts that any employee or any piece of
        # CI actually exists, nor that the provisos are satisfied.
        "literal": {
            "premises": [
                "∀x ((Employee(x, recipient) ∧ EngagedInRespectOfPurpose(x)) → AuthorisedPerson(x, recipient))",
                "∀x ∀p ((ConfidentialInformation(x) ∧ AuthorisedPerson(p, recipient) ∧ InformedOfDuties(p) ∧ UndertakesSameDuties(p) ∧ WrittenAccountKept(p)) → MayDisclose(recipient, x, p))",
            ],
            "conclusion": "∃x ∃p (ConfidentialInformation(x) ∧ Employee(p, recipient) ∧ MayDisclose(recipient, x, p))",
        },
        # Charitable: provisos treated as procedural side-conditions rather
        # than antecedents, and the hypothesis's "some ... some" read as a
        # permission schema rather than an existence claim.
        "charitable": {
            "premises": [
                "∀x ((Employee(x, recipient) ∧ EngagedInRespectOfPurpose(x)) → AuthorisedPerson(x, recipient))",
                "∀x ∀p ((ConfidentialInformation(x) ∧ AuthorisedPerson(p, recipient)) → MayDisclose(recipient, x, p))",
            ],
            "conclusion": "∀x ∀p ((ConfidentialInformation(x) ∧ Employee(p, recipient) ∧ EngagedInRespectOfPurpose(p)) → MayDisclose(recipient, x, p))",
        },
        "blocker": "existential_hypothesis + unsatisfied_provisos",
    },
    {
        "example_id": "23_nda-10",
        "gold": "True",
        # Both evidence spans are pure DEFINITIONS of "Confidential
        # Information". The obligation the hypothesis asserts ("shall not
        # disclose") is stated elsewhere in the NDA and is simply absent from
        # the annotated evidence spans. No convention can recover it.
        "literal": {
            "premises": [
                "∀x ((RelatingToProject(x) ∧ SuppliedByDiscloser(x)) → ConfidentialInformation(x))",
                "∀x (DiscussionsAndNegotiationsRelatingToProject(x) → ConfidentialInformation(x))",
            ],
            "conclusion": "∀x (FactThatAgreementWasNegotiated(x) → ¬MayDisclose(receivingParty, x))",
        },
        "charitable": {
            "premises": [
                "∀x ((RelatingToProject(x) ∧ SuppliedByDiscloser(x)) → ConfidentialInformation(x))",
                "∀x (DiscussionsAndNegotiationsRelatingToProject(x) → ConfidentialInformation(x))",
                "∀x (FactThatAgreementWasNegotiated(x) → DiscussionsAndNegotiationsRelatingToProject(x))",
            ],
            "conclusion": "∀x (FactThatAgreementWasNegotiated(x) → ¬MayDisclose(receivingParty, x))",
        },
        # Injected: the non-disclosure obligation itself, which lives
        # elsewhere in the NDA and is absent from the annotated spans.
        "assumption_augmented": {
            "premises": [
                "∀x ((RelatingToProject(x) ∧ SuppliedByDiscloser(x)) → ConfidentialInformation(x))",
                "∀x (DiscussionsAndNegotiationsRelatingToProject(x) → ConfidentialInformation(x))",
                "∀x (FactThatAgreementWasNegotiated(x) → DiscussionsAndNegotiationsRelatingToProject(x))",
                "∀x (ConfidentialInformation(x) → ¬MayDisclose(receivingParty, x))",
            ],
            "conclusion": "∀x (FactThatAgreementWasNegotiated(x) → ¬MayDisclose(receivingParty, x))",
        },
        "blocker": "obligation_outside_evidence_spans (definition-only premises)",
    },
    {
        "example_id": "30_nda-15",
        "gold": "True",
        # P2 is a sentence FRAGMENT ("4.2 not to confer any rights...") whose
        # subject sits in P1's dangling clause. Literal formalisation keeps the
        # premise's verb ("confer") and the hypothesis's verb ("grant") apart.
        "literal": {
            "premises": [
                "∀x (DisclosedByDisclosingParty(x) → AcknowledgedByReceivingParty(x))",
                "∀x (ConfidentialInformation(x) → ¬ConfersRight(agreement, receivingParty, x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
        },
        "charitable": {
            "premises": [
                "∀x (DisclosedByDisclosingParty(x) → AcknowledgedByReceivingParty(x))",
                "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
        },
        "blocker": "lexical_variation (confer vs grant) + sentence-fragment premise",
    },
    {
        "example_id": "493_nda-15",
        "gold": "True",
        # The premise carries an EXCEPTION ("except for the limited right to
        # use and disclosure as expressly permitted hereunder") that the
        # hypothesis ("shall not grant ANY right") ignores. Under strict formal
        # semantics the gold label is arguably wrong here -- the same class of
        # gold-label drift "Know Your Limits" found when re-annotating
        # ContractNLI (71/400 relabelled).
        "literal": {
            "premises": [
                "∀x ((InformationDisclosedHereunder(x) ∧ ¬ExpresslyPermittedLimitedRight(x)) → ¬GrantsRight(agreement, receivingParty, x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
        },
        "charitable": {
            "premises": [
                "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ¬GrantsRight(agreement, receivingParty, x))",
        },
        "blocker": "dropped_exception_clause (gold-label defensibility question)",
    },
    {
        "example_id": "48_nda-2",
        "gold": "False",
        # To CONTRADICT "CI shall only include technical information" you need
        # a witness: something that is CI and is not technical. The premise
        # says CI includes all commercially valuable information; that some
        # commercially valuable information is non-technical is world
        # knowledge, absent from the text.
        "literal": {
            "premises": [
                "∀x (HasCommercialValue(x) → ConfidentialInformation(x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → TechnicalInformation(x))",
        },
        "charitable": {
            "premises": [
                "∀x (HasCommercialValue(x) → ConfidentialInformation(x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → TechnicalInformation(x))",
        },
        # Injected: the world-knowledge witness the text never supplies.
        "assumption_augmented": {
            "premises": [
                "∀x (HasCommercialValue(x) → ConfidentialInformation(x))",
                "HasCommercialValue(customerList) ∧ ¬TechnicalInformation(customerList)",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → TechnicalInformation(x))",
        },
        "blocker": "needs_world_knowledge_witness (open-world: no non-technical instance assertable)",
    },
    {
        "example_id": "446_nda-5",
        "gold": "False",
        # Contradicting a PERMISSION with a PROHIBITION requires the
        # closed-world assumption that written permission was NOT given.
        # First-order logic is open-world: the prohibition is conditional on
        # the absence of permission, which cannot be asserted.
        "literal": {
            "premises": [
                "∀x ∀p ((ConcerningTradeSecret(x) ∧ Person(p) ∧ ¬PriorWrittenPermission(navidec)) → ¬MayDisclose(recipient, x, p))",
            ],
            "conclusion": "∃x ∃p (ConfidentialInformation(x) ∧ Employee(p, recipient) ∧ MayDisclose(recipient, x, p))",
        },
        # Charitable: align CI == trade-secret information, add the lexical
        # axiom that an employee is a person. The permission gap remains.
        "charitable": {
            "premises": [
                "∀x ∀p ((ConfidentialInformation(x) ∧ Person(p) ∧ ¬PriorWrittenPermission(navidec)) → ¬MayDisclose(recipient, x, p))",
                "∀p (Employee(p, recipient) → Person(p))",
            ],
            "conclusion": "∃x ∃p (ConfidentialInformation(x) ∧ Employee(p, recipient) ∧ MayDisclose(recipient, x, p))",
        },
        # Injected: the closed-world assumption that no prior written
        # permission was given, plus witnesses for the existentials.
        "assumption_augmented": {
            "premises": [
                "∀x ∀p ((ConfidentialInformation(x) ∧ Person(p) ∧ ¬PriorWrittenPermission(navidec)) → ¬MayDisclose(recipient, x, p))",
                "∀p (Employee(p, recipient) → Person(p))",
                "¬PriorWrittenPermission(navidec)",
                "ConfidentialInformation(tradeSecretDoc) ∧ Employee(alice, recipient)",
            ],
            "conclusion": "∃x ∃p (ConfidentialInformation(x) ∧ Employee(p, recipient) ∧ MayDisclose(recipient, x, p))",
        },
        "blocker": "open_world_permission_gap (¬PriorWrittenPermission not assertable)",
    },
    {
        "example_id": "46_nda-2",
        "gold": "False",
        # Unlike 48_nda-2, this premise explicitly enumerates non-technical
        # categories (customer, financial, personnel information), so a
        # charitable annotator can supply the ontological axiom that financial
        # information is not technical information and get a real witness.
        "literal": {
            "premises": [
                "∀x ((ConfidentialOrProprietary(x) ∧ DisclosedByDisclosingParty(x)) → ConfidentialInformation(x))",
                "ConfidentialInformation(customerInformation) ∧ ConfidentialInformation(financialInformation) ∧ ConfidentialInformation(personnelInformation)",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → TechnicalInformation(x))",
        },
        "charitable": {
            "premises": [
                "∀x ((ConfidentialOrProprietary(x) ∧ DisclosedByDisclosingParty(x)) → ConfidentialInformation(x))",
                "ConfidentialInformation(customerInformation) ∧ ConfidentialInformation(financialInformation) ∧ ConfidentialInformation(personnelInformation)",
                "¬TechnicalInformation(financialInformation)",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → TechnicalInformation(x))",
        },
        "blocker": "needs_ontological_axiom (financial information is not technical information)",
    },
    {
        "example_id": "564_nda-1",
        "gold": "False",
        # "whether or not such information is marked 'confidential'" scopes a
        # definition; it does not assert that unmarked confidential
        # information exists. Contradicting "all CI shall be expressly
        # identified" needs exactly that existence claim.
        "literal": {
            "premises": [
                "∀x (ProvidedToInvestorByCompany(x) → EvaluationMaterial(x))",
                "∀x ((EvaluationMaterial(x) ∧ ¬MarkedConfidential(x)) → EvaluationMaterial(x))",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ExpresslyIdentifiedByDisclosingParty(x))",
        },
        # Charitable: align Evaluation Material == Confidential Information and
        # read "whether or not marked" as asserting an unmarked instance --
        # which is a genuine over-reading, flagged as such.
        "charitable": {
            "premises": [
                "∀x (EvaluationMaterial(x) → ConfidentialInformation(x))",
                "EvaluationMaterial(oralDisclosure) ∧ ¬ExpresslyIdentifiedByDisclosingParty(oralDisclosure)",
            ],
            "conclusion": "∀x (ConfidentialInformation(x) → ExpresslyIdentifiedByDisclosingParty(x))",
        },
        "blocker": "definition_scope_read_as_existence_claim",
    },
]


CONVENTIONS = ("literal", "charitable", "assumption_augmented")


def run(timeout: int = 30) -> dict:
    rows = []
    for case in PROBE:
        row = {"example_id": case["example_id"], "gold": case["gold"],
               "blocker": case["blocker"]}
        for convention in CONVENTIONS:
            # Cases the charitable convention already derives need no injected
            # assumption -- assumption_augmented only ADDS premises, so it
            # defaults to the charitable formalisation where none was needed.
            spec = case.get(convention) or case["charitable"]
            try:
                res = check_entailment(spec["premises"], spec["conclusion"], timeout=timeout)
                predicted = res.label
                err = None
            except Exception as e:  # malformed hand-written FOL is OUR bug
                predicted, err = None, f"{type(e).__name__}: {e}"
            row[convention] = {
                "predicted": predicted,
                "match": predicted == case["gold"],
                "error": err,
            }
        rows.append(row)
        print(f"{row['example_id']:>14}  gold={case['gold']:<5} "
              f"literal={str(row['literal']['predicted']):<10} "
              f"charitable={str(row['charitable']['predicted']):<10} "
              f"+assumptions={str(row['assumption_augmented']['predicted']):<10} "
              f"[{case['blocker']}]")
        for conv in CONVENTIONS:
            if row[conv]["error"]:
                print(f"                 !! {conv} FOL rejected by grounder: {row[conv]['error'][:160]}")

    n = len(rows)
    counts = {c: sum(r[c]["match"] for r in rows) for c in CONVENTIONS}
    print(f"\n=== ContractNLI hand-formalisation ceiling probe (n={n}) ===")
    for c in CONVENTIONS:
        k = counts[c]
        lo, hi = _clopper_pearson(k, n)
        print(f"{c:<22} {k}/{n} ({k / n:.0%})  95% CI [{lo:.0%}, {hi:.0%}]")
    # n=10 is small and the intervals say so -- printed rather than left for a
    # reader to work out, because the point estimate alone would overstate what
    # this probe establishes.
    lo70 = binom.cdf(counts["charitable"], n, 0.70)
    print(f"\nP(observing <= {counts['charitable']}/{n} | true ceiling = 70%) = {lo70:.2f}")
    print("Compare FOLIO's Phase 2.1 gold-FOL ceiling: 81.1% (excluding malformed gold FOL).")
    print("Phase 2's pre-registered gate: <70% ceiling => do not interpret downstream")
    print("silent-failure numbers from this dataset as translation quality.")
    print("\nWHAT THIS PROBE DOES AND DOES NOT ESTABLISH, at this n:")
    print("  - The LITERAL convention clears the gate decisively (CI upper bound well")
    print("    below 70%): evidence-span premises taken at face value essentially never")
    print("    entail the gold label.")
    print("  - The CHARITABLE point estimate sits below the gate, but n is too small to")
    print("    REJECT a true 70% ceiling. Do not write 'the gate fires' for this arm --")
    print("    write the point estimate with its interval.")
    print("  - The five blockers are an existence proof, not a rate estimate, and do not")
    print("    depend on n: each is a demonstrated case where a CORRECT formalisation")
    print("    still fails to derive the gold label.")
    print("The spread across conventions is the point: on ContractNLI the ceiling is set")
    print("by the annotation convention, not by the dataset -- so the convention must be")
    print("pre-registered before the pilot, not chosen after seeing model output.")

    out = PROJECT_ROOT / "experiments" / "logs" / "contractnli_ceiling_probe.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "n": n,
        "matches": counts,
        "provenance": "Claude hand formalisation, NOT an independent human's -- feasibility probe only",
        "rows": rows,
    }
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out}")
    return summary


if __name__ == "__main__":
    run()
