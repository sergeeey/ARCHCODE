#!/usr/bin/env python3
"""
Batch download TCGA MAF files (multiple samples per tissue).

Usage:
    python batch_download_tcga.py --tissues COAD BRCA LUAD --samples 20 --output data/batch/
"""

import argparse
import json
import time
from pathlib import Path

import requests
import pandas as pd


def download_batch_tcga(tissue_codes: list[str], samples_per_tissue: int, output_dir: Path) -> None:
    """
    Download multiple MAF files per tissue type.

    Args:
        tissue_codes: List of TCGA tissue codes (e.g., ['COAD', 'BRCA'])
        samples_per_tissue: How many samples to download per tissue
        output_dir: Where to save processed data
    """
    FILES_ENDPOINT = "https://api.gdc.cancer.gov/files"
    DATA_ENDPOINT = "https://api.gdc.cancer.gov/data"

    output_dir.mkdir(parents=True, exist_ok=True)
    all_results = []

    for tissue_code in tissue_codes:
        print(f"\n=== {tissue_code} ===")

        # Query for MAF files
        filters = {
            "op": "and",
            "content": [
                {
                    "op": "in",
                    "content": {
                        "field": "cases.project.project_id",
                        "value": [f"TCGA-{tissue_code}"],
                    },
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.data_type",
                        "value": ["Masked Somatic Mutation"],
                    },
                },
                {"op": "in", "content": {"field": "files.data_format", "value": ["MAF"]}},
            ],
        }

        params = {
            "filters": json.dumps(filters),
            "fields": "file_id,file_name,file_size",
            "format": "JSON",
            "size": str(samples_per_tissue),
        }

        response = requests.get(FILES_ENDPOINT, params=params)
        if response.status_code != 200:
            print(f"  ✗ API error: {response.status_code}")
            continue

        data = response.json()
        hits = data["data"]["hits"]

        if not hits:
            print(f"  ✗ No MAF files found")
            continue

        print(f"  Found {len(hits)} MAF files, downloading {samples_per_tissue}...")

        for i, hit in enumerate(hits[:samples_per_tissue]):
            file_id = hit["file_id"]
            file_name = hit["file_name"]
            file_size = hit["file_size"]

            print(
                f"  [{i+1}/{samples_per_tissue}] {file_name} ({file_size / 1024 / 1024:.1f} MB)...",
                end=" ",
            )

            # Download
            download_response = requests.get(f"{DATA_ENDPOINT}/{file_id}", stream=True)

            if download_response.status_code != 200:
                print(f"✗ Download failed")
                continue

            # Save to temp directory
            raw_dir = output_dir / "raw"
            raw_dir.mkdir(exist_ok=True)
            maf_path = raw_dir / file_name

            with open(maf_path, "wb") as f:
                for chunk in download_response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Parse immediately
            try:
                # Simple parsing (reuse extract_mutation_rates logic)
                import gzip
                from io import StringIO

                if maf_path.suffix == ".gz":
                    opener = gzip.open
                else:
                    opener = open

                with opener(maf_path, "rt") as f:
                    lines = [line for line in f if not line.startswith("#")]

                maf_df = pd.read_csv(StringIO("".join(lines)), sep="\t", low_memory=False)

                # Filter silent mutations
                if "Variant_Classification" in maf_df.columns:
                    maf_df = maf_df[maf_df["Variant_Classification"] != "Silent"]

                # Count mutations per sample
                sample_col = "Tumor_Sample_Barcode"
                if sample_col not in maf_df.columns:
                    alt_cols = [c for c in maf_df.columns if "sample" in c.lower()]
                    if alt_cols:
                        sample_col = alt_cols[0]

                mutation_counts = maf_df[sample_col].value_counts()

                # Usually 1 sample per MAF file
                for sample_id, n_mutations in mutation_counts.items():
                    mutations_per_mb = n_mutations / 30.0  # 30 Mb exome coverage

                    all_results.append(
                        {
                            "tissue": tissue_code,
                            "sample_id": sample_id,
                            "mutations_per_mb": mutations_per_mb,
                            "file_id": file_id,
                        }
                    )

                print(f"✓ {mutations_per_mb:.2f} mut/Mb")

            except Exception as e:
                print(f"✗ Parse error: {e}")
                continue

            # Rate limit (GDC allows ~3 req/sec)
            time.sleep(0.35)

    # Save combined results
    results_df = pd.DataFrame(all_results)
    output_path = output_dir / "batch_mutations.csv"
    results_df.to_csv(output_path, index=False)

    print(f"\n✓ Total samples downloaded: {len(results_df)}")
    print(f"✓ Saved to {output_path}")

    # Summary
    print("\nSummary by tissue:")
    summary = (
        results_df.groupby("tissue")["mutations_per_mb"]
        .agg(["count", "mean", "std", "min", "max"])
        .round(2)
    )
    print(summary)


def main():
    parser = argparse.ArgumentParser(description="Batch download TCGA MAF files")
    parser.add_argument(
        "--tissues",
        nargs="+",
        required=True,
        help="TCGA tissue codes (e.g., COAD BRCA LUAD)",
    )
    parser.add_argument("--samples", type=int, default=20, help="Samples per tissue (default: 20)")
    parser.add_argument("--output", type=Path, required=True, help="Output directory")

    args = parser.parse_args()

    download_batch_tcga(args.tissues, args.samples, args.output)


if __name__ == "__main__":
    main()
