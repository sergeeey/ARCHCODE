#!/usr/bin/env python3
"""
Generate single-page taxonomy summary figure for talks and collaborator briefs.

Three panels side-by-side:
  Left:   Simplified taxonomy map (4 quadrants A-D + E overlay)
  Center: HBB Q2b enhancer distance histogram (hero data)
  Right:  Simplified tool matrix heatmap (4 tools × 5 classes)
  Bottom: Banner text

Input:
  - analysis/Q2b_true_blindspots.csv
  - analysis/discordance_2x2_matrix.csv  (for context)
  - analysis/tissue_mismatch_controls_summary.json  (for context)
  - docs/taxonomy_figure_specs.md  (spec)

Output:
  - figures/taxonomy/fig_taxonomy_summary_slide.pdf
  - figures/taxonomy/fig_taxonomy_summary_slide.png
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

# ПОЧЕМУ: publication-grade defaults set once here so all panels are consistent
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,  # TrueType for editability
        "ps.fonttype": 42,
    }
)

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
OUT_DIR = ROOT / "figures" / "taxonomy"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Data loading ──────────────────────────────────────────────────────────

q2b = pd.read_csv(ANALYSIS / "Q2b_true_blindspots.csv")
# Filter to HBB-only Q2b for the hero panel (architecture-driven blindspots)
q2b_hbb = q2b[q2b["Locus"] == "HBB"].copy()

with open(ANALYSIS / "tissue_mismatch_controls_summary.json") as f:
    tissue_data = json.load(f)


# ── Figure setup ──────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 5.5))

# ПОЧЕМУ: gridspec gives precise control over panel widths and the banner row
gs = fig.add_gridspec(
    2,
    3,
    height_ratios=[1, 0.08],
    width_ratios=[1, 1.1, 1],
    hspace=0.25,
    wspace=0.30,
    left=0.05,
    right=0.95,
    top=0.92,
    bottom=0.06,
)


# ══════════════════════════════════════════════════════════════════════════
# LEFT PANEL — Simplified taxonomy map
# ══════════════════════════════════════════════════════════════════════════

ax_tax = fig.add_subplot(gs[0, 0])

# ПОЧЕМУ: quadrant colors match the spec — A=blue, B=orange, C=purple, D=gray
colors = {
    "A": "#4393C3",  # blue — activity-driven
    "B": "#F4A460",  # sandy orange — architecture-driven
    "C": "#8B6BAE",  # purple — mixed
    "D": "#BFBFBF",  # gray — coverage gap
}

# Draw four quadrants as filled rectangles
quadrants = [
    ("D", 0, 0, 0.5, 0.5),  # bottom-left
    ("A", 0.5, 0, 0.5, 0.5),  # bottom-right
    ("B", 0, 0.5, 0.5, 0.5),  # top-left
    ("C", 0.5, 0.5, 0.5, 0.5),  # top-right
]

for label, x0, y0, w, h in quadrants:
    rect = mpatches.FancyBboxPatch(
        (x0, y0),
        w,
        h,
        boxstyle="round,pad=0.01",
        facecolor=colors[label],
        alpha=0.55,
        edgecolor="0.3",
        linewidth=1.2,
    )
    ax_tax.add_patch(rect)

# Quadrant labels with descriptors
label_props = dict(fontsize=13, fontweight="bold", ha="center", va="center")
desc_props = dict(fontsize=7.5, ha="center", va="center", color="0.15", style="italic")

ax_tax.text(0.25, 0.75, "B", **label_props)
ax_tax.text(0.25, 0.65, "Architecture-\ndriven", **desc_props)

ax_tax.text(0.75, 0.75, "C", **label_props)
ax_tax.text(0.75, 0.65, "Mixed", **desc_props)

ax_tax.text(0.75, 0.25, "A", **label_props)
ax_tax.text(0.75, 0.15, "Activity-\ndriven", **desc_props)

ax_tax.text(0.25, 0.25, "D", **label_props)
ax_tax.text(0.25, 0.15, "Coverage\ngap", **desc_props)

# Class E overlay (red hatched over B quadrant)
e_rect = mpatches.FancyBboxPatch(
    (0.02, 0.82),
    0.46,
    0.15,
    boxstyle="round,pad=0.01",
    facecolor="red",
    alpha=0.25,
    edgecolor="red",
    linewidth=1.5,
    linestyle="--",
)
ax_tax.add_patch(e_rect)
ax_tax.text(
    0.25,
    0.895,
    "E  Tissue-mismatch",
    fontsize=7,
    ha="center",
    va="center",
    color="darkred",
    fontweight="bold",
)

# Axes
ax_tax.set_xlim(-0.05, 1.05)
ax_tax.set_ylim(-0.05, 1.05)
ax_tax.set_xlabel("Sequence / Activity Signal  →", fontsize=9)
ax_tax.set_ylabel("Architecture / Contact Signal  →", fontsize=9)
ax_tax.set_xticks([])
ax_tax.set_yticks([])
ax_tax.set_title("A   Mechanistic Taxonomy", fontsize=11, fontweight="bold", loc="left")

# Axis arrows
ax_tax.annotate(
    "",
    xy=(1.02, -0.03),
    xytext=(-0.02, -0.03),
    arrowprops=dict(arrowstyle="->", color="0.4", lw=1.2),
)
ax_tax.annotate(
    "",
    xy=(-0.03, 1.02),
    xytext=(-0.03, -0.02),
    arrowprops=dict(arrowstyle="->", color="0.4", lw=1.2),
)

for spine in ax_tax.spines.values():
    spine.set_visible(False)


# ══════════════════════════════════════════════════════════════════════════
# CENTER PANEL — HBB Q2b enhancer distance histogram
# ══════════════════════════════════════════════════════════════════════════

ax_hist = fig.add_subplot(gs[0, 1])

distances = q2b_hbb["Enhancer_Dist_bp"].dropna().values
n_q2b = len(q2b_hbb)
mean_dist = distances.mean()

# ПОЧЕМУ: histogram better than scatter for a single-variable distribution;
# shows clustering near enhancers clearly on one slide
bins = np.arange(0, max(distances) + 100, 50)
ax_hist.hist(
    distances, bins=bins, color="#F4A460", edgecolor="0.3", linewidth=0.7, alpha=0.85, zorder=3
)

ax_hist.axvline(
    mean_dist,
    color="red",
    linestyle="--",
    linewidth=1.5,
    zorder=4,
    label=f"mean = {mean_dist:.0f} bp",
)

# Annotation box
stats_text = f"n = {n_q2b}\nmean = {mean_dist:.0f} bp\np = 2.51e-31"
ax_hist.text(
    0.97,
    0.95,
    stats_text,
    transform=ax_hist.transAxes,
    fontsize=9,
    va="top",
    ha="right",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="0.5", alpha=0.9),
)

ax_hist.set_xlabel("Distance to nearest enhancer (bp)", fontsize=9)
ax_hist.set_ylabel("Number of Q2b variants", fontsize=9)
ax_hist.set_title(
    "B   HBB Q2b: Architecture-Driven Blindspots", fontsize=11, fontweight="bold", loc="left"
)
ax_hist.legend(loc="upper center", fontsize=8, framealpha=0.9)
ax_hist.set_xlim(0, max(distances) + 80)
ax_hist.spines["top"].set_visible(False)
ax_hist.spines["right"].set_visible(False)
ax_hist.grid(axis="y", alpha=0.3, zorder=0)


# ══════════════════════════════════════════════════════════════════════════
# RIGHT PANEL — Simplified tool-to-mechanism heatmap
# ══════════════════════════════════════════════════════════════════════════

ax_heat = fig.add_subplot(gs[0, 2])

# ПОЧЕМУ: 4 tools (not 8) keeps the slide readable; these are the most relevant
tools = ["VEP", "MPRA", "ARCHCODE", "Hi-C"]
classes = ["A\nActivity", "B\nArchitecture", "C\nMixed", "D\nGap", "E\nMismatch"]

# Score encoding: 3=primary, 2=good, 1=partial, 0=blind, -1=N/A, -2=artifact
# From the spec table
matrix = np.array(
    [
        #  A   B   C   D   E
        [2, 0, 1, 0, -1],  # VEP
        [3, 0, 1, 0, -1],  # MPRA
        [0, 3, 1, 2, -2],  # ARCHCODE
        [0, 3, 2, 0, -1],  # Hi-C
    ]
)

# Custom colormap: map values to colors
from matplotlib.colors import ListedColormap, BoundaryNorm

# -2=artifact(red-striped), -1=N/A(gray), 0=blind(salmon), 1=partial(lightyellow),
# 2=good(yellow-green), 3=primary(green)
cmap_colors = ["#E06060", "#D0D0D0", "#F4A0A0", "#FFF8C4", "#C5E1A5", "#4CAF50"]
cmap = ListedColormap(cmap_colors)
bounds = [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
norm = BoundaryNorm(bounds, cmap.N)

im = ax_heat.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

# Cell text annotations
value_labels = {3: "+++", 2: "++", 1: "+", 0: "-", -1: "N/A", -2: "ART"}
for i in range(len(tools)):
    for j in range(len(classes)):
        val = matrix[i, j]
        txt = value_labels[val]
        color = "white" if val in (3, -2) else "0.15"
        ax_heat.text(
            j, i, txt, ha="center", va="center", fontsize=10, fontweight="bold", color=color
        )

# Red outline around B column for VEP and MPRA (blind spot)
blind_rect = mpatches.Rectangle(
    (0.5, -0.5),
    1,
    2,
    linewidth=2.5,
    edgecolor="red",
    facecolor="none",
    linestyle="-",
    zorder=5,
)
ax_heat.add_patch(blind_rect)
ax_heat.text(1, -0.85, "blind spot", fontsize=7, ha="center", color="red", fontweight="bold")

ax_heat.set_xticks(range(len(classes)))
ax_heat.set_xticklabels(classes, fontsize=8)
ax_heat.set_yticks(range(len(tools)))
ax_heat.set_yticklabels(tools, fontsize=9, fontweight="bold")
ax_heat.set_title("C   Tool Coverage Matrix", fontsize=11, fontweight="bold", loc="left")
ax_heat.tick_params(length=0)

# Light grid
for i in range(len(tools) + 1):
    ax_heat.axhline(i - 0.5, color="white", linewidth=1.5)
for j in range(len(classes) + 1):
    ax_heat.axvline(j - 0.5, color="white", linewidth=1.5)


# ══════════════════════════════════════════════════════════════════════════
# BOTTOM BANNER — Takeaway message
# ══════════════════════════════════════════════════════════════════════════

ax_banner = fig.add_subplot(gs[1, :])
ax_banner.set_xlim(0, 1)
ax_banner.set_ylim(0, 1)
ax_banner.axis("off")

banner_rect = FancyBboxPatch(
    (0.02, 0.1),
    0.96,
    0.8,
    boxstyle="round,pad=0.015",
    facecolor="#2C3E50",
    edgecolor="none",
    alpha=0.9,
)
ax_banner.add_patch(banner_rect)

ax_banner.text(
    0.5,
    0.5,
    "Single-axis scoring is the wrong abstraction.  "
    "Mechanistic decomposition is the right abstraction.",
    ha="center",
    va="center",
    fontsize=12,
    fontweight="bold",
    color="white",
    style="italic",
)


# ══════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════

out_pdf = OUT_DIR / "fig_taxonomy_summary_slide.pdf"
out_png = OUT_DIR / "fig_taxonomy_summary_slide.png"

fig.savefig(out_pdf)
fig.savefig(out_png, dpi=300)
plt.close(fig)

print(f"Saved: {out_pdf}")
print(f"Saved: {out_png}")
print(f"  Q2b HBB variants: n={n_q2b}, mean enhancer dist={mean_dist:.0f} bp")
