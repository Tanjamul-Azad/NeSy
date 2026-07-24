"""Statistical inference for CREST's experimental comparisons.

Two things are needed before any of these numbers belong in a paper, and
neither is optional at an A*-level venue.

1. PAIRED SIGNIFICANCE TESTING. Every comparison in this project is paired:
   the same FOLIO examples are run through both conditions. Comparing two
   independent proportions (a two-sample z-test, or worse, eyeballing the
   gap) throws away the pairing and is the wrong test. McNemar's test is the
   correct one -- it conditions on the discordant pairs, i.e. exactly the
   "helped" and "hurt" counts. The exact binomial version is used rather
   than the chi-square approximation because our discordant counts are
   small (b + c is often < 25), where the approximation is unreliable.

2. CLUSTERED CONFIDENCE INTERVALS. FOLIO examples are NOT independent:
   they are grouped by story, and examples in a story share their premises
   and differ only in the conclusion. The 203-example validation split
   contains only 73 stories. A standard binomial interval assumes 203
   independent trials and will therefore be too narrow. `cluster_bootstrap_ci`
   resamples whole stories, which respects the dependence structure and
   yields honestly wider intervals.

Reporting rule adopted for this project: give the point estimate, the
cluster-bootstrap CI, and the exact-McNemar p-value for any claim that one
condition differs from another. Never report a bare difference in
percentages as though it were a finding.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Sequence, Tuple

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


@dataclass
class McNemarResult:
    n_pairs: int
    both_success: int
    only_a_success: int  # "hurt" when A = baseline and B = the new method
    only_b_success: int  # "helped"
    both_failure: int
    p_value: float
    odds_ratio: float
    direction: str

    def summary(self) -> str:
        return (f"McNemar exact, n={self.n_pairs}: "
                f"A-only={self.only_a_success}, B-only={self.only_b_success}, "
                f"p={self.p_value:.4g} ({self.direction})")


def mcnemar_exact(a_success: Sequence[bool], b_success: Sequence[bool]) -> McNemarResult:
    """Exact McNemar test for two paired binary conditions.

    `a_success[i]` and `b_success[i]` must describe the SAME example under
    conditions A and B. Only discordant pairs carry information; concordant
    pairs are uninformative about a difference and are conditioned out --
    which is precisely why this test, and not a two-proportion test, is the
    right one for a paired design.
    """
    if len(a_success) != len(b_success):
        raise ValueError("paired sequences must be the same length")

    both = sum(1 for x, y in zip(a_success, b_success) if x and y)
    only_a = sum(1 for x, y in zip(a_success, b_success) if x and not y)
    only_b = sum(1 for x, y in zip(a_success, b_success) if y and not x)
    neither = sum(1 for x, y in zip(a_success, b_success) if not x and not y)

    n_disc = only_a + only_b
    if n_disc == 0:
        p = 1.0
    else:
        # Two-sided exact binomial on the discordant pairs under H0: p = 0.5.
        p = float(stats.binomtest(only_b, n_disc, 0.5, alternative="two-sided").pvalue)

    odds = (only_b / only_a) if only_a else float("inf") if only_b else float("nan")
    if only_b > only_a:
        direction = "B better than A"
    elif only_a > only_b:
        direction = "A better than B"
    else:
        direction = "no directional difference"

    return McNemarResult(len(a_success), both, only_a, only_b, neither, p, odds, direction)


def cluster_bootstrap_ci(
    values: Sequence[float],
    clusters: Sequence,
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_boot: int = 10000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Percentile bootstrap CI that resamples CLUSTERS, not observations.

    Returns (point_estimate, lo, hi).

    Resampling individual examples would assume independence that FOLIO does
    not have -- examples sharing a story share premises, so their outcomes
    are correlated. Resampling whole stories preserves that structure. The
    resulting interval is wider than a naive binomial one, and that width is
    the honest one.
    """
    values = np.asarray(values, dtype=float)
    clusters = np.asarray(clusters)
    point = float(statistic(values))

    uniq = np.unique(clusters)
    idx_by_cluster = {c: np.flatnonzero(clusters == c) for c in uniq}
    rng = np.random.default_rng(seed)

    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        picked = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_cluster[c] for c in picked])
        boot[i] = statistic(values[idx])

    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return point, float(lo), float(hi)


def proportion_ci_clustered(
    successes: Sequence[bool], clusters: Sequence, **kw
) -> Tuple[float, float, float]:
    return cluster_bootstrap_ci([1.0 if s else 0.0 for s in successes], clusters, **kw)


def compare_conditions(
    name_a: str, outcomes_a: Sequence[str],
    name_b: str, outcomes_b: Sequence[str],
    clusters: Sequence,
    success_when: str = "correct",
) -> Dict:
    """Full paired comparison of two conditions over the same examples.

    Tests the primary endpoint (accuracy) and, separately, the endpoint this
    project actually cares about: whether the example failed SILENTLY. A
    method can leave accuracy unchanged while converting silent failures
    into loud ones, which would be a genuine improvement for a system whose
    whole purpose is to avoid failing invisibly -- so it is tested
    explicitly rather than left implicit in the accuracy number.
    """
    succ_a = [o == success_when for o in outcomes_a]
    succ_b = [o == success_when for o in outcomes_b]
    acc = mcnemar_exact(succ_a, succ_b)

    # "not silent" as the success criterion: correct or loudly-failed both
    # count, because both are visible to a downstream consumer.
    quiet_a = [o != "silent_failure" for o in outcomes_a]
    quiet_b = [o != "silent_failure" for o in outcomes_b]
    sil = mcnemar_exact(quiet_a, quiet_b)

    pa, la, ha = proportion_ci_clustered(succ_a, clusters)
    pb, lb, hb = proportion_ci_clustered(succ_b, clusters)
    sa = proportion_ci_clustered([o == "silent_failure" for o in outcomes_a], clusters)
    sb = proportion_ci_clustered([o == "silent_failure" for o in outcomes_b], clusters)

    return {
        "n": len(outcomes_a),
        "n_clusters": len(set(clusters)),
        "accuracy": {
            name_a: {"point": pa, "ci95": [la, ha]},
            name_b: {"point": pb, "ci95": [lb, hb]},
            "mcnemar": acc,
        },
        "silent_failure_rate": {
            name_a: {"point": sa[0], "ci95": [sa[1], sa[2]]},
            name_b: {"point": sb[0], "ci95": [sb[1], sb[2]]},
            "mcnemar_on_not_silent": sil,
        },
    }


def print_comparison(name_a: str, name_b: str, res: Dict) -> None:
    print(f"  n = {res['n']} examples across {res['n_clusters']} stories "
          f"(clustered bootstrap, 10k resamples of whole stories)")
    print()
    acc = res["accuracy"]
    print("  ACCURACY")
    for nm in (name_a, name_b):
        d = acc[nm]
        print(f"    {nm:24s} {d['point']:.1%}   95% CI [{d['ci95'][0]:.1%}, {d['ci95'][1]:.1%}]")
    m = acc["mcnemar"]
    print(f"    {m.summary()}")
    print(f"      helped (only {name_b}): {m.only_b_success}   "
          f"hurt (only {name_a}): {m.only_a_success}   net: {m.only_b_success - m.only_a_success:+d}")
    print()
    sf = res["silent_failure_rate"]
    print("  SILENT-FAILURE RATE")
    for nm in (name_a, name_b):
        d = sf[nm]
        print(f"    {nm:24s} {d['point']:.1%}   95% CI [{d['ci95'][0]:.1%}, {d['ci95'][1]:.1%}]")
    m2 = sf["mcnemar_on_not_silent"]
    print(f"    {m2.summary()}   [endpoint: example did NOT fail silently]")
