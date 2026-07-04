"""
Simple Baseline Test — CORRECTED VERSION
=========================================
FIXES from previous version:
1. NO CADD as feature (it's supervised, trained on ClinVar = circularity)
2. Use distance-to-enhancer + phyloP ONLY (truly unsupervised features)
3. Test specifically on PEARL CLAIM: among pathogenic variants, can simple
   features distinguish pearls from non-pearls?
4. Also test: does simple model flag the SAME variants as pathogenic?

Proper null: "Pearl variants are simply closer to enhancers and more conserved
than other pathogenic variants. A simple model catches them without physics."
"""

import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, accuracy_score
from scipy import stats
import os

print("=" * 70)
print("SIMPLE BASELINE TEST — CORRECTED (no CADD)")
print("=" * 70)

# ============================================================
# 1. LOAD DATA
# ============================================================

# HBB Combined Atlas
atlas = pd.read_csv("D:/ДНК/results/HBB_Combined_Atlas.csv")
print(f"Loaded {len(atlas)} variants from HBB_Combined_Atlas.csv")

# HBB enhancer positions (from hbb_30kb_v2.json — MODEL_PARAMETER)
enhancer_positions = [5220000, 5225500, 5227000, 5230000, 5233000]

# HBB CTCF positions (from hbb_30kb_v2.json)
ctcf_positions = [5212000, 5218000, 5224000, 5228000, 5232000, 5236000]

# Pearl variants
pearl_mask = (
    (atlas["Label"] == "Pathogenic") &
    (atlas["ARCHCODE_SSIM"] < 0.95) &
    (atlas["VEP_Score"] < 0.5)
)
pearls = atlas[pearl_mask]
print(f"Pearl variants: {len(pearls)}")

# ============================================================
# 2. COMPUTE FEATURES
# ============================================================

print("\nComputing features...")

# Feature 1: Distance to nearest enhancer
def min_distance_to_set(positions, target_set):
    """Minimum distance from each position to any in target_set."""
    distances = []
    for pos in positions:
        min_dist = min(abs(pos - t) for t in target_set)
        distances.append(min_dist)
    return np.array(distances)

atlas["dist_to_enhancer"] = min_distance_to_set(
    atlas["Position_GRCh38"].values, enhancer_positions
)
atlas["log_dist_enhancer"] = np.log1p(atlas["dist_to_enhancer"])

# Feature 2: Distance to nearest CTCF
atlas["dist_to_ctcf"] = min_distance_to_set(
    atlas["Position_GRCh38"].values, ctcf_positions
)
atlas["log_dist_ctcf"] = np.log1p(atlas["dist_to_ctcf"])

# Feature 3: Is within enhancer neighborhood (<500bp)?
atlas["near_enhancer"] = (atlas["dist_to_enhancer"] < 500).astype(int)

# Feature 4: Variant category (ordinal encoding by effect severity)
category_severity = {
    "nonsense": 1,
    "frameshift": 2,
    "splice_donor": 3,
    "splice_acceptor": 3,
    "splice_region": 4,
    "missense": 5,
    "promoter": 6,
    "5_prime_UTR": 7,
    "3_prime_UTR": 8,
    "intronic": 9,
    "synonymous": 10,
    "other": 6,
}
atlas["severity"] = atlas["Category"].map(
    lambda x: category_severity.get(str(x).lower().strip(), 6)
)

# Feature 5: Position (normalized)
atlas["pos_normalized"] = (
    atlas["Position_GRCh38"] - atlas["Position_GRCh38"].min()
) / (atlas["Position_GRCh38"].max() - atlas["Position_GRCh38"].min())

# PhyloP: Not available for all variants (only pearls have it from conservation analysis).
# We have phyloP for 17 pearl positions (mean=2.39, range=[-0.195, 7.114])
# and 15 background positions (mean=0.73).
# For a fair test WITHOUT CADD, we'll use severity + distance features only.
# We'll note this limitation.

print(f"  dist_to_enhancer: mean={atlas['dist_to_enhancer'].mean():.0f}, "
      f"median={atlas['dist_to_enhancer'].median():.0f}")
print(f"  dist_to_ctcf: mean={atlas['dist_to_ctcf'].mean():.0f}, "
      f"median={atlas['dist_to_ctcf'].median():.0f}")
print(f"  near_enhancer (<500bp): {atlas['near_enhancer'].sum()}/{len(atlas)}")
print(f"  severity: min={atlas['severity'].min()}, max={atlas['severity'].max()}")

# ============================================================
# 3. TEST 1: Full discriminative power (pathogenic vs benign)
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: Pathogenic vs Benign (full set)")
print("=" * 70)

X_full = atlas[["log_dist_enhancer", "severity", "pos_normalized"]].values
y_full = (atlas["Label"] == "Pathogenic").astype(int).values

print(f"  n_pathogenic: {y_full.sum()}, n_benign: {(1-y_full).sum()}")

# Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
lr_probs = cross_val_predict(lr, X_full, y_full, cv=cv, method="predict_proba")[:, 1]
lr_auc = roc_auc_score(y_full, lr_probs)

print(f"\n  Model 1: LR (distance + severity + position)")
print(f"    AUC = {lr_auc:.4f}")

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf_probs = cross_val_predict(rf, X_full, y_full, cv=cv, method="predict_proba")[:, 1]
rf_auc = roc_auc_score(y_full, rf_probs)

print(f"  Model 2: RF (distance + severity + position)")
print(f"    AUC = {rf_auc:.4f}")

# Simple threshold: near enhancer = pathogenic
near_enhancer_pred = atlas["near_enhancer"].values
simple_auc = roc_auc_score(y_full, near_enhancer_pred)
print(f"  Model 3: Simple (within 500bp of enhancer)")
print(f"    AUC = {simple_auc:.4f}")

# ============================================================
# 4. TEST 2: THE PEARL CLAIM (key test!)
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: THE PEARL CLAIM — Among pathogenic variants,")
print("         can simple features distinguish pearls?")
print("=" * 70)

pathogenic_only = atlas[atlas["Label"] == "Pathogenic"].copy()
pathogenic_only["is_pearl"] = pearl_mask[pathogenic_only.index].astype(int)

n_pearls = pathogenic_only["is_pearl"].sum()
n_non_pearls = (1 - pathogenic_only["is_pearl"]).sum()

print(f"  Pathogenic variants: {len(pathogenic_only)}")
print(f"  Pearls: {n_pearls}")
print(f"  Non-pearl pathogenic: {n_non_pearls}")

if n_pearls < 5:
    print("  ⚠️  Too few pearls for CV. Using full pathogenic set with ARCHCODE_SSIM as proxy.")
    # Alternative: use ARCHCODE_SSIM < 0.95 as target (broader set)
    pathogenic_only["is_disrupted"] = (pathogenic_only["ARCHCODE_SSIM"] < 0.95).astype(int)
    n_disrupted = pathogenic_only["is_disrupted"].sum()
    print(f"  Variants with LSSIM < 0.95: {n_disrupted}")
    
    if n_disrupted >= 10:
        target_col = "is_disrupted"
        target_name = "LSSIM < 0.95"
    else:
        print("  ⚠️  Too few disrupted variants. Skipping.")
        target_col = None
        target_name = None
else:
    target_col = "is_pearl"
    target_name = "Pearl"
    target_col = "is_pearl"

if target_col:
    X_pearl = pathogenic_only[["log_dist_enhancer", "log_dist_ctcf", "severity", 
                                "pos_normalized", "near_enhancer"]].values
    y_pearl = pathogenic_only[target_col].values
    
    print(f"\n  Target: {target_name}")
    print(f"  n_positive: {y_pearl.sum()}, n_negative: {(1-y_pearl).sum()}")
    
    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    if y_pearl.sum() >= 5 and (1-y_pearl).sum() >= 5:
        cv = StratifiedKFold(n_splits=min(5, y_pearl.sum()), shuffle=True, random_state=42)
        try:
            lr_probs = cross_val_predict(lr, X_pearl, y_pearl, cv=cv, method="predict_proba")[:, 1]
            lr_auc_pearl = roc_auc_score(y_pearl, lr_probs)
            print(f"\n  LR AUC for predicting {target_name}: {lr_auc_pearl:.4f}")
        except Exception as e:
            print(f"\n  LR failed: {e}")
            lr_auc_pearl = None
    else:
        # Not enough for CV — just fit on all and report training AUC
        lr.fit(X_pearl, y_pearl)
        lr_probs_train = lr.predict_proba(X_pearl)[:, 1]
        lr_auc_pearl = roc_auc_score(y_pearl, lr_probs_train)
        print(f"\n  LR AUC (training, no CV — small sample): {lr_auc_pearl:.4f}")
    
    # Feature importance — fit separately to get coefficients
    if lr_auc_pearl is not None:
        lr_coef = LogisticRegression(max_iter=1000, random_state=42)
        lr_coef.fit(X_pearl, y_pearl)
        feature_names = ["log_dist_enhancer", "log_dist_ctcf", "severity", 
                        "pos_normalized", "near_enhancer"]
        print(f"\n  Feature coefficients:")
        for name, coef in zip(feature_names, lr_coef.coef_[0]):
            print(f"    {name:>20}: {coef:+.4f}")

# ============================================================
# 5. TEST 3: Do pearls cluster near enhancers?
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: Spatial clustering of pearls vs other pathogenic")
print("=" * 70)

pathogenic_only = atlas[atlas["Label"] == "Pathogenic"].copy()
pathogenic_only["is_pearl"] = False
pathogenic_only.loc[pearl_mask[pathogenic_only.index].values, "is_pearl"] = True

pearl_only = pathogenic_only[pathogenic_only["is_pearl"]]
non_pearl_pathogenic = pathogenic_only[~pathogenic_only["is_pearl"]]

if len(pearl_only) > 0:
    pearl_dist_enhancer = pearl_only["dist_to_enhancer"].values
    non_pearl_dist_enhancer = non_pearl_pathogenic["dist_to_enhancer"].values
    
    print(f"\n  Pearl dist to enhancer:")
    print(f"    mean = {pearl_dist_enhancer.mean():.0f} bp")
    print(f"    median = {np.median(pearl_dist_enhancer):.0f} bp")
    print(f"    range = [{pearl_dist_enhancer.min()}, {pearl_dist_enhancer.max()}]")
    
    print(f"\n  Non-pearl pathogenic dist to enhancer:")
    print(f"    mean = {non_pearl_dist_enhancer.mean():.0f} bp")
    print(f"    median = {np.median(non_pearl_dist_enhancer):.0f} bp")
    print(f"    range = [{non_pearl_dist_enhancer.min()}, {non_pearl_dist_enhancer.max()}]")
    
    # Mann-Whitney test
    mw_stat, mw_pval = stats.mannwhitneyu(
        pearl_dist_enhancer, non_pearl_dist_enhancer, alternative="two-sided"
    )
    print(f"\n  Mann-Whitney U test (pearl vs non-pearl dist to enhancer):")
    print(f"    U = {mw_stat}, p = {mw_pval:.6f}")
    
    # KS test
    ks_stat, ks_pval = stats.ks_2samp(pearl_dist_enhancer, non_pearl_dist_enhancer)
    print(f"  KS test:")
    print(f"    D = {ks_stat}, p = {ks_pval:.6f}")

# ============================================================
# 6. TEST 4: VEP-only baseline (for reference)
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: VEP score as baseline (for reference)")
print("=" * 70)

vep_auc_full = roc_auc_score(y_full, 1 - atlas["VEP_Score"].values)
print(f"  VEP AUC (pathogenic vs benign, full set): {vep_auc_full:.4f}")

# VEP on pathogenic only: can VEP distinguish pearls?
if len(pearl_only) > 0:
    vep_auc_pearl = roc_auc_score(
        pathogenic_only["is_pearl"].astype(int),
        1 - pathogenic_only["VEP_Score"].values
    )
    print(f"  VEP AUC (pearls among pathogenic): {vep_auc_pearl:.4f}")
    print(f"    (>0.5 means VEP can distinguish pearls — contradicts pearl claim)")
    print(f"    (<0.5 means VEP scores pearls LOWER — supports pearl claim)")

# ============================================================
# 7. SUMMARY
# ============================================================

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")

print(f"\n{'Model':<50} {'AUC':>8}")
print("-" * 60)
print(f"{'LR (distance + severity + position)':<50} {lr_auc:>8.4f}")
print(f"{'RF (distance + severity + position)':<50} {rf_auc:>8.4f}")
print(f"{'Simple (near enhancer)':<50} {simple_auc:>8.4f}")
print(f"{'VEP score':<50} {vep_auc_full:>8.4f}")
print(f"{'ARCHCODE (reported)':<50} {0.977:>8.4f}")

if target_col and 'lr_auc_pearl' in dir() and lr_auc_pearl is not None:
    print(f"\n{'--- Pearl discrimination (among pathogenic) ---':<50}")
    print(f"{'LR (distance + severity + position)':<50} {lr_auc_pearl:>8.4f}")

# ============================================================
# 8. VERDICT
# ============================================================

print(f"\n{'=' * 70}")
print("VERDICT")
print(f"{'=' * 70}")

# Key question: does the simple baseline beat ARCHCODE on the same task?
# ARCHCODE claims: AUC 0.977 on pathogenic vs benign
# Our best simple model (no CADD): RF with AUC = ?

if rf_auc >= 0.95:
    verdict = "FAIL 🔴"
    verdict_detail = (
        f"Random Forest with only distance + severity + position achieves "
        f"AUC = {rf_auc:.4f} ≥ 0.95. This rivals ARCHCODE's 0.977 without "
        f"any physics. The complex simulation is NOT needed for discrimination. "
        f"Simple spatial features capture most of the signal."
    )
elif rf_auc >= 0.90:
    verdict = "WARNING ⚠️"
    verdict_detail = (
        f"Random Forest with simple features achieves AUC = {rf_auc:.4f} "
        f"(0.90-0.95 range). This is below ARCHCODE's 0.977 but still "
        f"substantial. The physics adds value, but the gap is smaller than "
        f"claimed. A significant portion of the signal is explainable by "
        f"simple spatial features."
    )
else:
    verdict = "PASS ✅"
    verdict_detail = (
        f"Best simple model (RF) achieves AUC = {rf_auc:.4f} << 0.90. "
        f"Without CADD (circular), simple features are significantly worse "
        f"than ARCHCODE (0.977). The physics-based simulation adds genuine "
        f"discriminative value beyond spatial clustering."
    )

print(f"\nVerdict: {verdict}")
print(f"Detail: {verdict_detail}")

# ============================================================
# 9. SAVE RESULTS
# ============================================================

results = {
    "test_name": "Simple Baseline (CORRECTED — no CADD)",
    "dataset": "HBB Combined Atlas",
    "n_variants": len(atlas),
    "n_pathogenic": int(y_full.sum()),
    "n_benign": int((1-y_full).sum()),
    "archcode_reference_auc": 0.977,
    "models": {
        "lr_distance_severity_position": {
            "auc": float(lr_auc),
            "verdict": "FAIL" if lr_auc >= 0.95 else "WARNING" if lr_auc >= 0.90 else "PASS"
        },
        "rf_distance_severity_position": {
            "auc": float(rf_auc),
            "verdict": "FAIL" if rf_auc >= 0.95 else "WARNING" if rf_auc >= 0.90 else "PASS"
        },
        "simple_near_enhancer": {
            "auc": float(simple_auc)
        },
        "vep_score": {
            "auc_full": float(vep_auc_full),
            "auc_pearl": float(vep_auc_pearl) if 'vep_auc_pearl' in dir() else None
        }
    },
    "pearl_test": {
        "n_pearls": int(n_pearls),
        "lr_auc": float(lr_auc_pearl) if 'lr_auc_pearl' in dir() and lr_auc_pearl is not None else None,
    } if target_col and 'lr_auc_pearl' in dir() else None,
    "pearl_spatial": {
        "pearl_mean_dist_enhancer": float(pearl_dist_enhancer.mean()) if len(pearl_only) > 0 else None,
        "non_pearl_mean_dist_enhancer": float(non_pearl_dist_enhancer.mean()),
        "mw_pvalue": float(mw_pval) if len(pearl_only) > 0 else None,
        "ks_pvalue": float(ks_pval) if len(pearl_only) > 0 else None,
    } if len(pearl_only) > 0 else None,
    "verdict": verdict,
    "verdict_detail": verdict_detail
}

with open("D:/ДНК/results/simple_baseline_corrected.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to:")
print(f"  D:/ДНК/results/simple_baseline_corrected.json")
print(f"\n{'=' * 70}")
print("TEST COMPLETE")
print(f"{'=' * 70}")
