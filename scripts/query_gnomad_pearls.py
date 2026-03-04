#!/usr/bin/env python
"""
Query gnomAD v4 allele frequencies for ARCHCODE pearl variants (HBB locus).

Strategy:
1. Try gnomAD GraphQL API (v4 genome + exome)
2. Fallback to Ensembl VEP REST API (includes gnomAD colocated variants)
3. For non-SNV variants (IUPAC codes, indels): mark as NOT_QUERYABLE

Output: gnomad_pearl_af.csv + gnomad_pearl_af_summary.json
"""

import json
import time
import requests
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

RESULTS_DIR = Path("D:/ДНК/results")
ATLAS_PATH = RESULTS_DIR / "HBB_Unified_Atlas_95kb.csv"

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
ENSEMBL_VEP = "https://rest.ensembl.org/vep/homo_sapiens/region"

# ПОЧЕМУ GRCh38: gnomAD v4 uses GRCh38 coordinates natively.
# HBB is on chromosome 11.
CHROM = "11"


def query_gnomad_graphql(pos: int, ref: str, alt: str) -> dict | None:
    """Query gnomAD v4 GraphQL API for a single variant."""
    variant_id = f"{CHROM}-{pos}-{ref}-{alt}"

    # ПОЧЕМУ: gnomAD GraphQL supports both gnomad_r4 dataset.
    # We query both genome and exome for maximum coverage.
    query = """
    {
      variant(dataset: gnomad_r4, variantId: "%s") {
        genome {
          ac
          an
          af
        }
        exome {
          ac
          an
          af
        }
      }
    }
    """ % variant_id

    try:
        resp = requests.post(
            GNOMAD_API,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  gnomAD HTTP {resp.status_code} for {variant_id}")
            return None

        data = resp.json()
        if "errors" in data:
            print(f"  gnomAD errors for {variant_id}: {data['errors'][0].get('message', '')}")
            return None

        variant_data = data.get("data", {}).get("variant")
        if variant_data is None:
            print(f"  gnomAD: variant {variant_id} not found (null response)")
            return {"af": 0.0, "ac": 0, "an": 0, "source": "gnomAD_v4_absent"}

        result = {}

        # Prefer genome data, fallback to exome
        genome = variant_data.get("genome")
        exome = variant_data.get("exome")

        if genome and genome.get("an") and genome["an"] > 0:
            result = {
                "af": genome["af"],
                "ac": genome["ac"],
                "an": genome["an"],
                "source": "gnomAD_v4_genome",
            }
        if exome and exome.get("an") and exome["an"] > 0:
            # If we already have genome data, combine; otherwise use exome
            if result and result.get("an", 0) > 0:
                result["exome_af"] = exome["af"]
                result["exome_ac"] = exome["ac"]
                result["exome_an"] = exome["an"]
            else:
                result = {
                    "af": exome["af"],
                    "ac": exome["ac"],
                    "an": exome["an"],
                    "source": "gnomAD_v4_exome",
                }

        if not result:
            result = {"af": 0.0, "ac": 0, "an": 0, "source": "gnomAD_v4_absent"}

        return result

    except requests.exceptions.Timeout:
        print(f"  gnomAD timeout for {variant_id}")
        return None
    except Exception as e:
        print(f"  gnomAD error for {variant_id}: {e}")
        return None


def query_ensembl_vep(pos: int, ref: str, alt: str) -> dict | None:
    """Fallback: query Ensembl VEP REST API which includes gnomAD frequencies."""
    # ПОЧЕМУ: Ensembl VEP returns colocated_variants which include gnomAD AF.
    # Format: /vep/homo_sapiens/region/11:POS-POS:1/ALT
    region = f"{CHROM}:{pos}-{pos}:1/{alt}"
    url = f"{ENSEMBL_VEP}/{region}"

    try:
        resp = requests.get(
            url,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code != 200:
            print(f"  Ensembl HTTP {resp.status_code} for {pos} {ref}>{alt}")
            return None

        data = resp.json()
        if not data or not isinstance(data, list):
            return None

        for entry in data:
            colocated = entry.get("colocated_variants", [])
            for cv in colocated:
                freqs = cv.get("frequencies", {})
                minor_allele_freq = cv.get("minor_allele_freq")
                gnomad_af = cv.get("gnomad_af")
                gnomade_af = cv.get("gnomade_af")
                gnomadg_af = cv.get("gnomadg_af")

                # Try various gnomAD frequency fields
                if gnomadg_af is not None:
                    return {
                        "af": float(gnomadg_af),
                        "ac": -1,  # Not available from VEP
                        "an": -1,
                        "source": "ensembl_gnomAD_genome",
                    }
                if gnomade_af is not None:
                    return {
                        "af": float(gnomade_af),
                        "ac": -1,
                        "an": -1,
                        "source": "ensembl_gnomAD_exome",
                    }
                if gnomad_af is not None:
                    return {
                        "af": float(gnomad_af),
                        "ac": -1,
                        "an": -1,
                        "source": "ensembl_gnomAD",
                    }

                # Check alt-specific frequency in frequencies dict
                alt_lower = alt.lower()
                if alt_lower in freqs:
                    alt_freq_data = freqs[alt_lower]
                    for key in ["gnomade", "gnomadg", "gnomad"]:
                        if key in alt_freq_data:
                            return {
                                "af": float(alt_freq_data[key]),
                                "ac": -1,
                                "an": -1,
                                "source": f"ensembl_{key}",
                            }

        return {"af": 0.0, "ac": 0, "an": 0, "source": "ensembl_absent"}

    except requests.exceptions.Timeout:
        print(f"  Ensembl timeout for {pos} {ref}>{alt}")
        return None
    except Exception as e:
        print(f"  Ensembl error for {pos} {ref}>{alt}: {e}")
        return None


def is_simple_snv(ref: str, alt: str) -> bool:
    """Check if variant is a simple SNV (single nucleotide, no IUPAC ambiguity)."""
    return len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT"


def main():
    print("=" * 70)
    print("gnomAD Allele Frequency Query for ARCHCODE Pearl Variants (HBB)")
    print("=" * 70)

    # Load atlas and filter pearls
    df = pd.read_csv(ATLAS_PATH)
    pearls = df[df["Pearl"] == True].copy()
    print(f"\nTotal pearl variants: {len(pearls)}")

    results = []

    for idx, row in pearls.iterrows():
        cid = row["ClinVar_ID"]
        pos = int(row["Position_GRCh38"])
        ref = str(row["Ref"])
        alt = str(row["Alt"])
        cat = row["Category"]
        lssim = row["ARCHCODE_LSSIM"]

        print(f"\n[{len(results)+1}/27] {cid}: chr11:{pos} {ref}>{alt} ({cat})")

        # Non-queryable variants
        if not is_simple_snv(ref, alt):
            print(f"  SKIP: not a simple SNV (IUPAC code or indel)")
            results.append({
                "ClinVar_ID": cid,
                "Position": pos,
                "Ref": ref,
                "Alt": alt,
                "Category": cat,
                "LSSIM": lssim,
                "gnomAD_AF": np.nan,
                "gnomAD_AC": np.nan,
                "gnomAD_AN": np.nan,
                "gnomAD_source": "NOT_QUERYABLE",
            })
            continue

        # Strategy 1: gnomAD GraphQL
        result = query_gnomad_graphql(pos, ref, alt)

        # Strategy 2: Ensembl VEP fallback
        if result is None:
            print(f"  Falling back to Ensembl VEP...")
            time.sleep(0.5)  # Rate limiting for Ensembl
            result = query_ensembl_vep(pos, ref, alt)

        if result is None:
            print(f"  FAILED: no data from any source")
            results.append({
                "ClinVar_ID": cid,
                "Position": pos,
                "Ref": ref,
                "Alt": alt,
                "Category": cat,
                "LSSIM": lssim,
                "gnomAD_AF": np.nan,
                "gnomAD_AC": np.nan,
                "gnomAD_AN": np.nan,
                "gnomAD_source": "QUERY_FAILED",
            })
        else:
            af = result.get("af", 0.0)
            ac = result.get("ac", 0)
            an = result.get("an", 0)
            src = result.get("source", "unknown")
            print(f"  OK: AF={af:.6g}, AC={ac}, AN={an} [{src}]")
            results.append({
                "ClinVar_ID": cid,
                "Position": pos,
                "Ref": ref,
                "Alt": alt,
                "Category": cat,
                "LSSIM": lssim,
                "gnomAD_AF": af,
                "gnomAD_AC": ac,
                "gnomAD_AN": an,
                "gnomAD_source": src,
            })

        # Rate limiting between API calls
        time.sleep(0.3)

    # Save results CSV
    results_df = pd.DataFrame(results)
    out_csv = RESULTS_DIR / "gnomad_pearl_af.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\n{'=' * 70}")
    print(f"Saved: {out_csv}")
    print(f"{'=' * 70}")

    # ---- Summary Statistics ----
    print("\n" + "=" * 70)
    print("SUMMARY STATISTICS")
    print("=" * 70)

    queryable = results_df[results_df["gnomAD_source"] != "NOT_QUERYABLE"].copy()
    failed = results_df[results_df["gnomAD_source"] == "QUERY_FAILED"]
    successful = queryable[queryable["gnomAD_source"] != "QUERY_FAILED"]

    print(f"\nTotal pearls: {len(results_df)}")
    print(f"  Queryable SNVs: {len(queryable)}")
    print(f"  Non-queryable (indels/IUPAC): {len(results_df) - len(queryable)}")
    print(f"  Query failed: {len(failed)}")
    print(f"  Successfully queried: {len(successful)}")

    if len(successful) > 0:
        # AF distribution
        absent = successful[successful["gnomAD_AF"] == 0.0]
        ultra_rare = successful[(successful["gnomAD_AF"] > 0) & (successful["gnomAD_AF"] < 0.0001)]
        rare = successful[(successful["gnomAD_AF"] >= 0.0001) & (successful["gnomAD_AF"] < 0.01)]
        common = successful[successful["gnomAD_AF"] >= 0.01]

        print(f"\nAllele Frequency Distribution (of {len(successful)} queried):")
        print(f"  AF = 0 (absent from gnomAD): {len(absent)} ({100*len(absent)/len(successful):.1f}%)")
        print(f"  AF < 0.0001 (ultra-rare):    {len(ultra_rare)} ({100*len(ultra_rare)/len(successful):.1f}%)")
        print(f"  AF 0.0001-0.01 (rare):       {len(rare)} ({100*len(rare)/len(successful):.1f}%)")
        print(f"  AF >= 0.01 (common):          {len(common)} ({100*len(common)/len(successful):.1f}%)")

        afs = successful["gnomAD_AF"].values
        print(f"\n  Mean AF:   {np.mean(afs):.6g}")
        print(f"  Median AF: {np.median(afs):.6g}")
        print(f"  Max AF:    {np.max(afs):.6g}")

    # ---- Comparison with benign variants at same/nearby positions ----
    print("\n" + "-" * 70)
    print("COMPARISON: Pearl vs Benign AF distribution")
    print("-" * 70)

    # Get benign variants from atlas (non-pearl, ClinVar Benign/Likely benign)
    benign_mask = (
        (df["Pearl"] == False)
        & (df["Label"] == "Benign")
        & (df["Ref"].str.len() == 1)
        & (df["Alt"].str.len() == 1)
        & (df["Ref"].isin(["A", "C", "G", "T"]))
        & (df["Alt"].isin(["A", "C", "G", "T"]))
    )
    benign_snvs = df[benign_mask].copy()
    print(f"Benign SNVs available for comparison: {len(benign_snvs)}")

    # Query a sample of benign variants for comparison (up to 20)
    benign_sample = benign_snvs.head(20)
    benign_results = []

    if len(benign_sample) > 0:
        print(f"\nQuerying {len(benign_sample)} benign variants for comparison...")
        for _, row in benign_sample.iterrows():
            pos = int(row["Position_GRCh38"])
            ref = str(row["Ref"])
            alt = str(row["Alt"])
            cid = row["ClinVar_ID"]

            result = query_gnomad_graphql(pos, ref, alt)
            if result is None:
                time.sleep(0.5)
                result = query_ensembl_vep(pos, ref, alt)

            if result is not None:
                benign_results.append({
                    "ClinVar_ID": cid,
                    "Position": pos,
                    "gnomAD_AF": result.get("af", 0.0),
                    "source": result.get("source", "unknown"),
                })
                print(f"  {cid}: AF={result.get('af', 0.0):.6g}")
            else:
                benign_results.append({
                    "ClinVar_ID": cid,
                    "Position": pos,
                    "gnomAD_AF": np.nan,
                    "source": "FAILED",
                })
            time.sleep(0.3)

    # Mann-Whitney test
    mann_whitney_result = None
    if len(successful) > 0 and len(benign_results) > 0:
        pearl_afs = successful["gnomAD_AF"].dropna().values
        benign_afs = np.array([b["gnomAD_AF"] for b in benign_results if not np.isnan(b["gnomAD_AF"])])

        if len(pearl_afs) > 2 and len(benign_afs) > 2:
            stat, pvalue = stats.mannwhitneyu(pearl_afs, benign_afs, alternative="less")
            print(f"\nMann-Whitney U test (pearl AF < benign AF):")
            print(f"  U statistic: {stat:.4f}")
            print(f"  p-value:     {pvalue:.6g}")
            print(f"  Pearl median AF:  {np.median(pearl_afs):.6g}")
            print(f"  Benign median AF: {np.median(benign_afs):.6g}")
            mann_whitney_result = {
                "U_statistic": float(stat),
                "p_value": float(pvalue),
                "pearl_median_af": float(np.median(pearl_afs)),
                "benign_median_af": float(np.median(benign_afs)),
                "pearl_n": int(len(pearl_afs)),
                "benign_n": int(len(benign_afs)),
            }

    # ---- Save summary JSON ----
    summary = {
        "analysis": "gnomAD_allele_frequency_pearl_variants",
        "locus": "HBB (chr11)",
        "dataset": "gnomAD_v4",
        "coordinates": "GRCh38",
        "total_pearls": int(len(results_df)),
        "queryable_snvs": int(len(queryable)),
        "non_queryable": int(len(results_df) - len(queryable)),
        "query_failed": int(len(failed)),
        "successfully_queried": int(len(successful)),
        "af_distribution": {},
        "pearl_af_stats": {},
        "benign_comparison": {},
        "mann_whitney_test": mann_whitney_result,
        "interpretation": "",
    }

    if len(successful) > 0:
        afs = successful["gnomAD_AF"].values
        absent_n = int(len(successful[successful["gnomAD_AF"] == 0.0]))
        ultra_rare_n = int(len(successful[(successful["gnomAD_AF"] > 0) & (successful["gnomAD_AF"] < 0.0001)]))
        rare_n = int(len(successful[(successful["gnomAD_AF"] >= 0.0001) & (successful["gnomAD_AF"] < 0.01)]))
        common_n = int(len(successful[successful["gnomAD_AF"] >= 0.01]))

        summary["af_distribution"] = {
            "absent_AF_0": absent_n,
            "ultra_rare_AF_lt_0.0001": ultra_rare_n,
            "rare_AF_0.0001_to_0.01": rare_n,
            "common_AF_gte_0.01": common_n,
            "pct_absent": round(100 * absent_n / len(successful), 1),
            "pct_ultra_rare_or_absent": round(100 * (absent_n + ultra_rare_n) / len(successful), 1),
        }
        summary["pearl_af_stats"] = {
            "mean": float(np.mean(afs)),
            "median": float(np.median(afs)),
            "max": float(np.max(afs)),
            "min": float(np.min(afs)),
            "std": float(np.std(afs)),
        }

    if len(benign_results) > 0:
        benign_afs_clean = [b["gnomAD_AF"] for b in benign_results if not np.isnan(b["gnomAD_AF"])]
        if benign_afs_clean:
            summary["benign_comparison"] = {
                "n_queried": len(benign_afs_clean),
                "mean_af": float(np.mean(benign_afs_clean)),
                "median_af": float(np.median(benign_afs_clean)),
                "max_af": float(np.max(benign_afs_clean)),
            }

    # Interpretation
    if len(successful) > 0:
        absent_pct = summary["af_distribution"].get("pct_absent", 0)
        ultra_rare_pct = summary["af_distribution"].get("pct_ultra_rare_or_absent", 0)
        interpretation = (
            f"Of {len(successful)} queryable pearl variants, "
            f"{absent_pct}% are absent from gnomAD and "
            f"{ultra_rare_pct}% are absent or ultra-rare (AF<0.0001). "
        )
        if mann_whitney_result and mann_whitney_result["p_value"] < 0.05:
            interpretation += (
                f"Pearl variants have significantly lower AF than benign variants "
                f"(Mann-Whitney p={mann_whitney_result['p_value']:.4g}), "
                f"consistent with strong purifying selection against these "
                f"structurally impactful but sequence-subtle variants."
            )
        elif mann_whitney_result:
            interpretation += (
                f"Mann-Whitney test p={mann_whitney_result['p_value']:.4g} "
                f"(not significant at alpha=0.05)."
            )
        else:
            interpretation += "Insufficient benign comparison data for statistical test."
        summary["interpretation"] = interpretation

    out_json = RESULTS_DIR / "gnomad_pearl_af_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\nSaved summary: {out_json}")
    print(f"\nDone.")


if __name__ == "__main__":
    main()
