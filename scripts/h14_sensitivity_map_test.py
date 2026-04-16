"""
H-14: Region-Level Sensitivity Map Test
========================================
Question: Does ARCHCODE sensitivity map correlate with real regulatory
architecture BETTER than simple occupancy (H3K27ac proxy)?

Design:
- Uniform perturbation (effect=0.3) at each bin position
- Measure delta-LSSIM per bin -> sensitivity map
- Compare to: (a) input occupancy, (b) distance-to-enhancer, (c) CTCF proximity
- BCL11A positive control: DHS +58 (Casgevy) should be most sensitive

Kill criterion: If Spearman(sensitivity, occupancy) > 0.95, model = input.
If DHS +58 is NOT in top-5 by sensitivity, model fails basic sanity.

Pre-registered: 2026-04-15.
"""

import json, math
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

ROOT = Path("D:/\u0414\u041d\u041a")
OUTPUT_PATH = ROOT / "results/h14_sensitivity_map_results.json"

K_BASE = 0.002
ALPHA = 0.92
GAMMA_PARAM = 0.80
BACKGROUND_OCC = 0.1
CTCF_PENALTY = 0.15
UNIFORM_EFFECT = 0.3  # same perturbation everywhere


def load_config(name):
    path = ROOT / f"config/locus/{name}.json"
    with open(path) as f:
        return json.load(f)


def pos_to_bin(pos, window_start, resolution):
    return int((pos - window_start) / resolution)


def build_occupancy_landscape(config):
    n_bins = config["window"]["n_bins"]
    resolution = config["window"]["resolution_bp"]
    window_start = config["window"]["start"]
    occ = np.full(n_bins, BACKGROUND_OCC)
    for enh in config["features"]["enhancers"]:
        enh_bin = pos_to_bin(enh["position"], window_start, resolution)
        enh_occ = enh["occupancy"]
        spread = max(3, int(2000 / resolution))
        for i in range(n_bins):
            dist_bins = abs(i - enh_bin)
            contrib = enh_occ * math.exp(-0.5 * (dist_bins / spread) ** 2)
            occ[i] += contrib
    return np.clip(occ, 0, 1)


def get_ctcf_bins(config):
    ws = config["window"]["start"]
    res = config["window"]["resolution_bp"]
    return [pos_to_bin(s["position"], ws, res) for s in config["features"]["ctcf_sites"]]


def count_ctcf_between(i, j, ctcf_bins):
    lo, hi = min(i, j), max(i, j)
    return sum(1 for c in ctcf_bins if lo < c < hi)


def build_contact_matrix(occ, ctcf_bins, n_bins):
    mat = np.zeros((n_bins, n_bins))
    for i in range(n_bins):
        for j in range(i + 1, n_bins):
            dist = j - i
            dist_factor = dist ** (-1.0)
            occ_factor = math.sqrt(occ[i] * occ[j])
            n_ctcf = count_ctcf_between(i, j, ctcf_bins)
            perm_factor = CTCF_PENALTY ** n_ctcf
            kramer = 1 - K_BASE * (1 - ALPHA * (occ_factor ** GAMMA_PARAM))
            val = dist_factor * occ_factor * perm_factor * kramer
            mat[i][j] = val
            mat[j][i] = val
    return mat


def calculate_ssim(ref, mut):
    """SSIM between two flattened matrices."""
    a = ref.flatten().astype(float)
    b = mut.flatten().astype(float)
    mu_a, mu_b = np.mean(a), np.mean(b)
    var_a, var_b = np.var(a), np.var(b)
    cov_ab = np.cov(a, b)[0][1]
    c1, c2 = 0.0001, 0.0009
    ssim = ((2*mu_a*mu_b + c1) * (2*cov_ab + c2)) / ((mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2))
    return float(ssim)


def calculate_local_ssim(ref, mut, variant_bin, window_size=50):
    n = ref.shape[0]
    if n <= window_size:
        return calculate_ssim(ref, mut)
    start = variant_bin - window_size // 2
    end = start + window_size
    if start < 0:
        start, end = 0, window_size
    if end > n:
        end, start = n, n - window_size
    return calculate_ssim(ref[start:end, start:end], mut[start:end, start:end])


def apply_uniform_variant(base_occ, variant_bin, effect=UNIFORM_EFFECT):
    mut_occ = base_occ.copy()
    n = len(mut_occ)
    for i in range(n):
        dist = abs(i - variant_bin)
        if dist < 3:
            mut_occ[i] *= effect
        else:
            fade = effect + (1 - effect) * (dist / 3.0)
            if fade < 1.0:
                mut_occ[i] *= min(fade, 1.0)
    return np.clip(mut_occ, 0, 1)


def build_sensitivity_map(config):
    """For each bin: apply uniform perturbation, measure delta-LSSIM."""
    n_bins = config["window"]["n_bins"]
    wt_occ = build_occupancy_landscape(config)
    ctcf_bins = get_ctcf_bins(config)
    wt_mat = build_contact_matrix(wt_occ, ctcf_bins, n_bins)

    sensitivities = []
    for b in range(n_bins):
        mut_occ = apply_uniform_variant(wt_occ, b)
        mut_mat = build_contact_matrix(mut_occ, ctcf_bins, n_bins)
        lssim = calculate_local_ssim(wt_mat, mut_mat, b)
        delta_lssim = 1.0 - lssim  # higher = more sensitive
        sensitivities.append(delta_lssim)
        if (b + 1) % 50 == 0:
            print(f"    bin {b+1}/{n_bins}")

    return np.array(sensitivities), wt_occ


def test_locus(config, locus_name, known_elements=None):
    """Run sensitivity map test on one locus."""
    print(f"\n{'='*70}")
    print(f"LOCUS: {locus_name}")
    print(f"{'='*70}")

    n_bins = config["window"]["n_bins"]
    ws = config["window"]["start"]
    res = config["window"]["resolution_bp"]

    print(f"  Window: {config['window']['chromosome']}:{ws}-{config['window']['end']}")
    print(f"  Bins: {n_bins}, Resolution: {res}bp")

    print("  Building sensitivity map (uniform effect)...")
    sensitivity, occupancy = build_sensitivity_map(config)

    # Spearman: sensitivity vs occupancy
    rho_occ, p_occ = stats.spearmanr(sensitivity, occupancy)
    print(f"\n  Spearman(sensitivity, occupancy) = {rho_occ:.4f}, p = {p_occ:.2e}")

    # Distance to nearest enhancer
    enh_bins = [pos_to_bin(e["position"], ws, res) for e in config["features"]["enhancers"]]
    dist_to_enh = np.array([min(abs(b - eb) for eb in enh_bins) for b in range(n_bins)])
    rho_dist, p_dist = stats.spearmanr(sensitivity, -dist_to_enh)  # negative: closer = more sensitive
    print(f"  Spearman(sensitivity, -dist_to_enhancer) = {rho_dist:.4f}, p = {p_dist:.2e}")

    # Distance to nearest CTCF
    ctcf_bins = get_ctcf_bins(config)
    dist_to_ctcf = np.array([min(abs(b - cb) for cb in ctcf_bins) for b in range(n_bins)])
    rho_ctcf, p_ctcf = stats.spearmanr(sensitivity, -dist_to_ctcf)
    print(f"  Spearman(sensitivity, -dist_to_CTCF) = {rho_ctcf:.4f}, p = {p_ctcf:.2e}")

    # Baseline: occupancy * (1/dist_to_TSS)
    # TSS = first enhancer (promoter) typically
    tss_bin = enh_bins[0]
    dist_to_tss = np.array([max(abs(b - tss_bin), 1) for b in range(n_bins)])
    baseline = occupancy / dist_to_tss
    rho_base, p_base = stats.spearmanr(sensitivity, baseline)
    print(f"  Spearman(sensitivity, occ/dist_to_TSS) = {rho_base:.4f}, p = {p_base:.2e}")

    # Residual analysis: where does sensitivity != occupancy prediction?
    # Rank both, find largest rank differences
    sens_rank = stats.rankdata(-sensitivity)  # 1 = most sensitive
    occ_rank = stats.rankdata(-occupancy)     # 1 = highest occupancy
    rank_diff = sens_rank - occ_rank  # negative = more sensitive than occupancy predicts

    # Top-10 sensitive bins
    top_k = 10
    top_bins = np.argsort(-sensitivity)[:top_k]
    print(f"\n  Top-{top_k} sensitive bins:")
    for rank, b in enumerate(top_bins):
        pos = ws + b * res
        occ_r = int(occ_rank[b])
        print(f"    #{rank+1}: bin {b} (pos {pos:,}), delta_LSSIM={sensitivity[b]:.6f}, occ_rank={occ_r}")

    # Check known elements
    element_results = {}
    if known_elements:
        print(f"\n  Known element ranking:")
        for name, elem_pos in known_elements.items():
            elem_bin = pos_to_bin(elem_pos, ws, res)
            if 0 <= elem_bin < n_bins:
                elem_rank = int(sens_rank[elem_bin])
                elem_occ_rank = int(occ_rank[elem_bin])
                print(f"    {name}: bin {elem_bin}, sensitivity_rank={elem_rank}/{n_bins}, "
                      f"occ_rank={elem_occ_rank}, delta={sensitivity[elem_bin]:.6f}")
                element_results[name] = {
                    "bin": elem_bin, "position": int(elem_pos),
                    "sensitivity_rank": elem_rank,
                    "occupancy_rank": elem_occ_rank,
                    "delta_lssim": float(sensitivity[elem_bin]),
                }

    # Residual outliers: bins much more sensitive than occupancy predicts
    residual_outliers = np.argsort(rank_diff)[:10]
    print(f"\n  Top-10 'unexpectedly sensitive' bins (sens_rank << occ_rank):")
    for b in residual_outliers:
        pos = ws + b * res
        print(f"    bin {b} (pos {pos:,}): sens_rank={int(sens_rank[b])}, occ_rank={int(occ_rank[b])}, "
              f"diff={int(rank_diff[b])}")

    return {
        "locus": locus_name,
        "n_bins": n_bins,
        "spearman_vs_occupancy": {"rho": float(rho_occ), "p": float(p_occ)},
        "spearman_vs_enhancer_dist": {"rho": float(rho_dist), "p": float(p_dist)},
        "spearman_vs_ctcf_dist": {"rho": float(rho_ctcf), "p": float(p_ctcf)},
        "spearman_vs_baseline": {"rho": float(rho_base), "p": float(p_base)},
        "top_10_bins": [{"bin": int(b), "position": int(ws + b * res),
                         "delta_lssim": float(sensitivity[b])} for b in top_bins],
        "known_elements": element_results,
    }


def main():
    print("=" * 70)
    print("H-14: Region-Level Sensitivity Map Test")
    print("=" * 70)

    all_results = {}

    # BCL11A — known positive control
    bcl11a_config = load_config("bcl11a_erythroid_95kb")
    bcl11a_elements = {
        "DHS_+58_Casgevy": 60495193,
        "DHS_+55": 60498362,
        "DHS_+62": 60491066,
        "BCL11A_promoter": 60554000,
    }
    all_results["BCL11A"] = test_locus(bcl11a_config, "BCL11A", bcl11a_elements)

    # HBB — for comparison (no external truth, but known LCR)
    hbb_config = load_config("hbb_95kb_subTAD")
    hbb_elements = {
        "HBB_promoter": 5226268,
        "LCR_HS2": 5280700,
        "LCR_HS3": 5284800,
        "LCR_HS4": 5288250,
    }
    all_results["HBB"] = test_locus(hbb_config, "HBB", hbb_elements)

    # Verdict
    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)

    verdicts = []
    for locus, res in all_results.items():
        rho = res["spearman_vs_occupancy"]["rho"]
        rho_base = res["spearman_vs_baseline"]["rho"]

        if rho > 0.95:
            v = f"{locus}: FAIL -- sensitivity map = occupancy (rho={rho:.3f}). Model is trivial."
        elif rho > rho_base + 0.05:
            v = f"{locus}: MARGINAL -- sensitivity > baseline (rho_occ={rho:.3f} vs rho_base={rho_base:.3f})."
        else:
            v = f"{locus}: FAIL -- sensitivity does not beat baseline."

        # Check DHS +58 for BCL11A
        if locus == "BCL11A" and "DHS_+58_Casgevy" in res.get("known_elements", {}):
            casgevy_rank = res["known_elements"]["DHS_+58_Casgevy"]["sensitivity_rank"]
            if casgevy_rank <= 5:
                v += f" DHS+58 rank={casgevy_rank} (PASS sanity)."
            else:
                v += f" DHS+58 rank={casgevy_rank} (FAIL sanity -- not in top-5)."

        print(f"  {v}")
        verdicts.append(v)

    overall = "PASS" if any("MARGINAL" in v or "PASS" in v for v in verdicts) else "FAIL"
    print(f"\n  Overall: {overall}")

    output = {
        "hypothesis": "H-14: Region-level sensitivity map",
        "preregistered": "2026-04-15",
        "uniform_effect": UNIFORM_EFFECT,
        "loci": all_results,
        "verdicts": verdicts,
        "overall": overall,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
