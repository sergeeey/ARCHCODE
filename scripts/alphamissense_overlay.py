#!/usr/bin/env python3
"""
AlphaMissense × ARCHCODE Orthogonality Analysis

Queries Ensembl VEP REST API with AlphaMissense=1 for all missense SNVs
across 9 loci (HBB + 8 non-HBB). Compares AlphaMissense pathogenicity
scores with ARCHCODE LSSIM to demonstrate orthogonality.

Key hypothesis: AlphaMissense covers missense (protein structure),
ARCHCODE covers non-coding (chromatin structure) → zero overlap on Class B.

Usage:
  python scripts/alphamissense_overlay.py --all
  python scripts/alphamissense_overlay.py --locus HBB
  python scripts/alphamissense_overlay.py --all --dry-run
"""

import pandas as pd
import numpy as np
import requests
import time
import json
import argparse
import sys
from pathlib import Path
from scipy import stats

# --- API config (same as vep_batch_scoring.py) ---

VEP_API_URL = "https://rest.ensembl.org/vep/homo_sapiens/region"
VEP_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
BATCH_SIZE = 200
REQUEST_DELAY = 0.5

VALID_BASES = {"A", "C", "G", "T"}

LOCUS_CONFIG = {
    "HBB": {"chr": "11", "gene": "HBB", "atlas": "results/HBB_Unified_Atlas.csv"},
    "MLH1": {"chr": "3", "gene": "MLH1", "atlas": "results/MLH1_Unified_Atlas_300kb.csv"},
    "CFTR": {"chr": "7", "gene": "CFTR", "atlas": "results/CFTR_Unified_Atlas_317kb.csv"},
    "TP53": {"chr": "17", "gene": "TP53", "atlas": "results/TP53_Unified_Atlas_300kb.csv"},
    "BRCA1": {"chr": "17", "gene": "BRCA1", "atlas": "results/BRCA1_Unified_Atlas_400kb.csv"},
    "LDLR": {"chr": "19", "gene": "LDLR", "atlas": "results/LDLR_Unified_Atlas_300kb.csv"},
    "SCN5A": {"chr": "3", "gene": "SCN5A", "atlas": "results/SCN5A_Unified_Atlas_400kb.csv"},
    "TERT": {"chr": "5", "gene": "TERT", "atlas": "results/TERT_Unified_Atlas_300kb.csv"},
    "GJB2": {"chr": "13", "gene": "GJB2", "atlas": "results/GJB2_Unified_Atlas_300kb.csv"},
}


def is_queryable_snv(ref: str, alt: str) -> bool:
    return (
        isinstance(ref, str)
        and isinstance(alt, str)
        and len(ref) == 1
        and len(alt) == 1
        and ref in VALID_BASES
        and alt in VALID_BASES
    )


def run_vep_alphamissense_batch(variants: list[str], retries: int = 3) -> list[dict]:
    """Query VEP API with AlphaMissense enabled."""
    data = {
        "variants": variants,
        "SIFT": "b",
        "AlphaMissense": 1,
    }
    for attempt in range(retries):
        try:
            r = requests.post(VEP_API_URL, headers=VEP_HEADERS, json=data, timeout=120)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 5))
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    VEP API error {r.status_code}: {r.text[:200]}")
                time.sleep(2)
        except Exception as e:
            print(f"    Request error (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(3)
    return []


def parse_alphamissense(result: dict, gene_symbol: str) -> dict:
    """Extract AlphaMissense score from VEP result."""
    out = {
        "am_pathogenicity": None,
        "am_class": None,
        "is_missense": False,
        "vep_consequence": None,
    }

    transcript_consequences = result.get("transcript_consequences", [])

    # Filter to target gene
    gene_tcs = [tc for tc in transcript_consequences if tc.get("gene_symbol") == gene_symbol]
    if not gene_tcs:
        gene_tcs = transcript_consequences

    for tc in gene_tcs:
        cons = tc.get("consequence_terms", [])
        if "missense_variant" in cons:
            out["is_missense"] = True
            out["vep_consequence"] = "missense_variant"

            # AlphaMissense: nested dict {"am_pathogenicity": float, "am_class": str}
            am_data = tc.get("alphamissense", {})
            if isinstance(am_data, dict) and am_data.get("am_pathogenicity") is not None:
                out["am_pathogenicity"] = float(am_data["am_pathogenicity"])
                out["am_class"] = am_data.get("am_class")
                return out

    # If no missense found, get most severe consequence
    if gene_tcs:
        for tc in gene_tcs:
            cons = tc.get("consequence_terms", [])
            if cons:
                out["vep_consequence"] = cons[0]
                break

    return out


def process_locus(locus_name: str, project_root: Path, dry_run: bool = False) -> dict:
    """Process one locus: query AlphaMissense for all SNVs."""
    config = LOCUS_CONFIG[locus_name]
    atlas_path = project_root / config["atlas"]

    if not atlas_path.exists():
        print(f"  Atlas not found: {atlas_path}")
        return {}

    df = pd.read_csv(atlas_path)
    chrom = config["chr"]
    gene = config["gene"]

    # Find queryable SNVs
    snv_mask = df.apply(
        lambda r: is_queryable_snv(str(r.get("Ref", "")), str(r.get("Alt", ""))), axis=1
    )
    snv_df = df[snv_mask].copy()

    total = len(df)
    snv_count = len(snv_df)
    print(f"\n{'=' * 60}")
    print(f"  {locus_name}: {total} total variants, {snv_count} queryable SNVs")

    if dry_run:
        batches = (snv_count + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  DRY RUN: would query {batches} batches")
        return {"locus": locus_name, "total": total, "snvs": snv_count}

    # Checkpoint support
    checkpoint_path = project_root / f".am_checkpoint_{locus_name}.json"
    cache = {}
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            cache = json.load(f)
        print(f"  Resuming from checkpoint ({len(cache)} cached)")

    # Build VEP input strings for uncached variants
    queries = []
    for _, row in snv_df.iterrows():
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        key = f"{chrom}:{pos}:{ref}:{alt}"
        if key not in cache:
            vep_str = f"{chrom} {pos} . {ref} {alt} . . ."
            queries.append((key, vep_str))

    print(f"  {len(queries)} variants to query ({len(cache)} cached)")

    # Batch query
    for i in range(0, len(queries), BATCH_SIZE):
        batch = queries[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(queries) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"  Batch {batch_num}/{total_batches}: {len(batch)} variants...")

        vep_strings = [q[1] for q in batch]
        results = run_vep_alphamissense_batch(vep_strings)

        # Map results back by position
        result_map = {}
        for r in results:
            inp = r.get("input", "")
            parts = inp.split()
            if len(parts) >= 5:
                rkey = f"{parts[0]}:{parts[1]}:{parts[3]}:{parts[4]}"
                result_map[rkey] = r

        for key, _ in batch:
            if key in result_map:
                parsed = parse_alphamissense(result_map[key], gene)
                cache[key] = parsed
            else:
                cache[key] = {
                    "am_pathogenicity": None,
                    "am_class": None,
                    "is_missense": False,
                    "vep_consequence": None,
                }

        # Save checkpoint
        with open(checkpoint_path, "w") as f:
            json.dump(cache, f)

        time.sleep(REQUEST_DELAY)

    # Map results back to dataframe
    am_scores = []
    am_classes = []
    is_missense_list = []

    for _, row in df.iterrows():
        ref = str(row.get("Ref", ""))
        alt = str(row.get("Alt", ""))
        if is_queryable_snv(ref, alt):
            pos = int(row["Position_GRCh38"])
            key = f"{chrom}:{pos}:{ref}:{alt}"
            if key in cache:
                am_scores.append(cache[key].get("am_pathogenicity"))
                am_classes.append(cache[key].get("am_class"))
                is_missense_list.append(cache[key].get("is_missense", False))
            else:
                am_scores.append(None)
                am_classes.append(None)
                is_missense_list.append(False)
        else:
            am_scores.append(None)
            am_classes.append(None)
            is_missense_list.append(False)

    df["AM_Score"] = am_scores
    df["AM_Class"] = am_classes
    df["Is_Missense"] = is_missense_list

    # Compute stats
    missense_df = df[df["Is_Missense"] == True]
    has_am = missense_df[missense_df["AM_Score"].notna()]
    non_coding = df[~df["Is_Missense"]]

    lssim_col = "ARCHCODE_LSSIM"
    if lssim_col not in df.columns:
        lssim_col = "LSSIM"

    result = {
        "locus": locus_name,
        "total_variants": total,
        "snv_count": snv_count,
        "missense_count": len(missense_df),
        "am_scored_count": len(has_am),
        "non_coding_count": len(non_coding),
    }

    # Correlation: AM_Score vs LSSIM (for missense with both scores)
    if len(has_am) >= 5 and lssim_col in has_am.columns:
        am_vals = has_am["AM_Score"].values
        lssim_vals = has_am[lssim_col].values
        mask = ~np.isnan(am_vals) & ~np.isnan(lssim_vals)
        if mask.sum() >= 5:
            r, p = stats.spearmanr(am_vals[mask], lssim_vals[mask])
            result["spearman_r"] = round(r, 4)
            result["spearman_p"] = round(p, 6)
            result["n_corr"] = int(mask.sum())

    # AM class distribution
    if len(has_am) > 0:
        class_counts = has_am["AM_Class"].value_counts().to_dict()
        result["am_class_distribution"] = class_counts

    # Key finding: how many pearls are missense with AM score?
    if "Pearl" in df.columns:
        pearls = df[df["Pearl"] == True]
        pearl_missense = pearls[pearls["Is_Missense"] == True]
        pearl_with_am = pearl_missense[pearl_missense["AM_Score"].notna()]
        result["pearl_count"] = len(pearls)
        result["pearl_missense"] = len(pearl_missense)
        result["pearl_with_am"] = len(pearl_with_am)
        if len(pearl_with_am) > 0:
            result["pearl_am_scores"] = pearl_with_am["AM_Score"].tolist()

    # Coverage analysis: what fraction of variants does AM cover?
    result["am_coverage_pct"] = round(len(has_am) / total * 100, 1) if total > 0 else 0
    result["non_coding_pct"] = round(len(non_coding) / total * 100, 1) if total > 0 else 0

    # Cleanup checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    print(
        f"  Results: {len(has_am)} AM-scored missense, {len(non_coding)} non-coding (invisible to AM)"
    )
    if "spearman_r" in result:
        print(
            f"  Correlation AM vs LSSIM: rho={result['spearman_r']}, p={result['spearman_p']} (n={result['n_corr']})"
        )

    return result


def main():
    parser = argparse.ArgumentParser(description="AlphaMissense × ARCHCODE orthogonality analysis")
    parser.add_argument("--locus", type=str, help="Single locus name")
    parser.add_argument("--all", action="store_true", help="Process all 9 loci")
    parser.add_argument("--dry-run", action="store_true", help="Show counts only")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent

    if not args.all and not args.locus:
        print("Specify --locus NAME or --all")
        sys.exit(1)

    loci = list(LOCUS_CONFIG.keys()) if args.all else [args.locus.upper()]
    results = {}

    for locus in loci:
        if locus not in LOCUS_CONFIG:
            print(f"Unknown locus: {locus}")
            continue
        result = process_locus(locus, project_root, dry_run=args.dry_run)
        if result:
            results[locus] = result

    if args.dry_run:
        print("\nDry run complete.")
        return

    # Save results
    output_path = project_root / "analysis" / "alphamissense_archcode_overlay.json"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("ALPHAMISSENSE × ARCHCODE ORTHOGONALITY SUMMARY")
    print("=" * 70)

    total_variants = sum(r.get("total_variants", 0) for r in results.values())
    total_am = sum(r.get("am_scored_count", 0) for r in results.values())
    total_nc = sum(r.get("non_coding_count", 0) for r in results.values())
    total_pearls = sum(r.get("pearl_count", 0) for r in results.values())
    pearl_with_am = sum(r.get("pearl_with_am", 0) for r in results.values())

    print(f"\nTotal variants:           {total_variants}")
    print(f"AlphaMissense scored:     {total_am} ({total_am / total_variants * 100:.1f}%)")
    print(f"Non-coding (AM blind):    {total_nc} ({total_nc / total_variants * 100:.1f}%)")
    print(f"Pearl variants:           {total_pearls}")
    print(f"Pearls with AM score:     {pearl_with_am}")

    print(f"\nPer-locus correlations (AM_Score vs ARCHCODE_LSSIM):")
    print(f"{'Locus':<8} {'N':>6} {'Spearman r':>12} {'p-value':>12} {'AM coverage':>12}")
    print("-" * 52)
    for locus in loci:
        r = results.get(locus, {})
        n = r.get("n_corr", 0)
        rho = r.get("spearman_r", "N/A")
        p = r.get("spearman_p", "N/A")
        cov = r.get("am_coverage_pct", 0)
        if isinstance(rho, float):
            print(f"{locus:<8} {n:>6} {rho:>12.4f} {p:>12.6f} {cov:>11.1f}%")
        else:
            print(f"{locus:<8} {n:>6} {'N/A':>12} {'N/A':>12} {cov:>11.1f}%")

    print(
        f"\nKey finding: AlphaMissense covers {total_am / total_variants * 100:.1f}% of variants."
    )
    print(f"ARCHCODE Class B pearls with AM coverage: {pearl_with_am}/{total_pearls}")
    if total_pearls > 0 and pearl_with_am == 0:
        print(
            "→ CONFIRMED: AlphaMissense is completely blind to Class B architecture-driven variants."
        )


if __name__ == "__main__":
    main()
