#!/usr/bin/env python3
"""
Independent reproduction of HBB ROC/AUC analysis.
Goal: verify the claimed AUC = 0.9766 from roc_unified.json
"""

import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve, auc
from pathlib import Path

BASE = Path(__file__).parent.parent

# ============================================================
# 1. Load data
# ============================================================
csv_path = BASE / "results" / "HBB_Unified_Atlas_95kb.csv"
df = pd.read_csv(csv_path)

print("=" * 65)
print("HBB ROC/AUC INDEPENDENT REPRODUCTION")
print("=" * 65)
print(f"\nFile: {csv_path.name}")
print(f"Total variants: {len(df)}")
print(f"Columns: {list(df.columns)}")

# ============================================================
# 2. Classify variants
# ============================================================
print(f"\n--- Label distribution ---")
print(df["Label"].value_counts().to_string())

print(f"\n--- ClinVar_Significance distribution (raw) ---")
print(df["ClinVar_Significance"].value_counts().to_string())

y_true = (df["Label"] == "Pathogenic").astype(int).values
n_path = y_true.sum()
n_benign = (y_true == 0).sum()
print(f"\nBinary: Pathogenic={n_path}, Benign={n_benign}")

# ============================================================
# 3. ROC with ARCHCODE_SSIM (the original method)
# ============================================================
ssim = df["ARCHCODE_SSIM"].astype(float).values
y_score_ssim = 1.0 - ssim  # higher disruption = more pathogenic

fpr, tpr, thresholds = roc_curve(y_true, y_score_ssim)
auc_ssim = auc(fpr, tpr)

# Cross-check with sklearn shortcut
auc_ssim_sk = roc_auc_score(y_true, y_score_ssim)

print(f"\n--- ROC using ARCHCODE_SSIM (original method) ---")
print(f"  AUC (manual fpr/tpr):    {auc_ssim:.6f}")
print(f"  AUC (sklearn shortcut):  {auc_ssim_sk:.6f}")
print(f"  Claimed AUC:             0.9766")
print(
    f"  Match: {'YES' if round(auc_ssim, 4) == 0.9766 else 'NO'} (rounded to 4 dp: {round(auc_ssim, 4)})"
)

# Youden's J
j_scores = tpr - fpr
best_idx = np.argmax(j_scores)
best_ssim = 1.0 - thresholds[best_idx]
print(f"\n  Youden optimal SSIM threshold: {best_ssim:.4f}")
print(f"  Sensitivity at optimal: {tpr[best_idx]:.4f}")
print(f"  Specificity at optimal: {1.0 - fpr[best_idx]:.4f}")

# Mean SSIM by group
path_ssim = ssim[y_true == 1]
benign_ssim = ssim[y_true == 0]
print(f"\n  Mean SSIM (Pathogenic): {path_ssim.mean():.4f}")
print(f"  Mean SSIM (Benign):     {benign_ssim.mean():.4f}")
print(f"  Separation (delta):     {benign_ssim.mean() - path_ssim.mean():.4f}")

# ============================================================
# 4. ROC with ARCHCODE_LSSIM
# ============================================================
lssim = df["ARCHCODE_LSSIM"].astype(float).values
y_score_lssim = 1.0 - lssim

auc_lssim = roc_auc_score(y_true, y_score_lssim)

path_lssim = lssim[y_true == 1]
benign_lssim = lssim[y_true == 0]

print(f"\n--- ROC using ARCHCODE_LSSIM ---")
print(f"  AUC: {auc_lssim:.6f}")
print(f"  Mean LSSIM (Pathogenic): {path_lssim.mean():.4f}")
print(f"  Mean LSSIM (Benign):     {benign_lssim.mean():.4f}")
print(f"  Separation (delta):      {benign_lssim.mean() - path_lssim.mean():.4f}")

# ============================================================
# 5. POSITION_ONLY control (no category weighting)
# ============================================================
pos_csv = BASE / "results" / "HBB_Unified_Atlas_95kb_POSITION_ONLY.csv"
if pos_csv.exists():
    df_pos = pd.read_csv(pos_csv)
    y_true_pos = (df_pos["Label"] == "Pathogenic").astype(int).values
    ssim_pos = df_pos["ARCHCODE_SSIM"].astype(float).values
    lssim_pos = df_pos["ARCHCODE_LSSIM"].astype(float).values

    auc_pos_ssim = roc_auc_score(y_true_pos, 1.0 - ssim_pos)
    auc_pos_lssim = roc_auc_score(y_true_pos, 1.0 - lssim_pos)

    print(f"\n--- POSITION_ONLY control ---")
    print(f"  Variants: {len(df_pos)}")
    print(f"  AUC (SSIM):  {auc_pos_ssim:.6f}")
    print(f"  AUC (LSSIM): {auc_pos_lssim:.6f}")
    print(f"  Mean SSIM (Path): {ssim_pos[y_true_pos == 1].mean():.4f}")
    print(f"  Mean SSIM (Ben):  {ssim_pos[y_true_pos == 0].mean():.4f}")
    print(f"\n  Category weighting adds: {auc_ssim - auc_pos_ssim:+.6f} AUC (SSIM)")
    print(f"  Category weighting adds: {auc_lssim - auc_pos_lssim:+.6f} AUC (LSSIM)")
else:
    print(f"\n  POSITION_ONLY file not found: {pos_csv}")

# ============================================================
# 6. Additional controls: UNIFORM_MEDIUM, INVERTED, RANDOM
# ============================================================
controls = {
    "UNIFORM_MEDIUM": BASE / "results" / "HBB_Unified_Atlas_95kb_UNIFORM_MEDIUM.csv",
    "INVERTED": BASE / "results" / "HBB_Unified_Atlas_95kb_INVERTED.csv",
    "RANDOM": BASE / "results" / "HBB_Unified_Atlas_95kb_RANDOM.csv",
}

print(f"\n--- Ablation controls ---")
for name, path in controls.items():
    if path.exists():
        dfc = pd.read_csv(path)
        yt = (dfc["Label"] == "Pathogenic").astype(int).values
        sc = 1.0 - dfc["ARCHCODE_SSIM"].astype(float).values
        a = roc_auc_score(yt, sc)
        print(f"  {name:20s}: AUC(SSIM) = {a:.6f}")
    else:
        print(f"  {name:20s}: file not found")

# ============================================================
# 7. Effect_Source breakdown
# ============================================================
print(f"\n--- Effect_Source distribution ---")
print(df["Effect_Source"].value_counts().to_string())

# ============================================================
# 8. CADD comparison
# ============================================================
cadd = df["CADD_Phred"].astype(float).values
valid_cadd = cadd > 0  # -1 means missing
if valid_cadd.sum() > 50:
    auc_cadd = roc_auc_score(y_true[valid_cadd], cadd[valid_cadd])
    print(f"\n--- CADD comparison (n={valid_cadd.sum()} with valid CADD) ---")
    print(f"  AUC (CADD):     {auc_cadd:.6f}")
    print(f"  AUC (SSIM):     {roc_auc_score(y_true[valid_cadd], 1.0 - ssim[valid_cadd]):.6f}")
    print(f"  AUC (LSSIM):    {roc_auc_score(y_true[valid_cadd], 1.0 - lssim[valid_cadd]):.6f}")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 65}")
print("REPRODUCTION SUMMARY")
print(f"{'=' * 65}")
print(f"  Claimed AUC:              0.9766")
print(f"  Reproduced AUC (SSIM):    {round(auc_ssim, 4)}")
print(f"  Reproduced AUC (LSSIM):   {round(auc_lssim, 4)}")
match = "CONFIRMED" if round(auc_ssim, 4) == 0.9766 else "MISMATCH"
print(f"  Verdict:                  {match}")
print(f"{'=' * 65}")
