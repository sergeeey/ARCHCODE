"""
EXP-009: Genome-wide vs Focal Cohesin Loading — Ablation Study

Tests Anderson et al. 2026 (bioRxiv 10.64898/2026.01.20.700462v2):
  "Strong focal cohesin loading at enhancers is not compatible
   with their long-range regulatory functions"

Mode A: Genome-wide uniform occupancy + enhancer peaks (ARCHCODE default)
Mode B: Focal-only occupancy at enhancer positions (no background)
Mode C: Flat uniform occupancy (no enhancers, pure distance decay)

Compares all against K562 Hi-C reference (Pearson r).
"""

import json
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr
from scipy.ndimage import gaussian_filter

ROOT = Path(__file__).resolve().parent.parent

# HBB 95kb sub-TAD config
LOCUS_START = 5200000
LOCUS_END = 5295000
LOCUS_LEN = LOCUS_END - LOCUS_START  # 95000
RESOLUTION = 1000  # 1kb bins
N_BINS = LOCUS_LEN // RESOLUTION  # 95

# CTCF barriers from ENCODE K562 (ENCFF660GHM)
CTCF_SITES = [
    {"pos": 5204979, "orient": "+", "signal": 225, "name": "3primeHS1"},
    {"pos": 5280811, "orient": "-", "signal": 22, "name": "near_HS2"},
    {"pos": 5289092, "orient": "+", "signal": 21.5, "name": "near_HS4"},
    {"pos": 5291442, "orient": "-", "signal": 260, "name": "HS5"},
]

# LCR enhancers
ENHANCERS = [
    {"pos": 5226268, "occ": 0.85, "name": "HBB_promoter"},
    {"pos": 5275800, "occ": 0.4, "name": "LCR_HS1"},
    {"pos": 5280700, "occ": 0.9, "name": "LCR_HS2"},
    {"pos": 5284800, "occ": 0.7, "name": "LCR_HS3"},
    {"pos": 5288250, "occ": 0.6, "name": "LCR_HS4"},
]


def pos_to_bin(pos: int) -> int:
    return (pos - LOCUS_START) // RESOLUTION


def build_occupancy_landscape(mode: str) -> np.ndarray:
    """Build 1D occupancy landscape for given mode."""
    occ = np.zeros(N_BINS)

    if mode == "genome-wide":
        # ARCHCODE default: uniform background + Gaussian peaks at enhancers
        occ[:] = 0.1  # background occupancy
        for enh in ENHANCERS:
            b = pos_to_bin(enh["pos"])
            sigma = 3  # bins (~3kb)
            for i in range(max(0, b - 15), min(N_BINS, b + 15)):
                occ[i] += enh["occ"] * np.exp(-0.5 * ((i - b) / sigma) ** 2)

    elif mode == "focal":
        # Focal-only: NO background, only sharp peaks at enhancers
        occ[:] = 0.001  # near-zero background
        for enh in ENHANCERS:
            b = pos_to_bin(enh["pos"])
            sigma = 1.5  # sharper peaks (focal loading)
            for i in range(max(0, b - 10), min(N_BINS, b + 10)):
                occ[i] += enh["occ"] * np.exp(-0.5 * ((i - b) / sigma) ** 2)

    elif mode == "uniform":
        # Pure uniform — no enhancers at all
        occ[:] = 0.3

    # ПОЧЕМУ: clip to [0, 1] — occupancy is a probability, peaks can sum > 1.0
    return np.clip(occ, 0.0, 1.0)


def build_ctcf_barrier_matrix() -> np.ndarray:
    """Build CTCF barrier permeability factor for contact matrix."""
    perm = np.ones((N_BINS, N_BINS))
    for site in CTCF_SITES:
        b = pos_to_bin(site["pos"])
        strength = min(site["signal"] / 260, 1.0)  # normalize to strongest
        # Barrier reduces contacts across it
        for i in range(b):
            for j in range(b, N_BINS):
                perm[i, j] *= 1 - 0.7 * strength
                perm[j, i] *= 1 - 0.7 * strength
    return perm


def simulate_contact_matrix(mode: str) -> np.ndarray:
    """
    Analytical mean-field contact matrix.

    contact[i][j] = P(s) * sqrt(occ[i] * occ[j]) * CTCF_permeability

    This mirrors the logic in generate-unified-atlas.ts simulatePairedMatrices()
    """
    occ = build_occupancy_landscape(mode)
    ctcf_perm = build_ctcf_barrier_matrix()

    matrix = np.zeros((N_BINS, N_BINS))
    for i in range(N_BINS):
        for j in range(N_BINS):
            dist = abs(i - j)
            if dist == 0:
                matrix[i, j] = 1.0
            else:
                # P(s) ~ s^-1 (polymer physics distance decay)
                ps = 1.0 / dist
                # Occupancy-driven contact enrichment
                occ_factor = np.sqrt(occ[i] * occ[j])
                # CTCF barrier attenuation
                barrier = ctcf_perm[i, j]
                matrix[i, j] = ps * occ_factor * barrier

    # Normalize to [0, 1]
    matrix /= matrix.max()

    # Light smoothing (simulates finite resolution)
    matrix = gaussian_filter(matrix, sigma=0.5)

    return matrix


def upper_triangle(m: np.ndarray) -> np.ndarray:
    """Extract upper triangle (excluding diagonal)."""
    return m[np.triu_indices(m.shape[0], k=1)]


def main():
    print("=" * 60)
    print("  EXP-009: Cohesin Loading Mode Ablation")
    print("  Anderson et al. 2026 validation")
    print("=" * 60)

    # Load Hi-C reference
    hic_path = ROOT / "data" / "reference" / "HBB_K562_HiC_95kb_1000bp.npy"
    hic = None
    if hic_path.exists():
        hic_raw = np.load(str(hic_path))
        # Resize to match our bin count if needed
        if hic_raw.shape[0] != N_BINS:
            from scipy.ndimage import zoom

            factor = N_BINS / hic_raw.shape[0]
            hic = zoom(hic_raw, factor, order=1)
        else:
            hic = hic_raw
        # Normalize
        if hic.max() > 0:
            hic = hic / hic.max()
        print(f"  Hi-C loaded: {hic.shape} (from {hic_raw.shape})")
    else:
        print(f"  Hi-C not found at {hic_path}")

    # Simulate three modes
    modes = ["genome-wide", "focal", "uniform"]
    matrices = {}
    for mode in modes:
        m = simulate_contact_matrix(mode)
        matrices[mode] = m
        occ = build_occupancy_landscape(mode)
        print(f"\n  Mode '{mode}':")
        print(f"    Occupancy: mean={occ.mean():.4f}, max={occ.max():.4f}")
        print(f"    Matrix: mean={m.mean():.6f}, max={m.max():.4f}")

    # Correlations
    print("\n" + "─" * 60)
    print("  Correlation analysis")
    print("─" * 60)

    gw_flat = upper_triangle(matrices["genome-wide"])
    focal_flat = upper_triangle(matrices["focal"])
    uniform_flat = upper_triangle(matrices["uniform"])

    r_gw_focal, p_gw_focal = pearsonr(gw_flat, focal_flat)
    r_gw_uniform, _ = pearsonr(gw_flat, uniform_flat)
    r_focal_uniform, _ = pearsonr(focal_flat, uniform_flat)

    print(f"  Genome-wide vs Focal:   r = {r_gw_focal:.4f} (p = {p_gw_focal:.2e})")
    print(f"  Genome-wide vs Uniform: r = {r_gw_uniform:.4f}")
    print(f"  Focal vs Uniform:       r = {r_focal_uniform:.4f}")

    results = {
        "experiment": "EXP-009",
        "title": "Cohesin Loading Mode Ablation",
        "reference": "Anderson et al. 2026 (bioRxiv 10.64898/2026.01.20.700462v2)",
        "locus": f"HBB 95kb sub-TAD (chr11:{LOCUS_START}-{LOCUS_END})",
        "resolution_bp": RESOLUTION,
        "n_bins": N_BINS,
        "anderson_key_finding": "~75% of cohesin is engaged in genome-wide extrusion; focal loading at enhancers inhibits transcription",
    }

    if hic is not None:
        hic_flat = upper_triangle(hic)

        r_A, p_A = pearsonr(gw_flat, hic_flat)
        r_B, p_B = pearsonr(focal_flat, hic_flat)
        r_C, p_C = pearsonr(uniform_flat, hic_flat)

        print(f"\n  vs K562 Hi-C:")
        print(f"    Mode A (genome-wide): r = {r_A:.4f} (p = {p_A:.2e})")
        print(f"    Mode B (focal):       r = {r_B:.4f} (p = {p_B:.2e})")
        print(f"    Mode C (uniform):     r = {r_C:.4f} (p = {p_C:.2e})")
        print(f"\n    Δr (A - B) = {r_A - r_B:.4f}")
        print(f"    Δr (A - C) = {r_A - r_C:.4f}")

        if r_A > r_B:
            verdict = "CONFIRMED"
            print(f"\n  ✅ Genome-wide loading BETTER than focal (Δr = +{r_A - r_B:.4f})")
            print(f"     Consistent with Anderson et al. 2026")
        else:
            verdict = "NOT_CONFIRMED"
            print(f"\n  ⚠️ Focal loading shows higher Hi-C correlation")

        results.update(
            {
                "mode_A_genome_wide": {
                    "description": "Uniform background + Gaussian enhancer peaks (ARCHCODE default)",
                    "hi_c_r": round(r_A, 4),
                    "hi_c_p": float(f"{p_A:.2e}"),
                },
                "mode_B_focal": {
                    "description": "Near-zero background + sharp enhancer peaks only",
                    "hi_c_r": round(r_B, 4),
                    "hi_c_p": float(f"{p_B:.2e}"),
                },
                "mode_C_uniform": {
                    "description": "Flat uniform occupancy, no enhancers",
                    "hi_c_r": round(r_C, 4),
                    "hi_c_p": float(f"{p_C:.2e}"),
                },
                "delta_r_A_minus_B": round(r_A - r_B, 4),
                "delta_r_A_minus_C": round(r_A - r_C, 4),
                "verdict": verdict,
                "conclusion": (
                    f"Genome-wide loading (r={r_A:.3f}) outperforms focal loading (r={r_B:.3f}) "
                    f"by Δr={r_A - r_B:.4f}, consistent with Anderson et al. 2026."
                    if r_A > r_B
                    else f"Unexpected: focal loading (r={r_B:.3f}) >= genome-wide (r={r_A:.3f})."
                ),
            }
        )
    else:
        results.update(
            {
                "note": "Hi-C reference not available — inter-model comparison only",
                "inter_model": {
                    "genome_wide_vs_focal": round(r_gw_focal, 4),
                    "genome_wide_vs_uniform": round(r_gw_uniform, 4),
                    "focal_vs_uniform": round(r_focal_uniform, 4),
                },
            }
        )

    out_path = ROOT / "analysis" / "exp009_loading_mode_ablation.json"
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n  💾 Saved: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
