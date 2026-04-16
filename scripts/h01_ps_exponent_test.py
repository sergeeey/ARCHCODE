"""
H-01: P(s) Critical Exponent Shift Test
Pre-registered: 2026-04-15.
Kill criterion: delta-gamma must discriminate pathogenic vs benign WITHIN same category.
Kill baseline: distance-to-nearest-CTCF.
"""

import json, math
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

ROOT = Path("D:/\u0414\u041d\u041a")
CONFIG_PATH = ROOT / "config/locus/hbb_95kb_subTAD.json"
ATLAS_PATH = ROOT / "results/HBB_Unified_Atlas_95kb.csv"
OUTPUT_PATH = ROOT / "results/h01_ps_exponent_results.json"

K_BASE = 0.002
ALPHA = 0.92
GAMMA_PARAM = 0.80
BACKGROUND_OCC = 0.1
CTCF_PENALTY = 0.15

with open(CONFIG_PATH) as f:
    config = json.load(f)

WINDOW_START = config["window"]["start"]
RESOLUTION = config["window"]["resolution_bp"]
N_BINS = config["window"]["n_bins"]
enhancers = config["features"]["enhancers"]
ctcf_sites = config["features"]["ctcf_sites"]
ctcf_positions = [s["position"] for s in ctcf_sites]

CATEGORICAL_EFFECTS = {
    "nonsense": 0.1, "frameshift": 0.15,
    "splice_donor": 0.2, "splice_acceptor": 0.2, "splice_region": 0.5,
    "missense": 0.4, "promoter": 0.3,
    "5_prime_utr": 0.6, "3_prime_utr": 0.7,
    "intronic": 0.8, "synonymous": 0.9, "other": 0.5,
}


def pos_to_bin(pos):
    return int((pos - WINDOW_START) / RESOLUTION)


def build_occupancy_landscape():
    occ = np.full(N_BINS, BACKGROUND_OCC)
    for enh in enhancers:
        enh_bin = pos_to_bin(enh["position"])
        enh_occ = enh["occupancy"]
        spread = max(3, int(2000 / RESOLUTION))
        for i in range(N_BINS):
            dist_bins = abs(i - enh_bin)
            contrib = enh_occ * math.exp(-0.5 * (dist_bins / spread) ** 2)
            occ[i] += contrib
    return np.clip(occ, 0, 1)


def get_ctcf_bins():
    return [pos_to_bin(p) for p in ctcf_positions]


def count_ctcf_between(i, j, ctcf_bins):
    lo, hi = min(i, j), max(i, j)
    return sum(1 for c in ctcf_bins if lo < c < hi)


def build_contact_matrix(occ, ctcf_bins):
    mat = np.zeros((N_BINS, N_BINS))
    for i in range(N_BINS):
        for j in range(i + 1, N_BINS):
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


def apply_variant(base_occ, variant_bin, effect_strength):
    mut_occ = base_occ.copy()
    for i in range(N_BINS):
        dist = abs(i - variant_bin)
        if dist < 3:
            mut_occ[i] *= effect_strength
        else:
            fade = effect_strength + (1 - effect_strength) * (dist / 3.0)
            if fade < 1.0:
                mut_occ[i] *= min(fade, 1.0)
    return np.clip(mut_occ, 0, 1)


def compute_ps_curve(mat):
    n = mat.shape[0]
    max_dist = n // 2
    distances = []
    contacts = []
    for s in range(1, max_dist):
        vals = [mat[i][i + s] for i in range(n - s)]
        distances.append(s)
        contacts.append(np.mean(vals))
    return np.array(distances, dtype=float), np.array(contacts, dtype=float)


def compute_gamma(distances, contacts):
    mask = contacts > 0
    log_d = np.log(distances[mask])
    log_c = np.log(contacts[mask])
    gamma_vals = np.gradient(log_c, log_d)
    return distances[mask], gamma_vals


def compute_delta_gamma(wt_mat, mut_mat):
    d_wt, c_wt = compute_ps_curve(wt_mat)
    d_mut, c_mut = compute_ps_curve(mut_mat)
    _, gamma_wt = compute_gamma(d_wt, c_wt)
    _, gamma_mut = compute_gamma(d_mut, c_mut)
    n = min(len(gamma_wt), len(gamma_mut))
    delta_gamma = gamma_mut[:n] - gamma_wt[:n]
    return {
        "mean_delta_gamma": float(np.mean(delta_gamma)),
        "max_abs_delta_gamma": float(np.max(np.abs(delta_gamma))),
    }


def distance_to_nearest_ctcf(pos):
    return min(abs(pos - c) for c in ctcf_positions)


def main():
    print("=" * 70)
    print("H-01: P(s) Critical Exponent Shift Test")
    print("=" * 70)
    df = pd.read_csv(ATLAS_PATH)
    print(f"Loaded {len(df)} variants from {ATLAS_PATH.name}")
    print("Building WT contact matrix...")
    wt_occ = build_occupancy_landscape()
    ctcf_bins = get_ctcf_bins()
    wt_mat = build_contact_matrix(wt_occ, ctcf_bins)
    print(f"  Matrix: {N_BINS}x{N_BINS}, CTCF bins: {ctcf_bins}")
    print("Computing delta-gamma for each variant...")
    results = []
    for idx, row in df.iterrows():
        pos = int(row["Position_GRCh38"])
        category = str(row["Category"]).lower().replace(" ", "_")
        label = str(row.get("Label", ""))
        lssim = float(row.get("ARCHCODE_LSSIM", 1.0))
        effect = CATEGORICAL_EFFECTS.get(category, 0.5)
        variant_bin = pos_to_bin(pos)
        if variant_bin < 0 or variant_bin >= N_BINS:
            continue
        mut_occ = apply_variant(wt_occ, variant_bin, effect)
        mut_mat = build_contact_matrix(mut_occ, ctcf_bins)
        dg = compute_delta_gamma(wt_mat, mut_mat)
        results.append({
            "ClinVar_ID": row["ClinVar_ID"], "Position": pos,
            "Category": category, "Label": label, "LSSIM": lssim,
            "mean_delta_gamma": dg["mean_delta_gamma"],
            "max_abs_delta_gamma": dg["max_abs_delta_gamma"],
            "dist_to_ctcf": distance_to_nearest_ctcf(pos),
        })
        if (idx + 1) % 200 == 0:
            print(f"  {idx + 1}/{len(df)} variants processed")
    rdf = pd.DataFrame(results)
    print(f"\nComputed delta-gamma for {len(rdf)} variants")

    print("\n" + "=" * 70)
    print("OVERALL TEST: mean_delta_gamma by Label")
    print("=" * 70)
    for label in ["Pathogenic", "Benign"]:
        subset = rdf[rdf["Label"] == label]["mean_delta_gamma"]
        print(f"  {label}: n={len(subset)}, mean={subset.mean():.6f}, std={subset.std():.6f}")
    path_dg = rdf[rdf["Label"] == "Pathogenic"]["mean_delta_gamma"]
    ben_dg = rdf[rdf["Label"] == "Benign"]["mean_delta_gamma"]
    overall_p, overall_d = 1.0, 0.0
    if len(path_dg) > 5 and len(ben_dg) > 5:
        u_stat, overall_p = stats.mannwhitneyu(path_dg, ben_dg, alternative="two-sided")
        pooled_std = np.sqrt((path_dg.std()**2 + ben_dg.std()**2) / 2)
        overall_d = (path_dg.mean() - ben_dg.mean()) / pooled_std if pooled_std > 0 else 0
        print(f"  Mann-Whitney U={u_stat:.0f}, p={overall_p:.4e}, Cohen d={overall_d:.3f}")

    print("\n" + "=" * 70)
    print("WITHIN-CATEGORY TEST (kill test)")
    print("=" * 70)
    within_results = []
    for cat in sorted(rdf["Category"].unique()):
        cat_df = rdf[rdf["Category"] == cat]
        path_sub = cat_df[cat_df["Label"] == "Pathogenic"]["mean_delta_gamma"]
        ben_sub = cat_df[cat_df["Label"] == "Benign"]["mean_delta_gamma"]
        if len(path_sub) >= 3 and len(ben_sub) >= 3:
            u, p = stats.mannwhitneyu(path_sub, ben_sub, alternative="two-sided")
            pooled = np.sqrt((path_sub.std()**2 + ben_sub.std()**2) / 2)
            cd = (path_sub.mean() - ben_sub.mean()) / pooled if pooled > 0 else 0
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {cat:20s}  n_P={len(path_sub):4d}  n_B={len(ben_sub):4d}  p={p:.4e}  d={cd:+.3f}  {sig}")
            within_results.append({"category": cat, "n_path": int(len(path_sub)), "n_ben": int(len(ben_sub)),
                "p_value": float(p), "cohen_d": float(cd), "significant": bool(p < 0.05)})
        else:
            print(f"  {cat:20s}  n_P={len(path_sub):4d}  n_B={len(ben_sub):4d}  SKIP")
    n_sig = sum(1 for r in within_results if r["significant"])
    n_total = len(within_results)
    print(f"\n  Within-category significant: {n_sig}/{n_total}")

    print("\n" + "=" * 70)
    print("BASELINE: distance-to-nearest-CTCF")
    print("=" * 70)
    baseline_results = []
    for cat in sorted(rdf["Category"].unique()):
        cat_df = rdf[rdf["Category"] == cat]
        path_sub = cat_df[cat_df["Label"] == "Pathogenic"]["dist_to_ctcf"]
        ben_sub = cat_df[cat_df["Label"] == "Benign"]["dist_to_ctcf"]
        if len(path_sub) >= 3 and len(ben_sub) >= 3:
            u, p = stats.mannwhitneyu(path_sub, ben_sub, alternative="two-sided")
            pooled = np.sqrt((path_sub.std()**2 + ben_sub.std()**2) / 2)
            cd = (path_sub.mean() - ben_sub.mean()) / pooled if pooled > 0 else 0
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            print(f"  {cat:20s}  p={p:.4e}  d={cd:+.3f}  {sig}")
            baseline_results.append({"category": cat, "p_value": float(p), "cohen_d": float(cd),
                "significant": bool(p < 0.05)})
    n_sig_base = sum(1 for r in baseline_results if r["significant"])
    n_total_base = len(baseline_results)
    print(f"\n  Baseline significant: {n_sig_base}/{n_total_base}")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    if n_sig == 0:
        verdict = "FAIL -- delta-gamma does not discriminate within any category. H-01 killed."
    elif n_sig <= n_sig_base:
        verdict = f"FAIL -- delta-gamma ({n_sig}/{n_total} sig) does not beat baseline ({n_sig_base}/{n_total_base} sig)."
    else:
        verdict = f"PASS -- delta-gamma ({n_sig}/{n_total} sig) beats baseline ({n_sig_base}/{n_total_base} sig)."
    print(f"  {verdict}")

    output = {
        "hypothesis": "H-01: P(s) critical exponent shift",
        "preregistered": "2026-04-15", "n_variants": len(rdf),
        "overall": {"p_value": float(overall_p), "cohen_d": float(overall_d)},
        "within_category": within_results,
        "within_category_significant": n_sig, "within_category_total": n_total,
        "baseline_dist_to_ctcf": baseline_results,
        "baseline_significant": n_sig_base, "baseline_total": n_total_base,
        "verdict": verdict,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
