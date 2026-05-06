"""
cBioPortal API Data Download
Alternative to DepMap/Xena

Downloads TCGA expression + mutation via REST API
Target: BRCA, GBM, COAD (n=150 each)
"""

import requests
import pandas as pd
import numpy as np
from pathlib import Path
import time

# cBioPortal API
API_BASE = "https://www.cbioportal.org/api"
OUTPUT_DIR = Path("../data/cbioportal")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Target studies
STUDIES = {
    "brca": "brca_tcga_pan_can_atlas_2018",
    "gbm": "gbm_tcga_pan_can_atlas_2018",
    "coad": "coadread_tcga_pan_can_atlas_2018",
}

# Core G4 clearance genes
G4_GENES = ["WRN", "BLM", "BRIP1", "DHX36", "PIF1", "RTEL1"]
HR_GENES = ["RAD51", "BRCA1", "BRCA2", "PALB2"]
CONTROL_GENES = ["MYC", "EGFR", "TP53"]

ALL_GENES = G4_GENES + HR_GENES + CONTROL_GENES


def get_study_samples(study_id: str, max_samples: int = 150):
    """Get sample IDs for a study."""
    url = f"{API_BASE}/studies/{study_id}/samples"

    print(f"[{study_id}] Fetching samples...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        samples = response.json()

        sample_ids = [s["sampleId"] for s in samples[:max_samples]]
        print(f"  Found {len(sample_ids)} samples")

        return sample_ids

    except Exception as e:
        print(f"  Error: {e}")
        return []


def get_expression_data(study_id: str, sample_ids: list, genes: list):
    """Get RNA-seq expression for genes."""
    url = f"{API_BASE}/molecular-profiles/{study_id}_rna_seq_v2_mrna/molecular-data/fetch"

    print(f"[{study_id}] Fetching expression ({len(genes)} genes)...")

    payload = {
        "entrezGeneIds": [],  # Will use Hugo symbols
        "sampleIds": sample_ids,
        "projection": "SUMMARY",
    }

    try:
        # cBioPortal uses Hugo symbols, need to convert or use entrez IDs
        # Simplified: fetch all genes, filter later
        response = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=60
        )

        if response.status_code == 404:
            print(f"  Profile not found, trying alternative...")
            # Try mrna profile
            url_alt = f"{API_BASE}/molecular-profiles/{study_id}_mrna/molecular-data/fetch"
            response = requests.post(
                url_alt, json=payload, headers={"Content-Type": "application/json"}, timeout=60
            )

        response.raise_for_status()
        data = response.json()

        print(f"  Downloaded {len(data)} data points")

        # Convert to dataframe
        df = pd.DataFrame(data)

        if df.empty:
            print(f"  Warning: No data returned")
            return None

        # Pivot to genes × samples
        if "hugoGeneSymbol" in df.columns:
            df_pivot = df.pivot_table(
                index="hugoGeneSymbol", columns="sampleId", values="value", aggfunc="first"
            )

            # Filter to target genes
            target_genes = [g for g in genes if g in df_pivot.index]
            df_filtered = df_pivot.loc[target_genes]

            print(f"  Found {len(target_genes)}/{len(genes)} target genes")

            return df_filtered.T  # Return samples × genes
        else:
            print(f"  Warning: Unexpected data format")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None


def quick_test():
    """Quick test: fetch 10 samples from BRCA."""
    print("=" * 60)
    print("cBioPortal API Test")
    print("=" * 60)
    print()

    study_id = "brca_tcga_pan_can_atlas_2018"

    # Get samples
    samples = get_study_samples(study_id, max_samples=10)

    if not samples:
        print("\n[FAIL] Could not fetch samples")
        return False

    # Get expression
    expr_df = get_expression_data(study_id, samples, ["WRN", "BLM", "MYC"])

    if expr_df is None or expr_df.empty:
        print("\n[FAIL] Could not fetch expression")
        return False

    print(f"\n[SUCCESS] Expression shape: {expr_df.shape}")
    print(expr_df.head())

    return True


def download_all_studies():
    """Download expression for all studies."""
    print("\n" + "=" * 60)
    print("Full Download")
    print("=" * 60)
    print()

    all_data = {}

    for cancer_type, study_id in STUDIES.items():
        print(f"\n[{cancer_type.upper()}] {study_id}")

        # Get samples
        samples = get_study_samples(study_id, max_samples=150)

        if not samples:
            continue

        # Get expression
        expr_df = get_expression_data(study_id, samples, ALL_GENES)

        if expr_df is not None:
            # Save
            output_file = OUTPUT_DIR / f"{cancer_type}_expression.csv"
            expr_df.to_csv(output_file)
            print(f"  Saved: {output_file}")

            all_data[cancer_type] = expr_df

        time.sleep(2)  # Rate limit

    # Merge all
    if all_data:
        combined = pd.concat(all_data.values(), keys=all_data.keys())
        combined_file = OUTPUT_DIR / "all_expression.csv"
        combined.to_csv(combined_file)
        print(f"\n[COMBINED] Saved: {combined_file}")
        print(f"  Total: {len(combined)} samples × {combined.shape[1]} genes")


def main():
    print("=" * 60)
    print("cBioPortal Download — Real TCGA Data")
    print("=" * 60)
    print()

    # Quick test first
    success = quick_test()

    if not success:
        print("\n[ERROR] API test failed")
        print("Alternative: Manual download from cbioportal.org")
        return

    # Full download
    download_all_studies()


if __name__ == "__main__":
    main()
