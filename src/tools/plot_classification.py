"""
Visualization module for Cross-Omics Orthogonality Detector

Создаёт scatter plots с цветовой кодировкой классификации.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Dict, Optional
from orthogonality_detector import classify_orthogonality


def plot_classification(
    A: np.ndarray,
    B: np.ndarray,
    labels: np.ndarray,
    result: Optional[Dict] = None,
    method_a_name: str = "Method A",
    method_b_name: str = "Method B",
    group_0_name: str = "Group 0",
    group_1_name: str = "Group 1",
    title: Optional[str] = None,
    figsize: tuple = (10, 8),
    save_path: Optional[str] = None,
    show: bool = True,
    **kwargs,
) -> plt.Figure:
    """
    Создаёт scatter plot с классификацией ортогональности.

    Параметры:
    ----------
    A : np.ndarray
        Предсказания метода A
    B : np.ndarray
        Предсказания метода B
    labels : np.ndarray
        Бинарные метки (0/1)
    result : Dict, optional
        Результат от classify_orthogonality(). Если None, вычисляется автоматически.
    method_a_name : str
        Название метода A (для оси X)
    method_b_name : str
        Название метода B (для оси Y)
    group_0_name : str
        Название группы 0 (например "Benign")
    group_1_name : str
        Название группы 1 (например "Pathogenic")
    title : str, optional
        Заголовок графика. Если None, генерируется автоматически.
    figsize : tuple
        Размер figure (width, height)
    save_path : str, optional
        Путь для сохранения figure (PNG)
    show : bool
        Показать график (plt.show())
    **kwargs
        Дополнительные параметры для classify_orthogonality()

    Возвращает:
    -----------
    matplotlib.figure.Figure
    """

    # Классификация (если не предоставлена)
    if result is None:
        result = classify_orthogonality(A, B, labels, **kwargs)

    classification = result["classification"]
    rho = result["rho"]
    p_corr = result["p_correlation"]

    # Цветовая схема
    color_map = {
        "CONCORDANT": "#2E86AB",  # Синий (согласны)
        "ORTHOGONAL": "#06A77D",  # Зелёный (дополняют)
        "WEAK-ORTHOGONAL": "#F77F00",  # Оранжевый (один сильнее)
        "CONFLICTING": "#D62828",  # Красный (конфликт)
        "AMBIGUOUS": "#6C757D",  # Серый (непонятно)
    }

    # Создание figure
    fig, ax = plt.subplots(figsize=figsize)

    # Scatter plot — разные цвета для групп
    group_0_mask = labels == 0
    group_1_mask = labels == 1

    ax.scatter(
        A[group_0_mask],
        B[group_0_mask],
        c="lightblue",
        s=100,
        alpha=0.6,
        edgecolors="navy",
        linewidth=1.5,
        label=group_0_name,
        marker="o",
    )

    ax.scatter(
        A[group_1_mask],
        B[group_1_mask],
        c="lightcoral",
        s=100,
        alpha=0.6,
        edgecolors="darkred",
        linewidth=1.5,
        label=group_1_name,
        marker="^",
    )

    # Регрессионная линия (для визуализации корреляции)
    z = np.polyfit(A, B, 1)
    p = np.poly1d(z)
    x_line = np.linspace(A.min(), A.max(), 100)
    ax.plot(
        x_line,
        p(x_line),
        color=color_map[classification],
        linewidth=2.5,
        linestyle="--",
        alpha=0.7,
        label=f"Regression (ρ={rho:.3f})",
    )

    # Оси
    ax.set_xlabel(method_a_name, fontsize=14, fontweight="bold")
    ax.set_ylabel(method_b_name, fontsize=14, fontweight="bold")

    # Заголовок
    if title is None:
        title = f"Classification: {classification}\n(ρ={rho:.3f}, p={p_corr:.4f})"
    ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

    # Grid
    ax.grid(True, alpha=0.3, linestyle=":", linewidth=0.8)

    # Legend (группы + regression)
    ax.legend(loc="best", fontsize=11, framealpha=0.9)

    # Текстовый блок с результатами классификации
    textstr = f"""
Classification: {classification}
Correlation: ρ = {rho:.3f} (p={p_corr:.4f})

Method A: p = {result['p_diff_A']:.4f}
Method B: p = {result['p_diff_B']:.4f}

N = {result['n']} ({result['n_group_0']} / {result['n_group_1']})
CV: A={result['cv_A']:.1f}%, B={result['cv_B']:.1f}%
    """.strip()

    # Цвет рамки по классификации
    box_color = color_map[classification]

    props = dict(
        boxstyle="round,pad=0.8", facecolor="white", edgecolor=box_color, linewidth=2.5, alpha=0.95
    )

    ax.text(
        0.02,
        0.98,
        textstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
        family="monospace",
    )

    # Цветовая легенда классификаций (внизу справа)
    legend_patches = []
    for cls, color in color_map.items():
        patch = mpatches.Patch(color=color, label=cls)
        legend_patches.append(patch)

    # Вторая легенда (classification types)
    legend2 = ax.legend(
        handles=legend_patches,
        loc="lower right",
        title="Classification Types",
        fontsize=9,
        framealpha=0.9,
        title_fontsize=10,
    )
    ax.add_artist(legend2)  # Добавляем вторую легенду (не заменяя первую)

    # Tight layout
    plt.tight_layout()

    # Сохранение
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Figure saved: {save_path}")

    # Показать
    if show:
        plt.show()

    return fig


def plot_batch(
    datasets: list,
    ncols: int = 2,
    figsize_per_plot: tuple = (6, 5),
    save_path: Optional[str] = None,
    **kwargs,
) -> plt.Figure:
    """
    Создаёт grid из scatter plots для нескольких датасетов.

    Параметры:
    ----------
    datasets : list of tuples
        [(name, A, B, labels, method_a_name, method_b_name), ...]
    ncols : int
        Количество колонок в grid
    figsize_per_plot : tuple
        Размер одного subplot
    save_path : str, optional
        Путь для сохранения
    **kwargs
        Параметры для classify_orthogonality()

    Возвращает:
    -----------
    matplotlib.figure.Figure
    """

    n_datasets = len(datasets)
    nrows = (n_datasets + ncols - 1) // ncols

    fig_width = figsize_per_plot[0] * ncols
    fig_height = figsize_per_plot[1] * nrows

    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_width, fig_height))
    axes = np.array(axes).flatten()  # Для единообразного доступа

    for idx, dataset_info in enumerate(datasets):
        if len(dataset_info) == 6:
            name, A, B, labels, method_a_name, method_b_name = dataset_info
        else:
            name, A, B, labels = dataset_info[:4]
            method_a_name = "Method A"
            method_b_name = "Method B"

        ax = axes[idx]

        # Классификация
        result = classify_orthogonality(A, B, labels, **kwargs)
        classification = result["classification"]
        rho = result["rho"]

        # Цветовая схема
        color_map = {
            "CONCORDANT": "#2E86AB",
            "ORTHOGONAL": "#06A77D",
            "WEAK-ORTHOGONAL": "#F77F00",
            "CONFLICTING": "#D62828",
            "AMBIGUOUS": "#6C757D",
        }

        # Scatter
        group_0_mask = labels == 0
        group_1_mask = labels == 1

        ax.scatter(
            A[group_0_mask],
            B[group_0_mask],
            c="lightblue",
            s=60,
            alpha=0.6,
            edgecolors="navy",
            linewidth=1,
        )
        ax.scatter(
            A[group_1_mask],
            B[group_1_mask],
            c="lightcoral",
            s=60,
            alpha=0.6,
            edgecolors="darkred",
            linewidth=1,
            marker="^",
        )

        # Regression line
        z = np.polyfit(A, B, 1)
        p = np.poly1d(z)
        x_line = np.linspace(A.min(), A.max(), 50)
        ax.plot(
            x_line,
            p(x_line),
            color=color_map[classification],
            linewidth=2,
            linestyle="--",
            alpha=0.7,
        )

        # Labels
        ax.set_xlabel(method_a_name, fontsize=10)
        ax.set_ylabel(method_b_name, fontsize=10)
        ax.set_title(f"{name}\n{classification} (ρ={rho:.3f})", fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3, linestyle=":", linewidth=0.6)

    # Hide empty subplots
    for idx in range(n_datasets, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"✅ Batch figure saved: {save_path}")

    return fig


# Пример использования
if __name__ == "__main__":
    print("Cross-Omics Orthogonality Detector - Visualization Demo\n")

    # Test: ARCHCODE × AlphaGenome (real data)
    import json

    print("Loading ARCHCODE × AlphaGenome data...")
    with open("../../results/alphagenome_pearl_vs_control.json", "r") as f:
        data = json.load(f)

    A = []
    B = []
    labels = []

    for variant in data["results"]:
        A.append(variant["archcode_ssim"])
        B.append(variant["cage_pct"])
        labels.append(1 if variant["group"] == "PEARL" else 0)

    A = np.array(A)
    B = np.array(B)
    labels = np.array(labels)

    print(f"Data loaded: N={len(A)} variants\n")

    # Plot
    fig = plot_classification(
        A,
        B,
        labels,
        method_a_name="ARCHCODE SSIM (structural)",
        method_b_name="AlphaGenome CAGE % (functional)",
        group_0_name="Benign controls",
        group_1_name="Pathogenic (pearls)",
        title="ARCHCODE × AlphaGenome: Mechanism Orthogonality",
        save_path="../../results/fig_orthogonality_archcode_alphag.png",
        show=False,  # Don't block in demo
    )

    print("\n✅ Visualization complete!")
    print("Figure saved: results/fig_orthogonality_archcode_alphag.png")
