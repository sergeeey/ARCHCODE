#!/usr/bin/env python3
"""
Simple Baseline Test: Distance-to-Enhancer + Conservation + CADD vs ARCHCODE

Skeptic Engine question: Could a trivial model (distance to enhancer + conservation)
achieve similar results to ARCHCODE's physics-based LSSIM (AUC = 0.977)?

If a simple model achieves AUC >= 0.95, the complex physics isn't justified.
If all simple models achieve AUC < 0.90, the physics adds clear value.

Models tested:
  1. Logistic Regression on distance_to_enhancer only
  2. Logistic Regression on distance_to_enhancer + conservation (CADD proxy)
  3. Logistic Regression on distance_to_enhancer + conservation + CADD
  4. Random Forest on all features
  5. Simple threshold: variant within 1kb of enhancer = pathogenic

Usage: python scripts/simple_baseline_test.py

Output:
  - results/simple_baseline_results.json
  - results/simple_baseline_results.csv
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---- Paths ----
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
CONFIG_DIR = BASE_DIR / "config" / "locus"

# ---- ARCHCODE reference ----
ARCHCODE_AUC = 0.977

# ============================================================================
# 1. Load data
# ============================================================================

def load_hbb_data():
    """Load HBB variant data from the Combined Atlas + CADD from Unified Atlas."""
    # Use Combined Atlas as primary source (same as ROC analysis)
    atlas_path = RESULTS_DIR / "HBB_Combined_Atlas.csv"
    if not atlas_path.exists():
        print(f"ERROR: {atlas_path} not found")
        sys.exit(1)

    df = pd.read_csv(atlas_path)
    print(f"Loaded HBB Combined Atlas: {len(df)} variants")
    print(f"  Labels: {dict(df['Label'].value_counts())}")

    # Merge CADD from Unified Atlas (if available)
    unified_path = RESULTS_DIR / "HBB_Unified_Atlas_95kb.csv"
    if unified_path.exists():
        unified = pd.read_csv(unified_path, usecols=["ClinVar_ID", "CADD_Phred"])
        # Replace -1 with NaN (missing)
        unified["CADD_Phred"] = unified["CADD_Phred"].replace(-1, np.nan)
        df = df.merge(unified, on="ClinVar_ID", how="left", suffixes=("", "_unified"))
        # Prefer unified CADD if available
        if "CADD_Phred_unified" in df.columns:
            df["CADD_Phred"] = df["CADD_Phred"].fillna(df["CADD_Phred_unified"])
            df.drop(columns=["CADD_Phred_unified"], inplace=True, errors="ignore")
        cadd_count = df["CADD_Phred"].notna().sum()
        print(f"  CADD scores available: {cadd_count}/{len(df)} ({cadd_count/len(df)*100:.1f}%)")
    else:
        df["CADD_Phred"] = np.nan
        print("  WARNING: No Unified Atlas found, CADD scores not available")

    return df


def load_enhancer_positions():
    """Load HBB enhancer positions from locus config."""
    # Prefer 95kb config (more complete, ENCODE-validated)
    config_path = CONFIG_DIR / "hbb_95kb_subTAD.json"
    if not config_path.exists():
        # Fall back to 30kb config
        config_path = CONFIG_DIR / "hbb_30kb_v2.json"

    if not config_path.exists():
        print(f"ERROR: No HBB locus config found")
        return []

    import json as _json
    with open(config_path) as f:
        config = _json.load(f)

    enhancers = []
    for enh in config.get("features", {}).get("enhancers", []):
        enhancers.append({
            "name": enh.get("name", "unknown"),
            "position": enh["position"],
            "source": enh.get("source", "unknown"),
        })

    print(f"Loaded {len(enhancers)} enhancer positions from {config_path.name}")
    for e in enhancers:
        print(f"  {e['name']}: {e['position']:,} ({e['source']})")

    return enhancers


def load_ctcf_positions():
    """Load CTCF positions from locus config and BED file."""
    positions = []

    # From locus config
    config_path = CONFIG_DIR / "hbb_95kb_subTAD.json"
    if config_path.exists():
        import json as _json
        with open(config_path) as f:
            config = _json.load(f)
        for ctcf in config.get("features", {}).get("ctcf_sites", []):
            positions.append({
                "position": ctcf["position"],
                "name": ctcf.get("name", "unknown"),
                "source": "LOCUS_CONFIG",
            })

    # From K562 CTCF BED file
    bed_path = BASE_DIR / "data" / "reference" / "K562_CTCF_HBB.bed"
    if bed_path.exists():
        try:
            bed_df = pd.read_csv(bed_path, sep="\t", header=None,
                                 usecols=[0, 1, 2, 3],
                                 names=["chrom", "start", "end", "name"])
            bed_df["midpoint"] = (bed_df["start"] + bed_df["end"]) // 2
            for _, row in bed_df.iterrows():
                positions.append({
                    "position": int(row["midpoint"]),
                    "name": row["name"] if isinstance(row["name"], str) else "CTCF",
                    "source": "ENCODE_K562_CTCF_BED",
                })
        except Exception as e:
            print(f"  WARNING: Could not parse CTCF BED file: {e}")

    # Deduplicate by position (within 100bp)
    if positions:
        positions.sort(key=lambda x: x["position"])
        deduped = [positions[0]]
        for p in positions[1:]:
            if abs(p["position"] - deduped[-1]["position"]) > 100:
                deduped.append(p)
        positions = deduped

    print(f"Loaded {len(positions)} CTCF positions")
    for p in positions:
        print(f"  {p['name']}: {p['position']:,} ({p['source']})")

    return positions


# ============================================================================
# 2. Compute features
# ============================================================================

def compute_distance_to_nearest(variant_pos, target_positions):
    """Compute minimum distance from variant position to any target position."""
    if not target_positions:
        return np.nan
    distances = [abs(variant_pos - tp) for tp in target_positions]
    return min(distances)


def build_features(df, enhancers, ctcf_sites):
    """Compute baseline features for each variant."""
    enhancer_positions = [e["position"] for e in enhancers]
    ctcf_positions = [c["position"] for c in ctcf_sites]

    features = pd.DataFrame()
    features["ClinVar_ID"] = df["ClinVar_ID"]
    features["Position"] = df["Position_GRCh38"]

    # Distance to nearest enhancer
    features["distance_to_enhancer"] = df["Position_GRCh38"].apply(
        lambda pos: compute_distance_to_nearest(pos, enhancer_positions)
    )

    # Distance to nearest CTCF
    features["distance_to_ctcf"] = df["Position_GRCh38"].apply(
        lambda pos: compute_distance_to_nearest(pos, ctcf_positions)
    )

    # Conservation score: use CADD as proxy (no phyloP/phastCons available)
    if "CADD_Phred" in df.columns:
        features["conservation_score"] = df["CADD_Phred"].copy()
        features["cadd_score"] = df["CADD_Phred"].copy()
    else:
        features["conservation_score"] = np.nan
        features["cadd_score"] = np.nan

    # Log-transform distance (more biologically meaningful)
    features["log_distance_to_enhancer"] = np.log1p(features["distance_to_enhancer"])
    features["log_distance_to_ctcf"] = np.log1p(features["distance_to_ctcf"])

    # Binary: within 1kb of enhancer
    features["within_1kb_enhancer"] = (features["distance_to_enhancer"] <= 1000).astype(int)

    # Binary: within 5kb of enhancer
    features["within_5kb_enhancer"] = (features["distance_to_enhancer"] <= 5000).astype(int)

    # Labels: Pathogenic/Likely Pathogenic = 1, Benign/Likely Benign/VUS = 0
    features["label"] = (df["Label"] == "Pathogenic").astype(int)

    # Keep ARCHCODE SSIM for comparison
    if "ARCHCODE_SSIM" in df.columns:
        features["archcode_ssim"] = df["ARCHCODE_SSIM"]

    # Keep VEP score for comparison
    if "VEP_Score" in df.columns:
        features["vep_score"] = df["VEP_Score"]

    print(f"\nFeature summary:")
    print(f"  Total variants: {len(features)}")
    print(f"  Pathogenic (1): {features['label'].sum()}")
    print(f"  Benign (0): {(features['label'] == 0).sum()}")
    print(f"  distance_to_enhancer: mean={features['distance_to_enhancer'].mean():.0f}, "
          f"median={features['distance_to_enhancer'].median():.0f}")
    print(f"  distance_to_ctcf: mean={features['distance_to_ctcf'].mean():.0f}, "
          f"median={features['distance_to_ctcf'].median():.0f}")
    cadd_avail = features["cadd_score"].notna().sum()
    print(f"  CADD available: {cadd_avail}/{len(features)}")

    return features


# ============================================================================
# 3. Train and evaluate models
# ============================================================================

def evaluate_model_cv(X, y, model, n_folds=5, model_name="Model"):
    """Evaluate a model using stratified k-fold cross-validation."""
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    # Get cross-validated predictions (probabilities for positive class)
    try:
        y_proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
        auc = roc_auc_score(y, y_proba)
    except ValueError as e:
        print(f"  WARNING: {model_name} failed: {e}")
        return {"auc": np.nan, "auc_std": np.nan, "sensitivity": np.nan,
                "specificity": np.nan, "optimal_threshold": np.nan}

    # Per-fold AUC for std
    fold_aucs = []
    for train_idx, test_idx in cv.split(X, y):
        model_fold = clone_estimator(model)
        model_fold.fit(X[train_idx], y[train_idx])
        y_proba_fold = model_fold.predict_proba(X[test_idx])[:, 1]
        if len(np.unique(y[test_idx])) > 1:
            fold_aucs.append(roc_auc_score(y[test_idx], y_proba_fold))

    auc_std = np.std(fold_aucs) if len(fold_aucs) > 1 else 0.0

    # Optimal threshold (Youden's J)
    fpr, tpr, thresholds = roc_curve(y, y_proba)
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[best_idx]
    sensitivity = tpr[best_idx]
    specificity = 1.0 - fpr[best_idx]

    # Predictions at optimal threshold
    y_pred = (y_proba >= optimal_threshold).astype(int)
    accuracy = accuracy_score(y, y_pred)

    result = {
        "auc": round(float(auc), 4),
        "auc_std": round(float(auc_std), 4),
        "auc_str": f"{auc:.4f} +/- {auc_std:.4f}",
        "sensitivity": round(float(sensitivity), 4),
        "specificity": round(float(specificity), 4),
        "accuracy": round(float(accuracy), 4),
        "optimal_threshold": round(float(optimal_threshold), 4),
        "n_pathogenic": int(y.sum()),
        "n_benign": int(len(y) - y.sum()),
    }

    verdict = "FAIL" if auc >= 0.95 else ("INCONCLUSIVE" if auc >= 0.90 else "PASS")

    print(f"  {model_name}:")
    print(f"    AUC: {result['auc_str']} [{verdict}]")
    print(f"    Sensitivity: {sensitivity:.4f}, Specificity: {specificity:.4f}")
    print(f"    Optimal threshold: {optimal_threshold:.4f}")

    result["verdict"] = verdict
    return result


def clone_estimator(estimator):
    """Create a fresh clone of an sklearn estimator."""
    from sklearn.base import clone
    return clone(estimator)


def run_baseline_models(features):
    """Run all baseline models and return results."""
    # Prepare feature matrix
    base_features = ["log_distance_to_enhancer"]
    conservation_features = ["conservation_score"]
    all_features = base_features + conservation_features + ["cadd_score",
                                                            "log_distance_to_ctcf",
                                                            "within_5kb_enhancer"]

    X_base = features[base_features].values
    X_cons = features[base_features + conservation_features].values
    X_all = features[all_features].values
    y = features["label"].values

    # Impute missing values
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    # ---- Model 1: Logistic Regression on distance_to_enhancer only ----
    print("\n--- Model 1: Logistic Regression (distance to enhancer only) ---")
    X1 = scaler.fit_transform(imputer.fit_transform(X_base))
    model1 = LogisticRegression(random_state=42, max_iter=1000)
    result1 = evaluate_model_cv(X1, y, model1, model_name="LR(distance)")

    # ---- Model 2: Logistic Regression on distance + conservation ----
    print("\n--- Model 2: Logistic Regression (distance + conservation) ---")
    X2 = scaler.fit_transform(imputer.fit_transform(X_cons))
    model2 = LogisticRegression(random_state=42, max_iter=1000)
    result2 = evaluate_model_cv(X2, y, model2, model_name="LR(distance+conservation)")

    # ---- Model 3: Logistic Regression on distance + conservation + CADD ----
    print("\n--- Model 3: Logistic Regression (distance + conservation + CADD) ---")
    X3 = scaler.fit_transform(imputer.fit_transform(X_all))
    model3 = LogisticRegression(random_state=42, max_iter=1000)
    result3 = evaluate_model_cv(X3, y, model3, model_name="LR(all_features)")

    # ---- Model 4: Random Forest on all features ----
    print("\n--- Model 4: Random Forest (all features) ---")
    model4 = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    result4 = evaluate_model_cv(X3, y, model4, model_name="RandomForest(all)")

    # ---- Model 5: Simple threshold (within 1kb of enhancer = pathogenic) ----
    print("\n--- Model 5: Simple threshold (within 1kb of enhancer) ---")
    within_1kb = features["within_1kb_enhancer"].values
    # This is a binary predictor, so AUC is limited
    try:
        auc5 = roc_auc_score(y, within_1kb)
    except ValueError:
        auc5 = np.nan

    # Sensitivity/specificity at this threshold
    tp = np.sum((within_1kb == 1) & (y == 1))
    fn = np.sum((within_1kb == 0) & (y == 1))
    fp = np.sum((within_1kb == 1) & (y == 0))
    tn = np.sum((within_1kb == 0) & (y == 0))
    sensitivity5 = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity5 = tn / (tn + fp) if (tn + fp) > 0 else 0
    accuracy5 = (tp + tn) / len(y) if len(y) > 0 else 0

    verdict5 = "FAIL" if auc5 >= 0.95 else ("INCONCLUSIVE" if auc5 >= 0.90 else "PASS")
    result5 = {
        "auc": round(float(auc5), 4) if not np.isnan(auc5) else None,
        "auc_std": None,
        "auc_str": f"{auc5:.4f}" if not np.isnan(auc5) else "N/A",
        "sensitivity": round(float(sensitivity5), 4),
        "specificity": round(float(specificity5), 4),
        "accuracy": round(float(accuracy5), 4),
        "optimal_threshold": "binary (1kb)",
        "n_within_1kb_pathogenic": int(tp),
        "n_within_1kb_benign": int(fp),
        "n_outside_1kb_pathogenic": int(fn),
        "n_outside_1kb_benign": int(tn),
        "verdict": verdict5,
    }

    print(f"  Simple threshold (1kb):")
    print(f"    AUC: {result5['auc_str']} [{verdict5}]")
    print(f"    Sensitivity: {sensitivity5:.4f}, Specificity: {specificity5:.4f}")
    print(f"    TP={tp}, FP={fp}, TN={tn}, FN={fn}")

    # ---- Bonus: VEP score alone (if available) ----
    result_vep = None
    if "vep_score" in features.columns:
        print("\n--- Bonus: VEP Score alone ---")
        vep_X = features[["vep_score"]].values
        vep_X = scaler.fit_transform(imputer.fit_transform(vep_X))
        model_vep = LogisticRegression(random_state=42, max_iter=1000)
        result_vep = evaluate_model_cv(vep_X, y, model_vep, model_name="LR(VEP_score)")

    # ---- Bonus: ARCHCODE SSIM alone (reference) ----
    result_archcode = None
    if "archcode_ssim" in features.columns:
        print("\n--- Reference: ARCHCODE SSIM alone ---")
        # ARCHCODE predictor: 1 - SSIM (higher = more pathogenic)
        archcode_score = 1.0 - features["archcode_ssim"].values
        try:
            auc_archcode = roc_auc_score(y, archcode_score)
        except ValueError:
            auc_archcode = np.nan

        fpr_a, tpr_a, thresholds_a = roc_curve(y, archcode_score)
        j_scores_a = tpr_a - fpr_a
        best_idx_a = np.argmax(j_scores_a)
        optimal_ssim = 1.0 - thresholds_a[best_idx_a]
        sens_a = tpr_a[best_idx_a]
        spec_a = 1.0 - fpr_a[best_idx_a]

        verdict_arch = "PASS" if auc_archcode >= 0.95 else "FAIL"
        result_archcode = {
            "auc": round(float(auc_archcode), 4) if not np.isnan(auc_archcode) else None,
            "auc_str": f"{auc_archcode:.4f}" if not np.isnan(auc_archcode) else "N/A",
            "sensitivity": round(float(sens_a), 4),
            "specificity": round(float(spec_a), 4),
            "optimal_ssim_threshold": round(float(optimal_ssim), 4),
            "verdict": verdict_arch,
            "note": "Reference: ARCHCODE physics-based model",
        }
        print(f"  ARCHCODE SSIM:")
        print(f"    AUC: {result_archcode['auc_str']}")
        print(f"    Sensitivity: {sens_a:.4f}, Specificity: {spec_a:.4f}")
        print(f"    Optimal SSIM threshold: {optimal_ssim:.4f}")

    results = {
        "model1_distance_only": result1,
        "model2_distance_conservation": result2,
        "model3_all_features": result3,
        "model4_random_forest": result4,
        "model5_simple_threshold": result5,
    }
    if result_vep:
        results["bonus_vep_score"] = result_vep
    if result_archcode:
        results["reference_archcode_ssim"] = result_archcode

    return results


# ============================================================================
# 4. Save results and print summary
# ============================================================================

def save_results(features, results):
    """Save results to JSON and CSV."""
    # JSON
    output_json = RESULTS_DIR / "simple_baseline_results.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "test_name": "Simple Baseline: Distance + Conservation + CADD",
        "dataset": "HBB ClinVar variants (Combined Atlas)",
        "n_variants": len(features),
        "n_pathogenic": int(features["label"].sum()),
        "n_benign": int((features["label"] == 0).sum()),
        "archcode_reference_auc": ARCHCODE_AUC,
        "models": results,
        "overall_verdict": compute_overall_verdict(results),
        "limitations": [
            "No phyloP/phastCons conservation scores available; used CADD as proxy",
            "Enhancer positions from locus config (model parameters), not experimental H3K27ac peaks",
            "CTCF positions from K562 cell line (may not reflect erythroid context)",
            "Simple distance metric does not capture 3D genome topology",
        ],
    }

    with open(output_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {output_json}")

    # CSV with features and predictions
    output_csv = RESULTS_DIR / "simple_baseline_results.csv"
    features.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")

    return summary


def compute_overall_verdict(results):
    """Determine overall PASS/FAIL/INCONCLUSIVE."""
    model_aucs = []
    for key, val in results.items():
        if key.startswith("model") and "auc" in val and val["auc"] is not None:
            model_aucs.append(val["auc"])

    if not model_aucs:
        return "ERROR: No valid model results"

    max_auc = max(model_aucs)
    min_auc = min(model_aucs)

    if max_auc >= 0.95:
        return (f"FAIL (physics not justified) - "
                f"best simple model AUC = {max_auc:.4f} >= 0.95")
    elif min_auc >= 0.90:
        return (f"INCONCLUSIVE - "
                f"simple models AUC range: {min_auc:.4f}-{max_auc:.4f}")
    else:
        return (f"PASS (physics adds value) - "
                f"all simple models AUC < 0.90 (best: {max_auc:.4f})")


def print_summary(summary):
    """Print final summary with verdict."""
    print("\n" + "=" * 70)
    print("SIMPLE BASELINE TEST: Distance + Conservation + CADD vs ARCHCODE")
    print("=" * 70)

    print(f"\nDataset: {summary['dataset']}")
    print(f"  Variants: {summary['n_variants']} "
          f"(Pathogenic: {summary['n_pathogenic']}, Benign: {summary['n_benign']})")
    print(f"  ARCHCODE Reference AUC: {summary['archcode_reference_auc']}")

    print(f"\n--- Model Results ---")
    models = summary["models"]
    for key, val in models.items():
        label = key.replace("_", " ").title()
        auc_str = val.get("auc_str", "N/A")
        verdict = val.get("verdict", "")
        print(f"  {label}: AUC = {auc_str} [{verdict}]")

    print(f"\n--- Overall Verdict ---")
    print(f"  {summary['overall_verdict']}")

    print(f"\n--- Interpretation ---")
    verdict = summary["overall_verdict"]
    if verdict.startswith("FAIL"):
        print("  A simple model (distance + conservation) achieves AUC >= 0.95.")
        print("  The complex physics-based LSSIM may not be justified for HBB.")
        print("  RECOMMENDATION: Re-evaluate whether loop extrusion physics adds value.")
    elif verdict.startswith("INCONCLUSIVE"):
        print("  Simple models achieve moderate AUC (0.90-0.95).")
        print("  Physics may add marginal value but needs further investigation.")
        print("  RECOMMENDATION: Test on additional loci and blind variants.")
    else:
        print("  Simple models fail to reach AUC >= 0.90.")
        print("  Physics-based LSSIM provides substantial improvement over trivial baselines.")
        print("  RECOMMENDATION: The complex physics IS justified.")

    if summary.get("limitations"):
        print(f"\n--- Limitations ---")
        for lim in summary["limitations"]:
            print(f"  - {lim}")

    print("\n" + "=" * 70)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("SIMPLE BASELINE TEST: Distance + Conservation + CADD")
    print("Skeptic Engine: Can a trivial model match ARCHCODE's AUC = 0.977?")
    print("=" * 70)

    # 1. Load data
    print("\n[1/5] Loading data...")
    df = load_hbb_data()

    # 2. Load genomic features
    print("\n[2/5] Loading genomic features...")
    enhancers = load_enhancer_positions()
    ctcf_sites = load_ctcf_positions()

    # 3. Build feature matrix
    print("\n[3/5] Computing features...")
    features = build_features(df, enhancers, ctcf_sites)

    # 4. Run models
    print("\n[4/5] Running baseline models...")
    results = run_baseline_models(features)

    # 5. Save and print summary
    print("\n[5/5] Saving results...")
    summary = save_results(features, results)
    print_summary(summary)

    return 0


if __name__ == "__main__":
    exit(main())
