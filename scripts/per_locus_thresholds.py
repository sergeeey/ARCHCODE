#!/usr/bin/env python3
"""
Per-locus LSSIM threshold analysis across 9 ARCHCODE loci.

ПОЧЕМУ: Universal threshold (LSSIM < 0.95) works for HBB but produces FPs
for BRCA1/TP53. Per-locus thresholds calibrated on benign LSSIM distributions
solve this and demonstrate tissue-specificity of structural discrimination.

Output:
  - results/per_locus_thresholds.csv (detailed per-locus stats)
  - Prints manuscript-ready table to stdout
  - results/per_locus_thresholds_summary.json

Usage: python scripts/per_locus_thresholds.py
"""

import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Atlas files for all 9 loci
ATLAS_FILES = {
    "HBB":   "HBB_Unified_Atlas_95kb.csv",
    "CFTR":  "CFTR_Unified_Atlas_317kb.csv",
    "TP53":  "TP53_Unified_Atlas_300kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "MLH1":  "MLH1_Unified_Atlas_300kb.csv",
    "LDLR":  "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
    "TERT":  "TERT_Unified_Atlas_300kb.csv",
    "GJB2":  "GJB2_Unified_Atlas_300kb.csv",
}

# Locus metadata for interpretation
LOCUS_META = {
    "HBB":   {"tissue": "matched", "type": "regulatory", "gene": "beta-globin"},
    "CFTR":  {"tissue": "partial", "type": "mixed", "gene": "CFTR"},
    "TP53":  {"tissue": "partial", "type": "coding", "gene": "TP53"},
    "BRCA1": {"tissue": "partial", "type": "coding", "gene": "BRCA1"},
    "MLH1":  {"tissue": "partial", "type": "coding", "gene": "MLH1"},
    "LDLR":  {"tissue": "partial", "type": "coding", "gene": "LDLR"},
    "SCN5A": {"tissue": "mismatch", "type": "coding", "gene": "SCN5A (cardiac)"},
    "TERT":  {"tissue": "expressed", "type": "inter-TAD", "gene": "TERT (telomerase)"},
    "GJB2":  {"tissue": "mismatch", "type": "coding", "gene": "GJB2 (cochlear)"},
}


def percentile(data, p):
    """Compute p-th percentile of data."""
    if not data:
        return None
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


def sensitivity_specificity(path_lssim, ben_lssim, threshold):
    """Compute sensitivity (TP rate) and specificity (TN rate) at threshold."""
    if not path_lssim or not ben_lssim:
        return None, None, None, None
    tp = sum(1 for x in path_lssim if x < threshold)
    fn = sum(1 for x in path_lssim if x >= threshold)
    tn = sum(1 for x in ben_lssim if x >= threshold)
    fp = sum(1 for x in ben_lssim if x < threshold)
    sens = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    return sens, spec, fp, tp


def find_optimal_threshold(path_lssim, ben_lssim, max_fpr=0.01):
    """Find threshold that maximizes sensitivity at FPR <= max_fpr."""
    if not path_lssim or not ben_lssim:
        return None, None, None
    # Scan thresholds from min to max LSSIM
    all_vals = sorted(set(path_lssim + ben_lssim))
    best_thresh = None
    best_sens = 0
    best_spec = 1
    for thresh in all_vals:
        sens, spec, fp, tp = sensitivity_specificity(path_lssim, ben_lssim, thresh)
        fpr = 1 - spec
        if fpr <= max_fpr and sens > best_sens:
            best_thresh = thresh
            best_sens = sens
            best_spec = spec
    return best_thresh, best_sens, best_spec


def analyze_locus(locus, filepath):
    """Analyze LSSIM distributions for a single locus."""
    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    path_lssim = []
    ben_lssim = []
    path_ssim = []
    ben_ssim = []
    categories = defaultdict(lambda: {"path": [], "ben": []})

    for r in rows:
        lssim = float(r["ARCHCODE_LSSIM"]) if r.get("ARCHCODE_LSSIM") else None
        ssim = float(r["ARCHCODE_SSIM"]) if r.get("ARCHCODE_SSIM") else None
        label = r.get("Label", "")
        cat = r.get("Category", "other")

        if lssim is None:
            continue

        if label == "Pathogenic":
            path_lssim.append(lssim)
            if ssim is not None:
                path_ssim.append(ssim)
            categories[cat]["path"].append(lssim)
        elif label == "Benign":
            ben_lssim.append(lssim)
            if ssim is not None:
                ben_ssim.append(ssim)
            categories[cat]["ben"].append(lssim)

    # Basic stats
    result = {
        "locus": locus,
        "n_path": len(path_lssim),
        "n_ben": len(ben_lssim),
        "n_total": len(path_lssim) + len(ben_lssim),
    }

    if path_lssim:
        result["path_mean"] = round(statistics.mean(path_lssim), 6)
        result["path_median"] = round(statistics.median(path_lssim), 6)
        result["path_min"] = round(min(path_lssim), 6)
        result["path_5th"] = round(percentile(path_lssim, 5), 6)
    if ben_lssim:
        result["ben_mean"] = round(statistics.mean(ben_lssim), 6)
        result["ben_median"] = round(statistics.median(ben_lssim), 6)
        result["ben_min"] = round(min(ben_lssim), 6)
        result["ben_1st"] = round(percentile(ben_lssim, 1), 6)
        result["ben_5th"] = round(percentile(ben_lssim, 5), 6)

    # Delta (separation)
    if path_lssim and ben_lssim:
        result["delta_mean"] = round(
            statistics.mean(ben_lssim) - statistics.mean(path_lssim), 6
        )
        result["delta_median"] = round(
            statistics.median(ben_lssim) - statistics.median(path_lssim), 6
        )

    # Universal threshold (0.95) performance
    if path_lssim and ben_lssim:
        sens, spec, fp, tp = sensitivity_specificity(path_lssim, ben_lssim, 0.95)
        result["univ_sens"] = round(sens, 4)
        result["univ_spec"] = round(spec, 4)
        result["univ_fp"] = fp
        result["univ_tp"] = tp

    # Per-locus optimal threshold (FPR <= 1%)
    if path_lssim and ben_lssim:
        opt_thresh, opt_sens, opt_spec = find_optimal_threshold(
            path_lssim, ben_lssim, max_fpr=0.01
        )
        if opt_thresh is not None:
            result["opt_threshold"] = round(opt_thresh, 6)
            result["opt_sens"] = round(opt_sens, 4)
            result["opt_spec"] = round(opt_spec, 4)

    # Benign 1st percentile as conservative threshold
    if ben_lssim:
        ben_1st = percentile(ben_lssim, 1)
        sens_at_1st, spec_at_1st, _, _ = sensitivity_specificity(
            path_lssim, ben_lssim, ben_1st
        ) if path_lssim else (None, None, None, None)
        result["ben1_threshold"] = round(ben_1st, 6)
        if sens_at_1st is not None:
            result["ben1_sens"] = round(sens_at_1st, 4)
            result["ben1_spec"] = round(spec_at_1st, 4)

    # Per-category breakdown (top 3 by count)
    cat_summary = {}
    for cat, vals in sorted(categories.items(), key=lambda x: -len(x[1]["path"])-len(x[1]["ben"])):
        n_p = len(vals["path"])
        n_b = len(vals["ben"])
        if n_p + n_b < 5:
            continue
        cat_entry = {"n_path": n_p, "n_ben": n_b}
        if vals["path"]:
            cat_entry["path_mean"] = round(statistics.mean(vals["path"]), 6)
        if vals["ben"]:
            cat_entry["ben_mean"] = round(statistics.mean(vals["ben"]), 6)
        if vals["path"] and vals["ben"]:
            cat_entry["delta"] = round(
                statistics.mean(vals["ben"]) - statistics.mean(vals["path"]), 6
            )
        cat_summary[cat] = cat_entry
    result["categories"] = cat_summary

    # Tissue match metadata
    result["tissue"] = LOCUS_META[locus]["tissue"]
    result["gene_type"] = LOCUS_META[locus]["type"]

    return result


def main():
    print("=" * 72)
    print("PER-LOCUS LSSIM THRESHOLD ANALYSIS — 9 ARCHCODE Loci")
    print("=" * 72)

    all_results = []
    locus_order = ["HBB", "CFTR", "TP53", "BRCA1", "MLH1", "LDLR", "SCN5A", "TERT", "GJB2"]

    for locus in locus_order:
        filepath = RESULTS_DIR / ATLAS_FILES[locus]
        if not filepath.exists():
            print(f"  {locus}: atlas not found, skipping")
            continue
        result = analyze_locus(locus, filepath)
        all_results.append(result)

    # Print manuscript-ready table
    print(f"\n{'─' * 72}")
    print("TABLE: Per-Locus LSSIM Threshold Calibration")
    print(f"{'─' * 72}")
    header = (
        f"{'Locus':6s} {'Tissue':9s} {'N':>6s} "
        f"{'Path LSSIM':>10s} {'Ben LSSIM':>10s} {'Δ':>8s} "
        f"{'Univ 0.95':>10s} {'Opt Thresh':>10s} {'Opt Sens':>8s}"
    )
    print(header)
    print("─" * len(header))

    for r in all_results:
        path_mean = f"{r.get('path_mean', 0):.4f}" if "path_mean" in r else "N/A"
        ben_mean = f"{r.get('ben_mean', 0):.4f}" if "ben_mean" in r else "N/A"
        delta = f"{r.get('delta_mean', 0):.4f}" if "delta_mean" in r else "N/A"

        univ = "N/A"
        if "univ_sens" in r and "univ_fp" in r:
            univ = f"{r['univ_sens']:.1%}/{r['univ_fp']}FP"

        opt = "N/A"
        opt_sens = "N/A"
        if "opt_threshold" in r:
            opt = f"{r['opt_threshold']:.4f}"
            opt_sens = f"{r['opt_sens']:.1%}"

        print(
            f"{r['locus']:6s} {r['tissue']:9s} {r['n_total']:>6d} "
            f"{path_mean:>10s} {ben_mean:>10s} {delta:>8s} "
            f"{univ:>10s} {opt:>10s} {opt_sens:>8s}"
        )

    # Print detailed analysis per locus
    print(f"\n{'=' * 72}")
    print("DETAILED PER-LOCUS ANALYSIS")
    print(f"{'=' * 72}")

    for r in all_results:
        locus = r["locus"]
        meta = LOCUS_META[locus]
        print(f"\n--- {locus} ({meta['gene']}) — tissue: {meta['tissue']}, type: {meta['type']} ---")
        print(f"  Variants: {r['n_path']} Path + {r['n_ben']} Ben = {r['n_total']}")
        if "path_mean" in r:
            print(f"  Path LSSIM: mean={r['path_mean']:.4f}, median={r.get('path_median','N/A')}, min={r.get('path_min','N/A')}")
        if "ben_mean" in r:
            print(f"  Ben LSSIM:  mean={r['ben_mean']:.4f}, median={r.get('ben_median','N/A')}, min={r.get('ben_min','N/A')}")
        if "delta_mean" in r:
            print(f"  Δ(mean):    {r['delta_mean']:.4f} (ben - path)")

        if "univ_sens" in r:
            print(f"  Universal threshold (0.95): sens={r['univ_sens']:.1%}, spec={r['univ_spec']:.1%}, FP={r['univ_fp']}, TP={r['univ_tp']}")

        if "opt_threshold" in r:
            print(f"  Optimal (FPR≤1%): threshold={r['opt_threshold']:.4f}, sens={r['opt_sens']:.1%}, spec={r['opt_spec']:.1%}")
        else:
            print(f"  Optimal: no threshold achieves FPR≤1% with any sensitivity")

        if "ben1_threshold" in r:
            print(f"  Ben 1st percentile: {r['ben1_threshold']:.4f}", end="")
            if "ben1_sens" in r:
                print(f" → sens={r['ben1_sens']:.1%}, spec={r['ben1_spec']:.1%}")
            else:
                print()

        # Top categories
        if r.get("categories"):
            print(f"  Category breakdown:")
            for cat, cv in list(r["categories"].items())[:5]:
                p_mean = f"{cv['path_mean']:.4f}" if "path_mean" in cv else "N/A"
                b_mean = f"{cv['ben_mean']:.4f}" if "ben_mean" in cv else "N/A"
                delta_cat = f"Δ={cv['delta']:.4f}" if "delta" in cv else ""
                print(f"    {cat:20s} Path={p_mean} Ben={b_mean} {delta_cat} (n={cv['n_path']}P+{cv['n_ben']}B)")

    # Tissue-specificity gradient summary
    print(f"\n{'=' * 72}")
    print("TISSUE-SPECIFICITY GRADIENT")
    print(f"{'=' * 72}")
    gradient = sorted(all_results, key=lambda r: -r.get("delta_mean", 0))
    for r in gradient:
        delta = r.get("delta_mean", 0)
        bar = "█" * int(delta * 2000)  # scale for visibility
        signal = "STRONG" if delta > 0.01 else "MODERATE" if delta > 0.003 else "WEAK" if delta > 0.001 else "NULL"
        print(f"  {r['locus']:6s} [{r['tissue']:9s}] Δ={delta:.4f} {bar} {signal}")

    # Write CSV
    output_csv = RESULTS_DIR / "per_locus_thresholds.csv"
    fieldnames = [
        "locus", "tissue", "gene_type", "n_path", "n_ben", "n_total",
        "path_mean", "path_median", "path_min", "path_5th",
        "ben_mean", "ben_median", "ben_min", "ben_1st", "ben_5th",
        "delta_mean", "delta_median",
        "univ_sens", "univ_spec", "univ_fp", "univ_tp",
        "opt_threshold", "opt_sens", "opt_spec",
        "ben1_threshold", "ben1_sens", "ben1_spec",
    ]
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in all_results:
            writer.writerow(r)
    print(f"\nCSV saved: {output_csv}")

    # Write JSON summary
    output_json = RESULTS_DIR / "per_locus_thresholds_summary.json"
    with open(output_json, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"JSON saved: {output_json}")


if __name__ == "__main__":
    main()
