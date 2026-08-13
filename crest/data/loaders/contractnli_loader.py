"""ContractNLI loader -- real Non-Disclosure Agreements, the candidate second
naturalistic dataset (Tanjamul's insight, 2026-08-03: FOLIO is naturalistic
in LANGUAGE but not in DOMAIN; a symbolic-reasoning system is actually needed
for legal/policy text, not Wikipedia-trivia logic puzzles).

Source: Koreeda & Manning, EMNLP Findings 2021, CC BY 4.0.
https://stanfordnlp.github.io/contract-nli/ -- 607 real NDAs, 17 fixed
hypothesis templates applied per document, evidence-span-grounded
Entailment/Contradiction/NotMentioned labels.

NOT redistributed in this repo (65MB zip; CC BY 4.0 permits it, but there is
no reason to bloat the repo when the source is stable and free). Download
locally once:
    curl -o /tmp/contract-nli.zip https://stanfordnlp.github.io/contract-nli/resources/contract-nli.zip
    unzip /tmp/contract-nli.zip -d <CONTRACTNLI_DIR>
then point CONTRACTNLI_DIR (env var or the `data_dir` argument) at the
extracted folder containing train.json/dev.json/test.json.

## Why Entailment/Contradiction only, NotMentioned excluded (current scope)

Checked directly against the actual data (2026-08-03, test.json): evidence
spans are non-empty for 100% of Entailment (968/968) and Contradiction
(220/220) examples, and EMPTY for 100% of NotMentioned examples (903/903).
This is a structural property of the dataset, not a sampling artefact --
NotMentioned means "the document contains no evidence addressing this
hypothesis at all", so there is no natural evidence-span analogue to a
FOLIO premise set for those cases.

Modelling NotMentioned as our "Uncertain" class would require choosing SOME
span selection as pseudo-premises (e.g. the whole document, or a retrieval
step over topically related sentences) -- each choice is a real experimental
design decision with its own confound, and picking one under time pressure
without deciding it deliberately is exactly the kind of under-examined
choice this project's standing instruction (corner cases up front, not
patched after) warns against. **Left as an explicit open decision, not
silently resolved here.** Current loader only emits Entailment (True) and
Contradiction (False) examples -- a binary task, like PrOntoQA, not a 3-way
one. This is a real, known limitation of the current dataset integration
and must be stated as such if used in the paper before the 3-way question is
resolved.

## Structural mapping to LogicExample

- `premises`  = the NL text of the evidence spans Koreeda & Manning's own
                annotators marked as supporting/contradicting the hypothesis
                (their own gold evidence selection, not ours)
- `conclusion` = the hypothesis text (one of 17 fixed templates, e.g. "No
                reverse engineering")
- `label`     = "True" if Entailment, "False" if Contradiction
- `story_id`  = f"{document_id}_{hypothesis_key}" (each (document, hypothesis)
                pair is independent; hypotheses repeat verbatim across
                documents, which the capability-curve code must be aware of
                when computing story-level clustering -- see NOTE below)

## NOTE on clustering for statistics

Unlike FOLIO/ProofWriter/PrOntoQA, ContractNLI's `story_id` here does NOT
group multiple related conclusions under shared premises (each (doc,
hypothesis) pair has its own evidence-span premise set). The natural
non-independence to cluster on instead is DOCUMENT (multiple hypotheses
share the same source NDA and drafting style) and/or HYPOTHESIS TEMPLATE
(the same 17 templates recur verbatim across all 607 documents, so examples
sharing a hypothesis are not independent draws either). Before running
`crest/crest/evaluation/stats.py`'s clustered bootstrap on this dataset,
decide which axis to cluster on (or cluster on both, doubly) -- do not reuse
`story_id` blindly the way FOLIO's loader intends it.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from data.loaders.folio_loader import LogicExample

_LABEL_MAP = {"Entailment": "True", "Contradiction": "False"}


def _load_split(path: Path) -> List[LogicExample]:
    data = json.loads(path.read_text(encoding="utf-8"))
    hyp_defs = data["labels"]  # {hyp_key: {"hypothesis": str, "short_description": str}}

    examples = []
    for doc in data["documents"]:
        spans = doc["spans"]
        text = doc["text"]
        for hyp_key, ann in doc["annotation_sets"][0]["annotations"].items():
            choice = ann["choice"]
            if choice not in _LABEL_MAP:
                continue  # NotMentioned -- see module docstring
            evidence_idx = ann["spans"]
            if not evidence_idx:
                # Should not happen for Entailment/Contradiction per the
                # docstring's verified structural property, but guard rather
                # than assume -- a violated assumption here is exactly the
                # kind of silent corruption this project studies.
                raise ValueError(
                    f"{choice} example with empty evidence spans "
                    f"(doc={doc['id']}, hyp={hyp_key}) -- the no-empty-spans "
                    f"assumption in this loader's docstring no longer holds, "
                    f"update the module docstring and NotMentioned-handling "
                    f"logic before trusting any downstream number."
                )
            premises = [text[spans[i][0]:spans[i][1]].strip() for i in evidence_idx]
            premises = [p for p in premises if p]  # drop any empty spans defensively

            examples.append(LogicExample(
                source="ContractNLI",
                story_id=f"{doc['id']}_{hyp_key}",
                example_id=f"{doc['id']}_{hyp_key}",
                premises=premises,
                conclusion=hyp_defs[hyp_key]["hypothesis"],
                label=_LABEL_MAP[choice],
                has_gold_fol=False,
                premises_fol=None,
                conclusion_fol=None,
            ))
            examples[-1].label_space = ("False", "True")  # binary, like PrOntoQA
    return examples


def load_contractnli(split: str = "test", data_dir: Optional[str] = None) -> List[LogicExample]:
    """`split` in {"train", "dev", "test"} -- NOT the same split names as the
    other loaders ("validation"), because ContractNLI's own release uses
    train/dev/test. Callers going through data/loaders/registry.py's uniform
    `split="validation"` default must pass split="dev" or "test" explicitly
    for this dataset, or the registry needs a per-dataset split-name mapping
    added before this can be wired in there -- not yet done, this loader is
    currently standalone.
    """
    data_dir = data_dir or os.environ.get("CONTRACTNLI_DIR")
    if not data_dir:
        raise RuntimeError(
            "Set CONTRACTNLI_DIR to the extracted contract-nli/ folder "
            "(containing train.json/dev.json/test.json), or pass data_dir=. "
            "Download: https://stanfordnlp.github.io/contract-nli/resources/contract-nli.zip"
        )
    path = Path(data_dir) / f"{split}.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found -- check CONTRACTNLI_DIR and split name")
    return _load_split(path)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    data = load_contractnli(split="test")
    print(f"ContractNLI test split: {len(data)} examples (Entailment/Contradiction only)")
    from collections import Counter
    print("label dist:", Counter(e.label for e in data))
    e = data[0]
    print(f"\nfirst example_id={e.example_id} label={e.label}")
    print(f"premises ({len(e.premises)}):")
    for p in e.premises[:3]:
        print("  -", p[:150])
    print("conclusion:", e.conclusion)
