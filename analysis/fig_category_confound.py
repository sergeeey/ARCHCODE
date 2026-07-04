#!/usr/bin/env python3
"""Money figure v2: adds ARCHCODE_SSIM + unsupervised phyloP control to Panel B.
Panel A per-locus (log-SSIM, full clean set). Panel B: 5 methods, two positive controls survive."""

import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.lines import Line2D

ROOT = Path("D:/ДНК")
OUT_FIG = ROOT / "results" / "fig_category_confound.png"
RNG = np.random.default_rng(20260704)


def auc(y, s):
    y = np.asarray(y)
    s = np.asarray(s, float)
    npos = int(y.sum())
    nneg = len(y) - npos
    if npos == 0 or nneg == 0:
        return np.nan, 0
    r = rankdata(s)
    return (r[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg), npos * nneg


def marg(y, s):
    return auc(y, s)[0]


def strat(y, s, cat):
    num = den = 0.0
    for c in np.unique(cat):
        m = cat == c
        a, p = auc(y[m], s[m])
        if p > 0 and not np.isnan(a):
            num += a * p
            den += p
    return num / den if den else np.nan


def orient(y, s, cat):
    return s if marg(y, s) >= 0.5 else -s


def boot(fn, y, s, cat, B=800):
    n = len(y)
    idx = np.arange(n)
    v = []
    for _ in range(B):
        b = RNG.choice(idx, n, replace=True)
        r = fn(y[b], s[b], cat[b])
        if not np.isnan(r):
            v.append(r)
    return np.percentile(v, [2.5, 97.5])


# ---- clean full set ----
df = pd.read_csv(ROOT / "results" / "integrative_benchmark.csv")
sig = df["ClinVar_Significance"].fillna("NaN")
P = {
    "Pathogenic",
    "Likely pathogenic",
    "Pathogenic/Likely pathogenic",
    "Pathogenic/Likely pathogenic; other",
    "Pathogenic; drug response",
    "Pathogenic; other",
}
Bn = {"Benign", "Benign/Likely benign", "Likely benign"}
df["y"] = np.where(sig.isin(P), 1, np.where(sig.isin(Bn), 0, -1))
d = df[df["y"] >= 0].copy()
sub = pd.read_csv(ROOT / "results" / "benchmark_phylop_subset.csv")  # 23,038 w/ phylop

RED, GREEN, GRAY = "#d1495b", "#2e8540", "#8a8d91"
# Panel B methods: (label, dataframe, column, color)
METH = [
    ("ARCHCODE\nlog-SSIM", d, "ARCHCODE_LSSIM", RED),
    ("ARCHCODE\nSSIM", d, "ARCHCODE_SSIM", RED),
    ("VEP", d, "VEP_Score", GRAY),
    ("phyloP\n(unsup. ctrl)", sub, "phylop", GREEN),
    ("CADD\n(sup. ctrl)", sub if False else d, "CADD_Phred", GREEN),
]
B = []
for lab, frame, col, color in METH:
    g = frame.dropna(subset=[col])
    y = g["y"].values
    cat = g["Category"].values
    s = orient(y, g[col].values, cat)
    m, w = marg(y, s), strat(y, s, cat)
    B.append(
        dict(
            lab=lab,
            color=color,
            m=m,
            w=w,
            mci=boot(lambda a, b, c: marg(a, b), y, s, cat),
            wci=boot(strat, y, s, cat),
            n=len(g),
        )
    )
    print(f"{lab.splitlines()[0]:14s} marg={m:.3f} within={w:.3f} n={len(g)}")

# ---- Panel A per-locus (log-SSIM, clean full set) ----
perloc = []
for loc, g in d.dropna(subset=["ARCHCODE_LSSIM"]).groupby("Locus"):
    y = g["y"].values
    cat = g["Category"].values
    s = orient(y, g["ARCHCODE_LSSIM"].values, cat)
    m, w = marg(y, s), strat(y, s, cat)
    if np.isnan(m) or np.isnan(w):
        continue
    perloc.append(dict(locus=loc, n=len(g), marg=m, wit=w, wci=boot(strat, y, s, cat, 500)))
ss = orient(d["y"].values, d["ARCHCODE_LSSIM"].values, d["Category"].values)
perloc.append(
    dict(
        locus="POOLED",
        n=len(d),
        marg=marg(d["y"].values, ss),
        wit=strat(d["y"].values, ss, d["Category"].values),
        wci=boot(strat, d["y"].values, ss, d["Category"].values),
    )
)
perloc.sort(key=lambda r: (r["locus"] != "POOLED", -r["marg"]))

# ---- FIGURE ----
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig = plt.figure(figsize=(13.5, 6.4))
gs = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1.15], wspace=0.30)

axA = fig.add_subplot(gs[0])
ys = np.arange(len(perloc))[::-1]
for yi, r in zip(ys, perloc):
    lc = RED if r["wit"] < 0.55 else "#c9a227"
    axA.plot([r["marg"], r["wit"]], [yi, yi], color=lc, lw=2, alpha=0.8, zorder=1)
    axA.plot(r["wci"], [yi, yi], color=lc, lw=6, alpha=0.18, zorder=0)
    axA.scatter(r["marg"], yi, s=52, facecolor="white", edgecolor="#333", lw=1.3, zorder=3)
    axA.scatter(
        r["wit"],
        yi,
        s=68,
        color=lc,
        edgecolor="#333",
        lw=1.0,
        zorder=3,
        marker="D" if r["locus"] == "POOLED" else "o",
    )
axA.axvline(0.5, ls="--", color="#444", lw=1.4)
axA.text(
    0.5, len(perloc) - 0.3, "chance", rotation=90, va="top", ha="right", fontsize=8.5, color="#444"
)
axA.set_yticks(ys)
axA.set_yticklabels(
    [f"{r['locus']} (n={r['n']})" + ("★" if r["locus"] == "POOLED" else "") for r in perloc],
    fontsize=9,
)
axA.set_xlim(0.30, 1.0)
axA.set_xlabel("AUC (pathogenic vs benign)", fontsize=10.5)
axA.set_title(
    "A  ARCHCODE score collapses to chance\nwhen matched on variant category",
    fontsize=11,
    loc="left",
    fontweight="bold",
)
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
            markerfacecolor=RED,
            markeredgecolor="#333",
            markersize=8,
            label="within-category (95% CI)",
        ),
    ],
    loc="lower right",
    fontsize=8.5,
)
axA.grid(axis="x", alpha=0.25)

axB = fig.add_subplot(gs[1])
x = np.arange(len(B))
bw = 0.36
for i, r in enumerate(B):
    axB.bar(
        x[i] - bw / 2,
        r["m"],
        bw,
        color=r["color"],
        alpha=0.42,
        yerr=[[r["m"] - r["mci"][0]], [r["mci"][1] - r["m"]]],
        capsize=3,
        ecolor="#333",
        label="marginal" if i == 0 else None,
    )
    axB.bar(
        x[i] + bw / 2,
        r["w"],
        bw,
        color=r["color"],
        alpha=0.95,
        yerr=[[max(0, r["w"] - r["wci"][0])], [max(0, r["wci"][1] - r["w"])]],
        capsize=3,
        ecolor="#333",
        label="within-category" if i == 0 else None,
    )
axB.axhline(0.5, ls="--", color="#444", lw=1.4)
axB.text(len(B) - 0.5, 0.508, "chance", fontsize=8.5, color="#444", ha="right")
axB.set_xticks(x)
axB.set_xticklabels([r["lab"] for r in B], fontsize=8.5)
axB.set_ylim(0.30, 1.02)
axB.set_ylabel("AUC", fontsize=10.5)
axB.set_title(
    "B  Two controls of opposite provenance survive the same test;\nboth ARCHCODE metrics collapse — the collapse is specific",
    fontsize=10.5,
    loc="left",
    fontweight="bold",
)
axB.legend(loc="upper center", fontsize=8.5, ncol=2)
axB.grid(axis="y", alpha=0.25)

fig.suptitle(
    "Apparent 3D-structural variant-effect signal is explained by variant category, not structure  (9 loci, N=24,238)",
    fontsize=12,
    fontweight="bold",
    y=1.0,
)
fig.text(
    0.5,
    -0.02,
    "Stratified c-statistic (category-matched); bootstrap 95% CI. phyloP on 95% conservation-covered subset (23,038). Source: integrative_benchmark.csv + UCSC phyloP100way",
    ha="center",
    fontsize=7.5,
    color="#555",
)
fig.savefig(OUT_FIG, dpi=300, bbox_inches="tight")
print(f"\nSaved: {OUT_FIG}")
