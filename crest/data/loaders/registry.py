"""Dataset registry -- one name -> one loader, so every pipeline can run on
any dataset with a `--dataset` flag instead of a hardcoded FOLIO import.

Every loader returns List[LogicExample] with the same schema, so downstream
code (translation, grounding, classification, metrics) is dataset-agnostic.
The only per-dataset branch is the label space (2-way vs 3-way), carried on
each example as `.label_space` and handled in the severity metrics.
"""

from data.loaders.folio_loader import load_folio
from data.loaders.proofwriter_loader import load_proofwriter
from data.loaders.prontoqa_loader import load_prontoqa
from data.loaders.contractnli_loader import load_contractnli

LOADERS = {
    "folio": load_folio,
    "proofwriter": load_proofwriter,
    "prontoqa": load_prontoqa,
    "contractnli": load_contractnli,
}

# ContractNLI's own release names its splits train/dev/test, not
# train/validation. Rather than let a caller's `split="validation"` silently
# fail (or, worse, silently load the wrong split), translate it explicitly
# here. Everything else passes through unchanged, so `split="test"` still
# reaches the loader as "test".
SPLIT_ALIASES = {
    "contractnli": {"validation": "dev"},
}


def load_dataset_by_name(name: str, split: str = "validation"):
    if name not in LOADERS:
        raise ValueError(f"unknown dataset {name!r}; choices: {sorted(LOADERS)}")
    split = SPLIT_ALIASES.get(name, {}).get(split, split)
    data = LOADERS[name](split=split)
    # FOLIO examples predate label_space; default them to the 3-way set so
    # downstream severity code can assume the attribute always exists.
    for ex in data:
        if not hasattr(ex, "label_space"):
            ex.label_space = ("False", "True", "Uncertain")
    return data
