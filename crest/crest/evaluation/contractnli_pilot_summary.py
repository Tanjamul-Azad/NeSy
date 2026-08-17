"""Step 5: assemble the ContractNLI pilot runs into a reportable table.

Deliberately NOT folded into cross_summary.py. That module's assumptions are
FOLIO-shaped and every one of them is wrong here:

  - it clusters on `story_id`, which for ContractNLI is unique per example
    and therefore clusters nothing (the real axes are the source NDA and the
    hypothesis template -- see contractnli_loader.py);
  - it reports accuracy with no majority-class baseline, which is harmless at
    FOLIO's 35.5% and actively misleading at ContractNLI's 81.5%;
  - it says nothing about a ceiling, and ContractNLI's ceiling is the whole
    story (0% literal / 60% charitable / 100% assumption-augmented, per
    contractnli_ceiling_probe.py).

Reporting rules enforced here, per the pre-registration in
docs/RESEARCH_DIRECTION.md (written before any model output existed):

  1. Every accuracy figure is printed beside the majority-class baseline and
     the charitable-convention ceiling. An accuracy of 60% on this dataset
     means something completely different from 60% on FOLIO.
  2. Confidence intervals are bootstrapped twice -- clustered by document and
     clustered by hypothesis template -- and the WIDER interval is reported.
     Picking the narrower one after seeing both would be exactly the kind of
     analytic freedom the project's pre-registration discipline exists to
     remove.
  3. `Uncertain` is always a failure here (the task is binary) and always
     counts as under_determination, never as wrong_direction.
  4. Model-vs-model comparisons use McNemar exact on the paired examples,
     never a bare difference of percentages.

Run: python -m crest.evaluation.contractnli_pilot_summary
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from crest.evaluation.stats import mcnemar_exact, proportion_ci_clustered

# From contractnli_ceiling_probe.py -- what a CORRECT formalisation scores.
# The intervals are carried alongside the point estimates deliberately: at
# n=10 the charitable arm's CI is [26%, 88%], which cannot reject a true 70%
# ceiling, and a bare "60%" printed next to model results would imply a
# precision this probe does not have.
CEILING = {"literal": 0.00, "charitable": 0.60, "assumption_augmented": 1.00}
CEILING_CI = {"literal": (0.00, 0.31), "charitable": (0.26, 0.88),
              "assumption_augmented": (0.69, 1.00)}
PRIMARY_CEILING = "charitable"

_MODEL_ORDER = ["Llama-3.1-8B", "gpt-4o-mini", "gpt-4o"]


def _model_of(payload: dict, path: Path) -> str:
    model = payload.get("model") or ""
    if "Llama" in model:
        return "Llama-3.1-8B"
    if model in _MODEL_ORDER:
        return model
    for tag, readable in (("gpt4omini", "gpt-4o-mini"), ("gpt4o", "gpt-4o"),
                          ("story", "Llama-3.1-8B")):
        if f"_{tag}_" in path.name or path.name.endswith(f"_{tag}.json"):
            return readable
    return model or path.stem


def _severity(rec: dict):
    """Binary task: a well-formed prediction that is not the gold label is
    either an assertion of the opposite (wrong_direction) or a failure to
    decide at all (under_determination). `Uncertain` is always the latter.
    """
    if rec["outcome"] != "silent_failure":
        return None
    return "under_determination" if rec["predicted_label"] == "Uncertain" else "wrong_direction"


def _both_cluster_ci(mask, recs):
    """Return the WIDER of the document-clustered and hypothesis-clustered
    interval, plus which axis produced it -- see reporting rule 2.
    """
    docs = [r.get("cluster_id") or r["story_id"] for r in recs]
    hyps = [r.get("hypothesis_id") or r["story_id"] for r in recs]
    p, lo_d, hi_d = proportion_ci_clustered(mask, docs)
    _, lo_h, hi_h = proportion_ci_clustered(mask, hyps)
    if (hi_h - lo_h) > (hi_d - lo_d):
        return p, lo_h, hi_h, "hypothesis"
    return p, lo_d, hi_d, "document"


def summarise_file(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    recs = payload["results"]
    graded = [r for r in recs if r["outcome"] != "loud_failure"]

    gold = [r["gold_label"] for r in recs]
    majority = max(gold.count("True"), gold.count("False")) / len(recs)

    correct = [r["outcome"] == "correct" for r in graded]
    silent = [r["outcome"] == "silent_failure" for r in graded]
    under = [_severity(r) == "under_determination" for r in graded]
    wrong = [_severity(r) == "wrong_direction" for r in graded]

    acc, acc_lo, acc_hi, acc_axis = _both_cluster_ci(correct, graded)
    sil, sil_lo, sil_hi, sil_axis = _both_cluster_ci(silent, graded)

    pred_dist = {}
    for r in recs:
        pred_dist[str(r["predicted_label"])] = pred_dist.get(str(r["predicted_label"]), 0) + 1

    # Accuracy split by gold label: with 82/18 imbalance an aggregate number
    # hides whether a model is simply never proving anything.
    by_gold = {}
    for lab in ("True", "False"):
        sub = [r for r in graded if r["gold_label"] == lab]
        by_gold[lab] = {
            "n": len(sub),
            "accuracy": (sum(r["outcome"] == "correct" for r in sub) / len(sub)) if sub else None,
        }

    return {
        "file": path.name,
        "model": _model_of(payload, path),
        "n_total": len(recs),
        "n_gradeable": len(graded),
        "n_documents": len({r.get("cluster_id") or r["story_id"] for r in recs}),
        "n_hypotheses": len({r.get("hypothesis_id") or r["story_id"] for r in recs}),
        "loud": sum(r["outcome"] == "loud_failure" for r in recs),
        "majority_baseline": majority,
        "accuracy": {"point": acc, "lo": acc_lo, "hi": acc_hi, "cluster_axis": acc_axis},
        "silent": {"point": sil, "lo": sil_lo, "hi": sil_hi, "cluster_axis": sil_axis},
        "under_determination": sum(under) / len(graded) if graded else 0.0,
        "wrong_direction": sum(wrong) / len(graded) if graded else 0.0,
        "prediction_distribution": pred_dist,
        "accuracy_by_gold_label": by_gold,
        "_records": {r["example_id"]: r for r in recs},
    }


def compare(a: dict, b: dict) -> dict:
    """Paired McNemar between two models over their shared example ids."""
    shared = sorted(set(a["_records"]) & set(b["_records"]))
    if not shared:
        return {"n_paired": 0}
    a_ok = [a["_records"][i]["outcome"] == "correct" for i in shared]
    b_ok = [b["_records"][i]["outcome"] == "correct" for i in shared]
    a_quiet = [a["_records"][i]["outcome"] != "silent_failure" for i in shared]
    b_quiet = [b["_records"][i]["outcome"] != "silent_failure" for i in shared]
    return {
        "n_paired": len(shared),
        "accuracy": mcnemar_exact(a_ok, b_ok),
        "not_silent": mcnemar_exact(a_quiet, b_quiet),
    }


def main():
    logs = PROJECT_ROOT / "experiments" / "logs"
    files = sorted(logs.glob("vanilla_pipeline_contractnli_*.json"))
    # Smoke runs (n<50) exist to check plumbing, not to be reported.
    files = [p for p in files if not any(p.name.endswith(f"_n{k}.json") for k in range(1, 50))]

    if not files:
        print("No ContractNLI pilot runs found in experiments/logs/.")
        print("Expected: vanilla_pipeline_contractnli_<model>_test_n100.json")
        print("Run the pilot first -- see docs/RESEARCH_DIRECTION.md step 5.")
        return

    rows = [summarise_file(p) for p in files]
    rows.sort(key=lambda r: _MODEL_ORDER.index(r["model"]) if r["model"] in _MODEL_ORDER else 99)

    ceil = CEILING[PRIMARY_CEILING]
    print("=" * 78)
    print("ContractNLI pilot — real NDAs, evidence-span premises, binary True/False")
    print("=" * 78)
    clo, chi = CEILING_CI[PRIMARY_CEILING]
    print(f"CEILING (hand formalisation, {PRIMARY_CEILING} convention): {ceil:.0%}"
          f"  95% CI [{clo:.0%}, {chi:.0%}]  (n=10)")
    print(f"   other conventions: literal {CEILING['literal']:.0%} "
          f"[{CEILING_CI['literal'][0]:.0%}, {CEILING_CI['literal'][1]:.0%}] / "
          f"assumption-augmented {CEILING['assumption_augmented']:.0%} "
          f"[{CEILING_CI['assumption_augmented'][0]:.0%}, "
          f"{CEILING_CI['assumption_augmented'][1]:.0%}]")
    print("Read every accuracy below against that ceiling and the majority baseline,")
    print("NOT against 100% and NOT against the FOLIO numbers. The charitable ceiling's")
    print("interval is wide enough that it cannot reject a true 70% ceiling -- treat it")
    print("as indicative, and lean on the blocker taxonomy for the qualitative claim.\n")

    for r in rows:
        print(f"--- {r['model']}  ({r['file']})")
        print(f"    n={r['n_total']}  gradeable={r['n_gradeable']}  loud={r['loud']}  "
              f"docs={r['n_documents']}  hypotheses={r['n_hypotheses']}")
        a = r["accuracy"]
        print(f"    accuracy            {a['point']:.1%}  95% CI [{a['lo']:.1%}, {a['hi']:.1%}]"
              f"  ({a['cluster_axis']}-clustered, wider of the two)")
        print(f"      majority baseline {r['majority_baseline']:.1%}   ceiling {ceil:.0%}"
              f"   -> {'ABOVE' if a['point'] > r['majority_baseline'] else 'AT OR BELOW'} baseline")
        s = r["silent"]
        print(f"    silent failure      {s['point']:.1%}  95% CI [{s['lo']:.1%}, {s['hi']:.1%}]"
              f"  ({s['cluster_axis']}-clustered)")
        print(f"      under_determination {r['under_determination']:.1%}"
              f"   wrong_direction {r['wrong_direction']:.1%}")
        bl = r["accuracy_by_gold_label"]
        for lab in ("True", "False"):
            acc = bl[lab]["accuracy"]
            print(f"      gold={lab:<5} n={bl[lab]['n']:<4} accuracy="
                  f"{'n/a' if acc is None else f'{acc:.1%}'}")
        print(f"    predictions: {r['prediction_distribution']}")
        print()

    if len(rows) > 1:
        print("PAIRED MODEL COMPARISONS (McNemar exact, shared examples only)")
        for i in range(len(rows) - 1):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                c = compare(a, b)
                if not c["n_paired"]:
                    continue
                print(f"  {a['model']} vs {b['model']}  (n={c['n_paired']})")
                print(f"    accuracy:  {c['accuracy'].summary()}")
                print(f"    not-silent:{c['not_silent'].summary()}")
        print()

    print("PRE-REGISTERED READING (docs/RESEARCH_DIRECTION.md, fixed before these runs):")
    print("  If under-determination dominates for all models and the model gap is")
    print("  small, the conclusion is 'the capability x language-type interaction")
    print("  CANNOT BE TESTED on ContractNLI-as-FOL' -- not 'the gap does not")
    print("  replicate on legal text'. A floor effect does not license the second claim.")
    print(f"  Any model scoring meaningfully above the {ceil:.0%} ceiling falsifies the")
    print("  hand formalisation, which then gets redone rather than kept.")

    out = logs / "contractnli_pilot_summary.json"
    for r in rows:
        r.pop("_records", None)
    out.write_text(json.dumps({"ceiling": CEILING, "rows": rows}, indent=2,
                              ensure_ascii=False, default=str), encoding="utf-8")
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
