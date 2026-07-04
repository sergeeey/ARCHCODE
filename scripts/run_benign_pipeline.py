#!/usr/bin/env python3
"""
Run VEP + ARCHCODE pipeline on Benign HBB variants.
Then merge with existing pathogenic atlas for ROC analysis.

Input: data/hbb_benign_variants.csv (750 benign variants)
Output: results/HBB_Combined_Atlas.csv (pathogenic + benign)
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import math
from pathlib import Path

# === PATHS ===
BENIGN_CSV = Path(__file__).parent.parent / "data" / "hbb_benign_variants.csv"
PATHOGENIC_CSV = Path(__file__).parent.parent / "results" / "HBB_Clinical_Atlas_REAL.csv"
OUTPUT_CSV = Path(__file__).parent.parent / "results" / "HBB_Combined_Atlas.csv"
SUMMARY_JSON = Path(__file__).parent.parent / "results" / "COMBINED_ATLAS_SUMMARY.json"

# === VEP API ===
VEP_API_URL = "https://rest.ensembl.org/vep/homo_sapiens/region"
VEP_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
BATCH_SIZE = 200

CONSEQUENCE_SCORES = {
    "transcript_ablation": 0.99,
    "splice_acceptor_variant": 0.95,
    "splice_donor_variant": 0.95,
    "stop_gained": 0.90,
    "frameshift_variant": 0.90,
    "stop_lost": 0.85,
    "start_lost": 0.85,
    "missense_variant": 0.50,
    "splice_region_variant": 0.50,
    "coding_sequence_variant": 0.20,
    "5_prime_UTR_variant": 0.20,
    "upstream_gene_variant": 0.15,
    "3_prime_UTR_variant": 0.15,
    "intron_variant": 0.10,
    "synonymous_variant": 0.05,
    "intergenic_variant": 0.05,
}

# === ARCHCODE ANALYTICAL MODEL ===
# Parameters (same as generate-real-atlas.ts)
HBB_START = 5210000
HBB_END = 5240000
RESOLUTION = 600
N_BINS = 50
ALPHA = 0.92
GAMMA = 0.80
K_BASE = 0.002

# CTCF sites (positions within HBB region, 0-indexed bins)
CTCF_SITES = [5, 12, 20, 30, 38, 45]
CTCF_PERMEABILITY = 0.15

# MED1 occupancy profile (normalized 0-1)
MED1_PROFILE = np.zeros(N_BINS)
# Enhancer regions (approximate bins with elevated MED1)
ENHANCER_BINS = [(3, 8), (15, 20), (25, 30), (35, 40), (42, 47)]
for start, end in ENHANCER_BINS:
    MED1_PROFILE[start:end] = np.random.RandomState(2026).uniform(0.4, 0.9, end - start)

# Occupancy impact by category
CATEGORY_IMPACT = {
    "nonsense": 0.80,
    "frameshift": 0.75,
    "splice_donor": 0.70,
    "splice_acceptor": 0.70,
    "splice_region": 0.35,
    "missense": 0.30,
    "promoter": 0.50,
    "5_prime_UTR": 0.10,
    "3_prime_UTR": 0.05,
    "intronic": 0.02,
    "synonymous": 0.01,
    "other": 0.05,
}


def compute_contact_matrix(occupancy):
    """Analytical mean-field contact matrix computation."""
    C = np.zeros((N_BINS, N_BINS))

    for i in range(N_BINS):
        for j in range(i + 1, N_BINS):
            # Distance decay
            dist = abs(i - j)
            distance_factor = 1.0 / dist

            # Occupancy geometric mean
            occ_factor = math.sqrt(max(occupancy[i], 0.01) * max(occupancy[j], 0.01))

            # CTCF barrier product
            ctcf_factor = 1.0
            for site in CTCF_SITES:
                if i < site < j:
                    ctcf_factor *= CTCF_PERMEABILITY

            # Kramer modulation
            mean_occ = np.mean(occupancy[i:j + 1])
            kramer = 1.0 - K_BASE * (1.0 - ALPHA * (mean_occ ** GAMMA))

            C[i, j] = distance_factor * occ_factor * ctcf_factor * kramer
            C[j, i] = C[i, j]

    # Normalize
    max_val = C.max()
    if max_val > 0:
        C = C / max_val

    # Set diagonal
    np.fill_diagonal(C, 1.0)
    return C


def compute_ssim(mat_a, mat_b):
    """SSIM between two contact matrices (upper triangle, k=1)."""
    # Extract upper triangle (excluding diagonal)
    idx = np.triu_indices(N_BINS, k=1)
    a = mat_a[idx]
    b = mat_b[idx]

    mu_a = np.mean(a)
    mu_b = np.mean(b)
    sigma_a = np.std(a)
    sigma_b = np.std(b)
    sigma_ab = np.mean((a - mu_a) * (b - mu_b))

    L = 1.0
    C1 = (0.01 * L) ** 2
    C2 = (0.03 * L) ** 2

    numerator = (2 * mu_a * mu_b + C1) * (2 * sigma_ab + C2)
    denominator = (mu_a ** 2 + mu_b ** 2 + C1) * (sigma_a ** 2 + sigma_b ** 2 + C2)

    return numerator / denominator


def archcode_ssim(position, category):
    """Compute ARCHCODE SSIM for a variant."""
    # WT occupancy
    wt_occ = MED1_PROFILE.copy()
    wt_occ = np.maximum(wt_occ, 0.1)  # baseline

    # Mutant occupancy
    mut_occ = wt_occ.copy()

    # Find affected bin
    if HBB_START <= position <= HBB_END:
        affected_bin = int((position - HBB_START) / RESOLUTION)
        affected_bin = max(0, min(affected_bin - 1, N_BINS - 1))
    else:
        affected_bin = N_BINS // 2

    impact = CATEGORY_IMPACT.get(category, 0.05)

    # Apply perturbation (reduce occupancy at affected bin and neighbors)
    for offset in [-1, 0, 1]:
        b = affected_bin + offset
        if 0 <= b < N_BINS:
            weight = 1.0 if offset == 0 else 0.5
            mut_occ[b] *= (1.0 - impact * weight)

    # Compute matrices
    wt_matrix = compute_contact_matrix(wt_occ)
    mut_matrix = compute_contact_matrix(mut_occ)

    return compute_ssim(wt_matrix, mut_matrix)


def classify_ssim(ssim):
    """ARCHCODE verdict from SSIM."""
    if ssim < 0.85:
        return "PATHOGENIC"
    elif ssim < 0.92:
        return "LIKELY_PATHOGENIC"
    elif ssim < 0.96:
        return "VUS"
    elif ssim < 0.99:
        return "LIKELY_BENIGN"
    else:
        return "BENIGN"


def run_vep_batch(variants_df):
    """Run Ensembl VEP on variants."""
    results = []

    for batch_start in range(0, len(variants_df), BATCH_SIZE):
        batch = variants_df.iloc[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (len(variants_df) - 1) // BATCH_SIZE + 1

        # Build VEP input
        vep_input = []
        for _, row in batch.iterrows():
            pos = int(row["position"])
            ref = str(row["ref"])
            alt = str(row["alt"])
            vep_input.append(f"11 {pos} {pos} {ref}/{alt} 1")

        payload = {"variants": vep_input}

        print(f"  VEP batch {batch_num}/{total_batches}...", end=" ")

        for attempt in range(5):
            try:
                resp = requests.post(VEP_API_URL, json=payload, headers=VEP_HEADERS, timeout=60)
                if resp.status_code == 429:
                    wait = 10
                    print(f"rate-limited, wait {wait}s...", end=" ")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                vep_data = resp.json()

                for item in vep_data:
                    # Get most severe consequence
                    consequence = item.get("most_severe_consequence", "intergenic_variant")
                    score = CONSEQUENCE_SCORES.get(consequence, 0.10)

                    # SIFT for missense
                    sift_score = None
                    tc = item.get("transcript_consequences", [])
                    for t in tc:
                        if "sift_score" in t:
                            sift_score = t["sift_score"]
                            break

                    if consequence == "missense_variant" and sift_score is not None:
                        score = 0.4 + 0.5 * (1.0 - sift_score)

                    input_str = item.get("input", "")
                    parts = input_str.split()
                    pos = int(parts[1]) if len(parts) > 1 else 0

                    results.append({
                        "position": pos,
                        "vep_consequence": consequence,
                        "vep_score": round(score, 4),
                        "sift_score": sift_score,
                    })

                print(f"OK ({len(vep_data)} results)")
                break
            except Exception as e:
                wait = 5 * (attempt + 1)
                print(f"error, retry in {wait}s...", end=" ")
                time.sleep(wait)
        else:
            print("FAILED")
            # Fill with defaults
            for _, row in batch.iterrows():
                results.append({
                    "position": int(row["position"]),
                    "vep_consequence": "unknown",
                    "vep_score": 0.10,
                    "sift_score": None,
                })

        time.sleep(1)

    return pd.DataFrame(results)


def main():
    print("=" * 60)
    print("  BENIGN VARIANT PIPELINE: VEP + ARCHCODE")
    print("=" * 60)

    # Load benign variants
    df = pd.read_csv(BENIGN_CSV)
    print(f"\nLoaded {len(df)} benign variants")

    # Step 1: VEP predictions
    print("\n--- Step 1: Ensembl VEP Predictions ---")
    vep_results = run_vep_batch(df)

    # Merge VEP results with variants (by position)
    df["vep_consequence"] = "unknown"
    df["vep_score"] = 0.10
    df["sift_score"] = None

    # Match by position
    vep_by_pos = {}
    for _, row in vep_results.iterrows():
        vep_by_pos[row["position"]] = row

    for idx, row in df.iterrows():
        pos = int(row["position"])
        if pos in vep_by_pos:
            vep = vep_by_pos[pos]
            df.at[idx, "vep_consequence"] = vep["vep_consequence"]
            df.at[idx, "vep_score"] = vep["vep_score"]
            df.at[idx, "sift_score"] = vep["sift_score"]

    # Step 2: ARCHCODE SSIM
    print("\n--- Step 2: ARCHCODE SSIM Simulation ---")
    ssim_values = []
    verdicts = []
    for idx, row in df.iterrows():
        ssim = archcode_ssim(int(row["position"]), row["category"])
        ssim_values.append(round(ssim, 4))
        verdicts.append(classify_ssim(ssim))

    df["ARCHCODE_SSIM"] = ssim_values
    df["ARCHCODE_Verdict"] = verdicts
    print(f"  Computed SSIM for {len(df)} variants")
    print(f"  Mean SSIM: {np.mean(ssim_values):.4f}")
    print(f"  Range: [{min(ssim_values):.4f}, {max(ssim_values):.4f}]")

    # Step 3: Add label column
    df["Label"] = "Benign"  # All are Benign/LB

    # Step 4: Merge with pathogenic atlas
    print("\n--- Step 3: Merge with Pathogenic Atlas ---")
    path_df = pd.read_csv(PATHOGENIC_CSV)
    print(f"  Pathogenic atlas: {len(path_df)} variants")

    # Standardize columns for merge
    benign_out = df[["clinvar_id", "position", "ref", "alt", "category",
                      "clinical_significance", "ARCHCODE_SSIM", "ARCHCODE_Verdict",
                      "vep_consequence", "vep_score", "sift_score"]].copy()
    benign_out.columns = ["ClinVar_ID", "Position_GRCh38", "Ref", "Alt", "Category",
                           "ClinVar_Significance", "ARCHCODE_SSIM", "ARCHCODE_Verdict",
                           "VEP_Consequence", "VEP_Score", "SIFT_Score"]
    benign_out["Label"] = "Benign"
    benign_out["Source"] = "ClinVar_Benign"

    pathogenic_out = path_df[["ClinVar_ID", "Position_GRCh38", "Ref", "Alt", "Category",
                               "ClinVar_Significance", "ARCHCODE_SSIM", "ARCHCODE_Verdict",
                               "VEP_Consequence", "VEP_Score", "SIFT_Score"]].copy()
    pathogenic_out["Label"] = "Pathogenic"
    pathogenic_out["Source"] = "ClinVar_Pathogenic"

    combined = pd.concat([pathogenic_out, benign_out], ignore_index=True)
    combined.to_csv(OUTPUT_CSV, index=False)
    print(f"  Combined atlas: {len(combined)} variants")
    print(f"    Pathogenic: {len(pathogenic_out)}")
    print(f"    Benign: {len(benign_out)}")

    # Step 5: Summary
    print("\n--- Summary ---")
    path_ssim = pathogenic_out["ARCHCODE_SSIM"].astype(float)
    benign_ssim = benign_out["ARCHCODE_SSIM"].astype(float)

    summary = {
        "total_variants": len(combined),
        "pathogenic_count": len(pathogenic_out),
        "benign_count": len(benign_out),
        "pathogenic_mean_ssim": round(float(path_ssim.mean()), 4),
        "benign_mean_ssim": round(float(benign_ssim.mean()), 4),
        "pathogenic_ssim_range": [round(float(path_ssim.min()), 4), round(float(path_ssim.max()), 4)],
        "benign_ssim_range": [round(float(benign_ssim.min()), 4), round(float(benign_ssim.max()), 4)],
        "separation": round(float(benign_ssim.mean() - path_ssim.mean()), 4),
    }

    print(f"  Pathogenic mean SSIM: {summary['pathogenic_mean_ssim']}")
    print(f"  Benign mean SSIM: {summary['benign_mean_ssim']}")
    print(f"  Separation: {summary['separation']}")

    with open(SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved: {OUTPUT_CSV}")
    print(f"Saved: {SUMMARY_JSON}")

    return 0


if __name__ == "__main__":
    exit(main())
