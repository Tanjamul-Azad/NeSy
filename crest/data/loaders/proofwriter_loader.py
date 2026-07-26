"""ProofWriter loader (renma/ProofWriter eval subset).

600 examples, depth-5, open-world (OWA), 3-way balanced labels
(True/False/Unknown, 200 each). This is the subset Logic-LM and LINC report
on, so prevalence numbers here are directly comparable to that prior work.

See data/loaders/renma_common.py for the shared parsing and the important
caveats (no gold FOL, so no ceiling/strict-prevalence analysis here; OWA is
why classical Prover9 is the correct prover).
"""

from typing import List

from data.loaders.folio_loader import LogicExample
from data.loaders.renma_common import load_renma

HF_NAME = "renma/ProofWriter"


def load_proofwriter(split: str = "validation") -> List[LogicExample]:
    return load_renma(HF_NAME, source_tag="ProofWriter", split=split)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    data = load_proofwriter()
    print(f"ProofWriter: {len(data)} examples")
    from collections import Counter
    print("label dist:", Counter(e.label for e in data))
    e = data[0]
    print(f"\nfirst example_id={e.example_id} story_id={e.story_id} label={e.label} label_space={e.label_space}")
    print(f"premises ({len(e.premises)}):")
    for p in e.premises[:4]:
        print("  -", p)
    print("conclusion:", e.conclusion)
