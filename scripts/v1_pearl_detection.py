"""
V1 Module: 3D-aware variant scoring — Step 3: Pearl Detection

The RIGHT question: can structural features identify variants that
sequence-based tools MISS (pearls = ClinVar Benign + ARCHCODE structural disruption)?

Task 1: Pearl vs non-pearl ranking (structural features should dominate)
Task 2: Leave-structure-out ablation on pearl recall
Task 3: SHAP-style analysis — what makes a pearl a pearl?

Input:  analysis/v1_hbb_features.csv
Output: analysis/v1_pearl_detection_results.json
        figures/v1_pearl_detection.png
"""

import csv
import json
import math
import random
from pathlib import Path
from collections import Counter

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path("D:/ДНК")
FEATURES_PATH = ROOT / "analysis" / "v1_hbb_features.csv"
OUTPUT_JSON = ROOT / "analysis" / "v1_pearl_detection_results.json"
OUTPUT_FIG = ROOT / "figures" / "v1_pearl_detection.png"

# === Load data ===
rows = []
with open(FEATURES_PATH, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows.append(row)
print(f"Loaded {len(rows)} variants")

# === Feature sets ===
STRUCTURAL = [
    "ssim",
    "lssim",
    "delta_ssim",
    "delta_lssim",
    "delta_insulation",
    "loop_integrity",
    "struct_disruption_ratio",
]
SEQUENCE = ["vep_score", "sift_score", "cadd_phred"]
DISTANCE = [
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
CATEGORY = [
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
ALL_FEATURES = STRUCTURAL + SEQUENCE + DISTANCE + CATEGORY


def to_float(val: str) -> float:
    try:
        v = float(val)
        return 0.0 if math.isnan(v) or v == -1.0 else v
    except (ValueError, TypeError):
        return 0.0


# =====================================================================
# TASK 1: Pearl detection — binary classification
# Target: is_pearl (27 positives vs 1076 negatives)
# =====================================================================
print("\n" + "=" * 60)
print("TASK 1: Pearl Detection (is_pearl = 1 vs 0)")
print("=" * 60)

X_all = np.array([[to_float(r[f]) for f in ALL_FEATURES] for r in rows])
y_pearl = np.array([int(r["is_pearl"]) for r in rows])

print(f"Pearls: {y_pearl.sum()} / {len(y_pearl)} ({100 * y_pearl.mean():.1f}%)")

# WHY: 27/1103 is extremely imbalanced — use stratified k-fold cross-validation
# instead of single split to get stable estimates
from sklearn.model_selection import StratifiedKFold

results = {}
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

ABLATION_CONFIGS = {
    "all_features": ALL_FEATURES,
    "structural_only": STRUCTURAL,
    "sequence_only": SEQUENCE,
    "distance_only": DISTANCE,
    "no_structural": SEQUENCE + DISTANCE + CATEGORY,
    "no_sequence": STRUCTURAL + DISTANCE + CATEGORY,
    "structural_plus_distance": STRUCTURAL + DISTANCE,
}

for config_name, feature_set in ABLATION_CONFIGS.items():
    feat_idx = [ALL_FEATURES.index(f) for f in feature_set]
    X_sub = X_all[:, feat_idx]

    fold_aurocs = []
    fold_auprcs = []
    fold_recalls_at_50 = []  # recall when we pick top-50 ranked variants
    fold_recalls_at_100 = []
    all_probs = np.zeros(len(rows))
    all_tested = np.zeros(len(rows), dtype=bool)

    for fold, (train_idx, test_idx) in enumerate(skf.split(X_sub, y_pearl)):
        X_train, X_test = X_sub[train_idx], X_sub[test_idx]
        y_train, y_test = y_pearl[train_idx], y_pearl[test_idx]

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        # WHY: class_weight="balanced" critical for 27:1076 imbalance
        gb = GradientBoostingClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            subsample=0.8,
        )
        # Sample weights for imbalance
        counts = Counter(y_train)
        w0 = len(y_train) / (2 * counts[0])
        w1 = len(y_train) / (2 * counts[1])
        sw = np.array([w1 if y == 1 else w0 for y in y_train])
        gb.fit(X_train_s, y_train, sample_weight=sw)

        probs = gb.predict_proba(X_test_s)[:, 1]
        all_probs[test_idx] = probs
        all_tested[test_idx] = True

        if y_test.sum() > 0:
            auroc = roc_auc_score(y_test, probs)
            auprc = average_precision_score(y_test, probs)
            fold_aurocs.append(auroc)
            fold_auprcs.append(auprc)

            # Recall at top-K (proportional to test size)
            k50 = max(1, int(len(y_test) * 50 / len(rows)))
            k100 = max(1, int(len(y_test) * 100 / len(rows)))
            top_k50 = np.argsort(probs)[::-1][:k50]
            top_k100 = np.argsort(probs)[::-1][:k100]
            recall_50 = y_test[top_k50].sum() / max(1, y_test.sum())
            recall_100 = y_test[top_k100].sum() / max(1, y_test.sum())
            fold_recalls_at_50.append(recall_50)
            fold_recalls_at_100.append(recall_100)

    mean_auroc = np.mean(fold_aurocs) if fold_aurocs else 0
    mean_auprc = np.mean(fold_auprcs) if fold_auprcs else 0
    mean_r50 = np.mean(fold_recalls_at_50) if fold_recalls_at_50 else 0
    mean_r100 = np.mean(fold_recalls_at_100) if fold_recalls_at_100 else 0

    results[config_name] = {
        "AUROC": round(mean_auroc, 4),
        "AUPRC": round(mean_auprc, 4),
        "Recall@top50": round(mean_r50, 4),
        "Recall@top100": round(mean_r100, 4),
        "n_features": len(feature_set),
    }

    print(f"\n{config_name} ({len(feature_set)} feat):")
    print(
        f"  AUROC={mean_auroc:.4f}  AUPRC={mean_auprc:.4f}  "
        f"R@50={mean_r50:.4f}  R@100={mean_r100:.4f}"
    )

# === Ablation deltas ===
print(f"\n{'=' * 60}")
print("ABLATION: Structural value for pearl detection")
print(f"{'=' * 60}")

all_auroc = results["all_features"]["AUROC"]
no_struct = results["no_structural"]["AUROC"]
no_seq = results["no_sequence"]["AUROC"]
struct_only = results["structural_only"]["AUROC"]
seq_only = results["sequence_only"]["AUROC"]

delta_struct = all_auroc - no_struct
delta_seq = all_auroc - no_seq

print(f"\n  All features:       AUROC = {all_auroc}")
print(f"  No structural:      AUROC = {no_struct}  (Δ = {delta_struct:+.4f})")
print(f"  No sequence:        AUROC = {no_seq}  (Δ = {delta_seq:+.4f})")
print(f"  Structural only:    AUROC = {struct_only}")
print(f"  Sequence only:      AUROC = {seq_only}")

# Recall comparison (more important than AUROC for pearls)
all_r50 = results["all_features"]["Recall@top50"]
no_struct_r50 = results["no_structural"]["Recall@top50"]
seq_only_r50 = results["sequence_only"]["Recall@top50"]
struct_only_r50 = results["structural_only"]["Recall@top50"]

print(f"\n  Recall@top50:")
print(f"    All features:     {all_r50:.4f}")
print(f"    No structural:    {no_struct_r50:.4f}")
print(f"    Structural only:  {struct_only_r50:.4f}")
print(f"    Sequence only:    {seq_only_r50:.4f}")

if delta_struct > 0.02:
    verdict = "CONFIRMED: 3D structure is ESSENTIAL for pearl detection"
elif delta_struct > 0.005:
    verdict = "SUPPORTED: 3D structure contributes to pearl detection"
elif struct_only > seq_only + 0.02:
    verdict = "CONFIRMED: structural features outperform sequence for pearl detection"
else:
    verdict = "INCONCLUSIVE: neither feature set clearly dominates"

# Check recall-based verdict (more relevant)
if struct_only_r50 > seq_only_r50 + 0.1:
    recall_verdict = "CONFIRMED: structural features find more pearls than sequence"
elif seq_only_r50 > struct_only_r50 + 0.1:
    recall_verdict = "REFUTED: sequence features find more pearls (unexpected)"
else:
    recall_verdict = "COMPARABLE: both feature sets find similar pearl counts"

print(f"\n  AUROC verdict:  {verdict}")
print(f"  Recall verdict: {recall_verdict}")

results["verdict_auroc"] = verdict
results["verdict_recall"] = recall_verdict
results["delta_structural_auroc"] = round(delta_struct, 4)
results["delta_sequence_auroc"] = round(delta_seq, 4)

# =====================================================================
# TASK 2: Feature importance for pearl detection
# =====================================================================
print(f"\n{'=' * 60}")
print("TASK 2: What makes a pearl a pearl?")
print(f"{'=' * 60}")

# Train final model on all data for interpretation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_all)

gb_final = GradientBoostingClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    random_state=42,
    subsample=0.8,
)
counts = Counter(y_pearl)
w0 = len(y_pearl) / (2 * counts[0])
w1 = len(y_pearl) / (2 * counts[1])
sw = np.array([w1 if y == 1 else w0 for y in y_pearl])
gb_final.fit(X_scaled, y_pearl, sample_weight=sw)

importances = gb_final.feature_importances_
feat_imp = sorted(zip(ALL_FEATURES, importances.tolist()), key=lambda x: x[1], reverse=True)

print("\nTop-15 feature importances for pearl detection:")
for f, imp in feat_imp[:15]:
    ftype = (
        "STRUCT"
        if f in STRUCTURAL
        else "SEQ"
        if f in SEQUENCE
        else "DIST"
        if f in DISTANCE
        else "CAT"
    )
    bar = "█" * int(imp * 60)
    print(f"  [{ftype:6s}] {f:30s} {imp:.4f} {bar}")

results["feature_importance"] = [
    {
        "feature": f,
        "importance": round(imp, 4),
        "type": (
            "structural"
            if f in STRUCTURAL
            else "sequence"
            if f in SEQUENCE
            else "distance"
            if f in DISTANCE
            else "category"
        ),
    }
    for f, imp in feat_imp
]

# =====================================================================
# TASK 3: Pearl profile — what are pearls vs non-pearls?
# =====================================================================
print(f"\n{'=' * 60}")
print("TASK 3: Pearl profile (mean feature values)")
print(f"{'=' * 60}")

pearl_idx = np.where(y_pearl == 1)[0]
non_pearl_idx = np.where(y_pearl == 0)[0]

profile = {}
print(f"\n  {'Feature':30s} {'Pearl mean':>12s} {'Non-pearl':>12s} {'Ratio':>8s}")
print(f"  {'-' * 30} {'-' * 12} {'-' * 12} {'-' * 8}")

for i, f in enumerate(ALL_FEATURES):
    pearl_mean = X_all[pearl_idx, i].mean()
    non_pearl_mean = X_all[non_pearl_idx, i].mean()
    ratio = pearl_mean / non_pearl_mean if non_pearl_mean != 0 else float("inf")

    if abs(ratio - 1.0) > 0.1 or f in STRUCTURAL:
        print(f"  {f:30s} {pearl_mean:12.4f} {non_pearl_mean:12.4f} {ratio:8.2f}x")
        profile[f] = {
            "pearl_mean": round(pearl_mean, 4),
            "non_pearl_mean": round(non_pearl_mean, 4),
            "ratio": round(ratio, 4),
        }

results["pearl_profile"] = profile

# =====================================================================
# TASK 4: Sequence-blind pearl score
# =====================================================================
print(f"\n{'=' * 60}")
print("TASK 4: Can sequence tools detect pearls at all?")
print(f"{'=' * 60}")

# Check VEP/CADD/SIFT scores for pearls
for score_name in ["vep_score", "sift_score", "cadd_phred"]:
    si = ALL_FEATURES.index(score_name)
    pearl_vals = X_all[pearl_idx, si]
    non_pearl_vals = X_all[non_pearl_idx, si]
    print(f"\n  {score_name}:")
    print(f"    Pearls:     mean={pearl_vals.mean():.4f}, max={pearl_vals.max():.4f}")
    print(f"    Non-pearls: mean={non_pearl_vals.mean():.4f}, max={non_pearl_vals.max():.4f}")

    # How many pearls would be caught by sequence threshold?
    if score_name == "cadd_phred":
        threshold = 15.0  # CADD "damaging" threshold
        caught = (pearl_vals >= threshold).sum()
    else:
        threshold = 0.5  # generic "high impact"
        caught = (pearl_vals >= threshold).sum()
    print(
        f"    Pearls caught by {score_name}>={threshold}: {caught}/{len(pearl_vals)} "
        f"({100 * caught / len(pearl_vals):.0f}%)"
    )

results["sequence_blind_spot"] = {
    "total_pearls": int(len(pearl_vals)),
    "caught_by_vep_05": int((X_all[pearl_idx, ALL_FEATURES.index("vep_score")] >= 0.5).sum()),
    "caught_by_cadd_15": int((X_all[pearl_idx, ALL_FEATURES.index("cadd_phred")] >= 15).sum()),
}

# === Save ===
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {OUTPUT_JSON}")

# =====================================================================
# Figure: 4-panel pearl detection analysis
# =====================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# Panel A: AUROC comparison across ablations
configs = list(ABLATION_CONFIGS.keys())
aurocs = [results[c]["AUROC"] for c in configs]
colors_bar = []
for c in configs:
    if "structural" in c and "no" not in c:
        colors_bar.append("#EE6677")
    elif "sequence" in c and "no" not in c:
        colors_bar.append("#4477AA")
    elif c == "all_features":
        colors_bar.append("#333333")
    else:
        colors_bar.append("#999999")

axes[0, 0].barh([c.replace("_", "\n") for c in configs], aurocs, color=colors_bar, alpha=0.85)
axes[0, 0].set_xlabel("AUROC (5-fold CV)")
axes[0, 0].set_title("A. Pearl Detection: Feature Set Ablation")
axes[0, 0].set_xlim(0.5, 1.0)
axes[0, 0].axvline(x=0.5, color="gray", linestyle="--", alpha=0.3)

# Panel B: Feature importance top-10
top10 = results["feature_importance"][:10]
feat_names = [d["feature"] for d in top10][::-1]
feat_imps = [d["importance"] for d in top10][::-1]
feat_types = [d["type"] for d in top10][::-1]

type_colors = {
    "structural": "#EE6677",
    "sequence": "#4477AA",
    "distance": "#228833",
    "category": "#CCBB44",
}
bar_colors = [type_colors.get(t, "#999") for t in feat_types]

axes[0, 1].barh(feat_names, feat_imps, color=bar_colors, alpha=0.85)
axes[0, 1].set_xlabel("Feature Importance")
axes[0, 1].set_title("B. Top-10 Features for Pearl Detection")

from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor="#EE6677", label="Structural (3D)"),
    Patch(facecolor="#4477AA", label="Sequence"),
    Patch(facecolor="#228833", label="Distance"),
    Patch(facecolor="#CCBB44", label="Category"),
]
axes[0, 1].legend(handles=legend_elements, fontsize=8, loc="lower right")

# Panel C: Pearl vs non-pearl LSSIM distribution
lssim_idx = ALL_FEATURES.index("lssim")
pearl_lssim = X_all[pearl_idx, lssim_idx]
non_pearl_lssim = X_all[non_pearl_idx, lssim_idx]

axes[1, 0].hist(
    non_pearl_lssim,
    bins=50,
    alpha=0.6,
    color="#4477AA",
    label=f"Non-pearls (n={len(non_pearl_lssim)})",
    density=True,
)
axes[1, 0].hist(
    pearl_lssim,
    bins=15,
    alpha=0.8,
    color="#EE6677",
    label=f"Pearls (n={len(pearl_lssim)})",
    density=True,
)
axes[1, 0].set_xlabel("LSSIM")
axes[1, 0].set_ylabel("Density")
axes[1, 0].set_title("C. LSSIM Distribution: Pearls vs Non-Pearls")
axes[1, 0].legend()
axes[1, 0].axvline(x=0.95, color="red", linestyle="--", alpha=0.5, label="Pearl threshold")


# Panel D: Recall@K curves for structural vs sequence
# Re-compute recall at various K thresholds using cross-val probabilities
# Use the all_probs from all_features run
# Retrain quickly for struct-only and seq-only to get their probs
def get_cv_probs(feature_set):
    feat_idx = [ALL_FEATURES.index(f) for f in feature_set]
    X_sub = X_all[:, feat_idx]
    probs = np.zeros(len(rows))
    for train_i, test_i in skf.split(X_sub, y_pearl):
        sc = StandardScaler()
        Xtr = sc.fit_transform(X_sub[train_i])
        Xte = sc.transform(X_sub[test_i])
        m = GradientBoostingClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42, subsample=0.8
        )
        c = Counter(y_pearl[train_i])
        w = np.array([len(y_pearl[train_i]) / (2 * c[y]) for y in y_pearl[train_i]])
        m.fit(Xtr, y_pearl[train_i], sample_weight=w)
        probs[test_i] = m.predict_proba(Xte)[:, 1]
    return probs


probs_all = get_cv_probs(ALL_FEATURES)
probs_struct = get_cv_probs(STRUCTURAL)
probs_seq = get_cv_probs(SEQUENCE)

ks = list(range(1, 201))
total_pearls = y_pearl.sum()


def recall_at_k(probs, y, k):
    top_k = np.argsort(probs)[::-1][:k]
    return y[top_k].sum() / total_pearls


recalls_all = [recall_at_k(probs_all, y_pearl, k) for k in ks]
recalls_struct = [recall_at_k(probs_struct, y_pearl, k) for k in ks]
recalls_seq = [recall_at_k(probs_seq, y_pearl, k) for k in ks]

axes[1, 1].plot(ks, recalls_all, color="#333333", linewidth=2, label="All features")
axes[1, 1].plot(ks, recalls_struct, color="#EE6677", linewidth=2, label="Structural only")
axes[1, 1].plot(ks, recalls_seq, color="#4477AA", linewidth=2, label="Sequence only")
axes[1, 1].set_xlabel("Top-K variants inspected")
axes[1, 1].set_ylabel(f"Pearl Recall (out of {total_pearls})")
axes[1, 1].set_title("D. Recall@K: How many pearls found in top-K?")
axes[1, 1].legend()
axes[1, 1].axhline(y=1.0, color="gray", linestyle="--", alpha=0.3)
axes[1, 1].set_xlim(0, 200)

plt.tight_layout()
plt.savefig(OUTPUT_FIG, dpi=150, bbox_inches="tight")
print(f"Figure saved to {OUTPUT_FIG}")

# Final summary
print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
print(f"Pearl detection is the RIGHT task for 3D structural features.")
print(f"AUROC verdict:  {verdict}")
print(f"Recall verdict: {recall_verdict}")
print(f"\nRecall@50:  struct={struct_only_r50:.2f}  seq={seq_only_r50:.2f}  all={all_r50:.2f}")
print(
    f"Recall@100: struct={results['structural_only']['Recall@top100']:.2f}  "
    f"seq={results['sequence_only']['Recall@top100']:.2f}  "
    f"all={results['all_features']['Recall@top100']:.2f}"
)
