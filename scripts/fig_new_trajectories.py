#!/usr/bin/env python3
"""
Figures for new scientific trajectories:
- Figure A: Fragility Atlas heatmap (HBB 95kb)
- Figure B: Parameter sweep (3-panel: residence, CTCF, BET)
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
# Figure A: Fragility Atlas
# ══════════════════════════════════════════════════════════════════


def fig_fragility():
    df = pd.read_csv(ANALYSIS / "fragility_atlas_hbb.csv")

    fig, axes = plt.subplots(
        2, 1, figsize=(12, 6), gridspec_kw={"height_ratios": [3, 1], "hspace": 0.05}
    )

    # Panel 1: ΔSSIM landscape by effect level
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

    # Mark known features
    gene_start, gene_end = 5.225464, 5.227079
    ax.axvspan(gene_start, gene_end, alpha=0.15, color="#E74C3C", label="HBB gene")

    # Enhancer positions
    enhancers = [5.227, 5.2255, 5.230, 5.233, 5.2467, 5.2480, 5.2559]
    for e in enhancers:
        ax.axvline(e, color="#27AE60", alpha=0.3, linewidth=0.5)

    # CTCF positions
    ctcf = [5.212, 5.218, 5.224, 5.228, 5.232, 5.236, 5.248029, 5.257994, 5.2912, 5.3027]
    for c in ctcf:
        ax.axvline(c, color="#8E44AD", alpha=0.2, linewidth=0.5, linestyle=":")

    ax.set_ylabel("ΔSSIM (structural disruption)", fontsize=9)
    ax.set_title(
        "Structural Fragility Atlas — HBB 95kb saturation scan", fontsize=11, fontweight="bold"
    )
    ax.legend(fontsize=7, loc="upper right", ncol=2)
    ax.set_xlim(df["Position"].min() / 1e6, df["Position"].max() / 1e6)
    ax.tick_params(labelsize=8)
    ax.set_xticklabels([])

    # Panel 2: Feature annotation track
    ax2 = axes[1]
    ax2.set_xlim(ax.get_xlim())

    # Gene
    ax2.barh(0.5, gene_end - gene_start, left=gene_start, height=0.3, color="#E74C3C", alpha=0.7)
    ax2.text(
        (gene_start + gene_end) / 2,
        0.5,
        "HBB",
        ha="center",
        va="center",
        fontsize=7,
        fontweight="bold",
        color="white",
    )

    # Enhancers
    for i, e in enumerate(enhancers):
        ax2.plot(e, 0.0, "^", color="#27AE60", markersize=6)

    # CTCF
    for c in ctcf:
        ax2.plot(c, -0.5, "|", color="#8E44AD", markersize=8)

    ax2.set_ylim(-1, 1)
    ax2.set_xlabel("Genomic position (Mb, GRCh38)", fontsize=9)
    ax2.set_yticks([])
    ax2.tick_params(labelsize=8)

    # Annotation labels
    ax2.text(df["Position"].min() / 1e6 + 0.001, 0.0, "▲ enhancers", fontsize=6, color="#27AE60")
    ax2.text(df["Position"].min() / 1e6 + 0.001, -0.6, "| CTCF", fontsize=6, color="#8E44AD")

    plt.savefig(FIGURES / "fig_fragility_atlas.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(FIGURES / "fig_fragility_atlas.png", bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Saved: {FIGURES / 'fig_fragility_atlas.pdf'}")


# ══════════════════════════════════════════════════════════════════
# Figure B: Parameter Sweep
# ══════════════════════════════════════════════════════════════════


def fig_parameter_sweep():
    df = pd.read_csv(ANALYSIS / "parameter_sweep.csv")
    grid = pd.read_csv(ANALYSIS / "parameter_grid_2d.csv")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4), gridspec_kw={"wspace": 0.35})

    # Panel A: Residence time
    ax = axes[0]
    res = df[df["Sweep"] == "residence_time"].sort_values("Secondary_Value")
    ax.plot(
        res["Secondary_Value"],
        res["Delta_SSIM"],
        "o-",
        color="#2C3E50",
        linewidth=1.5,
        markersize=5,
    )
    ax.axhline(res["Delta_SSIM"].mean(), color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Cohesin residence time (min)", fontsize=9)
    ax.set_ylabel("ΔSSIM (variant discrimination)", fontsize=9)
    ax.set_title("A. Residence time\n(WAPL depletion model)", fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=8)
    # Annotate ranges
    ax.annotate(
        "WAPL depletion\n(vermicelli)",
        xy=(50, res["Delta_SSIM"].iloc[-1]),
        fontsize=7,
        color="#7F8C8D",
        ha="center",
    )
    ax.annotate(
        "Cohesin\ninhibitor",
        xy=(3, res["Delta_SSIM"].iloc[0]),
        fontsize=7,
        color="#7F8C8D",
        ha="center",
    )

    # Panel B: CTCF blocking
    ax = axes[1]
    ctcf = df[df["Sweep"] == "ctcf_blocking"].sort_values("Param_Value")
    ax.plot(
        ctcf["Param_Value"] * 100,
        ctcf["Delta_SSIM"],
        "s-",
        color="#8E44AD",
        linewidth=1.5,
        markersize=5,
    )
    ax.set_xlabel("CTCF blocking efficiency (%)", fontsize=9)
    ax.set_ylabel("ΔSSIM", fontsize=9)
    ax.set_title("B. CTCF barrier strength", fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=8)

    # Panel C: BET inhibitor
    ax = axes[2]
    bet = df[df["Sweep"] == "enhancer_occupancy"].sort_values("Secondary_Value")
    ax.plot(
        bet["Secondary_Value"],
        bet["Delta_SSIM"],
        "D-",
        color="#E74C3C",
        linewidth=1.5,
        markersize=5,
    )
    ax.set_xlabel("BET inhibition (%)", fontsize=9)
    ax.set_ylabel("ΔSSIM", fontsize=9)
    ax.set_title("C. BET inhibitor effect\n(enhancer occupancy)", fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=8)
    # Annotate key finding
    ax.annotate(
        "4× loss of\ndiscrimination",
        xy=(80, 0.03),
        fontsize=8,
        color="#C0392B",
        fontweight="bold",
        ha="center",
        arrowprops=dict(arrowstyle="->", color="#C0392B"),
        xytext=(60, 0.055),
    )

    fig.suptitle(
        "Pharmacological parameter sensitivity — VCV002024192 (HBB splice acceptor)",
        fontsize=10,
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(FIGURES / "fig_parameter_sweep.pdf", bbox_inches="tight", dpi=300)
    plt.savefig(FIGURES / "fig_parameter_sweep.png", bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Saved: {FIGURES / 'fig_parameter_sweep.pdf'}")


if __name__ == "__main__":
    fig_fragility()
    fig_parameter_sweep()
