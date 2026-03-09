#!/usr/bin/env python3
"""
Оверлей GWAS-хитов с предсказаниями ARCHCODE.

Для каждого GWAS SNP, попавшего в окно ARCHCODE-локуса:
1. Ищет ближайшую позицию в атласном CSV (или точное совпадение).
2. Присваивает интерпретацию: структурный механизм / кодирующий / неопределён.
3. Строит scatter-рисунок: -log10(p-value) vs ΔLSSIM с выделением жемчужин.

Использование:
    python scripts/gwas_archcode_overlay.py
    python scripts/gwas_archcode_overlay.py --gwas-file data/gwas/gwas_archcode_only.csv
    python scripts/gwas_archcode_overlay.py --max-distance 5000
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import structlog

# ПОЧЕМУ: Agg-бэкенд работает без GUI — важно для headless-среды Windows
matplotlib.use("Agg")

log = structlog.get_logger()

PROJECT = Path(__file__).parent.parent

# Маппинг локус → путь к атласному CSV
# ПОЧЕМУ: некоторые атласы называются по-разному (HBB — 95kb, остальные — 300/400kb).
# Здесь перечислены реальные файлы, проверённые в results/.
ATLAS_FILES: dict[str, Path] = {
    "HBB": PROJECT / "results" / "HBB_Unified_Atlas_95kb.csv",
    "BRCA1": PROJECT / "results" / "BRCA1_Unified_Atlas_400kb.csv",
    "TP53": PROJECT / "results" / "TP53_Unified_Atlas_300kb.csv",
    "TERT": PROJECT / "results" / "TERT_Unified_Atlas_300kb.csv",
    "MLH1": PROJECT / "results" / "MLH1_Unified_Atlas_300kb.csv",
    "CFTR": PROJECT / "results" / "CFTR_Unified_Atlas_317kb.csv",
    "SCN5A": PROJECT / "results" / "SCN5A_Unified_Atlas_400kb.csv",
    "GJB2": PROJECT / "results" / "GJB2_Unified_Atlas_300kb.csv",
    "LDLR": PROJECT / "results" / "LDLR_Unified_Atlas_300kb.csv",
}

# Стандартные цвета ARCHCODE (синяя/красная палитра из существующих рисунков)
COLOR_INTERGENIC = "#c0392b"  # красный — интергенные (структурный механизм возможен)
COLOR_GENIC = "#2980b9"  # синий — генные (кодирующий механизм вероятнее)
COLOR_PEARL = "#f39c12"  # оранжевый — жемчужины (LSSIM < порога в атласе)
COLOR_NEEDS_SIM = "#95a5a6"  # серый — нет данных в атласе


def load_gwas(path: Path) -> pd.DataFrame:
    """Загружает GWAS CSV и базово валидирует колонки."""
    if not path.exists():
        raise FileNotFoundError(f"GWAS file not found: {path}\nRun download_gwas_catalog.py first.")

    df = pd.read_csv(path, low_memory=False)

    required = {"rsID", "Chromosome", "Position_GRCh38", "P_Value", "ARCHCODE_Locus"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"GWAS CSV missing columns: {missing}")

    # Приводим типы
    df["Position_GRCh38"] = pd.to_numeric(df["Position_GRCh38"], errors="coerce")
    df["P_Value"] = pd.to_numeric(df["P_Value"], errors="coerce")
    df["Is_Intergenic"] = (
        df["Is_Intergenic"]
        .astype(str)
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False})
        .fillna(False)
    )

    log.info("GWAS data loaded", rows=len(df), loci=df["ARCHCODE_Locus"].unique().tolist())
    return df


def load_atlas(locus: str) -> pd.DataFrame | None:
    """
    Загружает атласный CSV для локуса.

    Возвращает None если файл не найден (некоторые локусы могут отсутствовать).
    """
    path = ATLAS_FILES.get(locus)
    if path is None or not path.exists():
        log.warning("Atlas file not found", locus=locus, expected_path=str(path))
        return None

    df = pd.read_csv(path, low_memory=False)
    df["Position_GRCh38"] = pd.to_numeric(df["Position_GRCh38"], errors="coerce")

    # ПОЧЕМУ: LSSIM — ключевая метрика ARCHCODE (Local Structural Similarity Index).
    # Значения < 0.95 → "жемчужина" (потенциально патогенный структурный эффект).
    if "ARCHCODE_LSSIM" not in df.columns:
        log.warning("Atlas has no ARCHCODE_LSSIM column", locus=locus, cols=list(df.columns))
        return None

    df["ARCHCODE_LSSIM"] = pd.to_numeric(df["ARCHCODE_LSSIM"], errors="coerce")
    log.info("Atlas loaded", locus=locus, rows=len(df))
    return df


def find_nearest_atlas_position(
    snp_pos: int,
    atlas_df: pd.DataFrame,
    max_distance: int,
) -> dict[str, Any] | None:
    """
    Ищет запись в атласе, ближайшую к позиции SNP.

    Возвращает словарь с LSSIM и метаданными или None если дистанция > max_distance.
    Предпочитает точное совпадение перед ближайшим.
    """
    if atlas_df is None or atlas_df.empty:
        return None

    positions = atlas_df["Position_GRCh38"].dropna()
    if positions.empty:
        return None

    # ПОЧЕМУ: ищем точное совпадение сначала — GWAS-позиции из GRCh38
    # теоретически должны матчиться с атласными (оба GRCh38), но на практике
    # позиция SNP может попасть между симулированными позициями.
    exact_mask = atlas_df["Position_GRCh38"] == snp_pos
    if exact_mask.any():
        row = atlas_df[exact_mask].iloc[0]
        return {
            "atlas_position": int(snp_pos),
            "distance": 0,
            "ARCHCODE_LSSIM": (
                float(row["ARCHCODE_LSSIM"]) if pd.notna(row["ARCHCODE_LSSIM"]) else None
            ),
            "ARCHCODE_Category": str(row.get("Category", "")),
            "Pearl": str(row.get("Pearl", "false")).lower() == "true",
            "ClinVar_Significance": str(row.get("ClinVar_Significance", "")),
            "match_type": "exact",
        }

    # Ближайшая позиция
    distances = (positions - snp_pos).abs()
    min_idx = distances.idxmin()
    min_dist = int(distances[min_idx])

    if min_dist > max_distance:
        return None

    row = atlas_df.loc[min_idx]
    return {
        "atlas_position": int(row["Position_GRCh38"]),
        "distance": min_dist,
        "ARCHCODE_LSSIM": float(row["ARCHCODE_LSSIM"]) if pd.notna(row["ARCHCODE_LSSIM"]) else None,
        "ARCHCODE_Category": str(row.get("Category", "")),
        "Pearl": str(row.get("Pearl", "false")).lower() == "true",
        "ClinVar_Significance": str(row.get("ClinVar_Significance", "")),
        "match_type": "nearest",
    }


def interpret(
    lssim: float | None,
    is_intergenic: bool,
    is_pearl: bool,
    distance: int,
) -> str:
    """
    Присваивает текстовую интерпретацию GWAS-хиту на основе ARCHCODE-данных.

    Логика интерпретации отражает центральную гипотезу ARCHCODE:
    интергенные хиты с низким LSSIM → структурный механизм объясняет GWAS-сигнал.
    """
    if lssim is None:
        return "Needs simulation — position not in atlas"

    delta_lssim = 1.0 - lssim  # ΔLSSIM: 0 = нет эффекта, >0 = структурное нарушение

    if not is_intergenic:
        return "Likely sequence-level mechanism — coding/splicing region"

    # Интергенный SNP
    if lssim < 0.95:
        if is_pearl:
            return "GWAS hit explained by structural disruption (pearl)"
        return "GWAS hit explained by structural disruption"

    if lssim > 0.99:
        return "Structural mechanism unlikely — LSSIM near WT"

    # Серая зона 0.95–0.99
    return f"Ambiguous — ΔLSSIM={delta_lssim:.4f}, intergenic, needs experimental follow-up"


def build_overlay_table(
    gwas_df: pd.DataFrame,
    max_distance: int,
) -> pd.DataFrame:
    """
    Строит таблицу оверлея: каждый GWAS SNP обогащается данными ARCHCODE.

    Атласы кешируются — не перезагружаем для каждого SNP.
    """
    # ПОЧЕМУ: кеш атласов в памяти — загрузка 9 CSV один раз экономит I/O.
    atlas_cache: dict[str, pd.DataFrame | None] = {}

    rows: list[dict[str, Any]] = []

    for _, snp in gwas_df.iterrows():
        locus = str(snp.get("ARCHCODE_Locus", ""))
        pos_raw = snp.get("Position_GRCh38")
        pos: int | None = int(pos_raw) if pd.notna(pos_raw) else None
        p_val = snp.get("P_Value")
        is_intergenic = bool(snp.get("Is_Intergenic", False))

        # Загружаем атлас с кешем
        if locus not in atlas_cache:
            atlas_cache[locus] = load_atlas(locus)
        atlas_df = atlas_cache[locus]

        # Ищем совпадение в атласе
        atlas_hit: dict[str, Any] | None = None
        if pos is not None and atlas_df is not None:
            atlas_hit = find_nearest_atlas_position(pos, atlas_df, max_distance)

        lssim = atlas_hit["ARCHCODE_LSSIM"] if atlas_hit else None
        is_pearl = atlas_hit["Pearl"] if atlas_hit else False
        distance = atlas_hit["distance"] if atlas_hit else None
        category = atlas_hit["ARCHCODE_Category"] if atlas_hit else ""
        match_type = atlas_hit["match_type"] if atlas_hit else "not_found"

        neg_log10_p: float | None = None
        if p_val is not None and p_val > 0:
            neg_log10_p = -np.log10(float(p_val))

        delta_lssim = (1.0 - lssim) if lssim is not None else None

        interpretation = interpret(lssim, is_intergenic, is_pearl, distance or 0)

        rows.append(
            {
                "rsID": snp.get("rsID", ""),
                "Chromosome": snp.get("Chromosome", ""),
                "Position_GRCh38": pos,
                "GWAS_P_Value": p_val,
                "Neg_Log10_P": neg_log10_p,
                "Effect_Size": snp.get("Effect_Size", ""),
                "Mapped_Gene": snp.get("Mapped_Gene", ""),
                "Trait": snp.get("Trait", ""),
                "Is_Intergenic": is_intergenic,
                "ARCHCODE_Locus": locus,
                "ARCHCODE_LSSIM": lssim,
                "ARCHCODE_Delta_LSSIM": delta_lssim,
                "ARCHCODE_Category": category,
                "Is_Pearl": is_pearl,
                "Atlas_Match_Type": match_type,
                "Atlas_Distance_bp": distance,
                "Interpretation": interpretation,
            }
        )

    return pd.DataFrame(rows)


def build_summary_json(overlay_df: pd.DataFrame) -> dict[str, Any]:
    """Формирует JSON-сводку по оверлею."""
    total = len(overlay_df)

    # ПОЧЕМУ: пустой DataFrame из build_overlay_table не имеет колонок —
    # защищаемся явной проверкой, чтобы pipeline не падал на dry-run / нет данных.
    if overlay_df.empty or "ARCHCODE_LSSIM" not in overlay_df.columns:
        return {
            "total_gwas_snps": 0,
            "matched_in_atlas": 0,
            "needs_simulation": 0,
            "interpretation_breakdown": {
                "structural_disruption": 0,
                "coding_sequence_level": 0,
                "structural_unlikely": 0,
                "ambiguous": 0,
            },
            "gwas_hits_overlapping_pearls": 0,
            "by_locus": {},
            "key_finding": "No GWAS SNPs in ARCHCODE windows — run download_gwas_catalog.py first.",
        }

    in_atlas = overlay_df["ARCHCODE_LSSIM"].notna().sum()
    needs_sim = (overlay_df["Atlas_Match_Type"] == "not_found").sum()

    structural = overlay_df["Interpretation"].str.contains("structural disruption", na=False).sum()
    coding = overlay_df["Interpretation"].str.contains("sequence-level", na=False).sum()
    unlikely = overlay_df["Interpretation"].str.contains("unlikely", na=False).sum()
    ambiguous = overlay_df["Interpretation"].str.contains("Ambiguous", na=False).sum()
    pearls_hit = overlay_df["Is_Pearl"].sum()

    by_locus = overlay_df.groupby("ARCHCODE_Locus")["rsID"].count().to_dict()

    return {
        "total_gwas_snps": int(total),
        "matched_in_atlas": int(in_atlas),
        "needs_simulation": int(needs_sim),
        "interpretation_breakdown": {
            "structural_disruption": int(structural),
            "coding_sequence_level": int(coding),
            "structural_unlikely": int(unlikely),
            "ambiguous": int(ambiguous),
        },
        "gwas_hits_overlapping_pearls": int(pearls_hit),
        "by_locus": {str(k): int(v) for k, v in by_locus.items()},
        "key_finding": (
            f"{structural}/{total} intergenic GWAS hits have ARCHCODE LSSIM < 0.95, "
            "suggesting structural mechanism for GWAS signal."
        ),
    }


def print_key_findings(overlay_df: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Выводит ключевые находки в консоль."""
    print("\n" + "=" * 60)
    print("GWAS × ARCHCODE OVERLAY — Key Findings")
    print("=" * 60)
    print(f"Total GWAS SNPs analysed:       {summary['total_gwas_snps']}")
    print(f"Matched in ARCHCODE atlas:       {summary['matched_in_atlas']}")
    print(f"Needs simulation (no match):     {summary['needs_simulation']}")
    print()
    print("Interpretation breakdown:")
    bd = summary["interpretation_breakdown"]
    print(f"  Structural disruption:         {bd['structural_disruption']}")
    print(f"  Coding/sequence-level:         {bd['coding_sequence_level']}")
    print(f"  Structural unlikely:           {bd['structural_unlikely']}")
    print(f"  Ambiguous (0.95–0.99):         {bd['ambiguous']}")
    print(f"\nGWAS hits on ARCHCODE pearls:   {summary['gwas_hits_overlapping_pearls']}")
    print()
    print("By locus:", summary["by_locus"])
    print()

    # Показываем самые значимые структурные хиты
    if overlay_df.empty or "Interpretation" not in overlay_df.columns:
        print("=" * 60)
        return

    structural_mask = overlay_df["Interpretation"].str.contains("structural disruption", na=False)
    structural_hits = overlay_df[structural_mask].sort_values("Neg_Log10_P", ascending=False)
    if not structural_hits.empty:
        print("Top structural disruption hits:")
        for _, row in structural_hits.head(5).iterrows():
            lssim_str = f"{row['ARCHCODE_LSSIM']:.4f}" if pd.notna(row["ARCHCODE_LSSIM"]) else "N/A"
            logp_str = f"{row['Neg_Log10_P']:.1f}" if pd.notna(row["Neg_Log10_P"]) else "N/A"
            print(
                f"  {str(row['rsID']):15s}  {str(row['ARCHCODE_Locus']):6s}  "
                f"LSSIM={lssim_str}  "
                f"-log10p={logp_str}  "
                f"{row['Trait']}"
            )

    print("=" * 60)


def make_overlay_figure(
    overlay_df: pd.DataFrame,
    out_pdf: Path,
    out_png: Path,
) -> None:
    """
    Строит scatter-рисунок: -log10(p-value) vs ΔLSSIM.

    Цвет: интергенные (красный) / генные (синий) / жемчужины (оранжевый).
    Аналог Manhattan-стиля, но по оси X — структурный эффект ARCHCODE.
    """
    # ПОЧЕМУ: пустой DataFrame не имеет колонок — проверяем до dropna,
    # иначе KeyError на отсутствующих колонках вместо понятного warning.
    required_cols = {"Neg_Log10_P", "ARCHCODE_Delta_LSSIM"}
    if overlay_df.empty or not required_cols.issubset(overlay_df.columns):
        log.warning("No data to plot — overlay table is empty or missing required columns")
        return

    df = overlay_df.dropna(subset=["Neg_Log10_P", "ARCHCODE_Delta_LSSIM"])

    if df.empty:
        log.warning("No data to plot — all SNPs lack LSSIM or p-value")
        return

    fig, ax = plt.subplots(figsize=(9, 6))

    # Разделяем по категориям для управления порядком слоёв
    mask_pearl = df["Is_Pearl"]
    mask_intergenic = df["Is_Intergenic"] & ~mask_pearl
    mask_genic = ~df["Is_Intergenic"] & ~mask_pearl

    def scatter_group(mask: pd.Series, color: str, label: str, zorder: int, alpha: float) -> None:
        sub = df[mask]
        if sub.empty:
            return
        ax.scatter(
            sub["ARCHCODE_Delta_LSSIM"],
            sub["Neg_Log10_P"],
            c=color,
            s=40,
            alpha=alpha,
            linewidths=0,
            label=f"{label} (n={len(sub)})",
            zorder=zorder,
        )

    scatter_group(mask_genic, COLOR_GENIC, "Genic", zorder=2, alpha=0.55)
    scatter_group(mask_intergenic, COLOR_INTERGENIC, "Intergenic", zorder=3, alpha=0.65)
    scatter_group(mask_pearl, COLOR_PEARL, "Pearl (ARCHCODE)", zorder=4, alpha=0.9)

    # Аннотация ключевых жемчужин
    pearl_subset = df[mask_pearl].nlargest(5, "Neg_Log10_P")
    for _, row in pearl_subset.iterrows():
        ax.annotate(
            row["rsID"],
            xy=(row["ARCHCODE_Delta_LSSIM"], row["Neg_Log10_P"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=7,
            color=COLOR_PEARL,
        )

    # ПОЧЕМУ: горизонтальная линия p=5e-8 (стандартный GWAS-порог)
    # и вертикальная ΔLSSIM=0.05 (граница ощутимого структурного эффекта).
    ax.axhline(
        -np.log10(5e-8),
        color="gray",
        linestyle="--",
        linewidth=0.8,
        alpha=0.6,
        label="GWAS threshold (p=5e-8)",
    )
    ax.axvline(
        0.05, color="darkgray", linestyle=":", linewidth=0.8, alpha=0.6, label="ΔLSSIM = 0.05"
    )

    ax.set_xlabel("ΔLSSIM (1 − LSSIM) — structural disruption", fontsize=11)
    ax.set_ylabel("−log₁₀(GWAS p-value)", fontsize=11)
    ax.set_title("GWAS Hematological Hits × ARCHCODE Structural Predictions", fontsize=12)
    ax.legend(fontsize=8, framealpha=0.8, loc="upper left")

    # Добавляем аннотацию локусов если есть жемчужины
    for locus_name, group in df[mask_pearl].groupby("ARCHCODE_Locus"):
        top = group.nlargest(1, "Neg_Log10_P").iloc[0]
        ax.text(
            top["ARCHCODE_Delta_LSSIM"],
            top["Neg_Log10_P"] + 0.3,
            locus_name,
            fontsize=6,
            color="gray",
            ha="center",
        )

    plt.tight_layout()

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_pdf), dpi=150, bbox_inches="tight")
    fig.savefig(str(out_png), dpi=150, bbox_inches="tight")
    plt.close(fig)

    log.info("Figure saved", pdf=str(out_pdf), png=str(out_png))


def main() -> int:
    """Основной поток выполнения."""
    parser = argparse.ArgumentParser(
        description="Overlay GWAS hematological hits with ARCHCODE structural predictions"
    )
    parser.add_argument(
        "--gwas-file",
        type=Path,
        default=PROJECT / "data" / "gwas" / "gwas_hematological_hits.csv",
        help="Путь к GWAS CSV (из download_gwas_catalog.py)",
    )
    parser.add_argument(
        "--max-distance",
        type=int,
        default=2000,
        help="Максимальная дистанция bp до ближайшей атласной позиции (default: 2000)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT / "analysis",
        help="Директория для CSV и JSON выходных файлов",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=PROJECT / "figures",
        help="Директория для рисунков",
    )
    args = parser.parse_args()

    # --- Загрузка данных ---
    try:
        gwas_df = load_gwas(args.gwas_file)
    except FileNotFoundError as e:
        log.error("Cannot load GWAS data", error=str(e))
        return 1
    except ValueError as e:
        log.error("Invalid GWAS data format", error=str(e))
        return 1

    # Фильтруем только SNPs с присвоенным ARCHCODE-локусом
    in_windows = gwas_df[
        gwas_df["ARCHCODE_Locus"].notna() & (gwas_df["ARCHCODE_Locus"] != "")
    ].copy()

    log.info("SNPs in ARCHCODE windows", count=len(in_windows))

    if in_windows.empty:
        log.warning(
            "No GWAS SNPs in ARCHCODE windows — overlay table will be empty. "
            "Check download_gwas_catalog.py output."
        )
        # ПОЧЕМУ: не падаем — создаём пустые выходные файлы,
        # чтобы следующий шаг пайплайна мог работать.

    # --- Построение оверлея ---
    log.info("Building overlay table", max_distance_bp=args.max_distance)
    overlay_df = build_overlay_table(in_windows, max_distance=args.max_distance)

    # --- Сохранение CSV ---
    args.output_dir.mkdir(parents=True, exist_ok=True)
    overlay_csv = args.output_dir / "gwas_archcode_overlay.csv"
    overlay_df.to_csv(overlay_csv, index=False)
    log.info("Overlay CSV saved", path=str(overlay_csv), rows=len(overlay_df))

    # --- Сохранение JSON-сводки ---
    summary = build_summary_json(overlay_df)
    summary_json = args.output_dir / "gwas_archcode_summary.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log.info("Summary JSON saved", path=str(summary_json))

    # --- Вывод в консоль ---
    print_key_findings(overlay_df, summary)

    # --- Рисунок ---
    make_overlay_figure(
        overlay_df=overlay_df,
        out_pdf=args.figures_dir / "fig_gwas_overlay.pdf",
        out_png=args.figures_dir / "fig_gwas_overlay.png",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
