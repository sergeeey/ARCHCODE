"""
TCGA Data Download via GDC API
Week 1, Day 1-2

Downloads:
1. Gene expression (RNA-seq FPKM-UQ) for helicase genes
2. Somatic mutation data (MAF files)
3. Clinical data (survival, stage)

Target: GBM, BRCA, COAD (n=150 each)
"""

import requests
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import time

# Configuration
BASE_URL = "https://api.gdc.cancer.gov"
OUTPUT_DIR = Path("../data/tcga_raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Helicase genes + controls
HELICASE_GENES = [
    "WRN",  # Werner syndrome helicase
    "BLM",  # Bloom syndrome helicase
    "BRIP1",  # FANCJ
    "RTEL1",  # Regulator of telomere length
    "PIF1",  # PIF1 helicase
    "RECQL4",  # Additional RecQ helicase
    "RECQL5",  # Additional RecQ helicase
]

CONTROL_GENES = [
    "MYC",  # Oncogene control
    "EGFR",  # RTK control
    "TP53",  # Tumor suppressor
]

ALL_GENES = HELICASE_GENES + CONTROL_GENES

# Cancer types (TCGA project codes)
CANCER_TYPES = {
    "GBM": "TCGA-GBM",  # Glioblastoma
    "BRCA": "TCGA-BRCA",  # Breast cancer
    "COAD": "TCGA-COAD",  # Colon adenocarcinoma
}


def query_gdc_cases(project_id: str, max_samples: int = 150) -> List[str]:
    """
    Query GDC for case UUIDs in a project.

    Args:
        project_id: TCGA project (e.g., "TCGA-GBM")
        max_samples: Maximum number of samples

    Returns:
        List of case UUIDs
    """
    endpoint = f"{BASE_URL}/cases"

    filters = {
        "op": "and",
        "content": [
            {"op": "in", "content": {"field": "project.project_id", "value": [project_id]}},
            {
                "op": "in",
                "content": {
                    "field": "files.data_type",
                    "value": ["Gene Expression Quantification"],
                },
            },
        ],
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "case_id,submitter_id",
        "format": "JSON",
        "size": max_samples,
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()

    data = response.json()
    case_ids = [hit["case_id"] for hit in data["data"]["hits"]]

    print(f"[{project_id}] Found {len(case_ids)} cases")
    return case_ids


def download_expression_data(project_id: str, case_ids: List[str]) -> pd.DataFrame:
    """
    Download gene expression for specified cases.

    Note: GDC API doesn't directly provide gene-level queries.
    This is a placeholder — real implementation would:
    1. Download STAR counts files
    2. Extract target genes
    3. Normalize to TPM/FPKM-UQ

    For Week 1, we'll use pre-computed TCGA PanCancer Atlas data
    from cBioPortal or Xena Browser instead.
    """
    print(f"[{project_id}] Expression download via GDC API requires file-level iteration")
    print(f"[{project_id}] Recommend: UCSC Xena Browser (pre-processed TCGA PanCancer)")

    # Return placeholder
    return pd.DataFrame(
        {
            "case_id": case_ids[:10],  # Placeholder
            "WRN": [0.0] * 10,
            "BLM": [0.0] * 10,
        }
    )


def download_mutation_data(project_id: str, case_ids: List[str]) -> pd.DataFrame:
    """
    Download somatic mutation data (MAF files).

    Calculates mutation burden (mutations/Mb).
    """
    endpoint = f"{BASE_URL}/files"

    filters = {
        "op": "and",
        "content": [
            {
                "op": "in",
                "content": {"field": "cases.case_id", "value": case_ids[:50]},
            },  # Limit for test
            {"op": "in", "content": {"field": "data_type", "value": ["Masked Somatic Mutation"]}},
            {"op": "in", "content": {"field": "data_format", "value": ["MAF"]}},
        ],
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "file_id,file_name,cases.case_id",
        "format": "JSON",
        "size": 100,
    }

    response = requests.get(endpoint, params=params)
    response.raise_for_status()

    data = response.json()
    file_count = len(data["data"]["hits"])

    print(f"[{project_id}] Found {file_count} MAF files (placeholder — not downloading)")

    # Return placeholder
    return pd.DataFrame(
        {
            "case_id": case_ids[:10],
            "mutation_burden": [0.0] * 10,
        }
    )


def main():
    """Main execution."""
    print("=" * 60)
    print("TCGA Download — Week 1, Day 1")
    print("=" * 60)
    print()

    print("Target genes:")
    print(f"  Helicases: {', '.join(HELICASE_GENES)}")
    print(f"  Controls: {', '.join(CONTROL_GENES)}")
    print()

    for cancer_short, project_id in CANCER_TYPES.items():
        print(f"\n[{cancer_short}] Querying {project_id}...")

        try:
            # Get case IDs
            case_ids = query_gdc_cases(project_id, max_samples=150)

            # Placeholder downloads (GDC API too low-level for gene queries)
            # expr_df = download_expression_data(project_id, case_ids)
            # mut_df = download_mutation_data(project_id, case_ids)

            # Save case IDs for next step
            output_file = OUTPUT_DIR / f"{cancer_short}_case_ids.txt"
            with open(output_file, "w") as f:
                f.write("\n".join(case_ids))

            print(f"[{cancer_short}] ✓ Saved {len(case_ids)} case IDs to {output_file}")

            time.sleep(1)  # Rate limit

        except Exception as e:
            print(f"[{cancer_short}] ✗ Error: {e}")

    print()
    print("=" * 60)
    print("RECOMMENDATION:")
    print("=" * 60)
    print("GDC API is file-level (requires downloading GB of BAM/counts files).")
    print()
    print("For Week 1 speed, use pre-processed sources:")
    print("1. UCSC Xena Browser — TCGA PanCancer Atlas (gene expression TPM)")
    print("2. cBioPortal — mutation + CNA data")
    print("3. Firehose pipeline — pre-computed RSEM/FPKM")
    print()
    print("Next script: 01b_download_xena.py (faster alternative)")
    print("=" * 60)


if __name__ == "__main__":
    main()
