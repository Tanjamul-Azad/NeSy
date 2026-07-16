"""FOLIO loader (Phase 1.2).

Do not assume the upstream schema — `tasksource/folio` has changed shape
before between dataset versions. `EXPECTED_FIELDS` is checked on every load
so a silent schema drift fails loudly instead of quietly corrupting every
downstream number.

Confirmed schema as of 2026-07-16 (train=1001, validation=203 rows):
    story_id: int, example_id: int
    premises: str            -- premises joined by "\n"
    premises-FOL: str        -- one gold FOL formula per line, aligned with premises
    conclusion: str
    conclusion-FOL: str
    label: str                -- "True" / "False" / "Uncertain"
"""

from dataclasses import dataclass
from typing import List, Optional

from datasets import load_dataset

EXPECTED_FIELDS = {
    "story_id",
    "example_id",
    "premises",
    "premises-FOL",
    "conclusion",
    "conclusion-FOL",
    "label",
}


@dataclass
class LogicExample:
    """Common schema shared across FOLIO / ProofWriter / PrOntoQA loaders."""

    source: str
    story_id: str
    example_id: str
    premises: List[str]
    conclusion: str
    label: str
    has_gold_fol: bool
    premises_fol: Optional[List[str]] = None
    conclusion_fol: Optional[str] = None


def _split_lines(text: str) -> List[str]:
    # Some FOLIO rows have leading/trailing blank lines (confirmed 2026-07-16,
    # e.g. example_id 996 and 1142) that are pure formatting artifacts, not
    # missing premises/FOL — filter them rather than let them shift alignment.
    return [line.strip() for line in text.split("\n") if line.strip()]


def _to_example(row: dict) -> LogicExample:
    premises = _split_lines(row["premises"])
    premises_fol = _split_lines(row["premises-FOL"])
    if len(premises) != len(premises_fol):
        raise ValueError(
            f"premises/premises-FOL line-count mismatch for example_id="
            f"{row['example_id']}: {len(premises)} vs {len(premises_fol)} "
            f"-- this is a genuine content mismatch, not the blank-line "
            f"artifact already filtered above. Needs manual inspection."
        )
    return LogicExample(
        source="FOLIO",
        story_id=str(row["story_id"]),
        example_id=str(row["example_id"]),
        premises=premises,
        premises_fol=premises_fol,
        conclusion=row["conclusion"],
        conclusion_fol=row["conclusion-FOL"],
        label=row["label"],
        has_gold_fol=True,
    )


def load_folio(split: Optional[str] = None):
    """Load FOLIO and convert to the common `LogicExample` schema.

    `split=None` returns a dict of {"train": [...], "validation": [...]}.
    """
    ds = load_dataset("tasksource/folio")

    actual_fields = set(ds["train"].features.keys())
    if not EXPECTED_FIELDS.issubset(actual_fields):
        raise ValueError(
            f"tasksource/folio schema changed. Expected at least "
            f"{EXPECTED_FIELDS}, got {actual_fields}. Update EXPECTED_FIELDS "
            f"and _to_example() before trusting any downstream number."
        )

    splits = [split] if split else list(ds.keys())
    result = {s: [_to_example(row) for row in ds[s]] for s in splits}
    return result if split is None else result[split]


if __name__ == "__main__":
    data = load_folio()
    for split, examples in data.items():
        print(f"{split}: {len(examples)} examples")
    print("first train example premises count:", len(data["train"][0].premises))
