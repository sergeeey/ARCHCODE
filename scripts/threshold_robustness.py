"""
EXP-004: Threshold Robustness with Bootstrap CI

Tests stability of pearl count across three perturbation strategies:
1. Bootstrap resampling — sampling variance of pearl count
2. Threshold sweep across all 9 loci — sensitivity to threshold choice
3. LSSIM perturbation (±20% enhancer occupancy noise) — biological noise

Outputs:
- analysis/threshold_robustness.csv         — sweep results per locus
- analysis/threshold_robustness_summary.json — all three analyses
- figures/fig_threshold_robustness.pdf/.png  — 3-panel figure
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import structlog

matplotlib.use("Agg")  # ПОЧЕМУ: headless среда Windows, избегаем Qt/Tk ошибок

# ── Logging ──────────────────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()

# ── Константы ─────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
RESULTS_DIR = REPO_ROOT / "results"
ANALYSIS_DIR = REPO_ROOT / "analysis"
FIGURES_DIR = REPO_ROOT / "figures"

THRESHOLD_NOMINAL = 0.95  # основной порог из рукописи
BOOTSTRAP_N = 1000  # число bootstrap-итераций
PERTURB_N = 500  # число perturbation-итераций
STABILITY_TOLERANCE = 0.10  # ±10% от count at 0.95 для stability zone

# ПОЧЕМУ seed=42: воспроизводимость между запусками — это требование EXP-004
RNG_SEED = 42

ATLAS_FILES: dict[str, str] = {
    "HBB": "HBB_Unified_Atlas.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "TERT": "TERT_Unified_Atlas_300kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
    "GJB2": "GJB2_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
}


# ── Загрузка данных ────────────────────────────────────────────────────────────


def load_atlas(locus: str, filename: str) -> pd.DataFrame | None:
    """Загружает и фильтрует один atlas-файл по меченым вариантам.

    Возвращает только строки с Label in {Pathogenic, Benign} и непустым ARCHCODE_LSSIM.
    Возвращает None если файл не найден.
    """
    path = RESULTS_DIR / filename
    if not path.exists():
        log.warning("atlas_not_found", locus=locus, path=str(path))
        return None

    df = pd.read_csv(path)
    required = ["ARCHCODE_LSSIM", "Label"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        log.error("missing_columns", locus=locus, missing=missing)
        return None

    # ПОЧЕМУ: фильтруем только labeled варианты — это основной набор для валидации
    df = df[df["Label"].isin(["Pathogenic", "Benign"])].copy()
    df = df.dropna(subset=["ARCHCODE_LSSIM"])
    log.info(
        "atlas_loaded",
        locus=locus,
        rows=len(df),
        pathogenic=(df["Label"] == "Pathogenic").sum(),
        benign=(df["Label"] == "Benign").sum(),
    )
    return df


def load_hbb() -> pd.DataFrame:
    """Загружает HBB atlas; прерывает выполнение если файл недоступен."""
    df = load_atlas("HBB", ATLAS_FILES["HBB"])
    if df is None:
        log.error("hbb_atlas_missing — cannot run analyses that require HBB")
        sys.exit(1)
    return df


# ── Analysis 1: Bootstrap CI ───────────────────────────────────────────────────


def bootstrap_pearl_count(
    df: pd.DataFrame,
    threshold: float = THRESHOLD_NOMINAL,
    n_iterations: int = BOOTSTRAP_N,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Bootstrap CI на число pearl-вариантов среди патогенных.

    Resample патогенные варианты WITH replacement, считаем сколько имеют
    ARCHCODE_LSSIM < threshold. Это sampling variance из-за конечного датасета.

    Returns dict с mean, ci_low (2.5%), ci_high (97.5%), и массивом counts.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    pathogenic = df[df["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"].values
    n = len(pathogenic)

    if n == 0:
        log.warning("no_pathogenic_variants_for_bootstrap")
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0, "counts": []}

    counts = np.empty(n_iterations, dtype=np.int32)
    for i in range(n_iterations):
        # ПОЧЕМУ with replacement: bootstrap по определению — resample с повторением
        sample = rng.choice(pathogenic, size=n, replace=True)
        counts[i] = int((sample < threshold).sum())

    # Observed (не-bootstrap) значение для сравнения
    observed = int((pathogenic < threshold).sum())

    result = {
        "observed": observed,
        "mean": float(np.mean(counts)),
        "std": float(np.std(counts)),
        "ci_low": float(np.percentile(counts, 2.5)),
        "ci_high": float(np.percentile(counts, 97.5)),
        "n_pathogenic": n,
        "threshold": threshold,
        "n_iterations": n_iterations,
        "counts": counts.tolist(),
    }
    log.info(
        "bootstrap_complete",
        observed=observed,
        mean=f"{result['mean']:.2f}",
        ci=f"[{result['ci_low']:.1f}, {result['ci_high']:.1f}]",
    )
    return result


# ── Analysis 2: Threshold Sweep ────────────────────────────────────────────────


def threshold_sweep_locus(
    df: pd.DataFrame,
    locus: str,
    thresholds: np.ndarray,
) -> pd.DataFrame:
    """Sweep по порогам для одного локуса, возвращает DataFrame с count на каждом шаге."""
    pathogenic = df[df["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"].values
    rows = []
    for t in thresholds:
        n = int((pathogenic < t).sum())
        rows.append(
            {
                "locus": locus,
                "threshold": round(float(t), 4),
                "count": n,
                "n_pathogenic": len(pathogenic),
            }
        )
    return pd.DataFrame(rows)


def find_stability_zone(
    sweep_df: pd.DataFrame,
    locus: str,
    tolerance: float = STABILITY_TOLERANCE,
) -> tuple[float, float]:
    """Находит contiguous диапазон порогов где count меняется <= tolerance от count@0.95.

    Returns (zone_low, zone_high) — границы stability zone.
    """
    sub = sweep_df[sweep_df["locus"] == locus].sort_values("threshold").reset_index(drop=True)
    if sub.empty:
        return (THRESHOLD_NOMINAL, THRESHOLD_NOMINAL)

    # Count при номинальном пороге
    nominal_row = sub.iloc[(sub["threshold"] - THRESHOLD_NOMINAL).abs().argsort()[:1]]
    count_nominal = int(nominal_row["count"].values[0])

    if count_nominal == 0:
        return (THRESHOLD_NOMINAL, THRESHOLD_NOMINAL)

    # Маска: count в пределах ±tolerance от count_nominal
    lower_bound = count_nominal * (1 - tolerance)
    upper_bound = count_nominal * (1 + tolerance)
    stable_mask = (sub["count"] >= lower_bound) & (sub["count"] <= upper_bound)

    # Находим contiguous region вокруг THRESHOLD_NOMINAL
    # ПОЧЕМУ: ищем только непрерывный кусок вокруг 0.95, не любой stable island
    nominal_idx = int((sub["threshold"] - THRESHOLD_NOMINAL).abs().idxmin())

    # Расширяем влево
    left = nominal_idx
    while left > 0 and stable_mask.iloc[left - 1]:
        left -= 1

    # Расширяем вправо
    right = nominal_idx
    while right < len(sub) - 1 and stable_mask.iloc[right + 1]:
        right += 1

    zone_low = float(sub.iloc[left]["threshold"])
    zone_high = float(sub.iloc[right]["threshold"])
    return (zone_low, zone_high)


def run_threshold_sweep(
    atlases: dict[str, pd.DataFrame],
    thresholds: np.ndarray,
) -> pd.DataFrame:
    """Запускает sweep по всем 9 локусам, возвращает combined DataFrame."""
    parts = []
    for locus, df in atlases.items():
        part = threshold_sweep_locus(df, locus, thresholds)
        parts.append(part)
    result = pd.concat(parts, ignore_index=True)
    log.info("threshold_sweep_complete", loci=len(atlases), thresholds=len(thresholds))
    return result


# ── Analysis 3: LSSIM Perturbation ────────────────────────────────────────────


def lssim_perturbation(
    df: pd.DataFrame,
    threshold: float = THRESHOLD_NOMINAL,
    n_iterations: int = PERTURB_N,
    perturbation_fraction: float = 0.20,
    rng: np.random.Generator | None = None,
) -> dict[str, Any]:
    """Симулирует биологический шум enhancer occupancy через ±20% perturbation LSSIM.

    ПОЧЕМУ ±20% от (1-LSSIM): это адитивная погрешность в "расстоянии от 1".
    Если вариант LSSIM=0.9, то (1-LSSIM)=0.1, шум = Uniform(-0.02, +0.02).
    Это моделирует неопределённость в ChIP-seq / ATAC-seq сигнале.
    """
    if rng is None:
        rng = np.random.default_rng(RNG_SEED)

    pathogenic_lssim = df[df["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"].values
    n = len(pathogenic_lssim)

    if n == 0:
        log.warning("no_pathogenic_for_perturbation")
        return {"mean": 0.0, "ci_low": 0.0, "ci_high": 0.0, "counts": []}

    counts = np.empty(n_iterations, dtype=np.int32)
    for i in range(n_iterations):
        # noise ~ Uniform(-f*(1-LSSIM), +f*(1-LSSIM)) для каждого варианта
        delta = (1.0 - pathogenic_lssim) * perturbation_fraction
        noise = rng.uniform(-delta, delta)
        perturbed = pathogenic_lssim + noise
        # Clip к [0, 1] — LSSIM не может выйти за пределы
        perturbed = np.clip(perturbed, 0.0, 1.0)
        counts[i] = int((perturbed < threshold).sum())

    observed = int((pathogenic_lssim < threshold).sum())

    result = {
        "observed": observed,
        "mean": float(np.mean(counts)),
        "std": float(np.std(counts)),
        "ci_low": float(np.percentile(counts, 2.5)),
        "ci_high": float(np.percentile(counts, 97.5)),
        "n_pathogenic": n,
        "threshold": threshold,
        "n_iterations": n_iterations,
        "perturbation_fraction": perturbation_fraction,
        "counts": counts.tolist(),
    }
    log.info(
        "perturbation_complete",
        observed=observed,
        mean=f"{result['mean']:.2f}",
        ci=f"[{result['ci_low']:.1f}, {result['ci_high']:.1f}]",
        std=f"{result['std']:.2f}",
    )
    return result


# ── Figure ─────────────────────────────────────────────────────────────────────


def make_figure(
    bootstrap_result: dict[str, Any],
    sweep_df: pd.DataFrame,
    perturb_result: dict[str, Any],
    hbb_stability_zone: tuple[float, float],
    out_dir: Path,
) -> None:
    """3-панельная фигура: Panel A (bootstrap), B (sweep), C (perturbation)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        "EXP-004: Threshold Robustness — Bootstrap CI & Perturbation Analysis",
        fontsize=12,
        fontweight="bold",
        y=1.01,
    )

    # ── Panel A: Bootstrap distribution ──────────────────────────────────────
    ax = axes[0]
    counts_boot = np.array(bootstrap_result["counts"])
    observed = bootstrap_result["observed"]
    ci_low = bootstrap_result["ci_low"]
    ci_high = bootstrap_result["ci_high"]

    ax.hist(counts_boot, bins=20, color="#2196F3", alpha=0.7, edgecolor="white", linewidth=0.5)
    ax.axvline(
        observed, color="#E53935", linewidth=2.0, linestyle="-", label=f"Observed = {observed}"
    )
    ax.axvline(
        ci_low,
        color="#1565C0",
        linewidth=1.5,
        linestyle="--",
        label=f"95% CI [{ci_low:.1f}, {ci_high:.1f}]",
    )
    ax.axvline(ci_high, color="#1565C0", linewidth=1.5, linestyle="--")
    ax.set_xlabel("Pearl count (pathogenic, LSSIM < 0.95)", fontsize=9)
    ax.set_ylabel("Bootstrap frequency", fontsize=9)
    ax.set_title(
        f"A  Bootstrap CI (HBB, n={bootstrap_result['n_iterations']})", fontsize=10, loc="left"
    )
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ── Panel B: Threshold sweep ─────────────────────────────────────────────
    ax = axes[1]
    hbb_sweep = sweep_df[sweep_df["locus"] == "HBB"].sort_values("threshold")
    other_loci = [loc for loc in sweep_df["locus"].unique() if loc != "HBB"]

    # Normalise other loci to count at 0.95 для сравнения (relative scale)
    # ПОЧЕМУ: разные локусы имеют разное абсолютное число вариантов,
    # показываем HBB абсолютно, остальных — тонкими серыми линиями (нормализованными)
    for locus in other_loci:
        lsub = sweep_df[sweep_df["locus"] == locus].sort_values("threshold")
        nom_row = lsub.iloc[(lsub["threshold"] - THRESHOLD_NOMINAL).abs().argsort()[:1]]
        count_nom = nom_row["count"].values[0]
        if count_nom > 0:
            ax.plot(
                lsub["threshold"],
                lsub["count"]
                / count_nom
                * hbb_sweep["count"].iloc[
                    (hbb_sweep["threshold"] - THRESHOLD_NOMINAL).abs().argsort().iloc[0]
                ],
                color="grey",
                alpha=0.25,
                linewidth=0.8,
            )

    # Stability zone shading for HBB
    zone_low, zone_high = hbb_stability_zone
    ax.axvspan(
        zone_low,
        zone_high,
        color="#A5D6A7",
        alpha=0.35,
        label=f"Stability zone [{zone_low:.3f}, {zone_high:.3f}]",
    )
    ax.plot(hbb_sweep["threshold"], hbb_sweep["count"], color="#1B5E20", linewidth=2.0, label="HBB")
    ax.axvline(
        THRESHOLD_NOMINAL,
        color="#E53935",
        linewidth=1.5,
        linestyle="--",
        label=f"Nominal = {THRESHOLD_NOMINAL}",
    )

    ax.set_xlabel("LSSIM threshold", fontsize=9)
    ax.set_ylabel("Pearl count (pathogenic)", fontsize=9)
    ax.set_title("B  Threshold sweep (9 loci)", fontsize=10, loc="left")
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # ── Panel C: Perturbation distribution ───────────────────────────────────
    ax = axes[2]
    counts_pert = np.array(perturb_result["counts"])
    p_observed = perturb_result["observed"]
    p_ci_low = perturb_result["ci_low"]
    p_ci_high = perturb_result["ci_high"]
    p_mean = perturb_result["mean"]

    ax.hist(counts_pert, bins=20, color="#FF7043", alpha=0.7, edgecolor="white", linewidth=0.5)
    ax.axvline(
        p_observed, color="#BF360C", linewidth=2.0, linestyle="-", label=f"Observed = {p_observed}"
    )
    ax.axvline(p_mean, color="#FF5722", linewidth=1.5, linestyle=":", label=f"Mean = {p_mean:.1f}")
    ax.axvline(
        p_ci_low,
        color="#4E342E",
        linewidth=1.5,
        linestyle="--",
        label=f"95% CI [{p_ci_low:.1f}, {p_ci_high:.1f}]",
    )
    ax.axvline(p_ci_high, color="#4E342E", linewidth=1.5, linestyle="--")
    ax.set_xlabel("Pearl count under ±20% LSSIM perturbation", fontsize=9)
    ax.set_ylabel("Perturbation frequency", fontsize=9)
    ax.set_title(
        f"C  Enhancer occupancy perturbation (HBB, n={perturb_result['n_iterations']})",
        fontsize=10,
        loc="left",
    )
    ax.legend(fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()

    pdf_path = out_dir / "fig_threshold_robustness.pdf"
    png_path = out_dir / "fig_threshold_robustness.png"
    plt.savefig(pdf_path, bbox_inches="tight", dpi=150)
    plt.savefig(png_path, bbox_inches="tight", dpi=150)
    plt.close()
    log.info("figure_saved", pdf=str(pdf_path), png=str(png_path))


# ── Print summary ──────────────────────────────────────────────────────────────


def print_summary(
    bootstrap_result: dict[str, Any],
    perturb_result: dict[str, Any],
    hbb_stability_zone: tuple[float, float],
    sweep_df: pd.DataFrame,
) -> None:
    """Выводит структурированную сводку в stdout."""
    sep = "─" * 60

    print(f"\n{sep}")
    print("EXP-004: THRESHOLD ROBUSTNESS SUMMARY")
    print(sep)

    print("\n[Analysis 1] Bootstrap CI on Pearl Count (HBB, threshold=0.95)")
    print(f"  Observed pearls     : {bootstrap_result['observed']}")
    print(f"  Bootstrap mean      : {bootstrap_result['mean']:.2f}")
    print(f"  Bootstrap std       : {bootstrap_result['std']:.2f}")
    print(f"  95% CI : [{bootstrap_result['ci_low']:.1f}, {bootstrap_result['ci_high']:.1f}]")
    print(f"  N pathogenic sampled: {bootstrap_result['n_pathogenic']}")
    print(f"  N iterations        : {bootstrap_result['n_iterations']}")

    print("\n[Analysis 2] Threshold Sweep — Stability Zone (HBB)")
    zone_low, zone_high = hbb_stability_zone
    print(f"  Nominal threshold   : {THRESHOLD_NOMINAL}")
    print(f"  Stability zone      : [{zone_low:.3f}, {zone_high:.3f}]")
    print(f"  Zone width          : {zone_high - zone_low:.3f}")
    print(f"  Tolerance applied   : ±{STABILITY_TOLERANCE * 100:.0f}% of count@0.95")

    print("\n  Pearl count at key thresholds (HBB, pathogenic):")
    hbb_sweep = sweep_df[sweep_df["locus"] == "HBB"].sort_values("threshold")
    for t_check in [0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.99]:
        row = hbb_sweep.iloc[(hbb_sweep["threshold"] - t_check).abs().argsort()[:1]]
        print(f"    threshold={t_check:.3f}: count={int(row['count'].values[0])}")

    print("\n[Analysis 3] LSSIM Perturbation ±20% (HBB, threshold=0.95)")
    print(f"  Observed pearls     : {perturb_result['observed']}")
    print(f"  Mean under perturb  : {perturb_result['mean']:.2f}")
    print(f"  Std under perturb   : {perturb_result['std']:.2f}")
    print(
        f"  95% CI              : [{perturb_result['ci_low']:.1f}, {perturb_result['ci_high']:.1f}]"
    )
    print(f"  N iterations        : {perturb_result['n_iterations']}")
    print(
        f"  Perturbation size   : "
        f"±{perturb_result['perturbation_fraction'] * 100:.0f}% of (1-LSSIM)"
    )

    print(f"\n{sep}\n")


# ── Main ───────────────────────────────────────────────────────────────────────


def main() -> None:
    """Точка входа: запускает все три анализа EXP-004."""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(RNG_SEED)

    # ── Загрузка данных ───────────────────────────────────────────────────────
    log.info("loading_hbb_atlas")
    hbb_df = load_hbb()

    log.info("loading_all_atlases")
    atlases: dict[str, pd.DataFrame] = {}
    for locus, filename in ATLAS_FILES.items():
        df = load_atlas(locus, filename)
        if df is not None:
            atlases[locus] = df
    log.info("atlases_ready", n_loci=len(atlases))

    # ── Analysis 1: Bootstrap ─────────────────────────────────────────────────
    log.info("running_bootstrap_analysis")
    bootstrap_result = bootstrap_pearl_count(
        hbb_df,
        threshold=THRESHOLD_NOMINAL,
        n_iterations=BOOTSTRAP_N,
        rng=rng,
    )

    # ── Analysis 2: Threshold sweep ───────────────────────────────────────────
    log.info("running_threshold_sweep")
    thresholds = np.arange(0.88, 0.995, 0.005)
    sweep_df = run_threshold_sweep(atlases, thresholds)

    # Stability zone for HBB (primary locus)
    hbb_stability_zone = find_stability_zone(sweep_df, "HBB", tolerance=STABILITY_TOLERANCE)
    log.info("stability_zone_hbb", zone=hbb_stability_zone)

    # Stability zones for all loci (for JSON summary)
    stability_zones: dict[str, dict[str, float]] = {}
    for locus in atlases:
        zone = find_stability_zone(sweep_df, locus, tolerance=STABILITY_TOLERANCE)
        stability_zones[locus] = {
            "low": zone[0],
            "high": zone[1],
            "width": round(zone[1] - zone[0], 4),
        }

    # ── Analysis 3: LSSIM perturbation ────────────────────────────────────────
    log.info("running_perturbation_analysis")
    perturb_result = lssim_perturbation(
        hbb_df,
        threshold=THRESHOLD_NOMINAL,
        n_iterations=PERTURB_N,
        perturbation_fraction=0.20,
        rng=rng,
    )

    # ── Save outputs ──────────────────────────────────────────────────────────

    # CSV: threshold sweep
    sweep_csv_path = ANALYSIS_DIR / "threshold_robustness.csv"
    sweep_df.to_csv(sweep_csv_path, index=False)
    log.info("sweep_csv_saved", path=str(sweep_csv_path))

    # JSON: summary
    summary: dict[str, Any] = {
        "experiment": "EXP-004",
        "description": "Threshold Robustness with Bootstrap CI",
        "rng_seed": RNG_SEED,
        "analysis_1_bootstrap": {k: v for k, v in bootstrap_result.items() if k != "counts"},
        "analysis_2_threshold_sweep": {
            "thresholds_range": [float(thresholds[0]), float(thresholds[-1])],
            "threshold_step": 0.005,
            "n_loci": len(atlases),
            "loci": list(atlases.keys()),
            "stability_zones": stability_zones,
        },
        "analysis_3_perturbation": {k: v for k, v in perturb_result.items() if k != "counts"},
    }
    summary_path = ANALYSIS_DIR / "threshold_robustness_summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    log.info("summary_json_saved", path=str(summary_path))

    # Figure
    log.info("generating_figure")
    make_figure(
        bootstrap_result=bootstrap_result,
        sweep_df=sweep_df,
        perturb_result=perturb_result,
        hbb_stability_zone=hbb_stability_zone,
        out_dir=FIGURES_DIR,
    )

    # Print to stdout
    print_summary(bootstrap_result, perturb_result, hbb_stability_zone, sweep_df)


if __name__ == "__main__":
    main()
