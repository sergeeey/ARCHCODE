#!/usr/bin/env python3
"""
Extract benign VEP data from HBB_Combined_Atlas.csv.

The Combined Atlas has 750 benign rows with VEP data already embedded.
This script extracts them into the same CSV format as data/hbb_vep_results.csv
so the unified TypeScript pipeline can load both identically.

Usage: python scripts/extract_benign_vep.py
"""

import csv
from pathlib import Path

COMBINED_CSV = Path(__file__).parent.parent / "results" / "HBB_Combined_Atlas.csv"
BENIGN_VARIANTS_CSV = Path(__file__).parent.parent / "data" / "hbb_benign_variants.csv"
OUTPUT_CSV = Path(__file__).parent.parent / "data" / "hbb_benign_vep_results.csv"

# Map VEP_Consequence → interpretation (same logic as pathogenic pipeline)
def get_interpretation(vep_score: float, sift_score: float) -> str:
    if vep_score >= 0.8:
        return "Very High Impact"
    elif vep_score >= 0.5:
        return "High Impact"
    elif vep_score >= 0.3:
        return "Moderate Impact"
    elif vep_score >= 0.1:
        return "Low Impact"
    else:
        return "Minimal Impact"


def main():
    # Read benign variants CSV for chr/position/ref/alt/category
    benign_variants = {}
    with open(BENIGN_VARIANTS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            benign_variants[row["clinvar_id"]] = row

    print(f"Loaded {len(benign_variants)} benign variants from {BENIGN_VARIANTS_CSV.name}")

    # Read Combined Atlas for VEP columns
    rows_written = 0
    with open(COMBINED_CSV, "r") as fin, open(OUTPUT_CSV, "w", newline="") as fout:
        reader = csv.DictReader(fin)
        writer = csv.writer(fout)
        writer.writerow([
            "clinvar_id", "chr", "position", "ref", "alt", "category",
            "vep_consequence", "vep_impact", "vep_score", "sift_score",
            "sift_prediction", "amino_acids", "interpretation"
        ])

        for row in reader:
            if row["Label"] != "Benign":
                continue

            clinvar_id = row["ClinVar_ID"]
            vep_score = float(row["VEP_Score"]) if row["VEP_Score"] else 0.0
            sift_score_raw = row.get("SIFT_Score", "")
            sift_score = float(sift_score_raw) if sift_score_raw and sift_score_raw != "" else -1.0

            # Get chr from benign variants if available, else default
            bv = benign_variants.get(clinvar_id, {})
            chr_val = bv.get("chr", "11")

            writer.writerow([
                clinvar_id,
                chr_val,
                row["Position_GRCh38"],
                row["Ref"],
                row["Alt"],
                row["Category"],
                row["VEP_Consequence"],
                "MODIFIER",  # Default — Combined Atlas doesn't store VEP_Impact for benign
                f"{vep_score:.2f}",
                f"{sift_score:.1f}" if sift_score >= 0 else "",
                "",  # sift_prediction
                "",  # amino_acids
                get_interpretation(vep_score, sift_score),
            ])
            rows_written += 1

    print(f"Wrote {rows_written} benign VEP rows to {OUTPUT_CSV.name}")
    return 0


if __name__ == "__main__":
    exit(main())
