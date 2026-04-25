#!/usr/bin/env python3
"""
Download TCGA mutation data (MAF files) for stress biology analysis.

Usage:
    python download_tcga.py --tissue COAD --output data/tcga_mutations.csv

Author: Sergey Boyko
Created: 2026-04-25
"""

import argparse
import sys
from pathlib import Path


def download_tcga_maf(tissue_type: str, output_path: Path) -> None:
    """
    Download TCGA MAF (Mutation Annotation Format) files for given tissue.

    Args:
        tissue_type: TCGA tissue code (e.g., 'COAD' for colon, 'BRCA' for breast)
        output_path: Where to save the processed mutation data

    Returns:
        None. Saves CSV with columns: sample_id, tissue, mutations_per_mb
    """
    import requests
    import json

    # GDC API endpoints
    FILES_ENDPOINT = "https://api.gdc.cancer.gov/files"
    DATA_ENDPOINT = "https://api.gdc.cancer.gov/data"

    # Query for MAF files for this tissue type
    filters = {
        "op": "and",
        "content": [
            {
                "op": "in",
                "content": {"field": "cases.project.project_id", "value": [f"TCGA-{tissue_type}"]},
            },
            {
                "op": "in",
                "content": {"field": "files.data_type", "value": ["Masked Somatic Mutation"]},
            },
            {"op": "in", "content": {"field": "files.data_format", "value": ["MAF"]}},
        ],
    }

    params = {
        "filters": json.dumps(filters),
        "fields": "file_id,file_name,file_size",
        "format": "JSON",
        "size": "100",  # Limit to first 100 files for testing
    }

    print(f"Querying GDC API for {tissue_type} MAF files...")
    response = requests.get(FILES_ENDPOINT, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"GDC API error: {response.status_code} - {response.text}")

    data = response.json()
    hits = data["data"]["hits"]

    if not hits:
        raise ValueError(f"No MAF files found for tissue type {tissue_type}")

    print(f"Found {len(hits)} MAF files. Downloading first file as test...")

    # Download first MAF file
    file_id = hits[0]["file_id"]
    file_name = hits[0]["file_name"]
    file_size = hits[0]["file_size"]

    print(f"  File: {file_name} ({file_size / 1024 / 1024:.1f} MB)")

    download_response = requests.get(f"{DATA_ENDPOINT}/{file_id}", stream=True)

    if download_response.status_code != 200:
        raise RuntimeError(f"Download error: {download_response.status_code}")

    # Save to data/raw/
    raw_dir = output_path.parent.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    maf_path = raw_dir / file_name

    with open(maf_path, "wb") as f:
        for chunk in download_response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"  Saved to {maf_path}")

    # Parse and extract mutation rates
    import subprocess

    print("Extracting mutation rates...")
    subprocess.run(
        [
            "python",
            str(Path(__file__).parent / "extract_mutation_rates.py"),
            "--maf",
            str(maf_path),
            "--output",
            str(output_path),
        ],
        check=True,
    )

    print(f"✓ Complete. Mutation rates saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Download TCGA mutation data")
    parser.add_argument(
        "--tissue", type=str, required=True, help="TCGA tissue code (e.g., COAD, BRCA, LUAD)"
    )
    parser.add_argument("--output", type=Path, required=True, help="Output CSV path")

    args = parser.parse_args()

    print(f"Downloading TCGA data for {args.tissue}...")
    download_tcga_maf(args.tissue, args.output)
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
