#!/usr/bin/env python3
"""
Task #24: Create Publication Figures for Spectral Analysis
===========================================================
Generates publication-quality figures for H1-H4 spectral fragility validation.

Figures:
  1. Figure S1: SFI cross-locus validation (HBB, TP53, BRCA1 boxplots)
  2. Figure S2: Phase boundary spatial distribution (Φ map + pearl positions)
  3. Figure S3: Codeword distance comparison (bar chart with error bars)
  4. Figure S4: LSSIM distribution comparison (violin plots)

Output: results/figures/spectral_*.pdf

Usage:
    python scripts/create_spectral_figures.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"

# Publication style
plt.style.use("seaborn-v0_8-paper")
sns.set_palette("colorblind")
COLORS = {
    "HBB": "#0173B2",  # Blue
    "TP53": "#DE8F05",  # Orange
    "BRCA1": "#029E73",  # Green
}


def setup_figure_dir():
    """Create figures directory"""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory: {FIGURES_DIR}")


def load_sfi_results():
    """Load H1 SFI validation results"""
    data = []

    # HBB pearls vs controls
    hbb_path = RESULTS_DIR / "spectral_fragility" / "HBB_SFI_results.csv"
    if hbb_path.exists():
        hbb = pd.read_csv(hbb_path)
        hbb["Locus"] = "HBB"
        data.append(hbb)

    # TP53 splice_region
    tp53_path = RESULTS_DIR / "spectral_fragility" / "TP53_SFI_results.csv"
    if tp53_path.exists():
        tp53 = pd.read_csv(tp53_path)
        tp53["Locus"] = "TP53"
        data.append(tp53)

    # BRCA1 synonymous
    brca1_path = RESULTS_DIR / "spectral_fragility" / "BRCA1_SFI_results.csv"
    if brca1_path.exists():
        brca1 = pd.read_csv(brca1_path)
        brca1["Locus"] = "BRCA1"
        data.append(brca1)

    if not data:
        raise FileNotFoundError("No SFI results found")

    return pd.concat(data, ignore_index=True)


def create_figure_1_sfi_validation():
    """Figure S1: SFI Cross-Locus Validation"""
    print("\n📊 Creating Figure S1: SFI Cross-Locus Validation...")

    sfi_data = load_sfi_results()

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)

    loci = ["HBB", "TP53", "BRCA1"]
    expected = ["Pathogenic > Benign", "Pathogenic > Benign", "No difference (negative control)"]

    for idx, (locus, exp) in enumerate(zip(loci, expected)):
        ax = axes[idx]
        locus_data = sfi_data[sfi_data["Locus"] == locus]

        if len(locus_data) == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            ax.set_title(f"{locus}\n(no data)")
            continue

        # Boxplot
        sns.boxplot(
            data=locus_data,
            x="Label",
            y="SFI",
            ax=ax,
            palette=[COLORS[locus], "#888888"],
            width=0.5,
        )

        # Add swarmplot
        sns.swarmplot(
            data=locus_data,
            x="Label",
            y="SFI",
            ax=ax,
            color="black",
            alpha=0.3,
            size=3,
        )

        # Statistics
        if "Pathogenic" in locus_data["Label"].values and "Benign" in locus_data["Label"].values:
            path_sfi = locus_data[locus_data["Label"] == "Pathogenic"]["SFI"]
            benign_sfi = locus_data[locus_data["Label"] == "Benign"]["SFI"]

            u_stat, p_value = stats.mannwhitneyu(path_sfi, benign_sfi, alternative="two-sided")
            d = (path_sfi.mean() - benign_sfi.mean()) / np.sqrt(
                (
                    (len(path_sfi) - 1) * path_sfi.std() ** 2
                    + (len(benign_sfi) - 1) * benign_sfi.std() ** 2
                )
                / (len(path_sfi) + len(benign_sfi) - 2)
            )

            # Add p-value annotation
            y_max = locus_data["SFI"].max()
            ax.text(
                0.5,
                y_max * 1.15,
                f"p={p_value:.4f}\nd={d:.2f}",
                ha="center",
                fontsize=9,
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

        ax.set_xlabel("")
        ax.set_ylabel("Spectral Fragility Index (SFI)" if idx == 0 else "")
        ax.set_title(f"{locus}\n{exp}", fontsize=10)

    plt.tight_layout()
    output_path = FIGURES_DIR / "spectral_S1_sfi_validation.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_figure_2_phase_boundary():
    """Figure S2: Phase Boundary Spatial Distribution"""
    print("\n📊 Creating Figure S2: Phase Boundary Map...")

    # Load Φ distribution
    phi_path = RESULTS_DIR / "phase_boundary" / "phi_with_pearls.csv"
    if not phi_path.exists():
        print("⚠️  Phase boundary data not found, skipping Figure S2")
        return

    phi_data = pd.read_csv(phi_path)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # Panel A: Φ spatial distribution
    ax1.plot(
        phi_data["genomic_position"] / 1e6,
        phi_data["Phi"],
        color=COLORS["HBB"],
        linewidth=2,
        label="Φ parameter",
    )

    # Critical regime shading
    ax1.axhspan(0.7, 1.5, alpha=0.2, color="gray", label="Critical regime (Φ≈1)")
    ax1.axhline(1.0, color="gray", linestyle="--", linewidth=1, alpha=0.5)

    ax1.set_ylabel("Phase Parameter Φ", fontsize=11)
    ax1.legend(fontsize=9)
    ax1.set_title("H2: Phase Boundary Hypothesis (REJECTED)", fontsize=12, fontweight="bold")

    # Panel B: Pearl density
    ax2.bar(
        phi_data["genomic_position"] / 1e6,
        phi_data["pearl_density"],
        width=0.0006,  # 600bp bin
        color=COLORS["HBB"],
        alpha=0.7,
        label="Pearl density",
    )

    ax2.set_xlabel("Genomic Position (Mbp, chr11)", fontsize=11)
    ax2.set_ylabel("Pearls per kb", fontsize=11)
    ax2.legend(fontsize=9)

    # Add annotation
    ax2.text(
        0.98,
        0.95,
        "Result: 0/20 pearls in Φ∈[0.7,1.5]\nSpearman ρ=0.325, p=0.021\nFisher OR=0.0, p=1.0",
        transform=ax2.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="red", linewidth=2),
    )

    plt.tight_layout()
    output_path = FIGURES_DIR / "spectral_S2_phase_boundary.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_figure_3_codeword_distance():
    """Figure S3: Codeword Distance Comparison"""
    print("\n📊 Creating Figure S3: Codeword Distance...")

    # Load codeword distance results
    cd_path = RESULTS_DIR / "codeword_distances.csv"
    if not cd_path.exists():
        print("⚠️  Codeword distance data not found, skipping Figure S3")
        return

    cd_data = pd.read_csv(cd_path)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Panel A: Codeword distance bar chart
    loci = cd_data["locus"]
    cd_values = cd_data["codeword_distance"]
    colors_list = [COLORS[loc] for loc in loci]

    bars = ax1.bar(loci, cd_values, color=colors_list, alpha=0.7, edgecolor="black", linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, cd_values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax1.set_ylabel("Codeword Distance (1 - min LSSIM)", fontsize=11)
    ax1.set_title("H4: Codeword Distance\n(Hypothesis REJECTED)", fontsize=12, fontweight="bold")
    ax1.set_ylim(0, 0.16)

    # Add expected vs actual annotation
    ax1.text(
        0.98,
        0.05,
        "Expected: HBB > TP53 > BRCA1\nActual: HBB > BRCA1 > TP53\n\nTP53 anomaly: min_LSSIM=0.944\n(very high structural stability)",
        transform=ax1.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
        bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.3),
    )

    # Panel B: Sensitive variant fraction
    frac_below_095 = cd_data["frac_below_095"] * 100  # Convert to percentage

    bars = ax2.bar(
        loci, frac_below_095, color=colors_list, alpha=0.7, edgecolor="black", linewidth=1.5
    )

    for bar, val in zip(bars, frac_below_095):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{val:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax2.set_ylabel("Disruptive Variants (LSSIM < 0.95) [%]", fontsize=11)
    ax2.set_title("Structural Variance\n(High in HBB only)", fontsize=12, fontweight="bold")

    # Add interpretation
    ax2.text(
        0.98,
        0.95,
        "HBB: 19.9% (unique)\nBRCA1: 0.7%\nTP53: 0.2%\n\nReinterpretation:\nDosage-sensitivity =\nhigh structural VARIANCE",
        transform=ax2.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.3),
    )

    plt.tight_layout()
    output_path = FIGURES_DIR / "spectral_S3_codeword_distance.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_figure_4_lssim_distributions():
    """Figure S4: LSSIM Distribution Comparison"""
    print("\n📊 Creating Figure S4: LSSIM Distributions...")

    # Load atlases
    atlases = {
        "HBB": RESULTS_DIR / "HBB_Unified_Atlas.csv",
        "TP53": RESULTS_DIR / "TP53_Unified_Atlas_300kb.csv",
        "BRCA1": RESULTS_DIR / "BRCA1_Unified_Atlas_400kb.csv",
    }

    data = []
    for locus, path in atlases.items():
        if not path.exists():
            print(f"⚠️  {locus} atlas not found")
            continue

        df = pd.read_csv(path)
        lssim = df["ARCHCODE_LSSIM"].dropna()
        data.append(pd.DataFrame({"Locus": locus, "LSSIM": lssim}))

    if not data:
        print("⚠️  No atlas data found, skipping Figure S4")
        return

    combined = pd.concat(data, ignore_index=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Panel A: Violin plot
    sns.violinplot(
        data=combined,
        x="Locus",
        y="LSSIM",
        ax=ax1,
        palette=[COLORS[loc] for loc in ["HBB", "TP53", "BRCA1"]],
        cut=0,
        inner="box",
    )

    ax1.axhline(0.95, color="red", linestyle="--", linewidth=1.5, label="Disruption threshold")
    ax1.set_ylabel("ARCHCODE LSSIM", fontsize=11)
    ax1.set_title("LSSIM Distribution by Locus", fontsize=12, fontweight="bold")
    ax1.legend(fontsize=9)

    # Add median annotations
    for idx, locus in enumerate(["HBB", "TP53", "BRCA1"]):
        locus_data = combined[combined["Locus"] == locus]["LSSIM"]
        median = locus_data.median()
        ax1.text(
            idx,
            median,
            f"  {median:.4f}",
            ha="left",
            va="center",
            fontsize=8,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )

    # Panel B: Histogram with KDE
    for locus, color in COLORS.items():
        locus_data = combined[combined["Locus"] == locus]["LSSIM"]
        ax2.hist(
            locus_data,
            bins=50,
            alpha=0.3,
            color=color,
            label=f"{locus} (n={len(locus_data)})",
            density=True,
        )

        # KDE
        from scipy.stats import gaussian_kde

        kde = gaussian_kde(locus_data)
        x_range = np.linspace(locus_data.min(), locus_data.max(), 200)
        ax2.plot(x_range, kde(x_range), color=color, linewidth=2)

    ax2.axvline(0.95, color="red", linestyle="--", linewidth=1.5, label="Threshold")
    ax2.set_xlabel("ARCHCODE LSSIM", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.set_title("LSSIM Distribution (KDE)", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=9)

    plt.tight_layout()
    output_path = FIGURES_DIR / "spectral_S4_lssim_distributions.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Saved: {output_path}")
    plt.close()


def main():
    print("=" * 70)
    print("TASK #24: CREATE SPECTRAL ANALYSIS FIGURES")
    print("=" * 70)

    setup_figure_dir()

    try:
        create_figure_1_sfi_validation()
    except Exception as e:
        print(f"⚠️  Figure S1 failed: {e}")

    try:
        create_figure_2_phase_boundary()
    except Exception as e:
        print(f"⚠️  Figure S2 failed: {e}")

    try:
        create_figure_3_codeword_distance()
    except Exception as e:
        print(f"⚠️  Figure S3 failed: {e}")

    try:
        create_figure_4_lssim_distributions()
    except Exception as e:
        print(f"⚠️  Figure S4 failed: {e}")

    print("\n" + "=" * 70)
    print("✅ FIGURE GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nFigures saved to: {FIGURES_DIR}")

    return 0


if __name__ == "__main__":
    exit(main())
