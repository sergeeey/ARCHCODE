"""
V1 Cross-Locus Pearl Detection — Negative Control

Hypothesis: structural features should NOT dominate pearl detection
on tissue-MISMATCHED loci (BRCA1 in K562, TP53 in K562).

If confirmed → tissue-specificity is the mechanism, not generic 3D bias.

Input:  results/BRCA1_Unified_Atlas_400kb.csv, results/TP53_Unified_Atlas_300kb.csv
        config/locus/brca1_400kb.json, config/locus/tp53_300kb.json
Output: analysis/v1_crosslocus_results.json
        figures/v1_crosslocus_comparison.png
"""

import csv
import json
import math
from pathlib import Path
from collections import Counter

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path("D:/ДНК")
OUTPUT_JSON = ROOT / "analysis" / "v1_crosslocus_results.json"
OUTPUT_FIG = ROOT / "figures" / "v1_crosslocus_comparison.png"

# === Feature definitions (same as HBB V1) ===
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
    "dist_to_nearest_enhancer",
    "dist_to_nearest_ctcf",
    "log_dist_enhancer",
    "log_dist_ctcf",
]
ALL_FEATURES = STRUCTURAL + SEQUENCE + DISTANCE

CATEGORIES = [
    "missense",
    "nonsense",
    "splice",
    "frameshift",
    "synonymous",
    "3_prime_UTR",
    "5_prime_UTR",
    "promoter",
    "other",
    "non_coding",
]


def safe_float(val: str, default: float = 0.0) -> float:
    try:
        v = float(val)
        return default if math.isnan(v) or v == -1.0 else v
    except (ValueError, TypeError):
        return default


def min_distance(pos: int, targets: list[int]) -> int:
    if not targets:
        return 0
    return min(abs(pos - t) for t in targets)


def load_config(config_path: Path) -> tuple[list[int], list[int]]:
    """Extract enhancer and CTCF positions from locus config."""
    with open(config_path) as f:
        cfg = json.load(f)
    features = cfg.get("features", cfg)

    enhancers = []
    for e in features.get("enhancers", []):
        pos = e.get("position") or e.get("pos")
        if pos:
            enhancers.append(int(pos))

    ctcf = []
    for c in features.get("ctcf_sites", []):
        pos = c.get("position") or c.get("pos")
        if pos:
            ctcf.append(int(pos))

    return enhancers, ctcf


def process_locus(atlas_path: Path, config_path: Path, locus_name: str) -> dict:
    """Run full V1 pearl detection pipeline for a single locus."""
    print(f"\n{'=' * 60}")
    print(f"LOCUS: {locus_name}")
    print(f"{'=' * 60}")

    enhancer_pos, ctcf_pos = load_config(config_path)
    print(f"  Enhancers: {len(enhancer_pos)}, CTCF: {len(ctcf_pos)}")

    # Load atlas
    rows = []
    # WHY: BRCA1/TP53 atlases don't have CADD_Phred column
    with open(atlas_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        available_cols = reader.fieldnames
        for row in reader:
            rows.append(row)

    has_cadd = "CADD_Phred" in available_cols
    print(f"  Variants: {len(rows)}, has CADD: {has_cadd}")

    # Build feature matrix
    X_rows = []
    y_pearl = []
    for row in rows:
        pos = int(row["Position_GRCh38"])
        ssim = safe_float(row.get("ARCHCODE_SSIM", ""))
        lssim = safe_float(row.get("ARCHCODE_LSSIM", ""))
        delta_ins = safe_float(row.get("ARCHCODE_DeltaInsulation", ""))
        loop_int = safe_float(row.get("ARCHCODE_LoopIntegrity", ""))
        vep_score = safe_float(row.get("VEP_Score", ""))
        sift_score = safe_float(row.get("SIFT_Score", ""))
        cadd = safe_float(row.get("CADD_Phred", "")) if has_cadd else 0.0

        delta_ssim = 1.0 - ssim if ssim > 0 else 0.0
        delta_lssim = 1.0 - lssim if lssim > 0 else 0.0
        struct_ratio = delta_lssim / (delta_ssim + 1e-8) if delta_ssim > 0 else 0.0

        dist_enh = min_distance(pos, enhancer_pos)
        dist_ctcf = min_distance(pos, ctcf_pos)

        features = [
            ssim,
            lssim,
            delta_ssim,
            delta_lssim,
            delta_ins,
            loop_int,
            struct_ratio,
            vep_score,
            sift_score,
            cadd,
            dist_enh,
            dist_ctcf,
            math.log10(dist_enh + 1),
            math.log10(dist_ctcf + 1),
        ]
        X_rows.append(features)

        is_pearl = row.get("Pearl", "false").lower() == "true"
        y_pearl.append(1 if is_pearl else 0)

    X = np.array(X_rows)
    y = np.array(y_pearl)

    n_pearls = y.sum()
    print(f"  Pearls: {n_pearls} / {len(y)} ({100 * y.mean():.2f}%)")

    if n_pearls < 2:
        print(f"  SKIP: too few pearls for cross-validation")
        return {
            "locus": locus_name,
            "n_variants": len(y),
            "n_pearls": int(n_pearls),
            "skipped": True,
            "reason": "too few pearls (<2) for stratified CV",
        }

    # === Ablation configs ===
    feat_sets = {
        "all_features": list(range(len(ALL_FEATURES))),
        "structural_only": list(range(len(STRUCTURAL))),
        "sequence_only": list(range(len(STRUCTURAL), len(STRUCTURAL) + len(SEQUENCE))),
        "no_structural": list(range(len(STRUCTURAL), len(ALL_FEATURES))),
        "no_sequence": list(range(len(STRUCTURAL)))
        + list(range(len(STRUCTURAL) + len(SEQUENCE), len(ALL_FEATURES))),
    }

    n_splits = min(5, n_pearls)  # can't have more folds than minority class
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    locus_results = {
        "locus": locus_name,
        "n_variants": len(y),
        "n_pearls": int(n_pearls),
        "skipped": False,
    }

    for config_name, feat_idx in feat_sets.items():
        X_sub = X[:, feat_idx]

        fold_aurocs = []
        fold_auprcs = []

        for train_idx, test_idx in skf.split(X_sub, y):
            X_train, X_test = X_sub[train_idx], X_sub[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            if y_test.sum() == 0 or y_train.sum() == 0:
                continue

            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            gb = GradientBoostingClassifier(
                n_estimators=300,
                max_depth=4,
                learning_rate=0.05,
                random_state=42,
                subsample=0.8,
            )
            counts = Counter(y_train)
            w0 = len(y_train) / (2 * counts[0])
            w1 = len(y_train) / (2 * counts[1])
            sw = np.array([w1 if yi == 1 else w0 for yi in y_train])
            gb.fit(X_train_s, y_train, sample_weight=sw)

            probs = gb.predict_proba(X_test_s)[:, 1]
            fold_aurocs.append(roc_auc_score(y_test, probs))
            fold_auprcs.append(average_precision_score(y_test, probs))

        mean_auroc = np.mean(fold_aurocs) if fold_aurocs else 0
        mean_auprc = np.mean(fold_auprcs) if fold_auprcs else 0

        locus_results[config_name] = {
            "AUROC": round(mean_auroc, 4),
            "AUPRC": round(mean_auprc, 4),
        }
        print(f"  {config_name:25s} AUROC={mean_auroc:.4f}  AUPRC={mean_auprc:.4f}")

    # Feature importance (full model)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    gb_full = GradientBoostingClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        subsample=0.8,
    )
    counts = Counter(y)
    w0 = len(y) / (2 * counts[0])
    w1 = len(y) / (2 * counts[1])
    sw = np.array([w1 if yi == 1 else w0 for yi in y])
    gb_full.fit(X_scaled, y, sample_weight=sw)

    importances = gb_full.feature_importances_
    feat_imp = sorted(zip(ALL_FEATURES, importances.tolist()), key=lambda x: x[1], reverse=True)

    print(f"\n  Top-5 features:")
    structural_importance = 0
    sequence_importance = 0
    for f, imp in feat_imp:
        ftype = "STRUCT" if f in STRUCTURAL else "SEQ" if f in SEQUENCE else "DIST"
        if f in STRUCTURAL:
            structural_importance += imp
        elif f in SEQUENCE:
            sequence_importance += imp

    for f, imp in feat_imp[:5]:
        ftype = "STRUCT" if f in STRUCTURAL else "SEQ" if f in SEQUENCE else "DIST"
        print(f"    [{ftype:6s}] {f:30s} {imp:.4f}")

    locus_results["structural_total_importance"] = round(structural_importance, 4)
    locus_results["sequence_total_importance"] = round(sequence_importance, 4)
    locus_results["feature_importance"] = [
        {"feature": f, "importance": round(imp, 4)} for f, imp in feat_imp[:10]
    ]

    # Pearl profile: LSSIM stats
    pearl_lssim = X[y == 1, 1]  # lssim is index 1
    non_pearl_lssim = X[y == 0, 1]
    locus_results["pearl_lssim_mean"] = (
        round(pearl_lssim.mean(), 4) if len(pearl_lssim) > 0 else None
    )
    locus_results["non_pearl_lssim_mean"] = round(non_pearl_lssim.mean(), 4)
    locus_results["lssim_separation"] = (
        round(non_pearl_lssim.mean() - pearl_lssim.mean(), 4) if len(pearl_lssim) > 0 else 0
    )

    # Sequence blind spot check
    vep_idx = ALL_FEATURES.index("vep_score")
    pearl_vep = X[y == 1, vep_idx]
    locus_results["pearls_caught_by_vep"] = int((pearl_vep >= 0.5).sum())

    return locus_results


# === Run for all three loci ===
loci = [
    (
        "HBB",
        ROOT / "results" / "HBB_Unified_Atlas_95kb.csv",
        ROOT / "config" / "locus" / "hbb_95kb_subTAD.json",
    ),
    (
        "BRCA1",
        ROOT / "results" / "BRCA1_Unified_Atlas_400kb.csv",
        ROOT / "config" / "locus" / "brca1_400kb.json",
    ),
    (
        "TP53",
        ROOT / "results" / "TP53_Unified_Atlas_300kb.csv",
        ROOT / "config" / "locus" / "tp53_300kb.json",
    ),
]

all_results = {}
for name, atlas, config in loci:
    result = process_locus(atlas, config, name)
    all_results[name] = result

# === Comparative analysis ===
print(f"\n{'=' * 60}")
print("CROSS-LOCUS COMPARISON")
print(f"{'=' * 60}")

print(f"\n  {'Locus':8s} {'Pearls':>8s} {'Struct Imp':>12s} {'Seq Imp':>10s} {'LSSIM sep':>10s}")
print(f"  {'-' * 8} {'-' * 8} {'-' * 12} {'-' * 10} {'-' * 10}")

for name in ["HBB", "BRCA1", "TP53"]:
    r = all_results[name]
    if r.get("skipped"):
        print(f"  {name:8s} {r['n_pearls']:8d} {'SKIPPED':>12s}")
        continue
    print(
        f"  {name:8s} {r['n_pearls']:8d} "
        f"{r['structural_total_importance']:12.4f} "
        f"{r['sequence_total_importance']:10.4f} "
        f"{r['lssim_separation']:10.4f}"
    )

# Verdict
hbb = all_results["HBB"]
brca1 = all_results["BRCA1"]

if not brca1.get("skipped"):
    hbb_struct_imp = hbb["structural_total_importance"]
    brca1_struct_imp = brca1["structural_total_importance"]

    if hbb_struct_imp > brca1_struct_imp + 0.1:
        tissue_verdict = (
            "CONFIRMED: structural features dominate at tissue-matched HBB "
            f"({hbb_struct_imp:.2f}) but not at mismatched BRCA1 ({brca1_struct_imp:.2f})"
        )
    elif brca1_struct_imp > hbb_struct_imp:
        tissue_verdict = (
            "REFUTED: structural features also dominate at mismatched locus (unexpected)"
        )
    else:
        tissue_verdict = "INCONCLUSIVE: similar structural importance across loci"

    print(f"\n  TISSUE-SPECIFICITY VERDICT: {tissue_verdict}")
    all_results["tissue_specificity_verdict"] = tissue_verdict

# Save
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {OUTPUT_JSON}")

# === Figure ===
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

locus_names = []
struct_imps = []
seq_imps = []
lssim_seps = []

for name in ["HBB", "BRCA1", "TP53"]:
    r = all_results[name]
    if r.get("skipped"):
        continue
    locus_names.append(name)
    struct_imps.append(r["structural_total_importance"])
    seq_imps.append(r["sequence_total_importance"])
    lssim_seps.append(r["lssim_separation"])

# Panel A: Structural vs Sequence importance
x = np.arange(len(locus_names))
width = 0.35
axes[0].bar(x - width / 2, struct_imps, width, color="#EE6677", label="Structural", alpha=0.85)
axes[0].bar(x + width / 2, seq_imps, width, color="#4477AA", label="Sequence", alpha=0.85)
axes[0].set_xticks(x)
axes[0].set_xticklabels(locus_names)
axes[0].set_ylabel("Total Feature Importance")
axes[0].set_title("A. Structural vs Sequence Importance")
axes[0].legend()

# Panel B: AUROC by config
configs_to_plot = ["all_features", "structural_only", "sequence_only"]
config_colors = ["#333333", "#EE6677", "#4477AA"]

for i, name in enumerate(locus_names):
    r = all_results[name]
    aurocs = [r[c]["AUROC"] for c in configs_to_plot]
    x_pos = np.arange(len(configs_to_plot)) + i * 0.25 - 0.25
    axes[1].bar(
        x_pos,
        aurocs,
        0.2,
        label=name if i == 0 else None,
        color=config_colors[i] if len(locus_names) <= 3 else None,
        alpha=0.85,
    )

axes[1].set_xticks(np.arange(len(configs_to_plot)))
axes[1].set_xticklabels(["All", "Struct\nonly", "Seq\nonly"])
axes[1].set_ylabel("AUROC (CV)")
axes[1].set_title("B. Pearl Detection AUROC")
axes[1].set_ylim(0.3, 1.0)

# Custom legend for Panel B
legend_b = [
    Patch(facecolor=c, label=n) for c, n in zip(config_colors[: len(locus_names)], locus_names)
]
axes[1].legend(handles=legend_b, fontsize=8)

# Panel C: LSSIM separation (pearl vs non-pearl)
bar_colors_c = ["#EE6677" if s > 0.01 else "#999999" for s in lssim_seps]
axes[2].bar(locus_names, lssim_seps, color=bar_colors_c, alpha=0.85)
axes[2].set_ylabel("ΔLSSIM (non-pearl − pearl)")
axes[2].set_title("C. LSSIM Separation")
axes[2].axhline(y=0, color="gray", linestyle="--", alpha=0.3)

plt.suptitle(
    "V1 Cross-Locus Pearl Detection: Tissue-Specificity Negative Control",
    fontsize=13,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(OUTPUT_FIG, dpi=150, bbox_inches="tight")
print(f"Figure saved to {OUTPUT_FIG}")
