"""PrOntoQA loader (renma/ProntoQA eval subset).

500 examples, open-world (OWA), BINARY labels (True/False only -- no
Unknown). This is the subset Logic-LM and LINC report on.

The binary label space is a feature, not a limitation, for this project: on
FOLIO a gold "Uncertain" can confound the under-determination measurement,
but here gold is never Uncertain, so any Uncertain the grounder returns is
necessarily a translation-induced failure. PrOntoQA therefore gives the
cleanest isolation of the under-determination phenomenon. Its reasoning is
also structurally different from ProofWriter's -- linear syllogistic chains
("Zumpuses are rompuses. Max is a yumpus.") rather than rule application --
which adds genuine diversity rather than a second dataset of the same shape.

See data/loaders/renma_common.py for shared parsing and caveats.
"""

from typing import List

from data.loaders.folio_loader import LogicExample
from data.loaders.renma_common import load_renma

HF_NAME = "renma/ProntoQA"


def load_prontoqa(split: str = "validation") -> List[LogicExample]:
    return load_renma(HF_NAME, source_tag="PrOntoQA", split=split)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    data = load_prontoqa()
    print(f"PrOntoQA: {len(data)} examples")
    from collections import Counter
    print("label dist:", Counter(e.label for e in data))
    e = data[0]
    print(f"\nfirst example_id={e.example_id} story_id={e.story_id} label={e.label} label_space={e.label_space}")
    print(f"premises ({len(e.premises)}):")
    for p in e.premises[:4]:
        print("  -", p)
    print("conclusion:", e.conclusion)
