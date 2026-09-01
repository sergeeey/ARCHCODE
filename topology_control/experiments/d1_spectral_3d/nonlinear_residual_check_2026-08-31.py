"""
Follow-up diagnostic, NOT part of the frozen pre-registration (commit 0f8cbb4).

D1 (this experiment) is already closed: KILL, decision.md 2026-08-30. The
committed pipeline (run_analysis.py) tests whether raw Hi-C `contact` adds
predictive power ON TOP OF a model that already includes `log10_dist`
(delta_auc = -0.0000 -- see result.json). That is a different, arguably
stricter question than: "if you regress contact on distance and look at the
univariate predictive power of the RESIDUAL alone, is it noise?" -- the
question this script answers, and the one an independent skeptic review
(2026-08-31, Claude-cod-top-2026 session, construct-measurement-gate dogfood)
specifically asked be re-run with a NONLINEAR distance control, since a linear
log-log fit could underfit a real, non-monotonic TAD-boundary structure and
manufacture a fake "residual is noise" result as an artifact of model
misspecification rather than a real absence of signal.

This script is exploratory, additive, and does NOT reopen or change D1's own
KILL verdict -- it answers a narrower, separate question using D1's own real
data (features_all.parquet), for a downstream user (negative-space-miner /
construct-measurement-gate dogfood in a different repo) who cited this
experiment's Hi-C-vs-distance relationship and asked for the nonlinear-control
robustness check.

Run: python nonlinear_residual_check_2026-08-31.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

HOLDOUT = ["chr20", "chr21", "chr22"]
N_BINS = 40


def linear_fit_residual(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    """OLS y ~ x, returns residuals and R^2."""
    slope, intercept = np.polyfit(x, y, deg=1)
    pred = slope * x + intercept
    resid = y - pred
    ss_res = np.sum(resid**2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return resid, r2, slope


def nonlinear_fit_residual(
    x: np.ndarray, y: np.ndarray, n_bins: int = N_BINS
) -> tuple[np.ndarray, float]:
    """
    Nonparametric distance control: bin x into quantile bins, take the local
    mean of y in each bin, linearly interpolate between bin centers to get a
    smooth nonlinear curve, subtract. Captures non-monotonic structure (e.g.
    a step near typical TAD sizes) that a single global linear fit cannot.
    """
    edges = np.unique(np.quantile(x, np.linspace(0, 1, n_bins + 1)))
    bin_idx = np.clip(np.digitize(x, edges[1:-1]), 0, len(edges) - 2)
    bin_centers = np.array([x[bin_idx == b].mean() for b in range(len(edges) - 1)])
    bin_means = np.array(
        [y[bin_idx == b].mean() if (bin_idx == b).any() else np.nan for b in range(len(edges) - 1)]
    )
    valid = ~np.isnan(bin_means)
    pred = np.interp(x, bin_centers[valid], bin_means[valid])
    resid = y - pred
    ss_res = np.sum(resid**2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return resid, r2


def auc_or_nan(label: np.ndarray, score: np.ndarray) -> float:
    if label.sum() == 0 or label.sum() == len(label):
        return float("nan")
    return roc_auc_score(label, score)


def report_for(df: pd.DataFrame, tag: str) -> dict:
    x = df["log10_dist"].to_numpy()
    y = np.log1p(
        df["contact"].to_numpy()
    )  # log1p: contact has real zeros (empty Hi-C bins), log(0) undefined
    label = df["label"].to_numpy()

    lin_resid, lin_r2, lin_slope = linear_fit_residual(x, y)
    nl_resid, nl_r2 = nonlinear_fit_residual(x, y)

    out = {
        "population": tag,
        "n": len(df),
        "n_pos": int(label.sum()),
        "linear_fit_slope_log10dist_on_log1p_contact": float(lin_slope),
        "linear_fit_r2": float(lin_r2),
        "nonlinear_fit_r2_binned_40": float(nl_r2),
        "auc_raw_contact_alone": auc_or_nan(label, df["contact"].to_numpy()),
        "auc_distance_alone": auc_or_nan(label, -x),
        "auc_linear_residual_alone": auc_or_nan(label, lin_resid),
        "auc_nonlinear_residual_alone": auc_or_nan(label, nl_resid),
    }
    return out


def main() -> None:
    raw = pd.read_parquet("features_all.parquet")
    df = raw[raw.bin_ok == 1].copy()  # same primary population as the frozen pipeline

    results = []
    results.append(report_for(df, "primary_population_bin_ok_1_all_chroms"))

    te = df[df.chrom.isin(HOLDOUT)].copy()
    results.append(report_for(te, "held_out_test_chr20-22_matching_prereg_split"))

    for r in results:
        print("=" * 78)
        print(f"population: {r['population']}  (n={r['n']:,}, n_pos={r['n_pos']:,})")
        print(
            f"  linear   fit: log1p(contact) ~ log10_dist   slope={r['linear_fit_slope_log10dist_on_log1p_contact']:+.4f}  R^2={r['linear_fit_r2']:.4f}"
        )
        print(
            f"  nonlinear fit (40-bin local mean, interpolated)             R^2={r['nonlinear_fit_r2_binned_40']:.4f}"
        )
        print(f"  AUC raw contact alone            : {r['auc_raw_contact_alone']:.4f}")
        print(f"  AUC distance alone                : {r['auc_distance_alone']:.4f}")
        print(f"  AUC linear residual alone         : {r['auc_linear_residual_alone']:.4f}")
        print(f"  AUC nonlinear residual alone      : {r['auc_nonlinear_residual_alone']:.4f}")

    Path("nonlinear_residual_check_2026-08-31.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print("\nsaved: nonlinear_residual_check_2026-08-31.json")


if __name__ == "__main__":
    main()
