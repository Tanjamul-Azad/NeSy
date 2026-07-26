"""Assemble every vanilla run into the paper's headline table.

The central result of the multi-dataset study: silent-failure prevalence
and its severity split, as a function of (dataset x model). Reports the
point estimate with a story-clustered bootstrap CI for each cell, so the
table is publication-ready rather than a pile of raw percentages.

Model and dataset come from the payload when present; older FOLIO files
predate those fields, so they are inferred from the filename as a fallback.

Run: python -m crest.evaluation.cross_summary
"""

import json
import re
import sys
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from crest.evaluation.stats import proportion_ci_clustered

# Filename model tags -> readable model name, for files predating the
# payload "model" field.
_MODEL_FROM_TAG = {
    "gpt4o": "gpt-4o", "gpt4omini": "gpt-4o-mini",
    "story": "Llama-3.1-8B",  # the original FOLIO Llama runs
}
_MODEL_ORDER = ["Llama-3.1-8B", "gpt-4o-mini", "gpt-4o"]
_DATASET_ORDER = ["folio", "proofwriter", "prontoqa"]


def _severity(gold, pred, outcome):
    if outcome != "silent_failure":
        return None
    if gold in ("True", "False") and pred == "Uncertain":
        return "under_determination"
    return "wrong_direction"


def _identify(path: Path, payload: dict):
    dataset = payload.get("dataset")
    model = payload.get("model")
    if model in (None, "unknown"):
        model = None
    name = path.name
    if dataset is None:
        m = re.search(r"vanilla_pipeline_(folio|proofwriter|prontoqa)_", name)
        dataset = m.group(1) if m else "folio"
    if model is None:
        for tag, readable in _MODEL_FROM_TAG.items():
            if f"_{tag}_" in name or name.endswith(f"_{tag}.json"):
                model = readable
                break
        model = model or "Llama-3.1-8B"
    return dataset, model


def summarise_file(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    recs = payload["results"]
    dataset, model = _identify(path, payload)

    graded = [r for r in recs if r["outcome"] != "loud_failure"]
    clusters = [r["story_id"] for r in graded]
    correct = [r["outcome"] == "correct" for r in graded]
    silent = [r["outcome"] == "silent_failure" for r in graded]
    wrong = [_severity(r["gold_label"], r["predicted_label"], r["outcome"]) == "wrong_direction"
             for r in graded]
    under = [_severity(r["gold_label"], r["predicted_label"], r["outcome"]) == "under_determination"
             for r in graded]

    def cell(mask):
        p, lo, hi = proportion_ci_clustered(mask, clusters)
        return {"point": p, "lo": lo, "hi": hi}

    return {
        "dataset": dataset, "model": model,
        "file": path.name,
        "n_total": len(recs), "n_gradeable": len(graded),
        "n_stories": len(set(clusters)),
        "loud": sum(r["outcome"] == "loud_failure" for r in recs),
        "accuracy": cell(correct),
        "silent": cell(silent),
        "wrong_direction": cell(wrong),
        "under_determination": cell(under),
    }


def main():
    logs = PROJECT_ROOT / "experiments" / "logs"
    # Only the primary story/few-shot vanilla runs (skip ablations/smoke).
    files = [p for p in logs.glob("vanilla_pipeline_*.json")
             if "zeroshot" not in p.name and "per_premise" not in p.name
             and not re.search(r"_n[1-9]\.json$|_n[1-9][0-9]\.json$", p.name)]  # skip tiny smoke n<100

    rows = []
    for p in sorted(files):
        try:
            rows.append(summarise_file(p))
        except Exception as e:
            print(f"  skip {p.name}: {type(e).__name__}: {e}")

    def sort_key(r):
        d = _DATASET_ORDER.index(r["dataset"]) if r["dataset"] in _DATASET_ORDER else 9
        m = _MODEL_ORDER.index(r["model"]) if r["model"] in _MODEL_ORDER else 9
        return (d, m)

    rows.sort(key=sort_key)

    print("=" * 100)
    print("CAPABILITY x DATASET  --  vanilla silent-failure prevalence (gradeable examples, 95% clustered CI)")
    print("=" * 100)
    hdr = f"{'dataset':12s} {'model':14s} {'n':>5s} {'acc':>16s} {'silent':>16s} {'WRONG_DIR':>16s} {'under_det':>16s}"
    print(hdr)
    print("-" * len(hdr))
    def fmt(c):
        return f"{c['point']:.0%}[{c['lo']:.0%},{c['hi']:.0%}]"
    cur = None
    for r in rows:
        if cur and cur != r["dataset"]:
            print()
        cur = r["dataset"]
        print(f"{r['dataset']:12s} {r['model']:14s} {r['n_gradeable']:5d} "
              f"{fmt(r['accuracy']):>16s} {fmt(r['silent']):>16s} "
              f"{fmt(r['wrong_direction']):>16s} {fmt(r['under_determination']):>16s}")

    out = PROJECT_ROOT / "experiments" / "logs" / "cross_summary.json"
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nwritten {out}")


if __name__ == "__main__":
    main()
