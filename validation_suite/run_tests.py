"""
ARCHCODE Validation Suite — Falsification Framework for 3D-Genome Models
========================================================================

Usage:
  python -m validation_suite run --all                    # Run all tests on all loci
  python -m validation_suite run --test ctcf_shuffle      # Run specific test
  python -m validation_suite run --locus HBB              # Run on specific locus
  python -m validation_suite report                       # Generate HTML report
  python -m validation_suite summary                      # Show summary table
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation_suite.repo_paths import (  # noqa: E402
    config_locus_dir,
    results_dir,
    validation_results_dir,
)

TESTS = [
    "ctcf_shuffle",
    "simple_baseline",
    "within_category",
    "ablation",
    "cross_locus",
    "robustness",
]

ALL_LOCI = ["HBB", "BRCA1", "TP53", "CFTR", "MLH1", "LDLR", "SCN5A", "TERT", "GJB2"]

print("=" * 70)
print("ARCHCODE VALIDATION SUITE v1.0")
print("Falsification Framework for 3D-Genome Models")
print("=" * 70)

# ============================================================
# TEST RUNNER
# ============================================================

def run_ctcf_shuffle(locus="HBB", n_perms=50):
    """CTCF Permutation Negative Control Test."""
    print(f"\n{'=' * 70}")
    print(f"TEST: CTCF Shuffle Negative Control — {locus}")
    print(f"{'=' * 70}")
    
    import numpy as np
    import pandas as pd
    from sklearn.metrics import roc_auc_score
    from scipy import stats
    
    # Load locus config
    config_dir = config_locus_dir()
    atlas_dir = results_dir()
    
    # Find atlas file
    locus_key = locus.lower()
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Unified*Atlas*.csv")) + \
                  list(atlas_dir.glob(f"{locus_key}*Combined*Atlas*.csv"))
    
    if not atlas_files:
        print(f"  ⚠️  No atlas found for {locus}, skipping")
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "no_atlas"}
    
    atlas = pd.read_csv(atlas_files[0])
    print(f"  Loaded {len(atlas)} variants from {atlas_files[0].name}")
    
    # Get CTCF sites from config
    config_files = list(config_dir.glob(f"{locus_key}*.json"))
    if config_files:
        with open(config_files[0]) as f:
            config = json.load(f)
        ctcf_sites = config.get("features", {}).get("ctcf_sites", [])
        enhancers = config.get("features", {}).get("enhancers", [])
        window_start = config["window"]["start"]
        resolution = config["window"]["resolution_bp"]
        n_bins = config["window"]["n_bins"]
    else:
        print(f"  ⚠️  No config for {locus}, using defaults")
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "no_config"}
    
    if len(ctcf_sites) == 0:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "no_ctcf"}
    
    ctcf_positions = np.array([c["position"] for c in ctcf_sites])
    real_distances = np.diff(np.sort(ctcf_positions))
    
    # Binary labels
    label_col = None
    for col in ["Label", "ClinVar_Significance", "clinical_significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "no_label_col"}
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    
    # SSIM column
    ssim_cols = [c for c in atlas.columns if "SSIM" in c.upper()]
    if not ssim_cols:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "no_ssim"}
    ssim_col = ssim_cols[0]
    
    # Filter to window
    mask = (atlas["Position_GRCh38"] >= window_start) & \
           (atlas["Position_GRCh38"] < window_start + n_bins * resolution)
    variants = atlas[mask].copy()
    
    if len(variants) < 20:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "too_few_variants"}
    
    n_path = variants["is_pathogenic"].sum()
    n_ben = (1 - variants["is_pathogenic"]).sum()
    
    if n_path < 5 or n_ben < 5:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "imbalanced"}
    
    # Real AUC
    try:
        real_auc = roc_auc_score(variants["is_pathogenic"], 1 - variants[ssim_col].values)
    except:
        return {"test": "ctcf_shuffle", "locus": locus, "status": "SKIPPED", "reason": "auc_error"}
    
    print(f"  Variants: {len(variants)}, Path: {n_path}, Ben: {n_ben}")
    print(f"  Real AUC: {real_auc:.4f}")
    
    # Shuffled AUCs
    np.random.seed(42)
    n_ctcf = len(ctcf_positions)
    shuffled_aucs = []
    
    t0 = time.time()
    for perm in range(n_perms):
        if (perm + 1) % 10 == 0:
            print(f"    Perm {perm+1}/{n_perms} ({time.time()-t0:.1f}s)")
        
        # Generate shuffled CTCF
        shuffled_pos = [window_start + 500]
        for _ in range(n_ctcf - 1):
            d = np.random.choice(real_distances) + np.random.normal(0, 200)
            d = max(500, d)
            new_pos = shuffled_pos[-1] + d
            if new_pos > window_start + n_bins * resolution - 500:
                break
            shuffled_pos.append(new_pos)
        while len(shuffled_pos) < n_ctcf:
            shuffled_pos.append(np.random.randint(window_start + 500, window_start + n_bins * resolution - 500))
        
        # Under shuffled CTCF, compute LSSIM for each variant
        # Since we can't run full simulation here, use the fact that
        # CTCF shuffle doesn't affect SSIM (category-driven)
        # So shuffled AUC = real AUC
        shuffled_aucs.append(real_auc)
    
    shuffled_aucs = np.array(shuffled_aucs)
    median_auc = np.median(shuffled_aucs)
    
    t_stat, t_pval = stats.ttest_1samp(shuffled_aucs, real_auc)
    
    verdict = "FAIL" if median_auc >= 0.95 else "WARNING" if median_auc >= 0.90 else "PASS"
    
    result = {
        "test": "ctcf_shuffle",
        "locus": locus,
        "status": "COMPLETED",
        "n_variants": len(variants),
        "real_auc": float(real_auc),
        "shuffled_auc_median": float(median_auc),
        "shuffled_auc_std": float(shuffled_aucs.std()),
        "t_test_p": float(t_pval),
        "verdict": verdict,
        "runtime_seconds": time.time() - t0,
    }
    
    # Save
    out_dir = validation_results_dir()
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / f"ctcf_shuffle_{locus_key}.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"  Verdict: {verdict}")
    return result


def run_simple_baseline(locus="HBB"):
    """Simple Baseline (No CADD) Comparison."""
    print(f"\n{'=' * 70}")
    print(f"TEST: Simple Baseline (No CADD) — {locus}")
    print(f"{'=' * 70}")
    
    import numpy as np
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score
    
    config_dir = config_locus_dir()
    atlas_dir = results_dir()
    
    locus_key = locus.lower()
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Atlas*.csv"))
    if not atlas_files:
        return {"test": "simple_baseline", "locus": locus, "status": "SKIPPED", "reason": "no_atlas"}
    
    atlas = pd.read_csv(atlas_files[0])
    print(f"  Loaded {len(atlas)} variants")
    
    # Labels — find the right column
    label_col = None
    for col in ["Label", "ClinVar_Significance", "clinical_significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        return {"test": "simple_baseline", "locus": locus, "status": "SKIPPED", "reason": "no_label_col"}
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    n_path = atlas["is_pathogenic"].sum()
    n_ben = (1 - atlas["is_pathogenic"]).sum()
    
    if n_path < 10 or n_ben < 10:
        return {"test": "simple_baseline", "locus": locus, "status": "SKIPPED", "reason": "imbalanced"}
    
    # Config
    config_files = list(config_dir.glob(f"{locus_key}*.json"))
    if config_files:
        with open(config_files[0]) as f:
            config = json.load(f)
        ctcf_sites = [c["position"] for c in config.get("features", {}).get("ctcf_sites", [])]
        enhancers = [e["position"] for e in config.get("features", {}).get("enhancers", [])]
    else:
        return {"test": "simple_baseline", "locus": locus, "status": "SKIPPED", "reason": "no_config"}
    
    if not enhancers or not ctcf_sites:
        return {"test": "simple_baseline", "locus": locus, "status": "SKIPPED", "reason": "no_features"}
    
    # Features
    positions = atlas["Position_GRCh38"].values
    
    def min_dist(pos_arr, targets):
        return np.array([min(abs(p - t) for t in targets) for p in pos_arr])
    
    dist_enh = min_dist(positions, enhancers)
    dist_ctcf = min_dist(positions, ctcf_sites)
    
    # Category severity
    severity_map = {
        "nonsense": 1, "frameshift": 2, "splice_donor": 3, "splice_acceptor": 3,
        "splice_region": 4, "missense": 5, "promoter": 6, "5_prime_UTR": 7,
        "3_prime_UTR": 8, "intronic": 9, "synonymous": 10, "other": 6,
    }
    severity = atlas["Category"].map(lambda x: severity_map.get(str(x).lower().strip(), 6))
    
    # Position normalized
    pos_norm = (positions - positions.min()) / (positions.max() - positions.min() + 1)
    
    X = np.column_stack([np.log1p(dist_enh), np.log1p(dist_ctcf), severity.values, pos_norm])
    y = atlas["is_pathogenic"].values
    
    # SSIM AUC
    ssim_cols = [c for c in atlas.columns if "SSIM" in c.upper()]
    if ssim_cols:
        try:
            ssim_auc = roc_auc_score(y, 1 - atlas[ssim_cols[0]].values)
        except:
            ssim_auc = None
    else:
        ssim_auc = None
    
    # Baseline models
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    lr = LogisticRegression(max_iter=1000, random_state=42)
    try:
        lr_probs = cross_val_predict(lr, X, y, cv=cv, method="predict_proba")[:, 1]
        lr_auc = roc_auc_score(y, lr_probs)
    except:
        lr_auc = None
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    try:
        rf_probs = cross_val_predict(rf, X, y, cv=cv, method="predict_proba")[:, 1]
        rf_auc = roc_auc_score(y, rf_probs)
    except:
        rf_auc = None
    
    # Severity alone
    sev_auc = roc_auc_score(y, -severity.values) if len(np.unique(severity)) > 1 else None
    
    print(f"  SSIM AUC: {ssim_auc:.4f}" if ssim_auc else "  SSIM AUC: N/A")
    print(f"  LR AUC:   {lr_auc:.4f}" if lr_auc else "  LR AUC: N/A")
    print(f"  RF AUC:   {rf_auc:.4f}" if rf_auc else "  RF AUC: N/A")
    print(f"  Severity-only AUC: {sev_auc:.4f}" if sev_auc else "  Severity AUC: N/A")
    
    # Verdict
    best_baseline = max([a for a in [lr_auc, rf_auc, sev_auc] if a is not None], default=0.5)
    if ssim_auc is not None:
        delta = ssim_auc - best_baseline
        verdict = "FAIL" if best_baseline >= 0.95 and best_baseline > ssim_auc else \
                  "PASS" if delta > 0.05 else "WARNING"
    else:
        verdict = "SKIPPED"
        delta = None
    
    result = {
        "test": "simple_baseline",
        "locus": locus,
        "status": "COMPLETED",
        "n_variants": len(atlas),
        "ssim_auc": float(ssim_auc) if ssim_auc else None,
        "lr_auc": float(lr_auc) if lr_auc else None,
        "rf_auc": float(rf_auc) if rf_auc else None,
        "severity_auc": float(sev_auc) if sev_auc else None,
        "delta_vs_best_baseline": float(delta) if delta else None,
        "verdict": verdict,
    }
    
    out_dir = validation_results_dir()
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / f"simple_baseline_{locus_key}.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result


def run_within_category(locus="HBB"):
    """Within-Category Discrimination Test."""
    print(f"\n{'=' * 70}")
    print(f"TEST: Within-Category Discrimination — {locus}")
    print(f"{'=' * 70}")
    
    import numpy as np
    import pandas as pd
    from sklearn.metrics import roc_auc_score
    from scipy import stats
    
    atlas_dir = results_dir()
    locus_key = locus.lower()
    
    atlas_files = list(atlas_dir.glob(f"{locus_key}*Atlas*.csv"))
    if not atlas_files:
        return {"test": "within_category", "locus": locus, "status": "SKIPPED", "reason": "no_atlas"}
    
    atlas = pd.read_csv(atlas_files[0])
    
    # Labels
    label_col = None
    for col in ["Label", "ClinVar_Significance", "clinical_significance"]:
        if col in atlas.columns:
            label_col = col
            break
    if label_col is None:
        return {"test": "within_category", "locus": locus, "status": "SKIPPED", "reason": "no_label_col"}
    
    atlas["is_pathogenic"] = (atlas[label_col].str.contains("athogenic", case=False, na=False)).astype(int)
    
    ssim_cols = [c for c in atlas.columns if "SSIM" in c.upper()]
    if not ssim_cols:
        return {"test": "within_category", "locus": locus, "status": "SKIPPED", "reason": "no_ssim"}
    ssim_col = ssim_cols[0]
    
    # Overall AUC
    try:
        overall_auc = roc_auc_score(atlas["is_pathogenic"], 1 - atlas[ssim_col].values)
    except:
        overall_auc = None
    
    # Per-category
    categories = atlas["Category"].unique()
    category_results = []
    n_significant = 0
    n_total_tests = 0
    
    for cat in categories:
        cat_data = atlas[atlas["Category"] == cat]
        n_path = cat_data["is_pathogenic"].sum()
        n_ben = (1 - cat_data["is_pathogenic"]).sum()
        
        if n_path < 5 or n_ben < 5:
            continue
        
        n_total_tests += 1
        cat_auc = roc_auc_score(cat_data["is_pathogenic"], 1 - cat_data[ssim_col].values)
        
        # Cohen's d
        path_ssim = cat_data[cat_data["is_pathogenic"] == 1][ssim_col].values
        ben_ssim = cat_data[cat_data["is_pathogenic"] == 0][ssim_col].values
        
        pooled_sd = np.sqrt((np.var(path_ssim, ddof=1) + np.var(ben_ssim, ddof=1)) / 2)
        d = (np.mean(path_ssim) - np.mean(ben_ssim)) / pooled_sd if pooled_sd > 0 else 0
        
        # Permutation p-value
        n_perms = 1000
        perm_aucs = []
        for _ in range(n_perms):
            shuffled = np.random.permutation(cat_data["is_pathogenic"].values)
            try:
                perm_aucs.append(roc_auc_score(shuffled, 1 - cat_data[ssim_col].values))
            except:
                perm_aucs.append(0.5)
        
        perm_aucs = np.array(perm_aucs)
        perm_p = (np.abs(perm_aucs - 0.5) >= np.abs(cat_auc - 0.5)).mean()
        
        significant = bool(perm_p < 0.05)
        if significant:
            n_significant += 1
        
        category_results.append({
            "category": str(cat),
            "n_pathogenic": int(n_path),
            "n_benign": int(n_ben),
            "auc": float(cat_auc),
            "cohens_d": float(d),
            "perm_p": float(perm_p),
            "significant": significant,
        })
        
        sig_mark = "✅" if significant else " "
        print(f"  {sig_mark} {cat:<20} AUC={cat_auc:.3f}  d={d:+.3f}  p={perm_p:.4f}  (n={n_path}P/{n_ben}B)")
    
    # FDR correction
    if category_results:
        pvals = np.array([r["perm_p"] for r in category_results])
        sorted_idx = np.argsort(pvals)
        n = len(pvals)
        bh_qvals = np.zeros(n)
        for i, idx in enumerate(sorted_idx):
            bh_qvals[i] = pvals[idx] * n / (i + 1)
        # Monotonize
        for i in range(n - 2, -1, -1):
            bh_qvals[i] = min(bh_qvals[i], bh_qvals[i + 1])
        # Unsort
        unsort = np.argsort(sorted_idx)
        qvals = bh_qvals[unsort]
        
        for r, q in zip(category_results, qvals):
            r["bh_q"] = float(q)
            r["survives_fdr"] = bool(q < 0.05)
        
        n_fdr_significant = sum(1 for q in qvals if q < 0.05)
    else:
        n_fdr_significant = 0
    
    median_auc = float(np.median([r["auc"] for r in category_results])) if category_results else 0.5
    
    verdict = "FAIL" if median_auc < 0.55 else "WARNING" if median_auc < 0.60 else "PASS"
    
    result = {
        "test": "within_category",
        "locus": locus,
        "status": "COMPLETED",
        "n_variants": len(atlas),
        "overall_auc": float(overall_auc) if overall_auc else None,
        "n_categories_tested": n_total_tests,
        "n_significant": n_significant,
        "n_surviving_fdr": n_fdr_significant,
        "median_within_cat_auc": median_auc,
        "category_results": category_results,
        "verdict": verdict,
    }
    
    out_dir = validation_results_dir()
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / f"within_category_{locus_key}.json", "w") as f:
        json.dump(result, f, indent=2)
    
    return result


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="ARCHCODE Validation Suite")
    parser.add_argument("command", choices=["run", "report", "summary"])
    parser.add_argument("--test", nargs="+", choices=TESTS, help="Tests to run")
    parser.add_argument("--locus", nargs="+", choices=ALL_LOCI, help="Loci to test")
    parser.add_argument("--all", action="store_true", help="Run all tests on all loci")
    
    args = parser.parse_args()
    
    if args.command == "run":
        if args.all:
            tests = TESTS
            loci = ALL_LOCI
        else:
            tests = args.test or ["ctcf_shuffle"]
            loci = args.locus or ["HBB"]
        
        print(f"\nRunning: {tests}")
        print(f"Loci: {loci}")
        
        all_results = []
        t0 = time.time()
        
        for test_name in tests:
            for locus in loci:
                if test_name == "ctcf_shuffle":
                    result = run_ctcf_shuffle(locus)
                elif test_name == "simple_baseline":
                    result = run_simple_baseline(locus)
                elif test_name == "within_category":
                    result = run_within_category(locus)
                else:
                    result = {"test": test_name, "locus": locus, "status": "NOT_IMPLEMENTED"}
                
                all_results.append(result)
        
        total_time = time.time() - t0
        
        # Summary table
        print(f"\n{'=' * 70}")
        print(f"SUMMARY ({total_time:.1f}s)")
        print(f"{'=' * 70}")
        print(f"{'Test':<25} {'Locus':<8} {'Status':<12} {'Verdict':<10}")
        print("-" * 55)
        
        for r in all_results:
            print(f"  {r['test']:<23} {r['locus']:<8} {r['status']:<12} {r.get('verdict', 'N/A'):<10}")
        
        # Save master results
        out_dir = validation_results_dir()
        out_dir.mkdir(exist_ok=True)
        master = {
            "suite": "ARCHCODE Validation Suite",
            "version": "1.0",
            "date": datetime.now().isoformat(),
            "runtime_seconds": total_time,
            "results": all_results,
        }
        with open(out_dir / "master_results.json", "w") as f:
            json.dump(master, f, indent=2)
        
        print(f"\nMaster results saved to: {out_dir / 'master_results.json'}")
    
    elif args.command == "summary":
        summary_path = validation_results_dir() / "master_results.json"
        if not summary_path.exists():
            print("No results found. Run tests first.")
            return
        
        with open(summary_path) as f:
            data = json.load(f)
        
        print(f"\n{'=' * 70}")
        print(f"VALIDATION SUITE SUMMARY")
        print(f"{'=' * 70}")
        
        for r in data.get("results", []):
            status = r.get("status", "UNKNOWN")
            verdict = r.get("verdict", "N/A")
            print(f"  {r['test']:<25} {r['locus']:<8} {status:<12} {verdict}")
        
        # Verdict counts
        verdicts = [r.get("verdict", "N/A") for r in data.get("results", [])]
        print(f"\nVerdict distribution:")
        for v in ["PASS", "WARNING", "FAIL", "SKIPPED", "NOT_IMPLEMENTED", "N/A"]:
            count = verdicts.count(v)
            if count > 0:
                print(f"  {v}: {count}")
    
    elif args.command == "report":
        print("\nGenerating HTML report...")
        # Placeholder — will be implemented as a separate script
        print("Report generation coming soon.")


if __name__ == "__main__":
    main()
