"""
EXP-003: Tissue-Mismatch Negative Controls.

Для каждого локуса запускаем ARCHCODE-подобный анализ с НЕПРАВИЛЬНЫМИ
энхансерами (из другого локуса/ткани) и сравниваем ΔLSSIM P/LP vs B/LB
с корректным (matched) результатом.

Логика: если сигнал ARCHCODE тканеспецифичен — при замене энхансеров из
другой ткани различие P/LP vs B/LB должно исчезать (ΔLSSIM → 0).
"""

import json
import sys
from pathlib import Path
from typing import NamedTuple

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import structlog
from scipy.stats import mannwhitneyu

matplotlib.use("Agg")  # ПОЧЕМУ: headless-рендер без GUI на сервере/CI

# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Пути
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config" / "locus"
RESULTS_DIR = ROOT / "results"
ANALYSIS_DIR = ROOT / "analysis"
FIGURES_DIR = ANALYSIS_DIR  # фигуры кладём рядом с CSV в analysis/

ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Определения локусов
# ---------------------------------------------------------------------------


class LocusConfig(NamedTuple):
    """Описание локуса: конфиг + атлас."""

    name: str
    config_file: str
    atlas_file: str
    tissue: str


LOCI: list[LocusConfig] = [
    LocusConfig(
        name="HBB",
        config_file="hbb_95kb_subTAD.json",
        atlas_file="HBB_Unified_Atlas.csv",
        tissue="K562_erythroid",
    ),
    LocusConfig(
        name="LDLR",
        config_file="ldlr_300kb.json",
        atlas_file="LDLR_Unified_Atlas_300kb.csv",
        tissue="HepG2_hepatocyte",
    ),
    LocusConfig(
        name="TP53",
        config_file="tp53_300kb.json",
        atlas_file="TP53_Unified_Atlas_300kb.csv",
        tissue="K562_partial",
    ),
]


# ---------------------------------------------------------------------------
# Структуры данных
# ---------------------------------------------------------------------------


class Enhancer(NamedTuple):
    """Один энхансер: геномная позиция + сила связывания."""

    position: int
    occupancy: float
    name: str


class LocusData(NamedTuple):
    """Полный контекст локуса после загрузки."""

    name: str
    tissue: str
    win_start: int
    win_end: int
    enhancers: list[Enhancer]
    atlas: pd.DataFrame


# ---------------------------------------------------------------------------
# Загрузка данных
# ---------------------------------------------------------------------------


def load_locus(cfg: LocusConfig) -> LocusData:
    """Загружает конфиг JSON + атлас CSV для одного локуса.

    Возвращает LocusData с распарсенными энхансерами и DataFrame вариантов.
    """
    config_path = CONFIG_DIR / cfg.config_file
    atlas_path = RESULTS_DIR / cfg.atlas_file

    log.info("loading locus", locus=cfg.name, config=str(config_path))

    with config_path.open() as fh:
        config = json.load(fh)

    win = config["window"]
    raw_enhancers = config["features"]["enhancers"]

    enhancers = [
        Enhancer(
            position=int(e["position"]),
            occupancy=float(e["occupancy"]),
            name=e.get("name", f"enh_{i}"),
        )
        for i, e in enumerate(raw_enhancers)
    ]

    atlas = pd.read_csv(atlas_path, low_memory=False)
    # Убедимся, что колонка позиции числовая
    atlas["Position_GRCh38"] = pd.to_numeric(atlas["Position_GRCh38"], errors="coerce")
    atlas = atlas.dropna(subset=["Position_GRCh38"])
    atlas["Position_GRCh38"] = atlas["Position_GRCh38"].astype(int)

    log.info(
        "locus loaded",
        locus=cfg.name,
        n_enhancers=len(enhancers),
        n_variants=len(atlas),
        win_start=win["start"],
        win_end=win["end"],
    )

    return LocusData(
        name=cfg.name,
        tissue=cfg.tissue,
        win_start=int(win["start"]),
        win_end=int(win["end"]),
        enhancers=enhancers,
        atlas=atlas,
    )


# ---------------------------------------------------------------------------
# Перенос энхансеров в координатную систему целевого локуса
# ---------------------------------------------------------------------------


def remap_enhancers(
    source: LocusData,
    target: LocusData,
) -> list[Enhancer]:
    """Переносит энхансеры source-локуса в координаты target-локуса.

    Пропорциональное отображение: сохраняем относительное положение
    внутри окна, occupancy переносится без изменений.

    ПОЧЕМУ пропорциональное (а не просто сдвиг):
    Окна разных локусов имеют разный размер (95kb vs 300kb), поэтому
    простой сдвиг перенёс бы энхансеры за пределы целевого окна.
    Пропорциональное отображение сохраняет относительную «близость»
    к вариантам — именно это мы проверяем.
    """
    src_span = source.win_end - source.win_start
    tgt_span = target.win_end - target.win_start

    if src_span == 0:
        raise ValueError(f"Source locus {source.name} has zero-width window")

    remapped: list[Enhancer] = []
    for enh in source.enhancers:
        rel = (enh.position - source.win_start) / src_span
        new_pos = int(target.win_start + rel * tgt_span)
        remapped.append(
            Enhancer(
                position=new_pos,
                occupancy=enh.occupancy,
                name=f"{enh.name}@{source.name}->MISMATCH",
            )
        )

    log.debug(
        "enhancers remapped",
        source=source.name,
        target=target.name,
        n=len(remapped),
    )
    return remapped


# ---------------------------------------------------------------------------
# Proximity score
# ---------------------------------------------------------------------------

SIGMA_BP: float = 5_000.0  # ПОЧЕМУ 5kb: типичный радиус влияния дистального энхансера
# в контакте через петлю (Davidson 2019, Sabaté 2024)


def gaussian_proximity_score(
    variant_positions: np.ndarray,
    enhancers: list[Enhancer],
) -> np.ndarray:
    """Вычисляет близость каждого варианта к набору энхансеров.

    score_i = Σ_j  occupancy_j × exp(-0.5 × (d_ij / σ)²)

    Результат: вектор float размером len(variant_positions).

    ПОЧЕМУ гауссово ядро, а не просто расстояние:
    Влияние энхансера не обрывается резко — оно плавно убывает
    с расстоянием. Гауссово ядро моделирует вероятность физического
    контакта в пространстве. σ=5kb — консервативная оценка
    «радиуса действия» на основе Hi-C данных K562.
    """
    if not enhancers:
        return np.zeros(len(variant_positions))

    enh_pos = np.array([e.position for e in enhancers], dtype=float)
    enh_occ = np.array([e.occupancy for e in enhancers], dtype=float)

    # variant_positions: (N,) → (N,1); enh_pos: (M,) → (1,M)
    dist_matrix = np.abs(variant_positions[:, np.newaxis] - enh_pos[np.newaxis, :])
    weights = np.exp(-0.5 * (dist_matrix / SIGMA_BP) ** 2)  # (N, M)
    scores = (weights * enh_occ[np.newaxis, :]).sum(axis=1)  # (N,)
    return scores


# ---------------------------------------------------------------------------
# ΔLSSIM из атласа (matched baseline)
# ---------------------------------------------------------------------------


def compute_matched_delta(atlas: pd.DataFrame, locus_name: str) -> dict:
    """Считает ΔLSSIM между P/LP и B/LB из реальных данных атласа.

    ΔLSSIM = mean_benign_LSSIM - mean_pathogenic_LSSIM
    Положительное значение = корректное направление (B > P).
    """
    plp = atlas[atlas["Label"] == "Pathogenic"]["ARCHCODE_LSSIM"].dropna()
    blb = atlas[atlas["Label"] == "Benign"]["ARCHCODE_LSSIM"].dropna()

    if len(plp) < 2 or len(blb) < 2:
        log.warning("insufficient data for matched delta", locus=locus_name)
        return {
            "mean_plp": float("nan"),
            "mean_blb": float("nan"),
            "delta": float("nan"),
            "p_value": float("nan"),
            "n_plp": len(plp),
            "n_blb": len(blb),
        }

    stat, pval = mannwhitneyu(plp, blb, alternative="two-sided")
    delta = float(blb.mean() - plp.mean())

    log.info(
        "matched delta computed",
        locus=locus_name,
        mean_plp=round(float(plp.mean()), 6),
        mean_blb=round(float(blb.mean()), 6),
        delta=round(delta, 6),
        p_value=round(pval, 4),
        n_plp=len(plp),
        n_blb=len(blb),
    )
    return {
        "mean_plp": float(plp.mean()),
        "mean_blb": float(blb.mean()),
        "delta": delta,
        "p_value": float(pval),
        "n_plp": int(len(plp)),
        "n_blb": int(len(blb)),
    }


# ---------------------------------------------------------------------------
# Proximity-based ΔLSSIM (mismatched proxy)
# ---------------------------------------------------------------------------


def compute_mismatch_delta(
    target: LocusData,
    mismatch_enhancers: list[Enhancer],
    source_name: str,
) -> dict:
    """Вычисляет прокси-ΔLSSIM при замене энхансеров на чужие.

    Использует gaussian_proximity_score вместо реального ARCHCODE LSSIM.
    Если тканеспецифичность реальна — чужие энхансеры не дадут разницы
    между P и B вариантами (delta ≈ 0).
    """
    atlas = target.atlas.copy()
    positions = atlas["Position_GRCh38"].values.astype(float)
    scores = gaussian_proximity_score(positions, mismatch_enhancers)
    atlas["_prox_score"] = scores

    plp_scores = atlas[atlas["Label"] == "Pathogenic"]["_prox_score"].dropna()
    blb_scores = atlas[atlas["Label"] == "Benign"]["_prox_score"].dropna()

    if len(plp_scores) < 2 or len(blb_scores) < 2:
        log.warning(
            "insufficient data for mismatch delta",
            target=target.name,
            source=source_name,
        )
        return {
            "mean_plp": float("nan"),
            "mean_blb": float("nan"),
            "delta": float("nan"),
            "p_value": float("nan"),
            "n_plp": len(plp_scores),
            "n_blb": len(blb_scores),
        }

    stat, pval = mannwhitneyu(plp_scores, blb_scores, alternative="two-sided")
    delta = float(blb_scores.mean() - plp_scores.mean())

    log.info(
        "mismatch delta computed",
        target=target.name,
        source=source_name,
        mean_plp=round(float(plp_scores.mean()), 6),
        mean_blb=round(float(blb_scores.mean()), 6),
        delta=round(delta, 6),
        p_value=round(pval, 4),
    )
    return {
        "mean_plp": float(plp_scores.mean()),
        "mean_blb": float(blb_scores.mean()),
        "delta": delta,
        "p_value": float(pval),
        "n_plp": int(len(plp_scores)),
        "n_blb": int(len(blb_scores)),
    }


# ---------------------------------------------------------------------------
# Также считаем matched proxy для нормировки
# ---------------------------------------------------------------------------


def compute_matched_proxy(target: LocusData) -> dict:
    """Считает proximity score с СОБСТВЕННЫМИ энхансерами (matched контроль).

    ПОЧЕМУ нужен matched-proxy отдельно от ΔLSSIM:
    LSSIM — это полный SSIM на матрице Hi-C, а proximity-score —
    упрощённый прокси. Чтобы честно сравнивать matched vs mismatch,
    нужно вычислить proxy и для matched-случая на той же метрике.
    """
    return compute_mismatch_delta(
        target=target,
        mismatch_enhancers=target.enhancers,
        source_name=target.name,  # источник = сам локус
    )


# ---------------------------------------------------------------------------
# Визуализация
# ---------------------------------------------------------------------------


def plot_heatmap(
    pivot_df: pd.DataFrame,
    out_base: Path,
) -> None:
    """Рисует тепловую карту locus × enhancer_source → delta.

    Диагональ (matched) должна показывать сигнал, внедиагональные —
    близко к нулю. Используем дивергирующую цветовую шкалу.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 5.5))

    loci = pivot_df.index.tolist()
    sources = pivot_df.columns.tolist()

    # --- левая панель: proxy delta (все ячейки на одной метрике) ---
    data_proxy = pivot_df.values.astype(float)

    # Нормировка: максимум по диагонали чтобы показать контраст
    abs_max = max(np.nanmax(np.abs(data_proxy)), 1e-9)
    im1 = axes[0].imshow(
        data_proxy,
        cmap="RdBu",
        vmin=-abs_max,
        vmax=abs_max,
        aspect="auto",
    )
    axes[0].set_title("Proximity-proxy ΔLSSIM\n(B/LB mean – P/LP mean)", fontsize=13)
    axes[0].set_xticks(range(len(sources)))
    axes[0].set_xticklabels(sources, rotation=30, ha="right", fontsize=10)
    axes[0].set_yticks(range(len(loci)))
    axes[0].set_yticklabels(loci, fontsize=10)
    axes[0].set_xlabel("Enhancer source (tissue)", fontsize=10)
    axes[0].set_ylabel("Target locus", fontsize=10)
    plt.colorbar(im1, ax=axes[0], label="Δ score (B – P)")

    # Аннотируем ячейки
    for i in range(len(loci)):
        for j in range(len(sources)):
            val = data_proxy[i, j]
            text = f"{val:.4f}" if not np.isnan(val) else "NA"
            # ПОЧЕМУ выбираем цвет текста: тёмный фон → белый текст
            color = "white" if abs(val) > abs_max * 0.55 else "black"
            axes[0].text(
                j, i, text, ha="center", va="center", fontsize=9, color=color, fontweight="bold"
            )

    # Подсвечиваем диагональ рамкой
    for k in range(min(len(loci), len(sources))):
        # Найти индекс source совпадающий с locus
        try:
            j = sources.index(loci[k])
            rect = plt.Rectangle(
                (j - 0.5, k - 0.5), 1, 1, linewidth=2.5, edgecolor="gold", facecolor="none"
            )
            axes[0].add_patch(rect)
        except ValueError:
            pass

    # --- правая панель: bar-plot для наглядности ---
    ax = axes[1]
    x = np.arange(len(loci))
    width = 0.25
    colors_list = ["#2166ac", "#d6604d", "#4dac26"]

    for j, src in enumerate(sources):
        vals = [data_proxy[i, j] for i in range(len(loci))]
        ax.bar(
            x + j * width,
            vals,
            width,
            label=src,
            color=colors_list[j % len(colors_list)],
            alpha=0.85,
            edgecolor="black",
            linewidth=0.7,
        )

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x + width)
    ax.set_xticklabels(loci, fontsize=11)
    ax.set_xlabel("Target locus", fontsize=11)
    ax.set_ylabel("Proxy ΔLSSIM (B – P)", fontsize=11)
    ax.set_title(
        "Tissue-mismatch negative controls\nSignal should vanish for off-diagonal (wrong tissue)",
        fontsize=12,
    )
    ax.legend(title="Enhancer source", fontsize=9, title_fontsize=9)
    ax.grid(axis="y", alpha=0.35)

    # Добавляем общую легенду
    fig.text(
        0.5,
        0.01,
        "Gold border = matched tissue (correct). "
        "Off-diagonal = tissue mismatch (negative control).",
        ha="center",
        fontsize=10,
        style="italic",
    )

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    pdf_path = out_base.with_suffix(".pdf")
    png_path = out_base.with_suffix(".png")
    fig.savefig(pdf_path, bbox_inches="tight", dpi=150)
    fig.savefig(png_path, bbox_inches="tight", dpi=150)
    plt.close(fig)

    log.info("figure saved", pdf=str(pdf_path), png=str(png_path))


# ---------------------------------------------------------------------------
# Главная функция
# ---------------------------------------------------------------------------


def main() -> None:
    """Запускает EXP-003: Tissue-Mismatch Negative Controls."""
    log.info("EXP-003: Tissue-Mismatch Negative Controls — start")

    # 1. Загрузка локусов
    locus_data: dict[str, LocusData] = {}
    for cfg in LOCI:
        try:
            ld = load_locus(cfg)
            locus_data[ld.name] = ld
        except FileNotFoundError as exc:
            log.error("config or atlas not found", error=str(exc))
            sys.exit(1)

    locus_names = list(locus_data.keys())  # ["HBB", "LDLR", "TP53"]

    # 2. Matched baseline из реального LSSIM
    log.info("--- Computing matched LSSIM baseline (real atlas values) ---")
    matched_real: dict[str, dict] = {}
    for name, ld in locus_data.items():
        matched_real[name] = compute_matched_delta(ld.atlas, name)

    # 3. Proxy delta: каждый локус × каждый источник энхансеров
    # включая matched (собственные энхансеры) как positive control
    log.info("--- Computing proximity-proxy delta (all locus × enhancer combinations) ---")

    rows: list[dict] = []

    # Матрица для тепловой карты: locus × source → delta
    pivot: dict[str, dict[str, float]] = {name: {} for name in locus_names}

    for target_name in locus_names:
        target = locus_data[target_name]

        for source_name in locus_names:
            source = locus_data[source_name]

            if source_name == target_name:
                # matched: используем собственные энхансеры
                result = compute_matched_proxy(target)
                label = "MATCHED"
            else:
                # mismatch: переносим энхансеры из другого локуса
                remapped = remap_enhancers(source, target)
                result = compute_mismatch_delta(target, remapped, source_name)
                label = "MISMATCH"

            row = {
                "locus": target_name,
                "locus_tissue": target.tissue,
                "enhancer_source": source_name,
                "enhancer_source_tissue": source.tissue,
                "condition": label,
                "n_enhancers": len(source.enhancers),
                "mean_score_plp": result["mean_plp"],
                "mean_score_blb": result["mean_blb"],
                "delta": result["delta"],
                "p_value": result["p_value"],
                "n_plp": result["n_plp"],
                "n_blb": result["n_blb"],
            }
            rows.append(row)
            pivot[target_name][source_name] = result["delta"]

    # 4. Сохраняем CSV
    results_df = pd.DataFrame(rows)
    csv_path = ANALYSIS_DIR / "tissue_mismatch_controls.csv"
    results_df.to_csv(csv_path, index=False)
    log.info("CSV saved", path=str(csv_path), n_rows=len(results_df))

    # 5. Сохраняем summary JSON
    summary: dict = {
        "experiment": "EXP-003",
        "description": (
            "Tissue-mismatch negative controls: ARCHCODE proxy score with wrong-tissue enhancers"
        ),
        "n_loci": len(locus_names),
        "loci": locus_names,
        "sigma_bp": SIGMA_BP,
        "matched_real_lssim": matched_real,
        "proxy_results": {
            f"{r['locus']}|{r['enhancer_source']}": {
                "condition": r["condition"],
                "delta": r["delta"],
                "p_value": r["p_value"],
                "n_plp": r["n_plp"],
                "n_blb": r["n_blb"],
            }
            for r in rows
        },
        "interpretation": (
            "Diagonal (matched) cells should show positive delta "
            "(benign variants have higher proximity score than pathogenic). "
            "Off-diagonal (mismatch) cells should show delta near zero — "
            "confirming that the signal is tissue-specific, not positional artifact."
        ),
    }

    json_path = ANALYSIS_DIR / "tissue_mismatch_controls_summary.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    log.info("JSON summary saved", path=str(json_path))

    # 6. Печать читаемого отчёта
    print("\n" + "=" * 70)
    print("EXP-003: Tissue-Mismatch Negative Controls — RESULTS")
    print("=" * 70)

    print("\n[A] MATCHED BASELINE — real ARCHCODE_LSSIM from atlas")
    header = f"{'Locus':<8} {'Tissue':<22} {'mean_PLP':>10} {'mean_BLB':>10} {'ΔLSSIM':>10} {'p-value':>10}"
    print(header)
    print("-" * 72)
    for name in locus_names:
        r = matched_real[name]
        tissue = locus_data[name].tissue
        print(
            f"{name:<8} {tissue:<22} "
            f"{r['mean_plp']:>10.6f} {r['mean_blb']:>10.6f} "
            f"{r['delta']:>+10.6f} {r['p_value']:>10.4f}"
        )

    print("\n[B] PROXIMITY PROXY — matched vs mismatch (diagonal vs off-diagonal)")
    print(
        f"{'Target':<7} {'Source':<7} {'Condition':<10} "
        f"{'mean_P':>10} {'mean_B':>10} {'Δ':>10} {'p-value':>10}"
    )
    print("-" * 72)
    for r in sorted(rows, key=lambda x: (x["locus"], x["condition"] == "MISMATCH")):
        print(
            f"{r['locus']:<7} {r['enhancer_source']:<7} {r['condition']:<10} "
            f"{r['mean_score_plp']:>10.6f} {r['mean_score_blb']:>10.6f} "
            f"{r['delta']:>+10.6f} {r['p_value']:>10.4f}"
        )

    print("\n[C] TISSUE MISMATCH EFFECT — signal attenuation")
    print(
        "Expected: matched Δ >> mismatch Δ ≈ 0\n"
        "(off-diagonal should collapse if signal is tissue-specific)\n"
    )
    for target_name in locus_names:
        matched_delta = pivot[target_name][target_name]
        mismatch_deltas = [
            (src, pivot[target_name][src]) for src in locus_names if src != target_name
        ]
        mismatch_mean = np.mean([d for _, d in mismatch_deltas])
        ratio = (matched_delta / mismatch_mean) if abs(mismatch_mean) > 1e-12 else float("inf")
        print(
            f"  {target_name}: matched Δ = {matched_delta:+.6f} | "
            f"mismatch mean Δ = {mismatch_mean:+.6f} | "
            f"ratio = {ratio:.1f}x"
        )

    print("=" * 70 + "\n")

    # 7. Тепловая карта
    pivot_df = pd.DataFrame(pivot).T  # index=locus, columns=source
    # Порядок строк и колонок одинаковый
    pivot_df = pivot_df.reindex(index=locus_names, columns=locus_names)

    fig_base = ANALYSIS_DIR / "fig_tissue_mismatch"
    plot_heatmap(pivot_df, fig_base)

    log.info("EXP-003 complete", csv=str(csv_path), json=str(json_path))
    print("Output files:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  PDF:  {fig_base.with_suffix('.pdf')}")
    print(f"  PNG:  {fig_base.with_suffix('.png')}")


if __name__ == "__main__":
    main()
