"""Visualization: RS-10 Experiment C - Pathological Bookmarking Defects & Multi-Cycle Drift.

Генерация publication-quality фигур для RS-10 Experiment C.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_pathological_data(json_path: str | Path) -> dict:
    """Загрузить данные патологического эксперимента."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_cycles_data(scenario: dict) -> dict:
    """
    Извлечь данные циклов из сценария.

    Returns:
        dict с массивами метрик по циклам
    """
    cycles = scenario.get("cycles", [])
    if not cycles:
        return {}

    return {
        "cycle_numbers": [c["cycle"] for c in cycles],
        "jaccard_vs_baseline": [c.get("jaccard_vs_baseline", 0.0) for c in cycles],
        "jaccard_vs_previous": [c.get("jaccard_vs_previous", 0.0) for c in cycles],
        "entropy": [c.get("entropy", 0.0) for c in cycles],
        "position_entropy": [c.get("position_entropy", 0.0) for c in cycles],
        "drift_distance": [c.get("drift_distance", 0.0) for c in cycles],
        "memory_retention_score": [c.get("memory_retention_score", 0.0) for c in cycles],
        "avg_stability": [c.get("avg_stability", 0.0) for c in cycles],
    }


def plot_drift_curves(data: dict, output_dir: Path) -> None:
    """Построить кривые дрейфа (Jaccard per cycle)."""
    print("[RS-10-C-Viz] Building drift curves...")

    fig, ax = plt.subplots(figsize=(12, 8))

    scenarios = data.get("scenarios", [])
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))

    for i, scenario in enumerate(scenarios):
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        bookmarking = scenario.get("bookmarking_fraction", 0.0)
        processivity = scenario.get("processivity", 1.0)

        # Label
        if "complete_loss" in scenario_name:
            label = "Complete Loss (B=0.0)"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect (B=0.3)"
        elif "threshold_sweep" in scenario_name:
            label = f"Threshold Sweep (B={bookmarking:.1f})"
        elif "compensation" in scenario_name:
            label = f"Compensation (P={processivity:.2f}, B=0.3)"
        else:
            label = scenario_name

        ax.plot(
            cycles_data["cycle_numbers"],
            cycles_data["jaccard_vs_baseline"],
            "o-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=4,
            alpha=0.8,
        )

    # Critical threshold line
    ax.axhline(y=0.3, color="red", linestyle="--", alpha=0.5, label="Collapse Threshold (0.3)")

    ax.set_xlabel("Cycle Number", fontsize=12, fontweight="bold")
    ax.set_ylabel("Jaccard Index vs Baseline (Architectural Memory)", fontsize=12, fontweight="bold")
    ax.set_title("Architectural Drift Through Cell Cycles", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()

    output_path = output_dir / "RS10_drift_curves.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-C-Viz] Saved: {output_path}")
    plt.close()


def plot_entropy_growth(data: dict, output_dir: Path) -> None:
    """Построить кривые роста энтропии."""
    print("[RS-10-C-Viz] Building entropy growth curves...")

    fig, ax = plt.subplots(figsize=(12, 8))

    scenarios = data.get("scenarios", [])
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))

    for i, scenario in enumerate(scenarios):
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        bookmarking = scenario.get("bookmarking_fraction", 0.0)

        # Label
        if "complete_loss" in scenario_name:
            label = "Complete Loss (B=0.0)"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect (B=0.3)"
        elif "threshold_sweep" in scenario_name:
            label = f"Threshold Sweep (B={bookmarking:.1f})"
        else:
            label = scenario_name

        ax.plot(
            cycles_data["cycle_numbers"],
            cycles_data["entropy"],
            "s-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=4,
            alpha=0.8,
        )

    # Zones
    ax.axhspan(0, 0.3, alpha=0.1, color="green", label="Memory Intact")
    ax.axhspan(0.7, 1.0, alpha=0.1, color="red", label="Memory Lost")

    ax.set_xlabel("Cycle Number", fontsize=12, fontweight="bold")
    ax.set_ylabel("Architecture Entropy (Memory Disruption)", fontsize=12, fontweight="bold")
    ax.set_title("Entropy Growth Through Cell Cycles", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()

    output_path = output_dir / "RS10_entropy_growth.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-C-Viz] Saved: {output_path}")
    plt.close()


def plot_drift_distance(data: dict, output_dir: Path) -> None:
    """Построить эволюцию drift distance."""
    print("[RS-10-C-Viz] Building drift distance evolution...")

    fig, ax = plt.subplots(figsize=(12, 8))

    scenarios = data.get("scenarios", [])
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))

    for i, scenario in enumerate(scenarios):
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        bookmarking = scenario.get("bookmarking_fraction", 0.0)

        # Label
        if "complete_loss" in scenario_name:
            label = "Complete Loss (B=0.0)"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect (B=0.3)"
        elif "threshold_sweep" in scenario_name:
            label = f"Threshold Sweep (B={bookmarking:.1f})"
        else:
            label = scenario_name

        ax.plot(
            cycles_data["cycle_numbers"],
            cycles_data["drift_distance"],
            "^-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=4,
            alpha=0.8,
        )

    # Critical threshold (20kb)
    ax.axhline(y=20000, color="red", linestyle="--", alpha=0.5, label="Critical Drift (20kb)")

    ax.set_xlabel("Cycle Number", fontsize=12, fontweight="bold")
    ax.set_ylabel("Average Drift Distance (bp)", fontsize=12, fontweight="bold")
    ax.set_title("Boundary Position Drift Through Cycles", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = output_dir / "RS10_drift_distance.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-C-Viz] Saved: {output_path}")
    plt.close()


def plot_memory_retention_heatmap(data: dict, output_dir: Path) -> None:
    """Построить heatmap памяти."""
    print("[RS-10-C-Viz] Building memory retention heatmap...")

    scenarios = data.get("scenarios", [])

    # Filter threshold sweep scenarios
    threshold_scenarios = [
        s for s in scenarios if "threshold_sweep" in s.get("scenario_name", "")
    ]

    if not threshold_scenarios:
        print("[RS-10-C-Viz] No threshold sweep scenarios found, skipping heatmap")
        return

    # Build matrix: bookmarking × cycle → memory retention
    bookmarking_values = sorted(set(s.get("bookmarking_fraction", 0.0) for s in threshold_scenarios))
    max_cycles = max(len(s.get("cycles", [])) for s in threshold_scenarios)

    matrix = np.full((len(bookmarking_values), max_cycles), np.nan)

    for scenario in threshold_scenarios:
        bookmarking = scenario.get("bookmarking_fraction", 0.0)
        cycles_data = extract_cycles_data(scenario)

        if bookmarking in bookmarking_values:
            b_idx = bookmarking_values.index(bookmarking)
            for cycle_idx, retention in enumerate(cycles_data.get("memory_retention_score", [])):
                if cycle_idx < max_cycles:
                    matrix[b_idx, cycle_idx] = retention

    fig, ax = plt.subplots(figsize=(12, 8))

    im = ax.imshow(
        matrix,
        aspect="auto",
        origin="lower",
        cmap="RdYlGn",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )

    # Labels
    ax.set_xlabel("Cycle Number", fontsize=12, fontweight="bold")
    ax.set_ylabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
    ax.set_title("Memory Retention Through Cycles", fontsize=14, fontweight="bold")

    # Ticks
    ax.set_yticks(range(len(bookmarking_values)))
    ax.set_yticklabels([f"{v:.1f}" for v in bookmarking_values])
    ax.set_xticks(range(0, max_cycles, max(1, max_cycles // 10)))
    ax.set_xticklabels(range(0, max_cycles, max(1, max_cycles // 10)))

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label="Memory Retention Score")
    cbar.ax.tick_params(labelsize=10)

    plt.tight_layout()

    output_path = output_dir / "RS10_memory_retention_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-C-Viz] Saved: {output_path}")
    plt.close()


def plot_combined_analysis(data: dict, output_dir: Path) -> None:
    """Построить комбинированный анализ (multi-panel)."""
    print("[RS-10-C-Viz] Building combined analysis...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    scenarios = data.get("scenarios", [])
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))

    # Panel A: Drift curves
    ax1 = axes[0, 0]
    for i, scenario in enumerate(scenarios[:5]):  # Limit to 5 for clarity
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        if "complete_loss" in scenario_name:
            label = "Complete Loss"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect"
        else:
            continue

        ax1.plot(
            cycles_data["cycle_numbers"],
            cycles_data["jaccard_vs_baseline"],
            "o-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=3,
        )

    ax1.axhline(y=0.3, color="red", linestyle="--", alpha=0.5)
    ax1.set_xlabel("Cycle Number", fontsize=11)
    ax1.set_ylabel("Jaccard Index", fontsize=11)
    ax1.set_title("A) Architectural Drift", fontsize=12, fontweight="bold")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel B: Entropy growth
    ax2 = axes[0, 1]
    for i, scenario in enumerate(scenarios[:5]):
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        if "complete_loss" in scenario_name:
            label = "Complete Loss"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect"
        else:
            continue

        ax2.plot(
            cycles_data["cycle_numbers"],
            cycles_data["entropy"],
            "s-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=3,
        )

    ax2.set_xlabel("Cycle Number", fontsize=11)
    ax2.set_ylabel("Entropy", fontsize=11)
    ax2.set_title("B) Entropy Growth", fontsize=12, fontweight="bold")
    ax2.legend(loc="best", fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Panel C: Drift distance
    ax3 = axes[1, 0]
    for i, scenario in enumerate(scenarios[:5]):
        cycles_data = extract_cycles_data(scenario)
        if not cycles_data:
            continue

        scenario_name = scenario.get("scenario_name", f"scenario_{i}")
        if "complete_loss" in scenario_name:
            label = "Complete Loss"
        elif "partial_defect" in scenario_name:
            label = "Partial Defect"
        else:
            continue

        ax3.plot(
            cycles_data["cycle_numbers"],
            cycles_data["drift_distance"],
            "^-",
            label=label,
            color=colors[i],
            linewidth=2,
            markersize=3,
        )

    ax3.axhline(y=20000, color="red", linestyle="--", alpha=0.5)
    ax3.set_xlabel("Cycle Number", fontsize=11)
    ax3.set_ylabel("Drift Distance (bp)", fontsize=11)
    ax3.set_title("C) Position Drift", fontsize=12, fontweight="bold")
    ax3.legend(loc="best", fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Panel D: Summary statistics
    ax4 = axes[1, 1]
    ax4.axis("off")

    # Extract summary statistics
    summary_text = "Summary Statistics:\n\n"
    for scenario in scenarios[:3]:
        scenario_name = scenario.get("scenario_name", "unknown")
        summary = scenario.get("summary", {})
        final_jaccard = summary.get("final_jaccard", 0.0)
        total_drift = summary.get("total_drift", 0.0)
        cycles_to_collapse = summary.get("cycles_to_collapse", "N/A")

        summary_text += f"{scenario_name}:\n"
        summary_text += f"  Final Jaccard: {final_jaccard:.3f}\n"
        summary_text += f"  Total Drift: {total_drift:.3f}\n"
        summary_text += f"  Cycles to Collapse: {cycles_to_collapse}\n\n"

    ax4.text(0.1, 0.5, summary_text, fontsize=10, verticalalignment="center", family="monospace")
    ax4.set_title("D) Summary", fontsize=12, fontweight="bold")

    plt.tight_layout()

    output_path = output_dir / "RS10_combined_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-C-Viz] Saved: {output_path}")
    plt.close()


def main() -> None:
    """Главная функция визуализации."""
    import argparse

    parser = argparse.ArgumentParser(description="Visualize RS-10 Experiment C results")
    parser.add_argument(
        "--input",
        type=str,
        default="data/output/RS10_pathological_bookmarking.json",
        help="Path to pathological experiment JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="figures/RS10",
        help="Output directory for figures",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RS-10 Experiment C Visualization")
    print("=" * 60)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\n[RS-10-C-Viz] Loading data from: {args.input}")
    data = load_pathological_data(args.input)

    scenarios = data.get("scenarios", [])
    print(f"[RS-10-C-Viz] Loaded {len(scenarios)} scenarios")

    # Generate all figures
    print("\n[RS-10-C-Viz] Generating figures...")

    plot_drift_curves(data, output_dir)
    plot_entropy_growth(data, output_dir)
    plot_drift_distance(data, output_dir)
    plot_memory_retention_heatmap(data, output_dir)
    plot_combined_analysis(data, output_dir)

    print("\n" + "=" * 60)
    print("✅ RS-10 Experiment C Visualization Complete")
    print("=" * 60)
    print(f"\nFigures saved to: {output_dir}")
    print("\nGenerated figures:")
    print("  1. RS10_drift_curves.png")
    print("  2. RS10_entropy_growth.png")
    print("  3. RS10_drift_distance.png")
    print("  4. RS10_memory_retention_heatmap.png")
    print("  5. RS10_combined_analysis.png")


if __name__ == "__main__":
    main()






