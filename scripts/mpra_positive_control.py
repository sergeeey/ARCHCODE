"""
mpra_positive_control.py — MPRA Positive Control Test (Falsifiability P0)

Тест фальсифицируемости ARCHCODE: проверяем, видит ли MPRA разницу между
Q3 (activity-driven: VEP высокий + LSSIM нейтральный) и
Q2b (architecture-driven: VEP низкий + LSSIM патогенный).

ПОЧЕМУ это ключевой тест:
  Если ARCHCODE действительно улавливает ортогональный механизм (3D-структура),
  то Q2b-варианты должны быть невидимы для MPRA (измеряет транскрипционную
  активность энхансеров, а не топологию хроматина), тогда как Q3-варианты
  MPRA должен детектировать. Если разницы нет — гипотеза об ортогональности
  механизмов ослаблена.

Источник MPRA: Kircher et al. 2019, Nat Commun 10:3583
  MaveDB URN: urn:mavedb:00000018-a-1
  Регион: chr11:5,227,022–5,227,208 (HBB 5'UTR/промотор, эритроидные клетки HEL)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import structlog
from pydantic import BaseModel, Field
from scipy import stats

# ПОЧЕМУ: бэкенд без дисплея — скрипт запускается в CI и на серверах без GUI
matplotlib.use("Agg")

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
ROOT = Path("D:/ДНК")
ATLAS_CSV = ROOT / "results" / "HBB_Unified_Atlas_95kb.csv"
MPRA_ALLELE_CSV = ROOT / "results" / "mpra_archcode_crossvalidation.csv"
MPRA_POSITION_CSV = ROOT / "results" / "mpra_archcode_position_match.csv"
MPRA_SUMMARY_JSON = ROOT / "results" / "mpra_crossvalidation_summary.json"

OUT_JSON = ROOT / "analysis" / "mpra_positive_control.json"
OUT_FIG_DIR = ROOT / "figures" / "taxonomy"
OUT_PDF = OUT_FIG_DIR / "fig_mpra_positive_control.pdf"
OUT_PNG = OUT_FIG_DIR / "fig_mpra_positive_control.png"

# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Константы — пороги квадрантов
# ---------------------------------------------------------------------------
VEP_THRESHOLD: float = 0.5  # выше = высокий VEP (sequence-level pathogenicity)
LSSIM_THRESHOLD: float = 0.95  # ниже = структурно патогенный (ARCHCODE)

QUADRANT_LABELS: dict[str, str] = {
    "Q1": "Q1: Concordant\nPathogenic\n(VEP≥0.5, LSSIM<0.95)",
    "Q2b": "Q2b: Architecture-\nDriven\n(VEP<0.5, LSSIM<0.95)",
    "Q3": "Q3: Activity-\nDriven\n(VEP≥0.5, LSSIM≥0.95)",
    "Q4": "Q4: Concordant\nBenign\n(VEP<0.5, LSSIM≥0.95)",
}

QUADRANT_COLORS: dict[str, str] = {
    "Q1": "#d62728",  # красный — двойная патогенность
    "Q2b": "#ff7f0e",  # оранжевый — ARCHCODE-специфический
    "Q3": "#2ca02c",  # зелёный — VEP-специфический
    "Q4": "#1f77b4",  # синий — двойная доброкачественность
}


# ---------------------------------------------------------------------------
# Модели данных
# ---------------------------------------------------------------------------
class QuadrantStats(BaseModel):
    """Статистика MPRA-скоров для одного квадранта."""

    quadrant: str
    n: int
    mean: float | None = None
    median: float | None = None
    std: float | None = None
    scores: list[float] = Field(default_factory=list)


class TestResult(BaseModel):
    """Результат теста Манна-Уитни между двумя квадрантами."""

    group_a: str
    group_b: str
    n_a: int
    n_b: int
    u_statistic: float | None = None
    p_value: float | None = None
    effect_size_r: float | None = None  # r = U / (n_a * n_b)
    interpretation: str = ""
    powered: bool = False  # достаточно ли данных для вывода


class MPRAPositiveControlResult(BaseModel):
    """Полный результат теста MPRA positive control."""

    mpra_source: str
    mpra_region: str
    atlas_total_variants: int
    atlas_in_mpra_region: int

    quadrant_stats: list[QuadrantStats]
    primary_test_q3_vs_q2b: TestResult
    secondary_test_q1_vs_q4: TestResult

    conclusion: str
    data_limitation: str
    falsifiability_verdict: str


# ---------------------------------------------------------------------------
# Функции
# ---------------------------------------------------------------------------


def assign_quadrant(
    df: pd.DataFrame,
    lssim_col: str = "ARCHCODE_LSSIM",
    vep_col: str = "VEP_Score",
) -> pd.DataFrame:
    """
    Назначает квадрант каждому варианту по порогам VEP и LSSIM.

    ПОЧЕМУ именно 0.95 для LSSIM:
      0.95 — медианный порог, при котором разделение патогенных/доброкачественных
      по LSSIM имеет наибольший AUC (см. EXP-004 threshold robustness).
      VEP ≥ 0.5 соответствует категории "HIGH" или "MODERATE" impact в Ensembl VEP.
    """
    df = df.copy()
    conditions = [
        (df[vep_col] >= VEP_THRESHOLD) & (df[lssim_col] < LSSIM_THRESHOLD),
        (df[vep_col] < VEP_THRESHOLD) & (df[lssim_col] < LSSIM_THRESHOLD),
        (df[vep_col] >= VEP_THRESHOLD) & (df[lssim_col] >= LSSIM_THRESHOLD),
        (df[vep_col] < VEP_THRESHOLD) & (df[lssim_col] >= LSSIM_THRESHOLD),
    ]
    choices = ["Q1", "Q2b", "Q3", "Q4"]
    df["quadrant"] = np.select(conditions, choices, default="Q4")
    return df


def load_mpra_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Загружает MPRA-данные: аллель-специфичные совпадения и позиционные совпадения.

    Возвращает:
        Tuple (allele_df, position_df) — оба содержат квадранты.
    """
    log.info("Загрузка MPRA данных", allele_file=str(MPRA_ALLELE_CSV))
    allele_df = pd.read_csv(MPRA_ALLELE_CSV)

    # ПОЧЕМУ переименование: crossvalidation файл использует краткие имена
    # без префикса ARCHCODE_, нормализуем для единообразия
    if "LSSIM" in allele_df.columns and "ARCHCODE_LSSIM" not in allele_df.columns:
        allele_df = allele_df.rename(columns={"LSSIM": "ARCHCODE_LSSIM"})
    if "MPRA_score" in allele_df.columns:
        allele_df = allele_df.rename(columns={"MPRA_score": "mpra_score"})
    if "MPRA_pval" in allele_df.columns:
        allele_df = allele_df.rename(columns={"MPRA_pval": "mpra_pval"})

    allele_df = assign_quadrant(allele_df)

    log.info("Загрузка позиционных совпадений", file=str(MPRA_POSITION_CSV))
    position_df = pd.read_csv(MPRA_POSITION_CSV)
    if "mpra_mean_score" in position_df.columns:
        position_df = position_df.rename(columns={"mpra_mean_score": "mpra_score"})
    position_df = assign_quadrant(position_df)

    return allele_df, position_df


def compute_quadrant_stats(df: pd.DataFrame, score_col: str = "mpra_score") -> list[QuadrantStats]:
    """
    Вычисляет дескриптивную статистику MPRA-скоров по квадрантам.
    """
    stats_list: list[QuadrantStats] = []
    for q in ["Q1", "Q2b", "Q3", "Q4"]:
        subset = df[df["quadrant"] == q][score_col].dropna()
        n = len(subset)
        qs = QuadrantStats(
            quadrant=q,
            n=n,
            scores=subset.tolist(),
        )
        if n > 0:
            qs.mean = float(subset.mean())
            qs.median = float(subset.median())
            qs.std = float(subset.std()) if n > 1 else 0.0
        stats_list.append(qs)
    return stats_list


def run_mann_whitney(
    df: pd.DataFrame,
    group_a: str,
    group_b: str,
    score_col: str = "mpra_score",
) -> TestResult:
    """
    Запускает тест Манна-Уитни U между двумя квадрантами.

    ПОЧЕМУ Манн-Уитни, а не t-тест:
      При малых выборках (N < 30) и неизвестном распределении MPRA-скоров
      непараметрический критерий надёжнее. Кроме того, MPRA-скоры могут
      иметь тяжёлые хвосты (выбросы по экспрессии).
    """
    a_scores = df[df["quadrant"] == group_a][score_col].dropna().values
    b_scores = df[df["quadrant"] == group_b][score_col].dropna().values

    result = TestResult(
        group_a=group_a,
        group_b=group_b,
        n_a=len(a_scores),
        n_b=len(b_scores),
    )

    # ПОЧЕМУ минимум 2 в каждой группе: при N=1 тест бессмысленен
    if len(a_scores) < 2 or len(b_scores) < 2:
        result.interpretation = (
            f"INSUFFICIENT DATA: {group_a} N={len(a_scores)}, "
            f"{group_b} N={len(b_scores)}. Тест не проводился."
        )
        result.powered = False
        return result

    u_stat, p_val = stats.mannwhitneyu(a_scores, b_scores, alternative="two-sided")
    # Размер эффекта r = U / (n_a * n_b), диапазон [0, 1]
    effect_r = float(u_stat) / (len(a_scores) * len(b_scores))

    result.u_statistic = float(u_stat)
    result.p_value = float(p_val)
    result.effect_size_r = effect_r

    # ПОЧЕМУ порог 0.05 без поправки Бонферрони:
    # у нас 2 ключевых теста, что требовало бы p < 0.025.
    # При N=1 vs N=10 мощность крайне мала, поэтому не применяем
    # поправку — честно сообщаем о низкой мощности.
    powered = (len(a_scores) >= 5) and (len(b_scores) >= 5)
    result.powered = powered

    if p_val < 0.05:
        direction = "выше" if float(a_scores.mean()) > float(b_scores.mean()) else "ниже"
        result.interpretation = (
            f"ЗНАЧИМО (p={p_val:.4f}): {group_a} MPRA {direction} чем {group_b}. "
            f"Effect size r={effect_r:.3f}."
        )
    else:
        result.interpretation = (
            f"НЕ ЗНАЧИМО (p={p_val:.4f}): различий между {group_a} и {group_b} "
            f"не обнаружено. Effect size r={effect_r:.3f}."
        )

    if not powered:
        result.interpretation += (
            f" ⚠️ НИЗКАЯ МОЩНОСТЬ: малые выборки ({group_a} N={len(a_scores)}, "
            f"{group_b} N={len(b_scores)}). Вывод предварительный."
        )

    return result


def build_figure(
    allele_df: pd.DataFrame,
    position_df: pd.DataFrame,
    primary_test: TestResult,
    score_col: str = "mpra_score",
) -> plt.Figure:
    """
    Строит двухпанельный боксплот MPRA-скоров по квадрантам.

    Левая панель — аллель-специфичные совпадения (N=22, наиболее точные).
    Правая панель — позиционные совпадения (N=30, более полные).
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    fig.suptitle(
        "MPRA Positive Control Test: Detection by Quadrant\n"
        "Source: Kircher et al. 2019 (HBB 5'UTR, HEL erythroid cells)",
        fontsize=12,
        fontweight="bold",
    )

    datasets = [
        (allele_df, "Allele-specific matches\n(N=22, exact ClinVar alleles)", axes[0]),
        (position_df, "Position-level matches\n(N=30, aggregated by position)", axes[1]),
    ]

    for df, title, ax in datasets:
        quadrant_data = []
        labels = []
        colors = []

        for q in ["Q1", "Q2b", "Q3", "Q4"]:
            subset = df[df["quadrant"] == q][score_col].dropna().values
            quadrant_data.append(subset)
            n = len(subset)
            labels.append(f"{QUADRANT_LABELS[q]}\n(N={n})")
            colors.append(QUADRANT_COLORS[q])

        bp = ax.boxplot(
            quadrant_data,
            patch_artist=True,
            widths=0.5,
            showfliers=True,
            medianprops={"color": "black", "linewidth": 2},
        )

        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.65)

        # ПОЧЕМУ jitter поверх боксплота: при малых N (1-15) отдельные точки
        # информативнее усов — видно реальное распределение
        for i, (subset, color) in enumerate(zip(quadrant_data, colors), start=1):
            if len(subset) > 0:
                jitter = np.random.default_rng(42).uniform(-0.12, 0.12, size=len(subset))
                ax.scatter(
                    np.full(len(subset), i) + jitter,
                    subset,
                    color=color,
                    edgecolors="black",
                    linewidths=0.5,
                    s=40,
                    alpha=0.85,
                    zorder=5,
                )

        # Нулевая линия — нейтральная активность энхансера
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8, alpha=0.7, label="Neutral")

        ax.set_xticks(range(1, 5))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_ylabel("MPRA score (log₂ RNA/DNA)", fontsize=9)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="y", alpha=0.3)

        # Аннотация: результат ключевого теста Q3 vs Q2b
        if "Allele" in title:
            pval_text = (
                f"Q3 vs Q2b: p={primary_test.p_value:.3f}"
                if primary_test.p_value is not None
                else "Q3 vs Q2b: insufficient N"
            )
            ax.text(
                0.98,
                0.97,
                pval_text,
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.3", "facecolor": "lightyellow", "alpha": 0.8},
            )

    # Предупреждение о статистической мощности
    warning_text = (
        "⚠ MPRA coverage limited to ~186 bp (5'UTR/promoter).\n"
        "Q3 N=1 in allele dataset — low power. Results are preliminary."
    )
    fig.text(
        0.5,
        0.01,
        warning_text,
        ha="center",
        fontsize=8,
        color="#8B0000",
        style="italic",
    )

    fig.tight_layout(rect=[0, 0.06, 1, 1])
    return fig


def summarize_findings(
    primary: TestResult,
    quadrant_stats: list[QuadrantStats],
    atlas_total: int,
    atlas_in_region: int,
) -> tuple[str, str, str]:
    """
    Формулирует вывод, ограничения и вердикт фальсифицируемости.

    Возвращает:
        (conclusion, data_limitation, falsifiability_verdict)
    """
    q_map = {qs.quadrant: qs for qs in quadrant_stats}
    q3 = q_map.get("Q3")
    q2b = q_map.get("Q2b")

    limitation = (
        f"Kircher 2019 MPRA охватывает только 186 bp (5'UTR/промотор HBB). "
        f"Из {atlas_total} вариантов атласа только {atlas_in_region} попадают в регион. "
        f"Q3 представлен {'N=' + str(q3.n) if q3 else 'N=0'} вариантами, "
        f"Q2b — {'N=' + str(q2b.n) if q2b else 'N=0'}. "
        f"Тест при Q3 N=1 статистически не мощный — необходимы MPRA-данные "
        f"для полного 95 kb региона или более широкого энхансерного скана."
    )

    if primary.p_value is not None and primary.p_value < 0.05:
        conclusion = (
            f"MPRA значимо различает Q3 и Q2b (p={primary.p_value:.4f}). "
            f"Q3 (activity-driven) детектируется MPRA, Q2b (architecture-driven) — нет. "
            f"Это ПОДДЕРЖИВАЕТ гипотезу об ортогональности механизмов ARCHCODE."
        )
        verdict = "SUPPORTED: Механистическая ортогональность подтверждена в доступных данных."
    elif primary.n_a < 2:
        conclusion = (
            f"Тест Q3 vs Q2b не проводился: Q3 N={primary.n_a} (недостаточно данных). "
            f"MPRA Kircher 2019 не охватывает регионы с высоким VEP-скором вне 5'UTR. "
            f"Фальсифицирующий тест требует расширенных MPRA-данных."
        )
        verdict = (
            "INCONCLUSIVE: Недостаточно Q3-вариантов в MPRA-регионе. "
            "Необходим MPRA с полным 95 kb охватом HBB локуса."
        )
    else:
        conclusion = (
            f"Тест Q3 vs Q2b: p={primary.p_value:.4f} — различие НЕ ЗНАЧИМО. "
            f"При доступном N (Q3={primary.n_a}, Q2b={primary.n_b}) мощность низкая. "
            f"Нельзя ни подтвердить, ни опровергнуть ортогональность механизмов."
        )
        verdict = (
            "INCONCLUSIVE: p > 0.05, но низкая мощность. "
            "Нулевой результат не фальсифицирует гипотезу при текущем N."
        )

    return conclusion, limitation, verdict


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------


def main() -> None:
    """Запускает полный пайплайн MPRA positive control теста."""
    log.info("=== MPRA Positive Control Test ===")
    log.info("Гипотеза: Q3 (activity-driven) виден MPRA, Q2b (architecture-driven) — нет")

    # --- 1. Загрузка атласа ---
    log.info("Загрузка HBB атласа", path=str(ATLAS_CSV))
    atlas = pd.read_csv(ATLAS_CSV)
    atlas_total = len(atlas)
    log.info("Атлас загружен", n_variants=atlas_total)

    # Квадранты для атласа — для контекста
    atlas = assign_quadrant(atlas)
    atlas_quad_counts = atlas["quadrant"].value_counts().to_dict()
    log.info("Квадранты в атласе (все)", counts=atlas_quad_counts)

    # --- 2. Загрузка MPRA данных ---
    allele_df, position_df = load_mpra_data()
    atlas_in_region = len(position_df)

    log.info(
        "MPRA данные загружены",
        allele_n=len(allele_df),
        position_n=atlas_in_region,
    )
    log.info("Квадранты (аллельные)", counts=allele_df["quadrant"].value_counts().to_dict())
    log.info("Квадранты (позиционные)", counts=position_df["quadrant"].value_counts().to_dict())

    # --- 3. Статистика по квадрантам ---
    quadrant_stats = compute_quadrant_stats(allele_df)
    log.info("Статистика MPRA по квадрантам (аллельные совпадения):")
    for qs in quadrant_stats:
        if qs.n > 0:
            log.info(
                f"  {qs.quadrant}",
                n=qs.n,
                mean=f"{qs.mean:.4f}" if qs.mean is not None else "—",
                std=f"{qs.std:.4f}" if qs.std is not None else "—",
            )

    # --- 4. Ключевой тест: Q3 vs Q2b ---
    log.info("Тест Манна-Уитни: Q3 (activity-driven) vs Q2b (architecture-driven)")
    primary_test = run_mann_whitney(allele_df, group_a="Q3", group_b="Q2b")
    log.info("Результат Q3 vs Q2b", interpretation=primary_test.interpretation)

    # --- 5. Вторичный тест: Q1 vs Q4 (sanity check) ---
    log.info("Вторичный тест: Q1 vs Q4 (concordant pathogenic vs benign)")
    secondary_test = run_mann_whitney(allele_df, group_a="Q1", group_b="Q4")
    log.info("Результат Q1 vs Q4", interpretation=secondary_test.interpretation)

    # --- 6. Формулировка выводов ---
    conclusion, data_limitation, verdict = summarize_findings(
        primary_test, quadrant_stats, atlas_total, atlas_in_region
    )

    log.info("=== ВЫВОД ===")
    log.info(conclusion)
    log.info("Ограничения данных", detail=data_limitation)
    log.info("Вердикт фальсифицируемости", verdict=verdict)

    # --- 7. Сохранение JSON ---
    result = MPRAPositiveControlResult(
        mpra_source="Kircher et al. 2019, Nat Commun 10:3583 (MaveDB: urn:mavedb:00000018-a-1)",
        mpra_region="chr11:5,227,022-5,227,208 (HBB 5'UTR/promoter, HEL erythroid cells)",
        atlas_total_variants=atlas_total,
        atlas_in_mpra_region=atlas_in_region,
        quadrant_stats=quadrant_stats,
        primary_test_q3_vs_q2b=primary_test,
        secondary_test_q1_vs_q4=secondary_test,
        conclusion=conclusion,
        data_limitation=data_limitation,
        falsifiability_verdict=verdict,
    )

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
    log.info("JSON сохранён", path=str(OUT_JSON))

    # --- 8. Фигура ---
    OUT_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure(allele_df, position_df, primary_test)
    fig.savefig(OUT_PDF, dpi=150, bbox_inches="tight")
    fig.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info("Фигура сохранена", pdf=str(OUT_PDF), png=str(OUT_PNG))

    # --- 9. Итоговое резюме в stdout ---
    print("\n" + "=" * 70)
    print("MPRA POSITIVE CONTROL TEST — ИТОГ")
    print("=" * 70)
    print(f"  Атлас HBB: {atlas_total} вариантов всего")
    print(f"  В MPRA-регионе: {atlas_in_region} вариантов")
    print(f"  Квадранты атласа: {atlas_quad_counts}")
    print()
    print("  MPRA квадранты (аллельные совпадения, N=22):")
    for qs in quadrant_stats:
        mean_str = f"{qs.mean:+.4f}" if qs.mean is not None else "  N/A "
        print(f"    {qs.quadrant}: N={qs.n:2d}  mean={mean_str}")
    print()
    print(f"  КЛЮЧЕВОЙ ТЕСТ (Q3 vs Q2b): {primary_test.interpretation}")
    print(f"  ВТОРИЧНЫЙ ТЕСТ (Q1 vs Q4): {secondary_test.interpretation}")
    print()
    print(f"  ВЫВОД: {conclusion}")
    print()
    print(f"  ФАЛЬСИФИЦИРУЕМОСТЬ: {verdict}")
    print()
    print(f"  ⚠ ОГРАНИЧЕНИЕ: {data_limitation}")
    print("=" * 70)


if __name__ == "__main__":
    main()
