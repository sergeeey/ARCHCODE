"""
CTCF Permutation Negative Control Test
=======================================
Tests whether ARCHCODE's pearl signal is biological or a geometry artifact.

Method:
1. Load real HBB CTCF sites and pearl variants
2. For 100 permutations: shuffle CTCF positions (preserving distance distribution)
3. Run simplified Kramer-rate simulation for each pearl with shuffled CTCF
4. Compare LSSIM distributions: real vs shuffled

Kill criterion: If >50% of shuffled runs produce LSSIM < 0.92 for pearls,
the signal is likely a geometry artifact, not biological specificity.
"""

import json
import numpy as np
import pandas as pd
from itertools import combinations
import os

# ============================================================
# 1. LOAD DATA
# ============================================================

print("=" * 70)
print("CTCF PERMUTATION NEGATIVE CONTROL TEST")
print("=" * 70)

# Real CTCF sites from literature-c curated config
with open("D:/ДНК/data/hbb_ctcf_sites_literature.json") as f:
    ctcf_data = json.load(f)

real_ctcf_sites = np.array([s["position_absolute"] for s in ctcf_data["ctcf_sites"]])
real_ctcf_orientations = np.array([1 if s["orientation"] == "F" else -1 for s in ctcf_data["ctcf_sites"]])
real_ctcf_strengths = np.array([s["strength"] for s in ctcf_data["ctcf_sites"]])

locus_start = ctcf_data["locus"]["start"]
locus_end = ctcf_data["locus"]["end"]
locus_length = locus_end - locus_start

print(f"\nLocus: chr11:{locus_start}-{locus_end} ({locus_length:,} bp)")
print(f"Real CTCF sites (n={len(real_ctcf_sites)}): {real_ctcf_sites}")
print(f"Orientations: {real_ctcf_orientations}")

# HBB Combined Atlas - LSSIM scores
atlas = pd.read_csv("D:/ДНК/results/HBB_Combined_Atlas.csv")
print(f"\nHBB Combined Atlas: {len(atlas)} variants")
print(f"Columns: {list(atlas.columns)}")

# Pearl variants: pathogenic + low LSSIM + low VEP
pearl_mask = (
    (atlas["Label"] == "Pathogenic") &
    (atlas["ARCHCODE_SSIM"] < 0.95) &
    (atlas["VEP_Score"] < 0.5)
)
pearls = atlas[pearl_mask].copy()
print(f"Pearl variants found: {len(pearls)}")

if len(pearls) == 0:
    # Try with Unified Atlas
    print("\nNo pearls in Combined Atlas, trying Unified Atlas...")
    atlas = pd.read_csv("D:/ДНК/results/HBB_Unified_Atlas_95kb.csv")
    pearl_mask = (
        (atlas["Label"] == "Pathogenic") &
        (atlas["ARCHCODE_LSSIM"] < 0.95) &
        (atlas["VEP_Score"] < 0.5)
    )
    pearls = atlas[pearl_mask].copy()
    print(f"Pearl variants (Unified Atlas): {len(pearls)}")

# Get pearl positions and real LSSIM
if "ARCHCODE_SSIM" in atlas.columns:
    lssim_col = "ARCHCODE_SSIM"
else:
    lssim_col = "ARCHCODE_LSSIM"

pearl_positions = pearls["Position_GRCh38"].values
pearl_real_lssim = pearls[lssim_col].values

print(f"Pearl positions: {pearl_positions}")
print(f"Real LSSIM values: {pearl_real_lssim}")
print(f"Mean real LSSIM: {pearl_real_lssim.mean():.4f}")

# Enhancer positions (from hbb_30kb_v2.json config — MODEL_PARAMETER)
enhancer_positions = np.array([5220000, 5225500, 5227000, 5230000, 5233000])

# ============================================================
# 2. ANALYTICAL KRAMER-RATE CONTACT MODEL (simplified)
# ============================================================

def compute_contact_probability(pos1, pos2, ctcf_sites, ctcf_orientations, ctcf_strengths,
                                 enhancer_positions, kramer_base=0.3):
    """
    Simplified analytical Kramer-rate contact probability.
    
    Models the probability that two genomic loci are in spatial contact,
    modulated by CTCF loop extrusion barriers and enhancer occupancy.
    
    This is a simplified version of the ARCHCODE analytical model:
    P_contact = kramer_base * distance_factor * loop_barrier_factor * enhancer_factor
    """
    # Distance factor: contact probability decays with genomic distance
    genomic_dist = abs(pos1 - pos2)
    if genomic_dist == 0:
        distance_factor = 1.0
    else:
        # Power-law decay (typical for chromatin)
        distance_factor = (genomic_dist / 1000.0) ** (-0.75)
    
    # Loop barrier factor: CTCF sites between pos1 and pos2 block extrusion
    lo, hi = min(pos1, pos2), max(pos1, pos2)
    
    barrier_factor = 1.0
    for ctcf_pos, ctcf_orient, ctcf_str in zip(ctcf_sites, ctcf_orientations, ctcf_strengths):
        if lo < ctcf_pos < hi:
            # Convergent CTCF pairs are strong barriers
            # Check if this CTCF is oriented to block extrusion toward the other position
            if ctcf_orient > 0 and pos1 < ctcf_pos < pos2:
                # Forward CTCF blocks extrusion from left to right
                barrier_factor *= (1.0 - 0.85 * ctcf_str)
            elif ctcf_orient < 0 and pos1 < ctcf_pos < pos2:
                # Reverse CTCF blocks extrusion from right to left
                barrier_factor *= (1.0 - 0.85 * ctcf_str)
    
    # Enhancer factor: proximity to enhancers increases contact probability
    enhancer_factor = 1.0
    for enh_pos in enhancer_positions:
        dist_to_enhancer = min(abs(pos1 - enh_pos), abs(pos2 - enh_pos))
        if dist_to_enhancer < 5000:
            enhancer_factor += 0.3 * np.exp(-dist_to_enhancer / 2000.0)
    
    contact_prob = kramer_base * distance_factor * barrier_factor * enhancer_factor
    return min(contact_prob, 1.0)


def compute_contact_matrix(ctcf_sites, ctcf_orientations, ctcf_strengths,
                           enhancer_positions, resolution=2000):
    """Compute full contact matrix at given resolution."""
    positions = np.arange(locus_start + resolution//2, locus_end, resolution)
    n = len(positions)
    contact_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            prob = compute_contact_probability(
                positions[i], positions[j],
                ctcf_sites, ctcf_orientations, ctcf_strengths,
                enhancer_positions
            )
            contact_matrix[i, j] = prob
            contact_matrix[j, i] = prob
    
    return contact_matrix, positions


def compute_lssim(matrix1, matrix2):
    """
    Compute Localized Structural Similarity Index (LSSIM).
    Simplified version: structural similarity of contact matrices.
    """
    # Flatten upper triangle (symmetric matrix)
    n = matrix1.shape[0]
    mask = np.triu_indices(n, k=1)
    
    v1 = matrix1[mask]
    v2 = matrix2[mask]
    
    # SSIM-like computation
    mu1, mu2 = np.mean(v1), np.mean(v2)
    sigma1, sigma2 = np.var(v1), np.var(v2)
    sigma12 = np.cov(v1, v2)[0, 1]
    
    C1 = 0.01 ** 2
    C2 = 0.03 ** 2
    
    ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
           ((mu1**2 + mu2**2 + C1) * (sigma1 + sigma2 + C2))
    
    return ssim


def compute_variant_lssim(variant_pos, ctcf_sites, ctcf_orientations, ctcf_strengths,
                          enhancer_positions, ref_ctcf_sites, ref_ctcf_orientations,
                          ref_ctcf_strengths, resolution=2000):
    """
    Compute LSSIM for a variant by comparing REF vs ALT contact matrices.
    
    The variant is modeled as a perturbation to the CTCF landscape:
    - If variant disrupts a CTCF site: reduce strength
    - If variant creates a new CTCF site: add a site
    - Otherwise: small local perturbation to nearby contacts
    """
    # Compute reference contact matrix
    ref_matrix, positions = compute_contact_matrix(
        ref_ctcf_sites, ref_ctcf_orientations, ref_ctcf_strengths,
        enhancer_positions, resolution
    )
    
    # Model variant effect on CTCF
    alt_ctcf_sites = ctcf_sites.copy()
    alt_ctcf_orientations = ctcf_orientations.copy()
    alt_ctcf_strengths = ctcf_strengths.copy()
    
    # Check if variant overlaps/destroys a CTCF site
    for i, ctcf_pos in enumerate(ctcf_sites):
        if abs(ctcf_pos - variant_pos) < 50:  # variant within 50bp of CTCF
            alt_ctcf_strengths[i] *= 0.3  # disrupt CTCF binding
        elif abs(ctcf_pos - variant_pos) < 200:
            alt_ctcf_strengths[i] *= 0.7  # partial disruption
    
    # Compute alt contact matrix
    alt_matrix, _ = compute_contact_matrix(
        alt_ctcf_sites, alt_ctcf_orientations, alt_ctcf_strengths,
        enhancer_positions, resolution
    )
    
    # LSSIM = similarity between REF and ALT matrices
    lssim = compute_lssim(ref_matrix, alt_matrix)
    return lssim


# ============================================================
# 3. COMPUTE REAL LSSIM WITH CURRENT MODEL (sanity check)
# ============================================================

print("\n" + "=" * 70)
print("SANITY CHECK: Computing real LSSIM with analytical model")
print("=" * 70)

real_lssim_computed = []
for pos in pearl_positions:
    lssim = compute_variant_lssim(
        pos,
        real_ctcf_sites, real_ctcf_orientations, real_ctcf_strengths,
        enhancer_positions,
        real_ctcf_sites, real_ctcf_orientations, real_ctcf_strengths,
        resolution=2000
    )
    real_lssim_computed.append(lssim)

real_lssim_computed = np.array(real_lssim_computed)
print(f"Computed real LSSIM: {real_lssim_computed}")
print(f"Mean: {real_lssim_computed.mean():.4f}")

# ============================================================
# 4. CTCF PERMUTATION TEST
# ============================================================

N_PERMS = 100
np.random.seed(42)

print(f"\n{'=' * 70}")
print(f"CTCF PERMUTATION TEST: {N_PERMS} permutations")
print(f"{'=' * 70}")

# Compute inter-CTCF distances for preserved distribution
real_distances = np.diff(np.sort(real_ctcf_sites))
print(f"\nReal inter-CTCF distances: {real_distances}")
print(f"Mean: {real_distances.mean():.0f} bp, Std: {real_distances.std():.0f} bp")

shuffled_lssim_all = []  # All shuffled LSSIM values (N_PERMS × N_PEARLS)

for perm in range(N_PERMS):
    if (perm + 1) % 10 == 0:
        print(f"  Permutation {perm+1}/{N_PERMS}...")
    
    # Generate shuffled CTCF positions preserving distance distribution
    # Method: sample from real inter-CTCF distance distribution
    n_ctcf = len(real_ctcf_sites)
    
    shuffled_positions = [locus_start + 1000]  # Start near beginning
    for _ in range(n_ctcf - 1):
        # Sample distance from real distribution (with some noise)
        sampled_dist = np.random.choice(real_distances)
        # Add small jitter
        sampled_dist += np.random.normal(0, sampled_dist * 0.1)
        sampled_dist = max(500, sampled_dist)  # Minimum 500bp apart
        new_pos = shuffled_positions[-1] + sampled_dist
        if new_pos > locus_end - 1000:
            break
        shuffled_positions.append(new_pos)
    
    # If we didn't get enough sites, pad with random positions
    while len(shuffled_positions) < n_ctcf:
        pad_pos = np.random.randint(locus_start + 1000, locus_end - 1000)
        shuffled_positions.append(pad_pos)
    
    shuffled_positions = np.array(shuffled_positions[:n_ctcf])
    shuffled_positions.sort()
    
    # Shuffle orientations independently (50/50)
    shuffled_orientations = np.random.choice([-1, 1], size=n_ctcf)
    
    # Keep strengths same (or shuffle them too — both options)
    shuffled_strengths = real_ctcf_strengths.copy()
    np.random.shuffle(shuffled_strengths)
    
    # Compute LSSIM for each pearl with this shuffled configuration
    perm_lssim = []
    for pos in pearl_positions:
        lssim = compute_variant_lssim(
            pos,
            shuffled_positions, shuffled_orientations, shuffled_strengths,
            enhancer_positions,
            real_ctcf_sites, real_ctcf_orientations, real_ctcf_strengths,
            resolution=2000
        )
        perm_lssim.append(lssim)
    
    shuffled_lssim_all.append(perm_lssim)

shuffled_lssim_all = np.array(shuffled_lssim_all)  # shape: (N_PERMS, N_PEARLS)

# ============================================================
# 5. ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

# Per-pearl statistics
print(f"\n{'Position':>12} {'Real LSSIM':>12} {'Shuffled μ':>12} {'Shuffled σ':>12} {'Frac < 0.95':>12} {'Frac < 0.92':>12}")
print("-" * 72)

per_pearl_results = []
for i, pos in enumerate(pearl_positions):
    real_l = pearl_real_lssim[i]
    shuffled_mean = shuffled_lssim_all[:, i].mean()
    shuffled_std = shuffled_lssim_all[:, i].std()
    frac_below_095 = (shuffled_lssim_all[:, i] < 0.95).mean()
    frac_below_092 = (shuffled_lssim_all[:, i] < 0.92).mean()
    
    per_pearl_results.append({
        "position": int(pos),
        "real_lssim": float(real_l),
        "shuffled_mean": float(shuffled_mean),
        "shuffled_std": float(shuffled_std),
        "frac_below_095": float(frac_below_095),
        "frac_below_092": float(frac_below_092)
    })
    
    print(f"{pos:>12} {real_l:>12.4f} {shuffled_mean:>12.4f} {shuffled_std:>12.4f} {frac_below_095:>12.4f} {frac_below_092:>12.4f}")

# Overall statistics
overall_frac_below_095 = (shuffled_lssim_all < 0.95).mean()
overall_frac_below_092 = (shuffled_lssim_all < 0.92).mean()
overall_frac_below_real = (shuffled_lssim_all < pearl_real_lssim.max()).mean()

print(f"\n{'=' * 70}")
print("OVERALL STATISTICS")
print(f"{'=' * 70}")
print(f"Real pearl LSSIM range: [{pearl_real_lssim.min():.4f}, {pearl_real_lssim.max():.4f}]")
print(f"Real pearl LSSIM mean:  {pearl_real_lssim.mean():.4f}")
print(f"Shuffled LSSIM mean:    {shuffled_lssim_all.mean():.4f}")
print(f"Shuffled LSSIM std:     {shuffled_lssim_all.std():.4f}")
print(f"Shuffled LSSIM range:   [{shuffled_lssim_all.min():.4f}, {shuffled_lssim_all.max():.4f}]")
print(f"\nFraction of shuffled LSSIM < 0.95: {overall_frac_below_095:.4f} ({overall_frac_below_095*100:.1f}%)")
print(f"Fraction of shuffled LSSIM < 0.92: {overall_frac_below_092:.4f} ({overall_frac_below_092*100:.1f}%)")
print(f"Fraction of shuffled LSSIM < real max ({pearl_real_lssim.max():.4f}): {overall_frac_below_real:.4f}")

# Kolmogorov-Smirnov test
from scipy import stats
real_flat = pearl_real_lssim
shuffled_flat = shuffled_lssim_all.flatten()
ks_stat, ks_pvalue = stats.ks_2samp(real_flat, shuffled_flat)
print(f"\nKolmogorov-Smirnov test:")
print(f"  KS statistic: {ks_stat:.4f}")
print(f"  KS p-value:   {ks_pvalue:.6f}")

# Mann-Whitney U test
mw_stat, mw_pvalue = stats.mannwhitneyu(real_flat, shuffled_flat, alternative='two-sided')
print(f"\nMann-Whitney U test:")
print(f"  U statistic:  {mw_stat}")
print(f"  U p-value:    {mw_pvalue:.6f}")

# ============================================================
# 6. KILL CRITERION
# ============================================================

print(f"\n{'=' * 70}")
print("VERDICT")
print(f"{'=' * 70}")

# Kill criterion: if >50% of shuffled runs produce LSSIM < 0.92
if overall_frac_below_092 > 0.50:
    verdict = "FAIL 🔴"
    verdict_detail = (
        f"FAIL — {overall_frac_below_092*100:.1f}% of shuffled CTCF configurations "
        f"produce LSSIM < 0.92 for pearl variants. This suggests the pearl signal "
        f"is primarily a GEOMETRY ARTIFACT, not biologically specific to real CTCF architecture. "
        f"The LSSIM metric responds to any random arrangement of barriers, not the real ones."
    )
elif overall_frac_below_095 > 0.50:
    verdict = "WARNING ⚠️"
    verdict_detail = (
        f"WARNING — {overall_frac_below_095*100:.1f}% of shuffled configurations "
        f"produce LSSIM < 0.95, but only {overall_frac_below_092*100:.1f}% < 0.92. "
        f"The signal is PARTIALLY geometry-driven but shows some biological specificity "
        f"at stricter thresholds."
    )
else:
    verdict = "PASS ✅"
    verdict_detail = (
        f"PASS — Only {overall_frac_below_092*100:.1f}% of shuffled configurations "
        f"produce LSSIM < 0.92 (vs {len(pearls[pearl_real_lssim < 0.92])}/{len(pearls)} real pearls). "
        f"The pearl signal is BIOLOGICALLY SPECIFIC to the real CTCF architecture. "
        f"Random CTCF arrangements do not reproduce the disruption signal."
    )

print(f"\nVerdict: {verdict}")
print(f"Detail: {verdict_detail}")

# ============================================================
# 7. SAVE RESULTS
# ============================================================

results = {
    "test_name": "CTCF Permutation Negative Control",
    "n_permutations": N_PERMS,
    "n_pearls": len(pearls),
    "locus": f"chr11:{locus_start}-{locus_end}",
    "real_ctcf_sites": real_ctcf_sites.tolist(),
    "pearl_positions": pearl_positions.tolist(),
    "pearl_real_lssim": pearl_real_lssim.tolist(),
    "overall_stats": {
        "shuffled_mean": float(shuffled_lssim_all.mean()),
        "shuffled_std": float(shuffled_lssim_all.std()),
        "shuffled_min": float(shuffled_lssim_all.min()),
        "shuffled_max": float(shuffled_lssim_all.max()),
        "frac_below_095": float(overall_frac_below_095),
        "frac_below_092": float(overall_frac_below_092),
        "ks_stat": float(ks_stat),
        "ks_pvalue": float(ks_pvalue),
        "mw_pvalue": float(mw_pvalue)
    },
    "per_pearl": per_pearl_results,
    "verdict": verdict,
    "verdict_detail": verdict_detail,
    "kill_criteria": {
        "frac_below_092": float(overall_frac_below_092),
        "threshold": 0.50,
        "result": "FAIL" if overall_frac_below_092 > 0.50 else "PASS"
    }
}

# Save JSON
os.makedirs("D:/ДНК/results", exist_ok=True)
with open("D:/ДНК/results/ctcf_shuffle_test.json", "w") as f:
    json.dump(results, f, indent=2)

# Save CSV
csv_rows = []
for i, pos in enumerate(pearl_positions):
    csv_rows.append({
        "position": int(pos),
        "real_lssim": float(pearl_real_lssim[i]),
        "shuffled_mean": float(shuffled_lssim_all[:, i].mean()),
        "shuffled_std": float(shuffled_lssim_all[:, i].std()),
        "shuffled_min": float(shuffled_lssim_all[:, i].min()),
        "shuffled_max": float(shuffled_lssim_all[:, i].max()),
        "frac_below_095": float((shuffled_lssim_all[:, i] < 0.95).mean()),
        "frac_below_092": float((shuffled_lssim_all[:, i] < 0.92).mean())
    })
csv_df = pd.DataFrame(csv_rows)
csv_df.to_csv("D:/ДНК/results/ctcf_shuffle_test.csv", index=False)

print(f"\nResults saved to:")
print(f"  D:/ДНК/results/ctcf_shuffle_test.json")
print(f"  D:/ДНК/results/ctcf_shuffle_test.csv")
print(f"\n{'=' * 70}")
print("TEST COMPLETE")
print(f"{'=' * 70}")
