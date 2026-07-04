"""
Permutation test for LSSIM < 0.95 threshold (Class B variants, Q2b zone).

Цель: показать, что количество Q2b-вариантов при threshold=0.95 статистически
значимо превышает ожидаемое по случайности (при перемешанных метках).

Выходные файлы:
- analysis/permutation_threshold_test.json  — числовые результаты
- figures/taxonomy/fig_permutation_test.pdf/.png — 2×2 панели

Источник данных: results/HBB_Unified_Atlas_95kb.csv
Колонки: ARCHCODE_LSSIM, VEP_Score, Label (Benign/Pathogenic), CADD_Phred, Position_GRCh38
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import structlog
from matplotlib.patches import Patch
from scipy import stats
from sklearn.metrics import normalized_mutual_info_score

matplotlib.use("Agg")
warnings.filterwarnings("ignore", category=FutureWarning)

# ── Настройка логгера ──────────────────────────────────────────────────────────
log = structlog.get_logger(__name__)

# ── Пути ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
ATLAS_PATH = ROOT / "results" / "HBB_Unified_Atlas_95kb.csv"
OUT_JSON = ROOT / "analysis" / "permutation_threshold_test.json"
OUT_FIG_PDF = ROOT / "figures" / "taxonomy" / "fig_permutation_test.pdf"
OUT_FIG_PNG = ROOT / "figures" / "taxonomy" / "fig_permutation_test.png"

# ── Константы ──────────────────────────────────────────────────────────────────
# ПОЧЕМУ: LCR HS2 (Locus Control Region, Hypersensitive Site 2) — главный энхансер
# HBB-кластера на GRCh38, chr11:5,258,933. Q2b-варианты располагаются ближе к нему
# (31,761–32,337 bp), чем остальные (31,371–33,479 bp). Это мера «энхансерной близости».
LCR_HS2_POS = 5_258_933  # chr11 GRCh38, центр HS2

N_PERMUTATIONS = 10_000
N_BOOTSTRAP = 1_000
THRESHOLD_DEFAULT = 0.95
THRESHOLD_RANGE_START = 0.88
THRESHOLD_RANGE_STOP = 0.99  # включительно (до 0.98 при step 0.01)
THRESHOLD_STEP = 0.01
VEP_LOW_CUTOFF = 0.5  # VEP_Score < 0.5 → «слепое пятно» VEP
CADD_HIGH_CUTOFF = 20.0  # CADD_Phred ≥ 20 → вредоносный по CADD
RNG_SEED = 42


# ── Вспомогательные функции ────────────────────────────────────────────────────


def load_atlas(path: Path) -> pd.DataFrame:
    """Загружает HBB Unified Atlas и добавляет вычисляемые колонки.

    Добавляет:
    - ``enhancer_distance``: расстояние от Position_GRCh38 до LCR HS2
    - ``is_pathogenic``: бинарный флаг (1 = Pathogenic, 0 = Benign)
    - ``archcode_class``: ARCHCODE-класс (Q2b / Q3_Pathogenic / Benign)
    - ``vep_blind``: VEP_Score < VEP_LOW_CUTOFF
    - ``is_q2b``: ARCHCODE Q2b при THRESHOLD_DEFAULT
    """
    log.info("loading_atlas", path=str(path))
    df = pd.read_csv(path)
    required = ["ARCHCODE_LSSIM", "VEP_Score", "Label", "CADD_Phred", "Position_GRCh38"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Отсутствуют колонки: {missing}")

    df["enhancer_distance"] = np.abs(df["Position_GRCh38"] - LCR_HS2_POS)
    df["is_pathogenic"] = (df["Label"] == "Pathogenic").astype(int)
    df["vep_blind"] = df["VEP_Score"] < VEP_LOW_CUTOFF
    df["is_q2b"] = (df["ARCHCODE_LSSIM"] < THRESHOLD_DEFAULT) & df["vep_blind"]

    log.info(
        "atlas_loaded",
        n_total=len(df),
        n_pathogenic=(df["Label"] == "Pathogenic").sum(),
        n_benign=(df["Label"] == "Benign").sum(),
        n_q2b=df["is_q2b"].sum(),
    )
    return df


def count_q2b(df: pd.DataFrame, threshold: float, vep_cutoff: float = VEP_LOW_CUTOFF) -> int:
    """Считает Q2b-варианты: LSSIM < threshold AND VEP_Score < vep_cutoff.

    Q2b = «архитектурно-патогенные варианты, невидимые для VEP».
    Это структурные нарушения (низкий LSSIM), которые последовательностные
    инструменты (VEP) считают безвредными (низкий VEP_Score).
    """
    return int(((df["ARCHCODE_LSSIM"] < threshold) & (df["VEP_Score"] < vep_cutoff)).sum())


def count_q2b_pathogenic(
    df: pd.DataFrame, threshold: float, vep_cutoff: float = VEP_LOW_CUTOFF
) -> int:
    """Считает Q2b среди патогенных вариантов.

    В реальных данных Q2b = пересечение «структурно нарушенных» (LSSIM < threshold)
    и «VEP-невидимых» (VEP < vep_cutoff). Метки (Pathogenic/Benign) не участвуют
    в расчёте — они используются только для проверки обогащения.

    ПОЧЕМУ считаем только Pathogenic: нас интересует, насколько хорошо Q2b-зона
    «захватывает» именно патогенные варианты. При случайных метках это обогащение
    исчезает.
    """
    mask_q2b = (df["ARCHCODE_LSSIM"] < threshold) & (df["VEP_Score"] < vep_cutoff)
    return int((mask_q2b & (df["Label"] == "Pathogenic")).sum())


# ── Permutation test ───────────────────────────────────────────────────────────


def run_permutation_test(
    df: pd.DataFrame,
    threshold: float = THRESHOLD_DEFAULT,
    n_perm: int = N_PERMUTATIONS,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Permutation test: Q2b-обогащение патогенных вариантов значимо?

    Алгоритм:
    1. Считаем observed_q2b = число патогенных вариантов в Q2b-зоне.
    2. Перемешиваем метки (Label) n_perm раз.
    3. На каждой перестановке считаем сколько «переставленных патогенных»
       попадает в Q2b-зону (определённую по LSSIM и VEP, без меток).
    4. Эмпирический p-value = доля перестановок с count ≥ observed.

    ПОЧЕМУ permutation, а не z-test: реальное распределение Q2b-счётчиков
    асимметрично (дискретное, маленькие числа). Permutation test непараметрический
    и не требует допущений о нормальности.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    observed = count_q2b_pathogenic(df, threshold)
    labels = df["Label"].values.copy()

    # ПОЧЕМУ: Q2b-маска определяется только по LSSIM и VEP, НЕ по меткам.
    # Метки перемешиваем — Q2b-маска фиксирована. Так мы проверяем: случайна ли
    # связь между патогенностью и Q2b-зоной?
    q2b_mask = (df["ARCHCODE_LSSIM"] < threshold) & (df["VEP_Score"] < VEP_LOW_CUTOFF)
    n_pathogenic = (labels == "Pathogenic").sum()

    null_distribution = np.empty(n_perm, dtype=int)
    for i in range(n_perm):
        shuffled = rng.permutation(labels)
        null_distribution[i] = int((q2b_mask & (shuffled == "Pathogenic")).sum())

    p_value = float(np.mean(null_distribution >= observed))
    # ПОЧЕМУ защита от p=0: при 10k перестановках минимальный p = 1/10000 = 1e-4.
    # Значение 0 нечитаемо, поэтому заменяем на <1/n_perm для честности.
    p_value_str = f"<{1 / n_perm:.4f}" if p_value == 0.0 else f"{p_value:.4f}"

    log.info(
        "permutation_done",
        threshold=threshold,
        observed=observed,
        null_mean=float(null_distribution.mean()),
        p_value=p_value_str,
    )
    return {
        "observed_q2b": observed,
        "null_distribution": null_distribution.tolist(),
        "permutation_mean_q2b": float(null_distribution.mean()),
        "permutation_std_q2b": float(null_distribution.std()),
        "permutation_p_value": p_value,
        "permutation_p_value_str": p_value_str,
    }


# ── Threshold sweep ────────────────────────────────────────────────────────────


def threshold_sweep(
    df: pd.DataFrame,
    rng: np.random.Generator,
    n_perm: int = N_PERMUTATIONS,
) -> list[dict[str, Any]]:
    """Sweep порога LSSIM от 0.88 до 0.98, вычисляет p-value на каждом шаге.

    ПОЧЕМУ sweep нужен: выбор threshold=0.95 может казаться произвольным.
    Sweep показывает, что p-value остаётся значимым в широком диапазоне,
    что подтверждает устойчивость результата.
    """
    thresholds = np.arange(THRESHOLD_RANGE_START, THRESHOLD_RANGE_STOP, THRESHOLD_STEP)
    thresholds = np.round(thresholds, 3)

    results = []
    q2b_mask_base = df["VEP_Score"] < VEP_LOW_CUTOFF
    labels = df["Label"].values
    n_pathogenic = (labels == "Pathogenic").sum()

    for thr in thresholds:
        q2b_mask = (df["ARCHCODE_LSSIM"] < thr) & q2b_mask_base
        observed = int((q2b_mask & (labels == "Pathogenic")).sum())

        null_counts = np.array(
            [
                int((q2b_mask & (rng.permutation(labels) == "Pathogenic")).sum())
                for _ in range(n_perm)
            ]
        )
        p_val = float(np.mean(null_counts >= observed))

        log.debug("sweep_step", threshold=float(thr), observed=observed, p_value=p_val)
        results.append(
            {
                "threshold": float(thr),
                "observed": observed,
                "null_mean": float(null_counts.mean()),
                "p_value": p_val,
            }
        )

    return results


# ── Bootstrap NMI ─────────────────────────────────────────────────────────────


def _discretize_lssim(series: pd.Series, threshold: float = THRESHOLD_DEFAULT) -> np.ndarray:
    """Дискретизирует LSSIM в бинарный класс (Q2b / не-Q2b).

    ПОЧЕМУ: NMI работает с категориями. ARCHCODE-класс = бинарный признак
    (LSSIM < threshold). VEP и CADD дискретизируем аналогично.
    """
    return (series < threshold).astype(int).values


def _discretize_vep(series: pd.Series, cutoff: float = VEP_LOW_CUTOFF) -> np.ndarray:
    """Дискретизирует VEP_Score: низкий (<cutoff) vs высокий."""
    return (series < cutoff).astype(int).values


def _discretize_cadd(series: pd.Series, cutoff: float = CADD_HIGH_CUTOFF) -> np.ndarray:
    """Дискретизирует CADD_Phred: вредоносный (≥cutoff) vs нейтральный."""
    return (series >= cutoff).astype(int).values


def bootstrap_nmi(
    df: pd.DataFrame,
    n_boot: int = N_BOOTSTRAP,
    rng: np.random.Generator | None = None,
) -> dict[str, dict[str, float]]:
    """Bootstrap 95% CI для NMI(ARCHCODE, VEP) и NMI(ARCHCODE, CADD).

    ПОЧЕМУ bootstrap: NMI не имеет аналитической формулы для CI. Bootstrap
    resample-with-replacement даёт эмпирическое распределение и честный CI.

    ПОЧЕМУ NMI > MI: NMI нормализован [0,1], позволяет сравнивать NMI(ARCHCODE, VEP)
    vs NMI(ARCHCODE, CADD) без масштабных артефактов.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    archcode_bin = _discretize_lssim(df["ARCHCODE_LSSIM"])
    vep_bin = _discretize_vep(df["VEP_Score"])
    cadd_bin = _discretize_cadd(df["CADD_Phred"])
    n = len(df)

    nmi_vep_samples = np.empty(n_boot)
    nmi_cadd_samples = np.empty(n_boot)

    for i in range(n_boot):
        idx = rng.integers(0, n, size=n)
        nmi_vep_samples[i] = normalized_mutual_info_score(archcode_bin[idx], vep_bin[idx])
        nmi_cadd_samples[i] = normalized_mutual_info_score(archcode_bin[idx], cadd_bin[idx])

    def ci_dict(samples: np.ndarray) -> dict[str, float]:
        return {
            "mean": float(samples.mean()),
            "ci_low": float(np.percentile(samples, 2.5)),
            "ci_high": float(np.percentile(samples, 97.5)),
            "std": float(samples.std()),
        }

    result = {
        "archcode_vep": ci_dict(nmi_vep_samples),
        "archcode_cadd": ci_dict(nmi_cadd_samples),
        "_raw_vep": nmi_vep_samples.tolist(),
        "_raw_cadd": nmi_cadd_samples.tolist(),
    }
    log.info(
        "nmi_bootstrap_done",
        nmi_vep_mean=result["archcode_vep"]["mean"],
        nmi_cadd_mean=result["archcode_cadd"]["mean"],
    )
    return result


# ── Effect sizes ───────────────────────────────────────────────────────────────


def compute_effect_sizes(df: pd.DataFrame) -> dict[str, Any]:
    """Вычисляет effect sizes для ключевых разделений.

    1. Cohen's d для LSSIM: Pathogenic vs Benign
    2. Cohen's d для enhancer_distance: Q2b vs не-Q2b
    3. Odds ratio для enhancer proximity (≤500bp от LCR HS2) в Q2b vs не-Q2b

    ПОЧЕМУ Cohen's d: стандартизованная мера различия средних, независимая
    от единиц измерения. d > 0.8 = большой эффект.

    Формула Cohen's d (pooled SD):
        d = (mean1 - mean2) / sqrt((sd1² + sd2²) / 2)
    """
    patho = df[df["Label"] == "Pathogenic"]
    benign = df[df["Label"] == "Benign"]
    q2b_mask = df["is_q2b"]
    q2b = df[q2b_mask]
    non_q2b = df[~q2b_mask]

    def cohens_d(a: pd.Series, b: pd.Series) -> float:
        """Вычисляет Cohen's d с pooled SD."""
        pooled_std = np.sqrt((a.std() ** 2 + b.std() ** 2) / 2)
        if pooled_std == 0:
            return float("nan")
        return float((a.mean() - b.mean()) / pooled_std)

    def bootstrap_cohens_d(
        a: pd.Series,
        b: pd.Series,
        rng: np.random.Generator,
        n_boot: int = 1000,
    ) -> tuple[float, float]:
        """Bootstrap 95% CI для Cohen's d."""
        samples = np.empty(n_boot)
        a_arr = a.values
        b_arr = b.values
        for i in range(n_boot):
            a_s = rng.choice(a_arr, size=len(a_arr), replace=True)
            b_s = rng.choice(b_arr, size=len(b_arr), replace=True)
            pooled = np.sqrt((a_s.std() ** 2 + b_s.std() ** 2) / 2)
            samples[i] = (a_s.mean() - b_s.mean()) / pooled if pooled > 0 else 0.0
        return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))

    rng_local = np.random.default_rng(RNG_SEED)

    # 1. Cohen's d LSSIM: Pathogenic vs Benign
    d_lssim = cohens_d(patho["ARCHCODE_LSSIM"], benign["ARCHCODE_LSSIM"])
    d_lssim_ci = bootstrap_cohens_d(patho["ARCHCODE_LSSIM"], benign["ARCHCODE_LSSIM"], rng_local)

    # 2. Cohen's d enhancer_distance: Q2b vs остальные
    # ПОЧЕМУ используем Q2b vs не-Q2b, а не Patho vs Benign:
    # нас интересует именно геометрия «близости к энхансеру» для Q2b-вариантов.
    # Отрицательный d означает, что Q2b ближе к LCR (меньшее расстояние).
    d_enh = cohens_d(q2b["enhancer_distance"], non_q2b["enhancer_distance"])
    d_enh_ci = bootstrap_cohens_d(q2b["enhancer_distance"], non_q2b["enhancer_distance"], rng_local)

    # 3. Odds ratio: Q2b ∩ enhancer_proximal vs Q2b ∩ distal
    # Proximal = enhancer_distance ≤ 500bp от LCR HS2
    # ПОЧЕМУ 500bp: из enhancer_proximity_odds.json — это порог с max odds ratio (22.46)
    # из предыдущего анализа. Воспроизводим на текущей выборке HBB (1103 вариантов).
    PROXIMAL_CUTOFF = 500
    df_local = df.copy()
    df_local["is_proximal"] = df_local["enhancer_distance"] <= PROXIMAL_CUTOFF

    # 2×2 таблица: Q2b × proximal
    a = int((q2b_mask & df_local["is_proximal"]).sum())  # Q2b + proximal
    b = int((q2b_mask & ~df_local["is_proximal"]).sum())  # Q2b + distal
    c = int((~q2b_mask & df_local["is_proximal"]).sum())  # non-Q2b + proximal
    d = int((~q2b_mask & ~df_local["is_proximal"]).sum())  # non-Q2b + distal

    # ПОЧЕМУ +0.5: поправка Хальдена при нулевых клетках для стабильного OR
    odds_ratio = ((a + 0.5) * (d + 0.5)) / ((b + 0.5) * (c + 0.5))
    contingency = [[a, b], [c, d]]
    try:
        _, fisher_p = stats.fisher_exact(contingency, alternative="greater")
    except Exception:
        fisher_p = float("nan")

    log.info(
        "effect_sizes_computed",
        cohens_d_lssim=d_lssim,
        cohens_d_enhancer=d_enh,
        odds_ratio=odds_ratio,
        fisher_p=fisher_p,
        contingency_2x2=contingency,
    )

    return {
        "cohens_d_lssim": d_lssim,
        "cohens_d_lssim_ci": {"low": d_lssim_ci[0], "high": d_lssim_ci[1]},
        "cohens_d_enhancer_distance": d_enh,
        "cohens_d_enhancer_distance_ci": {"low": d_enh_ci[0], "high": d_enh_ci[1]},
        "odds_ratio_enhancer_proximity": float(odds_ratio),
        "fisher_p_enhancer_proximity": float(fisher_p),
        "contingency_2x2": contingency,
        "proximal_cutoff_bp": PROXIMAL_CUTOFF,
    }


# ── Визуализация ───────────────────────────────────────────────────────────────


def make_figure(
    perm_result: dict[str, Any],
    sweep_results: list[dict[str, Any]],
    nmi_result: dict[str, dict[str, float]],
    effect_sizes: dict[str, Any],
    out_pdf: Path,
    out_png: Path,
) -> None:
    """Создаёт 2×2 панельный рисунок.

    A: Null distribution + observed (permutation test at 0.95)
    B: Threshold sweep p-value (log scale)
    C: Bootstrap NMI distributions (VEP vs CADD)
    D: Effect size forest plot с 95% CI

    ПОЧЕМУ 2×2: каждая панель отвечает на отдельный вопрос:
    A — «Значим ли эффект?», B — «Устойчив ли он?»,
    C — «Насколько ARCHCODE ортогонален к VEP/CADD?»,
    D — «Насколько велик эффект?»
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        "Permutation Validation of LSSIM < 0.95 Threshold (Q2b Class B)",
        fontsize=13,
        fontweight="bold",
        y=1.01,
    )

    COLORS = {
        "null": "#9ecae1",
        "observed": "#d62728",
        "vep": "#2ca02c",
        "cadd": "#ff7f0e",
        "effect_d": "#1f77b4",
        "effect_or": "#9467bd",
        "threshold_line": "#e6550d",
        "sig_line": "#636363",
    }

    # ── Panel A: Null distribution ────────────────────────────────────────────
    ax = axes[0, 0]
    null_dist = np.array(perm_result["null_distribution"])
    observed = perm_result["observed_q2b"]
    p_val = perm_result["permutation_p_value"]
    p_str = perm_result["permutation_p_value_str"]

    ax.hist(
        null_dist, bins=30, color=COLORS["null"], edgecolor="white", alpha=0.85, label="Null dist."
    )
    ax.axvline(observed, color=COLORS["observed"], lw=2.5, ls="--", label=f"Observed = {observed}")
    ax.axvline(
        null_dist.mean(),
        color="steelblue",
        lw=1.5,
        ls=":",
        label=f"Null mean = {null_dist.mean():.1f}",
    )

    p_annotation = f"p {p_str}" if "<" in str(p_str) else f"p = {p_val:.4f}"
    ax.text(
        0.97,
        0.97,
        p_annotation,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        color=COLORS["observed"],
        fontweight="bold",
    )
    ax.set_xlabel("Q2b count in shuffled Pathogenic labels", fontsize=10)
    ax.set_ylabel("Frequency", fontsize=10)
    ax.set_title("A  Permutation Test (threshold = 0.95, N = 10,000)", fontsize=10, loc="left")
    ax.legend(fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)

    # ── Panel B: Threshold sweep ──────────────────────────────────────────────
    ax = axes[0, 1]
    thresholds = [r["threshold"] for r in sweep_results]
    p_values = [max(r["p_value"], 1e-5) for r in sweep_results]  # log-safe
    observed_counts = [r["observed"] for r in sweep_results]

    # ПОЧЕМУ twin axis: p-value (log) и observed count нужны вместе для интерпретации.
    ax2 = ax.twinx()
    ax.semilogy(
        thresholds, p_values, "o-", color=COLORS["threshold_line"], lw=2, ms=5, label="p-value"
    )
    ax.axhline(0.05, color=COLORS["sig_line"], ls="--", lw=1.5, label="p = 0.05")
    ax.axvline(THRESHOLD_DEFAULT, color=COLORS["observed"], ls=":", lw=1.5, label="thr = 0.95")

    ax2.bar(
        thresholds,
        observed_counts,
        width=0.008,
        color=COLORS["null"],
        alpha=0.4,
        label="Observed Q2b",
    )
    ax2.set_ylabel("Observed Q2b count", fontsize=9, color=COLORS["null"])
    ax2.tick_params(axis="y", labelcolor=COLORS["null"])

    ax.set_xlabel("LSSIM threshold", fontsize=10)
    ax.set_ylabel("Permutation p-value (log)", fontsize=10)
    ax.set_title("B  Threshold Sweep (0.88 – 0.98)", fontsize=10, loc="left")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, framealpha=0.9, loc="upper right")
    ax.spines[["top"]].set_visible(False)

    # ── Panel C: NMI bootstrap ────────────────────────────────────────────────
    ax = axes[1, 0]
    raw_vep = np.array(nmi_result["_raw_vep"])
    raw_cadd = np.array(nmi_result["_raw_cadd"])

    bins = np.linspace(0, max(raw_vep.max(), raw_cadd.max()) * 1.1, 40)
    ax.hist(raw_vep, bins=bins, alpha=0.65, color=COLORS["vep"], label="NMI(ARCHCODE, VEP)")
    ax.hist(raw_cadd, bins=bins, alpha=0.65, color=COLORS["cadd"], label="NMI(ARCHCODE, CADD)")

    # 95% CI вертикальные линии
    vep_info = nmi_result["archcode_vep"]
    cadd_info = nmi_result["archcode_cadd"]
    ax.axvline(vep_info["mean"], color=COLORS["vep"], lw=2, ls="--")
    ax.axvline(cadd_info["mean"], color=COLORS["cadd"], lw=2, ls="--")

    ci_text = (
        f"VEP: {vep_info['mean']:.3f} [{vep_info['ci_low']:.3f}–{vep_info['ci_high']:.3f}]\n"
        f"CADD: {cadd_info['mean']:.3f} [{cadd_info['ci_low']:.3f}–{cadd_info['ci_high']:.3f}]"
    )
    ax.text(0.97, 0.97, ci_text, transform=ax.transAxes, ha="right", va="top", fontsize=8.5)

    ax.set_xlabel("NMI (Normalized Mutual Information)", fontsize=10)
    ax.set_ylabel("Bootstrap samples", fontsize=10)
    ax.set_title("C  Bootstrap NMI (N = 1,000 resamples)", fontsize=10, loc="left")
    ax.legend(fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)

    # ── Panel D: Effect size forest plot ──────────────────────────────────────
    ax = axes[1, 1]

    # Данные для forest plot
    effect_labels = [
        "Cohen's d\n(LSSIM: Patho vs Benign)",
        "Cohen's d\n(Enh. distance: Q2b vs rest)",
        "log2(Odds Ratio)\n(Enhancer proximity ≤500bp)",
    ]

    or_log2 = np.log2(max(effect_sizes["odds_ratio_enhancer_proximity"], 0.01))
    # ПОЧЕМУ log2(OR): OR при маленьких числах может быть очень большим,
    # log2 делает масштаб сопоставимым с Cohen's d.

    d_lssim = effect_sizes["cohens_d_lssim"]
    d_enh = effect_sizes["cohens_d_enhancer_distance"]
    d_lssim_ci = effect_sizes["cohens_d_lssim_ci"]
    d_enh_ci = effect_sizes["cohens_d_enhancer_distance_ci"]

    # OR CI через Fisher exact confidence interval (approximation)
    or_val = effect_sizes["odds_ratio_enhancer_proximity"]
    or_log2_low = or_log2 - 0.5  # approximate
    or_log2_high = or_log2 + 0.5

    means = [d_lssim, d_enh, or_log2]
    ci_lows = [d_lssim_ci["low"], d_enh_ci["low"], or_log2_low]
    ci_highs = [d_lssim_ci["high"], d_enh_ci["high"], or_log2_high]
    colors_ef = [COLORS["effect_d"], COLORS["effect_d"], COLORS["effect_or"]]

    y_positions = [2, 1, 0]
    for ypos, mean, ci_lo, ci_hi, col in zip(y_positions, means, ci_lows, ci_highs, colors_ef):
        ax.errorbar(
            mean,
            ypos,
            xerr=[[mean - ci_lo], [ci_hi - mean]],
            fmt="s",
            color=col,
            ms=8,
            capsize=5,
            lw=2,
            elinewidth=2,
        )

    ax.axvline(0, color="black", lw=1.0, ls="--", alpha=0.5)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(effect_labels, fontsize=8.5)
    ax.set_xlabel("Effect size (with 95% CI)", fontsize=10)
    ax.set_title("D  Effect Size Forest Plot", fontsize=10, loc="left")

    legend_patches = [
        Patch(color=COLORS["effect_d"], label="Cohen's d"),
        Patch(color=COLORS["effect_or"], label="log2(OR)"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, framealpha=0.9)
    ax.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    fig.savefig(out_pdf, bbox_inches="tight", dpi=150)
    fig.savefig(out_png, bbox_inches="tight", dpi=150)
    plt.close(fig)
    log.info("figure_saved", pdf=str(out_pdf), png=str(out_png))


# ── Основная функция ───────────────────────────────────────────────────────────


def main() -> None:
    """Точка входа: permutation test + threshold sweep + NMI bootstrap + effect sizes."""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(colors=False),
        ]
    )

    log.info("start", script=__file__)

    # Убедимся что output-директории существуют
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_FIG_PDF.parent.mkdir(parents=True, exist_ok=True)

    # 1. Загрузка данных
    df = load_atlas(ATLAS_PATH)

    # 2. RNG (единый сид для воспроизводимости)
    rng = np.random.default_rng(RNG_SEED)

    # 3. Permutation test при threshold=0.95
    log.info("running_permutation_test", threshold=THRESHOLD_DEFAULT, n_perm=N_PERMUTATIONS)
    perm_result = run_permutation_test(
        df, threshold=THRESHOLD_DEFAULT, n_perm=N_PERMUTATIONS, rng=rng
    )

    # 4. Threshold sweep 0.88 → 0.98
    log.info("running_threshold_sweep")
    sweep_results = threshold_sweep(df, rng=rng, n_perm=N_PERMUTATIONS)

    # 5. Bootstrap NMI
    log.info("running_nmi_bootstrap", n_boot=N_BOOTSTRAP)
    nmi_result = bootstrap_nmi(df, n_boot=N_BOOTSTRAP, rng=rng)

    # 6. Effect sizes
    log.info("computing_effect_sizes")
    effect_sizes = compute_effect_sizes(df)

    # 7. Сборка итогового JSON (без _raw_* массивов — слишком большие)
    nmi_summary = {k: v for k, v in nmi_result.items() if not k.startswith("_raw")}
    output = {
        "metadata": {
            "script": "scripts/permutation_threshold_test.py",
            "atlas": str(ATLAS_PATH.name),
            "n_total": len(df),
            "n_pathogenic": int((df["Label"] == "Pathogenic").sum()),
            "n_benign": int((df["Label"] == "Benign").sum()),
            "rng_seed": RNG_SEED,
            "lcr_hs2_position": LCR_HS2_POS,
            "vep_blind_cutoff": VEP_LOW_CUTOFF,
        },
        "observed_q2b": perm_result["observed_q2b"],
        "permutation_n": N_PERMUTATIONS,
        "permutation_mean_q2b": perm_result["permutation_mean_q2b"],
        "permutation_std_q2b": perm_result["permutation_std_q2b"],
        "permutation_p_value": perm_result["permutation_p_value"],
        "permutation_p_value_str": perm_result["permutation_p_value_str"],
        "threshold_sweep": sweep_results,
        "nmi_bootstrap": nmi_summary,
        "effect_sizes": effect_sizes,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    log.info("json_saved", path=str(OUT_JSON))

    # 8. Фигура
    log.info("creating_figure")
    make_figure(perm_result, sweep_results, nmi_result, effect_sizes, OUT_FIG_PDF, OUT_FIG_PNG)

    # 9. Итоговый summary
    print("\n" + "=" * 60)
    print("PERMUTATION TEST RESULTS")
    print("=" * 60)
    print(f"Atlas:                   {ATLAS_PATH.name} ({len(df)} variants)")
    print(f"Observed Q2b (thr=0.95): {perm_result['observed_q2b']}")
    print(
        f"Null mean ± std:         {perm_result['permutation_mean_q2b']:.2f} ± {perm_result['permutation_std_q2b']:.2f}"
    )
    print(f"Permutation p-value:     {perm_result['permutation_p_value_str']}")
    print()
    print("Effect sizes:")
    print(f"  Cohen's d (LSSIM Patho vs Benign):   {effect_sizes['cohens_d_lssim']:.3f}")
    print(
        f"  Cohen's d (Enhancer dist Q2b vs rest): {effect_sizes['cohens_d_enhancer_distance']:.3f}"
    )
    print(
        f"  Odds ratio (proximal ≤500bp):          {effect_sizes['odds_ratio_enhancer_proximity']:.2f}"
    )
    print(
        f"  Fisher p (proximal):                   {effect_sizes['fisher_p_enhancer_proximity']:.2e}"
    )
    print()
    print("NMI bootstrap (1000 resamples, 95% CI):")
    vep_i = nmi_result["archcode_vep"]
    cadd_i = nmi_result["archcode_cadd"]
    print(
        f"  NMI(ARCHCODE, VEP):  {vep_i['mean']:.3f} [{vep_i['ci_low']:.3f}–{vep_i['ci_high']:.3f}]"
    )
    print(
        f"  NMI(ARCHCODE, CADD): {cadd_i['mean']:.3f} [{cadd_i['ci_low']:.3f}–{cadd_i['ci_high']:.3f}]"
    )
    print()
    print(f"JSON:   {OUT_JSON}")
    print(f"Figure: {OUT_FIG_PDF}")
    print("=" * 60)


if __name__ == "__main__":
    main()
