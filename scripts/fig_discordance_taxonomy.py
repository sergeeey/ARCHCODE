#!/usr/bin/env python3
"""
fig_discordance_taxonomy.py — Publication figure: discordance taxonomy (3 panels)
==================================================================================
Panel A: Extended 2×2 matrix with Q2a/Q2b split (conceptual diagram)
Panel B: Enhancer distance comparison — Q2a vs Q2b vs Q3 (violin + box, real data)
Panel C: Tissue specificity of Q2b across loci (scatter, hardcoded per-locus counts)

ПОЧЕМУ отдельный скрипт, а не часть discordance_v2_split.py:
  Визуализация — другая ответственность. Хранить figure-код отдельно позволяет
  итерировать дизайн без перезапуска тяжёлого data-pipeline.
  Логику загрузки данных — копируем из v2_split (не импортируем, чтобы избежать
  побочных print-эффектов от main()).
"""

import json
import warnings
from pathlib import Path

# ПОЧЕМУ Agg ставится до остальных matplotlib-импортов: headless рендеринг на
# Windows требует выбора бэкенда ДО первого обращения к pyplot. Иначе — ошибка
# "cannot connect to display" или падение на машинах без GUI.
import matplotlib  # noqa: E402 — intentional early backend selection

matplotlib.use("Agg")  # noqa: E402

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import structlog  # noqa: E402
from matplotlib.ticker import LogLocator, NullFormatter  # noqa: E402
from scipy import stats  # noqa: E402

warnings.filterwarnings("ignore", category=FutureWarning)

log = structlog.get_logger()

# ── Пути ──────────────────────────────────────────────────────────────────────

BASE = Path(r"D:\ДНК")
RESULTS = BASE / "results"
CONFIG = BASE / "config" / "locus"
FIGURES = BASE / "figures"
FIGURES.mkdir(exist_ok=True)

# ── Конфиг (зеркало из discordance_v2_split.py) ───────────────────────────────

LSSIM_THRESHOLD = 0.95
VEP_THRESHOLD = 0.5
CADD_THRESHOLD = 20

LOCUS_ATLAS = {
    "HBB": "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
    "TERT": "TERT_Unified_Atlas_300kb.csv",
    "GJB2": "GJB2_Unified_Atlas_300kb.csv",
}

LOCUS_CONFIG = {
    "HBB": "hbb_95kb_subTAD.json",
    "BRCA1": "brca1_400kb.json",
    "TP53": "tp53_300kb.json",
    "CFTR": "cftr_317kb.json",
    "MLH1": "mlh1_300kb.json",
    "LDLR": "ldlr_300kb.json",
    "SCN5A": "scn5a_400kb.json",
    "TERT": "tert_300kb.json",
    "GJB2": "gjb2_300kb.json",
}

TISSUE_MATCH = {
    "HBB": 1.0,
    "BRCA1": 0.5,
    "TP53": 0.5,
    "CFTR": 0.0,
    "MLH1": 0.5,
    "LDLR": 0.0,
    "SCN5A": 0.0,
    "TERT": 0.5,
    "GJB2": 0.0,
}

# ── Цветовая схема ────────────────────────────────────────────────────────────

COLORS = {
    "Q1": "#2ca02c",  # зелёный
    "Q2a": "#ffbb78",  # светло-оранжевый
    "Q2b": "#d62728",  # красный
    "Q3": "#1f77b4",  # синий
    "Q4": "#aec7e8",  # светло-серо-синий
}

# ── Загрузка данных (идентично v2_split.py) ──────────────────────────────────


def _load_locus_config(locus: str) -> dict:
    """Загружает конфиг локуса и возвращает позиции энхансеров и CTCF-сайтов."""
    path = CONFIG / LOCUS_CONFIG[locus]
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    return {
        "enhancers": [e["position"] for e in cfg["features"]["enhancers"]],
        "ctcf_sites": [c["position"] for c in cfg["features"]["ctcf_sites"]],
    }


def _compute_min_distance(positions: pd.Series, targets: list[int]) -> pd.Series:
    """Минимальное расстояние от каждой позиции до ближайшего таргета."""
    if not targets:
        return pd.Series(np.nan, index=positions.index)
    targets_arr = np.array(targets)
    return positions.apply(lambda p: int(np.min(np.abs(targets_arr - p))))


def load_all_data() -> pd.DataFrame:
    """
    Загружает все 9 атласов, вычисляет квадранты Q1–Q4 и расстояния до энхансеров.
    Возвращает объединённый DataFrame с колонками Q, Q2a, Q2b.
    """
    frames = []
    for locus, fname in LOCUS_ATLAS.items():
        path = RESULTS / fname
        if not path.exists():
            log.warning("atlas_missing", locus=locus, path=str(path))
            continue
        df = pd.read_csv(path)
        df["Locus"] = locus
        df["Tissue_Match"] = TISSUE_MATCH[locus]
        cfg = _load_locus_config(locus)
        df["Dist_Enhancer"] = _compute_min_distance(df["Position_GRCh38"], cfg["enhancers"])
        df["Dist_CTCF"] = _compute_min_distance(df["Position_GRCh38"], cfg["ctcf_sites"])
        frames.append(df)

    if not frames:
        raise FileNotFoundError(f"Не найден ни один атлас в {RESULTS}")

    combined = pd.concat(frames, ignore_index=True)
    log.info("data_loaded", n_variants=len(combined), n_loci=len(frames))

    # ARCHCODE HIGH = структурный сигнал (LSSIM < threshold → disruption)
    combined["ARCHCODE_HIGH"] = combined["ARCHCODE_LSSIM"] < LSSIM_THRESHOLD

    # SEQ_HIGH = sequence tool видит эффект
    vep_high = combined["VEP_Score"] >= VEP_THRESHOLD
    if "CADD_Phred" in combined.columns:
        cadd_vals = pd.to_numeric(combined["CADD_Phred"], errors="coerce")
        combined["SEQ_HIGH"] = vep_high | (cadd_vals >= CADD_THRESHOLD).fillna(False)
    else:
        combined["SEQ_HIGH"] = vep_high

    conditions = [
        combined["ARCHCODE_HIGH"] & combined["SEQ_HIGH"],
        combined["ARCHCODE_HIGH"] & ~combined["SEQ_HIGH"],
        ~combined["ARCHCODE_HIGH"] & combined["SEQ_HIGH"],
        ~combined["ARCHCODE_HIGH"] & ~combined["SEQ_HIGH"],
    ]
    combined["Q"] = np.select(conditions, ["Q1", "Q2", "Q3", "Q4"], default="?")

    # Q2a/Q2b split
    # ПОЧЕМУ: VEP_Score == -1 означает "VEP не смог оценить" — это gap, не discordance
    q2_mask = combined["Q"] == "Q2"
    combined["Q_fine"] = combined["Q"].copy()
    combined.loc[q2_mask & (combined["VEP_Score"] == -1.0), "Q_fine"] = "Q2a"
    combined.loc[
        q2_mask & (combined["VEP_Score"] >= 0) & (combined["VEP_Score"] < VEP_THRESHOLD),
        "Q_fine",
    ] = "Q2b"

    return combined


# ── Panel A: концептуальная матрица ──────────────────────────────────────────


def draw_panel_a(ax: plt.Axes, counts: dict[str, int]) -> None:
    """
    Рисует расширенную 2×2 матрицу с разбивкой Q2 на Q2a/Q2b.
    Использует патчи (прямоугольники) вместо scatter, потому что
    концептуальная схема важнее точного масштаба данных.
    """
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 3)
    ax.set_aspect("equal")
    ax.axis("off")

    # Фоновые квадранты (без рамок — минималистично)
    quads = [
        # (x0, y0, width, height, color, label, n)
        (0, 2, 1, 1, COLORS["Q1"], "Concordant\nPathogenic", counts.get("Q1", 270)),
        (0, 1, 1, 1, COLORS["Q2a"], "Coverage Gap\n(VEP=−1)", counts.get("Q2a", 207)),
        (0, 0, 1, 1, COLORS["Q2b"], "True Blind Spot\n(VEP<0.5)", counts.get("Q2b", 54)),
        (1, 1, 1, 2, COLORS["Q3"], "Sequence\nChannel", counts.get("Q3", 10385)),
        (1, 0, 1, 1, COLORS["Q4"], "Concordant\nBenign", counts.get("Q4", 19402)),
    ]

    for x0, y0, w, h, color, label, n in quads:
        rect = mpatches.FancyBboxPatch(
            (x0 + 0.02, y0 + 0.02),
            w - 0.04,
            h - 0.04,
            boxstyle="round,pad=0.02",
            facecolor=color,
            edgecolor="white",
            linewidth=1.5,
            alpha=0.85,
        )
        ax.add_patch(rect)
        # Метка квадранта
        ax.text(
            x0 + w / 2,
            y0 + h / 2 + 0.12,
            label,
            ha="center",
            va="center",
            fontsize=8.5,
            fontweight="bold",
            color="white" if color in (COLORS["Q2b"], COLORS["Q3"], COLORS["Q1"]) else "#333333",
            multialignment="center",
        )
        # Счётчик
        ax.text(
            x0 + w / 2,
            y0 + h / 2 - 0.20,
            f"N={n:,}",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if color in (COLORS["Q2b"], COLORS["Q3"], COLORS["Q1"]) else "#555555",
        )

    # Разделительные линии осей
    ax.plot([1, 1], [0, 3], color="#555555", lw=1.2, linestyle="--", alpha=0.6)
    ax.plot([0, 2], [2, 2], color="#555555", lw=1.2, linestyle="--", alpha=0.6)

    # Метки осей со стрелками
    ax.annotate(
        "",
        xy=(2.0, 0),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2),
        annotation_clip=False,
    )
    ax.text(
        1.0, -0.18, "Sequence Score (VEP/CADD)", ha="center", va="top", fontsize=9, color="#333333"
    )

    ax.annotate(
        "",
        xy=(0, 3.0),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.2),
        annotation_clip=False,
    )
    ax.text(
        -0.18,
        1.5,
        "Structural Score\n(ARCHCODE)",
        ha="right",
        va="center",
        fontsize=9,
        color="#333333",
        rotation=90,
    )

    # Метки делений осей
    ax.text(0.5, -0.08, "Low", ha="center", va="top", fontsize=8, color="#666666")
    ax.text(1.5, -0.08, "High", ha="center", va="top", fontsize=8, color="#666666")
    ax.text(-0.08, 0.5, "Low", ha="right", va="center", fontsize=8, color="#666666")
    ax.text(-0.08, 2.5, "High", ha="right", va="center", fontsize=8, color="#666666")

    ax.set_title("A. Discordance Framework", fontsize=11, fontweight="bold", pad=10)


# ── Panel B: сравнение расстояний до энхансеров ──────────────────────────────


def draw_panel_b(ax: plt.Axes, df: pd.DataFrame) -> None:
    """
    Violin + box plot для Q2a, Q2b, Q3 по расстоянию до ближайшего энхансера.
    Log-scale Y, p-value аннотация Q2b vs Q3.
    """
    groups = {
        "Q2a": df[df["Q_fine"] == "Q2a"]["Dist_Enhancer"].dropna(),
        "Q2b": df[df["Q_fine"] == "Q2b"]["Dist_Enhancer"].dropna(),
        "Q3": df[df["Q"] == "Q3"]["Dist_Enhancer"].dropna(),
    }

    labels = list(groups.keys())
    data = [groups[k].values for k in labels]
    colors_list = [COLORS["Q2a"], COLORS["Q2b"], COLORS["Q3"]]
    positions = [1, 2, 3]

    # Violin
    parts = ax.violinplot(
        data,
        positions=positions,
        showmedians=False,
        showextrema=False,
        widths=0.6,
    )
    for body, color in zip(parts["bodies"], colors_list):
        body.set_facecolor(color)
        body.set_alpha(0.45)
        body.set_edgecolor("none")

    # Box поверх violin
    bp = ax.boxplot(
        data,
        positions=positions,
        widths=0.25,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(color="#555555", linewidth=1),
        capprops=dict(color="#555555", linewidth=1),
        boxprops=dict(linewidth=0),
    )
    for patch, color in zip(bp["boxes"], colors_list):
        patch.set_facecolor(color)
        patch.set_alpha(0.9)

    # p-value Q2b vs Q3
    q2b_vals = groups["Q2b"]
    q3_vals = groups["Q3"]
    if len(q2b_vals) > 1 and len(q3_vals) > 1:
        _, p = stats.mannwhitneyu(q2b_vals, q3_vals, alternative="less")
        p_str = f"p={p:.2e}" if p >= 1e-300 else "p<10⁻³⁰⁰"
        # Скобка
        y_top = max(q2b_vals.max(), q3_vals.max()) * 3
        ax.plot([2, 2, 3, 3], [y_top, y_top * 1.5, y_top * 1.5, y_top], lw=1, color="#333333")
        ax.text(2.5, y_top * 1.7, p_str, ha="center", va="bottom", fontsize=8, color="#333333")

    # Медианные аннотации
    for pos, (label, vals) in zip(positions, groups.items()):
        if len(vals) > 0:
            med = int(np.median(vals))
            ax.text(
                pos,
                np.median(vals) * 0.55,
                f"{med:,} bp",
                ha="center",
                va="top",
                fontsize=7.5,
                color="white",
                fontweight="bold",
            )

    # Текстовая аннотация из задания
    ax.text(
        0.97,
        0.97,
        "Q2b: 434 bp\nQ3: 25,138 bp\n58× enrichment",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#333333",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.85),
    )

    ax.set_yscale("log")
    # ПОЧЕМУ LogLocator: автоматические логарифмические деления без клаттера
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(positions)
    ax.set_xticklabels([f"{lbl}\n(n={len(groups[lbl]):,})" for lbl in labels], fontsize=9)
    ax.set_ylabel("Distance to Nearest Enhancer (bp)", fontsize=10)
    ax.set_title("B. Enhancer Proximity", fontsize=11, fontweight="bold")
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xlim(0.5, 3.5)


# ── Panel C: тканевая специфичность Q2b ──────────────────────────────────────

# ПОЧЕМУ хардкод: эти числа — результат предыдущего pipeline (Q2b_true_blindspots.csv),
# а не входные параметры. Вычислены в discordance_v2_split.py и верифицированы вручную.
PER_LOCUS_Q2B: list[dict] = [
    {"locus": "HBB", "n_q2b": 25, "n_total": 1103, "tissue": 1.0},
    {"locus": "BRCA1", "n_q2b": 26, "n_total": 10682, "tissue": 0.5},
    {"locus": "TP53", "n_q2b": 2, "n_total": 2794, "tissue": 0.5},
    {"locus": "TERT", "n_q2b": 1, "n_total": 2089, "tissue": 0.5},
    {"locus": "CFTR", "n_q2b": 0, "n_total": 3349, "tissue": 0.0},
    {"locus": "MLH1", "n_q2b": 0, "n_total": 4060, "tissue": 0.5},
    {"locus": "LDLR", "n_q2b": 0, "n_total": 3284, "tissue": 0.0},
    {"locus": "SCN5A", "n_q2b": 0, "n_total": 2488, "tissue": 0.0},
    {"locus": "GJB2", "n_q2b": 0, "n_total": 469, "tissue": 0.0},
]


def draw_panel_c(ax: plt.Axes) -> None:
    """
    Scatter: X = tissue match, Y = Q2b ratio (n_Q2b / n_total) для каждого локуса.
    Размер точек — пропорционален n_total. Аннотация Spearman rho.
    """
    ldf = pd.DataFrame(PER_LOCUS_Q2B)
    ldf["q2b_ratio"] = ldf["n_q2b"] / ldf["n_total"]

    # Spearman
    rho, p_sp = stats.spearmanr(ldf["q2b_ratio"], ldf["tissue"])
    p_str = f"ρ={rho:.2f}, p={p_sp:.3f}"

    # Размер точек: масштаб sqrt чтобы крупные локусы не подавляли
    # ПОЧЕМУ sqrt: линейный масштаб делает HBB (1103) невидимым рядом с BRCA1 (10682)
    sizes = (np.sqrt(ldf["n_total"]) / np.sqrt(ldf["n_total"].max()) * 300 + 40).values

    # Цвет по tissue_match
    cmap_vals = ldf["tissue"].values
    ax.scatter(
        ldf["tissue"] + np.random.default_rng(42).uniform(-0.02, 0.02, len(ldf)),
        ldf["q2b_ratio"],
        s=sizes,
        c=cmap_vals,
        cmap="RdYlGn",
        vmin=0,
        vmax=1,
        alpha=0.8,
        edgecolors="#333333",
        linewidths=0.8,
        zorder=3,
    )

    # Подписи локусов
    for _, row in ldf.iterrows():
        x_offset = 0.03
        y_offset = 0.0003
        # HBB и BRCA1 могут перекрываться — сдвигаем
        if row["locus"] == "HBB":
            x_offset = 0.04
            y_offset = 0.0010
        elif row["locus"] == "BRCA1":
            x_offset = 0.04
            y_offset = -0.0010
        ax.annotate(
            row["locus"],
            xy=(row["tissue"], row["q2b_ratio"]),
            xytext=(row["tissue"] + x_offset, row["q2b_ratio"] + y_offset),
            fontsize=8,
            color="#333333",
            arrowprops=dict(arrowstyle="-", color="#aaaaaa", lw=0.6),
        )

    # Линия тренда (только для непустых)
    if rho != 0 and len(ldf) > 2:
        x_line = np.array([ldf["tissue"].min() - 0.05, ldf["tissue"].max() + 0.05])
        slope, intercept, *_ = stats.linregress(ldf["tissue"], ldf["q2b_ratio"])
        ax.plot(
            x_line,
            slope * x_line + intercept,
            color="#888888",
            lw=1.2,
            linestyle="--",
            alpha=0.7,
            zorder=2,
        )

    # Аннотация Spearman
    ax.text(
        0.97,
        0.97,
        f"Spearman\n{p_str}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#cccccc", alpha=0.9),
    )

    ax.set_xlabel("Tissue Match Score", fontsize=10)
    ax.set_ylabel("Q2b Ratio (N_Q2b / N_total)", fontsize=10)
    ax.set_title("C. Tissue Dependence of Q2b", fontsize=11, fontweight="bold")
    ax.set_xlim(-0.15, 1.25)
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xticklabels(["0.0\n(no match)", "0.5\n(partial)", "1.0\n(full)"], fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.set_ylim(-0.002, ldf["q2b_ratio"].max() * 1.35)


# ── Главная функция сборки фигуры ─────────────────────────────────────────────


def build_figure() -> None:
    """Загружает данные, строит 3-панельную фигуру и сохраняет PDF + PNG."""
    log.info("loading_data")
    try:
        df = load_all_data()
        data_available = True
    except FileNotFoundError as exc:
        log.warning("atlas_not_found", error=str(exc))
        log.info("falling_back_to_reported_counts")
        df = None
        data_available = False

    # Считаем реальные N для panel A
    if data_available and df is not None:
        q2 = df[df["Q"] == "Q2"]
        q2a_n = int((q2["VEP_Score"] == -1.0).sum())
        q2b_n = int(((q2["VEP_Score"] >= 0) & (q2["VEP_Score"] < VEP_THRESHOLD)).sum())
        counts = {
            "Q1": int((df["Q"] == "Q1").sum()),
            "Q2a": q2a_n,
            "Q2b": q2b_n,
            "Q3": int((df["Q"] == "Q3").sum()),
            "Q4": int((df["Q"] == "Q4").sum()),
        }
        log.info("quadrant_counts", **counts)
    else:
        # ПОЧЕМУ fallback: числа из DISCORDANCE_REPORT_v2.md (верифицированы pipeline)
        counts = {"Q1": 270, "Q2a": 207, "Q2b": 54, "Q3": 10385, "Q4": 19402}

    # Стиль
    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        plt.style.use("ggplot")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.patch.set_facecolor("white")

    # ── Panel A ──
    draw_panel_a(axes[0], counts)

    # ── Panel B ──
    if data_available and df is not None:
        draw_panel_b(axes[1], df)
    else:
        # Fallback: синтетические данные для демонстрации формы дистрибутива
        log.warning("panel_b_synthetic", reason="atlas files not found")
        rng = np.random.default_rng(0)
        fake_df = pd.DataFrame(
            {
                "Q_fine": (["Q2a"] * 207 + ["Q2b"] * 54 + ["Q3"] * 10385),
                "Q": (["Q2"] * 207 + ["Q2"] * 54 + ["Q3"] * 10385),
                "Dist_Enhancer": np.concatenate(
                    [
                        rng.lognormal(np.log(2000), 1.2, 207),
                        rng.lognormal(np.log(434), 0.8, 54),
                        rng.lognormal(np.log(25138), 1.0, 10385),
                    ]
                ),
            }
        )
        axes[1].text(
            0.5,
            0.02,
            "[SYNTHETIC — atlas files not found]",
            transform=axes[1].transAxes,
            ha="center",
            fontsize=7,
            color="red",
            alpha=0.8,
        )
        draw_panel_b(axes[1], fake_df)

    # ── Panel C ──
    draw_panel_c(axes[2])

    fig.suptitle(
        "Discordance Taxonomy: ARCHCODE Structural Signal vs Sequence Tools",
        fontsize=12,
        fontweight="bold",
        y=1.01,
    )

    plt.tight_layout(pad=1.5, w_pad=2.5)

    # Сохранение
    pdf_path = FIGURES / "fig_discordance_taxonomy.pdf"
    png_path = FIGURES / "fig_discordance_taxonomy.png"

    fig.savefig(pdf_path, bbox_inches="tight", dpi=300)
    fig.savefig(png_path, bbox_inches="tight", dpi=300)

    log.info("figure_saved", pdf=str(pdf_path), png=str(png_path))
    print(f"Saved:\n  {pdf_path}\n  {png_path}")

    plt.close(fig)


if __name__ == "__main__":
    build_figure()
