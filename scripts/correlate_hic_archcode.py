#!/usr/bin/env python3
"""
Correlate K562 Hi-C contact matrix with ARCHCODE WT simulation.

ПОЧЕМУ: v1.0 used GM12878 Hi-C (r=0.16, p=0.30, n=12 — not significant).
GM12878 is a B-cell line where HBB is silent. K562 is erythroleukemia
(erythroid lineage) where HBB is actively transcribed → expect stronger
correlation because ARCHCODE models active-locus chromatin architecture.

This script:
  1. Regenerates the ARCHCODE WT reference matrix (same math as generate-unified-atlas.ts)
  2. Loads K562 Hi-C matrix from extract_k562_hbb.py output
  3. Handles resolution mismatch (Hi-C 1kb → ARCHCODE 600bp) via interpolation
  4. Computes Pearson r, Spearman ρ with p-values
  5. Compares to GM12878 baseline

Input:  data/reference/HBB_K562_HiC_{res}bp.npy
Output: results/hic_correlation_k562.json

Usage: python scripts/correlate_hic_archcode.py [--locus 30kb|95kb]
"""

import sys
import json
import math
import argparse
from pathlib import Path

import numpy as np
from scipy import stats, ndimage

from lib.locus_config import resolve_locus_path, load_locus_config, add_locus_argument

# === Parse arguments ===
_parser = argparse.ArgumentParser(description="Correlate K562 Hi-C with ARCHCODE WT")
add_locus_argument(_parser)
_args = _parser.parse_args()

# === Load locus config ===
_config_path = resolve_locus_path(_args.locus)
LOCUS = load_locus_config(_config_path)

SIM_START = LOCUS["window"]["start"]
SIM_END = LOCUS["window"]["end"]
RESOLUTION = LOCUS["window"]["resolution_bp"]
N_BINS = LOCUS["window"]["n_bins"]
ENHANCERS = LOCUS["features"]["enhancers"]
CTCF_SITES = LOCUS["features"]["ctcf_sites"]

# Kramer kinetics (from src/domain/constants/biophysics.ts — NOT in locus config)
K_BASE = 0.002
DEFAULT_ALPHA = 0.92
DEFAULT_GAMMA = 0.8
BACKGROUND_OCCUPANCY = 0.1

# Paths
DATA_DIR = Path(__file__).parent.parent / "data" / "reference"
RESULTS_DIR = Path(__file__).parent.parent / "results"


class SeededRandom:
    """Mulberry32 PRNG — must match SeededRandom from src/utils/random.ts exactly."""

    def __init__(self, seed: int):
        self._state = seed & 0xFFFFFFFF

    def random(self) -> float:
        # Mulberry32 algorithm (same as TypeScript)
        self._state = (self._state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self._state
        t = self._imul(t ^ (t >> 15), t | 1)
        t = (t ^ (t + self._imul(t ^ (t >> 7), t | 61))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    @staticmethod
    def _imul(a: int, b: int) -> int:
        """Emulate Math.imul (32-bit integer multiplication)."""
        a, b = a & 0xFFFFFFFF, b & 0xFFFFFFFF
        return ((a * b) & 0xFFFFFFFF)


def generate_archcode_wt_matrix(seed: int = 0) -> np.ndarray:
    """Regenerate ARCHCODE WT reference matrix.

    ПОЧЕМУ не грузим из файла: unified atlas генерирует пары (ref, mut) на лету
    для каждого варианта, а не сохраняет WT отдельно. Но WT reference одинакова
    для всех вариантов (она не зависит от позиции мутации), поэтому можно
    сгенерировать один раз.

    Логика полностью повторяет simulatePairedMatrices() из generate-unified-atlas.ts
    при variantBin = -1 (нет мутации).
    """
    rng = SeededRandom(seed)

    # Build MED1 occupancy landscape
    base_landscape = []
    for i in range(N_BINS):
        genomic_pos = SIM_START + i * RESOLUTION
        occ = BACKGROUND_OCCUPANCY + rng.random() * 0.05

        for enh in ENHANCERS:
            dist = abs(genomic_pos - enh["position"]) / RESOLUTION
            if dist < 5:
                occ += enh["occupancy"] * math.exp(-0.5 * dist * dist)

        base_landscape.append(min(1.0, occ))

    ref_occupancy = base_landscape[:]

    # CTCF barrier bins
    ctcf_bins = [
        math.floor((c["position"] - SIM_START) / RESOLUTION)
        for c in CTCF_SITES
    ]
    ctcf_bins = [b for b in ctcf_bins if 0 <= b < N_BINS]

    # Analytical contact map
    ref_matrix = np.zeros((N_BINS, N_BINS))

    for i in range(N_BINS):
        for j in range(i + 1, N_BINS):
            dist = j - i
            dist_factor = dist ** (-1.0)

            occ_factor = math.sqrt(ref_occupancy[i] * ref_occupancy[j])

            perm = 1.0
            for ctcf in ctcf_bins:
                if ctcf > i and ctcf < j:
                    perm *= 0.15

            kramer = 1 - K_BASE * (
                1 - DEFAULT_ALPHA * max(0.001, occ_factor) ** DEFAULT_GAMMA
            )

            val = dist_factor * occ_factor * perm * kramer
            ref_matrix[i, j] = val
            ref_matrix[j, i] = val

    # Normalize to [0, 1]
    max_val = ref_matrix.max()
    if max_val > 0:
        ref_matrix /= max_val

    return ref_matrix


def resize_matrix(matrix: np.ndarray, target_size: int) -> np.ndarray:
    """Resize Hi-C matrix to match ARCHCODE dimensions via zoom interpolation.

    ПОЧЕМУ zoom а не простой rebin: Hi-C может быть 30x30 (1kb) vs ARCHCODE 50x50 (600bp).
    ndimage.zoom с order=1 (bilinear) сохраняет структуру контактов
    без артефактов интерполяции высокого порядка.
    """
    current_size = matrix.shape[0]
    if current_size == target_size:
        return matrix

    zoom_factor = target_size / current_size
    resized = ndimage.zoom(matrix, zoom_factor, order=1)

    # Ensure exact target size (zoom may be off by 1 pixel)
    if resized.shape[0] != target_size:
        result = np.zeros((target_size, target_size))
        n = min(target_size, resized.shape[0])
        result[:n, :n] = resized[:n, :n]
        resized = result

    # Enforce symmetry
    resized = (resized + resized.T) / 2.0
    return resized


def flatten_upper_triangle(matrix: np.ndarray, k_min: int = 2) -> np.ndarray:
    """Extract upper triangle excluding near-diagonal (k < k_min).

    ПОЧЕМУ k_min=2: near-diagonal bins are dominated by polymer self-contact
    (distance decay) rather than specific 3D architecture. Excluding them
    focuses the correlation on biologically meaningful long-range contacts.
    """
    n = matrix.shape[0]
    values = []
    for i in range(n):
        for j in range(i + k_min, n):
            values.append(matrix[i, j])
    return np.array(values)


def compute_correlations(
    archcode: np.ndarray, hic: np.ndarray, k_min: int = 2
) -> dict:
    """Compute Pearson and Spearman correlations between flattened upper triangles."""
    arch_flat = flatten_upper_triangle(archcode, k_min)
    hic_flat = flatten_upper_triangle(hic, k_min)

    # Remove entries where Hi-C is zero (no data / unmappable)
    mask = (hic_flat > 0) & np.isfinite(hic_flat) & np.isfinite(arch_flat)
    arch_valid = arch_flat[mask]
    hic_valid = hic_flat[mask]

    n_total = len(arch_flat)
    n_valid = len(arch_valid)

    if n_valid < 10:
        return {
            "error": f"Too few valid data points ({n_valid})",
            "n_total": n_total,
            "n_valid": n_valid,
        }

    pearson_r, pearson_p = stats.pearsonr(arch_valid, hic_valid)
    spearman_r, spearman_p = stats.spearmanr(arch_valid, hic_valid)

    return {
        "k_min": k_min,
        "n_total": n_total,
        "n_valid": n_valid,
        "n_zero_removed": n_total - n_valid,
        "pearson_r": round(float(pearson_r), 4),
        "pearson_p": float(pearson_p),
        "spearman_rho": round(float(spearman_r), 4),
        "spearman_p": float(spearman_p),
    }


def main():
    print("=" * 60)
    print("  ARCHCODE: K562 Hi-C vs Simulation Correlation")
    print("=" * 60)
    print(f"  Locus config: {LOCUS['id']} ({LOCUS['name']})")
    print(f"  Window: chr11:{SIM_START}-{SIM_END} ({(SIM_END - SIM_START) // 1000}kb)")
    print(f"  Matrix: {N_BINS}x{N_BINS} ({RESOLUTION}bp resolution)")

    # Step 1: Generate ARCHCODE WT matrix
    print("\n--- Step 1: Generate ARCHCODE WT reference matrix ---")
    archcode_wt = generate_archcode_wt_matrix(seed=0)
    print(f"  Shape: {archcode_wt.shape}")
    print(f"  Range: [{archcode_wt.min():.4f}, {archcode_wt.max():.4f}]")

    # Save for inspection
    archcode_npy = DATA_DIR / f"ARCHCODE_WT_reference_{N_BINS}x{N_BINS}.npy"
    np.save(archcode_npy, archcode_wt)
    print(f"  Saved: {archcode_npy.name}")

    # Step 2: Load K562 Hi-C matrix
    print("\n--- Step 2: Load K562 Hi-C matrix ---")

    # Find the extracted .npy file matching the current locus window size
    window_kb = (SIM_END - SIM_START) // 1000
    hic_pattern = f"HBB_K562_HiC_{window_kb}kb_*bp.npy" if window_kb != 30 else "HBB_K562_HiC_*bp.npy"
    hic_files = sorted(DATA_DIR.glob(hic_pattern))
    hic_files = [f for f in hic_files if "extended" not in f.name]

    if not hic_files:
        print("  ERROR: No HBB K562 Hi-C matrix found.")
        print("  Run first: python scripts/extract_k562_hbb.py")
        sys.exit(1)

    hic_path = hic_files[0]
    hic_matrix = np.load(hic_path)
    hic_res = int(hic_path.stem.split("_")[-1].replace("bp", ""))

    print(f"  File: {hic_path.name}")
    print(f"  Shape: {hic_matrix.shape}")
    print(f"  Resolution: {hic_res}bp")
    print(f"  Range: [{hic_matrix.min():.6f}, {hic_matrix.max():.6f}]")

    # Step 3: Resize Hi-C to match ARCHCODE
    print(f"\n--- Step 3: Resize Hi-C ({hic_matrix.shape[0]}x{hic_matrix.shape[0]}) → ({N_BINS}x{N_BINS}) ---")
    hic_resized = resize_matrix(hic_matrix, N_BINS)
    print(f"  Resized: {hic_resized.shape}")

    # Normalize Hi-C to [0, 1] for fair comparison
    hic_max = hic_resized.max()
    if hic_max > 0:
        hic_norm = hic_resized / hic_max
    else:
        print("  ERROR: Hi-C matrix is all zeros")
        sys.exit(1)

    # Step 4: Compute correlations
    print("\n--- Step 4: Compute correlations ---")

    results = {}
    for k_min in [2, 3, 5]:
        corr = compute_correlations(archcode_wt, hic_norm, k_min=k_min)
        results[f"k_min_{k_min}"] = corr
        if "error" not in corr:
            sig = "***" if corr["pearson_p"] < 0.001 else (
                "**" if corr["pearson_p"] < 0.01 else (
                    "*" if corr["pearson_p"] < 0.05 else "ns"
                )
            )
            print(f"  k>={k_min}: Pearson r={corr['pearson_r']:.4f} (p={corr['pearson_p']:.2e}) {sig}")
            print(f"         Spearman ρ={corr['spearman_rho']:.4f} (p={corr['spearman_p']:.2e})")
            print(f"         n={corr['n_valid']} valid / {corr['n_total']} total")
        else:
            print(f"  k>={k_min}: {corr['error']}")

    # Primary result (k>=2, standard for Hi-C comparison)
    primary = results.get("k_min_2", {})

    # Step 5: Comparison with GM12878
    print("\n--- Step 5: Comparison with previous result ---")
    gm12878 = {"pearson_r": 0.16, "pearson_p": 0.30, "n": 12, "cell_line": "GM12878"}
    print(f"  GM12878 (v1.0):  r = {gm12878['pearson_r']:.2f} (p = {gm12878['pearson_p']:.2f}, n = {gm12878['n']})")

    if "error" not in primary:
        improvement = primary["pearson_r"] - gm12878["pearson_r"]
        print(f"  K562    (v2.0):  r = {primary['pearson_r']:.4f} (p = {primary['pearson_p']:.2e}, n = {primary['n_valid']})")
        print(f"  Improvement:     Δr = {improvement:+.4f}")

        if primary["pearson_p"] < 0.05:
            print("  SIGNIFICANT: K562 correlation is statistically significant!")
        else:
            print("  Not significant at α=0.05")

    # Step 6: Save results
    print("\n--- Step 6: Save results ---")
    RESULTS_DIR.mkdir(exist_ok=True)

    output = {
        "analysis": "ARCHCODE vs K562 Hi-C correlation",
        "locus_config_id": LOCUS["id"],
        "archcode": {
            "region": f"chr11:{SIM_START}-{SIM_END}",
            "resolution_bp": RESOLUTION,
            "matrix_size": N_BINS,
            "parameters": {
                "K_BASE": K_BASE,
                "alpha": DEFAULT_ALPHA,
                "gamma": DEFAULT_GAMMA,
            },
        },
        "hic": {
            "source": "4DNFI18UHVRO.mcool (4DN Data Portal)",
            "cell_line": "K562",
            "original_resolution_bp": hic_res,
            "interpolated_to": N_BINS,
        },
        "correlations": results,
        "primary_result": primary,
        "comparison": {
            "gm12878_v1": gm12878,
            "k562_v2": {
                "pearson_r": primary.get("pearson_r"),
                "pearson_p": primary.get("pearson_p"),
                "n": primary.get("n_valid"),
            },
        },
    }

    suffix = f"_{_args.locus}" if _args.locus != "30kb" else ""
    output_path = RESULTS_DIR / f"hic_correlation_k562{suffix}.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved: {output_path}")

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
