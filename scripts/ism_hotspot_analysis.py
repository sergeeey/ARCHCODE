#!/usr/bin/env python3
"""
AlphaGenome ISM Hotspot Analysis

Post-GATE-1 pivot: Identify functional hotspots in HBB promoter (not positional enrichment).

Hypothesis: AlphaGenome ISM-sensitive positions overlap with ClinVar pathogenic variants.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import fisher_exact

# Paths
DATA_PATH = Path("D:/ДНК/results/alphagenome_ism_promoter.json")
OUTPUT_JSON = Path("D:/ДНК/results/ism_hotspot_analysis.json")
OUTPUT_FIG = Path("D:/ДНК/results/fig_ism_hotspots.png")


def load_data():
    """Load AlphaGenome ISM scan data."""
    with open(DATA_PATH) as f:
        data = json.load(f)
    return pd.DataFrame(data["results"])


def identify_hotspots(df, threshold_pct=-10):
    """
    Identify ISM hotspots (positions with strong CAGE disruption).

    Hotspot = max_cage_pct < threshold (negative = disruption)
    """
    df["is_hotspot"] = df["max_cage_pct"] < threshold_pct

    hotspots = df[df["is_hotspot"]].copy()
    hotspots = hotspots.sort_values("max_cage_pct")  # Sort by strongest disruption

    return hotspots


def overlap_analysis(df):
    """Fisher exact test: pearls vs hotspots."""

    # Define hotspot threshold (top 20% strongest disruption)
    threshold = df["max_cage_pct"].quantile(0.2)

    df["is_hotspot"] = df["max_cage_pct"] < threshold

    # Contingency table
    #                Hotspot   Non-Hotspot
    # Pearl             a           b
    # Non-Pearl         c           d

    a = len(df[(df["is_pearl"] == True) & (df["is_hotspot"] == True)])
    b = len(df[(df["is_pearl"] == True) & (df["is_hotspot"] == False)])
    c = len(df[(df["is_pearl"] == False) & (df["is_hotspot"] == True)])
    d = len(df[(df["is_pearl"] == False) & (df["is_hotspot"] == False)])

    oddsratio, pvalue = fisher_exact([[a, b], [c, d]], alternative="greater")

    return {
        "contingency_table": {
            "pearls_in_hotspot": a,
            "pearls_not_hotspot": b,
            "non_pearls_in_hotspot": c,
            "non_pearls_not_hotspot": d,
        },
        "threshold_pct": float(threshold),
        "odds_ratio": float(oddsratio),
        "p_value": float(pvalue),
        "interpretation": "Pearls enrich in ISM hotspots" if pvalue < 0.05 else "No enrichment",
    }


def create_figure(df):
    """Create ISM hotspot lineplot."""

    fig, ax = plt.subplots(figsize=(14, 6))

    # Lineplot: position vs CAGE disruption
    ax.plot(
        df["pos"],
        df["max_cage_pct"],
        linewidth=2,
        color="#3498db",
        alpha=0.7,
        label="ISM CAGE delta",
    )

    # Fill negative region (disruption)
    ax.fill_between(
        df["pos"],
        0,
        df["max_cage_pct"],
        where=(df["max_cage_pct"] < 0),
        color="#e74c3c",
        alpha=0.3,
        label="Disruption (negative CAGE)",
    )

    # Fill positive region (activation)
    ax.fill_between(
        df["pos"],
        0,
        df["max_cage_pct"],
        where=(df["max_cage_pct"] > 0),
        color="#2ecc71",
        alpha=0.3,
        label="Activation (positive CAGE)",
    )

    # Mark pearl positions
    pearls = df[df["is_pearl"] == True]
    ax.scatter(
        pearls["pos"],
        pearls["max_cage_pct"],
        s=150,
        color="red",
        marker="D",
        edgecolor="black",
        linewidth=1.5,
        label=f"Pearl positions (N={len(pearls)})",
        zorder=5,
    )

    # Horizontal line at 0
    ax.axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.5)

    # Hotspot threshold (top 20% strongest disruption)
    threshold = df["max_cage_pct"].quantile(0.2)
    ax.axhline(
        y=threshold,
        color="orange",
        linestyle="--",
        linewidth=1.5,
        alpha=0.7,
        label=f"Hotspot threshold (20th percentile: {threshold:.1f}%)",
    )

    # Styling
    ax.set_xlabel("Genomic Position (chr11, GRCh38)", fontsize=12, fontweight="bold")
    ax.set_ylabel("ISM CAGE Disruption (%)", fontsize=12, fontweight="bold")
    ax.set_title(
        "AlphaGenome ISM: HBB Promoter Functional Hotspots\nPearl Positions (red diamonds) vs ISM Sensitivity",
        fontsize=14,
        fontweight="bold",
        pad=20,
    )

    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    # Format x-axis
    ax.ticklabel_format(style="plain", axis="x")

    plt.tight_layout()
    plt.savefig(OUTPUT_FIG, dpi=300, bbox_inches="tight")
    print(f"✓ Figure saved: {OUTPUT_FIG}")

    return fig


def main():
    """Run ISM hotspot analysis."""

    print("=" * 70)
    print("AlphaGenome ISM Hotspot Analysis — HBB Promoter")
    print("=" * 70)
    print()

    # Load data
    print(f"Loading ISM data from {DATA_PATH.name}...")
    df = load_data()

    print(f"✓ Loaded {len(df)} positions (chr11:{df['pos'].min()}-{df['pos'].max()})")
    print(f"✓ Pearl positions marked: {df['is_pearl'].sum()}")
    print()

    # Identify hotspots
    print("Identifying ISM hotspots (top 20% strongest disruption)...")
    threshold = df["max_cage_pct"].quantile(0.2)
    hotspots = df[df["max_cage_pct"] < threshold]

    print(f"✓ Hotspot threshold: CAGE < {threshold:.1f}%")
    print(f"✓ Hotspots identified: {len(hotspots)} positions")
    print()

    # Overlap analysis
    print("Testing pearl enrichment in ISM hotspots (Fisher exact test)...")
    overlap_result = overlap_analysis(df)

    print(f"  Contingency table:")
    print(f"    Pearls in hotspot: {overlap_result['contingency_table']['pearls_in_hotspot']}")
    print(f"    Pearls not hotspot: {overlap_result['contingency_table']['pearls_not_hotspot']}")
    print(
        f"    Non-pearls in hotspot: {overlap_result['contingency_table']['non_pearls_in_hotspot']}"
    )
    print(
        f"    Non-pearls not hotspot: {overlap_result['contingency_table']['non_pearls_not_hotspot']}"
    )
    print(f"  Odds ratio: {overlap_result['odds_ratio']:.2f}")
    print(f"  p-value: {overlap_result['p_value']:.4f}")
    print(f"  Interpretation: {overlap_result['interpretation']}")
    print()

    # Create figure
    print("Creating ISM hotspot figure...")
    create_figure(df)

    # Save results
    print("Saving results...")
    output = {
        "experiment": "AlphaGenome ISM hotspot analysis",
        "hypothesis": "AlphaGenome ISM-sensitive positions overlap with ClinVar pathogenic variants",
        "zone": {
            "chromosome": "chr11",
            "start": int(df["pos"].min()),
            "end": int(df["pos"].max()),
            "size_bp": int(df["pos"].max() - df["pos"].min() + 1),
        },
        "summary": {
            "total_positions": len(df),
            "pearl_positions": int(df["is_pearl"].sum()),
            "hotspot_threshold_pct": float(threshold),
            "hotspots_identified": len(hotspots),
        },
        "overlap_analysis": overlap_result,
        "top_hotspots": hotspots.head(10)[["pos", "max_cage_pct", "is_pearl"]].to_dict(
            orient="records"
        ),
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✓ Results saved: {OUTPUT_JSON}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"ISM scan: {len(df)} positions in HBB promoter")
    print(
        f"Pearl overlap: {overlap_result['contingency_table']['pearls_in_hotspot']}/{df['is_pearl'].sum()} pearls in hotspots"
    )
    print(f"Fisher exact: p={overlap_result['p_value']:.4f} ({overlap_result['interpretation']})")
    print()

    if overlap_result["p_value"] < 0.05:
        print(
            "✓ AlphaGenome ISM identifies functional hotspots overlapping with ClinVar pathogenic"
        )
    else:
        print("⚠ No significant enrichment — ISM hotspots do not align with pearl positions")
    print()


if __name__ == "__main__":
    main()
