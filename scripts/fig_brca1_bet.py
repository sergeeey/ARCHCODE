#!/usr/bin/env python3
"""
Figures for BRCA1 Fragility Atlas + Multi-Locus BET Sweep.
- Figure A: BRCA1 fragility landscape (severe effect) with gene/enhancer annotations
- Figure B: BET inhibitor effect by tissue match (9 loci heatmap + dose-response)
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

BASE = Path(r"D:\ДНК")
ANALYSIS = BASE / "analysis"
FIGURES = BASE / "figures"

# ══════════════════════════════════════════════════════════════════
# Figure A: BRCA1 Fragility Atlas
# ══════════════════════════════════════════════════════════════════


def fig_brca1_fragility():
    df = pd.read_csv(ANALYSIS / "fragility_atlas_brca1.csv")

    fig, axes = plt.subplots(
        2, 1, figsize=(14, 6), gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05}
    )

    # Panel 1: ΔSSIM by effect level
    ax = axes[0]
    for level, color, ls in [
        ("severe", "#C0392B", "-"),
        ("strong", "#E67E22", "--"),
        ("moderate", "#2980B9", "-."),
        ("weak", "#95A5A6", ":"),
    ]:
        sub = df[df["Effect_Level"] == level].sort_values("Position")
        ax.plot(
            sub["Position"] / 1e6,
            sub["Delta_SSIM"],
            color=color,
            linewidth=1.2,
            linestyle=ls,
            label=f"{level} (effect={sub['Effect_Strength'].iloc[0]})",
        )

    # Mark BRCA1 gene
    gene_start, gene_end = 43.044294, 43.125364
    ax.axvspan(gene_start, gene_end, alpha=0.10, color="#3498DB", label="BRCA1 gene")

    # Enhancer positions
    enhancers = [
        43.125364,
        43.170700,
        42.981500,
        43.007000,
        42.998900,
        42.929000,
        42.964500,
        43.024600,
        43.021500,
    ]
    for e in enhancers:
        ax.axvline(e, color="#27AE60", alpha=0.3, linewidth=0.5)

    # CTCF positions
    ctcf = [
        42.929437,
        42.937930,
        42.964377,
        42.980938,
        42.998141,
        43.004047,
        43.006741,
        43.024579,
        43.042287,
        43.085710,
        43.124566,
        43.171272,
        43.172342,
        43.214276,
    ]
    for c in ctcf:
        ax.axvline(c, color="#8E44AD", alpha=0.2, linewidth=0.5, linestyle=":")

    ax.set_ylabel("ΔSSIM (structural disruption)", fontsize=9)
    ax.set_title(
        "Structural Fragility Atlas — BRCA1 400kb (MCF7 enhancers)", fontsize=11, fontweight="bold"
    )
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.set_xlim(df["Position"].min() / 1e6, df["Position"].max() / 1e6)
    ax.tick_params(labelsize=8)
    ax.set_xticklabels([])

    # Panel 2: gene annotation track
    ax2 = axes[1]
    ax2.set_xlim(ax.get_xlim())

    # BRCA1 gene bar
    ax2.barh(0.5, gene_end - gene_start, left=gene_start, height=0.3, color="#3498DB", alpha=0.7)
    ax2.text(
        (gene_start + gene_end) / 2,
        0.5,
        "BRCA1",
        ha="center",
        va="center",
        fontsize=7,
        fontweight="bold",
        color="white",
    )

    # Other genes
    genes = [
        ("G6PC1", 42.900798, 42.914438),
        ("RPL27", 42.998272, 43.002959),
        ("IFI35", 43.006783, 43.014456),
        ("VAT1", 43.014606, 43.022385),
        ("NBR2", 43.125556, 43.153671),
        ("NBR1", 43.170408, 43.211688),
    ]
    for name, gs, ge in genes:
        ax2.barh(0.5, ge - gs, left=gs, height=0.2, color="#BDC3C7", alpha=0.5)
        ax2.text((gs + ge) / 2, 0.5, name, ha="center", va="center", fontsize=5, color="#7F8C8D")

    # Enhancers
    for e in enhancers:
        ax2.plot(e, 0.0, "^", color="#27AE60", markersize=5)

    # CTCF
    for c in ctcf:
        ax2.plot(c, -0.5, "|", color="#8E44AD", markersize=6)

    ax2.set_ylim(-1, 1)
    ax2.set_xlabel("Genomic position (Mb, GRCh38, chr17)", fontsize=9)
    ax2.set_yticks([])
    ax2.tick_params(labelsize=8)
    ax2.text(df["Position"].min() / 1e6 + 0.002, 0.0, "▲ enhancers", fontsize=6, color="#27AE60")
    ax2.text(df["Position"].min() / 1e6 + 0.002, -0.6, "| CTCF", fontsize=6, color="#8E44AD")

    plt.savefig(FIGURES / "fig_fragility_atlas_brca1.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(FIGURES / "fig_fragility_atlas_brca1.png", bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Saved: {FIGURES / 'fig_fragility_atlas_brca1.pdf'}")


# ══════════════════════════════════════════════════════════════════
# Figure B: Multi-Locus BET Sweep
# ══════════════════════════════════════════════════════════════════


def fig_bet_sweep():
    df = pd.read_csv(ANALYSIS / "bet_sweep_multilocus.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"wspace": 0.35})

    # Panel A: Dose-response curves colored by tissue match
    ax = axes[0]
    match_colors = {"matched": "#E74C3C", "partial": "#F39C12", "mismatch": "#95A5A6"}
    match_styles = {"matched": "-", "partial": "--", "mismatch": ":"}

    for locus in df["Locus"].unique():
        sub = df[df["Locus"] == locus].sort_values("BET_Inhibition_Pct")
        match = sub["Tissue_Match"].iloc[0]
        ax.plot(
            sub["BET_Inhibition_Pct"],
            sub["Delta_SSIM"],
            marker="o",
            markersize=4,
            linewidth=1.5,
            linestyle=match_styles[match],
            color=match_colors[match],
            label=f"{locus} ({match})",
            alpha=0.8,
        )

    ax.set_xlabel("BET inhibition (%)", fontsize=10)
    ax.set_ylabel("ΔSSIM (variant discrimination)", fontsize=10)
    ax.set_title("A. BET inhibitor dose-response\nacross 9 loci", fontsize=11, fontweight="bold")
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.tick_params(labelsize=8)

    # Panel B: Heatmap — loss of discrimination
    ax = axes[1]

    # Order loci by tissue match then by baseline ΔSSIM
    order = ["HBB", "TERT", "MLH1", "LDLR", "BRCA1", "TP53", "CFTR", "SCN5A", "GJB2"]
    bet_levels = sorted(df["BET_Inhibition_Pct"].unique())

    matrix = np.zeros((len(order), len(bet_levels)))
    for i, locus in enumerate(order):
        for j, bet in enumerate(bet_levels):
            row = df[(df["Locus"] == locus) & (df["BET_Inhibition_Pct"] == bet)]
            if len(row) > 0:
                matrix[i, j] = row["Delta_SSIM"].values[0]

    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_xticks(range(len(bet_levels)))
    ax.set_xticklabels([f"{int(b)}%" for b in bet_levels], fontsize=8)
    ax.set_yticks(range(len(order)))

    # Color-code y labels by tissue match
    tissue_map = dict(zip(df["Locus"], df["Tissue_Match"]))
    for i, locus in enumerate(order):
        color = match_colors.get(tissue_map.get(locus, "partial"), "#333")
        ax.get_yticklabels()[i].set_color(color) if ax.get_yticklabels() else None

    ax.set_yticklabels(order, fontsize=9)
    ax.set_xlabel("BET inhibition level", fontsize=10)
    ax.set_title(
        "B. ΔSSIM heatmap\n(yellow=low, red=high disruption)", fontsize=11, fontweight="bold"
    )

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("ΔSSIM", fontsize=9)

    # Add text annotations
    for i in range(len(order)):
        for j in range(len(bet_levels)):
            val = matrix[i, j]
            color = "white" if val > 0.10 else "black"
            ax.text(j, i, f"{val:.3f}", ha="center", va="center", fontsize=6, color=color)

    fig.suptitle(
        "BET Inhibitor Effect on Structural Variant Discrimination — 9 Genomic Loci",
        fontsize=11,
        y=1.02,
    )
    plt.savefig(FIGURES / "fig_bet_sweep_multilocus.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(FIGURES / "fig_bet_sweep_multilocus.png", bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Saved: {FIGURES / 'fig_bet_sweep_multilocus.pdf'}")


if __name__ == "__main__":
    fig_brca1_fragility()
    fig_bet_sweep()
