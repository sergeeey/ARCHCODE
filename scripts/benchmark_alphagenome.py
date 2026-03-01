#!/usr/bin/env python3
"""
ARCHCODE vs AlphaGenome benchmark: compare contact map predictions.

ПОЧЕМУ этот скрипт:
AlphaGenome (DeepMind) предсказывает 3D chromatin contact maps из ДНК последовательности.
ARCHCODE строит contact maps из mean-field loop extrusion модели.
Прямое сравнение обоих подходов с Hi-C ground truth показывает,
насколько наша аналитическая модель приближается к DL-модели.

Usage:
    python scripts/benchmark_alphagenome.py --locus 30kb
    python scripts/benchmark_alphagenome.py --locus ldlr --cell-line HepG2
    python scripts/benchmark_alphagenome.py --locus 30kb --api-key YOUR_KEY
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# ПОЧЕМУ lazy imports: alphagenome SDK тяжёлый, не хотим ломать --help
# если SDK не установлен
PROJECT_ROOT = Path(__file__).parent.parent


def get_api_key(args: argparse.Namespace) -> str:
    """Resolve API key from args, env, or .env file."""
    if args.api_key:
        return args.api_key

    env_key = os.environ.get("ALPHAGENOME_API_KEY")
    if env_key:
        return env_key

    if args.api_key_file:
        p = Path(args.api_key_file)
        if p.exists():
            for line in p.read_text().splitlines():
                if line.startswith("ALPHAGENOME_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

    # Try project .env
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ALPHAGENOME_API_KEY=") and "=" in line:
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val

    print("ERROR: No API key found.")
    print("  Provide via: --api-key KEY, ALPHAGENOME_API_KEY env var, or --api-key-file .env")
    print("  Get your key at: https://deepmind.google.com/science/alphagenome")
    sys.exit(1)


def load_locus_config(locus: str) -> dict:
    """Load locus config using the standard ARCHCODE loader."""
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from lib.locus_config import resolve_locus_path, load_locus_config as _load
    path = resolve_locus_path(locus)
    return _load(path)


def get_archcode_matrix(locus: str, config: dict) -> np.ndarray:
    """Build ARCHCODE wild-type contact matrix using the analytical engine."""
    # ПОЧЕМУ Python port: TypeScript engine — основной, но для бенчмарка
    # нам нужен Python для прямого сравнения с AlphaGenome output.
    # Используем тот же аналитический движок что и в TDA скрипте.
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from tda_proof_of_concept import build_contact_matrix, load_locus_config as tda_load

    tda_config = tda_load(locus)
    matrix = build_contact_matrix(tda_config, variant_bin=-1)
    return matrix


def predict_contact_map(
    api_key: str,
    chromosome: str,
    start: int,
    end: int,
    cell_line: str = "GM12878",
) -> tuple[np.ndarray, int, dict]:
    """
    Get AlphaGenome contact map prediction for a genomic interval.

    ПОЧЕМУ ontology_terms=None: AlphaGenome возвращает 0 tracks для UBERON terms
    (bone marrow и т.п.). Реальные данные — это cell lines из 4DN, индексируемые
    через EFO/CLO ontology. Запрашиваем все 28 tracks, потом выбираем нужный
    по имени cell line (GM12878, HepG2, etc.).

    Returns (contact_matrix_2d, resolution_bp, track_metadata).
    """
    from alphagenome.models import dna_client
    from alphagenome.models.dna_output import OutputType
    from alphagenome.data import genome

    print(f"  Creating AlphaGenome client...")
    model = dna_client.create(api_key)

    # ПОЧЕМУ resize: AlphaGenome требует фиксированные длины последовательности
    # (16kb, 100kb, 500kb, 1Mb). Берём ближайшую >= нашему окну.
    window_size = end - start
    center = (start + end) // 2

    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    seq_length = None
    for sl in supported:
        if sl >= window_size:
            seq_length = sl
            break
    if seq_length is None:
        seq_length = supported[-1]  # 1Mb

    print(f"  Window: {chromosome}:{start}-{end} ({window_size} bp)")
    print(f"  AlphaGenome sequence length: {seq_length} bp")

    # ПОЧЕМУ center-based interval: AlphaGenome хочет interval определённой длины,
    # мы центрируем его на нашем окне
    interval = genome.Interval(chromosome, center - seq_length // 2, center + seq_length // 2)
    print(f"  Interval: {interval}")

    print(f"  Requesting CONTACT_MAPS prediction (all cell lines)...")
    output = model.predict_interval(
        interval=interval,
        requested_outputs=[OutputType.CONTACT_MAPS],
        ontology_terms=None,
    )

    contact_data = output.contact_maps
    if contact_data is None:
        raise RuntimeError("AlphaGenome returned no contact map data")

    print(f"  Contact map shape: {contact_data.values.shape}")
    print(f"  Resolution: {contact_data.resolution} bp")

    n_tracks = contact_data.values.shape[2]
    meta_df = contact_data.metadata
    print(f"  Available cell lines ({n_tracks}):")
    for i, row in meta_df.iterrows():
        marker = " <<<" if row["biosample_name"] == cell_line else ""
        print(f"    [{i:2d}] {row['biosample_name']:12s} ({row['Assay title']}, {row['ontology_curie']}){marker}")

    # ПОЧЕМУ поиск по biosample_name: metadata DataFrame содержит столбец
    # biosample_name с именами cell lines (GM12878, HepG2, HFFc6, etc.)
    matches = meta_df[meta_df["biosample_name"] == cell_line]
    if matches.empty:
        available = sorted(meta_df["biosample_name"].unique())
        raise RuntimeError(
            f"Cell line '{cell_line}' not found in AlphaGenome predictions. "
            f"Available: {available}"
        )

    track_idx = matches.index[0]
    track_meta = matches.iloc[0].to_dict()
    print(f"  Selected track [{track_idx}]: {cell_line} ({track_meta['Assay title']})")

    # Extract single 2D matrix for the selected cell line
    matrix_2d = contact_data.values[:, :, track_idx]
    print(f"  2D matrix shape: {matrix_2d.shape}")

    return matrix_2d, contact_data.resolution, track_meta


def extract_window(
    full_matrix: np.ndarray,
    full_interval_start: int,
    resolution: int,
    window_start: int,
    window_end: int,
) -> np.ndarray:
    """Extract our window region from the full AlphaGenome contact matrix (2D)."""
    bin_start = (window_start - full_interval_start) // resolution
    bin_end = (window_end - full_interval_start) // resolution

    bin_start = max(0, bin_start)
    bin_end = min(full_matrix.shape[0], bin_end)

    print(f"  Extracting bins {bin_start}:{bin_end} from {full_matrix.shape[0]} total bins")
    return full_matrix[bin_start:bin_end, bin_start:bin_end]


def resample_matrix(matrix: np.ndarray, target_size: int) -> np.ndarray:
    """
    Resample a contact matrix to target_size x target_size.

    ПОЧЕМУ resample: AlphaGenome и ARCHCODE могут иметь разные разрешения.
    AlphaGenome может давать 128bp, а наш HBB 30kb config — 600bp (50 bins).
    Нужно привести к одному размеру для корреляции.
    """
    from scipy.ndimage import zoom

    if matrix.shape[0] == target_size:
        return matrix

    factor = target_size / matrix.shape[0]
    resampled = zoom(matrix, factor, order=1)  # bilinear interpolation
    return resampled[:target_size, :target_size]  # trim rounding artifacts


def distance_normalize(matrix: np.ndarray) -> np.ndarray:
    """
    Compute Observed/Expected ratio per genomic distance stratum.

    ПОЧЕМУ: AlphaGenome возвращает distance-normalized (O/E) values.
    Для корректного сравнения нужно привести ARCHCODE и Hi-C к тому же формату.
    Каждая диагональ матрицы = фиксированная геномная дистанция.
    O/E = value / mean(values at this distance).
    """
    n = matrix.shape[0]
    result = np.zeros_like(matrix, dtype=float)
    for d in range(n):
        diag_vals = np.array([matrix[i, i + d] for i in range(n - d)])
        mean_d = diag_vals.mean()
        if mean_d > 1e-12:
            for i in range(n - d):
                result[i, i + d] = matrix[i, i + d] / mean_d
                result[i + d, i] = result[i, i + d]
        else:
            for i in range(n - d):
                result[i, i + d] = 1.0
                result[i + d, i] = 1.0
    return result


def correlate_matrices(
    archcode: np.ndarray,
    alphagenome: np.ndarray,
    hic: np.ndarray | None = None,
) -> dict:
    """
    Compute Pearson and Spearman correlations between matrix pairs.

    ПОЧЕМУ два типа корреляции:
    - Pearson: линейная связь, чувствителен к масштабу
    - Spearman: ранговая, устойчива к нелинейным трансформациям (log, exp)
    """
    from scipy.stats import pearsonr, spearmanr

    results = {}

    # ПОЧЕМУ k=2: исключаем главную диагональ (d=0, self-contact) и
    # ближайших соседей (d=1, артефакт resolution). Для distance-normalized
    # данных короткие дистанции наименее информативны.
    def upper_triangle(m: np.ndarray) -> np.ndarray:
        return m[np.triu_indices_from(m, k=2)]

    arch_flat = upper_triangle(archcode)
    ag_flat = upper_triangle(alphagenome)

    mask = np.isfinite(arch_flat) & np.isfinite(ag_flat)
    if mask.sum() < 10:
        print("  WARNING: too few valid pairs for correlation")
        return {"error": "insufficient valid pairs"}

    r, p = pearsonr(arch_flat[mask], ag_flat[mask])
    rho, p_s = spearmanr(arch_flat[mask], ag_flat[mask])
    results["archcode_vs_alphagenome"] = {
        "pearson_r": float(r), "pearson_p": float(p),
        "spearman_rho": float(rho), "spearman_p": float(p_s),
        "n": int(mask.sum()),
    }
    print(f"  ARCHCODE vs AlphaGenome: r = {r:.4f}, ρ = {rho:.4f} (n = {mask.sum()})")

    if hic is not None:
        hic_flat = upper_triangle(hic)

        mask_h = np.isfinite(arch_flat) & np.isfinite(hic_flat)
        if mask_h.sum() >= 10:
            r_ah, p_ah = pearsonr(arch_flat[mask_h], hic_flat[mask_h])
            rho_ah, ps_ah = spearmanr(arch_flat[mask_h], hic_flat[mask_h])
            results["archcode_vs_hic"] = {
                "pearson_r": float(r_ah), "pearson_p": float(p_ah),
                "spearman_rho": float(rho_ah), "spearman_p": float(ps_ah),
                "n": int(mask_h.sum()),
            }
            print(f"  ARCHCODE vs Hi-C:       r = {r_ah:.4f}, ρ = {rho_ah:.4f} (n = {mask_h.sum()})")

        mask_g = np.isfinite(ag_flat) & np.isfinite(hic_flat)
        if mask_g.sum() >= 10:
            r_gh, p_gh = pearsonr(ag_flat[mask_g], hic_flat[mask_g])
            rho_gh, ps_gh = spearmanr(ag_flat[mask_g], hic_flat[mask_g])
            results["alphagenome_vs_hic"] = {
                "pearson_r": float(r_gh), "pearson_p": float(p_gh),
                "spearman_rho": float(rho_gh), "spearman_p": float(ps_gh),
                "n": int(mask_g.sum()),
            }
            print(f"  AlphaGenome vs Hi-C:    r = {r_gh:.4f}, ρ = {rho_gh:.4f} (n = {mask_g.sum()})")

    return results


def main():
    parser = argparse.ArgumentParser(description="ARCHCODE vs AlphaGenome benchmark")
    parser.add_argument("--locus", default="30kb", help="Locus alias (default: 30kb)")
    parser.add_argument("--api-key", help="AlphaGenome API key")
    parser.add_argument("--api-key-file", help="File containing ALPHAGENOME_API_KEY=...")
    parser.add_argument(
        "--cell-line",
        default="GM12878",
        help="Cell line for contact map (default: GM12878). Available: GM12878, HepG2, HFFc6, etc.",
    )
    parser.add_argument("--output", help="Output JSON path (default: results/alphagenome_benchmark_<locus>.json)")
    args = parser.parse_args()

    api_key = get_api_key(args)

    print("=" * 70)
    print("ARCHCODE vs AlphaGenome Benchmark")
    print("=" * 70)

    # Step 1: Load locus config
    print(f"\n--- Step 1: Load locus config ({args.locus}) ---")
    config = load_locus_config(args.locus)
    window = config["window"]
    chrom = window["chromosome"]
    start = window["start"]
    end = window["end"]
    n_bins = window["n_bins"]
    resolution = window["resolution_bp"]
    print(f"  {chrom}:{start}-{end} ({n_bins} bins × {resolution} bp)")

    # Step 2: Build ARCHCODE wild-type matrix
    print(f"\n--- Step 2: Build ARCHCODE wild-type matrix ---")
    archcode_matrix = get_archcode_matrix(args.locus, config)
    print(f"  Shape: {archcode_matrix.shape}")
    print(f"  Value range: {archcode_matrix.min():.4f} - {archcode_matrix.max():.4f}")

    # Step 3: Get AlphaGenome prediction
    print(f"\n--- Step 3: AlphaGenome contact map prediction ---")
    ag_matrix_2d, ag_resolution, track_meta = predict_contact_map(
        api_key, chrom, start, end, args.cell_line
    )

    # Step 4: Extract our window from AlphaGenome output
    print(f"\n--- Step 4: Extract window & resample ---")
    window_size = end - start
    center = (start + end) // 2

    from alphagenome.models import dna_client
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())
    seq_length = next((sl for sl in supported if sl >= window_size), supported[-1])
    ag_interval_start = center - seq_length // 2

    ag_window = extract_window(ag_matrix_2d, ag_interval_start, ag_resolution, start, end)
    print(f"  AlphaGenome window shape: {ag_window.shape}")

    # Resample to match ARCHCODE resolution
    ag_resampled = resample_matrix(ag_window, n_bins)
    print(f"  Resampled to: {ag_resampled.shape}")

    # ПОЧЕМУ distance normalization: AlphaGenome возвращает distance-normalized
    # (Obs/Expected) values. ARCHCODE и Hi-C содержат raw contact probabilities
    # с distance decay. Для корректного сравнения приводим всех к O/E формату.
    print(f"  Distance-normalizing ARCHCODE matrix...")
    archcode_oe = distance_normalize(archcode_matrix)

    # AlphaGenome уже distance-normalized, просто exp() для линейной шкалы
    print(f"  AlphaGenome: applying exp() (log → linear scale)")
    ag_linear = np.exp(ag_resampled)

    def normalize(m):
        mn, mx = m.min(), m.max()
        if mx - mn < 1e-12:
            return np.zeros_like(m)
        return (m - mn) / (mx - mn)

    archcode_norm = normalize(archcode_oe)
    ag_norm = normalize(ag_linear)

    # Step 5: Load Hi-C if available
    print(f"\n--- Step 5: Correlation analysis ---")
    hic_matrix = None
    # ПОЧЕМУ только locus-specific: ранее fallback на *HBB* давал ложные корреляции
    # для CFTR и других локусов, где нет своего Hi-C файла. Загрузка Hi-C с чужого
    # локуса = ложная валидация. Лучше честно сказать "No Hi-C" чем показать
    # неверную корреляцию.
    gene_name = config.get("id", args.locus).split("_")[0].upper()
    hic_files = list((PROJECT_ROOT / "data" / "reference").glob(f"*{gene_name}*HiC*1000bp.npy"))

    if hic_files:
        hic_path = hic_files[0]
        print(f"  Loading Hi-C: {hic_path.name}")
        hic_raw = np.load(hic_path)
        if hic_raw.shape[0] != n_bins:
            hic_raw = resample_matrix(hic_raw, n_bins)
        hic_oe = distance_normalize(hic_raw)
        hic_matrix = normalize(hic_oe)
    else:
        print("  No Hi-C data found for this locus")

    correlations = correlate_matrices(archcode_norm, ag_norm, hic_matrix)

    # Step 6: Save results
    output_path = args.output or f"results/alphagenome_benchmark_{args.locus.replace('/', '_')}.json"
    output_path = PROJECT_ROOT / output_path

    result = {
        "locus": args.locus,
        "locus_id": config.get("id"),
        "window": {
            "chromosome": chrom,
            "start": start,
            "end": end,
            "resolution_bp": resolution,
            "n_bins": n_bins,
        },
        "alphagenome": {
            "sdk_version": "0.6.0",
            "sequence_length": seq_length,
            "contact_map_resolution": ag_resolution,
            "contact_map_shape": list(ag_matrix_2d.shape),
            "cell_line": args.cell_line,
            "track_name": track_meta.get("name", ""),
            "assay": track_meta.get("Assay title", ""),
            "ontology_curie": track_meta.get("ontology_curie", ""),
        },
        "correlations": correlations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))
    print(f"\n  Results saved: {output_path}")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY (distance-normalized, O/E)")
    print(f"{'=' * 70}")
    for key, label in [
        ("archcode_vs_alphagenome", "ARCHCODE ↔ AlphaGenome"),
        ("archcode_vs_hic", "ARCHCODE ↔ Hi-C"),
        ("alphagenome_vs_hic", "AlphaGenome ↔ Hi-C"),
    ]:
        if key in correlations:
            c = correlations[key]
            print(f"  {label:25s}  r = {c['pearson_r']:.4f}  ρ = {c['spearman_rho']:.4f}")
    print()


if __name__ == "__main__":
    main()
