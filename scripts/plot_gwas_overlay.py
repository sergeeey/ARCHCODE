"""
Визуализация GWAS × ARCHCODE overlay: 2-панельная фигура публикационного качества.

Panel A: Stacked bar chart — количество GWAS SNP по локусам и категориям интерпретации.
Panel B: Boxplot — распределение LSSIM для GWAS SNP vs все варианты атласа (HBB, BRCA1, TP53).
"""

import re
import sys
from pathlib import Path

# ПОЧЕМУ: Agg backend нужно установить ДО импорта pyplot — иначе matplotlib
# пытается инициализировать display backend и падает в headless-среде
import matplotlib  # noqa: E402

matplotlib.use("Agg")  # noqa: E402

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import structlog  # noqa: E402

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "analysis" / "gwas_archcode_overlay.csv"
FIGURES_DIR = ROOT / "figures"

ATLAS_FILES: dict[str, Path] = {
    "HBB": ROOT / "results" / "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": ROOT / "results" / "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": ROOT / "results" / "TP53_Unified_Atlas_300kb.csv",
}

# ---------------------------------------------------------------------------
# Палитра категорий
# ---------------------------------------------------------------------------
CATEGORY_ORDER = [
    "Structural disruption",
    "Structural disruption (pearl)",
    "Ambiguous",
    "Structural unlikely",
    "Needs simulation",
]

CATEGORY_COLORS: dict[str, str] = {
    "Structural disruption": "#c0392b",
    "Structural disruption (pearl)": "#922b21",  # тёмно-красный для pearl подкатегории
    "Ambiguous": "#f39c12",
    "Structural unlikely": "#2980b9",
    "Needs simulation": "#95a5a6",
}

# ПОЧЕМУ: упрощённые метки для легенды — иначе не влезут при figsize=(12,5)
CATEGORY_LABELS: dict[str, str] = {
    "Structural disruption": "Structural disruption",
    "Structural disruption (pearl)": "Structural disruption (pearl)",
    "Ambiguous": "Ambiguous",
    "Structural unlikely": "Structural unlikely",
    "Needs simulation": "Needs simulation",
}

# ---------------------------------------------------------------------------
# Нормализация категорий интерпретации
# ---------------------------------------------------------------------------


def normalize_interpretation(interp: str | float) -> str:
    """Нормализует текстовое поле Interpretation в одну из 5 категорий."""
    if pd.isna(interp):
        return "Needs simulation"
    s = str(interp)
    # ПОЧЕМУ: проверяем pearl РАНЬШЕ чем просто disruption — иначе pearl-записи
    # поглощаются общим паттерном structural disruption
    if "structural disruption" in s.lower() and "pearl" in s.lower():
        return "Structural disruption (pearl)"
    if "structural disruption" in s.lower():
        return "Structural disruption"
    if re.search(r"structural mechanism unlikely", s, re.IGNORECASE):
        return "Structural unlikely"
    if re.search(r"ambiguous", s, re.IGNORECASE):
        return "Ambiguous"
    if re.search(r"needs simulation", s, re.IGNORECASE):
        return "Needs simulation"
    return "Needs simulation"


# ---------------------------------------------------------------------------
# Загрузка данных
# ---------------------------------------------------------------------------


def load_gwas_data(path: Path) -> pd.DataFrame:
    """Загружает и обогащает GWAS × ARCHCODE overlay CSV."""
    log.info("loading gwas overlay", path=str(path))
    df = pd.read_csv(path)
    df["Category_Norm"] = df["Interpretation"].apply(normalize_interpretation)
    log.info("gwas data loaded", rows=len(df), loci=df["ARCHCODE_Locus"].nunique())
    return df


def load_atlas_lssim(locus: str, path: Path) -> pd.Series:
    """Загружает колонку ARCHCODE_LSSIM из файла атласа для заданного локуса."""
    log.info("loading atlas", locus=locus, path=str(path))
    df = pd.read_csv(path, usecols=["ARCHCODE_LSSIM"])
    series = df["ARCHCODE_LSSIM"].dropna()
    log.info("atlas loaded", locus=locus, n_variants=len(series))
    return series


# ---------------------------------------------------------------------------
# Panel A — Stacked bar chart
# ---------------------------------------------------------------------------


def build_panel_a_data(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Строит сводную таблицу: строки = локусы, столбцы = категории, сортировка по total."""
    pivot = df.groupby(["ARCHCODE_Locus", "Category_Norm"]).size().unstack(fill_value=0)
    # Добавляем отсутствующие категории как нулевые столбцы
    for cat in CATEGORY_ORDER:
        if cat not in pivot.columns:
            pivot[cat] = 0
    pivot = pivot[CATEGORY_ORDER]  # фиксированный порядок столбцов
    pivot["_total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("_total", ascending=False).drop(columns="_total")

    # ПОЧЕМУ: сортировка по total descending даёт наглядную убывающую гистограмму,
    # что упрощает восприятие вклада каждого локуса
    locus_order = list(pivot.index)
    return pivot, locus_order


def draw_panel_a(ax: plt.Axes, df: pd.DataFrame) -> None:
    """Рисует stacked bar chart на переданной оси."""
    pivot, locus_order = build_panel_a_data(df)

    x = np.arange(len(locus_order))
    bottom = np.zeros(len(locus_order))

    for cat in CATEGORY_ORDER:
        values = pivot[cat].values
        ax.bar(
            x,
            values,
            bottom=bottom,
            color=CATEGORY_COLORS[cat],
            label=CATEGORY_LABELS[cat],
            width=0.65,
            edgecolor="white",
            linewidth=0.5,
        )
        bottom += values

    ax.set_xticks(x)
    ax.set_xticklabels(locus_order, fontsize=8, rotation=30, ha="right")
    ax.set_ylabel("Number of GWAS SNPs", fontsize=10)
    ax.set_title(
        "A   GWAS SNPs per Locus by Interpretation", fontsize=10, loc="left", fontweight="bold"
    )
    ax.tick_params(axis="y", labelsize=8)

    # ПОЧЕМУ: убираем все спайны кроме нижнего и левого — minimalist стиль публикации
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Легенда внутри панели, сверху справа
    handles = [
        mpatches.Patch(color=CATEGORY_COLORS[c], label=CATEGORY_LABELS[c]) for c in CATEGORY_ORDER
    ]
    ax.legend(
        handles=handles,
        fontsize=7,
        loc="upper right",
        frameon=False,
        handlelength=1.2,
        handleheight=0.9,
    )

    # Аннотация тотала над каждым баром
    totals = pivot.sum(axis=1).values
    for xi, total in zip(x, totals):
        ax.text(
            xi, total + 0.5, str(int(total)), ha="center", va="bottom", fontsize=7, color="#444444"
        )


# ---------------------------------------------------------------------------
# Panel B — LSSIM distribution
# ---------------------------------------------------------------------------


def draw_panel_b(ax: plt.Axes, df: pd.DataFrame) -> None:
    """Рисует boxplot LSSIM: GWAS SNP (красный) vs атлас ClinVar (серый) для 3 локусов."""
    loci_for_b = ["HBB", "BRCA1", "TP53"]

    # Данные для boxplot: список словарей {label, data, color, is_gwas}
    box_data: list[dict] = []

    for locus in loci_for_b:
        # --- Атлас ClinVar (фон) ---
        atlas_path = ATLAS_FILES.get(locus)
        if atlas_path and atlas_path.exists():
            atlas_lssim = load_atlas_lssim(locus, atlas_path)
        else:
            log.warning("atlas file not found", locus=locus)
            atlas_lssim = pd.Series(dtype=float)

        # --- GWAS SNP в этом локусе с известным LSSIM ---
        gwas_locus = df[df["ARCHCODE_Locus"] == locus]["ARCHCODE_LSSIM"].dropna()

        box_data.append(
            {
                "label": f"{locus}\nAtlas\n(n={len(atlas_lssim)})",
                "data": atlas_lssim.values,
                "color": "#bdc3c7",  # серый
                "is_gwas": False,
                "locus": locus,
            }
        )
        box_data.append(
            {
                "label": f"{locus}\nGWAS\n(n={len(gwas_locus)})",
                "data": gwas_locus.values,
                "color": "#e74c3c",  # красный
                "is_gwas": True,
                "locus": locus,
            }
        )

    positions = list(range(1, len(box_data) + 1))

    # ПОЧЕМУ: ширина боксов у GWAS-групп уменьшена — выборка меньше и визуально
    # подчёркивает разницу масштабов между атласом (тысячи) и GWAS (десятки)
    widths = [0.5 if not d["is_gwas"] else 0.35 for d in box_data]

    for pos, item, width in zip(positions, box_data, widths):
        if len(item["data"]) == 0:
            continue
        ax.boxplot(
            item["data"],
            positions=[pos],
            widths=width,
            patch_artist=True,
            notch=False,
            showfliers=False,  # outliers покажем отдельно как точки
            boxprops=dict(facecolor=item["color"], color="#555555", linewidth=0.8),
            medianprops=dict(color="#2c3e50", linewidth=1.5),
            whiskerprops=dict(color="#555555", linewidth=0.8),
            capprops=dict(color="#555555", linewidth=0.8),
        )

        # Jitter-точки поверх boxplot (только для GWAS — их мало)
        if item["is_gwas"] and len(item["data"]) > 0:
            jitter = np.random.default_rng(42).uniform(-0.08, 0.08, size=len(item["data"]))
            ax.scatter(
                np.full(len(item["data"]), pos) + jitter,
                item["data"],
                color="#c0392b",
                s=18,
                alpha=0.7,
                zorder=5,
                linewidths=0,
            )

    # --- Аннотации pearl и конкретных rsID ---
    # ПОЧЕМУ: rs334 (sickle cell) и rs11549407 — ключевые клинически значимые SNP,
    # их аннотация напрямую связывает визуализацию с биологическим нарративом

    # Находим позиции GWAS-боксов для HBB
    hbb_gwas_pos = None
    for i, item in enumerate(box_data):
        if item["locus"] == "HBB" and item["is_gwas"]:
            hbb_gwas_pos = positions[i]
            break

    if hbb_gwas_pos is not None:
        # rs334 (sickle cell mutation)
        rs334_row = df[df["rsID"] == "rs334"]["ARCHCODE_LSSIM"].dropna()
        if len(rs334_row) > 0:
            lssim_val = rs334_row.iloc[0]
            ax.annotate(
                "rs334\n(sickle cell)",
                xy=(hbb_gwas_pos, lssim_val),
                xytext=(hbb_gwas_pos + 0.6, lssim_val - 0.035),
                fontsize=6.5,
                color="#922b21",
                arrowprops=dict(arrowstyle="->", color="#922b21", lw=0.8),
                ha="left",
            )
            # Diamond marker для rs334
            ax.scatter(
                [hbb_gwas_pos],
                [lssim_val],
                marker="D",
                color="#c0392b",
                s=40,
                zorder=6,
                edgecolors="#7b241c",
                linewidths=0.7,
            )

        # rs11549407
        rs_row = df[df["rsID"] == "rs11549407"]["ARCHCODE_LSSIM"].dropna()
        if len(rs_row) > 0:
            lssim_val2 = rs_row.iloc[0]
            ax.annotate(
                "rs11549407",
                xy=(hbb_gwas_pos, lssim_val2),
                xytext=(hbb_gwas_pos + 0.6, lssim_val2 + 0.025),
                fontsize=6.5,
                color="#922b21",
                arrowprops=dict(arrowstyle="->", color="#922b21", lw=0.8),
                ha="left",
            )

        # Pearl diamonds — все Is_Pearl в HBB
        pearls_hbb = df[(df["ARCHCODE_Locus"] == "HBB") & df["Is_Pearl"]]["ARCHCODE_LSSIM"].dropna()
        if len(pearls_hbb) > 0:
            ax.scatter(
                np.full(len(pearls_hbb), hbb_gwas_pos),
                pearls_hbb.values,
                marker="D",
                color="#f39c12",
                s=35,
                zorder=7,
                edgecolors="#d68910",
                linewidths=0.7,
                label="Pearl",
            )

    # Оформление оси X
    tick_positions = positions
    tick_labels = [d["label"] for d in box_data]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=7)

    ax.set_ylabel("ARCHCODE LSSIM", fontsize=10)
    ax.set_title(
        "B   LSSIM Distribution: GWAS SNPs vs Atlas ClinVar Variants",
        fontsize=10,
        loc="left",
        fontweight="bold",
    )
    ax.tick_params(axis="y", labelsize=8)
    ax.set_ylim(0.72, 1.02)

    # Линия порога структурного нарушения (LSSIM < 0.95)
    ax.axhline(y=0.95, color="#c0392b", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(
        len(box_data) + 0.3,
        0.951,
        "LSSIM < 0.95\n(disruption\nthreshold)",
        fontsize=6,
        color="#c0392b",
        va="bottom",
        ha="right",
    )

    # Разделители между локусами
    # ПОЧЕМУ: вертикальные линии между группами локусов помогают читателю
    # быстро сгруппировать atlas + gwas без дополнительного лейбла
    for sep in [2.5, 4.5]:
        ax.axvline(x=sep, color="#dddddd", linewidth=0.8, linestyle="-", zorder=0)

    # Легенда
    legend_handles = [
        mpatches.Patch(color="#bdc3c7", label="Atlas ClinVar variants"),
        mpatches.Patch(color="#e74c3c", label="GWAS SNPs"),
        plt.Line2D(
            [0],
            [0],
            marker="D",
            color="w",
            markerfacecolor="#f39c12",
            markeredgecolor="#d68910",
            markersize=6,
            label="Pearl overlap",
        ),
    ]
    ax.legend(handles=legend_handles, fontsize=7, loc="lower right", frameon=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Тихо обрезаем X-диапазон
    ax.set_xlim(0.3, len(box_data) + 0.7)


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------


def main() -> None:
    """Генерирует fig_gwas_overlay.pdf и fig_gwas_overlay.png."""
    log.info("starting gwas overlay plot generation")

    # Проверка входных данных
    if not DATA_CSV.exists():
        log.error("gwas csv not found", path=str(DATA_CSV))
        sys.exit(1)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_gwas_data(DATA_CSV)

    # --- Создаём фигуру ---
    # ПОЧЕМУ: GridSpec с width_ratio 1:1.3 даёт Panel B чуть больше места —
    # там 6 боксов (3 локуса × 2) и аннотации, которым нужен простор
    fig = plt.figure(figsize=(12, 5))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.3], wspace=0.38)

    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])

    draw_panel_a(ax_a, df)
    draw_panel_b(ax_b, df)

    fig.tight_layout(pad=1.2)

    # --- Сохранение ---
    out_pdf = FIGURES_DIR / "fig_gwas_overlay.pdf"
    out_png = FIGURES_DIR / "fig_gwas_overlay.png"

    fig.savefig(out_pdf, dpi=300, bbox_inches="tight")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    log.info("figure saved", pdf=str(out_pdf), png=str(out_png))
    print(f"[OK] Saved:\n  {out_pdf}\n  {out_png}")


if __name__ == "__main__":
    main()
