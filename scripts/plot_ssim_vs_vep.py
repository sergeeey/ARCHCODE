#!/usr/bin/env python3
"""
Publication figure: ARCHCODE SSIM vs VEP Score scatter plot.

Highlights 20 pearl variants (VEP-blind, ARCHCODE-detected) in red.
Shows discordance zones and category-level clustering.

Output: results/figures/fig_ssim_vs_vep.png (300 DPI)

Usage:
    python scripts/plot_ssim_vs_vep.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# ПОЧЕМУ matplotlib, а не seaborn: seaborn не установлен, а для scatter plot
# с кастомными зонами matplotlib даёт полный контроль без лишних зависимостей.

ATLAS_PATH = Path("results/HBB_Clinical_Atlas_REAL.csv")
OUTPUT_DIR = Path("results/figures")
OUTPUT_PATH = OUTPUT_DIR / "fig_ssim_vs_vep.png"

# Category → marker shape mapping
CATEGORY_MARKERS = {
    "nonsense": "v",        # triangle down
    "frameshift": "s",      # square
    "splice_donor": "D",    # diamond
    "splice_acceptor": "D",
    "missense": "o",        # circle
    "splice_region": "^",   # triangle up
    "promoter": "P",        # plus (filled)
    "3_prime_UTR": "<",     # triangle left
    "5_prime_UTR": ">",     # triangle right
    "intronic": "h",        # hexagon
    "synonymous": "*",      # star
    "other": "X",           # X (filled)
}

# Category → color (non-pearl)
CATEGORY_COLORS = {
    "nonsense": "#2563EB",       # blue
    "frameshift": "#7C3AED",     # purple
    "splice_donor": "#0891B2",   # cyan
    "splice_acceptor": "#0891B2",
    "missense": "#6B7280",       # gray
    "splice_region": "#059669",  # green
    "promoter": "#D97706",       # amber
    "3_prime_UTR": "#9CA3AF",    # light gray
    "5_prime_UTR": "#9CA3AF",
    "intronic": "#D1D5DB",       # very light gray
    "synonymous": "#E5E7EB",     # near white
    "other": "#9CA3AF",
}

PEARL_COLOR = "#DC2626"       # red
PEARL_EDGE = "#991B1B"        # dark red


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ATLAS_PATH)
    print(f"Loaded {len(df)} variants from {ATLAS_PATH}")

    # Separate pearls from non-pearls
    pearls = df[df["Pearl"] == True].copy()
    non_pearls = df[df["Pearl"] != True].copy()
    print(f"Pearls: {len(pearls)}, Non-pearls: {len(non_pearls)}")

    # --- Figure setup ---
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#FAFAFA")

    # --- Discordance zone shading ---
    # Zone 1: VEP pathogenic, ARCHCODE benign (VEP-only) — top-right
    ax.axhspan(0.5, 1.05, xmin=0, xmax=1, alpha=0.04, color="#3B82F6",
               zorder=0)
    # Zone 2: ARCHCODE pathogenic, VEP benign (ARCHCODE-only) — bottom-left
    # Pearl zone: VEP < 0.3 AND SSIM < 0.95
    ax.fill_between([0.82, 0.95], 0, 0.3, alpha=0.08, color="#DC2626",
                    zorder=0, label="_nolegend_")

    # Threshold lines
    ax.axhline(y=0.3, color="#DC2626", linewidth=0.8, linestyle="--",
               alpha=0.5, zorder=1)
    ax.axhline(y=0.5, color="#6B7280", linewidth=0.6, linestyle=":",
               alpha=0.4, zorder=1)
    ax.axvline(x=0.85, color="#6B7280", linewidth=0.6, linestyle=":",
               alpha=0.4, zorder=1)
    ax.axvline(x=0.92, color="#6B7280", linewidth=0.6, linestyle=":",
               alpha=0.4, zorder=1)
    ax.axvline(x=0.95, color="#DC2626", linewidth=0.8, linestyle="--",
               alpha=0.5, zorder=1)

    # Threshold labels
    ax.text(0.848, 1.01, "PATH", fontsize=6.5, color="#6B7280", ha="center",
            transform=ax.get_xaxis_transform())
    ax.text(0.885, 1.01, "LP", fontsize=6.5, color="#6B7280", ha="center",
            transform=ax.get_xaxis_transform())
    ax.text(0.94, 1.01, "VUS", fontsize=6.5, color="#6B7280", ha="center",
            transform=ax.get_xaxis_transform())
    ax.text(0.975, 1.01, "LB/B", fontsize=6.5, color="#6B7280", ha="center",
            transform=ax.get_xaxis_transform())

    # --- Plot non-pearls by category ---
    plotted_categories = set()
    for cat in CATEGORY_MARKERS:
        subset = non_pearls[non_pearls["Category"] == cat]
        if len(subset) == 0:
            continue
        plotted_categories.add(cat)
        ax.scatter(
            subset["ARCHCODE_SSIM"],
            subset["VEP_Score"],
            marker=CATEGORY_MARKERS.get(cat, "o"),
            c=CATEGORY_COLORS.get(cat, "#6B7280"),
            s=30,
            alpha=0.6,
            edgecolors="white",
            linewidths=0.3,
            zorder=2,
            label=cat.replace("_", " ") + f" (n={len(subset)})",
        )

    # --- Plot pearls on top ---
    ax.scatter(
        pearls["ARCHCODE_SSIM"],
        pearls["VEP_Score"],
        marker="o",
        c=PEARL_COLOR,
        s=80,
        alpha=0.95,
        edgecolors=PEARL_EDGE,
        linewidths=1.2,
        zorder=5,
        label=f"Pearl variants (n={len(pearls)})",
    )

    # --- Annotate pearl groups ---
    # Promoter cluster
    promoter_pearls = pearls[pearls["Category"] == "promoter"]
    if len(promoter_pearls) > 0:
        cx = promoter_pearls["ARCHCODE_SSIM"].mean()
        cy = promoter_pearls["VEP_Score"].mean()
        ax.annotate(
            f"Promoter pearls\n(n={len(promoter_pearls)})",
            xy=(cx, cy),
            xytext=(cx - 0.035, cy + 0.08),
            fontsize=7.5,
            color=PEARL_EDGE,
            fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=PEARL_EDGE, lw=0.8),
            zorder=6,
        )

    # Splice_acceptor pearl
    sa_pearls = pearls[pearls["Category"] == "splice_acceptor"]
    if len(sa_pearls) > 0:
        row = sa_pearls.iloc[0]
        ax.annotate(
            f"splice_acceptor\n(VCV002024192)",
            xy=(row["ARCHCODE_SSIM"], row["VEP_Score"]),
            xytext=(row["ARCHCODE_SSIM"] - 0.045, row["VEP_Score"] - 0.07),
            fontsize=6.5,
            color=PEARL_EDGE,
            arrowprops=dict(arrowstyle="->", color=PEARL_EDGE, lw=0.7),
            zorder=6,
        )

    # Frameshift pearl
    fs_pearls = pearls[pearls["Category"] == "frameshift"]
    if len(fs_pearls) > 0:
        row = fs_pearls.iloc[0]
        ax.annotate(
            f"frameshift\n(VCV000869358)",
            xy=(row["ARCHCODE_SSIM"], row["VEP_Score"]),
            xytext=(row["ARCHCODE_SSIM"] - 0.005, row["VEP_Score"] - 0.08),
            fontsize=6.5,
            color=PEARL_EDGE,
            arrowprops=dict(arrowstyle="->", color=PEARL_EDGE, lw=0.7),
            zorder=6,
        )

    # --- "Pearl zone" label ---
    ax.text(
        0.875, 0.06, "Pearl zone\n(VEP < 0.3, SSIM < 0.95)",
        fontsize=7, color="#DC2626", alpha=0.7, ha="center",
        style="italic", zorder=6,
    )

    # --- Axis formatting ---
    ax.set_xlabel("ARCHCODE SSIM (structural similarity to wild-type)",
                  fontsize=11, labelpad=8)
    ax.set_ylabel("VEP Score (sequence-based pathogenicity)",
                  fontsize=11, labelpad=8)
    ax.set_title(
        "ARCHCODE vs VEP: Structural and Sequence-Based\n"
        "Variant Pathogenicity for 353 Real HBB ClinVar Variants",
        fontsize=12.5, fontweight="bold", pad=14,
    )

    # Axis limits
    ax.set_xlim(0.845, 1.005)
    ax.set_ylim(-0.02, 1.02)

    # Grid
    ax.grid(True, alpha=0.15, linewidth=0.5)
    ax.tick_params(labelsize=9)

    # --- Legend ---
    handles, labels = ax.get_legend_handles_labels()
    # Move pearl to first position
    pearl_idx = next(i for i, l in enumerate(labels) if "Pearl" in l)
    handles = [handles[pearl_idx]] + handles[:pearl_idx] + handles[pearl_idx+1:]
    labels = [labels[pearl_idx]] + labels[:pearl_idx] + labels[pearl_idx+1:]

    legend = ax.legend(
        handles, labels,
        loc="upper left",
        fontsize=7,
        framealpha=0.9,
        edgecolor="#D1D5DB",
        title="Variant category",
        title_fontsize=8,
        ncol=2,
        columnspacing=1.0,
        handletextpad=0.4,
    )
    legend.get_frame().set_linewidth(0.5)

    # --- Summary statistics text box ---
    stats_text = (
        f"n = 353 real ClinVar HBB variants\n"
        f"ARCHCODE pathogenic: 161 (45.6%)\n"
        f"Pearls: {len(pearls)} (VEP < 0.3, SSIM < 0.95)\n"
        f"Discordant: 130 (36.8%)\n"
        f"Mean SSIM: 0.927 | Mean VEP: 0.754"
    )
    ax.text(
        0.99, 0.02, stats_text,
        transform=ax.transAxes, fontsize=6.5,
        verticalalignment="bottom", horizontalalignment="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                  edgecolor="#D1D5DB", alpha=0.9),
    )

    plt.tight_layout()
    fig.savefig(str(OUTPUT_PATH), dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    print(f"\nFigure saved: {OUTPUT_PATH}")
    print(f"Size: {OUTPUT_PATH.stat().st_size / 1024:.0f} KB")

    plt.close()


if __name__ == "__main__":
    main()
