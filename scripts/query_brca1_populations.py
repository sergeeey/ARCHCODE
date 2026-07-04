#!/usr/bin/env python
"""
gnomAD v4 population query для BRCA1 Pathogenic variants.
Быстрый standalone script (не зависит от query_gnomad_populations.py).
"""

import json
import time
import requests
import pandas as pd
from pathlib import Path

GNOMAD_API = "https://gnomad.broadinstitute.org/api"
RATE_LIMIT_DELAY = 3.0  # 3 sec между запросами (conservative)


def query_variant(chrom: str, pos: int, ref: str, alt: str) -> dict:
    """Query gnomAD v4 with population stratification."""
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
          faf95 { popmax }
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
          faf95 { popmax }
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

    try:
        resp = requests.post(GNOMAD_API, json={"query": query}, timeout=30)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}"}

        data = resp.json()
        variant = data.get("data", {}).get("variant")
        if not variant:
            return {"error": "Variant not found"}

        # Prefer genome over exome
        dataset = variant.get("genome") or variant.get("exome")
        if not dataset:
            return {"error": "No gnomAD data"}

        # Extract populations
        populations = dataset.get("populations", [])
        pop_dict = {}
        for p in populations:
            pop_id = p.get("id")
            if pop_id:
                ac = p.get("ac", 0)
                an = p.get("an", 0)
                af = (ac / an) if an > 0 else 0.0
                pop_dict[pop_id.upper()] = af

        # FAF95 popmax
        faf95_data = dataset.get("faf95", {})
        popmax = faf95_data.get("popmax") if faf95_data else None

        return {
            "af": dataset.get("af", 0.0),
            "ac": dataset.get("ac", 0),
            "an": dataset.get("an", 0),
            "popmax": popmax,
            "af_afr": pop_dict.get("AFR", 0.0),
            "af_amr": pop_dict.get("AMR", 0.0),
            "af_eas": pop_dict.get("EAS", 0.0),
            "af_eur": pop_dict.get("NFE", 0.0),  # Non-Finnish European
            "af_sas": pop_dict.get("SAS", 0.0),
            "af_asj": pop_dict.get("ASJ", 0.0),  # Ashkenazi Jewish
            "af_fin": pop_dict.get("FIN", 0.0),
            "af_mid": pop_dict.get("MID", 0.0),
        }

    except Exception as e:
        return {"error": str(e)}


def main():
    input_csv = Path("D:/ДНК/results/brca1_pathogenic_query_input.csv")
    output_csv = Path("D:/ДНК/results/brca1_pathogenic_populations.csv")

    df = pd.read_csv(input_csv)

    print(f"Querying {len(df)} BRCA1 Pathogenic variants...")
    print(f"Rate limit: {RATE_LIMIT_DELAY}s delay\n")

    results = []

    for idx, row in df.iterrows():
        chrom = str(row["chromosome"])
        pos = int(row["position"])
        ref = row["ref"]
        alt = row["alt"]
        clinvar_id = row["clinvar_id"]

        print(f"[{idx+1}/{len(df)}] {clinvar_id}: chr{chrom}:{pos} {ref}>{alt}")

        result = query_variant(chrom, pos, ref, alt)

        if "error" in result:
            print(f"  ❌ FAILED: {result['error']}")
            result_row = {
                "ClinVar_ID": clinvar_id,
                "Position": pos,
                "Ref": ref,
                "Alt": alt,
                "gnomAD_AF": None,
                "AF_AFR": None,
                "AF_AMR": None,
                "AF_EAS": None,
                "AF_EUR": None,
                "AF_SAS": None,
                "AF_ASJ": None,
                "popmax": None,
                "error": result["error"],
            }
        else:
            af = result["af"]
            af_asj = result["af_asj"]
            popmax = result["popmax"] or "N/A"
            print(f"  ✓ AF={af:.6g}, AF_ASJ={af_asj:.6g}, popmax={popmax}")

            result_row = {
                "ClinVar_ID": clinvar_id,
                "Position": pos,
                "Ref": ref,
                "Alt": alt,
                "gnomAD_AF": af,
                "AF_AFR": result["af_afr"],
                "AF_AMR": result["af_amr"],
                "AF_EAS": result["af_eas"],
                "AF_EUR": result["af_eur"],
                "AF_SAS": result["af_sas"],
                "AF_ASJ": af_asj,
                "AF_FIN": result["af_fin"],
                "AF_MID": result["af_mid"],
                "popmax": popmax,
                "error": None,
            }

        results.append(result_row)
        time.sleep(RATE_LIMIT_DELAY)

    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_csv, index=False)

    print(f"\n✅ Saved: {output_csv}")
    print(f"Success: {len(results_df[results_df['error'].isna()])}/{len(results_df)}")


if __name__ == "__main__":
    main()
