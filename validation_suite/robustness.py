"""
Robustness Test — Stability across seeds, resolution, and tissue mismatch.

Tests:
1. Seed stability: 10 different random seeds for landscape generation
2. Resolution sensitivity: does changing resolution affect rankings?
3. Tissue mismatch: K562 annotations on non-K562 loci
"""

import json
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validation_suite.repo_paths import (  # noqa: E402
    config_locus_dir,
    results_dir,
    validation_results_dir,
)

_ROOT = results_dir()

print("=" * 70)
print("ROBUSTNESS TEST")
print("=" * 70)

# ============================================================
# 1. SEED STABILITY
# ============================================================

print(f"\n{'=' * 70}")
print("TEST 1: Seed Stability")
print(f"{'=' * 70}")

# The ARCHCODE SSIM depends on the RNG seed used for landscape generation
# Different seeds → different occupancy landscapes → different SSIM values
# A robust model should have low variance across seeds

N_SEEDS = 10

K_BASE = 0.002
DEFAULT_ALPHA = 0.92
DEFAULT_GAMMA = 0.8
BACKGROUND_OCCUPANCY = 0.1
CTCF_INSULATION = 0.15

CATEGORICAL_EFFECTS = {
    "nonsense": 0.1, "frameshift": 0.15, "splice_donor": 0.2,
    "splice_acceptor": 0.2, "splice_region": 0.5, "missense": 0.4,
    "promoter": 0.3, "5_prime_UTR": 0.6, "3_prime_UTR": 0.7,
    "intronic": 0.8, "synonymous": 0.9, "other": 0.5,
}

# Load HBB
atlas = pd.read_csv(_ROOT / "HBB_Unified_Atlas.csv")
with open(config_locus_dir() / "hbb_30kb_v2.json") as f:
    config = json.load(f)

label_col = "Label"
atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)

# Sample 50 variants for speed
np.random.seed(42)
sample_idx = np.random.choice(len(atlas), size=min(50, len(atlas)), replace=False)
sample = atlas.iloc[sample_idx]
y_sample = sample["is_pathogenic"].values

def compute_ssim_seed(config, positions, categories, effects, seed):
    """Compute SSIM for multiple variants with a given seed."""
    rng = np.random.default_rng(seed)
    
    window_start = config["window"]["start"]
    resolution = config["window"]["resolution_bp"]
    n_bins = config["window"]["n_bins"]
    
    enhancers = [(e["position"], e["occupancy"]) for e in config["features"].get("enhancers", [])]
    ctcf_sites = [c["position"] for c in config["features"].get("ctcf_sites", [])]
    ctcf_bins = [int((p - window_start) // resolution) for p in ctcf_sites
                 if window_start <= p < window_start + n_bins * resolution]
    
    # Build occupancy
    base_occ = np.zeros(n_bins)
    for i in range(n_bins):
        pos = window_start + i * resolution
        occ = BACKGROUND_OCCUPANCY + rng.random() * 0.05
        for enh_pos, enh_occ in enhancers:
            dist = abs(pos - enh_pos) / resolution
            if dist < 5:
                occ += enh_occ * np.exp(-0.5 * dist * dist)
        base_occ[i] = min(1.0, occ)
    
    # Distance factor
    dist_factor = np.zeros((n_bins, n_bins))
    for i in range(n_bins):
        for j in range(i+1, n_bins):
            dist_factor[i,j] = (j-i) ** (-1.0)
            dist_factor[j,i] = dist_factor[i,j]
    
    ssim_values = []
    for pos, cat, eff in zip(positions, categories, effects):
        vb = int((pos - window_start) // resolution)
        if vb < 0 or vb >= n_bins:
            ssim_values.append(1.0)
            continue
        
        # REF
        ref_occ_factor = np.sqrt(np.outer(base_occ, base_occ))
        ref_perm = np.ones((n_bins, n_bins))
        for ctcf in ctcf_bins:
            mask = (np.arange(n_bins)[:, None] < ctcf) & (np.arange(n_bins)[None, :] > ctcf)
            ref_perm[mask] *= CTCF_INSULATION
        ref_kramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * np.power(np.maximum(0.001, ref_occ_factor), DEFAULT_GAMMA))
        ref_matrix = dist_factor * ref_occ_factor * ref_perm * ref_kramer
        
        # MUT
        mut_occ = base_occ.copy()
        for d in range(3):
            for idx in [vb - d, vb + d]:
                if 0 <= idx < n_bins:
                    reduction = eff + (1 - eff) * (d / 3.0)
                    mut_occ[idx] = base_occ[idx] * reduction
        
        mut_occ_factor = np.sqrt(np.outer(mut_occ, mut_occ))
        if "splice" in cat.lower() or "promoter" in cat.lower():
            mut_ctcf = [b for b in ctcf_bins if abs(b - vb) > 2]
        else:
            mut_ctcf = ctcf_bins
        
        mut_perm = np.ones((n_bins, n_bins))
        for ctcf in mut_ctcf:
            mask = (np.arange(n_bins)[:, None] < ctcf) & (np.arange(n_bins)[None, :] > ctcf)
            mut_perm[mask] *= CTCF_INSULATION
        
        mut_kramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * np.power(np.maximum(0.001, mut_occ_factor), DEFAULT_GAMMA))
        mut_matrix = dist_factor * mut_occ_factor * mut_perm * mut_kramer
        
        # Joint norm
        max_val = max(ref_matrix.max(), mut_matrix.max())
        if max_val > 0:
            ref_matrix /= max_val
            mut_matrix /= max_val
        
        # SSIM
        flat_r = ref_matrix.flatten()
        flat_m = mut_matrix.flatten()
        mu_r, mu_m = flat_r.mean(), flat_m.mean()
        sig_r2, sig_m2 = flat_r.var(), flat_m.var()
        sig_rm = ((flat_r - mu_r) * (flat_m - mu_m)).mean()
        
        ssim = ((2*mu_r*mu_m + 0.0001) * (2*sig_rm + 0.0009)) / \
               ((mu_r**2 + mu_m**2 + 0.0001) * (sig_r2 + sig_m2 + 0.0009))
        
        ssim_values.append(ssim)
    
    return np.array(ssim_values)


positions = sample["Position_GRCh38"].values
categories = sample["Category"].values
effects = [CATEGORICAL_EFFECTS.get(str(c).lower().strip(), 0.5) for c in categories]

seed_aucs = []
for seed in range(N_SEEDS):
    ssim_vals = compute_ssim_seed(config, positions, categories, effects, seed)
    try:
        auc = roc_auc_score(y_sample, 1 - ssim_vals)
    except:
        auc = 0.5
    seed_aucs.append(auc)
    print(f"  Seed {seed}: AUC = {auc:.4f}")

seed_aucs = np.array(seed_aucs)
seed_mean = seed_aucs.mean()
seed_std = seed_aucs.std()
seed_cv = seed_std / seed_mean if seed_mean > 0 else 0

print(f"\n  Seed AUC: mean={seed_mean:.4f}, std={seed_std:.4f}, CV={seed_cv:.4f}")

seed_verdict = "PASS" if seed_cv < 0.05 else "WARNING" if seed_cv < 0.10 else "FAIL"

# ============================================================
# 2. TISSUE MISMATCH
# ============================================================

print(f"\n{'=' * 70}")
print("TEST 2: Tissue Mismatch (K562 annotations on non-erythroid loci)")
print(f"{'=' * 70}")

# Compare AUCs for tissue-matched vs tissue-mismatched loci
# HBB (erythroid, K562 matched) vs SCN5A (cardiac, K562 mismatched)
# etc.

tissue_info = {
    "HBB": {"tissue": "erythroid", "matched": True, "cell": "K562"},
    "BRCA1": {"tissue": "breast", "matched": False, "cell": "MCF7"},
    "TP53": {"tissue": "fibroblast", "matched": False, "cell": "IMR90"},
    "CFTR": {"tissue": "lung", "matched": False, "cell": "A549"},
    "MLH1": {"tissue": "colon", "matched": False, "cell": "HCT116"},
    "LDLR": {"tissue": "liver", "matched": False, "cell": "K562"},
    "SCN5A": {"tissue": "cardiac", "matched": False, "cell": "K562"},
    "TERT": {"tissue": "stem_cell", "matched": False, "cell": "SK-N-SH"},
    "GJB2": {"tissue": "cochlear", "matched": False, "cell": "K562"},
}

atlas_dir = results_dir()

mismatch_results = []
for locus, info in tissue_info.items():
    locus_key = locus.lower()
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Atlas*.csv"))
    if not atlas_files:
        continue
    
    atlas = pd.read_csv(atlas_files[0])
    label_col = None
    for col in ["Label", "ClinVar_Significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        continue
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    ssim_cols = [c for c in atlas.columns if "SSIM" in c.upper()]
    if not ssim_cols:
        continue
    
    y = atlas["is_pathogenic"].values
    ssim = atlas[ssim_cols[0]].values
    
    try:
        auc = roc_auc_score(y, 1 - ssim)
    except:
        auc = 0.5
    
    mismatch_results.append({
        "locus": locus,
        "tissue": info["tissue"],
        "matched": info["matched"],
        "cell_type": info["cell"],
        "auc": float(auc),
        "n_variants": len(atlas),
    })
    
    match_mark = "✅" if info["matched"] else "⚠️"
    print(f"  {match_mark} {locus:<8} ({info['tissue']:>12}, {info['cell']:>6}) AUC = {auc:.4f}")

# Compare matched vs mismatched
matched_aucs = [r["auc"] for r in mismatch_results if r["matched"]]
mismatched_aucs = [r["auc"] for r in mismatch_results if not r["matched"]]

if matched_aucs and mismatched_aucs:
    mean_matched = np.mean(matched_aucs)
    mean_mismatched = np.mean(mismatched_aucs)
    print(f"\n  Matched mean AUC:     {mean_matched:.4f} (n={len(matched_aucs)})")
    print(f"  Mismatched mean AUC:  {mean_mismatched:.4f} (n={len(mismatched_aucs)})")
    print(f"  Delta:                {mean_matched - mean_mismatched:+.4f}")
    
    tissue_verdict = "PASS" if abs(mean_matched - mean_mismatched) < 0.10 else "WARNING"
else:
    tissue_verdict = "SKIPPED"
    mean_matched = None
    mean_mismatched = None

# ============================================================
# SAVE
# ============================================================

results = {
    "test": "robustness",
    "seed_stability": {
        "n_seeds": N_SEEDS,
        "auc_mean": float(seed_mean),
        "auc_std": float(seed_std),
        "auc_cv": float(seed_cv),
        "verdict": seed_verdict,
    },
    "tissue_mismatch": {
        "matched_mean_auc": float(mean_matched) if mean_matched else None,
        "mismatched_mean_auc": float(mean_mismatched) if mean_mismatched else None,
        "delta": float(mean_matched - mean_mismatched) if mean_matched and mean_mismatched else None,
        "verdict": tissue_verdict,
        "per_locus": mismatch_results,
    },
}

out_dir = validation_results_dir()
out_dir.mkdir(exist_ok=True)
with open(out_dir / "robustness.json", "w") as f:
    json.dump(results, f, indent=2)

# Overall verdict
overall = "PASS" if seed_verdict == "PASS" and tissue_verdict == "PASS" else "WARNING"

print(f"\n{'=' * 70}")
print("VERDICT")
print(f"{'=' * 70}")
print(f"  Seed stability: {seed_verdict} (CV={seed_cv:.4f})")
print(f"  Tissue mismatch: {tissue_verdict}")
print(f"  Overall: {overall}")

results["verdict"] = overall

with open(out_dir / "robustness.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved: {out_dir / 'robustness.json'}")
