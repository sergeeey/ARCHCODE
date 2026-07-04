#!/usr/bin/env python
"""
Query gnomAD v4 with POPULATION STRATIFICATION for ARCHCODE variants.

Generic multi-locus population filter (generalization of HBB-specific script).

Extension of PyPop methodology: meta-analysis across populations (AFR, AMR, EAS, EUR, SAS).

Examples:
    # HBB pearls (boolean filter)
    $ python population_filter.py --atlas results/HBB_Unified_Atlas.csv \\
        --chrom 11 --cohort-column Pearl --cohort-op equals \\
        --cohort-value true --locus-name HBB --out hbb_pearls

    # CFTR structural pathogenic (numeric filter)
    $ python population_filter.py --atlas results/CFTR_Unified_Atlas_317kb.csv \\
        --chrom 7 --cohort-column ARCHCODE_LSSIM --cohort-op less_than \\
        --cohort-value 0.93 --locus-name CFTR --out cftr_low_lssim

    # Dry run (preview without querying)
    $ python population_filter.py [args] --dry-run

Output:
    {out}.csv:  Population data (variant × populations)
    {out}.json: Summary statistics
"""

import argparse
import json
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path

RESULTS_DIR = Path("D:/ДНК/results")
GNOMAD_API = "https://gnomad.broadinstitute.org/api"


class CohortGateBlocked(ValueError):
    """Controlled cohort-gate failure before gnomAD query."""

    def __init__(self, message: str, reason: str, matched_variants: int = 0):
        super().__init__(message)
        self.reason = reason
        self.matched_variants = matched_variants


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Query gnomAD v4 with population stratification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--atlas", required=True, type=Path, help="Path to Unified Atlas CSV")
    parser.add_argument(
        "--chrom", required=True, type=str, help="Chromosome (e.g., '11', '7', '17')"
    )
    parser.add_argument(
        "--cohort-column",
        required=True,
        type=str,
        help="Column for filter (e.g., 'Pearl', 'ARCHCODE_LSSIM')",
    )
    parser.add_argument(
        "--cohort-op",
        required=True,
        choices=["equals", "less_than", "greater_than", "less_equal", "greater_equal"],
        help="Comparison operator",
    )
    parser.add_argument(
        "--cohort-value", required=True, type=str, help="Filter value (e.g., 'true', '0.93')"
    )
    parser.add_argument(
        "--locus-name",
        required=True,
        type=str,
        help="Locus name for metadata (e.g., 'HBB', 'CFTR')",
    )
    parser.add_argument("--out", required=True, type=str, help="Output prefix (e.g., 'hbb_pearls')")
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=3.0,
        help="Delay between requests in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview cohort without querying gnomAD"
    )
    parser.add_argument(
        "--allow-indels",
        action="store_true",
        help="Allow indels (deletions/insertions) — may fail if not supported by gnomAD query",
    )
    parser.add_argument(
        "--skip-common",
        action="store_true",
        help="Skip variants likely benign based on ClinVar significance (Benign/Likely_benign)",
    )
    parser.add_argument(
        "--treat-not-found-as-absent",
        action="store_true",
        help=(
            "Treat gnomAD 'Variant not found' GraphQL errors as not observed. "
            "Use only after coordinate/build sanity checks."
        ),
    )

    return parser.parse_args()


def apply_cohort_filter(df: pd.DataFrame, args) -> pd.DataFrame:
    """Apply cohort filter based on CLI arguments."""

    # Validate column exists
    if args.cohort_column not in df.columns:
        raise ValueError(
            f"Column '{args.cohort_column}' not found in atlas.\n" f"Available: {list(df.columns)}"
        )

    # Parse value based on column dtype
    col_dtype = df[args.cohort_column].dtype

    if col_dtype == bool or args.cohort_value.lower() in ["true", "false"]:
        value = args.cohort_value.lower() == "true"
    elif col_dtype in [np.float64, np.float32]:
        value = float(args.cohort_value)
    elif col_dtype in [np.int64, np.int32]:
        value = int(args.cohort_value)
    else:
        value = args.cohort_value  # String comparison

    # Apply operator
    if args.cohort_op == "equals":
        mask = df[args.cohort_column] == value
    elif args.cohort_op == "less_than":
        mask = df[args.cohort_column] < value
    elif args.cohort_op == "greater_than":
        mask = df[args.cohort_column] > value
    elif args.cohort_op == "less_equal":
        mask = df[args.cohort_column] <= value
    elif args.cohort_op == "greater_equal":
        mask = df[args.cohort_column] >= value
    else:
        raise ValueError(f"Unknown operator: {args.cohort_op}")

    filtered = df[mask].copy()

    print(f"Cohort filter: {args.cohort_column} {args.cohort_op} {value}")
    if len(df) == 0:
        print("Result: 0/0 variants (NA%)")
        raise CohortGateBlocked(
            f"Cohort gate blocked: input atlas contains 0 rows.\n"
            f"Check: {args.atlas}",
            reason="input_atlas_zero_rows",
            matched_variants=0,
        )

    print(f"Result: {len(filtered)}/{len(df)} variants ({100*len(filtered)/len(df):.1f}%)")

    if len(filtered) == 0:
        raise CohortGateBlocked(
            f"Cohort gate blocked: filter produced 0 variants.\n"
            f"Check: {args.cohort_column} {args.cohort_op} {args.cohort_value}",
            reason="cohort_filter_zero_rows",
            matched_variants=0,
        )

    return filtered


def write_blocked_gate_summary(
    args,
    df: pd.DataFrame,
    error: CohortGateBlocked,
    mode: str,
) -> tuple[Path, Path]:
    """Write deterministic artifacts for a blocked cohort gate."""
    out_csv = RESULTS_DIR / f"{args.out}.csv"
    out_json = RESULTS_DIR / f"{args.out}.json"

    # Preserve the atlas schema where possible so downstream tooling can read
    # an empty result table without special-casing missing files.
    df.head(0).to_csv(out_csv, index=False)

    summary = {
        "analysis": "gnomAD_population_stratification",
        "mode": mode,
        "status": "COHORT_GATE_BLOCKED",
        "exit_code": 2,
        "locus": f"{args.locus_name} (chr{args.chrom})",
        "atlas_file": str(args.atlas),
        "total_variants_in_atlas": int(len(df)),
        "cohort_filter": {
            "column": args.cohort_column,
            "operator": args.cohort_op,
            "value": args.cohort_value,
            "matched_variants": int(error.matched_variants),
        },
        "blocker": {
            "reason": error.reason,
            "message": str(error),
        },
        "dataset": "gnomAD_v4",
        "query_status": {
            "successful_gnomad_rows": 0,
            "query_failed_rows": 0,
            "source_counts": {},
        },
        "live_query_allowed": False,
        "interpretation_note": (
            "No gnomAD query was run because the cohort gate was empty. "
            "This is a controlled gate failure, not population evidence."
        ),
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    return out_csv, out_json


def absent_result(source: str) -> dict:
    """Return a normalized not-observed result."""
    return {
        "af": 0.0,
        "ac": 0,
        "an": 0,
        "af_afr": 0.0,
        "af_amr": 0.0,
        "af_eas": 0.0,
        "af_eur": 0.0,
        "af_sas": 0.0,
        "popmax": None,
        "faf95_popmax": None,
        "source": source,
    }


def query_gnomad_with_populations(
    chrom: str,
    pos: int,
    ref: str,
    alt: str,
    rate_limit: float,
    treat_not_found_as_absent: bool = False,
) -> dict | None:
    """Query gnomAD v4 GraphQL API with population stratification."""
    variant_id = f"{chrom}-{pos}-{ref}-{alt}"

    query = (
        """
    {
      variant(dataset: gnomad_r4, variantId: "%s") {
        variant_id
        genome {
          ac
          an
          af
          faf95 {
            popmax
            popmax_population
          }
          populations {
            id
            ac
            an
          }
        }
        exome {
          ac
          an
          af
          faf95 {
            popmax
            popmax_population
          }
          populations {
            id
            ac
            an
          }
        }
      }
    }
    """
        % variant_id
    )

    # Retry logic for HTTP 429
    max_retries = 3
    retry_delay = 2.0
    resp = None

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                GNOMAD_API,
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2**attempt)
                    print(
                        f"  Rate limited (429), retry {attempt+1}/{max_retries} after {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  gnomAD HTTP 429 for {variant_id} (max retries exceeded)")
                    return None

            if resp.status_code != 200:
                print(f"  gnomAD HTTP {resp.status_code} for {variant_id}")
                return None

            break

        except requests.exceptions.Timeout:
            print(f"  Timeout for {variant_id}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None
        except Exception as e:
            print(f"  Error for {variant_id}: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return None

    if resp is None:
        return None

    try:
        data = resp.json()
        if "errors" in data:
            message = data["errors"][0].get("message", "")
            print(f"  gnomAD errors: {message[:100]}")
            if treat_not_found_as_absent and "Variant not found" in message:
                return absent_result("gnomAD_v4_not_observed_graphql")
            return None

        variant_data = data.get("data", {}).get("variant")
        if variant_data is None:
            return absent_result("gnomAD_v4_absent")

        genome = variant_data.get("genome")
        exome = variant_data.get("exome")

        dataset = genome if genome and genome.get("an", 0) > 0 else exome
        if not dataset or dataset.get("an", 0) == 0:
            return absent_result("gnomAD_v4_absent")

        faf95_data = dataset.get("faf95", {})
        result = {
            "af": dataset.get("af", 0.0),
            "ac": dataset.get("ac", 0),
            "an": dataset.get("an", 0),
            "popmax": faf95_data.get("popmax_population") if faf95_data else None,
            "faf95_popmax": faf95_data.get("popmax") if faf95_data else None,
            "source": "gnomAD_v4_genome" if dataset == genome else "gnomAD_v4_exome",
        }

        # Extract population-specific frequencies
        populations = dataset.get("populations", [])
        pop_dict = {}
        for p in populations:
            pop_id = p.get("id")
            if pop_id:
                ac = p.get("ac", 0)
                an = p.get("an", 0)
                af = (ac / an) if an > 0 else 0.0
                pop_dict[pop_id] = af

        result["af_afr"] = pop_dict.get("afr", 0.0)
        result["af_amr"] = pop_dict.get("amr", 0.0)
        result["af_eas"] = pop_dict.get("eas", 0.0)
        result["af_eur"] = pop_dict.get("eur", 0.0)
        result["af_sas"] = pop_dict.get("sas", 0.0)
        result["af_fin"] = pop_dict.get("fin", 0.0)
        result["af_asj"] = pop_dict.get("asj", 0.0)
        result["af_mid"] = pop_dict.get("mid", 0.0)
        result["af_remaining"] = pop_dict.get("remaining", 0.0)

        return result

    except Exception as e:
        print(f"  JSON parse error for {variant_id}: {e}")
        return None


def is_simple_snv(ref: str, alt: str) -> bool:
    """Check if variant is a simple SNV."""
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT" and ref != alt


def analyze_cross_population_consistency(df: pd.DataFrame) -> dict:
    """Analyze cross-population constraint consistency."""
    pop_cols = ["AF_AFR", "AF_AMR", "AF_EAS", "AF_EUR", "AF_SAS"]

    strong = df[(df[pop_cols] == 0.0).all(axis=1)]
    absent_counts = (df[pop_cols] == 0.0).sum(axis=1)
    weak = df[(absent_counts >= 3) & (absent_counts < 5)]
    false = df[(df[pop_cols] >= 0.01).any(axis=1)]

    max_af_per_pop = df[pop_cols].max()

    return {
        "strong_evidence_n": len(strong),
        "weak_evidence_n": len(weak),
        "false_pearls_n": len(false),
        "strong_evidence_pct": round(100 * len(strong) / len(df), 1) if len(df) > 0 else 0,
        "max_af_per_population": {
            "AFR": float(max_af_per_pop["AF_AFR"]),
            "AMR": float(max_af_per_pop["AF_AMR"]),
            "EAS": float(max_af_per_pop["AF_EAS"]),
            "EUR": float(max_af_per_pop["AF_EUR"]),
            "SAS": float(max_af_per_pop["AF_SAS"]),
        },
    }


def main():
    args = parse_args()

    print("=" * 80)
    print("gnomAD Population Stratification Query — Generic Multi-Locus Filter")
    print("=" * 80)
    print(f"\nLocus: {args.locus_name} (chr{args.chrom})")
    print(f"Atlas: {args.atlas}")

    # Load atlas
    if not args.atlas.exists():
        raise FileNotFoundError(f"Atlas file not found: {args.atlas}")

    df = pd.read_csv(args.atlas)
    print(f"Total variants in atlas: {len(df)}")

    # Apply cohort filter
    try:
        cohort = apply_cohort_filter(df, args)
    except CohortGateBlocked as exc:
        mode = "dry_run_blocked" if args.dry_run else "live_blocked_before_query"
        out_csv, out_json = write_blocked_gate_summary(args, df, exc, mode)
        print("\nCOHORT GATE BLOCKED")
        print(str(exc))
        print(f"Saved empty result table: {out_csv}")
        print(f"Saved blocked-gate summary: {out_json}")
        raise SystemExit(2)

    # Dry run mode — preview only
    if args.dry_run:
        print(f"\n{'='*80}")
        print("DRY RUN MODE — Preview Only")
        print(f"{'='*80}")
        print(f"\nFirst 5 cohort variants:")
        display_cols = ["ClinVar_ID", "Position_GRCh38", args.cohort_column]
        if "Category" in cohort.columns:
            display_cols.append("Category")
        print(cohort[display_cols].head().to_string(index=False))
        print(f"\nTo proceed: remove --dry-run flag")
        print(f"Expected runtime: ~{len(cohort) * args.rate_limit / 60:.1f} minutes")
        return

    # Filter to simple SNVs (unless --allow-indels)
    if args.allow_indels:
        cohort_snv = cohort.copy()
        print(f"\nQueryable variants (SNVs + indels): {len(cohort_snv)}")
    else:
        snv_mask = cohort.apply(lambda r: is_simple_snv(str(r["Ref"]), str(r["Alt"])), axis=1)
        cohort_snv = cohort[snv_mask].copy()
        print(f"\nQueryable SNVs: {len(cohort_snv)}")
        print(f"Non-queryable (indels): {len(cohort) - len(cohort_snv)}")
        if len(cohort_snv) == 0:
            print("\n⚠️  All variants filtered out (indels only).")
            print("   Try: add --allow-indels flag (WARNING: may fail on gnomAD query)")
            return

    # Skip common variants (Benign/Likely_benign from ClinVar)
    if args.skip_common and "ClinVar_Significance" in cohort_snv.columns:
        before = len(cohort_snv)
        common_keywords = ["Benign", "Likely_benign", "benign"]
        cohort_snv = cohort_snv[
            ~cohort_snv["ClinVar_Significance"].str.contains(
                "|".join(common_keywords), case=False, na=False
            )
        ]
        print(f"Filtered out {before - len(cohort_snv)} common variants (Benign/Likely_benign)")
        if len(cohort_snv) == 0:
            print("\n⚠️  All variants filtered out (all were Benign).")
            return

    print(f"\n{'='*80}")
    print(f"Starting gnomAD queries (rate limit: {args.rate_limit}s/request)")
    print(f"{'='*80}\n")

    results = []

    for idx, row in cohort_snv.iterrows():
        cid = row["ClinVar_ID"]
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        cat = row.get("Category", "unknown")
        lssim = row.get("ARCHCODE_LSSIM", -1)

        print(f"[{len(results)+1}/{len(cohort_snv)}] {cid}: chr{args.chrom}:{pos} {ref}>{alt}")

        result = query_gnomad_with_populations(
            args.chrom,
            pos,
            ref,
            alt,
            args.rate_limit,
            treat_not_found_as_absent=args.treat_not_found_as_absent,
        )

        if result is None:
            print(f"  FAILED: no data")
            results.append(
                {
                    "ClinVar_ID": cid,
                    "Position": pos,
                    "Ref": ref,
                    "Alt": alt,
                    "Category": cat,
                    "LSSIM": lssim,
                    "gnomAD_AF": np.nan,
                    "gnomAD_AC": np.nan,
                    "gnomAD_AN": np.nan,
                    "AF_AFR": np.nan,
                    "AF_AMR": np.nan,
                    "AF_EAS": np.nan,
                    "AF_EUR": np.nan,
                    "AF_SAS": np.nan,
                    "popmax": None,
                    "faf95_popmax": np.nan,
                    "gnomAD_source": "QUERY_FAILED",
                }
            )
        else:
            af = result["af"]
            ac = result["ac"]
            an = result["an"]
            src = result["source"]

            print(f"  Joint AF={af:.6g}, AC={ac}, AN={an} [{src}]")
            print(
                f"  AFR={result['af_afr']:.6g} | AMR={result['af_amr']:.6g} | "
                f"EAS={result['af_eas']:.6g} | EUR={result['af_eur']:.6g} | SAS={result['af_sas']:.6g}"
            )

            results.append(
                {
                    "ClinVar_ID": cid,
                    "Position": pos,
                    "Ref": ref,
                    "Alt": alt,
                    "Category": cat,
                    "LSSIM": lssim,
                    "gnomAD_AF": af,
                    "gnomAD_AC": ac,
                    "gnomAD_AN": an,
                    "AF_AFR": result["af_afr"],
                    "AF_AMR": result["af_amr"],
                    "AF_EAS": result["af_eas"],
                    "AF_EUR": result["af_eur"],
                    "AF_SAS": result["af_sas"],
                    "AF_FIN": result.get("af_fin", 0.0),
                    "AF_ASJ": result.get("af_asj", 0.0),
                    "AF_MID": result.get("af_mid", 0.0),
                    "popmax": result.get("popmax"),
                    "faf95_popmax": result.get("faf95_popmax", 0.0),
                    "gnomAD_source": src,
                }
            )

        time.sleep(args.rate_limit)

    # Save results
    results_df = pd.DataFrame(results)
    out_csv = RESULTS_DIR / f"{args.out}.csv"
    results_df.to_csv(out_csv, index=False)

    print(f"\n{'='*80}")
    print(f"Saved: {out_csv}")
    print(f"{'='*80}")

    # Analysis
    successful = results_df[results_df["gnomAD_source"].str.contains("gnomAD_v4", na=False)]

    query_status = {
        "successful_gnomad_rows": int(len(successful)),
        "query_failed_rows": int((results_df["gnomAD_source"] == "QUERY_FAILED").sum()),
        "source_counts": results_df["gnomAD_source"].value_counts(dropna=False).to_dict(),
    }

    summary = {
        "analysis": "gnomAD_population_stratification",
        "locus": f"{args.locus_name} (chr{args.chrom})",
        "atlas_file": str(args.atlas),
        "cohort_filter": {
            "column": args.cohort_column,
            "operator": args.cohort_op,
            "value": args.cohort_value,
            "matched_variants": len(cohort),
        },
        "dataset": "gnomAD_v4",
        "total_rows_written": len(results_df),
        "query_status": query_status,
        "interpretation_note": (
            "QUERY_FAILED rows are technical failures, not evidence of absence. "
            "Rows marked gnomAD_v4_absent or gnomAD_v4_not_observed_graphql are "
            "not-observed query results and still require coordinate/build sanity checks."
        ),
    }

    if len(successful) > 0:
        print(f"\n{'='*80}")
        print("CROSS-POPULATION CONSTRAINT ANALYSIS")
        print(f"{'='*80}")

        cross_pop = analyze_cross_population_consistency(successful)

        print(
            f"\nStrong evidence (absent in ALL 5 populations): {cross_pop['strong_evidence_n']} "
            f"({cross_pop['strong_evidence_pct']}%)"
        )
        print(f"Weak evidence (absent in ≥3/5 populations):   {cross_pop['weak_evidence_n']}")
        print(f"False pearls (AF≥1% in any population):        {cross_pop['false_pearls_n']}")

        print("\nMaximum AF per population:")
        for pop, max_af in cross_pop["max_af_per_population"].items():
            print(f"  {pop}: {max_af:.6g}")

        summary["total_queried"] = len(successful)
        summary["cross_population_analysis"] = cross_pop

    out_json = RESULTS_DIR / f"{args.out}.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nSaved summary: {out_json}")

    print("\nDone.")


if __name__ == "__main__":
    main()
