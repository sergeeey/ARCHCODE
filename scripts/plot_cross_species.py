#!/usr/bin/env python3
"""
Figure 12: Cross-Species Conservation of Structural Pathogenicity

Human HBB pearl positions mapped to mouse Hbb-bs via TSS-relative coordinates.
Panel A: Scatter plot (human vs mouse LSSIM) with Pearson r
Panel B: Bar chart — mean LSSIM by category (human vs mouse)
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PROJECT = Path(__file__).parent.parent
DATA = PROJECT / "results" / "cross_species_hbb_comparison.json"
OUT_PDF = PROJECT / "figures" / "fig12_cross_species.pdf"
OUT_PNG = PROJECT / "figures" / "fig12_cross_species.png"

with open(DATA) as f:
    data = json.load(f)

results = data["results"]
human_lssim = [r["humanLSSIM"] for r in results]
mouse_lssim = [r["mouseLSSIM"] for r in results]
categories = [r["category"] for r in results]
pearson_r = data["pearson_r"]

# Color map by category
CAT_COLORS = {
    "promoter": "#E74C3C",
    "missense": "#3498DB",
    "frameshift": "#2ECC71",
    "splice_acceptor": "#9B59B6",
    "other": "#95A5A6",
}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# --- Panel A: Scatter ---
for cat in set(categories):
    h = [human_lssim[i] for i in range(len(results)) if categories[i] == cat]
    m = [mouse_lssim[i] for i in range(len(results)) if categories[i] == cat]
    ax1.scatter(h, m, c=CAT_COLORS.get(cat, "#95A5A6"), label=cat, s=80, alpha=0.8,
                edgecolors="black", linewidths=0.5, zorder=5)

# Reference lines
ax1.axhline(0.95, color="red", linestyle="--", alpha=0.5, label="Pearl threshold (0.95)")
ax1.axvline(0.95, color="red", linestyle="--", alpha=0.5)

# Fit line
z = np.polyfit(human_lssim, mouse_lssim, 1)
p = np.poly1d(z)
x_fit = np.linspace(min(human_lssim) - 0.02, max(human_lssim) + 0.02, 100)
ax1.plot(x_fit, p(x_fit), "k--", alpha=0.3, linewidth=1)

ax1.set_xlabel("Human LSSIM", fontsize=12)
ax1.set_ylabel("Mouse LSSIM", fontsize=12)
ax1.set_title(f"A. Cross-Species LSSIM Correlation\n(Pearson r = {pearson_r:.3f}, n = {len(results)})", fontsize=13)
ax1.legend(fontsize=9, loc="lower right")
ax1.set_xlim(0.77, 0.96)
ax1.set_ylim(0.96, 1.005)

# Annotation
ax1.annotate(
    f"Direction conserved:\n17/17 positions show\nmouse LSSIM < WT baseline",
    xy=(0.82, 0.975), fontsize=8, style="italic",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8)
)

# --- Panel B: Category bar chart ---
cat_data = {}
for r in results:
    cat = r["category"]
    if cat not in cat_data:
        cat_data[cat] = {"human": [], "mouse": []}
    cat_data[cat]["human"].append(r["humanLSSIM"])
    cat_data[cat]["mouse"].append(r["mouseLSSIM"])

cats = sorted(cat_data.keys(), key=lambda c: np.mean(cat_data[c]["human"]))
x = np.arange(len(cats))
width = 0.35

human_means = [np.mean(cat_data[c]["human"]) for c in cats]
mouse_means = [np.mean(cat_data[c]["mouse"]) for c in cats]
human_stds = [np.std(cat_data[c]["human"]) if len(cat_data[c]["human"]) > 1 else 0 for c in cats]
mouse_stds = [np.std(cat_data[c]["mouse"]) if len(cat_data[c]["mouse"]) > 1 else 0 for c in cats]

bars1 = ax2.bar(x - width/2, human_means, width, yerr=human_stds, label="Human HBB",
                color="#3498DB", alpha=0.8, capsize=3)
bars2 = ax2.bar(x + width/2, mouse_means, width, yerr=mouse_stds, label="Mouse Hbb-bs",
                color="#E74C3C", alpha=0.8, capsize=3)

ax2.axhline(0.95, color="gray", linestyle="--", alpha=0.5, label="Pearl threshold")
ax2.set_xlabel("Variant Category", fontsize=12)
ax2.set_ylabel("Mean LSSIM", fontsize=12)
ax2.set_title("B. Category-Level Conservation\n(Human vs Mouse LSSIM)", fontsize=13)
ax2.set_xticks(x)
ax2.set_xticklabels(cats, rotation=30, ha="right", fontsize=10)
ax2.legend(fontsize=9)
ax2.set_ylim(0.75, 1.02)

# Add n counts
for i, cat in enumerate(cats):
    n = len(cat_data[cat]["human"])
    ax2.text(i, 0.76, f"n={n}", ha="center", fontsize=8, color="gray")

plt.tight_layout()
fig.savefig(OUT_PDF, dpi=300, bbox_inches="tight")
fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print(f"Saved: {OUT_PDF}")
print(f"Saved: {OUT_PNG}")
plt.close()
