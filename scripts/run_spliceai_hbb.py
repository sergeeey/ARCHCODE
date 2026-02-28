#!/usr/bin/env python3
"""
SpliceAI Predictions for HBB Variants via Broad Institute Lookup API

Uses the public SpliceAI Lookup API (no local installation needed).
API: https://spliceailookup-api.broadinstitute.org/

Replaces mock AlphaGenome scores with real splice impact predictions.

Thresholds from Jaganathan et al. 2019 (Cell):
  DOI: 10.1016/j.cell.2018.12.015
  - >0.8:  Very high splice impact
  - 0.5-0.8: High impact
  - 0.2-0.5: Moderate impact
  - <0.2:  Low impact (SpliceAI "blind")

Usage:
  python scripts/run_spliceai_hbb.py --variants data/hbb_real_variants.csv
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import argparse
from pathlib import Path

# Broad Institute SpliceAI Lookup API
SPLICEAI_API_URL = "https://spliceailookup-api.broadinstitute.org/spliceai/"

# Rate limit: be polite, ~1 request per second
REQUEST_DELAY = 1.1


def interpret_score(score: float) -> str:
    """
    Interpret SpliceAI delta score.

    Thresholds from Jaganathan et al. 2019 (Cell):
    DOI: 10.1016/j.cell.2018.12.015
    """
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


def query_spliceai_api(chrom: str, pos: int, ref: str, alt: str,
                       genome: str = "hg38", distance: int = 500) -> dict | None:
    """
    Query SpliceAI Lookup API for a single variant.

    Returns dict with delta scores or None on failure.
    """
    # API expects: /spliceai/?hg=38&distance=500&variant=chr11-5226762-A-T
    chrom_str = f"chr{chrom}" if not str(chrom).startswith("chr") else str(chrom)
    variant_str = f"{chrom_str}-{pos}-{ref}-{alt}"

    params = {
        "hg": "38",
        "distance": str(distance),
        "variant": variant_str,
    }

    try:
        resp = requests.get(SPLICEAI_API_URL, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data
        elif resp.status_code == 404:
            return None
        else:
            print(f"  API error {resp.status_code} for {variant_str}")
            return None
    except requests.exceptions.Timeout:
        print(f"  Timeout for {variant_str}")
        return None
    except Exception as e:
        print(f"  Error for {variant_str}: {e}")
        return None


def parse_spliceai_response(data: dict) -> dict:
    """
    Parse SpliceAI API response into structured scores.

    API returns scores in format:
    {"scores": [{"ALLELE": "T", "SYMBOL": "HBB",
                 "DS_AG": 0.01, "DS_AL": 0.00,
                 "DS_DG": 0.00, "DS_DL": 0.00,
                 "DP_AG": -5, "DP_AL": 2, "DP_DG": -2, "DP_DL": 48}]}
    """
    scores = data.get("scores", [])
    if not scores:
        return {
            "acceptor_gain": 0.0,
            "acceptor_loss": 0.0,
            "donor_gain": 0.0,
            "donor_loss": 0.0,
            "max_delta": 0.0,
            "gene": "",
        }

    # Take first score entry (usually HBB)
    s = scores[0]
    ag = float(s.get("DS_AG", 0))
    al = float(s.get("DS_AL", 0))
    dg = float(s.get("DS_DG", 0))
    dl = float(s.get("DS_DL", 0))

    return {
        "acceptor_gain": ag,
        "acceptor_loss": al,
        "donor_gain": dg,
        "donor_loss": dl,
        "max_delta": max(ag, al, dg, dl),
        "gene": s.get("SYMBOL", ""),
    }


def run_spliceai_api_predictions(variants_file: str, output_file: str,
                                  cache_file: str | None = None) -> pd.DataFrame:
    """
    Run SpliceAI predictions via Broad Institute API.

    Supports caching to avoid re-querying on restart.
    """
    print("Loading variants...")
    df = pd.read_csv(variants_file)
    print(f"Loaded {len(df)} variants from {variants_file}")

    # Load cache if exists
    cache = {}
    cache_path = Path(cache_file) if cache_file else Path(output_file).with_suffix(".cache.json")
    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached results from {cache_path}")

    results = []
    errors = 0
    cached_hits = 0

    total = len(df)
    print(f"\nQuerying SpliceAI Lookup API for {total} variants...")
    print(f"Estimated time: ~{total * REQUEST_DELAY / 60:.1f} minutes")
    print()

    for idx, row in df.iterrows():
        chrom = str(row["chr"])
        pos = int(row["position"])
        ref = str(row["ref"])
        alt = str(row["alt"])
        clinvar_id = str(row.get("clinvar_id", f"var_{idx}"))

        # Cache key
        key = f"{chrom}-{pos}-{ref}-{alt}"

        if key in cache:
            scores = cache[key]
            cached_hits += 1
        else:
            # Query API
            raw = query_spliceai_api(chrom, pos, ref, alt)
            if raw is None:
                scores = {
                    "acceptor_gain": np.nan,
                    "acceptor_loss": np.nan,
                    "donor_gain": np.nan,
                    "donor_loss": np.nan,
                    "max_delta": np.nan,
                    "gene": "",
                }
                errors += 1
            else:
                scores = parse_spliceai_response(raw)
                # Save to cache
                cache[key] = scores

            # Rate limiting
            time.sleep(REQUEST_DELAY)

        results.append({
            "clinvar_id": clinvar_id,
            "chr": chrom,
            "position": pos,
            "ref": ref,
            "alt": alt,
            "spliceai_max_delta": scores["max_delta"],
            "acceptor_gain": scores["acceptor_gain"],
            "acceptor_loss": scores["acceptor_loss"],
            "donor_gain": scores["donor_gain"],
            "donor_loss": scores["donor_loss"],
            "gene": scores.get("gene", ""),
            "interpretation": interpret_score(scores["max_delta"]) if not np.isnan(scores["max_delta"]) else "ERROR",
        })

        # Progress
        done = idx + 1
        if done % 10 == 0 or done == total:
            remaining = (total - done) * REQUEST_DELAY / 60
            print(f"  [{done}/{total}] {done*100/total:.0f}% complete "
                  f"(~{remaining:.1f} min remaining, {errors} errors, {cached_hits} cached)")

        # Save cache every 50 variants
        if done % 50 == 0:
            with open(cache_path, "w") as f:
                json.dump(cache, f, indent=2, default=str)

    # Final cache save
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2, default=str)
    print(f"\nCache saved: {cache_path} ({len(cache)} entries)")

    # Create results DataFrame
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

    # Summary statistics
    valid = results_df["spliceai_max_delta"].notna()
    print(f"\n{'='*60}")
    print(f"SpliceAI Predictions Complete")
    print(f"{'='*60}")
    print(f"Total variants:     {len(results_df)}")
    print(f"Valid predictions:   {valid.sum()}")
    print(f"Errors:             {errors}")
    print(f"Cached hits:        {cached_hits}")
    print()

    if valid.sum() > 0:
        scores = results_df.loc[valid, "spliceai_max_delta"]
        print(f"Score distribution:")
        print(f"  Very High (>0.8): {(scores > 0.8).sum()}")
        print(f"  High (0.5-0.8):   {((scores >= 0.5) & (scores <= 0.8)).sum()}")
        print(f"  Moderate (0.2-0.5): {((scores >= 0.2) & (scores < 0.5)).sum()}")
        print(f"  Low (<0.2):       {(scores < 0.2).sum()}")
        print(f"  Mean score:       {scores.mean():.4f}")
        print(f"  Median score:     {scores.median():.4f}")

    print(f"\nResults saved: {output_file}")
    return results_df


def main():
    parser = argparse.ArgumentParser(
        description="Run SpliceAI predictions on HBB variants via Broad Institute API"
    )
    parser.add_argument("--variants", type=str, required=True,
                        help="Input CSV with columns: clinvar_id, chr, position, ref, alt")
    parser.add_argument("--output", type=str, default="data/hbb_spliceai_results.csv",
                        help="Output CSV file (default: data/hbb_spliceai_results.csv)")
    parser.add_argument("--cache", type=str, default=None,
                        help="Cache file for API results (auto-generated if not set)")

    args = parser.parse_args()

    results = run_spliceai_api_predictions(
        variants_file=args.variants,
        output_file=args.output,
        cache_file=args.cache,
    )

    print(f"\nNext steps:")
    print(f"1. Run ARCHCODE simulation: npx tsx scripts/generate-clinical-atlas.ts --real")
    print(f"2. Merge results: python scripts/create_real_atlas.py")


if __name__ == "__main__":
    main()
