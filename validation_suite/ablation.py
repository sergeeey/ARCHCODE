"""
Ablation Suite — Decomposing the signal in ARCHCODE SSIM.

Tests 5 ablation modes:
1. categorical (baseline) — real effect strength from category
2. position_only — fixed effect strength = 0.3 for ALL variants
3. uniform_medium — fixed effect strength = 0.5 for ALL variants
4. inverted — reversed effect strength (benign→strong, pathogenic→weak)
5. random — random effect strength per variant

Purpose: Which component drives the AUC?
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

# ============================================================
# EXACT TypeScript formula port
# ============================================================

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


def compute_ssim_for_variant(config, variant_pos, effect_strength, category, seed=42):
    """Compute SSIM for one variant using exact TypeScript formula."""
    rng = np.random.default_rng(seed)
    
    window_start = config["window"]["start"]
    resolution = config["window"]["resolution_bp"]
    n_bins = config["window"]["n_bins"]
    
    enhancers = [(e["position"], e["occupancy"]) for e in config["features"].get("enhancers", [])]
    ctcf_sites = [c["position"] for c in config["features"].get("ctcf_sites", [])]
    ctcf_bins = [int((p - window_start) // resolution) for p in ctcf_sites
                 if window_start <= p < window_start + n_bins * resolution]
    
    # Build occupancy landscape
    base_occ = np.zeros(n_bins)
    for i in range(n_bins):
        pos = window_start + i * resolution
        occ = BACKGROUND_OCCUPANCY + rng.random() * 0.05
        for enh_pos, enh_occ in enhancers:
            dist = abs(pos - enh_pos) / resolution
            if dist < 5:
                occ += enh_occ * np.exp(-0.5 * dist * dist)
        base_occ[i] = min(1.0, occ)
    
    variant_bin = int((variant_pos - window_start) // resolution)
    if variant_bin < 0 or variant_bin >= n_bins:
        return 1.0
    
    # REF matrix
    ref_matrix = _build_matrix(base_occ, ctcf_bins, ctcf_bins, -1, "", n_bins)
    
    # MUT occupancy
    mut_occ = base_occ.copy()
    for d in range(3):
        for idx in [variant_bin - d, variant_bin + d]:
            if 0 <= idx < n_bins:
                reduction = effect_strength + (1 - effect_strength) * (d / 3.0)
                mut_occ[idx] = base_occ[idx] * reduction
    
    # MUT CTCF
    if "splice" in category.lower() or "promoter" in category.lower():
        mut_ctcf = [b for b in ctcf_bins if abs(b - variant_bin) > 2]
    else:
        mut_ctcf = ctcf_bins
    
    mut_matrix = _build_matrix(mut_occ, ctcf_bins, mut_ctcf, variant_bin, category, n_bins)
    
    # Joint normalization
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
    
    return ssim


def _build_matrix(occupancy, ctcf_bins_ref, ctcf_bins_mut, variant_bin, category, n_bins):
    """Vectorized contact matrix — exact TypeScript formula."""
    dist_factor = np.zeros((n_bins, n_bins))
    for i in range(n_bins):
        for j in range(i+1, n_bins):
            dist_factor[i,j] = (j-i) ** (-1.0)
            dist_factor[j,i] = dist_factor[i,j]
    
    occ_factor = np.sqrt(np.outer(occupancy, occupancy))
    
    # CTCF
    perm = np.ones((n_bins, n_bins))
    active_ctcf = ctcf_bins_mut if (
        "splice" in category.lower() or "promoter" in category.lower()
    ) else ctcf_bins_ref
    
    for ctcf in active_ctcf:
        mask = (np.arange(n_bins)[:, None] < ctcf) & (np.arange(n_bins)[None, :] > ctcf)
        perm[mask] *= CTCF_INSULATION
    
    # Kramer
    kramer = 1 - K_BASE * (1 - DEFAULT_ALPHA * np.power(np.maximum(0.001, occ_factor), DEFAULT_GAMMA))
    
    return dist_factor * occ_factor * perm * kramer


def run_ablation(locus="HBB"):
    """Run all 5 ablation modes on a locus."""
    print(f"\n{'=' * 70}")
    print(f"ABLATION SUITE — {locus}")
    print(f"{'=' * 70}")
    
    # Find config
    config_dir = config_locus_dir()
    locus_key = locus.lower()
    config_files = list(config_dir.glob(f"{locus_key}*.json"))
    if not config_files:
        return {"test": "ablation", "locus": locus, "status": "SKIPPED", "reason": "no_config"}
    
    with open(config_files[0]) as f:
        config = json.load(f)
    
    # Find atlas
    atlas_dir = results_dir()
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Atlas*.csv"))
    if not atlas_files:
        return {"test": "ablation", "locus": locus, "status": "SKIPPED", "reason": "no_atlas"}
    
    atlas = pd.read_csv(atlas_files[0])
    
    # Labels
    label_col = None
    for col in ["Label", "ClinVar_Significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        return {"test": "ablation", "locus": locus, "status": "SKIPPED", "reason": "no_label"}
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    n_path = atlas["is_pathogenic"].sum()
    n_ben = (1 - atlas["is_pathogenic"]).sum()
    
    if n_path < 10 or n_ben < 10:
        return {"test": "ablation", "locus": locus, "status": "SKIPPED", "reason": "imbalanced"}
    
    # Get variants in window
    window_start = config["window"]["start"]
    window_end = window_start + config["window"]["n_bins"] * config["window"]["resolution_bp"]
    mask = (atlas["Position_GRCh38"] >= window_start) & (atlas["Position_GRCh38"] < window_end)
    variants = atlas[mask].copy()
    
    # Subsample for speed (stratified by label)
    MAX_VARIANTS = 100
    if len(variants) > MAX_VARIANTS:
        path_idx = variants[variants["is_pathogenic"] == 1].index
        ben_idx = variants[variants["is_pathogenic"] == 0].index
        n_path_sample = min(len(path_idx), MAX_VARIANTS // 2)
        n_ben_sample = MAX_VARIANTS - n_path_sample
        np.random.seed(42)
        sample_idx = np.concatenate([
            np.random.choice(path_idx, size=n_path_sample, replace=False),
            np.random.choice(ben_idx, size=n_ben_sample, replace=False),
        ])
        variants = variants.loc[sample_idx]
        print(f"  Subsampled to {len(variants)} variants ({n_path_sample}P/{n_ben_sample}B)")
    
    if len(variants) < 20:
        return {"test": "ablation", "locus": locus, "status": "SKIPPED", "reason": "too_few"}
    
    y = variants["is_pathogenic"].values
    
    # Define ablation modes
    modes = {
        "categorical": lambda cat: CATEGORICAL_EFFECTS.get(cat, 0.5),
        "position_only": lambda cat: 0.3,
        "uniform_medium": lambda cat: 0.5,
        "inverted": lambda cat: 1.0 - CATEGORICAL_EFFECTS.get(cat, 0.5),
        "random": lambda cat: float(np.random.random()),
    }
    
    results = {}
    t0 = time.time()
    
    for mode_name, eff_fn in modes.items():
        print(f"  Computing {mode_name}...")
        
        np.random.seed(42)
        lssim_values = []
        
        for _, row in variants.iterrows():
            pos = int(row["Position_GRCh38"])
            cat = str(row["Category"])
            eff = eff_fn(cat)
            
            ssim = compute_ssim_for_variant(config, pos, eff, cat, seed=42)
            lssim_values.append(ssim)
        
        lssim_values = np.array(lssim_values)
        
        try:
            auc = roc_auc_score(y, 1 - lssim_values)
        except:
            auc = 0.5
        
        delta_from_cat = auc - results.get("categorical_auc", auc)
        
        results[f"{mode_name}_auc"] = float(auc)
        results[f"{mode_name}_mean_lssim"] = float(lssim_values.mean())
        results[f"{mode_name}_std_lssim"] = float(lssim_values.std())
        results[f"{mode_name}_delta_from_categorical"] = float(delta_from_cat)
        
        print(f"    AUC = {auc:.4f}, mean SSIM = {lssim_values.mean():.4f}, delta = {delta_from_cat:+.4f}")
    
    results["runtime_seconds"] = time.time() - t0
    results["n_variants"] = len(variants)
    results["n_pathogenic"] = int(n_path)
    results["n_benign"] = int(n_ben)
    
    # Verdict
    cat_auc = results.get("categorical_auc", 0)
    pos_auc = results.get("position_only_auc", 0)
    delta = cat_auc - pos_auc
    
    if delta > 0.10:
        verdict = "WARNING"
        verdict_detail = f"Category adds +{delta:.3f} AUC over position-only. Physics adds value beyond position, but category mapping dominates."
    elif delta > 0.05:
        verdict = "WARNING"
        verdict_detail = f"Category adds +{delta:.3f} AUC. Marginal physics contribution."
    else:
        verdict = "FAIL"
        verdict_detail = f"Category adds only +{delta:.3f} AUC. Almost all signal is position-driven, not physics."
    
    # Check inverted
    inv_auc = results.get("inverted_auc", 0.5)
    if inv_auc < 0.4:
        verdict_detail += f" Inverted AUC={inv_auc:.3f} — model is anti-predictive when effect strengths are reversed."
    
    results["verdict"] = verdict
    results["verdict_detail"] = verdict_detail
    
    print(f"\n  Verdict: {verdict}")
    print(f"  Delta categorical vs position-only: {delta:+.4f}")
    
    # Save
    out_dir = validation_results_dir()
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / f"ablation_{locus_key}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return {
        "test": "ablation",
        "locus": locus,
        "status": "COMPLETED",
        "verdict": verdict,
        "categorical_auc": results.get("categorical_auc"),
        "position_only_auc": results.get("position_only_auc"),
        "inverted_auc": results.get("inverted_auc"),
        "delta": delta,
        "details": results,
    }


if __name__ == "__main__":
    import sys
    loci = sys.argv[1:] if len(sys.argv) > 1 else ["HBB", "TP53"]
    
    all_results = []
    for locus in loci:
        result = run_ablation(locus)
        all_results.append(result)
    
    print(f"\n{'=' * 70}")
    print("ABLATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"{'Locus':<8} {'Cat AUC':>8} {'Pos AUC':>8} {'Uniform AUC':>12} {'Inv AUC':>8} {'Delta':>8} {'Verdict':<8}")
    print("-" * 70)
    
    for r in all_results:
        if r["status"] != "COMPLETED":
            continue
        d = r.get("details", {})
        print(f"{r['locus']:<8} {r['categorical_auc']:>8.4f} {r['position_only_auc']:>8.4f} "
              f"{d.get('uniform_medium_auc', 0):>12.4f} {r['inverted_auc']:>8.4f} "
              f"{r['delta']:>+8.4f} {r['verdict']:<8}")
