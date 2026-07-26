"""Does the model's own generation confidence predict a silent failure?

This is the detection result the project turns on. If a low-confidence
translation is more likely to fail silently, then confidence is a
gold-label-free risk signal a pre-solver layer can act on -- the bridge from
"we measured the problem" to "we can flag it before the solver runs".

Endpoint: among GRADEABLE examples (loud failures excluded -- they are
already visible, so there is nothing to detect), how well does a confidence
feature separate silent_failure from correct?

Metric: AUROC, computed as the Mann-Whitney statistic
  AUROC = P(score(silent failure) > score(correct))
where score is chosen so that "higher = riskier" (we use -mean_logprob and
-min_logprob, i.e. lower confidence = higher risk). AUROC = 0.5 is chance;
1.0 is perfect separation. Reported with a cluster-aware bootstrap CI
(resampling stories) because examples within a story are not independent.

Also reports a decision-relevant operating point: if we flag the least
confident k% as "at risk", what precision and recall do we get on silent
failures? That is what a deployed detector actually does.

No new model calls: reads the `confidence` field the vanilla pipeline already
logs. Run: python -m crest.evaluation.confidence_analysis <results.json>
"""

import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def _auroc(scores: np.ndarray, positive: np.ndarray) -> float:
    """AUROC via the rank-sum identity. positive is a boolean mask (the class
    we want scored higher). Ties are handled by average ranks.
    """
    pos = scores[positive]
    neg = scores[~positive]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = scores.argsort()
    ranks = np.empty(len(scores), dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    # average ranks for ties
    _, inv, counts = np.unique(scores, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts))
    np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    r_pos = ranks[positive].sum()
    return (r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def _bootstrap_auroc_ci(scores, positive, clusters, n_boot=5000, seed=42):
    rng = np.random.default_rng(seed)
    uniq = np.unique(clusters)
    idx_by = {c: np.flatnonzero(clusters == c) for c in uniq}
    boot = []
    for _ in range(n_boot):
        picked = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by[c] for c in picked])
        a = _auroc(scores[idx], positive[idx])
        if not np.isnan(a):
            boot.append(a)
    if not boot:
        return (float("nan"), float("nan"))
    return tuple(np.percentile(boot, [2.5, 97.5]))


def analyse(results_path: Path) -> dict:
    data = json.loads(results_path.read_text(encoding="utf-8"))
    recs = data["results"]

    # Gradeable only: loud failures are already visible, not the detection
    # target. Keep only examples that have a confidence reading.
    graded = [r for r in recs
              if r["outcome"] in ("correct", "silent_failure") and r.get("confidence")]
    n_missing = sum(1 for r in recs
                    if r["outcome"] in ("correct", "silent_failure") and not r.get("confidence"))

    if not graded:
        return {"error": "no gradeable examples with confidence", "file": results_path.name}

    clusters = np.array([r["story_id"] for r in graded])
    is_silent = np.array([r["outcome"] == "silent_failure" for r in graded])

    out = {
        "file": results_path.name,
        "dataset": data.get("dataset"),
        "n_gradeable_with_confidence": len(graded),
        "n_gradeable_missing_confidence": n_missing,
        "n_silent": int(is_silent.sum()),
        "n_correct": int((~is_silent).sum()),
        "features": {},
    }

    for feat in ("mean_logprob", "min_logprob", "perplexity"):
        vals = np.array([r["confidence"][feat] for r in graded], dtype=float)
        # Risk score: higher = riskier. Low logprob = risky, so negate;
        # perplexity is already "higher = less confident".
        score = vals if feat == "perplexity" else -vals
        auroc = _auroc(score, is_silent)
        lo, hi = _bootstrap_auroc_ci(score, is_silent, clusters)
        out["features"][feat] = {
            "auroc": auroc,
            "auroc_ci95": [lo, hi],
            "mean_on_silent": float(vals[is_silent].mean()),
            "mean_on_correct": float(vals[~is_silent].mean()),
        }

    # Operating point on the best feature: flag the riskiest 20%.
    best = max(out["features"], key=lambda f: (out["features"][f]["auroc"]
                                               if not np.isnan(out["features"][f]["auroc"]) else -1))
    vals = np.array([r["confidence"][best] for r in graded], dtype=float)
    score = vals if best == "perplexity" else -vals
    k = 0.20
    thresh = np.quantile(score, 1 - k)
    flagged = score >= thresh
    tp = int((flagged & is_silent).sum())
    out["operating_point"] = {
        "feature": best,
        "flag_top_fraction": k,
        "precision": tp / int(flagged.sum()) if flagged.sum() else float("nan"),
        "recall": tp / int(is_silent.sum()) if is_silent.sum() else float("nan"),
        "base_rate_silent": float(is_silent.mean()),
    }
    return out


def _print(out: dict) -> None:
    if "error" in out:
        print(f"  {out['file']}: {out['error']}")
        return
    print(f"=== {out['file']}  (dataset={out['dataset']}) ===")
    print(f"  gradeable with confidence: {out['n_gradeable_with_confidence']} "
          f"(silent={out['n_silent']}, correct={out['n_correct']}; "
          f"missing conf={out['n_gradeable_missing_confidence']})")
    print("  AUROC of confidence for predicting silent failure (0.5 = chance):")
    for feat, d in out["features"].items():
        print(f"    {feat:14s} AUROC={d['auroc']:.3f}  CI95 [{d['auroc_ci95'][0]:.3f}, {d['auroc_ci95'][1]:.3f}]"
              f"   silent={d['mean_on_silent']:.3f} vs correct={d['mean_on_correct']:.3f}")
    op = out["operating_point"]
    print(f"  operating point (flag riskiest {op['flag_top_fraction']:.0%} by {op['feature']}):")
    print(f"    precision={op['precision']:.1%}  recall={op['recall']:.1%}  "
          f"(silent base rate {op['base_rate_silent']:.1%})")


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        # default: every vanilla results file that has confidence
        paths = sorted(str(p) for p in (PROJECT_ROOT / "experiments" / "logs").glob("vanilla_pipeline_*.json"))
    for p in paths:
        out = analyse(Path(p))
        _print(out)
        print()
