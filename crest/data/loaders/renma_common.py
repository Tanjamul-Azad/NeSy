"""Shared loader for the renma/* NeSy evaluation subsets (ProofWriter, PrOntoQA).

These are the same curated subsets Logic-LM and LINC evaluate on, which is
the point: reporting on them makes CREST's prevalence numbers directly
comparable to that prior work, instead of on an idiosyncratic split.

Both datasets share one schema:
    id                 str   e.g. "ProofWriter_AttNoneg-OWA-D5-1041_Q1"
    context            str   NL premises, one theory as period-joined sentences
    question           str   "... true, false, or unknown? <STATEMENT>."
    options            list  e.g. ["A) True", "B) False", "C) Unknown"]
    answer             str   the option letter ("A"/"B"/"C")
    raw_logic_programs list  Logic-LM's OWN pseudo-logic DSL (Predicates/Facts/
                             Rules) -- NOT first-order logic, and NOT usable as
                             gold FOL for a Phase-2.1-style ceiling check. We
                             deliberately do not touch it; the LLM translates
                             fresh from `context`/`question` NL exactly as for
                             FOLIO.

Two consequences worth stating plainly, because they shape what can be
measured on these datasets:

1. NO GOLD FOL. FOLIO shipped human-written gold FOL, which Phase 2.1 used to
   establish a grounder ceiling and Phase 3.2 used for the strict-prevalence
   filter. These datasets have none, so those two analyses are FOLIO-only.
   The grounder itself is dataset-agnostic (it runs Prover9 on whatever FOL
   it is handed), so its correctness carries over; what does not carry over
   is a dataset-specific gold-FOL ceiling number. Report raw prevalence
   (Phase 3.1) here, and say so.

2. LABEL SPACE DIFFERS BY DATASET. ProofWriter is 3-way (True/False/Unknown),
   PrOntoQA is binary (True/False). "Unknown" is normalised to "Uncertain"
   to match EntailmentResult's label set. On PrOntoQA, gold is never
   Uncertain, so any Uncertain the grounder returns is necessarily a
   translation-induced failure -- a cleaner isolation of the
   under-determination phenomenon than FOLIO allows, where a gold Uncertain
   can confound it. `label_space` is recorded on every example so downstream
   severity code can branch correctly rather than assume three classes.

All examples use the ProofWriter/PrOntoQA OWA (open-world) configs, which is
why classical Prover9 is the right prover: under OWA, "not provable either
way" genuinely means Unknown, exactly Prover9's behaviour. A CWA
(closed-world, negation-as-failure) split would systematically mismatch a
classical prover and must not be substituted in.
"""

import os
import re
from typing import List

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from datasets import load_dataset

from data.loaders.folio_loader import LogicExample

EXPECTED_FIELDS = {"id", "context", "question", "options", "answer"}

# Option letter -> normalised label. "Unknown" -> "Uncertain" so the label
# set matches EntailmentResult ("True"/"False"/"Uncertain").
_LABEL_NORM = {"true": "True", "false": "False", "unknown": "Uncertain", "uncertain": "Uncertain"}


def _parse_options(options: List[str]) -> dict:
    """["A) True", "B) False", ...] -> {"A": "True", "B": "False", ...},
    labels normalised. Parsed per row rather than hardcoded because the two
    datasets differ (PrOntoQA omits the Unknown option).
    """
    mapping = {}
    for opt in options:
        m = re.match(r"\s*([A-Z])\s*\)\s*(.+?)\s*$", opt)
        if not m:
            raise ValueError(f"unparseable option string: {opt!r}")
        letter, text = m.group(1), m.group(2).strip().lower()
        if text not in _LABEL_NORM:
            raise ValueError(f"unexpected option label {text!r} in {opt!r}")
        mapping[letter] = _LABEL_NORM[text]
    return mapping


def _extract_conclusion(question: str) -> str:
    """The conclusion is the statement after the framing question. Both
    datasets end with "... true or false? <STATEMENT>." Take everything
    after the last "?", which is robust to the two different framings.
    """
    if "?" not in question:
        raise ValueError(f"no '?' in question, cannot locate conclusion: {question!r}")
    conclusion = question.rsplit("?", 1)[1].strip()
    if not conclusion:
        raise ValueError(f"empty conclusion after '?': {question!r}")
    return conclusion


def _split_premises(context: str) -> List[str]:
    """Split the period-joined theory into individual premises.

    These are synthetic, single-clause sentences ("If X and Y then Z.") with
    no internal periods or abbreviations, so a period-boundary split is safe
    here -- unlike general prose. A sentence is kept only if it has content.
    """
    parts = re.split(r"(?<=[.])\s+", context.strip())
    premises = [p.strip() for p in parts if p.strip()]
    if not premises:
        raise ValueError(f"no premises parsed from context: {context[:120]!r}")
    return premises


def load_renma(hf_name: str, source_tag: str, split: str = "validation") -> List[LogicExample]:
    ds = load_dataset(hf_name)
    if split not in ds:
        raise ValueError(f"{hf_name} has no split {split!r}; available: {list(ds.keys())}")
    rows = ds[split]

    actual = set(rows.features.keys())
    if not EXPECTED_FIELDS.issubset(actual):
        raise ValueError(
            f"{hf_name} schema changed. Expected at least {EXPECTED_FIELDS}, "
            f"got {actual}. Update the loader before trusting any number."
        )

    examples = []
    for row in rows:
        opt_map = _parse_options(row["options"])
        letter = row["answer"].strip()
        if letter not in opt_map:
            raise ValueError(
                f"answer letter {letter!r} not among options {opt_map} "
                f"for id={row['id']}"
            )
        label = opt_map[letter]
        # Distinct-sorted label set for this row's dataset, so downstream
        # severity logic can tell a 2-way dataset from a 3-way one.
        label_space = tuple(sorted(set(opt_map.values())))

        ex = LogicExample(
            source=source_tag,
            story_id=str(row["id"]).rsplit("_Q", 1)[0],  # group questions sharing a theory
            example_id=str(row["id"]),
            premises=_split_premises(row["context"]),
            conclusion=_extract_conclusion(row["question"]),
            label=label,
            has_gold_fol=False,
            premises_fol=None,
            conclusion_fol=None,
        )
        # Attach label_space without changing the shared dataclass definition.
        ex.label_space = label_space
        examples.append(ex)

    return examples
