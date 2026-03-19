"""
V1 Module: 3D-aware variant scoring — Step 2: Baseline Model + Ablation

Trains LogReg / RF / XGBoost on enriched HBB features.
Key question: does LSSIM (3D structure) add predictive power over sequence-only scores?

Input:  analysis/v1_hbb_features.csv
Output: analysis/v1_model_results.json
        figures/v1_model_comparison.png
"""

import csv
import json
import math
import random
from pathlib import Path
from collections import Counter

ROOT = Path("D:/ДНК")
FEATURES_PATH = ROOT / "analysis" / "v1_hbb_features.csv"
OUTPUT_JSON = ROOT / "analysis" / "v1_model_results.json"
OUTPUT_FIG = ROOT / "figures" / "v1_model_comparison.png"

# === Load data ===
print("Loading features...")
rows = []
with open(FEATURES_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

print(f"Loaded {len(rows)} variants, {len(fieldnames)} columns")

# === Define feature sets for ablation ===
STRUCTURAL_FEATURES = [
    "ssim",
    "lssim",
    "delta_ssim",
    "delta_lssim",
    "delta_insulation",
    "loop_integrity",
    "struct_disruption_ratio",
]

SEQUENCE_FEATURES = [
    "vep_score",
    "sift_score",
    "cadd_phred",
]

DISTANCE_FEATURES = [
    "dist_to_lcr",
    "dist_to_nearest_enhancer",
    "dist_to_nearest_ctcf",
    "dist_to_tss",
    "in_hbb_gene",
    "log_dist_lcr",
    "log_dist_enhancer",
    "log_dist_ctcf",
    "log_dist_tss",
]

CATEGORY_FEATURES = [
    "cat_missense",
    "cat_nonsense",
    "cat_splice",
    "cat_frameshift",
    "cat_synonymous",
    "cat_3_prime_UTR",
    "cat_5_prime_UTR",
    "cat_promoter",
    "cat_other",
    "cat_non_coding",
]

ALL_FEATURES = STRUCTURAL_FEATURES + SEQUENCE_FEATURES + DISTANCE_FEATURES + CATEGORY_FEATURES


# === Prepare numpy-free data matrices ===
def to_float(val: str) -> float:
    try:
        v = float(val)
        return 0.0 if math.isnan(v) or v == -1.0 else v
    except (ValueError, TypeError):
        return 0.0


def extract_features(
    rows: list[dict], feature_names: list[str]
) -> tuple[list[list[float]], list[int]]:
    X = []
    y = []
    for row in rows:
        x = [to_float(row[f]) for f in feature_names]
        label = int(row["label"])
        X.append(x)
        y.append(label)
    return X, y


# === Train/test split (stratified 80/20) ===
random.seed(42)

pathogenic_idx = [i for i, r in enumerate(rows) if r["label"] == "1"]
benign_idx = [i for i, r in enumerate(rows) if r["label"] == "0"]

random.shuffle(pathogenic_idx)
random.shuffle(benign_idx)

n_path_test = max(1, len(pathogenic_idx) // 5)
n_ben_test = max(1, len(benign_idx) // 5)

test_idx = set(pathogenic_idx[:n_path_test] + benign_idx[:n_ben_test])
train_idx = set(range(len(rows))) - test_idx

train_rows = [rows[i] for i in sorted(train_idx)]
test_rows = [rows[i] for i in sorted(test_idx)]

print(
    f"Train: {len(train_rows)} (P={sum(1 for r in train_rows if r['label'] == '1')}, "
    f"B={sum(1 for r in train_rows if r['label'] == '0')})"
)
print(
    f"Test:  {len(test_rows)} (P={sum(1 for r in test_rows if r['label'] == '1')}, "
    f"B={sum(1 for r in test_rows if r['label'] == '0')})"
)

# === Try sklearn, fallback to manual logistic regression ===
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
    from sklearn.preprocessing import StandardScaler
    import numpy as np

    HAS_SKLEARN = True
    print("Using scikit-learn models")
except ImportError:
    HAS_SKLEARN = False
    print("scikit-learn not found — using manual logistic regression")

if HAS_SKLEARN:
    import numpy as np

    results = {}

    # === Feature set ablation configurations ===
    ABLATION_CONFIGS = {
        "all_features": ALL_FEATURES,
        "structural_only": STRUCTURAL_FEATURES,
        "sequence_only": SEQUENCE_FEATURES,
        "no_structural": SEQUENCE_FEATURES + DISTANCE_FEATURES + CATEGORY_FEATURES,
        "no_sequence": STRUCTURAL_FEATURES + DISTANCE_FEATURES + CATEGORY_FEATURES,
        "structural_plus_distance": STRUCTURAL_FEATURES + DISTANCE_FEATURES,
    }

    # === Train and evaluate each configuration ===
    for config_name, feature_set in ABLATION_CONFIGS.items():
        print(f"\n--- {config_name} ({len(feature_set)} features) ---")

        X_train, y_train = extract_features(train_rows, feature_set)
        X_test, y_test = extract_features(test_rows, feature_set)

        X_train = np.array(X_train)
        X_test = np.array(X_test)
        y_train = np.array(y_train)
        y_test = np.array(y_test)

        # Standardize
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        config_results = {}

        # --- Logistic Regression ---
        lr = LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")
        lr.fit(X_train_s, y_train)
        lr_probs = lr.predict_proba(X_test_s)[:, 1]
        lr_auroc = roc_auc_score(y_test, lr_probs)
        lr_auprc = average_precision_score(y_test, lr_probs)
        config_results["LogReg"] = {"AUROC": round(lr_auroc, 4), "AUPRC": round(lr_auprc, 4)}
        print(f"  LogReg:  AUROC={lr_auroc:.4f}, AUPRC={lr_auprc:.4f}")

        # --- Random Forest ---
        rf = RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"
        )
        rf.fit(X_train, y_train)
        rf_probs = rf.predict_proba(X_test)[:, 1]
        rf_auroc = roc_auc_score(y_test, rf_probs)
        rf_auprc = average_precision_score(y_test, rf_probs)
        config_results["RandomForest"] = {"AUROC": round(rf_auroc, 4), "AUPRC": round(rf_auprc, 4)}
        print(f"  RF:      AUROC={rf_auroc:.4f}, AUPRC={rf_auprc:.4f}")

        # --- Gradient Boosting (XGBoost-like) ---
        gb = GradientBoostingClassifier(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        )
        # WHY: GradientBoosting doesn't support class_weight, use sample_weight instead
        class_counts = Counter(y_train)
        weight_0 = len(y_train) / (2 * class_counts[0])
        weight_1 = len(y_train) / (2 * class_counts[1])
        sample_weights = np.array([weight_1 if y == 1 else weight_0 for y in y_train])
        gb.fit(X_train, y_train, sample_weight=sample_weights)
        gb_probs = gb.predict_proba(X_test)[:, 1]
        gb_auroc = roc_auc_score(y_test, gb_probs)
        gb_auprc = average_precision_score(y_test, gb_probs)
        config_results["GradientBoosting"] = {
            "AUROC": round(gb_auroc, 4),
            "AUPRC": round(gb_auprc, 4),
        }
        print(f"  GB:      AUROC={gb_auroc:.4f}, AUPRC={gb_auprc:.4f}")

        # Feature importance (from best model = GB)
        if config_name == "all_features":
            importances = gb.feature_importances_
            feat_imp = sorted(
                zip(feature_set, importances.tolist()), key=lambda x: x[1], reverse=True
            )
            config_results["feature_importance_top10"] = [
                {"feature": f, "importance": round(imp, 4)} for f, imp in feat_imp[:10]
            ]
            print("\n  Top-10 feature importances (GradientBoosting):")
            for f, imp in feat_imp[:10]:
                bar = "█" * int(imp * 50)
                print(f"    {f:30s} {imp:.4f} {bar}")

        results[config_name] = config_results

    # === Ablation delta analysis ===
    print(f"\n{'=' * 60}")
    print("ABLATION ANALYSIS: Does 3D structure add value?")
    print(f"{'=' * 60}")

    best_model = "GradientBoosting"
    all_auroc = results["all_features"][best_model]["AUROC"]
    no_struct_auroc = results["no_structural"][best_model]["AUROC"]
    no_seq_auroc = results["no_sequence"][best_model]["AUROC"]
    struct_only_auroc = results["structural_only"][best_model]["AUROC"]
    seq_only_auroc = results["sequence_only"][best_model]["AUROC"]

    print(f"\n  All features:       AUROC = {all_auroc}")
    print(
        f"  No structural:      AUROC = {no_struct_auroc}  (Δ = {all_auroc - no_struct_auroc:+.4f})"
    )
    print(f"  No sequence:        AUROC = {no_seq_auroc}  (Δ = {all_auroc - no_seq_auroc:+.4f})")
    print(f"  Structural only:    AUROC = {struct_only_auroc}")
    print(f"  Sequence only:      AUROC = {seq_only_auroc}")

    delta_struct = all_auroc - no_struct_auroc
    delta_seq = all_auroc - no_seq_auroc

    if delta_struct > 0.02:
        verdict = "CONFIRMED: 3D structure adds significant predictive power"
    elif delta_struct > 0.005:
        verdict = "MARGINAL: 3D structure adds modest predictive power"
    else:
        verdict = "NOT CONFIRMED: 3D structure does not add predictive power over sequence"

    print(f"\n  VERDICT: {verdict}")
    results["ablation_verdict"] = verdict
    results["ablation_delta_structural"] = round(delta_struct, 4)
    results["ablation_delta_sequence"] = round(delta_seq, 4)

    # === Save results ===
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUTPUT_JSON}")

    # === Plot ===
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Panel A: Model comparison across configs
        configs = list(ABLATION_CONFIGS.keys())
        models = ["LogReg", "RandomForest", "GradientBoosting"]
        colors = ["#4477AA", "#228833", "#EE6677"]

        x = range(len(configs))
        width = 0.25
        for i, model in enumerate(models):
            aurocs = [results[c][model]["AUROC"] for c in configs]
            offset = (i - 1) * width
            bars = axes[0].bar(
                [xi + offset for xi in x], aurocs, width, label=model, color=colors[i], alpha=0.85
            )

        axes[0].set_xticks(x)
        axes[0].set_xticklabels([c.replace("_", "\n") for c in configs], fontsize=8)
        axes[0].set_ylabel("AUROC")
        axes[0].set_title("A. Model × Feature Set Comparison")
        axes[0].legend(fontsize=8)
        axes[0].set_ylim(0.5, 1.0)
        axes[0].axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

        # Panel B: Feature importance (top 10)
        if "feature_importance_top10" in results.get("all_features", {}):
            top10 = results["all_features"]["feature_importance_top10"]
            feat_names = [d["feature"] for d in top10][::-1]
            feat_imps = [d["importance"] for d in top10][::-1]

            # Color by type
            bar_colors = []
            for f in feat_names:
                if f in STRUCTURAL_FEATURES:
                    bar_colors.append("#EE6677")
                elif f in SEQUENCE_FEATURES:
                    bar_colors.append("#4477AA")
                elif f in DISTANCE_FEATURES:
                    bar_colors.append("#228833")
                else:
                    bar_colors.append("#CCBB44")

            axes[1].barh(feat_names, feat_imps, color=bar_colors, alpha=0.85)
            axes[1].set_xlabel("Feature Importance (GradientBoosting)")
            axes[1].set_title("B. Top-10 Features")

            # Legend
            from matplotlib.patches import Patch

            legend_elements = [
                Patch(facecolor="#EE6677", label="Structural (3D)"),
                Patch(facecolor="#4477AA", label="Sequence"),
                Patch(facecolor="#228833", label="Distance"),
                Patch(facecolor="#CCBB44", label="Category"),
            ]
            axes[1].legend(handles=legend_elements, fontsize=8, loc="lower right")

        plt.tight_layout()
        plt.savefig(OUTPUT_FIG, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {OUTPUT_FIG}")
    except Exception as e:
        print(f"Figure generation failed: {e}")

else:
    # === Manual fallback (no sklearn) ===
    print("\nInstall scikit-learn for full model comparison:")
    print("  pip install scikit-learn")
    print("\nFalling back to correlation analysis...")

    X_all, y_all = extract_features(rows, ALL_FEATURES)

    # Compute point-biserial correlation for each feature
    def mean(vals):
        return sum(vals) / len(vals) if vals else 0

    def pearson_r(a, b):
        n = len(a)
        if n < 3:
            return 0
        ma, mb = mean(a), mean(b)
        num = sum((ai - ma) * (bi - mb) for ai, bi in zip(a, b))
        da = math.sqrt(sum((ai - ma) ** 2 for ai in a))
        db = math.sqrt(sum((bi - mb) ** 2 for bi in b))
        return num / (da * db) if da * db > 0 else 0

    print("\nFeature correlations with pathogenicity label:")
    for i, feat in enumerate(ALL_FEATURES):
        vals = [x[i] for x in X_all]
        r = pearson_r(vals, y_all)
        bar = "+" * int(abs(r) * 30) if r > 0 else "-" * int(abs(r) * 30)
        print(f"  {feat:30s}  r={r:+.4f}  {bar}")
