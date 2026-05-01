#!/usr/bin/env python
"""
Query gnomAD v4 with POPULATION STRATIFICATION for ARCHCODE pearls.

Extension of PyPop methodology: meta-analysis across populations (AFR, AMR, EAS, EUR, SAS).

Strategy:
1. Query gnomAD GraphQL API with population-specific frequencies
2. Extract AF for each genetic ancestry group
3. Analyze cross-population constraint consistency
4. Identify false pearls (population-specific benign variants)

Output: gnomad_populations_pearls.csv + gnomad_populations_summary.json
"""

import json
import time
import requests
import pandas as pd
import numpy as np
from pathlib import Path

RESULTS_DIR = Path("D:/ДНК/results")
ATLAS_PATH = RESULTS_DIR / "HBB_Unified_Atlas.csv"

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
CHROM = "11"

# Rate limiting: gnomAD API allows ~2 req/sec, but we got HTTP 429 at 1.0s delay
# Increase to 3.0 sec for retry run (conservative to avoid ban)
RATE_LIMIT_DELAY = 3.0


def query_gnomad_with_populations(pos: int, ref: str, alt: str) -> dict | None:
    """Query gnomAD v4 GraphQL API with population stratification."""
    variant_id = f"{CHROM}-{pos}-{ref}-{alt}"

    # MODIFIED QUERY: added populations block
    # NOTE: 'af' field does NOT exist on VariantPopulation type → compute manually from ac/an
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

    # Retry logic for HTTP 429 (rate limiting)
    max_retries = 3
    retry_delay = 2.0  # start with 2 seconds
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
                    wait_time = retry_delay * (2**attempt)  # exponential backoff
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

            # Success — break retry loop
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

    # Parse response (outside retry loop)
    if resp is None:
        return None

    try:
        data = resp.json()
        if "errors" in data:
            print(f"  gnomAD errors: {data['errors'][0].get('message', '')[:100]}")
            return None

        variant_data = data.get("data", {}).get("variant")
        if variant_data is None:
            # Variant not found → absent from gnomAD
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
                "source": "gnomAD_v4_absent",
            }

        # Prefer genome data, fallback to exome
        genome = variant_data.get("genome")
        exome = variant_data.get("exome")

        dataset = genome if genome and genome.get("an", 0) > 0 else exome
        if not dataset or dataset.get("an", 0) == 0:
            # Present in gnomAD schema but AC=0 across all populations
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
                "source": "gnomAD_v4_absent",
            }

        # Extract overall frequencies
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
        # CRITICAL: API returns ac/an only (no af field) → compute af = ac/an manually
        populations = dataset.get("populations", [])
        pop_dict = {}
        for p in populations:
            pop_id = p.get("id")
            if pop_id:
                ac = p.get("ac", 0)
                an = p.get("an", 0)
                af = (ac / an) if an > 0 else 0.0
                pop_dict[pop_id] = af

        result["af_afr"] = pop_dict.get("afr", 0.0)  # African/African American
        result["af_amr"] = pop_dict.get("amr", 0.0)  # Latino/Admixed American
        result["af_eas"] = pop_dict.get("eas", 0.0)  # East Asian
        result["af_eur"] = pop_dict.get("eur", 0.0)  # European (non-Finnish)
        result["af_sas"] = pop_dict.get("sas", 0.0)  # South Asian

        # Additional populations (optional, not in standard 5)
        result["af_fin"] = pop_dict.get("fin", 0.0)  # Finnish
        result["af_asj"] = pop_dict.get("asj", 0.0)  # Ashkenazi Jewish
        result["af_mid"] = pop_dict.get("mid", 0.0)  # Middle Eastern
        result["af_remaining"] = pop_dict.get("remaining", 0.0)  # Other

        return result

    except Exception as e:
        print(f"  JSON parse error for {variant_id}: {e}")
        return None


def is_simple_snv(ref: str, alt: str) -> bool:
    """Check if variant is a simple SNV."""
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT"


def analyze_cross_population_consistency(df: pd.DataFrame) -> dict:
    """
    Analyze cross-population constraint consistency.

    Returns:
    - strong_evidence: pearls absent in ALL populations (100% cross-pop consistency)
    - weak_evidence: pearls absent in some but present in others (population-specific)
    - false_pearls: pearls present at >1% AF in any population (likely benign)
    """
    # Column names are UPPERCASE in DataFrame (AF_AFR not af_afr)
    pop_cols = ["AF_AFR", "AF_AMR", "AF_EAS", "AF_EUR", "AF_SAS"]

    # Strong evidence: absent in all 5 major populations
    strong = df[(df[pop_cols] == 0.0).all(axis=1)]

    # Weak evidence: absent in ≥3 populations, present in ≤2
    absent_counts = (df[pop_cols] == 0.0).sum(axis=1)
    weak = df[(absent_counts >= 3) & (absent_counts < 5)]

    # False pearls: AF ≥ 0.01 (1%) in ANY population
    false = df[(df[pop_cols] >= 0.01).any(axis=1)]

    # Population-specific enrichment (Fisher exact test would go here)
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
    print("=" * 80)
    print("gnomAD Population Stratification Query — PyPop Meta-Analysis Extension")
    print("=" * 80)

    # Load HBB atlas and filter pearls
    df = pd.read_csv(ATLAS_PATH)
    pearls = df[df["Pearl"] == True].copy()
    print(f"\nTotal pearl variants: {len(pearls)}")

    # Filter to simple SNVs only
    snv_mask = pearls.apply(lambda r: is_simple_snv(str(r["Ref"]), str(r["Alt"])), axis=1)
    pearls_snv = pearls[snv_mask].copy()
    print(f"Queryable SNVs: {len(pearls_snv)}")
    print(f"Non-queryable (indels/IUPAC): {len(pearls) - len(pearls_snv)}")

    # RESUME MODE: only query variants that previously FAILED (HTTP 429)
    RESUME_FROM_FAILED = True
    existing_results_path = RESULTS_DIR / "gnomad_populations_pearls.csv"

    if RESUME_FROM_FAILED and existing_results_path.exists():
        print(f"\n🔄 RESUME MODE: loading previous results from {existing_results_path.name}")
        prev_results = pd.read_csv(existing_results_path)
        failed_ids = set(
            prev_results[prev_results["gnomAD_source"] == "QUERY_FAILED"]["ClinVar_ID"]
        )
        pearls_snv = pearls_snv[pearls_snv["ClinVar_ID"].isin(failed_ids)]
        print(f"Found {len(failed_ids)} previously failed variants to retry")
        print(f"🚀 RETRY RUN: querying {len(pearls_snv)} failed variants\n")
    else:
        print(f"\n🚀 FULL RUN: querying all {len(pearls_snv)} variants\n")

    results = []

    for idx, row in pearls_snv.iterrows():
        cid = row["ClinVar_ID"]
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        cat = row.get("Category", "unknown")
        lssim = row.get("ARCHCODE_LSSIM", -1)

        print(f"\n[{len(results)+1}/{len(pearls_snv)}] {cid}: chr11:{pos} {ref}>{alt}")

        result = query_gnomad_with_populations(pos, ref, alt)

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
            popmax = result.get("popmax")
            faf95 = result.get("faf95_popmax")

            # Population-specific AFs
            af_afr = result["af_afr"]
            af_amr = result["af_amr"]
            af_eas = result["af_eas"]
            af_eur = result["af_eur"]
            af_sas = result["af_sas"]

            print(f"  Joint AF={af:.6g}, AC={ac}, AN={an} [{src}]")
            print(
                f"  AFR={af_afr:.6g} | AMR={af_amr:.6g} | EAS={af_eas:.6g} | EUR={af_eur:.6g} | SAS={af_sas:.6g}"
            )
            if popmax:
                print(f"  Popmax: {popmax} (FAF95={faf95:.6g})" if faf95 else f"  Popmax: {popmax}")

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
                    "AF_AFR": af_afr,
                    "AF_AMR": af_amr,
                    "AF_EAS": af_eas,
                    "AF_EUR": af_eur,
                    "AF_SAS": af_sas,
                    "AF_FIN": result.get("af_fin", 0.0),
                    "AF_ASJ": result.get("af_asj", 0.0),
                    "AF_MID": result.get("af_mid", 0.0),
                    "popmax": popmax,
                    "faf95_popmax": faf95 if faf95 else 0.0,
                    "gnomAD_source": src,
                }
            )

        # Rate limiting
        time.sleep(RATE_LIMIT_DELAY)

    # Save results (merge with previous if RESUME mode)
    results_df = pd.DataFrame(results)

    if RESUME_FROM_FAILED and existing_results_path.exists():
        # Merge new results with old results
        prev_results = pd.read_csv(existing_results_path)
        # Remove old failed entries
        prev_results = prev_results[prev_results["gnomAD_source"] != "QUERY_FAILED"]
        # Append new results
        results_df = pd.concat([prev_results, results_df], ignore_index=True)
        # Sort by position
        results_df = results_df.sort_values("Position").reset_index(drop=True)
        print(
            f"\n📊 Merged {len(prev_results)} previous + {len(results)} new = {len(results_df)} total"
        )

    out_csv = RESULTS_DIR / "gnomad_populations_pearls.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\n{'=' * 80}")
    print(f"Saved: {out_csv}")
    print(f"{'=' * 80}")

    # --- Analysis: Cross-Population Consistency ---
    successful = results_df[results_df["gnomAD_source"].str.contains("gnomAD_v4", na=False)]

    if len(successful) > 0:
        print("\n" + "=" * 80)
        print("CROSS-POPULATION CONSTRAINT ANALYSIS (PyPop Meta-Analysis)")
        print("=" * 80)

        cross_pop = analyze_cross_population_consistency(successful)

        print(
            f"\nStrong evidence (absent in ALL 5 populations): {cross_pop['strong_evidence_n']} ({cross_pop['strong_evidence_pct']}%)"
        )
        print(f"Weak evidence (absent in ≥3/5 populations):   {cross_pop['weak_evidence_n']}")
        print(f"False pearls (AF≥1% in any population):        {cross_pop['false_pearls_n']}")

        print("\nMaximum AF observed per population:")
        for pop, max_af in cross_pop["max_af_per_population"].items():
            print(f"  {pop}: {max_af:.6g}")

        # Save summary
        summary = {
            "analysis": "gnomAD_population_stratification_PyPop_extension",
            "locus": "HBB (chr11)",
            "dataset": "gnomAD_v4",
            "total_pearls_queried": len(successful),
            "cross_population_analysis": cross_pop,
            "interpretation": (
                f"{cross_pop['strong_evidence_pct']}% of pearls show cross-population consistency "
                f"(absent in all 5 major genetic ancestry groups), supporting universal structural "
                f"constraint. {cross_pop['false_pearls_n']} variants present at ≥1% AF in at least "
                f"one population, flagged as potential false pearls (population-specific benign)."
            ),
        }

        out_json = RESULTS_DIR / "gnomad_populations_summary.json"
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\nSaved summary: {out_json}")

    print("\nDone.")


if __name__ == "__main__":
    main()
