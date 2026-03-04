#!/usr/bin/env python3
"""
Build integrative ARCHCODE vs CADD benchmark across all 7 loci.

ПОЧЕМУ: bioRxiv отклонил рукопись за отсутствие "new data". Интегративный
benchmark (ARCHCODE + CADD + VEP на 27,760 вариантах) создаёт новый dataset,
которого раньше не существовало.

Usage: python scripts/build_integrative_benchmark.py

Output:
  - results/integrative_benchmark.csv (all variants with all scores)
  - results/integrative_benchmark_summary.json (statistics)
  - Prints key findings to stdout
"""

import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# HBB has CADD in unified atlas, others in separate files
HBB_FILE = "HBB_Unified_Atlas_95kb.csv"
CADD_FILES = {
    "CFTR": "cadd_scores_CFTR.csv",
    "TP53": "cadd_scores_TP53.csv",
    "BRCA1": "cadd_scores_BRCA1.csv",
    "MLH1": "cadd_scores_MLH1.csv",
    "LDLR": "cadd_scores_LDLR.csv",
    "SCN5A": "cadd_scores_SCN5A.csv",
}
ATLAS_FILES = {
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
}


def load_hbb():
    """Load HBB with existing CADD scores."""
    rows = []
    with open(RESULTS_DIR / HBB_FILE) as f:
        reader = csv.DictReader(f)
        for r in reader:
            cadd = r.get("CADD_Phred", "")
            if cadd == "-1":
                cadd = "NA"
            rows.append({
                "Locus": "HBB",
                "ClinVar_ID": r["ClinVar_ID"],
                "Position": r["Position_GRCh38"],
                "Ref": r["Ref"],
                "Alt": r["Alt"],
                "Category": r["Category"],
                "ClinVar_Significance": r.get("ClinVar_Significance", ""),
                "Label": r.get("Label", ""),
                "ARCHCODE_SSIM": r.get("ARCHCODE_SSIM", ""),
                "ARCHCODE_LSSIM": r.get("ARCHCODE_LSSIM", ""),
                "VEP_Score": r.get("VEP_Score", ""),
                "CADD_Phred": cadd,
                "Pearl": r.get("Pearl", "false"),
            })
    return rows


def load_other_locus(locus: str):
    """Load a non-HBB locus, merging atlas data with CADD scores."""
    # Load CADD scores
    cadd_map = {}
    cadd_file = RESULTS_DIR / CADD_FILES[locus]
    if cadd_file.exists():
        with open(cadd_file) as f:
            for r in csv.DictReader(f):
                cadd_map[r["ClinVar_ID"]] = r.get("CADD_Phred", "NA")

    # Load atlas
    rows = []
    with open(RESULTS_DIR / ATLAS_FILES[locus]) as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = r["ClinVar_ID"]
            cadd = cadd_map.get(cid, "NA")
            rows.append({
                "Locus": locus,
                "ClinVar_ID": cid,
                "Position": r["Position_GRCh38"],
                "Ref": r["Ref"],
                "Alt": r["Alt"],
                "Category": r["Category"],
                "ClinVar_Significance": r.get("ClinVar_Significance", ""),
                "Label": r.get("Label", ""),
                "ARCHCODE_SSIM": r.get("ARCHCODE_SSIM", ""),
                "ARCHCODE_LSSIM": r.get("ARCHCODE_LSSIM", ""),
                "VEP_Score": r.get("VEP_Score", ""),
                "CADD_Phred": cadd,
                "Pearl": r.get("Pearl", "false"),
            })
    return rows


def analyze(all_rows):
    """Analyze the integrative benchmark and print key findings."""
    # Basic stats
    total = len(all_rows)
    cadd_scored = [r for r in all_rows if r["CADD_Phred"] not in ("NA", "")]
    pearls = [r for r in all_rows if r["Pearl"].lower() == "true"]
    pearls_with_cadd = [r for r in pearls if r["CADD_Phred"] not in ("NA", "")]

    print(f"\n{'='*70}")
    print(f"INTEGRATIVE BENCHMARK: ARCHCODE × CADD × VEP")
    print(f"{'='*70}")
    print(f"Total variants: {total}")
    print(f"CADD scored: {len(cadd_scored)} ({len(cadd_scored)/total*100:.1f}%)")
    print(f"Pearl variants: {len(pearls)} ({len(pearls_with_cadd)} with CADD)")

    # Per-locus stats
    print(f"\n--- Per-Locus Summary ---")
    loci = defaultdict(list)
    for r in all_rows:
        loci[r["Locus"]].append(r)

    for locus in ["HBB", "CFTR", "TP53", "BRCA1", "MLH1", "LDLR", "SCN5A"]:
        rows = loci[locus]
        scored = [r for r in rows if r["CADD_Phred"] not in ("NA", "")]
        locus_pearls = [r for r in rows if r["Pearl"].lower() == "true"]
        print(f"  {locus:6s}: {len(rows):6d} variants, "
              f"{len(scored):5d} CADD-scored ({len(scored)/len(rows)*100:.0f}%), "
              f"{len(locus_pearls)} pearls")

    # Pearl variant CADD analysis (KEY RESULT)
    print(f"\n--- Pearl Variants: CADD Distribution ---")
    if pearls_with_cadd:
        pearl_cadd = [float(r["CADD_Phred"]) for r in pearls_with_cadd]
        print(f"  n = {len(pearl_cadd)}")
        print(f"  Mean CADD:   {statistics.mean(pearl_cadd):.1f}")
        print(f"  Median CADD: {statistics.median(pearl_cadd):.1f}")
        print(f"  Range:       [{min(pearl_cadd):.1f}, {max(pearl_cadd):.1f}]")

        # Pathogenic vs benign CADD for comparison
        path_cadd = [float(r["CADD_Phred"]) for r in cadd_scored
                     if r["Label"] == "Pathogenic" and r["Pearl"].lower() != "true"]
        ben_cadd = [float(r["CADD_Phred"]) for r in cadd_scored
                    if r["Label"] == "Benign" and r["Pearl"].lower() != "true"]

        if path_cadd:
            print(f"\n  Non-pearl Pathogenic: mean={statistics.mean(path_cadd):.1f}, "
                  f"median={statistics.median(path_cadd):.1f} (n={len(path_cadd)})")
        if ben_cadd:
            print(f"  Non-pearl Benign:     mean={statistics.mean(ben_cadd):.1f}, "
                  f"median={statistics.median(ben_cadd):.1f} (n={len(ben_cadd)})")

        # Three-zone classification
        low = sum(1 for c in pearl_cadd if c < 10)
        mid = sum(1 for c in pearl_cadd if 10 <= c < 20)
        high = sum(1 for c in pearl_cadd if 20 <= c < 30)
        vhigh = sum(1 for c in pearl_cadd if c >= 30)
        print(f"\n  Pearl CADD zones:")
        print(f"    <10 (CADD-benign):    {low}")
        print(f"    10-20 (ambiguous):    {mid}")
        print(f"    20-30 (elevated):     {high}")
        print(f"    30+ (CADD-pathogenic): {vhigh}")

    # Concordance matrix: ARCHCODE × CADD
    print(f"\n--- Concordance: ARCHCODE × CADD ---")
    # ARCHCODE threshold: LSSIM < 0.95 = structural pathogenic
    # CADD threshold: phred >= 20 = likely pathogenic
    q_both = 0  # both flag
    q_archcode = 0  # only ARCHCODE flags
    q_cadd = 0  # only CADD flags
    q_neither = 0  # neither flags
    for r in cadd_scored:
        lssim = float(r["ARCHCODE_LSSIM"]) if r["ARCHCODE_LSSIM"] else 1.0
        cadd = float(r["CADD_Phred"])
        arch_flag = lssim < 0.95
        cadd_flag = cadd >= 20
        if arch_flag and cadd_flag:
            q_both += 1
        elif arch_flag and not cadd_flag:
            q_archcode += 1
        elif not arch_flag and cadd_flag:
            q_cadd += 1
        else:
            q_neither += 1

    total_q = q_both + q_archcode + q_cadd + q_neither
    print(f"  ARCHCODE+ & CADD+: {q_both:5d} ({q_both/total_q*100:.1f}%)")
    print(f"  ARCHCODE+ only:    {q_archcode:5d} ({q_archcode/total_q*100:.1f}%)")
    print(f"  CADD+ only:        {q_cadd:5d} ({q_cadd/total_q*100:.1f}%)")
    print(f"  Both negative:     {q_neither:5d} ({q_neither/total_q*100:.1f}%)")

    return {
        "total_variants": total,
        "cadd_scored": len(cadd_scored),
        "cadd_coverage_pct": round(len(cadd_scored) / total * 100, 1),
        "total_pearls": len(pearls),
        "pearls_with_cadd": len(pearls_with_cadd),
        "pearl_cadd_mean": round(statistics.mean(pearl_cadd), 1) if pearls_with_cadd else None,
        "pearl_cadd_median": round(statistics.median(pearl_cadd), 1) if pearls_with_cadd else None,
        "concordance": {
            "both_positive": q_both,
            "archcode_only": q_archcode,
            "cadd_only": q_cadd,
            "both_negative": q_neither,
        },
        "per_locus": {
            locus: {
                "total": len(rows),
                "cadd_scored": len([r for r in rows if r["CADD_Phred"] not in ("NA", "")]),
                "pearls": len([r for r in rows if r["Pearl"].lower() == "true"]),
            }
            for locus, rows in loci.items()
        },
    }


def main():
    print("Building integrative benchmark...")

    # Load all loci
    all_rows = load_hbb()
    print(f"  HBB: {len(all_rows)} variants")

    for locus in ["CFTR", "TP53", "BRCA1", "MLH1", "LDLR", "SCN5A"]:
        cadd_file = RESULTS_DIR / CADD_FILES[locus]
        if not cadd_file.exists():
            print(f"  {locus}: CADD scores not yet available, skipping")
            continue
        rows = load_other_locus(locus)
        all_rows.extend(rows)
        print(f"  {locus}: {len(rows)} variants")

    # Write unified CSV
    output_csv = RESULTS_DIR / "integrative_benchmark.csv"
    fieldnames = ["Locus", "ClinVar_ID", "Position", "Ref", "Alt", "Category",
                  "ClinVar_Significance", "Label", "ARCHCODE_SSIM", "ARCHCODE_LSSIM",
                  "VEP_Score", "CADD_Phred", "Pearl"]
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n  Unified CSV: {output_csv} ({len(all_rows)} rows)")

    # Analyze
    summary = analyze(all_rows)

    # Write summary JSON
    output_json = RESULTS_DIR / "integrative_benchmark_summary.json"
    with open(output_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n  Summary JSON: {output_json}")


if __name__ == "__main__":
    main()
