#!/usr/bin/env python3
"""
Spectral Fragility Index (SFI) — Batch Analysis Pipeline

Reads contact matrices from results/contact_matrices/{LOCUS}/,
computes SFI for each WT/MUT pair, saves results to CSV.

Usage:
    python scripts/spectral_fragility_batch.py --locus HBB
    python scripts/spectral_fragility_batch.py --locus HBB --subset pearls
"""

import argparse
import json
import sys
from pathlib import Path
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
from tqdm import tqdm

# Add scripts/ to path for spectral_fragility import
sys.path.insert(0, str(Path(__file__).parent))
from spectral_fragility import (
    compute_spectral_fragility,
    spectral_gap_disruption,
)

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def load_contact_matrix(json_path: Path) -> np.ndarray:
    """Load contact matrix from JSON file"""
    with open(json_path) as f:
        matrix = json.load(f)
    return np.array(matrix, dtype=np.float64)


def process_variant(args):
    """Process single variant (WT/MUT pair) — multiprocessing worker"""
    wt_path, mut_path, k_modes = args

    try:
        # Load matrices
        C_wt = load_contact_matrix(wt_path)
        C_mut = load_contact_matrix(mut_path)

        # Compute SFI
        sfi, components = compute_spectral_fragility(C_wt, C_mut, k=k_modes)

        # Spectral gap disruption
        delta_gap, gap_wt, gap_mut = spectral_gap_disruption(C_wt, C_mut)

        # Extract ClinVar ID from filename
        clinvar_id = wt_path.stem.replace("_wt", "")

        return {
            "ClinVar_ID": clinvar_id,
            "SFI": sfi,
            "eigenvalue_shifts_mean": components["eigenvalue_shifts"].mean(),
            "eigenvalue_shifts_max": components["eigenvalue_shifts"].max(),
            "eigenvector_angles_mean": components["eigenvector_angles"].mean(),
            "eigenvector_angles_max": components["eigenvector_angles"].max(),
            "spectral_gap_disruption": delta_gap,
            "spectral_gap_wt": gap_wt,
            "spectral_gap_mut": gap_mut,
            "matrix_shape": f"{C_wt.shape[0]}x{C_wt.shape[1]}",
        }

    except Exception as e:
        return {"ClinVar_ID": wt_path.stem.replace("_wt", ""), "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Batch SFI analysis on contact matrices")
    parser.add_argument(
        "--locus",
        default="30KB",
        help="Locus identifier (directory name in contact_matrices/)",
    )
    parser.add_argument(
        "--subset",
        choices=["all", "pearls", "pilot"],
        default="all",
        help="Subset to process: all, pearls (n=25), pilot (n=50)",
    )
    parser.add_argument("--k-modes", type=int, default=10, help="Number of eigenmodes to analyze")
    parser.add_argument(
        "--workers", type=int, default=cpu_count(), help="Number of parallel workers"
    )
    parser.add_argument("--output", help="Output CSV path (default: results/sfi_{locus}.csv)")
    args = parser.parse_args()

    # Input directory
    input_dir = RESULTS_DIR / "contact_matrices" / args.locus
    if not input_dir.exists():
        print(f"ERROR: Input directory not found: {input_dir}")
        print(f"Run: npx tsx scripts/generate-unified-atlas.ts --locus {args.locus}")
        return 1

    # Find all WT matrices
    wt_files = sorted(input_dir.glob("*_wt.json"))
    print(f"Found {len(wt_files)} WT matrices in {input_dir}")

    if len(wt_files) == 0:
        print("ERROR: No contact matrices found")
        return 1

    # Subset filtering
    if args.subset == "pearls":
        # Load HBB atlas to filter pearls
        atlas_path = RESULTS_DIR / "HBB_Unified_Atlas.csv"
        if not atlas_path.exists():
            print(f"ERROR: Atlas not found: {atlas_path}")
            return 1

        atlas = pd.read_csv(atlas_path)
        pearl_ids = set(atlas[atlas["Pearl"] == True]["ClinVar_ID"].values)
        wt_files = [f for f in wt_files if f.stem.replace("_wt", "") in pearl_ids]
        print(f"  Filtered to {len(wt_files)} pearls")

    elif args.subset == "pilot":
        # Load HBB atlas
        atlas_path = RESULTS_DIR / "HBB_Unified_Atlas.csv"
        if not atlas_path.exists():
            print(f"ERROR: Atlas not found: {atlas_path}")
            return 1

        atlas = pd.read_csv(atlas_path)

        # All pearls (n=20 for HBB)
        pearls = atlas[atlas["Pearl"] == True]
        pearl_ids = set(pearls["ClinVar_ID"].values)

        # Matched benign controls: same genomic region as pearls
        pearl_min_pos = pearls["Position_GRCh38"].min()
        pearl_max_pos = pearls["Position_GRCh38"].max()

        benign_in_region = atlas[
            (atlas["Label"] == "Benign")
            & (atlas["Position_GRCh38"] >= pearl_min_pos)
            & (atlas["Position_GRCh38"] <= pearl_max_pos)
        ]

        # Take 25 benign (or all if less than 25)
        n_benign = min(25, len(benign_in_region))
        benign_ids = set(benign_in_region["ClinVar_ID"].values[:n_benign])

        pilot_ids = pearl_ids.union(benign_ids)
        wt_files = [f for f in wt_files if f.stem.replace("_wt", "") in pilot_ids]
        print(f"  Filtered to pilot subset: {len(wt_files)} variants")
        print(f"    Pearls: {len(pearl_ids)}")
        print(f"    Benign (region-matched): {len(benign_ids)}")
        print(f"    Region: chr11:{pearl_min_pos}-{pearl_max_pos}")

    # Build (WT, MUT) pairs
    tasks = []
    for wt_path in wt_files:
        mut_path = wt_path.parent / wt_path.name.replace("_wt.json", "_mut.json")
        if not mut_path.exists():
            print(f"WARNING: MUT file missing for {wt_path.name}")
            continue
        tasks.append((wt_path, mut_path, args.k_modes))

    print(f"\nProcessing {len(tasks)} WT/MUT pairs with {args.workers} workers...")
    print(f"Eigenmodes: {args.k_modes}")

    # Parallel processing
    with Pool(processes=args.workers) as pool:
        results = list(
            tqdm(pool.imap(process_variant, tasks), total=len(tasks), desc="Computing SFI")
        )

    # Filter errors
    errors = [r for r in results if "error" in r]
    valid_results = [r for r in results if "error" not in r]

    if errors:
        print(f"\nWARNING: {len(errors)} variants failed:")
        for e in errors[:5]:
            print(f"  {e['ClinVar_ID']}: {e['error']}")

    if not valid_results:
        print("ERROR: No valid results")
        return 1

    # Save to CSV
    df = pd.DataFrame(valid_results)
    output_path = (
        Path(args.output)
        if args.output
        else RESULTS_DIR / f"sfi_{args.locus.lower()}_{args.subset}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\n✅ Results saved: {output_path}")
    print(f"   Valid results: {len(valid_results)}/{len(tasks)}")
    print(f"   SFI range: [{df['SFI'].min():.4f}, {df['SFI'].max():.4f}]")
    print(f"   Mean SFI: {df['SFI'].mean():.4f}")

    return 0


if __name__ == "__main__":
    exit(main())
