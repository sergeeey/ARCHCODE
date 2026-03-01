#!/usr/bin/env python3
"""
ARCHCODE TDA Proof-of-Concept — Topological Data Analysis of Contact Matrices

ПОЧЕМУ TDA: SSIM измеряет пиксельную разницу между матрицами, но не улавливает
топологические изменения (появление/исчезновение петель, слияние доменов).
Persistent homology через ripser даёт метрику формы: persistence diagrams
показывают рождение и смерть топологических features (connected components,
loops, voids). Если патогенные варианты систематически изменяют persistence
landscape — это новый, ортогональный к SSIM, маркер патогенности.

Usage:
    python scripts/tda_proof_of_concept.py [--locus 95kb|30kb|cftr]
"""

import numpy as np
import json
import sys
import os
from pathlib import Path

# ПОЧЕМУ: ripser работает с distance matrices. Контактная матрица — это
# similarity matrix, нужно конвертировать: distance = 1 - contact
try:
    from ripser import ripser
    from persim import plot_diagrams, wasserstein, bottleneck
except ImportError:
    print("ERROR: pip install ripser persim")
    sys.exit(1)

# ============================================================================
# ARCHCODE analytical engine (Python port of simulatePairedMatrices)
# ============================================================================

def load_locus_config(locus_name: str) -> dict:
    """Load locus config JSON and flatten to standard keys."""
    config_map = {
        "30kb": "config/locus/hbb_30kb_v2.json",
        "95kb": "config/locus/hbb_95kb_subTAD.json",
        "cftr": "config/locus/cftr_317kb.json",
        "tp53": "config/locus/tp53_300kb.json",
        "brca1": "config/locus/brca1_400kb.json",
    }
    config_path = Path(config_map.get(locus_name, f"config/locus/{locus_name}.json"))
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path) as f:
        raw = json.load(f)

    # ПОЧЕМУ flatten: конфиги имеют вложенную структуру window.n_bins,
    # features.enhancers. Для удобства вытаскиваем в плоский dict.
    window = raw.get("window", {})
    features = raw.get("features", {})
    return {
        "id": raw.get("id", locus_name),
        "n_bins": window.get("n_bins", 50),
        "resolution": window.get("resolution_bp", 600),
        "genomic_start": window.get("start", 0),
        "genomic_end": window.get("end", 0),
        "enhancers": features.get("enhancers", []),
        "ctcf_sites": features.get("ctcf_sites", []),
    }


def build_contact_matrix(
    config: dict,
    variant_bin: int = -1,
    effect_strength: float = 1.0,
    category: str = "",
    seed: int = 2026,
) -> np.ndarray:
    """
    Build analytical contact matrix (Python port of TypeScript engine).
    Returns NxN numpy array normalized to [0,1].
    """
    n_bins = config["n_bins"]
    resolution = config["resolution"]
    sim_start = config["genomic_start"]

    # Kramer kinetics params
    K_BASE = 0.002
    ALPHA = 0.92
    GAMMA = 0.80
    BG_OCC = 0.05

    # Build MED1 occupancy landscape
    rng = np.random.RandomState(seed)
    occupancy = np.full(n_bins, BG_OCC) + rng.random(n_bins) * 0.05

    for enh in config.get("enhancers", []):
        for i in range(n_bins):
            genomic_pos = sim_start + i * resolution
            dist = abs(genomic_pos - enh["position"]) / resolution
            if dist < 5:
                occupancy[i] += enh["occupancy"] * np.exp(-0.5 * dist * dist)

    occupancy = np.clip(occupancy, 0, 1)

    # Apply variant perturbation
    mut_occupancy = occupancy.copy()
    if variant_bin >= 0:
        for i in range(n_bins):
            dist = abs(i - variant_bin)
            if dist < 3:
                reduction = effect_strength + (1 - effect_strength) * (dist / 3)
                mut_occupancy[i] = occupancy[i] * reduction

    # CTCF barriers
    ctcf_bins = []
    for c in config.get("ctcf_sites", []):
        b = int((c["position"] - sim_start) / resolution)
        if 0 <= b < n_bins:
            ctcf_bins.append(b)

    # Analytical contact map
    matrix = np.zeros((n_bins, n_bins))
    occ = mut_occupancy if variant_bin >= 0 else occupancy

    for i in range(n_bins):
        for j in range(i + 1, n_bins):
            dist = j - i
            dist_factor = dist ** (-1.0)
            occ_factor = np.sqrt(occ[i] * occ[j])

            perm = 1.0
            for ctcf in ctcf_bins:
                if i < ctcf < j:
                    perm *= 0.15

            kramer = 1 - K_BASE * (1 - ALPHA * max(0.001, occ_factor) ** GAMMA)

            matrix[i, j] = dist_factor * occ_factor * perm * kramer
            matrix[j, i] = matrix[i, j]

    # Normalize
    max_val = matrix.max()
    if max_val > 0:
        matrix /= max_val

    return matrix


# ============================================================================
# TDA Functions
# ============================================================================

def contact_to_distance(contact_matrix: np.ndarray) -> np.ndarray:
    """
    Convert contact (similarity) matrix to distance matrix for ripser.
    ПОЧЕМУ 1-C: контактная матрица — similarity (высокое = близко).
    Ripser ожидает distance (высокое = далеко). Простое преобразование d=1-c
    сохраняет метрическую структуру для [0,1]-нормализованных матриц.
    """
    return 1.0 - contact_matrix


def compute_persistence(distance_matrix: np.ndarray, maxdim: int = 1) -> dict:
    """
    Compute persistent homology via ripser.
    maxdim=1 даёт H0 (connected components) и H1 (loops/cycles).
    H0 показывает кластеризацию доменов, H1 — наличие замкнутых петель.
    """
    result = ripser(distance_matrix, maxdim=maxdim, distance_matrix=True)
    return result


def persistence_summary(dgms: list) -> dict:
    """
    Extract summary statistics from persistence diagrams.
    ПОЧЕМУ эти метрики:
    - total_persistence: суммарная "длительность жизни" всех features
    - max_persistence: самая долгоживущая feature (доминантная структура)
    - n_features: количество topological features
    - entropy: Shannon entropy of lifetimes (diversity структуры)
    """
    summary = {}
    dim_names = ["H0_components", "H1_loops"]

    for dim, name in enumerate(dim_names):
        if dim >= len(dgms):
            summary[name] = {
                "n_features": 0,
                "total_persistence": 0.0,
                "max_persistence": 0.0,
                "mean_persistence": 0.0,
                "entropy": 0.0,
            }
            continue

        dgm = dgms[dim]
        # Filter out infinite death times (H0 has one infinite component)
        finite = dgm[np.isfinite(dgm[:, 1])]
        lifetimes = finite[:, 1] - finite[:, 0] if len(finite) > 0 else np.array([])
        lifetimes = lifetimes[lifetimes > 1e-10]  # filter noise

        if len(lifetimes) == 0:
            summary[name] = {
                "n_features": 0,
                "total_persistence": 0.0,
                "max_persistence": 0.0,
                "mean_persistence": 0.0,
                "entropy": 0.0,
            }
            continue

        total = lifetimes.sum()
        probs = lifetimes / total if total > 0 else np.ones_like(lifetimes)
        entropy = -np.sum(probs * np.log(probs + 1e-15))

        summary[name] = {
            "n_features": int(len(lifetimes)),
            "total_persistence": float(total),
            "max_persistence": float(lifetimes.max()),
            "mean_persistence": float(lifetimes.mean()),
            "entropy": float(entropy),
        }

    return summary


def compute_landscape_vector(dgm: np.ndarray, n_points: int = 100) -> np.ndarray:
    """
    Compute persistence landscape (vectorized summary).
    ПОЧЕМУ landscape: persistence diagrams нельзя напрямую сравнивать
    как векторы. Landscape преобразует diagram в функцию, которую можно
    усреднять, вычитать и использовать в ML.
    """
    finite = dgm[np.isfinite(dgm[:, 1])]
    if len(finite) == 0:
        return np.zeros(n_points)

    births = finite[:, 0]
    deaths = finite[:, 1]

    t_min = births.min()
    t_max = deaths.max()
    t_range = np.linspace(t_min, t_max, n_points)

    landscape = np.zeros(n_points)
    for b, d in zip(births, deaths):
        mid = (b + d) / 2
        height = (d - b) / 2
        tent = np.maximum(0, height - np.abs(t_range - mid))
        landscape = np.maximum(landscape, tent)

    return landscape


# ============================================================================
# Effect strength mapping (same as TypeScript engine)
# ============================================================================

EFFECT_STRENGTHS = {
    "nonsense": 0.1,
    "frameshift": 0.15,
    "splice_donor": 0.2,
    "splice_acceptor": 0.2,
    "splice_region": 0.5,
    "missense": 0.4,
    "promoter": 0.3,
    "5_prime_UTR": 0.6,
    "3_prime_UTR": 0.7,
    "intronic": 0.8,
    "synonymous": 0.9,
    "other": 0.5,
}


# ============================================================================
# Main Analysis
# ============================================================================

def main():
    locus = "95kb"
    if "--locus" in sys.argv:
        idx = sys.argv.index("--locus")
        locus = sys.argv[idx + 1]

    print(f"=== ARCHCODE TDA Proof-of-Concept ===")
    print(f"Locus: {locus}")

    config = load_locus_config(locus)
    n_bins = config["n_bins"]
    resolution = config["resolution"]
    sim_start = config["genomic_start"]
    print(f"Matrix size: {n_bins}x{n_bins}, resolution: {resolution} bp")

    # Step 1: Wild-type contact matrix
    print("\n--- Step 1: Wild-type persistence ---")
    wt_matrix = build_contact_matrix(config)
    wt_dist = contact_to_distance(wt_matrix)
    wt_result = compute_persistence(wt_dist, maxdim=1)
    wt_summary = persistence_summary(wt_result["dgms"])
    print(f"  H0 (components): {wt_summary['H0_components']['n_features']} features, "
          f"total persistence = {wt_summary['H0_components']['total_persistence']:.4f}")
    print(f"  H1 (loops): {wt_summary['H1_loops']['n_features']} features, "
          f"total persistence = {wt_summary['H1_loops']['total_persistence']:.4f}")

    # Step 2: Simulate representative variants across categories
    print("\n--- Step 2: Variant persistence comparison ---")

    # Pick representative positions for each category
    test_categories = ["nonsense", "frameshift", "splice_donor", "promoter",
                       "missense", "intronic", "synonymous"]

    # Use center of gene as variant position (HBB-specific for 95kb)
    if locus in ("95kb", "30kb"):
        variant_genomic = 5226270  # HBB codon 39
    else:
        variant_genomic = config["genomic_start"] + (config["genomic_end"] - config["genomic_start"]) // 2

    variant_bin = int((variant_genomic - sim_start) / resolution)
    variant_bin = max(0, min(n_bins - 1, variant_bin))
    print(f"  Variant bin: {variant_bin} (genomic: {variant_genomic})")

    results = []
    wt_landscape_h1 = compute_landscape_vector(wt_result["dgms"][1])

    for cat in test_categories:
        eff = EFFECT_STRENGTHS.get(cat, 0.5)
        mut_matrix = build_contact_matrix(config, variant_bin, eff, cat)
        mut_dist = contact_to_distance(mut_matrix)
        mut_result = compute_persistence(mut_dist, maxdim=1)
        mut_summary = persistence_summary(mut_result["dgms"])

        # SSIM (for comparison)
        flat_wt = wt_matrix[np.triu_indices(n_bins, k=1)]
        flat_mut = mut_matrix[np.triu_indices(n_bins, k=1)]
        mu_a, mu_b = flat_wt.mean(), flat_mut.mean()
        sig_a2 = ((flat_wt - mu_a) ** 2).mean()
        sig_b2 = ((flat_mut - mu_b) ** 2).mean()
        sig_ab = ((flat_wt - mu_a) * (flat_mut - mu_b)).mean()
        c1, c2 = 0.0001, 0.0009
        ssim = ((2 * mu_a * mu_b + c1) * (2 * sig_ab + c2)) / \
               ((mu_a**2 + mu_b**2 + c1) * (sig_a2 + sig_b2 + c2))

        # Wasserstein distance between persistence diagrams
        w_h0 = wasserstein(wt_result["dgms"][0], mut_result["dgms"][0])
        w_h1 = wasserstein(wt_result["dgms"][1], mut_result["dgms"][1])

        # Bottleneck distance
        b_h0 = bottleneck(wt_result["dgms"][0], mut_result["dgms"][0])
        b_h1 = bottleneck(wt_result["dgms"][1], mut_result["dgms"][1])

        # Landscape distance
        mut_landscape_h1 = compute_landscape_vector(mut_result["dgms"][1])
        landscape_dist = np.linalg.norm(wt_landscape_h1 - mut_landscape_h1)

        row = {
            "category": cat,
            "effect_strength": eff,
            "ssim": round(ssim, 6),
            "wasserstein_h0": round(w_h0, 6),
            "wasserstein_h1": round(w_h1, 6),
            "bottleneck_h0": round(b_h0, 6),
            "bottleneck_h1": round(b_h1, 6),
            "landscape_dist_h1": round(landscape_dist, 6),
            "h1_n_features_wt": wt_summary["H1_loops"]["n_features"],
            "h1_n_features_mut": mut_summary["H1_loops"]["n_features"],
            "h1_total_pers_wt": round(wt_summary["H1_loops"]["total_persistence"], 6),
            "h1_total_pers_mut": round(mut_summary["H1_loops"]["total_persistence"], 6),
        }
        results.append(row)

        print(f"  {cat:16s} | eff={eff:.2f} | SSIM={ssim:.4f} | "
              f"W_H1={w_h1:.6f} | B_H1={b_h1:.6f} | L_H1={landscape_dist:.6f}")

    # Step 3: Correlation analysis — does TDA rank correlate with SSIM rank?
    print("\n--- Step 3: Rank correlation (TDA vs SSIM) ---")
    from scipy.stats import spearmanr

    ssim_vals = [r["ssim"] for r in results]
    w_h1_vals = [r["wasserstein_h1"] for r in results]
    b_h1_vals = [r["bottleneck_h1"] for r in results]
    l_h1_vals = [r["landscape_dist_h1"] for r in results]

    # Lower SSIM = more disruption, Higher Wasserstein = more disruption
    # So we expect negative correlation
    rho_w, p_w = spearmanr(ssim_vals, w_h1_vals)
    rho_b, p_b = spearmanr(ssim_vals, b_h1_vals)
    rho_l, p_l = spearmanr(ssim_vals, l_h1_vals)

    print(f"  SSIM vs Wasserstein H1: rho = {rho_w:.4f}, p = {p_w:.4f}")
    print(f"  SSIM vs Bottleneck  H1: rho = {rho_b:.4f}, p = {p_b:.4f}")
    print(f"  SSIM vs Landscape   H1: rho = {rho_l:.4f}, p = {rho_l:.4f}")

    # Step 4: Multi-position scan — test TDA sensitivity across genome
    print("\n--- Step 4: Positional scan (nonsense at every 10th bin) ---")
    scan_results = []
    for bin_pos in range(0, n_bins, max(1, n_bins // 15)):
        mut_matrix = build_contact_matrix(config, bin_pos, 0.1, "nonsense")
        mut_dist = contact_to_distance(mut_matrix)
        mut_result = compute_persistence(mut_dist, maxdim=1)

        flat_wt = wt_matrix[np.triu_indices(n_bins, k=1)]
        flat_mut = mut_matrix[np.triu_indices(n_bins, k=1)]
        mu_a, mu_b = flat_wt.mean(), flat_mut.mean()
        sig_a2 = ((flat_wt - mu_a) ** 2).mean()
        sig_b2 = ((flat_mut - mu_b) ** 2).mean()
        sig_ab = ((flat_wt - mu_a) * (flat_mut - mu_b)).mean()
        c1, c2 = 0.0001, 0.0009
        ssim = ((2 * mu_a * mu_b + c1) * (2 * sig_ab + c2)) / \
               ((mu_a**2 + mu_b**2 + c1) * (sig_a2 + sig_b2 + c2))

        w_h1 = wasserstein(wt_result["dgms"][1], mut_result["dgms"][1])

        scan_results.append({
            "bin": bin_pos,
            "genomic_pos": sim_start + bin_pos * resolution,
            "ssim": round(ssim, 6),
            "wasserstein_h1": round(w_h1, 6),
        })

    ssim_scan = [r["ssim"] for r in scan_results]
    w_scan = [r["wasserstein_h1"] for r in scan_results]
    rho_scan, p_scan = spearmanr(ssim_scan, w_scan)
    print(f"  Positional scan: {len(scan_results)} positions")
    print(f"  SSIM range: {min(ssim_scan):.4f} — {max(ssim_scan):.4f}")
    print(f"  Wasserstein H1 range: {min(w_scan):.6f} — {max(w_scan):.6f}")
    print(f"  SSIM vs W_H1 positional: rho = {rho_scan:.4f}, p = {p_scan:.6f}")

    # Step 5: Save results
    output = {
        "analysis": "ARCHCODE TDA proof-of-concept",
        "locus": locus,
        "n_bins": n_bins,
        "resolution": resolution,
        "wt_persistence": wt_summary,
        "variant_comparison": results,
        "rank_correlations": {
            "ssim_vs_wasserstein_h1": {"rho": round(rho_w, 4), "p": round(p_w, 4)},
            "ssim_vs_bottleneck_h1": {"rho": round(rho_b, 4), "p": round(p_b, 4)},
            "ssim_vs_landscape_h1": {"rho": round(rho_l, 4), "p": round(p_l, 4)},
        },
        "positional_scan": {
            "n_positions": len(scan_results),
            "ssim_range": [min(ssim_scan), max(ssim_scan)],
            "wasserstein_h1_range": [min(w_scan), max(w_scan)],
            "positional_rho": round(rho_scan, 4),
            "positional_p": round(p_scan, 6),
        },
        "scan_data": scan_results,
        "interpretation": "",
    }

    # Save
    out_path = f"results/tda_proof_of_concept_{locus}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {out_path}")

    # Step 6: Generate visualization
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Panel A: WT persistence diagram
        ax = axes[0, 0]
        for dim, (dgm, label, color) in enumerate(
            zip(wt_result["dgms"], ["H0", "H1"], ["blue", "red"])
        ):
            finite = dgm[np.isfinite(dgm[:, 1])]
            if len(finite) > 0:
                ax.scatter(finite[:, 0], finite[:, 1], s=10, alpha=0.5,
                          color=color, label=f"{label} ({len(finite)} features)")
        lim = ax.get_xlim()[1]
        ax.plot([0, lim], [0, lim], "k--", alpha=0.3, linewidth=0.5)
        ax.set_xlabel("Birth")
        ax.set_ylabel("Death")
        ax.set_title("Wild-type persistence diagram")
        ax.legend(fontsize=8)

        # Panel B: TDA vs SSIM by category
        ax = axes[0, 1]
        categories = [r["category"] for r in results]
        ssim_v = [1 - r["ssim"] for r in results]  # disruption = 1-SSIM
        w_h1_v = [r["wasserstein_h1"] for r in results]
        ax.barh(range(len(categories)), ssim_v, height=0.4, align="edge",
                label="1 - SSIM", color="steelblue", alpha=0.7)
        ax.barh([x - 0.4 for x in range(len(categories))], w_h1_v, height=0.4,
                align="edge", label="Wasserstein H1", color="coral", alpha=0.7)
        ax.set_yticks(range(len(categories)))
        ax.set_yticklabels(categories, fontsize=8)
        ax.set_xlabel("Disruption magnitude")
        ax.set_title("SSIM vs TDA disruption by category")
        ax.legend(fontsize=8)

        # Panel C: Positional scan
        ax = axes[1, 0]
        positions = [r["bin"] for r in scan_results]
        ax.plot(positions, [1 - r["ssim"] for r in scan_results],
                "b-", label="1 - SSIM", alpha=0.7)
        ax2 = ax.twinx()
        ax2.plot(positions, [r["wasserstein_h1"] for r in scan_results],
                 "r-", label="Wasserstein H1", alpha=0.7)
        ax.set_xlabel("Bin position")
        ax.set_ylabel("1 - SSIM", color="blue")
        ax2.set_ylabel("Wasserstein H1", color="red")
        ax.set_title(f"Positional scan (nonsense, rho={rho_scan:.3f})")

        # Panel D: Landscape comparison
        ax = axes[1, 1]
        ax.plot(wt_landscape_h1, "k-", label="Wild-type", linewidth=2)
        for cat in ["nonsense", "synonymous"]:
            eff = EFFECT_STRENGTHS[cat]
            mut_m = build_contact_matrix(config, variant_bin, eff, cat)
            mut_d = contact_to_distance(mut_m)
            mut_r = compute_persistence(mut_d, maxdim=1)
            mut_l = compute_landscape_vector(mut_r["dgms"][1])
            ax.plot(mut_l, label=cat, alpha=0.7)
        ax.set_xlabel("Landscape index")
        ax.set_ylabel("Amplitude")
        ax.set_title("Persistence landscape (H1)")
        ax.legend(fontsize=8)

        plt.tight_layout()
        plot_path = f"plots/tda_proof_of_concept_{locus}.png"
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        print(f"Plot saved: {plot_path}")
        plt.close()

    except Exception as e:
        print(f"Plot generation failed: {e}")

    # Interpretation
    if abs(rho_w) > 0.7:
        interp = (
            "STRONG correlation between SSIM and TDA metrics. TDA captures "
            "similar structural information as SSIM but in topological space. "
            "Potential value: TDA may detect topological changes (loop merging, "
            "domain splitting) that SSIM misses as pixel-level perturbations."
        )
    elif abs(rho_w) > 0.4:
        interp = (
            "MODERATE correlation. TDA and SSIM capture partially overlapping "
            "structural information. This is the ideal scenario: TDA adds "
            "complementary topological signal beyond SSIM pixel comparison."
        )
    else:
        interp = (
            "WEAK correlation. TDA and SSIM measure fundamentally different "
            "aspects of structural disruption. TDA may provide orthogonal "
            "information, or may be insensitive to the perturbation scale."
        )
    output["interpretation"] = interp
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nInterpretation: {interp}")


if __name__ == "__main__":
    main()
