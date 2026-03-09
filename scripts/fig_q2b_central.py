#!/usr/bin/env python3
"""
Q2b-Only Central Figure — 3-panel trust amplifier
==================================================
Panel A: Q2b vs Q3 enhancer distance (box + strip)
Panel B: Per-locus Q2b count (HBB vs TERT vs null)
Panel C: Threshold sensitivity (Q2b count vs LSSIM threshold)
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(r"D:\ДНК")
OUTPUT = BASE / "figures"
ANALYSIS = BASE / "analysis"

# ── Load pre-computed data ───────────────────────────────────────

sensitivity = pd.read_csv(ANALYSIS / "threshold_sensitivity.csv")
with open(ANALYSIS / "enhancer_proximity_odds.json") as f:
    odds = json.load(f)

# Load Q2b and Q3 raw data for Panel A
q2b = pd.read_csv(ANALYSIS / "Q2b_true_blindspots.csv")

# We need Q3 distances — reload from discordance script logic
import sys

sys.path.insert(0, str(BASE / "scripts"))
from low_hanging_fruits import load_all_data

df = load_all_data(lssim_threshold=0.95)
q3_data = df[df["Q"] == "Q3"]

# ── Figure ───────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), gridspec_kw={"wspace": 0.35})

# ── Panel A: Q2b vs Q3 enhancer distance ─────────────────────────
ax = axes[0]

q2b_dists = q2b["Enhancer_Dist_bp"].dropna().values
q3_dists = q3_data["Dist_Enhancer"].dropna().values

# Cap Q3 at 50kb for visualization
q3_dists_viz = np.clip(q3_dists, 0, 50000)

bp = ax.boxplot(
    [q2b_dists, q3_dists_viz],
    labels=["Q2b\n(blind spots)", "Q3\n(seq-channel)"],
    widths=0.5,
    patch_artist=True,
    showfliers=False,
    medianprops=dict(color="black", linewidth=1.5),
)
bp["boxes"][0].set_facecolor("#E74C3C")
bp["boxes"][0].set_alpha(0.7)
bp["boxes"][1].set_facecolor("#3498DB")
bp["boxes"][1].set_alpha(0.7)

# Strip plot overlay for Q2b (small N, show all points)
jitter = np.random.default_rng(42).uniform(-0.12, 0.12, len(q2b_dists))
ax.scatter(
    1 + jitter,
    q2b_dists,
    c="#C0392B",
    s=20,
    alpha=0.8,
    zorder=5,
    edgecolors="white",
    linewidths=0.3,
)

# Annotation
_, p_mw = stats.mannwhitneyu(q2b_dists, q3_dists, alternative="less")
ax.text(
    0.5,
    0.95,
    f"p = {p_mw:.1e}",
    transform=ax.transAxes,
    ha="center",
    va="top",
    fontsize=9,
    style="italic",
)

# 1kb threshold line
ax.axhline(1000, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
ax.text(2.45, 1050, "1 kb", fontsize=7, color="gray", ha="right")

ax.set_ylabel("Distance to nearest enhancer (bp)", fontsize=9)
ax.set_title("A. Q2b enhancer proximity", fontsize=10, fontweight="bold")
ax.set_ylim(-50, 12000)
ax.tick_params(labelsize=8)

# ── Panel B: Per-locus Q2b count ────────────────────────────────
ax = axes[1]

loci_order = ["HBB", "BRCA1", "TERT", "TP53", "MLH1", "CFTR", "LDLR", "SCN5A", "GJB2"]
q2b_counts = q2b.groupby("Locus").size().reindex(loci_order, fill_value=0)

colors = []
tissue_map = {
    "HBB": 1.0,
    "BRCA1": 0.5,
    "TP53": 0.5,
    "CFTR": 0.0,
    "MLH1": 0.5,
    "LDLR": 0.0,
    "SCN5A": 0.0,
    "TERT": 0.5,
    "GJB2": 0.0,
}
for locus in loci_order:
    tm = tissue_map[locus]
    if tm == 1.0:
        colors.append("#E74C3C")
    elif tm == 0.5:
        colors.append("#F39C12")
    else:
        colors.append("#95A5A6")

bars = ax.bar(
    range(len(loci_order)), q2b_counts.values, color=colors, edgecolor="white", linewidth=0.5
)
ax.set_xticks(range(len(loci_order)))
ax.set_xticklabels(loci_order, rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Q2b variants", fontsize=9)
ax.set_title("B. Q2b by locus", fontsize=10, fontweight="bold")
ax.tick_params(labelsize=8)

# Legend
patches = [
    mpatches.Patch(color="#E74C3C", label="Tissue-matched"),
    mpatches.Patch(color="#F39C12", label="Partial match"),
    mpatches.Patch(color="#95A5A6", label="Tissue-mismatched"),
]
ax.legend(handles=patches, fontsize=7, loc="upper right")

# Add count labels
for i, v in enumerate(q2b_counts.values):
    if v > 0:
        ax.text(i, v + 0.3, str(v), ha="center", va="bottom", fontsize=7, fontweight="bold")

# ── Panel C: Threshold sensitivity ──────────────────────────────
ax = axes[2]

thresholds = sensitivity["LSSIM_threshold"].values
n_q2b = sensitivity["N_Q2b"].values
n_hbb = sensitivity["N_Q2b_HBB"].values

ax.plot(thresholds, n_q2b, "o-", color="#E74C3C", linewidth=1.5, markersize=5, label="All loci Q2b")
ax.plot(thresholds, n_hbb, "s--", color="#2C3E50", linewidth=1.2, markersize=4, label="HBB Q2b")

# Mark default threshold
ax.axvline(0.95, color="gray", linestyle=":", alpha=0.5)
ax.text(0.951, max(n_q2b) * 0.9, "default\n(0.95)", fontsize=7, color="gray")

# Shade stable core region
ax.axvspan(0.92, 0.96, alpha=0.08, color="#E74C3C")
ax.text(
    0.94,
    max(n_q2b) * 0.15,
    "stable\ncore",
    fontsize=7,
    color="#C0392B",
    ha="center",
    style="italic",
)

ax.set_xlabel("LSSIM threshold", fontsize=9)
ax.set_ylabel("Q2b variant count", fontsize=9)
ax.set_title("C. Threshold sensitivity", fontsize=10, fontweight="bold")
ax.legend(fontsize=7, loc="upper left")
ax.tick_params(labelsize=8)

# ── Save ─────────────────────────────────────────────────────────
fig.suptitle(
    "True structural blind spots (Q2b): not coverage gaps", fontsize=11, fontweight="bold", y=1.02
)
plt.tight_layout()
fig.savefig(OUTPUT / "fig_q2b_central.pdf", bbox_inches="tight", dpi=300)
fig.savefig(OUTPUT / "fig_q2b_central.png", bbox_inches="tight", dpi=300)
plt.close()

print(f"Saved: {OUTPUT / 'fig_q2b_central.pdf'}")
print(f"Saved: {OUTPUT / 'fig_q2b_central.png'}")
