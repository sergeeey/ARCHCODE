#!/usr/bin/env python3
"""
Ensembl VEP Predictions for HBB Variants

Uses the Ensembl REST API to get real variant consequences, SIFT scores,
and splice impact predictions for all HBB ClinVar variants.

API: https://rest.ensembl.org/vep/homo_sapiens/region
Batch mode: up to 200 variants per request.

VEP consequence severity → "sequence-based pathogenicity score":
  - splice_donor/acceptor_variant   → 0.95 (canonical splice site)
  - stop_gained (nonsense)           → 0.90
  - frameshift_variant               → 0.90
  - splice_region_variant            → 0.50
  - missense_variant                 → SIFT-based (0.01-0.99)
  - synonymous_variant               → 0.05
  - intron_variant                   → 0.10
  - upstream/downstream              → 0.15

Usage:
  python scripts/run_vep_predictions.py --variants data/hbb_real_variants.csv
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import argparse
from pathlib import Path

VEP_API_URL = "https://rest.ensembl.org/vep/homo_sapiens/region"
VEP_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

# VEP batch limit
BATCH_SIZE = 200
REQUEST_DELAY = 1.0

# Consequence severity scores (SO term → pathogenicity estimate)
# Based on Ensembl consequence hierarchy:
# https://www.ensembl.org/info/genome/variation/prediction/predicted_data.html
CONSEQUENCE_SCORES = {
    "transcript_ablation": 0.99,
    "splice_acceptor_variant": 0.95,
    "splice_donor_variant": 0.95,
    "stop_gained": 0.90,
    "frameshift_variant": 0.90,
    "stop_lost": 0.85,
    "start_lost": 0.85,
    "transcript_amplification": 0.80,
    "inframe_insertion": 0.60,
    "inframe_deletion": 0.60,
    "missense_variant": 0.50,  # Default; overridden by SIFT if available
    "protein_altering_variant": 0.50,
    "splice_region_variant": 0.50,
    "splice_donor_5th_base_variant": 0.40,
    "splice_donor_region_variant": 0.35,
    "splice_polypyrimidine_tract_variant": 0.30,
    "incomplete_terminal_codon_variant": 0.30,
    "start_retained_variant": 0.15,
    "stop_retained_variant": 0.15,
    "synonymous_variant": 0.05,
    "coding_sequence_variant": 0.20,
    "mature_miRNA_variant": 0.25,
    "5_prime_UTR_variant": 0.20,
    "3_prime_UTR_variant": 0.15,
    "non_coding_transcript_exon_variant": 0.15,
    "intron_variant": 0.10,
    "NMD_transcript_variant": 0.10,
    "non_coding_transcript_variant": 0.10,
    "upstream_gene_variant": 0.15,
    "downstream_gene_variant": 0.10,
    "TFBS_ablation": 0.40,
    "TFBS_amplification": 0.25,
    "TF_binding_site_variant": 0.20,
    "regulatory_region_ablation": 0.35,
    "regulatory_region_amplification": 0.20,
    "feature_elongation": 0.10,
    "regulatory_region_variant": 0.15,
    "feature_truncation": 0.10,
    "intergenic_variant": 0.05,
}


def format_variant_for_vep(chrom: str, pos: int, ref: str, alt: str) -> str:
    """Format variant as VEP input string."""
    # VEP expects: CHROM START . REF ALT . . .
    return f"{chrom} {pos} . {ref} {alt} . . ."


def parse_vep_result(result: dict) -> dict:
    """
    Parse VEP result for a single variant.
    Returns the most severe consequence and associated scores.
    """
    transcript_consequences = result.get("transcript_consequences", [])

    # Filter for HBB gene transcripts only
    hbb_consequences = [
        tc for tc in transcript_consequences
        if tc.get("gene_symbol") == "HBB"
    ]
    if not hbb_consequences:
        hbb_consequences = transcript_consequences

    if not hbb_consequences:
        return {
            "most_severe_consequence": result.get("most_severe_consequence", "unknown"),
            "vep_score": 0.1,
            "sift_score": np.nan,
            "sift_prediction": "",
            "impact": "MODIFIER",
            "amino_acids": "",
            "codons": "",
        }

    # Find the most severe consequence across HBB transcripts
    best_tc = None
    best_severity = -1
    for tc in hbb_consequences:
        terms = tc.get("consequence_terms", [])
        for term in terms:
            severity = CONSEQUENCE_SCORES.get(term, 0.1)
            if severity > best_severity:
                best_severity = severity
                best_tc = tc

    if best_tc is None:
        best_tc = hbb_consequences[0]

    # Get SIFT score if available (for missense)
    sift_score = best_tc.get("sift_score", np.nan)
    sift_prediction = best_tc.get("sift_prediction", "")

    # For missense: use SIFT to refine the score
    # SIFT: lower = more damaging (0=deleterious, 1=tolerated)
    # We invert: vep_score = 1 - sift_score for missense
    most_severe = result.get("most_severe_consequence", "unknown")
    vep_score = best_severity

    if most_severe == "missense_variant" and not np.isnan(sift_score):
        # Combine consequence severity with SIFT prediction
        # SIFT < 0.05 = deleterious → score ~0.7-0.9
        # SIFT > 0.05 = tolerated  → score ~0.3-0.5
        vep_score = 0.4 + 0.5 * (1 - sift_score)

    return {
        "most_severe_consequence": most_severe,
        "vep_score": round(vep_score, 4),
        "sift_score": round(sift_score, 4) if not np.isnan(sift_score) else np.nan,
        "sift_prediction": sift_prediction,
        "impact": best_tc.get("impact", "MODIFIER"),
        "amino_acids": best_tc.get("amino_acids", ""),
        "codons": best_tc.get("codons", ""),
    }


def interpret_vep_score(score: float) -> str:
    """Interpret VEP-based pathogenicity score."""
    if np.isnan(score):
        return "N/A"
    if score >= 0.8:
        return "Very High Impact"
    elif score >= 0.5:
        return "High Impact"
    elif score >= 0.2:
        return "Moderate Impact"
    else:
        return "Low Impact"


def run_vep_batch(variants: list[str], retries: int = 3) -> list[dict]:
    """Query Ensembl VEP API with a batch of variants."""
    data = {"variants": variants, "SIFT": "b"}

    for attempt in range(retries):
        try:
            r = requests.post(
                VEP_API_URL, headers=VEP_HEADERS, json=data, timeout=120
            )
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                # Rate limited
                wait = int(r.headers.get("Retry-After", 5))
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  VEP API error {r.status_code}: {r.text[:200]}")
                time.sleep(2)
        except Exception as e:
            print(f"  Request error (attempt {attempt+1}): {e}")
            time.sleep(3)

    return []


def run_vep_predictions(variants_file: str, output_file: str) -> pd.DataFrame:
    """Run VEP predictions for all variants."""
    print("Loading variants...")
    df = pd.read_csv(variants_file)
    print(f"Loaded {len(df)} variants from {variants_file}")

    # Format variants for VEP
    vep_inputs = []
    for _, row in df.iterrows():
        chrom = str(row["chr"])
        pos = int(row["position"])
        ref = str(row["ref"])
        alt = str(row["alt"])
        vep_inputs.append(format_variant_for_vep(chrom, pos, ref, alt))

    print(f"\nQuerying Ensembl VEP for {len(vep_inputs)} variants...")
    total_batches = (len(vep_inputs) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Batch size: {BATCH_SIZE}, total batches: {total_batches}")

    # Process in batches
    all_results = []
    for batch_idx in range(0, len(vep_inputs), BATCH_SIZE):
        batch = vep_inputs[batch_idx : batch_idx + BATCH_SIZE]
        batch_num = batch_idx // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} variants)...")

        vep_results = run_vep_batch(batch)

        # Match results back to input variants by position
        result_map = {}
        for vr in vep_results:
            key = f"{vr.get('seq_region_name', '')}:{vr.get('start', 0)}"
            result_map[key] = vr

        for i, input_str in enumerate(batch):
            row_idx = batch_idx + i
            row = df.iloc[row_idx]
            key = f"{row['chr']}:{int(row['position'])}"

            if key in result_map:
                parsed = parse_vep_result(result_map[key])
            else:
                parsed = {
                    "most_severe_consequence": "unknown",
                    "vep_score": 0.1,
                    "sift_score": np.nan,
                    "sift_prediction": "",
                    "impact": "MODIFIER",
                    "amino_acids": "",
                    "codons": "",
                }

            all_results.append({
                "clinvar_id": str(row.get("clinvar_id", f"var_{row_idx}")),
                "chr": str(row["chr"]),
                "position": int(row["position"]),
                "ref": str(row["ref"]),
                "alt": str(row["alt"]),
                "category": str(row.get("category", "")),
                "vep_consequence": parsed["most_severe_consequence"],
                "vep_impact": parsed["impact"],
                "vep_score": parsed["vep_score"],
                "sift_score": parsed["sift_score"],
                "sift_prediction": parsed["sift_prediction"],
                "amino_acids": parsed["amino_acids"],
                "interpretation": interpret_vep_score(parsed["vep_score"]),
            })

        time.sleep(REQUEST_DELAY)

    # Save results
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(output_file, index=False)

    # Summary
    valid = results_df["vep_score"].notna()
    print(f"\n{'='*60}")
    print(f"Ensembl VEP Predictions Complete")
    print(f"{'='*60}")
    print(f"Total variants:      {len(results_df)}")
    print(f"Valid predictions:   {valid.sum()}")
    print()

    if valid.sum() > 0:
        scores = results_df.loc[valid, "vep_score"]
        print(f"Score distribution:")
        print(f"  Very High (>0.8):   {(scores > 0.8).sum()}")
        print(f"  High (0.5-0.8):     {((scores >= 0.5) & (scores <= 0.8)).sum()}")
        print(f"  Moderate (0.2-0.5): {((scores >= 0.2) & (scores < 0.5)).sum()}")
        print(f"  Low (<0.2):         {(scores < 0.2).sum()}")
        print(f"  Mean score:         {scores.mean():.4f}")
        print(f"  Median score:       {scores.median():.4f}")

    print(f"\nConsequence breakdown:")
    for csq, cnt in results_df["vep_consequence"].value_counts().items():
        print(f"  {csq}: {cnt}")

    print(f"\nSIFT predictions (missense only):")
    sift_valid = results_df["sift_prediction"].str.len() > 0
    if sift_valid.sum() > 0:
        for pred, cnt in results_df.loc[sift_valid, "sift_prediction"].value_counts().items():
            print(f"  {pred}: {cnt}")

    print(f"\nResults saved: {output_file}")
    return results_df


def main():
    parser = argparse.ArgumentParser(
        description="Run Ensembl VEP predictions on HBB variants"
    )
    parser.add_argument(
        "--variants", type=str, required=True,
        help="Input CSV: clinvar_id, chr, position, ref, alt"
    )
    parser.add_argument(
        "--output", type=str, default="data/hbb_vep_results.csv",
        help="Output CSV (default: data/hbb_vep_results.csv)"
    )

    args = parser.parse_args()

    run_vep_predictions(
        variants_file=args.variants,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
