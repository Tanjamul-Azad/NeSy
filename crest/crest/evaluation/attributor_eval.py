"""P-A gate: does the attributor actually discriminate, or just fire a lot?

Evaluates CREST-D's two signals against every committed run. The results files
store only the FOL, so the source sentences are re-joined from the datasets by
example_id -- no new model calls, no GPU, no API cost.

THE METRIC THAT MATTERS, AND WHY IT IS NOT ACCURACY
===================================================
A detector that flags 90% of everything would "catch" 90% of silent failures
and be worthless. So the number to read is not recall, and not precision on
its own, but **lift**: how much higher is the silent-failure rate among flagged
examples than the base rate in the same cell?

  lift = P(silent | flagged) / P(silent)

lift = 1.0 means the signal carries no information whatever its recall looks
like. This is the same discipline the confidence-detector negative result was
held to (AUROC 0.49 on FOLIO x gpt-4o-mini, reported as a failure rather than
buried), and signal 2 is held to it here before anything is built on top.

Reported per dataset x model, plus each signal alone and both combined, so a
weak signal cannot hide inside the union.

P-A's pre-registered gate (docs/RESEARCH_DIRECTION.md 3.96): coverage on FOLIO
must exceed ~25% for the framework to address a meaningful share. Signal 1
alone reached 11.3% pooled.

Run: python -m crest.evaluation.attributor_eval
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from crest.detection import predicate_checker, structural_diff

_DATASET_SPLIT = {
    "folio": ("folio", "validation"),
    "proofwriter": ("proofwriter", "validation"),
    "prontoqa": ("prontoqa", "validation"),
    "contractnli": ("contractnli", "test"),
}

_NL_CACHE = {}


def nl_index(dataset: str):
    """example_id -> (premises_nl, conclusion_nl), loaded once per dataset."""
    if dataset in _NL_CACHE:
        return _NL_CACHE[dataset]
    from data.loaders.registry import load_dataset_by_name
    name, split = _DATASET_SPLIT[dataset]
    data = load_dataset_by_name(name, split=split)
    _NL_CACHE[dataset] = {str(e.example_id): (e.premises, e.conclusion) for e in data}
    return _NL_CACHE[dataset]


def _dataset_of(payload, path):
    d = payload.get("dataset")
    if d:
        return d
    m = re.search(r"vanilla_pipeline_(folio|proofwriter|prontoqa|contractnli)_", path.name)
    return m.group(1) if m else "folio"


def _model_of(payload, path):
    m = payload.get("model") or ""
    if "Llama" in m:
        return "Llama-3.1-8B"
    if m and m != "unknown":
        return m
    for tag, readable in (("gpt4omini", "gpt-4o-mini"), ("gpt4o", "gpt-4o"),
                          ("story", "Llama-3.1-8B")):
        if f"_{tag}_" in path.name:
            return readable
    return "Llama-3.1-8B"


def evaluate(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    dataset = _dataset_of(payload, path)
    idx = nl_index(dataset)

    rows = []
    for r in payload["results"]:
        conc_fol = r.get("translated_conclusion")
        if not conc_fol:
            continue  # unparseable output: no formula exists to inspect
        nl = idx.get(str(r["example_id"]))
        if nl is None:
            continue  # example not in the current split (should not happen)
        prem_nl, conc_nl = nl
        prem_fol = r.get("translated_premises") or []
        if len(prem_nl) != len(prem_fol):
            # Misalignment would compare a sentence against another
            # sentence's formula, manufacturing mismatches. Skip rather
            # than silently produce a wrong signal.
            continue

        s1 = predicate_checker.check(prem_fol, conc_fol)
        s2 = structural_diff.check(prem_nl, prem_fol, conc_nl, conc_fol)
        rows.append({
            "silent": r["outcome"] == "silent_failure",
            "sig1": s1.predicted_outcome != "no_reachability_objection",
            "sig2": s2.flagged,
            "kinds": s2.kinds,
        })

    def stats(mask_key):
        flagged = [x for x in rows if x[mask_key]]
        silent = [x for x in rows if x["silent"]]
        if not rows:
            return None
        base = len(silent) / len(rows)
        prec = (sum(x["silent"] for x in flagged) / len(flagged)) if flagged else None
        rec = (sum(x[mask_key] for x in silent) / len(silent)) if silent else None
        return {
            "flag_rate": len(flagged) / len(rows),
            "precision": prec,
            "recall": rec,
            "base_rate": base,
            "lift": (prec / base) if (prec is not None and base) else None,
        }

    both = [dict(x, both=(x["sig1"] or x["sig2"])) for x in rows]
    rows_both = both
    flagged_both = [x for x in rows_both if x["both"]]
    silent_all = [x for x in rows_both if x["silent"]]
    base = (len(silent_all) / len(rows_both)) if rows_both else 0
    prec_both = (sum(x["silent"] for x in flagged_both) / len(flagged_both)) if flagged_both else None

    kind_counts = {}
    for x in rows:
        for k in x["kinds"]:
            kind_counts[k] = kind_counts.get(k, 0) + 1

    return {
        "dataset": dataset, "model": _model_of(payload, path), "file": path.name,
        "n_analysable": len(rows),
        "sig1": stats("sig1"), "sig2": stats("sig2"),
        "combined": {
            "flag_rate": (len(flagged_both) / len(rows_both)) if rows_both else None,
            "precision": prec_both,
            "recall": (sum(x["both"] for x in silent_all) / len(silent_all)) if silent_all else None,
            "base_rate": base,
            "lift": (prec_both / base) if (prec_both is not None and base) else None,
        },
        "mismatch_kinds": kind_counts,
    }


RULES = ["quantifier_missing", "quantifier_substituted", "negation_parity",
         "conditional_lost", "exclusivity_lost"]


def per_rule(files):
    """Lift of each structural rule on its own.

    The aggregate signal 2 turned out uninformative (lift ~1.0). Averaging
    rules together can hide an informative one inside several noisy ones, so
    each is measured separately before the module is judged -- decompose
    before discarding.
    """
    pool, totals = {}, {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        ds = _dataset_of(payload, path)
        try:
            idx = nl_index(ds)
        except Exception:
            continue
        for r in payload["results"]:
            cf = r.get("translated_conclusion")
            if not cf:
                continue
            nl = idx.get(str(r["example_id"]))
            if nl is None:
                continue
            prem_nl, conc_nl = nl
            prem_fol = r.get("translated_premises") or []
            if len(prem_nl) != len(prem_fol):
                continue
            silent = r["outcome"] == "silent_failure"
            t = totals.setdefault(ds, [0, 0])
            t[0] += silent
            t[1] += 1
            kinds = set(structural_diff.check(prem_nl, prem_fol, conc_nl, cf).kinds)
            for k in kinds:
                c = pool.setdefault((ds, k), [0, 0])
                c[0] += silent
                c[1] += 1
    return pool, totals


def print_per_rule(pool, totals):
    print()
    print("=" * 82)
    print("PER-RULE lift -- does any single rule carry information the aggregate hides?")
    print("=" * 82)
    print(f"{'dataset':<13} {'rule':<24} {'fires':>6} {'fire%':>7} {'prec':>7} {'base':>7} {'lift':>6}")
    print("-" * 82)
    out = []
    for ds in sorted(totals):
        s_, n_ = totals[ds]
        base = s_ / n_ if n_ else 0
        for k in RULES:
            c = pool.get((ds, k))
            if not c or not c[1]:
                continue
            prec = c[0] / c[1]
            lift = prec / base if base else float("nan")
            print(f"{ds:<13} {k:<24} {c[1]:>6} {c[1]/n_:>6.1%} {prec:>6.1%} {base:>6.1%} {lift:>6.2f}")
            out.append({"dataset": ds, "rule": k, "fires": c[1], "fire_rate": c[1]/n_,
                        "precision": prec, "base_rate": base, "lift": lift})
        print()
    return out


def main():
    logs = PROJECT_ROOT / "experiments" / "logs"
    files = [p for p in sorted(logs.glob("vanilla_pipeline_*.json"))
             if "zeroshot" not in p.name and "per_premise" not in p.name
             and not re.search(r"_n[1-9]\.json$", p.name)]

    rows = []
    for p in files:
        try:
            r = evaluate(p)
            if r["n_analysable"] >= 50:
                rows.append(r)
        except Exception as e:
            print(f"  skip {p.name}: {type(e).__name__}: {e}")

    print("=" * 104)
    print("CREST-D attributor: discrimination, not just firing (lift = precision / base rate)")
    print("=" * 104)
    print(f"{'dataset':<12} {'model':<14} {'n':>5} {'base':>6} | "
          f"{'s1 rec':>7} {'s1 lift':>8} | {'s2 rec':>7} {'s2 lift':>8} | "
          f"{'BOTH rec':>9} {'lift':>6} {'flag%':>7}")
    print("-" * 104)

    def f(x, pct=True):
        if x is None:
            return "   n/a"
        return f"{x:6.1%}" if pct else f"{x:6.2f}"

    for r in rows:
        c, s1, s2 = r["combined"], r["sig1"], r["sig2"]
        print(f"{r['dataset']:<12} {r['model']:<14} {r['n_analysable']:>5} "
              f"{f(c['base_rate'])} | {f(s1['recall'])} {f(s1['lift'], False):>8} | "
              f"{f(s2['recall'])} {f(s2['lift'], False):>8} | "
              f"{f(c['recall']):>9} {f(c['lift'], False)} {f(c['flag_rate'])}")

    folio = [r for r in rows if r["dataset"] == "folio"]
    if folio:
        cov = sum(r["combined"]["recall"] * 1 for r in folio) / len(folio)
        print("-" * 104)
        print(f"P-A GATE: mean FOLIO coverage (both signals) = {cov:.1%} "
              f"-- gate is ~25%: {'PASS' if cov >= 0.25 else 'FAIL'}")

    agg = {}
    for r in rows:
        for k, v in r["mismatch_kinds"].items():
            agg[k] = agg.get(k, 0) + v
    print("\nStructural mismatch kinds fired (all runs):")
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]):
        print(f"   {v:>6}  {k}")

    pool, totals = per_rule(files)
    rule_rows = print_per_rule(pool, totals)
    print("READING: rules with real lift fire RARELY and only on synthetic, templated")
    print("text (PrOntoQA, ProofWriter). On naturalistic text they fire constantly and")
    print("their lift collapses to ~1.0 -- the same shape as the confidence-detector")
    print("negative result (AUROC 0.87 synthetic / 0.49 naturalistic). Two independent")
    print("cheap signals now fail in exactly the regime where the problem lives.")

    out = logs / "attributor_eval.json"
    out.write_text(json.dumps({"cells": rows, "per_rule": rule_rows}, indent=2,
                              ensure_ascii=False), encoding="utf-8")
    print(f"\nWritten to {out}")


if __name__ == "__main__":
    main()
