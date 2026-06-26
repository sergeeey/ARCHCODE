#!/usr/bin/env python
"""
Etap 2 — HBB truth audit (falsification-first).

WHY this script exists:
  The 2026-06-05 plan asks to honestly rewrite the central HBB result. The old
  loud claim ("Cohen d=2.13 -> LSSIM predicts pathogenicity") is suspected to be
  a category-distribution artifact, because LSSIM is a DETERMINISTIC function of
  the variant consequence category via the CATEGORICAL_EFFECTS lookup table in
  scripts/generate-unified-atlas.ts (verified by reading the source).

  This script does NOT recompute LSSIM. It treats the canonical atlas as given
  (READ-ONLY) and asks the only honest questions:
    Q1. Per consequence category: n, mean/median LSSIM, IQR, bootstrap 95% CI.
    Q2. Where BOTH classes exist in a category: Mann-Whitney U, Cliff's delta,
        within-category AUC. (matched-category test = the real test)
    Q3. Decompose the across-group Cohen d into a category-distribution effect:
        recompute Cohen d after stratifying / re-weighting categories.

  Output: HBB_SEVERITY_STATS.json (machine) — markdown report is written by hand
  citing these numbers. Every number in the report must trace to this JSON.

Evidence policy: this is [VERIFIED-INLINE] computation on the project's own
canonical CSV (a real ClinVar-derived artifact, NOT synthetic). It validates a
DESCRIPTIVE claim about the atlas, not a causal/real-world pathogenicity claim.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ATLAS = Path(__file__).resolve().parents[1] / "HBB_Unified_Atlas_95kb.csv"
OUT = Path(__file__).resolve().parent / "HBB_SEVERITY_STATS.json"
RNG = np.random.default_rng(20260605)  # fixed seed: reproducible, passed in not Date.now()


def cliffs_delta(a, b):
    """Cliff's delta = P(a>b) - P(a<b). Nonparametric effect size in [-1,1]."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return None
    gt = sum((x > b).sum() for x in a)
    lt = sum((x < b).sum() for x in a)
    return (gt - lt) / (len(a) * len(b))


def auc_mw(pos, neg):
    """AUC via Mann-Whitney U (score = LSSIM). Pathogenic expected LOWER LSSIM,
    so we score on (1 - LSSIM): higher score = more 'pathogenic-like'."""
    if len(pos) < 1 or len(neg) < 1:
        return None
    sp = 1.0 - np.asarray(pos, float)
    sn = 1.0 - np.asarray(neg, float)
    u, _ = stats.mannwhitneyu(sp, sn, alternative="two-sided")
    return u / (len(sp) * len(sn))


def boot_ci(x, fn=np.mean, n=5000, alpha=0.05):
    x = np.asarray(x, float)
    if len(x) < 2:
        return [None, None]
    idx = RNG.integers(0, len(x), size=(n, len(x)))
    stat = fn(x[idx], axis=1)
    lo, hi = np.quantile(stat, [alpha / 2, 1 - alpha / 2])
    return [round(float(lo), 6), round(float(hi), 6)]


def cohen_d(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    sp = np.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    if sp == 0:
        return None
    return float((a.mean() - b.mean()) / sp)


def main():
    df = pd.read_csv(ATLAS)
    df = df.dropna(subset=["ARCHCODE_LSSIM"])
    df["is_path"] = df["Label"].str.lower().eq("pathogenic")
    df["is_benign"] = df["Label"].str.lower().eq("benign")

    out = {
        "source_csv": str(ATLAS.name),
        "n_rows": int(len(df)),
        "n_pathogenic": int(df["is_path"].sum()),
        "n_benign": int(df["is_benign"].sum()),
        "note": "LSSIM is a deterministic function of Category via CATEGORICAL_EFFECTS "
                "(verified in scripts/generate-unified-atlas.ts). These statistics are "
                "DESCRIPTIVE of the canonical atlas, not independent pathogenicity evidence.",
        "categories": [],
        "global": {},
        "confound_decomposition": {},
    }

    # ---- Q1 + Q2: per category ----
    for cat, g in df.groupby("Category"):
        lp = g.loc[g["is_path"], "ARCHCODE_LSSIM"].to_numpy()
        lb = g.loc[g["is_benign"], "ARCHCODE_LSSIM"].to_numpy()
        all_l = g["ARCHCODE_LSSIM"].to_numpy()
        rec = {
            "category": cat,
            "n_total": int(len(g)),
            "n_path": int(len(lp)),
            "n_benign": int(len(lb)),
            "mean_lssim": round(float(np.mean(all_l)), 6),
            "median_lssim": round(float(np.median(all_l)), 6),
            "iqr": [round(float(np.quantile(all_l, 0.25)), 6),
                    round(float(np.quantile(all_l, 0.75)), 6)],
            "boot95_mean": boot_ci(all_l),
            "within_category_testable": bool(len(lp) >= 3 and len(lb) >= 3),
            "mannwhitney_p": None,
            "cliffs_delta": None,
            "within_category_auc": None,
        }
        if len(lp) >= 3 and len(lb) >= 3:
            try:
                _, p = stats.mannwhitneyu(lp, lb, alternative="two-sided")
                rec["mannwhitney_p"] = float(p)
            except ValueError:
                rec["mannwhitney_p"] = None
            rec["cliffs_delta"] = cliffs_delta(lp, lb)
            rec["within_category_auc"] = auc_mw(lp, lb)
        out["categories"].append(rec)

    # ---- Q1/Q2 global ----
    lp = df.loc[df["is_path"], "ARCHCODE_LSSIM"].to_numpy()
    lb = df.loc[df["is_benign"], "ARCHCODE_LSSIM"].to_numpy()
    out["global"] = {
        "cohen_d_path_vs_benign": round(cohen_d(lp, lb), 4) if cohen_d(lp, lb) else None,
        "cliffs_delta_path_vs_benign": cliffs_delta(lp, lb),
        "global_auc": auc_mw(lp, lb),
        "path_mean_lssim": round(float(lp.mean()), 6),
        "benign_mean_lssim": round(float(lb.mean()), 6),
        "n_testable_categories": int(sum(c["within_category_testable"] for c in out["categories"])),
    }

    # ---- Q3: confound decomposition ----
    # The benign group's category mix vs pathogenic group's category mix.
    path_mix = df.loc[df["is_path"], "Category"].value_counts(normalize=True).round(4).to_dict()
    ben_mix = df.loc[df["is_benign"], "Category"].value_counts(normalize=True).round(4).to_dict()
    # Category-stratified Cohen d: weight per-category d by min(n_path,n_benign), only testable cats
    strat = []
    for c in out["categories"]:
        if c["within_category_testable"]:
            g = df[df["Category"] == c["category"]]
            d = cohen_d(g.loc[g["is_path"], "ARCHCODE_LSSIM"], g.loc[g["is_benign"], "ARCHCODE_LSSIM"])
            strat.append({"category": c["category"],
                          "within_cat_cohen_d": round(d, 4) if d is not None else None,
                          "weight": int(min(c["n_path"], c["n_benign"]))})
    wsum = sum(s["weight"] for s in strat) or 1
    pooled = sum((s["within_cat_cohen_d"] or 0) * s["weight"] for s in strat) / wsum
    out["confound_decomposition"] = {
        "pathogenic_category_mix": path_mix,
        "benign_category_mix": ben_mix,
        "benign_pct_intronic": round(float(ben_mix.get("intronic", 0)) * 100, 1),
        "stratified_cohen_d_components": strat,
        "category_stratified_pooled_cohen_d": round(float(pooled), 4),
        "interpretation": "If the naive across-group Cohen d collapses toward ~0 after "
                          "category stratification, the d=2.13-style effect is a "
                          "category-distribution artifact, not independent structural signal.",
    }

    OUT.write_text(json.dumps(out, indent=2))
    print(f"WROTE {OUT}")
    print(f"  naive Cohen d (path vs benign)        = {out['global']['cohen_d_path_vs_benign']}")
    print(f"  category-stratified pooled Cohen d    = {out['confound_decomposition']['category_stratified_pooled_cohen_d']}")
    print(f"  global AUC                            = {round(out['global']['global_auc'],4)}")
    print(f"  benign group % intronic              = {out['confound_decomposition']['benign_pct_intronic']}%")
    print(f"  testable (both-class) categories      = {out['global']['n_testable_categories']}")
    for c in out["categories"]:
        if c["within_category_testable"]:
            print(f"    [{c['category']}] n={c['n_total']} path={c['n_path']} ben={c['n_benign']} "
                  f"within-AUC={round(c['within_category_auc'],4)} cliff={round(c['cliffs_delta'],4)} "
                  f"MW_p={c['mannwhitney_p']:.3g}")


if __name__ == "__main__":
    sys.exit(main())
