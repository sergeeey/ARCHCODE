"""Visualization: RS-10 Experiment B - Processivity × Bookmarking Matrix.

Генерация publication-quality фигур для RS-10 Experiment B.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_matrix_data(json_path: str | Path) -> dict:
    """Загрузить данные матричного эксперимента."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_2d_matrix(
    data: dict, metric_key: str = "avg_stability_after"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Построить 2D матрицу из данных эксперимента.

    Args:
        data: Данные эксперимента
        metric_key: Ключ метрики в metrics

    Returns:
        (X, Y, Z) где X=processivity, Y=bookmarking, Z=metric
    """
    grid = data["grid"]
    successful_runs = [r for r in grid if "error" not in r]

    # Уникальные значения
    processivity_values = sorted(set(r["processivity"] for r in successful_runs))
    bookmarking_values = sorted(set(r["bookmarking_fraction"] for r in successful_runs))

    # Создать матрицу
    matrix = np.full((len(bookmarking_values), len(processivity_values)), np.nan)

    # Заполнить матрицу
    for run in successful_runs:
        p_idx = processivity_values.index(run["processivity"])
        b_idx = bookmarking_values.index(run["bookmarking_fraction"])
        metric_value = run["metrics"].get(metric_key, np.nan)
        matrix[b_idx, p_idx] = metric_value

    # Создать meshgrid
    X, Y = np.meshgrid(processivity_values, bookmarking_values)

    return X, Y, matrix


def plot_stability_heatmap(data: dict, output_dir: Path) -> None:
    """Построить heatmap стабильности."""
    print("[RS-10-Viz] Building stability heatmap...")

    X, Y, Z = build_2d_matrix(data, "avg_stability_after")

    fig, ax = plt.subplots(figsize=(10, 8))

    # Heatmap
    im = ax.imshow(
        Z,
        aspect="auto",
        origin="lower",
        cmap="RdYlGn",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )

    # Contour lines
    contours = ax.contour(
        X, Y, Z, levels=[0.4, 0.5, 0.7], colors="black", alpha=0.5, linewidths=1.5
    )
    ax.clabel(contours, inline=True, fontsize=10, fmt="%.2f")

    # Labels
    ax.set_xlabel("Processivity (NIPBL × WAPL)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
    ax.set_title(
        "Architectural Stability After Mitosis Recovery", fontsize=14, fontweight="bold"
    )

    # Ticks
    processivity_values = sorted(set(r["processivity"] for r in data["grid"] if "error" not in r))
    bookmarking_values = sorted(
        set(r["bookmarking_fraction"] for r in data["grid"] if "error" not in r)
    )
    ax.set_xticks(range(len(processivity_values)))
    ax.set_xticklabels([f"{v:.2f}" for v in processivity_values])
    ax.set_yticks(range(len(bookmarking_values)))
    ax.set_yticklabels([f"{v:.2f}" for v in bookmarking_values])

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label="Average Stability After Recovery")
    cbar.ax.tick_params(labelsize=10)

    plt.tight_layout()

    output_path = output_dir / "RS10_stability_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Viz] Saved: {output_path}")
    plt.close()


def plot_jaccard_heatmap(data: dict, output_dir: Path) -> None:
    """Построить heatmap Jaccard index (архитектурная память)."""
    print("[RS-10-Viz] Building Jaccard heatmap...")

    X, Y, Z = build_2d_matrix(data, "jaccard_stable")

    fig, ax = plt.subplots(figsize=(10, 8))

    # Heatmap
    im = ax.imshow(
        Z,
        aspect="auto",
        origin="lower",
        cmap="Blues",
        vmin=0.0,
        vmax=1.0,
        interpolation="bilinear",
    )

    # Contour lines для критических значений
    contours = ax.contour(
        X, Y, Z, levels=[0.3, 0.5, 0.7], colors="white", alpha=0.8, linewidths=2
    )
    ax.clabel(contours, inline=True, fontsize=10, fmt="%.2f", colors="white")

    # Labels
    ax.set_xlabel("Processivity (NIPBL × WAPL)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Bookmarking Fraction", fontsize=12, fontweight="bold")
    ax.set_title(
        "Architectural Memory Recovery (Jaccard Index)", fontsize=14, fontweight="bold"
    )

    # Ticks
    processivity_values = sorted(set(r["processivity"] for r in data["grid"] if "error" not in r))
    bookmarking_values = sorted(
        set(r["bookmarking_fraction"] for r in data["grid"] if "error" not in r)
    )
    ax.set_xticks(range(len(processivity_values)))
    ax.set_xticklabels([f"{v:.2f}" for v in processivity_values])
    ax.set_yticks(range(len(bookmarking_values)))
    ax.set_yticklabels([f"{v:.2f}" for v in bookmarking_values])

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label="Jaccard Index (Architectural Memory)")
    cbar.ax.tick_params(labelsize=10)

    plt.tight_layout()

    output_path = output_dir / "RS10_jaccard_heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Viz] Saved: {output_path}")
    plt.close()


def plot_3d_memory_surface(data: dict, output_dir: Path) -> None:
    """Построить 3D поверхность архитектурной памяти."""
    print("[RS-10-Viz] Building 3D memory surface...")

    X, Y, Z = build_2d_matrix(data, "jaccard_stable")

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection="3d")

    # Surface plot
    surf = ax.plot_surface(
        X, Y, Z, cmap="viridis", alpha=0.8, linewidth=0, antialiased=True
    )

    # Labels
    ax.set_xlabel("Processivity", fontsize=11, fontweight="bold")
    ax.set_ylabel("Bookmarking Fraction", fontsize=11, fontweight="bold")
    ax.set_zlabel("Jaccard Index (Memory)", fontsize=11, fontweight="bold")
    ax.set_title(
        "3D Memory Surface: Architectural Recovery Landscape", fontsize=13, fontweight="bold"
    )

    # Colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, label="Jaccard Index")

    # View angle
    ax.view_init(elev=30, azim=45)

    plt.tight_layout()

    output_path = output_dir / "RS10_3d_memory_surface.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Viz] Saved: {output_path}")
    plt.close()


def plot_critical_lines(data: dict, output_dir: Path) -> None:
    """Построить график критических линий."""
    print("[RS-10-Viz] Building critical lines plot...")

    grid = data["grid"]
    successful_runs = [r for r in grid if "error" not in r]

    # Группировать по processivity
    processivity_groups: dict[float, list[dict]] = {}
    for run in successful_runs:
        p = run["processivity"]
        if p not in processivity_groups:
            processivity_groups[p] = []
        processivity_groups[p].append(run)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Для каждого уровня processivity найти минимальный bookmarking для восстановления
    processivity_values = sorted(processivity_groups.keys())
    min_bookmarking_jaccard_05 = []
    min_bookmarking_jaccard_07 = []

    for p in processivity_values:
        runs = sorted(processivity_groups[p], key=lambda x: x["bookmarking_fraction"])

        # Найти минимальный bookmarking для Jaccard > 0.5
        min_b_05 = None
        for run in runs:
            if run["metrics"]["jaccard_stable"] >= 0.5:
                min_b_05 = run["bookmarking_fraction"]
                break

        # Найти минимальный bookmarking для Jaccard > 0.7
        min_b_07 = None
        for run in runs:
            if run["metrics"]["jaccard_stable"] >= 0.7:
                min_b_07 = run["bookmarking_fraction"]
                break

        min_bookmarking_jaccard_05.append(min_b_05 if min_b_05 is not None else 1.0)
        min_bookmarking_jaccard_07.append(min_b_07 if min_b_07 is not None else 1.0)

    # Plot lines
    ax.plot(
        processivity_values,
        min_bookmarking_jaccard_05,
        "o-",
        label="Jaccard ≥ 0.5 (Partial Recovery)",
        linewidth=2,
        markersize=8,
    )
    ax.plot(
        processivity_values,
        min_bookmarking_jaccard_07,
        "s-",
        label="Jaccard ≥ 0.7 (Full Recovery)",
        linewidth=2,
        markersize=8,
    )

    # Fill regions
    ax.fill_between(
        processivity_values,
        0,
        min_bookmarking_jaccard_05,
        alpha=0.2,
        color="red",
        label="Failure Zone",
    )
    ax.fill_between(
        processivity_values,
        min_bookmarking_jaccard_05,
        min_bookmarking_jaccard_07,
        alpha=0.2,
        color="yellow",
        label="Partial Recovery",
    )
    ax.fill_between(
        processivity_values,
        min_bookmarking_jaccard_07,
        1.0,
        alpha=0.2,
        color="green",
        label="Full Recovery",
    )

    # Labels
    ax.set_xlabel("Processivity (NIPBL × WAPL)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Minimum Bookmarking Fraction Required", fontsize=12, fontweight="bold")
    ax.set_title("Critical Recovery Thresholds", fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.1)

    plt.tight_layout()

    output_path = output_dir / "RS10_critical_lines.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Viz] Saved: {output_path}")
    plt.close()


def plot_bookmarking_compensation(data: dict, output_dir: Path) -> None:
    """Построить анализ компенсации bookmarking."""
    print("[RS-10-Viz] Building bookmarking compensation analysis...")

    grid = data["grid"]
    successful_runs = [r for r in grid if "error" not in r]

    # Группировать по processivity
    processivity_groups: dict[float, list[dict]] = {}
    for run in successful_runs:
        p = run["processivity"]
        if p not in processivity_groups:
            processivity_groups[p] = []
        processivity_groups[p].append(run)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Panel A: Stability vs Bookmarking
    ax1 = axes[0]
    processivity_levels = sorted(processivity_groups.keys())
    colors = plt.cm.viridis(np.linspace(0, 1, len(processivity_levels)))

    for i, p in enumerate(processivity_levels):
        runs = sorted(processivity_groups[p], key=lambda x: x["bookmarking_fraction"])
        bookmarking = [r["bookmarking_fraction"] for r in runs]
        stability = [r["metrics"]["avg_stability_after"] for r in runs]
        ax1.plot(
            bookmarking,
            stability,
            "o-",
            label=f"P={p:.2f}",
            color=colors[i],
            linewidth=2,
            markersize=6,
        )

    ax1.set_xlabel("Bookmarking Fraction", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Average Stability After Recovery", fontsize=11, fontweight="bold")
    ax1.set_title("A) Stability Recovery", fontsize=12, fontweight="bold")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Panel B: Jaccard vs Bookmarking
    ax2 = axes[1]
    for i, p in enumerate(processivity_levels):
        runs = sorted(processivity_groups[p], key=lambda x: x["bookmarking_fraction"])
        bookmarking = [r["bookmarking_fraction"] for r in runs]
        jaccard = [r["metrics"]["jaccard_stable"] for r in runs]
        ax2.plot(
            bookmarking,
            jaccard,
            "s-",
            label=f"P={p:.2f}",
            color=colors[i],
            linewidth=2,
            markersize=6,
        )

    ax2.set_xlabel("Bookmarking Fraction", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Jaccard Index (Memory)", fontsize=11, fontweight="bold")
    ax2.set_title("B) Architectural Memory", fontsize=12, fontweight="bold")
    ax2.legend(loc="best", fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Panel C: Minimum bookmarking vs Processivity
    ax3 = axes[2]
    min_bookmarking = []
    for p in processivity_levels:
        runs = sorted(processivity_groups[p], key=lambda x: x["bookmarking_fraction"])
        min_b = None
        for run in runs:
            if run["metrics"]["jaccard_stable"] >= 0.5:
                min_b = run["bookmarking_fraction"]
                break
        min_bookmarking.append(min_b if min_b is not None else 1.0)

    ax3.plot(processivity_levels, min_bookmarking, "o-", linewidth=2, markersize=8, color="red")
    ax3.fill_between(processivity_levels, min_bookmarking, 1.0, alpha=0.2, color="green")
    ax3.fill_between(processivity_levels, 0, min_bookmarking, alpha=0.2, color="red")

    ax3.set_xlabel("Processivity", fontsize=11, fontweight="bold")
    ax3.set_ylabel("Min Bookmarking for Recovery", fontsize=11, fontweight="bold")
    ax3.set_title("C) Compensation Threshold", fontsize=12, fontweight="bold")
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1.1)

    plt.tight_layout()

    output_path = output_dir / "RS10_bookmarking_compensation.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"[RS-10-Viz] Saved: {output_path}")
    plt.close()


def main() -> None:
    """Главная функция визуализации."""
    import argparse

    parser = argparse.ArgumentParser(description="Visualize RS-10 Experiment B results")
    parser.add_argument(
        "--input",
        type=str,
        default="data/output/RS10_processivity_bookmarking_matrix.json",
        help="Path to matrix experiment JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="figures/RS10",
        help="Output directory for figures",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RS-10 Experiment B Visualization")
    print("=" * 60)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\n[RS-10-Viz] Loading data from: {args.input}")
    data = load_matrix_data(args.input)

    successful_runs = [r for r in data["grid"] if "error" not in r]
    print(f"[RS-10-Viz] Loaded {len(successful_runs)} successful runs")

    # Generate all figures
    print("\n[RS-10-Viz] Generating figures...")

    plot_stability_heatmap(data, output_dir)
    plot_jaccard_heatmap(data, output_dir)
    plot_3d_memory_surface(data, output_dir)
    plot_critical_lines(data, output_dir)
    plot_bookmarking_compensation(data, output_dir)

    print("\n" + "=" * 60)
    print("✅ RS-10 Visualization Complete")
    print("=" * 60)
    print(f"\nFigures saved to: {output_dir}")
    print("\nGenerated figures:")
    print("  1. RS10_stability_heatmap.png")
    print("  2. RS10_jaccard_heatmap.png")
    print("  3. RS10_3d_memory_surface.png")
    print("  4. RS10_critical_lines.png")
    print("  5. RS10_bookmarking_compensation.png")


if __name__ == "__main__":
    main()






