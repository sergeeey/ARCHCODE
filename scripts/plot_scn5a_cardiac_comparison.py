"""
Скрипт генерации публикационного рисунка: SCN5A K562 vs Cardiac comparison.

Три панели:
  A — Распределение LSSIM (box + strip) для K562 и Cardiac по Pathogenic/Benign
  B — Structural calls по категориям: K562 vs Cardiac grouped bar
  C — Amplification summary: horizontal bar (cardiac/k562 ratio)

Выходные файлы:
  figures/taxonomy/fig_scn5a_cardiac_comparison.pdf (300 dpi)
  figures/taxonomy/fig_scn5a_cardiac_comparison.png (150 dpi)
"""

# ПОЧЕМУ Agg устанавливается до остальных импортов matplotlib:
# matplotlib.use() должен вызываться до первого import pyplot,
# иначе backend уже инициализирован и смена игнорируется (Windows headless).
import matplotlib  # noqa: E402 — backend must be set before pyplot import

matplotlib.use("Agg")

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import structlog  # noqa: E402
from pathlib import Path  # noqa: E402

log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
ROOT = Path("D:/ДНК")
K562_CSV = ROOT / "results" / "SCN5A_Unified_Atlas_400kb.csv"
CARDIAC_CSV = ROOT / "results" / "SCN5A_Unified_Atlas_250kb.csv"
OUT_DIR = ROOT / "figures" / "taxonomy"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Цвета и стиль
# ---------------------------------------------------------------------------
# ПОЧЕМУ именованные константы: легко перенести в другую фигуру / CLAUDE.md style
COLOR_K562_PATH = "#1f77b4"  # синий — K562 Pathogenic
COLOR_K562_BEN = "#aec7e8"  # светло-синий — K562 Benign
COLOR_CARDIAC_PATH = "#d62728"  # красный — Cardiac Pathogenic
COLOR_CARDIAC_BEN = "#ffbb78"  # светло-оранжевый — Cardiac Benign

COLOR_K562 = "#1f77b4"
COLOR_CARDIAC = "#d62728"

STRIP_ALPHA = 0.25
STRIP_SIZE = 1.5
BOX_WIDTH = 0.45

# Каноничные числа из analysis/scn5a_cardiac_comparison.json
# ПОЧЕМУ хардкод: это итоговые числа из верифицированного JSON,
# использование их напрямую исключает risk численных артефактов при перерасчёте.
CANON = {
    "k562": {
        "delta": -0.003432,
        "struct_calls": 199,
        "q2": 214,
        "frameshift_min": 0.9786,
    },
    "cardiac": {
        "delta": -0.004706,
        "struct_calls": 577,
        "q2": 274,
        "frameshift_min": 0.9714,
    },
    "ratio": {
        "delta": 1.37,
        "struct_calls": 2.90,
        "q2": 1.28,
    },
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Загрузить K562 и Cardiac CSV, вернуть пару DataFrame."""
    log.info("loading_data", k562=str(K562_CSV), cardiac=str(CARDIAC_CSV))
    k562 = pd.read_csv(K562_CSV)
    cardiac = pd.read_csv(CARDIAC_CSV)
    log.info("data_loaded", k562_shape=k562.shape, cardiac_shape=cardiac.shape)
    return k562, cardiac


def _remove_spines(ax: plt.Axes, keep: tuple[str, ...] = ("left", "bottom")) -> None:
    """Убрать лишние рамки для publication-style."""
    for spine in ax.spines:
        ax.spines[spine].set_visible(spine in keep)


# ---------------------------------------------------------------------------
# Panel A — LSSIM Distribution
# ---------------------------------------------------------------------------
def plot_panel_a(ax: plt.Axes, k562: pd.DataFrame, cardiac: pd.DataFrame) -> None:
    """
    Рисует box + strip plot: 4 группы (K562-P, K562-B, Cardiac-P, Cardiac-B).
    Аннотирует delta (mean P − mean B) для каждого источника.
    """
    groups = [
        (
            k562[k562["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"],
            "K562\nPathogenic",
            COLOR_K562_PATH,
        ),
        (k562[k562["Label"] == "Benign"]["ARCHCODE_LSSIM"], "K562\nBenign", COLOR_K562_BEN),
        (
            cardiac[cardiac["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"],
            "Cardiac\nPathogenic",
            COLOR_CARDIAC_PATH,
        ),
        (
            cardiac[cardiac["Label"] == "Benign"]["ARCHCODE_LSSIM"],
            "Cardiac\nBenign",
            COLOR_CARDIAC_BEN,
        ),
    ]

    positions = [0, 1, 2.5, 3.5]
    tick_labels = [g[1] for g in groups]

    for pos, (series, label, color) in zip(positions, groups):
        data = series.dropna().values

        # Box plot (возврат не используется — patch_artist применяется через boxprops)
        ax.boxplot(
            data,
            positions=[pos],
            widths=BOX_WIDTH,
            patch_artist=True,
            showfliers=False,
            medianprops=dict(color="black", linewidth=1.5),
            boxprops=dict(facecolor=color, alpha=0.7, linewidth=0.8),
            whiskerprops=dict(linewidth=0.8),
            capprops=dict(linewidth=0.8),
        )

        # Strip plot поверх box
        jitter = np.random.default_rng(42).uniform(-0.18, 0.18, size=len(data))
        ax.scatter(
            pos + jitter,
            data,
            color=color,
            alpha=STRIP_ALPHA,
            s=STRIP_SIZE,
            zorder=2,
            rasterized=True,  # ПОЧЕМУ: тысячи точек → pdf без rasterize раздуется до 100 MB
        )

    # Аннотация delta
    k562_delta = CANON["k562"]["delta"]
    cardiac_delta = CANON["cardiac"]["delta"]

    ax.annotate(
        f"Δ={k562_delta:.4f}",
        xy=(0.5, 0.04),
        xycoords="axes fraction",
        ha="center",
        fontsize=7,
        color=COLOR_K562,
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=COLOR_K562, linewidth=0.6),
    )
    ax.annotate(
        f"Δ={cardiac_delta:.4f}",
        xy=(0.78, 0.04),
        xycoords="axes fraction",
        ha="center",
        fontsize=7,
        color=COLOR_CARDIAC,
        bbox=dict(
            boxstyle="round,pad=0.2", facecolor="white", edgecolor=COLOR_CARDIAC, linewidth=0.6
        ),
    )

    # Разделитель между K562 и Cardiac
    ax.axvline(x=1.75, color="grey", linewidth=0.6, linestyle="--", alpha=0.5)

    ax.set_xticks(positions)
    ax.set_xticklabels(tick_labels, fontsize=7)
    ax.set_ylabel("ARCHCODE LSSIM", fontsize=8)
    ax.set_title(
        "A  LSSIM Distribution: K562 vs Cardiac", fontsize=9, loc="left", fontweight="bold"
    )

    # ПОЧЕМУ ylim обрезан: все значения > 0.97, zoom делает разницу видимой
    all_vals = pd.concat([k562["ARCHCODE_LSSIM"], cardiac["ARCHCODE_LSSIM"]]).dropna()
    ymin = max(all_vals.min() - 0.002, 0.97)
    ax.set_ylim(ymin, 1.001)

    _remove_spines(ax)
    ax.tick_params(axis="both", labelsize=7)


# ---------------------------------------------------------------------------
# Panel B — Structural Calls by Category
# ---------------------------------------------------------------------------
def plot_panel_b(ax: plt.Axes, k562: pd.DataFrame, cardiac: pd.DataFrame) -> None:
    """
    Grouped bar: количество structural calls по категориям.
    Structural call = ARCHCODE_Verdict != 'BENIGN' AND != 'LIKELY_BENIGN'.
    """

    # ПОЧЕМУ такой фильтр: BENIGN и LIKELY_BENIGN — не структурные вызовы;
    # VUS, LIKELY_PATHOGENIC — структурные (неопределённые/патогенные).
    def struct_mask(df: pd.DataFrame) -> pd.Series:
        return ~df["ARCHCODE_Verdict"].isin(["BENIGN", "LIKELY_BENIGN"])

    k562_struct = k562[struct_mask(k562)]
    cardiac_struct = cardiac[struct_mask(cardiac)]

    # Унион категорий, отсортированный по суммарному числу вызовов
    all_cats = set(k562_struct["Category"].dropna()) | set(cardiac_struct["Category"].dropna())
    cat_totals = {
        c: k562_struct["Category"].value_counts().get(c, 0)
        + cardiac_struct["Category"].value_counts().get(c, 0)
        for c in all_cats
    }
    # ПОЧЕМУ сортировка по убыванию: самые значимые категории слева
    categories = sorted(cat_totals, key=lambda c: cat_totals[c], reverse=True)

    k562_counts = [k562_struct["Category"].value_counts().get(c, 0) for c in categories]
    cardiac_counts = [cardiac_struct["Category"].value_counts().get(c, 0) for c in categories]

    x = np.arange(len(categories))
    width = 0.38

    bars_k562 = ax.bar(
        x - width / 2, k562_counts, width, label="K562", color=COLOR_K562, alpha=0.85
    )
    bars_cardiac = ax.bar(
        x + width / 2, cardiac_counts, width, label="Cardiac", color=COLOR_CARDIAC, alpha=0.85
    )

    # Подписи значений на столбцах (только ненулевые)
    def _label_bars(bars: list, counts: list) -> None:
        for bar, count in zip(bars, counts):
            if count > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1.5,
                    str(count),
                    ha="center",
                    va="bottom",
                    fontsize=6,
                    rotation=90 if count < 20 else 0,
                )

    _label_bars(bars_k562, k562_counts)
    _label_bars(bars_cardiac, cardiac_counts)

    # Красивые подписи категорий
    cat_labels = [c.replace("_", "\n") for c in categories]
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=6.5)
    ax.set_ylabel("Structural Calls (n)", fontsize=8)
    ax.set_title("B  Structural Calls by Category", fontsize=9, loc="left", fontweight="bold")

    # Итог в легенде
    ax.legend(
        handles=[
            mpatches.Patch(facecolor=COLOR_K562, alpha=0.85, label=f"K562 (n={len(k562_struct)})"),
            mpatches.Patch(
                facecolor=COLOR_CARDIAC, alpha=0.85, label=f"Cardiac (n={len(cardiac_struct)})"
            ),
        ],
        fontsize=7,
        frameon=False,
    )

    _remove_spines(ax)
    ax.tick_params(axis="both", labelsize=7)


# ---------------------------------------------------------------------------
# Panel C — Signal Amplification Summary
# ---------------------------------------------------------------------------
def plot_panel_c(ax: plt.Axes) -> None:
    """
    Горизонтальный barh: cardiac / k562 ratio для 4 метрик.
    Вертикальная линия ratio=1.0 — baseline.
    Аннотации с реальными числами обоих источников.
    """
    metrics = [
        {
            "label": "Delta P−B\n(|Δ| mean)",
            "ratio": CANON["ratio"]["delta"],
            "k562_val": f"{abs(CANON['k562']['delta']):.4f}",
            "cardiac_val": f"{abs(CANON['cardiac']['delta']):.4f}",
        },
        {
            "label": "Structural\nCalls",
            "ratio": CANON["ratio"]["struct_calls"],
            "k562_val": str(CANON["k562"]["struct_calls"]),
            "cardiac_val": str(CANON["cardiac"]["struct_calls"]),
        },
        {
            "label": "Q2 Variants\n(struct calls)",
            "ratio": CANON["ratio"]["q2"],
            "k562_val": str(CANON["k562"]["q2"]),
            "cardiac_val": str(CANON["cardiac"]["q2"]),
        },
        {
            "label": "Frameshift\nMin LSSIM\n(1 − min)",
            "ratio": round(
                (1 - CANON["cardiac"]["frameshift_min"]) / (1 - CANON["k562"]["frameshift_min"]), 2
            ),
            "k562_val": f"{CANON['k562']['frameshift_min']:.4f}",
            "cardiac_val": f"{CANON['cardiac']['frameshift_min']:.4f}",
        },
    ]

    y_pos = np.arange(len(metrics))
    ratios = [m["ratio"] for m in metrics]

    # ПОЧЕМУ цвет зависит от ratio>1: зелёный = усиление, серый = нет разницы
    colors = [COLOR_CARDIAC if r > 1.0 else "grey" for r in ratios]

    bars = ax.barh(y_pos, ratios, color=colors, alpha=0.85, height=0.55)

    # Аннотации: K562 val → Cardiac val
    for i, (bar, m) in enumerate(zip(bars, metrics)):
        ratio_val = m["ratio"]
        # Текст справа от бара
        ax.text(
            ratio_val + 0.05,
            i,
            f"×{ratio_val:.2f}  ({m['k562_val']} → {m['cardiac_val']})",
            va="center",
            fontsize=7,
            color="black",
        )

    # Baseline ratio=1
    ax.axvline(x=1.0, color="black", linewidth=1.0, linestyle="-", alpha=0.8)
    ax.text(1.01, len(metrics) - 0.1, "baseline\n(ratio=1)", fontsize=6, color="grey", va="top")

    ax.set_yticks(y_pos)
    ax.set_yticklabels([m["label"] for m in metrics], fontsize=7.5)
    ax.set_xlabel("Cardiac / K562 ratio", fontsize=8)
    ax.set_title("C  Cardiac vs K562 Amplification", fontsize=9, loc="left", fontweight="bold")

    # xlim: немного правее самого большого ratio + место для аннотаций
    ax.set_xlim(0, max(ratios) + 1.6)

    _remove_spines(ax, keep=("bottom",))
    ax.tick_params(axis="both", labelsize=7)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Собрать фигуру из трёх панелей и сохранить PDF + PNG."""
    k562, cardiac = load_data()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.subplots_adjust(wspace=0.38, left=0.05, right=0.97, top=0.90, bottom=0.12)

    plot_panel_a(axes[0], k562, cardiac)
    plot_panel_b(axes[1], k562, cardiac)
    plot_panel_c(axes[2])

    # Общий заголовок
    fig.suptitle(
        "SCN5A: Tissue-Mismatch (K562) vs Tissue-Matched (Cardiac) — ARCHCODE Comparison",
        fontsize=10,
        fontweight="bold",
        y=0.97,
    )

    pdf_path = OUT_DIR / "fig_scn5a_cardiac_comparison.pdf"
    png_path = OUT_DIR / "fig_scn5a_cardiac_comparison.png"

    fig.savefig(pdf_path, dpi=300, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    log.info("figure_saved", pdf=str(pdf_path), png=str(png_path))
    print(f"Saved:\n  {pdf_path}\n  {png_path}")


if __name__ == "__main__":
    main()
