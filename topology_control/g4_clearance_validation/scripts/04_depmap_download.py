"""
DepMap Data Download
Real data alternative to Xena

Downloads:
1. OmicsExpressionProteinCodingGenesTPMLogp1 (expression)
2. OmicsSomaticMutations (mutations)
3. PRISM Repurposing screens (drug response)
4. Model metadata (cell line info)
"""

import requests
import pandas as pd
from pathlib import Path
import time

# DepMap release
DEPMAP_BASE = "https://depmap.org/portal/download/api/download"
RELEASE = "25Q3"  # Update based on current_release.txt

OUTPUT_DIR = Path("../data/depmap")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Core G4 clearance genes (specific)
G4_HELICASES = ["WRN", "BLM", "BRIP1", "DHX36", "PIF1", "RTEL1"]
HR_GENES = ["RAD51", "BRCA1", "BRCA2", "PALB2"]
CONTROL_GENES = ["MYC", "EGFR", "TP53"]

ALL_GENES = G4_HELICASES + HR_GENES + CONTROL_GENES


def download_file(file_name: str, label: str) -> Path:
    """Download DepMap file."""
    url = f"{DEPMAP_BASE}/external?file_name={file_name}"
    output = OUTPUT_DIR / file_name

    if output.exists():
        print(f"[{label}] Exists: {output.name}")
        return output

    print(f"[{label}] Downloading {file_name}...")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size_mb = output.stat().st_size / 1e6
        print(f"  ✓ {size_mb:.1f} MB")
        return output

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("DepMap Download — Real Data")
    print("=" * 60)
    print()

    files = {
        "expression": "OmicsExpressionProteinCodingGenesTPMLogp1.csv",
        "mutations": "OmicsSomaticMutations.csv",
        "prism_primary": "primary-screen-replicate-collapsed-logfold-change.csv",
        "prism_secondary": "secondary-screen-dose-response-curve-parameters.csv",
        "model": "Model.csv",
    }

    for label, filename in files.items():
        download_file(filename, label)
        time.sleep(1)

    print()
    print("=" * 60)
    print("Next: Check for CX-5461 / G4 compounds")
    print("=" * 60)


if __name__ == "__main__":
    main()
