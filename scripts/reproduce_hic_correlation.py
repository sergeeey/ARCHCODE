#!/usr/bin/env python3
"""
Independent reproduction of Hi-C validation correlations.

Loads raw Hi-C .npy matrices and ARCHCODE locus configs,
regenerates the analytical WT contact matrix from scratch,
and computes Pearson r independently.

Compares with claimed values:
  BRCA1 K562: r=0.53
  TP53  K562: r=0.29

Usage: python scripts/reproduce_hic_correlation.py
"""

import json
import math
from pathlib import Path

import numpy as np
from scipy import stats, ndimage

PROJECT = Path(__file__).parent.parent
DATA_REF = PROJECT / "data" / "reference"
CONFIG_DIR = PROJECT / "config" / "locus"


def load_config(name: str) -> dict:
    path = CONFIG_DIR / name
    with open(path) as f:
        return json.load(f)


# ============================================================
# Method A: "correlate_hic_archcode.py" style (HBB-derived)
#   - Gaussian occupancy spreading from enhancers
#   - Mulberry32 PRNG for background noise
#   - sqrt(occ_i * occ_j) factor
#   - CTCF barrier *= 0.15
#   - Kramer kinetics: (1 - K_BASE*(1 - alpha*occ^gamma))
#   - Normalized to [0,1]
# ============================================================


class SeededRandom:
    """Mulberry32 PRNG — must match TypeScript exactly."""

    def __init__(self, seed: int):
        self._state = seed & 0xFFFFFFFF

    def random(self) -> float:
        self._state = (self._state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self._state
        t = self._imul(t ^ (t >> 15), t | 1)
        t = (t ^ (t + self._imul(t ^ (t >> 7), t | 61))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    @staticmethod
    def _imul(a: int, b: int) -> int:
        a, b = a & 0xFFFFFFFF, b & 0xFFFFFFFF
        return (a * b) & 0xFFFFFFFF


def build_archcode_matrix_method_a(config: dict) -> np.ndarray:
    """Rebuild WT matrix using Method A (correlate_hic_archcode.py style)."""
    w = config["window"]
    n = w["n_bins"]
    res = w["resolution_bp"]
    start = w["start"]
    enhancers = config["features"]["enhancers"]
    ctcf_sites = config["features"]["ctcf_sites"]

    K_BASE = 0.002
    ALPHA = 0.92
    GAMMA = 0.8
    BG_OCC = 0.1

    rng = SeededRandom(0)

    # Occupancy landscape with Gaussian spreading
    occ = []
    for i in range(n):
        pos = start + i * res
        o = BG_OCC + rng.random() * 0.05
        for enh in enhancers:
            dist = abs(pos - enh["position"]) / res
            if dist < 5:
                o += enh["occupancy"] * math.exp(-0.5 * dist * dist)
        occ.append(min(1.0, o))

    # CTCF bins
    ctcf_bins = []
    for c in ctcf_sites:
        b = math.floor((c["position"] - start) / res)
        if 0 <= b < n:
            ctcf_bins.append(b)

    # Build contact matrix
    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = j - i
            dist_factor = d ** (-1.0)
            occ_factor = math.sqrt(occ[i] * occ[j])

            perm = 1.0
            for cb in ctcf_bins:
                if cb > i and cb < j:
                    perm *= 0.15

            kramer = 1 - K_BASE * (1 - ALPHA * max(0.001, occ_factor) ** GAMMA)
            val = dist_factor * occ_factor * perm * kramer
            mat[i, j] = val
            mat[j, i] = val

    mx = mat.max()
    if mx > 0:
        mat /= mx
    return mat


# ============================================================
# Method B: "download_hic_regions.py" style (correlate_with_archcode)
#   - Point occupancy (no Gaussian spreading)
#   - No PRNG noise
#   - avg_occ = (occ_i + occ_j)/2 for Kramer
#   - Same CTCF barrier
# ============================================================


def build_archcode_matrix_method_b(config: dict) -> np.ndarray:
    """Rebuild WT matrix using Method B (download_hic_regions.py style)."""
    w = config["window"]
    n = w["n_bins"]
    res = w["resolution_bp"]
    start = w["start"]
    enhancers = config["features"]["enhancers"]
    ctcf_sites = config["features"]["ctcf_sites"]

    ALPHA = 0.92
    GAMMA = 0.80
    K_BASE = 0.002

    # Point occupancy (no Gaussian spreading)
    occ = np.full(n, 0.01)
    for enh in enhancers:
        b = (enh["position"] - start) // res
        if 0 <= b < n:
            occ[b] = max(occ[b], enh["occupancy"])

    ctcf_bins = []
    for c in ctcf_sites:
        b = (c["position"] - start) // res
        if 0 <= b < n:
            ctcf_bins.append(b)

    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            d = abs(i - j)
            if d == 0:
                mat[i, j] = 1.0
                continue

            contact = (1.0 / d) * np.sqrt(occ[i] * occ[j])

            perm = 1.0
            for cb in ctcf_bins:
                if cb > i and cb < j:
                    perm *= 0.15
            contact *= perm

            avg_occ = (occ[i] + occ[j]) / 2.0
            p_unload = K_BASE * (1.0 - ALPHA * (avg_occ**GAMMA))
            contact *= 1.0 - p_unload

            mat[i, j] = contact
            mat[j, i] = contact

    return mat


def resize_matrix(matrix: np.ndarray, target: int) -> np.ndarray:
    """Bilinear interpolation resize."""
    if matrix.shape[0] == target:
        return matrix
    zoom = target / matrix.shape[0]
    resized = ndimage.zoom(matrix, zoom, order=1)
    if resized.shape[0] != target:
        result = np.zeros((target, target))
        m = min(target, resized.shape[0])
        result[:m, :m] = resized[:m, :m]
        resized = result
    return (resized + resized.T) / 2.0


def correlate_upper_triangle(a: np.ndarray, b: np.ndarray, k_min: int = 1):
    """Pearson & Spearman on upper triangle, excluding near-diagonal."""
    n = a.shape[0]
    a_vals, b_vals = [], []
    for i in range(n):
        for j in range(i + k_min, n):
            a_vals.append(a[i, j])
            b_vals.append(b[i, j])
    a_arr = np.array(a_vals)
    b_arr = np.array(b_vals)

    # Remove zeros in Hi-C (unmappable)
    mask = (b_arr > 0) & np.isfinite(a_arr) & np.isfinite(b_arr)
    a_v = a_arr[mask]
    b_v = b_arr[mask]

    if len(a_v) < 10:
        return None, None, None, None, 0

    r, p = stats.pearsonr(a_v, b_v)
    rho, rho_p = stats.spearmanr(a_v, b_v)
    return r, p, rho, rho_p, len(a_v)


def analyze_locus(
    gene: str, config_file: str, hic_file: str, claimed_r: float, cell_type: str = "K562"
):
    """Full independent analysis for one locus."""
    print(f"\n{'=' * 70}")
    print(f"  {gene} — Independent Hi-C Correlation Reproduction")
    print(f"{'=' * 70}")

    config = load_config(config_file)
    w = config["window"]
    n_bins = w["n_bins"]
    res = w["resolution_bp"]
    print(f"  Config: {config_file}")
    print(
        f"  Window: {w['chromosome']}:{w['start']:,}-{w['end']:,} ({(w['end'] - w['start']) // 1000}kb)"
    )
    print(f"  Matrix: {n_bins}x{n_bins} @ {res}bp")
    print(f"  Enhancers: {len(config['features']['enhancers'])}")
    print(f"  CTCF sites: {len(config['features']['ctcf_sites'])}")

    # Load Hi-C
    hic_path = DATA_REF / hic_file
    if not hic_path.exists():
        print(f"  ERROR: Hi-C file not found: {hic_path}")
        return
    hic = np.load(hic_path)
    print(f"\n  Hi-C matrix: {hic.shape}, range [{hic.min():.4f}, {hic.max():.4f}]")
    print(f"  Non-zero fraction: {np.count_nonzero(hic) / hic.size:.3f}")

    # Resize Hi-C to match ARCHCODE bins
    hic_resized = resize_matrix(hic, n_bins)
    hic_max = hic_resized.max()
    if hic_max > 0:
        hic_norm = hic_resized / hic_max
    else:
        print("  ERROR: Hi-C all zeros after resize")
        return

    # ---- Method A (correlate_hic_archcode.py style) ----
    print(f"\n  --- Method A: Gaussian occupancy + Mulberry32 PRNG ---")
    arch_a = build_archcode_matrix_method_a(config)
    for k_min in [1, 2]:
        r, p, rho, rho_p, n_v = correlate_upper_triangle(arch_a, hic_norm, k_min=k_min)
        if r is not None:
            print(
                f"    k>={k_min}: Pearson r = {r:.4f} (p={p:.2e}), "
                f"Spearman rho = {rho:.4f}, n_valid = {n_v:,}"
            )

    # ---- Method B (download_hic_regions.py style) ----
    print(f"\n  --- Method B: Point occupancy, avg_occ Kramer ---")
    arch_b = build_archcode_matrix_method_b(config)
    for k_min in [1, 2]:
        r, p, rho, rho_p, n_v = correlate_upper_triangle(arch_b, hic_norm, k_min=k_min)
        if r is not None:
            print(
                f"    k>={k_min}: Pearson r = {r:.4f} (p={p:.2e}), "
                f"Spearman rho = {rho:.4f}, n_valid = {n_v:,}"
            )

    # ---- Method B on raw (non-resized) Hi-C ----
    # This matches what download_hic_regions.py --correlate actually does
    print(f"\n  --- Method B on raw Hi-C (no resize, {hic.shape[0]}x{hic.shape[0]}) ---")
    arch_b_raw = build_archcode_matrix_method_b_native(config, hic.shape[0])
    for k_min in [1, 2]:
        r, p, rho, rho_p, n_v = correlate_upper_triangle(arch_b_raw, hic, k_min=k_min)
        if r is not None:
            print(
                f"    k>={k_min}: Pearson r = {r:.4f} (p={p:.2e}), "
                f"Spearman rho = {rho:.4f}, n_valid = {n_v:,}"
            )

    # ---- Comparison ----
    print(f"\n  --- Comparison ---")
    print(f"  Claimed r ({cell_type}): {claimed_r}")

    # Also check MCF7 if available
    mcf7_files = {
        "BRCA1": "BRCA1_MCF7_HiC_1000bp.npy",
        "TP53": "TP53_MCF7_HiC_1000bp.npy",
    }
    mcf7_file = mcf7_files.get(gene)
    if mcf7_file and (DATA_REF / mcf7_file).exists():
        mcf7 = np.load(DATA_REF / mcf7_file)
        mcf7_resized = resize_matrix(mcf7, n_bins)
        mcf7_max = mcf7_resized.max()
        if mcf7_max > 0:
            mcf7_norm = mcf7_resized / mcf7_max
            r_mcf7, p_mcf7, _, _, n_mcf7 = correlate_upper_triangle(arch_a, mcf7_norm, k_min=2)
            if r_mcf7 is not None:
                print(f"  MCF7 (Method A, k>=2): r = {r_mcf7:.4f} (p={p_mcf7:.2e}, n={n_mcf7:,})")


def build_archcode_matrix_method_b_native(config: dict, n: int) -> np.ndarray:
    """Method B but at Hi-C native resolution (no resize needed)."""
    w = config["window"]
    res_bp = (w["end"] - w["start"]) / n  # effective resolution
    start = w["start"]
    enhancers = config["features"]["enhancers"]
    ctcf_sites = config["features"]["ctcf_sites"]

    ALPHA = 0.92
    GAMMA = 0.80
    K_BASE = 0.002

    occ = np.full(n, 0.01)
    for enh in enhancers:
        b = int((enh["position"] - start) / res_bp)
        if 0 <= b < n:
            occ[b] = max(occ[b], enh["occupancy"])

    ctcf_bins = []
    for c in ctcf_sites:
        b = int((c["position"] - start) / res_bp)
        if 0 <= b < n:
            ctcf_bins.append(b)

    mat = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            d = abs(i - j)
            if d == 0:
                mat[i, j] = 1.0
                continue

            contact = (1.0 / d) * np.sqrt(occ[i] * occ[j])

            perm = 1.0
            for cb in ctcf_bins:
                if cb > i and cb < j:
                    perm *= 0.15
            contact *= perm

            avg_occ = (occ[i] + occ[j]) / 2.0
            p_unload = K_BASE * (1.0 - ALPHA * (avg_occ**GAMMA))
            contact *= 1.0 - p_unload

            mat[i, j] = contact
            mat[j, i] = contact

    return mat


def main():
    print("=" * 70)
    print("  ARCHCODE Hi-C Correlation — Independent Reproduction")
    print("  (No imports from ARCHCODE codebase)")
    print("=" * 70)

    # List available Hi-C .npy files
    print("\n  Available Hi-C reference matrices:")
    for f in sorted(DATA_REF.glob("*_HiC_*.npy")):
        arr = np.load(f)
        print(
            f"    {f.name}: shape={arr.shape}, "
            f"range=[{arr.min():.4f}, {arr.max():.4f}], "
            f"nonzero={np.count_nonzero(arr) / arr.size:.3f}"
        )

    # BRCA1 (claimed r=0.53 K562)
    analyze_locus(
        gene="BRCA1",
        config_file="brca1_400kb.json",
        hic_file="BRCA1_K562_HiC_1000bp.npy",
        claimed_r=0.5304,
        cell_type="K562",
    )

    # TP53 (claimed r=0.29 K562)
    analyze_locus(
        gene="TP53",
        config_file="tp53_300kb.json",
        hic_file="TP53_K562_HiC_1000bp.npy",
        claimed_r=0.2926,
        cell_type="K562",
    )

    # MLH1 if available
    if (DATA_REF / "MLH1_K562_HiC_1000bp.npy").exists():
        analyze_locus(
            gene="MLH1",
            config_file="mlh1_300kb.json",
            hic_file="MLH1_K562_HiC_1000bp.npy",
            claimed_r=0.5886,
            cell_type="K562",
        )

    # LDLR if available
    if (DATA_REF / "LDLR_HepG2_HiC_1000bp.npy").exists():
        analyze_locus(
            gene="LDLR",
            config_file="ldlr_300kb.json",
            hic_file="LDLR_HepG2_HiC_1000bp.npy",
            claimed_r=0.3195,
            cell_type="HepG2",
        )

    print(f"\n{'=' * 70}")
    print("  DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
