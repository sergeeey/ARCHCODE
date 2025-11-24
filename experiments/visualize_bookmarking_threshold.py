"""Visualization: RS-10 Bookmarking Threshold Analysis.

Визуализация перколяционного перехода в bookmarking threshold.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_threshold_data(json_path: str | Path) -> dict:
    """Загрузить данные анализа порога."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_jaccard_vs_bookmarking(data: dict, output_dir: Path) -> None:
    """Построить Jaccard vs bookmarking_fraction."""
    print("[RS-10-Threshold-Viz] Building Jaccard vs bookmarking plot...")

    results = data.get("results", [])
    threshold_estimate = data.get("threshold_estimate")

    bookmarking_fractions = [r["bookmarking_fraction"] for r in results]
    final_jaccards = [r["final_jaccard"] for r in results]

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.plot(
        bookmarking_fractions,
        final_jaccards,
        "o-",
        linewidth=2,
        markersize=8,
        color="blue",
        label="Jaccard Index",
    )

    # Mark threshold
    if threshold_estimate:
        ax.axvline(
            x=threshold_estimate,
            color="red",
            linestyle="--",
            linewidth=2,
            alpha=0.7,
            label=f"Percolation Threshold (~{threshold_estimate:.2f})",
        )

    # Mark zones
    if threshold_estimate:
        ax.axvspan(0, threshold_estimate, alpha=0.1, color="red", label="Memory Loss Zone")
        ax.axvspan(threshold_estimate, 1.0, alpha=0.1, color="green", label="Memory Retention Zone")

    ax.set_xlabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
    ax.set_ylabel("Final Jaccard Index (after 20 cycles)", fontsize=12, fontweight="bold")
    ax.set_title("Bookmarking Threshold: Percolation-like Transition", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()

    output_path = output_dir / "bookmarking_threshold_jaccard.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Threshold-Viz] Saved: {output_path}")
    plt.close()


def plot_entropy_vs_bookmarking(data: dict, output_dir: Path) -> None:
    """Построить Entropy vs bookmarking_fraction."""
    print("[RS-10-Threshold-Viz] Building Entropy vs bookmarking plot...")

    results = data.get("results", [])
    threshold_estimate = data.get("threshold_estimate")

    bookmarking_fractions = [r["bookmarking_fraction"] for r in results]
    final_entropies = [r["final_entropy"] for r in results]

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.plot(
        bookmarking_fractions,
        final_entropies,
        "s-",
        linewidth=2,
        markersize=8,
        color="orange",
        label="Architecture Entropy",
    )

    # Mark threshold
    if threshold_estimate:
        ax.axvline(
            x=threshold_estimate,
            color="red",
            linestyle="--",
            linewidth=2,
            alpha=0.7,
            label=f"Percolation Threshold (~{threshold_estimate:.2f})",
        )

    ax.set_xlabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
    ax.set_ylabel("Final Entropy (after 20 cycles)", fontsize=12, fontweight="bold")
    ax.set_title("Entropy Growth vs Bookmarking Fraction", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()

    output_path = output_dir / "bookmarking_threshold_entropy.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Threshold-Viz] Saved: {output_path}")
    plt.close()


def plot_jaccard_curves(data: dict, output_dir: Path) -> None:
    """Построить Jaccard vs cycle для разных bookmarking fractions."""
    print("[RS-10-Threshold-Viz] Building Jaccard curves...")

    results = data.get("results", [])
    threshold_estimate = data.get("threshold_estimate")

    fig, ax = plt.subplots(figsize=(12, 8))

    colors = plt.cm.viridis(np.linspace(0, 1, len(results)))

    for i, result in enumerate(results):
        bookmarking_frac = result["bookmarking_fraction"]
        cycles = result.get("cycles", [])

        if not cycles:
            continue

        cycle_numbers = [c["cycle"] for c in cycles]
        jaccards = [c.get("jaccard_vs_baseline", 0.0) for c in cycles]

        # Highlight threshold region
        if threshold_estimate and abs(bookmarking_frac - threshold_estimate) < 0.1:
            linewidth = 3
            alpha = 1.0
        else:
            linewidth = 2
            alpha = 0.7

        ax.plot(
            cycle_numbers,
            jaccards,
            "o-",
            label=f"B={bookmarking_frac:.2f}",
            color=colors[i],
            linewidth=linewidth,
            markersize=4,
            alpha=alpha,
        )

    # Mark collapse threshold
    ax.axhline(y=0.3, color="red", linestyle="--", alpha=0.5, label="Collapse Threshold (0.3)")

    ax.set_xlabel("Cycle Number", fontsize=12, fontweight="bold")
    ax.set_ylabel("Jaccard Index vs Baseline", fontsize=12, fontweight="bold")
    ax.set_title("Memory Decay Through Cycles (Different Bookmarking Fractions)", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()

    output_path = output_dir / "bookmarking_threshold_curves.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Threshold-Viz] Saved: {output_path}")
    plt.close()


def main() -> None:
    """Главная функция визуализации."""
    import argparse

    parser = argparse.ArgumentParser(description="Visualize bookmarking threshold analysis")
    parser.add_argument(
        "--input",
        type=str,
        default="data/output/RS10_bookmarking_threshold_analysis.json",
        help="Path to threshold analysis JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="figures/RS10",
        help="Output directory for figures",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RS-10 Bookmarking Threshold Visualization")
    print("=" * 60)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\n[RS-10-Threshold-Viz] Loading data from: {args.input}")
    data = load_threshold_data(args.input)

    results = data.get("results", [])
    print(f"[RS-10-Threshold-Viz] Loaded {len(results)} bookmarking fractions")

    # Generate all figures
    print("\n[RS-10-Threshold-Viz] Generating figures...")

    plot_jaccard_vs_bookmarking(data, output_dir)
    plot_entropy_vs_bookmarking(data, output_dir)
    plot_jaccard_curves(data, output_dir)

    print("\n" + "=" * 60)
    print("✅ RS-10 Bookmarking Threshold Visualization Complete")
    print("=" * 60)
    print(f"\nFigures saved to: {output_dir}")
    print("\nGenerated figures:")
    print("  1. bookmarking_threshold_jaccard.png")
    print("  2. bookmarking_threshold_entropy.png")
    print("  3. bookmarking_threshold_curves.png")


if __name__ == "__main__":
    main()






