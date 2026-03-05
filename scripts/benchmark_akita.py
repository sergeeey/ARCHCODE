#!/usr/bin/env python3
"""
ARCHCODE vs Akita benchmark: compare contact map predictions using local DL inference.

ПОЧЕМУ этот скрипт:
Akita (Fudenberg et al. 2020, Nature Methods) — открытая DL-модель для contact maps.
Тот же 2048bp resolution что AlphaGenome, но полностью локальный inference (Basenji/TF).
Двойной DL-бенчмарк (AlphaGenome + Akita) подтверждает: ARCHCODE vs two independent DL models.

Akita model specs:
- Input: 1,048,576 bp DNA one-hot (N, 1048576, 4)
- Output: upper triangle vector (N, 99681, 5)
- Resolution: 2048 bp → 448×448 contact map (512 - 2×32 crop)
- Targets: [HFF, H1-hESC, GM12878, IMR-90, HCT-116]
- Output format: log₂(O/E) — distance normalized

Usage:
    python scripts/benchmark_akita.py --locus 30kb
    python scripts/benchmark_akita.py --locus cftr
    python scripts/benchmark_akita.py --all
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

PROJECT_ROOT = Path(__file__).parent.parent

# ПОЧЕМУ target index map: Akita выдаёт 5 cell types в фиксированном порядке
# из обучающего набора (Rao et al. 2014 Hi-C). GM12878 = idx 2.
AKITA_TARGETS = {
    "HFF": 0,
    "H1-hESC": 1,
    "GM12878": 2,
    "IMR-90": 3,
    "HCT-116": 4,
}

# Akita architecture constants from params.json
AKITA_SEQ_LENGTH = 1_048_576  # 1Mb input
AKITA_TARGET_LENGTH = 512
AKITA_CROP = 32
AKITA_DIAG_OFFSET = 2
AKITA_OUTPUT_SIZE = 448  # 512 - 2*32
AKITA_RESOLUTION = 2048  # bp per bin


def load_locus_config(locus: str) -> dict:
    """Load locus config using the standard ARCHCODE loader."""
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from lib.locus_config import resolve_locus_path, load_locus_config as _load
    path = resolve_locus_path(locus)
    return _load(path)


def get_archcode_matrix(locus: str) -> np.ndarray:
    """Build ARCHCODE wild-type contact matrix using the analytical engine."""
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from tda_proof_of_concept import build_contact_matrix, load_locus_config as tda_load
    tda_config = tda_load(locus)
    matrix = build_contact_matrix(tda_config, variant_bin=-1)
    return matrix


def fetch_sequence(chrom: str, start: int, end: int) -> str:
    """
    Fetch reference sequence from Ensembl REST API.

    ПОЧЕМУ Ensembl REST: не требует локальной FASTA (>3 GB для hg38).
    Один HTTP запрос на 1Mb — ~2 секунды. Кешируем в data/reference_sequences/.
    """
    import urllib.request

    cache_dir = PROJECT_ROOT / "data" / "reference_sequences"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{chrom}_{start}_{end}.txt"

    if cache_path.exists():
        seq = cache_path.read_text().strip()
        if len(seq) == end - start:
            print(f"  Cached sequence: {cache_path.name} ({len(seq)} bp)")
            return seq

    # ПОЧЕМУ chrom_num: Ensembl REST API использует "11" а не "chr11"
    # ПОЧЕМУ end-1: Ensembl 1-based inclusive на обоих концах, т.е. start..end
    # возвращает (end-start+1) bp. Нам нужно ровно (end-start) bp.
    chrom_num = chrom.replace("chr", "")
    url = f"https://rest.ensembl.org/sequence/region/human/{chrom_num}:{start}..{end - 1}:1"
    headers = {"Content-Type": "text/plain"}

    print(f"  Fetching {chrom}:{start}-{end} from Ensembl REST API...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        seq = response.read().decode("utf-8").strip()

    if len(seq) != end - start:
        raise RuntimeError(
            f"Ensembl returned {len(seq)} bp, expected {end - start} bp"
        )

    cache_path.write_text(seq)
    print(f"  Fetched {len(seq)} bp, cached to {cache_path.name}")
    return seq


def load_akita_model():
    """
    Load Akita model from local weights.

    ПОЧЕМУ sys.path вместо pip install: basenji зависит от pysam/pybigwig
    которые не ставятся на Windows. Нам нужны только seqnn + dna_io.
    """
    sys.path.insert(0, str(PROJECT_ROOT / "external" / "basenji"))
    from basenji import seqnn

    params_path = PROJECT_ROOT / "data" / "models" / "akita" / "params.json"
    weights_path = PROJECT_ROOT / "data" / "models" / "akita" / "model_best.h5"

    if not weights_path.exists():
        raise FileNotFoundError(
            f"Akita weights not found: {weights_path}\n"
            f"Download: curl -L -o {weights_path} "
            f"https://storage.googleapis.com/basenji_hic/1m/models/9-14/model_best.h5"
        )

    with open(params_path) as f:
        params = json.load(f)

    print("  Building Akita model...")
    model = seqnn.SeqNN(params["model"])
    model.restore(str(weights_path))
    print(f"  Model loaded: input={model.model.input_shape}, output={model.model.output_shape}")
    return model


def predict_contact_map(
    model,
    sequence: str,
    target_idx: int = 2,
) -> np.ndarray:
    """
    Predict contact map from DNA sequence using Akita.

    ПОЧЕМУ one-hot + predict + reshape: Akita API — это raw TF model,
    не cloud SDK. Мы делаем всё руками: encode → predict → reshape.

    Returns 448×448 contact map (log₂(O/E) values).
    """
    sys.path.insert(0, str(PROJECT_ROOT / "external" / "basenji"))
    from basenji import dna_io

    if len(sequence) != AKITA_SEQ_LENGTH:
        raise ValueError(
            f"Akita requires {AKITA_SEQ_LENGTH} bp, got {len(sequence)} bp"
        )

    seq_1hot = dna_io.dna_1hot(sequence)
    pred = model.model.predict(seq_1hot[np.newaxis], verbose=0)
    # pred shape: (1, 99681, 5)

    # Extract target cell type
    ut_vector = pred[0, :, target_idx]

    # ПОЧЕМУ upper_tri_to_2d: Akita выдаёт верхний треугольник как вектор.
    # Нужно восстановить 2D matrix для визуализации и корреляции.
    mat = upper_tri_to_2d(ut_vector, n=AKITA_OUTPUT_SIZE, offset=AKITA_DIAG_OFFSET)
    return mat


def upper_tri_to_2d(ut_vector: np.ndarray, n: int = 448, offset: int = 2) -> np.ndarray:
    """
    Reconstruct 2D symmetric matrix from upper triangle vector.

    ПОЧЕМУ offset=2: Akita обрезает 2 ближайшие диагонали (self-contact + nearest neighbor).
    """
    mat = np.zeros((n, n))
    triu_idx = np.triu_indices(n, k=offset)
    expected_len = len(triu_idx[0])
    if len(ut_vector) != expected_len:
        raise ValueError(
            f"Upper triangle vector length {len(ut_vector)} != expected {expected_len} "
            f"for n={n}, offset={offset}"
        )
    mat[triu_idx] = ut_vector
    mat += mat.T
    return mat


def extract_window(
    full_matrix: np.ndarray,
    full_interval_start: int,
    resolution: int,
    window_start: int,
    window_end: int,
) -> np.ndarray:
    """Extract locus window from the full Akita 448×448 contact matrix."""
    bin_start = (window_start - full_interval_start) // resolution
    bin_end = (window_end - full_interval_start) // resolution

    bin_start = max(0, bin_start)
    bin_end = min(full_matrix.shape[0], bin_end)

    print(f"  Extracting bins {bin_start}:{bin_end} from {full_matrix.shape[0]} total bins")
    return full_matrix[bin_start:bin_end, bin_start:bin_end]


def resample_matrix(matrix: np.ndarray, target_size: int) -> np.ndarray:
    """Resample contact matrix to target_size × target_size (bilinear)."""
    from scipy.ndimage import zoom

    if matrix.shape[0] == target_size:
        return matrix

    factor = target_size / matrix.shape[0]
    resampled = zoom(matrix, factor, order=1)
    return resampled[:target_size, :target_size]


def distance_normalize(matrix: np.ndarray) -> np.ndarray:
    """Compute O/E ratio per genomic distance stratum."""
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


def _global_ssim_from_arrays(a: np.ndarray, b: np.ndarray) -> float:
    """Compute SSIM on two flattened arrays."""
    if a.size == 0 or b.size == 0:
        return 1.0
    mu_a = float(np.mean(a))
    mu_b = float(np.mean(b))
    sig_a2 = float(np.mean((a - mu_a) ** 2))
    sig_b2 = float(np.mean((b - mu_b) ** 2))
    sig_ab = float(np.mean((a - mu_a) * (b - mu_b)))
    c1 = 0.0001
    c2 = 0.0009
    denom = (mu_a * mu_a + mu_b * mu_b + c1) * (sig_a2 + sig_b2 + c2)
    if abs(denom) < 1e-15:
        return 1.0
    return float(((2 * mu_a * mu_b + c1) * (2 * sig_ab + c2)) / denom)


def local_ssim_mean(
    ref: np.ndarray,
    mut: np.ndarray,
    window_size: int = 50,
) -> tuple[float, int]:
    """
    Sliding-window local SSIM mean over contact matrices.
    Uses upper triangle (k=1) within each local window.
    """
    n = ref.shape[0]
    if n == 0 or ref.shape != mut.shape:
        return 0.0, 0

    if n <= window_size:
        idx = np.triu_indices(n, k=1)
        return _global_ssim_from_arrays(ref[idx], mut[idx]), 1

    step = max(1, window_size // 2)
    ssim_sum = 0.0
    count = 0
    for i in range(0, n - window_size + 1, step):
        for j in range(0, n - window_size + 1, step):
            sub_ref = ref[i : i + window_size, j : j + window_size]
            sub_mut = mut[i : i + window_size, j : j + window_size]
            idx = np.triu_indices(window_size, k=1)
            ssim_sum += _global_ssim_from_arrays(sub_ref[idx], sub_mut[idx])
            count += 1
    return (ssim_sum / count if count > 0 else 0.0), count


def compute_local_metrics(
    archcode: np.ndarray,
    akita: np.ndarray,
    hic: np.ndarray | None = None,
    window_size: int = 50,
) -> dict:
    """Compute local SSIM metrics for the same pairs as correlation metrics."""
    local = {}
    lssim, nwin = local_ssim_mean(archcode, akita, window_size)
    local["archcode_vs_akita"] = {
        "local_ssim_mean": float(lssim),
        "window_size": int(window_size),
        "n_local_windows": int(nwin),
    }
    if hic is not None:
        lssim_ah, nwin_ah = local_ssim_mean(archcode, hic, window_size)
        local["archcode_vs_hic"] = {
            "local_ssim_mean": float(lssim_ah),
            "window_size": int(window_size),
            "n_local_windows": int(nwin_ah),
        }
        lssim_gh, nwin_gh = local_ssim_mean(akita, hic, window_size)
        local["akita_vs_hic"] = {
            "local_ssim_mean": float(lssim_gh),
            "window_size": int(window_size),
            "n_local_windows": int(nwin_gh),
        }
    return local


def correlate_matrices(
    archcode: np.ndarray,
    akita: np.ndarray,
    hic: np.ndarray | None = None,
) -> dict:
    """Compute Pearson and Spearman correlations between matrix pairs."""
    from scipy.stats import pearsonr, spearmanr

    results = {}

    def upper_triangle(m: np.ndarray) -> np.ndarray:
        return m[np.triu_indices_from(m, k=2)]

    arch_flat = upper_triangle(archcode)
    ak_flat = upper_triangle(akita)

    mask = np.isfinite(arch_flat) & np.isfinite(ak_flat)
    if mask.sum() < 10:
        print("  WARNING: too few valid pairs for correlation")
        return {"error": "insufficient valid pairs"}

    r, p = pearsonr(arch_flat[mask], ak_flat[mask])
    rho, p_s = spearmanr(arch_flat[mask], ak_flat[mask])
    results["archcode_vs_akita"] = {
        "pearson_r": float(r), "pearson_p": float(p),
        "spearman_rho": float(rho), "spearman_p": float(p_s),
        "n": int(mask.sum()),
    }
    print(f"  ARCHCODE vs Akita: r = {r:.4f}, ρ = {rho:.4f} (n = {mask.sum()})")

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
            print(f"  ARCHCODE vs Hi-C:  r = {r_ah:.4f}, ρ = {rho_ah:.4f} (n = {mask_h.sum()})")

        mask_g = np.isfinite(ak_flat) & np.isfinite(hic_flat)
        if mask_g.sum() >= 10:
            r_gh, p_gh = pearsonr(ak_flat[mask_g], hic_flat[mask_g])
            rho_gh, ps_gh = spearmanr(ak_flat[mask_g], hic_flat[mask_g])
            results["akita_vs_hic"] = {
                "pearson_r": float(r_gh), "pearson_p": float(p_gh),
                "spearman_rho": float(rho_gh), "spearman_p": float(ps_gh),
                "n": int(mask_g.sum()),
            }
            print(f"  Akita vs Hi-C:     r = {r_gh:.4f}, ρ = {rho_gh:.4f} (n = {mask_g.sum()})")

    return results


def benchmark_locus(
    model,
    locus: str,
    cell_type: str = "GM12878",
) -> dict:
    """Run full benchmark for a single locus."""
    target_idx = AKITA_TARGETS.get(cell_type)
    if target_idx is None:
        raise ValueError(f"Unknown cell type: {cell_type}. Available: {list(AKITA_TARGETS.keys())}")

    # Step 1: Load locus config
    print(f"\n--- Load locus config ({locus}) ---")
    config = load_locus_config(locus)
    window = config["window"]
    chrom = window["chromosome"]
    start = window["start"]
    end = window["end"]
    n_bins = window["n_bins"]
    resolution = window["resolution_bp"]
    print(f"  {chrom}:{start}-{end} ({n_bins} bins × {resolution} bp)")

    # Step 2: Build ARCHCODE wild-type matrix
    print(f"\n--- Build ARCHCODE wild-type matrix ---")
    archcode_matrix = get_archcode_matrix(locus)
    print(f"  Shape: {archcode_matrix.shape}")

    # Step 3: Fetch 1Mb sequence centered on locus
    print(f"\n--- Fetch reference sequence ---")
    center = (start + end) // 2
    seq_start = center - AKITA_SEQ_LENGTH // 2
    seq_end = center + AKITA_SEQ_LENGTH // 2
    sequence = fetch_sequence(chrom, seq_start, seq_end)

    # Step 4: Akita prediction
    print(f"\n--- Akita contact map prediction ({cell_type}, idx={target_idx}) ---")
    t0 = time.time()
    akita_matrix = predict_contact_map(model, sequence, target_idx)
    predict_time = time.time() - t0
    print(f"  Full contact map shape: {akita_matrix.shape}")
    print(f"  Prediction time: {predict_time:.1f}s")

    # Step 5: Extract locus window from Akita output
    print(f"\n--- Extract window & resample ---")
    akita_window = extract_window(
        akita_matrix, seq_start, AKITA_RESOLUTION, start, end
    )
    print(f"  Akita window shape: {akita_window.shape}")

    akita_resampled = resample_matrix(akita_window, n_bins)
    print(f"  Resampled to: {akita_resampled.shape}")

    # ПОЧЕМУ distance normalization: Akita output — log₂(O/E), уже distance-normalized.
    # ARCHCODE — raw contact probabilities. Приводим ARCHCODE к O/E формату,
    # а Akita переводим из log-scale в линейный (exp).
    print(f"  Distance-normalizing ARCHCODE matrix...")
    archcode_oe = distance_normalize(archcode_matrix)

    print(f"  Akita: applying exp() (log → linear scale)")
    akita_linear = np.exp(akita_resampled)

    def normalize(m):
        mn, mx = m.min(), m.max()
        if mx - mn < 1e-12:
            return np.zeros_like(m)
        return (m - mn) / (mx - mn)

    archcode_norm = normalize(archcode_oe)
    akita_norm = normalize(akita_linear)

    # Step 6: Load Hi-C if available
    print(f"\n--- Correlation analysis ---")
    hic_matrix = None
    gene_name = config.get("id", locus).split("_")[0].upper()
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

    correlations = correlate_matrices(archcode_norm, akita_norm, hic_matrix)
    local_metrics = compute_local_metrics(archcode_norm, akita_norm, hic_matrix, window_size=50)

    # Build result
    result = {
        "locus": locus,
        "locus_id": config.get("id"),
        "window": {
            "chromosome": chrom,
            "start": start,
            "end": end,
            "resolution_bp": resolution,
            "n_bins": n_bins,
        },
        "akita": {
            "framework": "basenji",
            "model_file": "model_best.h5",
            "reference": "Fudenberg et al. 2020, Nature Methods",
            "seq_length": AKITA_SEQ_LENGTH,
            "contact_map_resolution": AKITA_RESOLUTION,
            "contact_map_shape": [AKITA_OUTPUT_SIZE, AKITA_OUTPUT_SIZE],
            "cell_type": cell_type,
            "target_index": target_idx,
            "akita_window_bins": int(akita_window.shape[0]),
            "prediction_time_sec": round(predict_time, 1),
        },
        "correlations": correlations,
        "local_metrics": local_metrics,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="ARCHCODE vs Akita benchmark")
    parser.add_argument("--locus", default="30kb", help="Locus alias (default: 30kb)")
    parser.add_argument(
        "--cell-type", default="GM12878",
        help="Cell type for contact map (default: GM12878). Available: HFF, H1-hESC, GM12878, IMR-90, HCT-116",
    )
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument(
        "--all", action="store_true",
        help="Run benchmark for all 6 loci",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("ARCHCODE vs Akita Benchmark (Local DL Inference)")
    print("=" * 70)

    # Load model once — reuse for all loci
    print("\n--- Loading Akita model ---")
    model = load_akita_model()

    loci = ["30kb", "95kb", "cftr", "tp53", "brca1", "mlh1", "ldlr"] if args.all else [args.locus]

    for locus in loci:
        print(f"\n{'=' * 70}")
        print(f"LOCUS: {locus}")
        print(f"{'=' * 70}")

        try:
            result = benchmark_locus(model, locus, args.cell_type)
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
            continue

        # Save results
        output_path = args.output if (args.output and len(loci) == 1) else None
        if output_path is None:
            output_path = f"results/akita_benchmark_{locus.replace('/', '_')}.json"
        output_path = PROJECT_ROOT / output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2))
        print(f"\n  Results saved: {output_path}")

        # Summary
        print(f"\n  SUMMARY (distance-normalized, O/E):")
        for key, label in [
            ("archcode_vs_akita", "ARCHCODE ↔ Akita"),
            ("archcode_vs_hic", "ARCHCODE ↔ Hi-C"),
            ("akita_vs_hic", "Akita ↔ Hi-C"),
        ]:
            if key in result["correlations"]:
                c = result["correlations"][key]
                print(f"    {label:22s}  r = {c['pearson_r']:.4f}  ρ = {c['spearman_rho']:.4f}")
                if key in result["local_metrics"]:
                    lm = result["local_metrics"][key]
                    print(
                        f"    {'':22s}  LSSIM = {lm['local_ssim_mean']:.4f} "
                        f"(w={lm['window_size']}, n={lm['n_local_windows']})"
                    )

    print(f"\n{'=' * 70}")
    print("DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
