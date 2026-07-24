"""Corner-case tests for the whole-story translation parser.

Runs on CPU with no GPU and no model download -- `parse_story_output` is
deliberately a pure function separated from LlamaHarness for exactly this
reason. Every bug caught here is a Kaggle GPU run not wasted.

Run: python -m pytest tests/test_story_parser.py   (or: python tests/test_story_parser.py)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crest.inference.llama_harness import parse_story_output, StoryFormatError


# --- Outputs that must parse -------------------------------------------------
# The model is instructed to emit "P1: <fol>", but small instruction-tuned
# models drift on surface formatting. Rejecting a semantically fine formula
# over a stray asterisk would inflate the measured loud-failure rate with
# formatting noise that has nothing to do with translation quality.

@pytest.mark.parametrize("name,raw,n,expected_premises,expected_conclusion", [
    ("clean",
     "P1: ∀x (Student(x) → Smart(x))\nP2: Student(john)\nC: Smart(john)",
     2, ["∀x (Student(x) → Smart(x))", "Student(john)"], "Smart(john)"),
    ("markdown fences", "```\nP1: A(x)\nP2: B(x)\nC: C(x)\n```",
     2, ["A(x)", "B(x)"], "C(x)"),
    ("preamble chatter", "Sure! Here are the translations:\n\nP1: A(x)\nP2: B(x)\nC: C(x)",
     2, ["A(x)", "B(x)"], "C(x)"),
    ("dot separators", "P1. A(x)\nP2. B(x)\nC. C(x)", 2, ["A(x)", "B(x)"], "C(x)"),
    ("paren separators", "P1) A(x)\nP2) B(x)\nC) C(x)", 2, ["A(x)", "B(x)"], "C(x)"),
    ("bold labels", "**P1:** A(x)\n**P2:** B(x)\n**C:** C(x)", 2, ["A(x)", "B(x)"], "C(x)"),
    ("bold whole line", "**P1: A(x)**\n**P2: B(x)**\n**C: C(x)**", 2, ["A(x)", "B(x)"], "C(x)"),
    ("lowercase labels", "p1: A(x)\np2: B(x)\nc: C(x)", 2, ["A(x)", "B(x)"], "C(x)"),
    ("blank lines", "P1: A(x)\n\n\nP2: B(x)\n\nC: C(x)", 2, ["A(x)", "B(x)"], "C(x)"),
    ("trailing commentary", "P1: A(x)\nP2: B(x)\nC: C(x)\n\nNote: standard FOL syntax.",
     2, ["A(x)", "B(x)"], "C(x)"),
    # Two-digit labels: FOLIO stories do exceed 9 premises.
    ("ten plus premises",
     "\n".join(f"P{i}: A{i}(x)" for i in range(1, 12)) + "\nC: C(x)",
     11, [f"A{i}(x)" for i in range(1, 12)], "C(x)"),
    # Unicode FOL operators must survive untouched -- the XOR expansion and
    # symbol normalisation downstream depend on them being intact.
    ("xor and negation preserved", "P1: A(x) ⊕ B(x)\nC: ¬C(x)",
     1, ["A(x) ⊕ B(x)"], "¬C(x)"),
])
def test_parses(name, raw, n, expected_premises, expected_conclusion):
    premises, conclusion = parse_story_output(raw, n)
    assert premises == expected_premises
    assert conclusion == expected_conclusion


# --- Outputs that must be REJECTED -------------------------------------------
# These all represent a premise/formula count mismatch. Silently padding or
# truncating here would misalign every premise with the wrong formula and
# corrupt the entailment result invisibly -- the precise class of silent
# failure this project exists to study, so the parser must not commit one.

@pytest.mark.parametrize("name,raw,n", [
    ("missing premise", "P1: A(x)\nC: C(x)", 2),
    ("missing conclusion", "P1: A(x)\nP2: B(x)", 2),
    ("extra premise", "P1: A(x)\nP2: B(x)\nP3: D(x)\nC: C(x)", 2),
    ("duplicate premise", "P1: A(x)\nP1: Z(x)\nP2: B(x)\nC: C(x)", 2),
    ("duplicate conclusion", "P1: A(x)\nP2: B(x)\nC: C(x)\nC: Z(x)", 2),
    ("empty output", "", 2),
    ("refusal / pure prose", "I cannot translate these statements.", 2),
    # Hitting the max_new_tokens ceiling mid-output looks like this. It must
    # fail loudly rather than yield a short-but-plausible premise list.
    ("truncated mid-output", "P1: A(x)\nP2: B(x)\nP3: D(", 5),
])
def test_rejects(name, raw, n):
    with pytest.raises(StoryFormatError):
        parse_story_output(raw, n)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
