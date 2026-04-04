"""
Cross-locus summary figure for the taxonomy paper.

Panels:
    A — Горизонтальный bar chart |Δ LSSIM| по локусу (сортировка по убыванию)
    B — Structural calls per locus (тот же порядок, лог-шкала)
    C — Scatter tissue match vs Q2b count
    D — Tool blind-spot mini-heatmap (5 инструментов × 5 классов)

Источники данных:
    results/cross_locus_atlas_comparison.json  — метрики по локусу
    analysis/taxonomy_assignment_table.csv     — классы таксономии
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from scipy import stats

import structlog

# ПОЧЕМУ: structlog вместо print — единый формат для всего проекта
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_JSON = ROOT / "results" / "cross_locus_atlas_comparison.json"
TAX_CSV = ROOT / "analysis" / "taxonomy_assignment_table.csv"
OUT_DIR = ROOT / "figures" / "taxonomy"


# ---------------------------------------------------------------------------
# Константы цветов / классов
# ---------------------------------------------------------------------------

# ПОЧЕМУ: определяем цвет одним словарём — не дублируем в каждом панели
CLASS_COLORS: dict[str, str] = {
    "B": "#4472C4",  # синий — architecture
    "A": "#ED7D31",  # оранжевый — activity
    "C": "#70AD47",  # зелёный — mixed
    "D": "#A5A5A5",  # серый — coverage gap
    "E": "#FF0000",  # красный — tissue mismatch
    "E_partial": "#FF8080",  # светло-красный — partial tissue mismatch
    "B_tentative": "#9DC3E6",  # светло-синий — tentative B
    "unclassified": "#FFFFFF",  # белый
    "D+B": "#4472C4",  # штриховой blue/gray — обрабатывается отдельно
}

# Назначение классов по локусу (Panel A/B)
# ПОЧЕМУ: жёстко задаём из задания, т.к. taxonomy_assignment_table
# содержит несколько case_id per locus — нужен canonical class per locus
LOCUS_CLASS: dict[str, str] = {
    "HBB": "B",
    "TERT": "D+B",
    "BCL11A": "unclassified",
    "PTEN": "unclassified",
    "MLH1": "D",
    "TP53": "B_tentative",
    "CFTR": "D",
    "GJB2": "E",
    "GATA1": "unclassified",
    "SCN5A": "E",
    "LDLR": "E_partial",
    "HBA1": "unclassified",
    "BRCA1": "D+B",
}

# Аннотации на панели A
LOCUS_ANNOTATIONS: dict[str, str] = {
    "SCN5A": "→B with cardiac",
}

# Тканевое совпадение per locus (из evidence_bundle + EXP-003 данных)
# ПОЧЕМУ: значения извлечены из taxonomy_assignment_table.csv (поле evidence_bundle)
# и из cross_locus_atlas_comparison.json; HBA1/BCL11A/GATA1/PTEN не имеют
# явного tissue_match в таблице — их помечаем как NaN
TISSUE_MATCH: dict[str, float] = {
    "HBB": 1.0,
    "TERT": 0.5,
    "BCL11A": float("nan"),
    "PTEN": float("nan"),
    "MLH1": 0.5,
    "TP53": 0.5,
    "CFTR": 0.0,
    "GJB2": 0.0,
    "GATA1": float("nan"),
    "SCN5A": 0.0,
    "LDLR": 0.0,
    "HBA1": float("nan"),
    "BRCA1": 0.5,
}


# ---------------------------------------------------------------------------
# Загрузка данных
# ---------------------------------------------------------------------------


def load_atlas(path: Path) -> pd.DataFrame:
    """Загружает JSON кросс-локусного атласа и возвращает DataFrame."""
    with path.open() as fh:
        raw: dict[str, Any] = json.load(fh)

    rows = []
    for entry in raw["loci"]:
        locus_key = entry["locus"]
        # Нормализуем имя: убираем суффикс размера
        name = locus_key.split("_")[0].upper()
        rows.append(
            {
                "locus_key": locus_key,
                "locus": name,
                "total_variants": entry["total_variants"],
                "pathogenic_n": entry["pathogenic_n"],
                "structural_calls": entry["structural_pathogenic"],
                "delta_lssim": entry["delta_lssim"],
                "abs_delta": abs(entry["delta_lssim"]),
            }
        )
    df = pd.DataFrame(rows)
    log.info("atlas_loaded", n_loci=len(df))
    return df


def load_taxonomy(path: Path) -> pd.DataFrame:
    """Загружает таблицу классов таксономии (primary case per locus)."""
    df = pd.read_csv(path)
    log.info("taxonomy_loaded", n_rows=len(df))
    return df


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------


def get_bar_style(
    class_label: str,
) -> dict[str, Any]:
    """
    Возвращает kwargs для ax.barh() с учётом штриховки для D+B классов.

    ПОЧЕМУ: hatching не поддерживается через единый color — нужен отдельный
    patch для hatch-контура (edgecolor) и заливка базовым цветом.
    """
    if class_label == "D+B":
        return {
            "color": CLASS_COLORS["B"],
            "hatch": "///",
            "edgecolor": CLASS_COLORS["D"],
            "linewidth": 0.8,
        }
    color = CLASS_COLORS.get(class_label, "#CCCCCC")
    return {
        "color": color,
        "edgecolor": "black" if color == "#FFFFFF" else "none",
        "linewidth": 0.5,
    }


def make_legend_handles() -> list[mpatches.Patch]:
    """Создаёт список legend handles для классов таксономии."""
    specs = [
        ("B — Architecture", CLASS_COLORS["B"], None),
        ("A — Activity", CLASS_COLORS["A"], None),
        ("C — Mixed", CLASS_COLORS["C"], None),
        ("D — Coverage gap", CLASS_COLORS["D"], None),
        ("E — Tissue mismatch", CLASS_COLORS["E"], None),
        ("E partial", CLASS_COLORS["E_partial"], None),
        ("B tentative", CLASS_COLORS["B_tentative"], None),
        ("D+B (hatched)", CLASS_COLORS["B"], "///"),
        ("Unclassified", CLASS_COLORS["unclassified"], None),
    ]
    handles = []
    for label, color, hatch in specs:
        patch = mpatches.Patch(
            facecolor=color,
            edgecolor="black",
            hatch=hatch or "",
            label=label,
            linewidth=0.5,
        )
        handles.append(patch)
    return handles


# ---------------------------------------------------------------------------
# Панель A — |Δ LSSIM| горизонтальный bar chart
# ---------------------------------------------------------------------------


def plot_panel_a(ax: plt.Axes, df: pd.DataFrame) -> None:
    """
    Горизонтальные бары |Δ LSSIM| отсортированы по убыванию.
    Цвет определяется классом таксономии.
    """
    # ПОЧЕМУ: HBB имеет положительный delta (+0.0049) — берём abs для
    # единообразной сортировки по величине сигнала
    sorted_df = df.sort_values("abs_delta", ascending=True).reset_index(drop=True)

    for i, row in sorted_df.iterrows():
        cls = LOCUS_CLASS.get(row["locus"], "unclassified")
        style = get_bar_style(cls)
        ax.barh(i, row["abs_delta"], height=0.7, **style)

        # Подпись HBB с реальным значением
        if row["locus"] == "HBB":
            ax.text(
                row["abs_delta"] + 0.0002,
                i,
                f"Δ={row['delta_lssim']:+.4f}",
                va="center",
                ha="left",
                fontsize=8,
                color="#333333",
            )

        # Аннотация SCN5A
        ann = LOCUS_ANNOTATIONS.get(row["locus"])
        if ann:
            ax.text(
                row["abs_delta"] + 0.0002,
                i,
                ann,
                va="center",
                ha="left",
                fontsize=7,
                color="#666666",
                style="italic",
            )

    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df["locus"], fontsize=10)
    ax.set_xlabel("|Δ LSSIM| (pathogenic − benign)", fontsize=10)
    ax.set_title("A  |Δ LSSIM| by locus", fontsize=11, fontweight="bold", loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)

    # Легенда внутри панели A
    handles = make_legend_handles()
    ax.legend(
        handles=handles,
        loc="lower right",
        fontsize=7,
        framealpha=0.8,
        ncol=1,
        handlelength=1.5,
    )


# ---------------------------------------------------------------------------
# Панель B — Structural calls
# ---------------------------------------------------------------------------


def plot_panel_b(ax: plt.Axes, df: pd.DataFrame) -> None:
    """
    Количество структурных вызовов per locus (тот же порядок, что Panel A).
    Лог-шкала на оси X; ноль заменяем на 0.3 для отображения на log-шкале.
    """
    sorted_df = df.sort_values("abs_delta", ascending=True).reset_index(drop=True)

    # ПОЧЕМУ: log(0) = -inf — используем 0.3 как визуальную метку "нет вызовов"
    MIN_LOG = 0.3

    for i, row in sorted_df.iterrows():
        cls = LOCUS_CLASS.get(row["locus"], "unclassified")
        style = get_bar_style(cls)
        val = row["structural_calls"] if row["structural_calls"] > 0 else MIN_LOG
        ax.barh(i, val, height=0.7, **style)

        # Подписываем реальное значение
        label_x = max(val * 1.05, MIN_LOG * 1.5)
        ax.text(
            label_x,
            i,
            str(int(row["structural_calls"])),
            va="center",
            ha="left",
            fontsize=8,
        )

    ax.set_xscale("log")
    ax.set_xlim(left=0.2)
    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df["locus"], fontsize=10)
    ax.set_xlabel("Structural calls (pathogenic)", fontsize=10)
    ax.set_title("B  Structural calls per locus", fontsize=11, fontweight="bold", loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)


# ---------------------------------------------------------------------------
# Панель C — Scatter tissue match vs Q2b count
# ---------------------------------------------------------------------------


def plot_panel_c(ax: plt.Axes, df: pd.DataFrame) -> None:
    """
    Scatter: X = tissue_match (0, 0.5, 1.0), Y = structural_calls (Q2b proxy).
    Размер точки пропорционален total_variants.
    Линия регрессии + Spearman ρ.
    Ключевые точки подписаны.

    ПОЧЕМУ: structural_calls = pathogenic variants below LSSIM threshold —
    это лучший доступный прокси Q2b из JSON-данных. Tissue_match берём из
    TISSUE_MATCH словаря (извлечено из evidence_bundle таксономической таблицы).
    """
    # Добавляем tissue_match в df
    plot_df = df.copy()
    plot_df["tissue_match"] = plot_df["locus"].map(TISSUE_MATCH)

    # Убираем строки без tissue_match (HBA1, BCL11A, PTEN, GATA1 = NaN)
    plot_df = plot_df.dropna(subset=["tissue_match"]).reset_index(drop=True)

    # Нормализуем размер точки
    size_raw = plot_df["total_variants"].values
    size_norm = 30 + 400 * (size_raw / size_raw.max())

    # Jitter по X для разделения точек с одинаковым tissue_match
    rng = np.random.default_rng(42)
    jitter = rng.uniform(-0.03, 0.03, size=len(plot_df))
    x = plot_df["tissue_match"].values + jitter
    y = plot_df["structural_calls"].values

    # Цвета по классу
    colors = [
        CLASS_COLORS.get(LOCUS_CLASS.get(locus, "unclassified"), "#AAAAAA")
        for locus in plot_df["locus"]
    ]
    # Белые точки плохо видны → заменяем на светло-серые
    colors = ["#CCCCCC" if c == "#FFFFFF" else c for c in colors]

    ax.scatter(
        x, y, s=size_norm, c=colors, alpha=0.85, edgecolors="black", linewidths=0.5, zorder=3
    )

    # Регрессионная линия (по исходным x без jitter)
    x_orig = plot_df["tissue_match"].values
    if len(np.unique(x_orig)) > 1:
        slope, intercept, _, _, _ = stats.linregress(x_orig, y)
        x_line = np.linspace(x_orig.min() - 0.05, x_orig.max() + 0.05, 100)
        ax.plot(x_line, slope * x_line + intercept, "k--", linewidth=1.2, alpha=0.6)

    # Spearman ρ
    rho, pval = stats.spearmanr(x_orig, y)
    ax.text(
        0.97,
        0.97,
        f"Spearman ρ = {rho:.2f}\np = {pval:.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#AAAAAA", alpha=0.8),
    )

    # Подписи ключевых точек
    labels_to_show = {"HBB", "SCN5A", "GJB2"}
    for _, row in plot_df.iterrows():
        if row["locus"] in labels_to_show:
            jit_val = jitter[plot_df[plot_df["locus"] == row["locus"]].index[0]]
            ax.annotate(
                row["locus"],
                xy=(row["tissue_match"] + jit_val, row["structural_calls"]),
                xytext=(8, 4),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
                arrowprops=dict(arrowstyle="-", color="#555555", lw=0.8),
            )

    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xticklabels(["0.0\n(mismatch)", "0.5\n(partial)", "1.0\n(matched)"], fontsize=9)
    ax.set_xlabel("Tissue match score", fontsize=10)
    ax.set_ylabel("Structural calls (pathogenic)", fontsize=10)
    ax.set_title(
        "C  Tissue match vs structural signal",
        fontsize=11,
        fontweight="bold",
        loc="left",
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Размер-легенда
    for sz_val in [100, 1000, 5000, 10000]:
        if sz_val <= size_raw.max():
            sz_pt = 30 + 400 * (sz_val / size_raw.max())
            ax.scatter(
                [],
                [],
                s=sz_pt,
                c="gray",
                alpha=0.6,
                edgecolors="black",
                linewidths=0.5,
                label=f"n={sz_val:,}",
            )
    ax.legend(title="Total variants", fontsize=8, title_fontsize=8, loc="upper left")


# ---------------------------------------------------------------------------
# Панель D — Tool blind spot heatmap
# ---------------------------------------------------------------------------


def plot_panel_d(ax: plt.Axes) -> None:
    """
    Мини-тепловая карта 5 инструментов × 5 классов.
    Значения: 1=Detects (green), 0=Blind (red), 0.5=Partial (yellow).
    """
    tools = ["VEP", "CADD", "MPRA", "CRISPRi", "ARCHCODE"]
    classes = ["A\n(Activity)", "B\n(Architecture)", "C\n(Mixed)", "D\n(Coverage)", "E\n(Tissue)"]

    # ПОЧЕМУ: матрица кодирована числами для colormap — не строками
    # 1.0 = green (detects), 0.0 = red (blind), 0.5 = yellow (partial)
    matrix = np.array(
        [
            # A     B     C     D     E
            [1.0, 0.0, 0.5, 0.0, 0.0],  # VEP
            [1.0, 0.0, 0.5, 0.0, 0.0],  # CADD
            [1.0, 0.0, 0.5, 0.0, 0.0],  # MPRA
            [1.0, 0.0, 0.5, 0.0, 0.5],  # CRISPRi
            [0.0, 1.0, 0.5, 1.0, 0.0],  # ARCHCODE
        ]
    )

    # Кастомный colormap: red → yellow → green
    # ПОЧЕМУ: ListedColormap с 3 значениями точно соответствует 0/0.5/1
    cmap = ListedColormap(["#FF4444", "#FFD700", "#44BB44"])
    bounds = [-0.25, 0.25, 0.75, 1.25]
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    # Подписи ячеек
    labels_map = {0.0: "Blind", 0.5: "Partial", 1.0: "Detects"}
    for i in range(len(tools)):
        for j in range(len(classes)):
            val = matrix[i, j]
            txt = labels_map[val]
            # Темный текст для светлых ячеек (желтых)
            text_color = "black" if val == 0.5 else "white"
            ax.text(
                j, i, txt, ha="center", va="center", fontsize=9, color=text_color, fontweight="bold"
            )

    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, fontsize=9)
    ax.set_yticks(range(len(tools)))
    ax.set_yticklabels(tools, fontsize=10)
    ax.set_title("D  Tool blind-spot matrix", fontsize=11, fontweight="bold", loc="left")

    # Легенда
    legend_patches = [
        mpatches.Patch(facecolor="#44BB44", label="Detects"),
        mpatches.Patch(facecolor="#FFD700", label="Partial"),
        mpatches.Patch(facecolor="#FF4444", label="Blind"),
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower right",
        bbox_to_anchor=(1.0, -0.25),
        ncol=3,
        fontsize=9,
        framealpha=0.9,
    )

    # Без gridlines на heatmap (по заданию)
    ax.grid(False)


# ---------------------------------------------------------------------------
# Главная функция сборки фигуры
# ---------------------------------------------------------------------------


def build_figure(df: pd.DataFrame) -> plt.Figure:
    """
    Собирает 4-панельную фигуру 2×2, ~12×10 дюймов.
    """
    fig, axes = plt.subplots(
        2,
        2,
        figsize=(12, 10),
        gridspec_kw={"hspace": 0.45, "wspace": 0.38},
    )

    ax_a, ax_b = axes[0, 0], axes[0, 1]
    ax_c, ax_d = axes[1, 0], axes[1, 1]

    # ПОЧЕМУ: единый стиль белого фона задаём через rcParams,
    # а не поверх каждой оси — одна точка изменения
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.family": "sans-serif",
            "font.size": 10,
        }
    )

    plot_panel_a(ax_a, df)
    plot_panel_b(ax_b, df)
    plot_panel_c(ax_c, df)
    plot_panel_d(ax_d)

    fig.suptitle(
        "Cross-locus summary: ARCHCODE taxonomy framework",
        fontsize=13,
        fontweight="bold",
        y=1.01,
    )
    return fig


# ---------------------------------------------------------------------------
# Сохранение
# ---------------------------------------------------------------------------


def save_figure(fig: plt.Figure, out_dir: Path) -> None:
    """Сохраняет фигуру в PDF и PNG (300 DPI) в указанную директорию."""
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / "fig_crosslocus_summary.pdf"
    png_path = out_dir / "fig_crosslocus_summary.png"

    fig.savefig(pdf_path, bbox_inches="tight", dpi=300, format="pdf")
    fig.savefig(png_path, bbox_inches="tight", dpi=300, format="png")

    log.info("figure_saved", pdf=str(pdf_path), png=str(png_path))


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------


def main() -> None:
    """Генерирует кросс-локусную summary фигуру для статьи по таксономии."""
    log.info("start", script="plot_taxonomy_crosslocus_summary.py")

    if not DATA_JSON.exists():
        raise FileNotFoundError(f"JSON not found: {DATA_JSON}")
    if not TAX_CSV.exists():
        raise FileNotFoundError(f"CSV not found: {TAX_CSV}")

    df_atlas = load_atlas(DATA_JSON)
    load_taxonomy(TAX_CSV)  # проверка файла; данные используются через LOCUS_CLASS/TISSUE_MATCH

    # Проверяем что все 13 локусов на месте
    expected_n = 13
    if len(df_atlas) != expected_n:
        log.warning("unexpected_locus_count", got=len(df_atlas), expected=expected_n)

    fig = build_figure(df_atlas)
    save_figure(fig, OUT_DIR)
    plt.close(fig)

    log.info("done")


if __name__ == "__main__":
    main()
