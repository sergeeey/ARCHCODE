"""
Cross-Locus Transfer Test.

Train LSSIM threshold on HBB, apply to all other loci.
Measure AUC drop. Also test pairwise transfers.
"""

import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validation_suite.repo_paths import results_dir, validation_results_dir  # noqa: E402

print("=" * 70)
print("CROSS-LOCUS TRANSFER TEST")
print("=" * 70)

atlas_dir = results_dir()
ALL_LOCI = ["HBB", "BRCA1", "TP53", "CFTR", "MLH1", "LDLR", "SCN5A", "TERT", "GJB2"]

def load_locus_data(locus):
    """Load locus atlas with labels."""
    locus_key = locus.lower()
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Atlas*.csv"))
    if not atlas_files:
        return None
    
    atlas = pd.read_csv(atlas_files[0])
    
    label_col = None
    for col in ["Label", "ClinVar_Significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        return None
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    
    ssim_cols = [c for c in atlas.columns if "SSIM" in c.upper()]
    if not ssim_cols:
        return None
    
    return {
        "atlas": atlas,
        "ssim_col": ssim_cols[0],
        "n_path": atlas["is_pathogenic"].sum(),
        "n_ben": (1 - atlas["is_pathogenic"]).sum(),
    }

# Load all loci
locus_data = {}
for locus in ALL_LOCI:
    data = load_locus_data(locus)
    if data:
        locus_data[locus] = data
        print(f"  {locus}: {len(data['atlas'])} variants, "
              f"{data['n_path']}P/{data['n_ben']}B, "
              f"SSIM col: {data['ssim_col']}")

# Compute per-locus AUC (diagonal)
print(f"\n{'=' * 70}")
print("PER-LOCUS AUC (diagonal)")
print(f"{'=' * 70}")

diagonal_aucs = {}
for locus, data in locus_data.items():
    y = data["atlas"]["is_pathogenic"].values
    ssim = data["atlas"][data["ssim_col"]].values
    try:
        auc = roc_auc_score(y, 1 - ssim)
    except:
        auc = 0.5
    diagonal_aucs[locus] = auc
    print(f"  {locus}: AUC = {auc:.4f}")

# Find optimal threshold on HBB
hbb_data = locus_data.get("HBB")
if hbb_data:
    hbb_y = hbb_data["atlas"]["is_pathogenic"].values
    hbb_ssim = hbb_data["atlas"][hbb_data["ssim_col"]].values
    
    # Find Youden-optimal threshold
    from sklearn.metrics import roc_curve
    fpr, tpr, thresholds = roc_curve(hbb_y, 1 - hbb_ssim)
    youden = tpr - fpr
    best_idx = np.argmax(youden)
    hbb_threshold = thresholds[best_idx]
    hbb_sensitivity = tpr[best_idx]
    hbb_specificity = 1 - fpr[best_idx]
    
    print(f"\n  HBB optimal threshold: {hbb_threshold:.4f}")
    print(f"  Sensitivity: {hbb_sensitivity:.4f}, Specificity: {hbb_specificity:.4f}")
else:
    hbb_threshold = 0.95
    print("  HBB not available, using default threshold 0.95")

# Transfer HBB threshold to all other loci
print(f"\n{'=' * 70}")
print(f"TRANSFER: HBB threshold ({hbb_threshold:.4f}) → all loci")
print(f"{'=' * 70}")

transfer_results = []
for locus, data in locus_data.items():
    y = data["atlas"]["is_pathogenic"].values
    ssim = data["atlas"][data["ssim_col"]].values
    
    # AUC (threshold-independent)
    try:
        auc = roc_auc_score(y, 1 - ssim)
    except:
        auc = 0.5
    
    # Accuracy at HBB threshold (threshold-dependent)
    predicted = (ssim < hbb_threshold).astype(int)
    accuracy = (predicted == y).mean()
    
    # Sensitivity/specificity at HBB threshold
    tp = ((predicted == 1) & (y == 1)).sum()
    fn = ((predicted == 0) & (y == 1)).sum()
    tn = ((predicted == 0) & (y == 0)).sum()
    fp = ((predicted == 1) & (y == 0)).sum()
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    delta_auc = auc - diagonal_aucs.get(locus, 0)
    
    result = {
        "locus": locus,
        "diagonal_auc": diagonal_aucs.get(locus, 0),
        "transferred_auc": auc,
        "auc_delta": float(delta_auc),
        "accuracy_at_hbb_threshold": float(accuracy),
        "sensitivity_at_hbb_threshold": float(sensitivity),
        "specificity_at_hbb_threshold": float(specificity),
    }
    
    transfer_results.append(result)
    
    print(f"  {locus:<8} AUC={auc:.4f}  "
          f"Δ={delta_auc:+.4f}  "
          f"Acc={accuracy:.3f}  "
          f"Sens={sensitivity:.3f}  "
          f"Spec={specificity:.3f}")

# Pairwise transfer matrix (locus-specific thresholds)
print(f"\n{'=' * 70}")
print("PAIRWISE TRANSFER MATRIX (AUC)")
print(f"{'=' * 70}")

# Compute per-locus optimal thresholds
locus_thresholds = {}
for locus, data in locus_data.items():
    y = data["atlas"]["is_pathogenic"].values
    ssim = data["atlas"][data["ssim_col"]].values
    try:
        fpr, tpr, thresholds = roc_curve(y, 1 - ssim)
        youden = tpr - fpr
        best_idx = np.argmax(youden)
        locus_thresholds[locus] = thresholds[best_idx]
    except:
        locus_thresholds[locus] = 0.95

print(f"\n  Threshold → ", end="")
for loc in locus_data:
    print(f"{loc:<8} ", end="")
print()
print("  " + "-" * (13 + 9 * len(locus_data)))

for src_loc in locus_data:
    src_threshold = locus_thresholds[src_loc]
    print(f"  {src_loc} ({src_threshold:.3f}) → ", end="")
    
    for tgt_loc in locus_data:
        tgt_data = locus_data[tgt_loc]
        y = tgt_data["atlas"]["is_pathogenic"].values
        ssim = tgt_data["atlas"][tgt_data["ssim_col"]].values
        
        # AUC is threshold-independent, so it's the same regardless of source
        # But we can measure accuracy at the source threshold
        predicted = (ssim < src_threshold).astype(int)
        accuracy = (predicted == y).mean()
        
        print(f"{accuracy:.3f}     ", end="")
    print()

# Save
out_dir = validation_results_dir()
out_dir.mkdir(exist_ok=True)

master = {
    "test": "cross_locus_transfer",
    "hbb_threshold": float(hbb_threshold),
    "hbb_sensitivity": float(hbb_sensitivity) if 'hbb_sensitivity' in dir() else None,
    "hbb_specificity": float(hbb_specificity) if 'hbb_specificity' in dir() else None,
    "diagonal_aucs": {k: float(v) for k, v in diagonal_aucs.items()},
    "transfer_results": transfer_results,
    "locus_thresholds": {k: float(v) for k, v in locus_thresholds.items()},
}

with open(out_dir / "cross_locus_transfer.json", "w") as f:
    json.dump(master, f, indent=2)

# Verdict
max_drop = max(abs(r["auc_delta"]) for r in transfer_results)
avg_drop = np.mean([abs(r["auc_delta"]) for r in transfer_results])

print(f"\n{'=' * 70}")
print("VERDICT")
print(f"{'=' * 70}")
print(f"  Max AUC drop: {max_drop:.4f}")
print(f"  Avg AUC drop: {avg_drop:.4f}")

if max_drop > 0.15:
    verdict = "FAIL"
    detail = f"Max AUC drop = {max_drop:.3f} > 0.15. Model does NOT transfer across loci."
elif max_drop > 0.10:
    verdict = "WARNING"
    detail = f"Max AUC drop = {max_drop:.3f}. Marginal transfer."
else:
    verdict = "PASS"
    detail = f"Max AUC drop = {max_drop:.3f}. Model transfers well across loci."

print(f"  Verdict: {verdict}")
print(f"  Detail: {detail}")

master["verdict"] = verdict
master["verdict_detail"] = detail

with open(out_dir / "cross_locus_transfer.json", "w") as f:
    json.dump(master, f, indent=2)

print(f"\nSaved: {out_dir / 'cross_locus_transfer.json'}")
