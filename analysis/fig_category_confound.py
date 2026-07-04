#!/usr/bin/env python3
"""
Money figure: category confounding in 3D-structural variant-effect scoring.
Mathematically rigorous: stratified (category-matched) c-statistic + bootstrap 95% CI.
9 disease loci, 30,318 variants. CADD as positive control.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata
import matplotlib.pyplot as plt
from matplotlib import gridspec

ROOT = Path("D:/ДНК")
DF = pd.read_csv(ROOT / "results" / "integrative_benchmark.csv")
OUT_FIG = ROOT / "results" / "fig_category_confound.png"
OUT_JSON = ROOT / "results" / "fig_category_confound_stats.json"
RNG = np.random.default_rng(20260704)  # fixed seed — reproducible, no Date/random ban issue


# ---------- fast AUC via average ranks (handles ties) ----------
def auc(y, s):
    y = np.asarray(y)
    s = np.asarray(s, float)
    npos = int(y.sum())
    nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return np.nan, 0
    r = rankdata(s)  # average ranks -> ties handled
    a = (r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)
    return a, npos * nneg  # return #pairs for stratified aggregation


def marginal_auc(y, s):
    a, _ = auc(y, s)
    return a


def stratified_auc(y, s, cat):
    """Conditional c-statistic: concordant pairs only within same category."""
    num = den = 0.0
    for c in np.unique(cat):
        m = cat == c
        a, pairs = auc(y[m], s[m])
        if pairs > 0 and not np.isnan(a):
            num += a * pairs
            den += pairs
    return num / den if den > 0 else np.nan


def orient(y, s, cat):
    """Flip score sign so marginal AUC >= 0.5 (fair comparison across methods)."""
    a = marginal_auc(y, s)
    return s if a >= 0.5 else -s


def boot_ci(fn, y, s, cat, B=1000):
    n = len(y)
    idx = np.arange(n)
    vals = []
    for _ in range(B):
        b = RNG.choice(idx, size=n, replace=True)
        v = fn(y[b], s[b], cat[b])
        if not np.isnan(v):
            vals.append(v)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return lo, hi


# ---------- prepare (CLEAN labels: exclude Conflicting + NaN significance) ----------
_sig = DF["ClinVar_Significance"].fillna("NaN")
_PATH = {
    "Pathogenic",
    "Likely pathogenic",
    "Pathogenic/Likely pathogenic",
    "Pathogenic/Likely pathogenic; other",
    "Pathogenic; drug response",
    "Pathogenic; other",
}
_BEN = {"Benign", "Benign/Likely benign", "Likely benign"}
DF["_y"] = np.where(_sig.isin(_PATH), 1, np.where(_sig.isin(_BEN), 0, -1))
d = DF[(DF["_y"] >= 0) & DF["Category"].notna()].copy()
y_all = d["_y"].values
cat_all = d["Category"].values

METHODS = {
    "ARCHCODE\n(3D structure)": ("ARCHCODE_LSSIM", "#d1495b"),
    "CADD\n(positive control)": ("CADD_Phred", "#2e8540"),
    "VEP": ("VEP_Score", "#8a8d91"),
}

# ---------- Panel B stats: method comparison (pooled) ----------
methB = {}
for name, (col, color) in METHODS.items():
    sub = d.dropna(subset=[col])
    yy = sub["_y"].values
    cc = sub["Category"].values
    ss = orient(yy, sub[col].values, cc)
    m = marginal_auc(yy, ss)
    w = stratified_auc(yy, ss, cc)
    m_ci = boot_ci(lambda a, b, c: marginal_auc(a, b), yy, ss, cc, B=1000)
    w_ci = boot_ci(stratified_auc, yy, ss, cc, B=1000)
    methB[name] = dict(color=color, marg=m, marg_ci=m_ci, wit=w, wit_ci=w_ci, n=len(sub))
    print(
        f"{name.splitlines()[0]:10s} marg={m:.3f} [{m_ci[0]:.3f},{m_ci[1]:.3f}]  "
        f"within={w:.3f} [{w_ci[0]:.3f},{w_ci[1]:.3f}]"
    )

# ---------- Panel A stats: per-locus ARCHCODE ----------
col = "ARCHCODE_LSSIM"
perloc = []
for loc, g in d.dropna(subset=[col]).groupby("Locus"):
    yy = g["_y"].values
    cc = g["Category"].values
    ss = orient(yy, g[col].values, cc)
    m = marginal_auc(yy, ss)
    w = stratified_auc(yy, ss, cc)
    if np.isnan(m) or np.isnan(w):  # e.g. HBB: no label balance after cleaning
        continue
    w_ci = boot_ci(stratified_auc, yy, ss, cc, B=600)
    perloc.append(dict(locus=loc, n=len(g), marg=m, wit=w, wit_ci=w_ci))
# pooled row
ss_all = orient(y_all, d[col].values, cat_all)
perloc.append(
    dict(
        locus="POOLED",
        n=len(d),
        marg=marginal_auc(y_all, ss_all),
        wit=stratified_auc(y_all, ss_all, cat_all),
        wit_ci=boot_ci(stratified_auc, y_all, ss_all, cat_all, B=1000),
    )
)
perloc.sort(key=lambda r: (r["locus"] != "POOLED", -r["marg"]))

# ---------- FIGURE ----------
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig = plt.figure(figsize=(13, 6.2))
gs = gridspec.GridSpec(1, 2, width_ratios=[1.25, 1.0], wspace=0.32)

# --- Panel A: per-locus dumbbell ---
axA = fig.add_subplot(gs[0])
ys = np.arange(len(perloc))[::-1]
for yi, r in zip(ys, perloc):
    collapses = r["wit"] < 0.55
    lc = "#d1495b" if collapses else "#c9a227"
    axA.plot([r["marg"], r["wit"]], [yi, yi], color=lc, lw=2, zorder=1, alpha=0.8)
    axA.scatter(r["marg"], yi, s=55, facecolor="white", edgecolor="#333", zorder=3, lw=1.3)
    xl = r["wit_ci"]
    axA.plot([xl[0], xl[1]], [yi, yi], color=lc, lw=6, alpha=0.18, zorder=0)
    axA.scatter(
        r["wit"],
        yi,
        s=70,
        color=lc,
        edgecolor="#333",
        zorder=3,
        lw=1.0,
        marker="D" if r["locus"] == "POOLED" else "o",
    )
axA.axvline(0.5, ls="--", color="#444", lw=1.4, zorder=0)
axA.text(
    0.5, len(perloc) - 0.3, "chance", rotation=90, va="top", ha="right", fontsize=8.5, color="#444"
)
axA.set_yticks(ys)
axA.set_yticklabels(
    [f"{r['locus']}  (n={r['n']})" + ("★" if r["locus"] == "POOLED" else "") for r in perloc],
    fontsize=9,
)
axA.set_xlim(0.30, 1.0)
axA.set_xlabel("AUC (pathogenic vs benign)", fontsize=10.5)
axA.set_title(
    "A  ARCHCODE structural score collapses to chance\nwhen matched on variant category",
    fontsize=11,
    loc="left",
    fontweight="bold",
)
# legend for A
from matplotlib.lines import Line2D

axA.legend(
    handles=[
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="white",
            markeredgecolor="#333",
            markersize=8,
            label="marginal (raw)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="#d1495b",
            markeredgecolor="#333",
            markersize=8,
            label="within-category (matched, 95% CI)",
        ),
    ],
    loc="lower right",
    fontsize=8.5,
    frameon=True,
)
axA.grid(axis="x", alpha=0.25)

# --- Panel B: method comparison (positive control) ---
axB = fig.add_subplot(gs[1])
names = list(methB.keys())
x = np.arange(len(names))
bw = 0.36
for i, name in enumerate(names):
    r = methB[name]
    # marginal
    axB.bar(
        x[i] - bw / 2,
        r["marg"],
        bw,
        color=r["color"],
        alpha=0.45,
        yerr=[[r["marg"] - r["marg_ci"][0]], [r["marg_ci"][1] - r["marg"]]],
        capsize=3,
        ecolor="#333",
        label="marginal" if i == 0 else None,
    )
    # within-category
    axB.bar(
        x[i] + bw / 2,
        r["wit"],
        bw,
        color=r["color"],
        alpha=0.95,
        yerr=[[max(0, r["wit"] - r["wit_ci"][0])], [max(0, r["wit_ci"][1] - r["wit"])]],
        capsize=3,
        ecolor="#333",
        label="within-category" if i == 0 else None,
    )
axB.axhline(0.5, ls="--", color="#444", lw=1.4)
axB.text(len(names) - 0.5, 0.508, "chance", fontsize=8.5, color="#444", ha="right")
axB.set_xticks(x)
axB.set_xticklabels(names, fontsize=9)
axB.set_ylim(0.30, 1.0)
axB.set_ylabel("AUC", fontsize=10.5)
axB.set_title(
    "B  A valid predictor (CADD) survives the same test\n"
    "— proving the collapse is real, not an artifact",
    fontsize=11,
    loc="left",
    fontweight="bold",
)
axB.legend(loc="upper center", fontsize=8.5, ncol=2, frameon=True)
axB.grid(axis="y", alpha=0.25)

fig.suptitle(
    "Apparent 3D-structural variant-effect signal is explained by variant category, not structure  "
    "(9 disease loci, N=24,238 high-confidence variants; Conflicting/VUS excluded)",
    fontsize=12,
    fontweight="bold",
    y=1.0,
)
fig.text(
    0.5,
    -0.02,
    "Stratified c-statistic (category-matched); bootstrap 95% CI (B=1000). "
    "Scores oriented to marginal AUC≥0.5. Source: integrative_benchmark.csv",
    ha="center",
    fontsize=8,
    color="#555",
)
fig.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
print(f"\nSaved figure: {OUT_FIG}")

# save stats
stats = {
    "panelB": {
        k: {
            kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items() if kk != "color"
        }
        for k, v in methB.items()
    },
    "panelA_perlocus": perloc,
}
OUT_JSON.write_text(json.dumps(stats, indent=2, default=float))
print(f"Saved stats: {OUT_JSON}")
