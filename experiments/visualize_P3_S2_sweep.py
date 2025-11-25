"""Visualization: RS-09 Coupled Dynamics Sweep Phase Diagrams.

Построение heatmap для фазовой диаграммы стабильности TAD границ.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_sweep_results(json_path: str | Path) -> dict:
    """Загрузить результаты sweep эксперимента."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_phase_diagrams(
    results: dict,
    output_dir: Path | str = "data/output",
    prefix: str = "P3_S2_phase_diagram",
) -> None:
    """
    Построить фазовые диаграммы: stability, collapse, risk.

    Args:
        results: Результаты sweep эксперимента
        output_dir: Директория для сохранения графиков
        prefix: Префикс для имен файлов
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    phase_diagrams = results["phase_diagrams"]
    sweep_params = results["sweep_parameters"]
    nipbl_range = sweep_params["nipbl_range"]
    wapl_range = sweep_params["wapl_range"]

    # Convert to numpy arrays
    stability_matrix = np.array(phase_diagrams["stability_matrix"])
    collapse_matrix = np.array(phase_diagrams["collapse_matrix"])
    risk_matrix = np.array(phase_diagrams["risk_matrix"])

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (15, 5)
    plt.rcParams["font.size"] = 10

    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # 1. Stability Heatmap
    ax1 = axes[0]
    im1 = ax1.imshow(
        stability_matrix,
        aspect="auto",
        origin="lower",
        cmap="RdYlGn",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )
    ax1.set_xlabel("NIPBL Velocity Multiplier", fontsize=12, fontweight="bold")
    ax1.set_ylabel("WAPL Lifetime Factor", fontsize=12, fontweight="bold")
    ax1.set_title("Boundary Stability Landscape", fontsize=14, fontweight="bold")
    ax1.set_xticks(range(len(nipbl_range)))
    ax1.set_xticklabels([f"{v:.1f}" for v in nipbl_range])
    ax1.set_yticks(range(len(wapl_range)))
    ax1.set_yticklabels([f"{v:.1f}" for v in wapl_range])
    plt.colorbar(im1, ax=ax1, label="Average Stability Score")

    # Add phase transition boundaries
    transitions = results["phase_transitions"]["transitions"]
    if transitions:
        for trans in transitions[:10]:  # Limit to first 10 for clarity
            nipbl_idx = nipbl_range.index(trans["nipbl_velocity"])
            wapl_idx = wapl_range.index(trans["wapl_lifetime"])
            ax1.plot(nipbl_idx, wapl_idx, "ko", markersize=8, alpha=0.6)

    # 2. Collapse Probability Heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(
        collapse_matrix,
        aspect="auto",
        origin="lower",
        cmap="Reds",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )
    ax2.set_xlabel("NIPBL Velocity Multiplier", fontsize=12, fontweight="bold")
    ax2.set_ylabel("WAPL Lifetime Factor", fontsize=12, fontweight="bold")
    ax2.set_title("Collapse Probability Map", fontsize=14, fontweight="bold")
    ax2.set_xticks(range(len(nipbl_range)))
    ax2.set_xticklabels([f"{v:.1f}" for v in nipbl_range])
    ax2.set_yticks(range(len(wapl_range)))
    ax2.set_yticklabels([f"{v:.1f}" for v in wapl_range])
    plt.colorbar(im2, ax=ax2, label="Collapse Probability")

    # 3. Risk Heatmap
    ax3 = axes[2]
    im3 = ax3.imshow(
        risk_matrix,
        aspect="auto",
        origin="lower",
        cmap="YlOrRd",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )
    ax3.set_xlabel("NIPBL Velocity Multiplier", fontsize=12, fontweight="bold")
    ax3.set_ylabel("WAPL Lifetime Factor", fontsize=12, fontweight="bold")
    ax3.set_title("Oncogenic Risk Map", fontsize=14, fontweight="bold")
    ax3.set_xticks(range(len(nipbl_range)))
    ax3.set_xticklabels([f"{v:.1f}" for v in nipbl_range])
    ax3.set_yticks(range(len(wapl_range)))
    ax3.set_yticklabels([f"{v:.1f}" for v in wapl_range])
    plt.colorbar(im3, ax=ax3, label="Average Risk Score")

    plt.tight_layout()

    # Save figure
    output_path = output_dir / f"{prefix}_heatmaps.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Heatmaps saved: {output_path}")
    plt.close()

    # Create processivity contour plot
    plot_processivity_contour(
        results, output_dir, prefix=f"{prefix}_processivity"
    )


def plot_processivity_contour(
    results: dict,
    output_dir: Path | str = "data/output",
    prefix: str = "P3_S2_processivity",
) -> None:
    """
    Построить контурную диаграмму processivity.

    Args:
        results: Результаты sweep эксперимента
        output_dir: Директория для сохранения графиков
        prefix: Префикс для имени файла
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    sweep_params = results["sweep_parameters"]
    nipbl_range = sweep_params["nipbl_range"]
    wapl_range = sweep_params["wapl_range"]

    # Build processivity matrix
    processivity_matrix = []
    for wapl in wapl_range:
        row = []
        for nipbl in nipbl_range:
            row.append(nipbl * wapl)
        processivity_matrix.append(row)

    processivity_matrix = np.array(processivity_matrix)
    stability_matrix = np.array(results["phase_diagrams"]["stability_matrix"])

    # Create contour plot
    fig, ax = plt.subplots(figsize=(10, 8))

    # Create meshgrid
    X, Y = np.meshgrid(nipbl_range, wapl_range)

    # Plot stability contours
    contours = ax.contour(
        X, Y, stability_matrix, levels=10, colors="black", alpha=0.3, linewidths=1
    )
    ax.clabel(contours, inline=True, fontsize=8)

    # Fill contour
    im = ax.contourf(
        X,
        Y,
        stability_matrix,
        levels=20,
        cmap="RdYlGn",
        vmin=0.0,
        vmax=1.0,
        alpha=0.8,
    )

    # Mark phase transitions
    transitions = results["phase_transitions"]["transitions"]
    if transitions:
        trans_nipbl = [t["nipbl_velocity"] for t in transitions]
        trans_wapl = [t["wapl_lifetime"] for t in transitions]
        ax.scatter(
            trans_nipbl,
            trans_wapl,
            c="black",
            s=100,
            marker="x",
            linewidths=2,
            label="Phase Transitions",
            zorder=5,
        )

    # Mark WT and CdLS points
    ax.plot(1.0, 1.0, "bo", markersize=15, label="Wild-type", zorder=6)
    ax.plot(0.5, 1.0, "ro", markersize=15, label="CdLS", zorder=6)

    # Add processivity isolines
    processivity_levels = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    processivity_contours = ax.contour(
        X,
        Y,
        processivity_matrix,
        levels=processivity_levels,
        colors="blue",
        linestyles="--",
        alpha=0.5,
        linewidths=1,
    )
    ax.clabel(processivity_contours, inline=True, fontsize=8, fmt="P=%.1f")

    ax.set_xlabel("NIPBL Velocity Multiplier", fontsize=12, fontweight="bold")
    ax.set_ylabel("WAPL Lifetime Factor", fontsize=12, fontweight="bold")
    ax.set_title(
        "Phase Diagram: Stability vs Processivity", fontsize=14, fontweight="bold"
    )
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)

    plt.colorbar(im, ax=ax, label="Average Stability Score")

    plt.tight_layout()

    # Save figure
    output_path = output_dir / f"{prefix}_contour.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✅ Contour plot saved: {output_path}")
    plt.close()


def main() -> None:
    """Главная функция визуализации."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize RS-09 Coupled Dynamics Sweep results"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/output/P3_S2_coupled_sweep.json",
        help="Path to sweep results JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/output",
        help="Output directory for plots",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RS-09 Phase Diagram Visualization")
    print("=" * 60)

    # Load results
    print(f"\nLoading results from: {args.input}")
    results = load_sweep_results(args.input)

    # Print summary
    summary = results["summary"]
    print(f"\nSummary:")
    print(f"  Stability range: {summary['min_stability']:.3f} - {summary['max_stability']:.3f}")
    print(f"  Collapse range: {summary['min_collapse']:.3f} - {summary['max_collapse']:.3f}")
    if summary.get("critical_processivity"):
        print(f"  Critical processivity: {summary['critical_processivity']}")

    # Generate plots
    print("\nGenerating phase diagrams...")
    plot_phase_diagrams(results, output_dir=args.output_dir)

    print("\n" + "=" * 60)
    print("✅ Visualization Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()







