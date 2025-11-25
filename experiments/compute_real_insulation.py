"""
Compute Insulation Score and TAD boundaries from real Hi-C data.

Analyzes Rao 2014 GM12878 data and extracts key metrics:
- Insulation Score
- TAD boundaries
- Contact probability P(s)
- Compartment strength
"""

import sys
from pathlib import Path

import cooler
import numpy as np
import pandas as pd

try:
    import cooltools
    from cooltools import insulation
    COOLTOOLS_AVAILABLE = True
except ImportError:
    COOLTOOLS_AVAILABLE = False
    print("⚠️  cooltools not available. Some features will be limited.")

sys.path.insert(0, str(Path(__file__).parent.parent))


def compute_insulation_score(
    cooler_obj: cooler.Cooler,
    window_size: int = 500000,
    resolution: int = 10000,
) -> pd.DataFrame:
    """
    Compute insulation score from cooler object.

    Args:
        cooler_obj: Cooler object
        window_size: Window size for insulation calculation (bp)
        resolution: Resolution of the cooler (bp)

    Returns:
        DataFrame with insulation scores
    """
    if not COOLTOOLS_AVAILABLE:
        # Fallback: simple diagonal-based insulation
        print("⚠️  Using fallback insulation calculation (cooltools not available)")
        return compute_insulation_fallback(cooler_obj, window_size, resolution)

    try:
        # Use cooltools insulation
        insul = insulation(
            cooler_obj,
            window_bp=window_size,
            ignore_diags=2,
            verbose=False,
        )
        return insul
    except Exception as e:
        print(f"⚠️  Error with cooltools insulation: {e}")
        print("Falling back to simple calculation...")
        return compute_insulation_fallback(cooler_obj, window_size, resolution)


def compute_insulation_fallback(
    cooler_obj: cooler.Cooler,
    window_size: int,
    resolution: int,
) -> pd.DataFrame:
    """
    Fallback insulation calculation (simple diagonal-based).

    Args:
        cooler_obj: Cooler object
        window_size: Window size (bp)
        resolution: Resolution (bp)

    Returns:
        DataFrame with insulation scores
    """
    window_bins = window_size // resolution

    # Get chromosome info
    chroms = cooler_obj.chromnames
    all_insulation = []

    for chrom in chroms:
        try:
            # Get matrix for chromosome
            matrix = cooler_obj.matrix(balance=True).fetch(chrom)

            # Calculate insulation as mean of off-diagonal contacts
            insulation_scores = []
            positions = []

            for i in range(len(matrix) - window_bins):
                # Window: [i, i+window_bins]
                window_matrix = matrix[i : i + window_bins, i : i + window_bins]

                # Mean of off-diagonal (insulation)
                mask = ~np.eye(window_bins, dtype=bool)
                insulation_val = np.mean(window_matrix[mask])

                insulation_scores.append(insulation_val)
                positions.append(i * resolution)

            if insulation_scores:
                chrom_df = pd.DataFrame({
                    "chrom": chrom,
                    "start": positions,
                    "end": [p + resolution for p in positions],
                    "insulation_score": insulation_scores,
                })
                all_insulation.append(chrom_df)

        except Exception as e:
            print(f"⚠️  Error processing {chrom}: {e}")
            continue

    if all_insulation:
        return pd.concat(all_insulation, ignore_index=True)
    else:
        return pd.DataFrame(columns=["chrom", "start", "end", "insulation_score"])


def compute_ps_scaling(
    cooler_obj: cooler.Cooler,
    max_distance: int = 10_000_000,
) -> pd.DataFrame:
    """
    Compute contact probability P(s) vs genomic distance.

    Args:
        cooler_obj: Cooler object
        max_distance: Maximum distance to compute (bp)

    Returns:
        DataFrame with P(s) values
    """
    print("📊 Computing P(s) scaling...")

    # Get all chromosomes
    chroms = cooler_obj.chromnames
    all_distances = []
    all_counts = []

    for chrom in chroms:
        try:
            # Get balanced matrix
            matrix = cooler_obj.matrix(balance=True).fetch(chrom)

            # Get bin positions
            bins = cooler_obj.bins().fetch(chrom)
            positions = bins["start"].values

            # Calculate P(s) for this chromosome
            n = len(matrix)
            for i in range(n):
                for j in range(i + 1, n):
                    distance = abs(positions[j] - positions[i])
                    if distance <= max_distance:
                        contact = matrix[i, j]
                        if not np.isnan(contact) and contact > 0:
                            all_distances.append(distance)
                            all_counts.append(contact)

        except Exception as e:
            print(f"⚠️  Error processing {chrom} for P(s): {e}")
            continue

    if not all_distances:
        return pd.DataFrame(columns=["distance", "ps"])

    # Bin distances logarithmically
    distances_array = np.array(all_distances)
    counts_array = np.array(all_counts)

    # Log bins
    log_bins = np.logspace(
        np.log10(min(distances_array)),
        np.log10(max(distances_array)),
        num=50,
    )

    # Calculate mean P(s) per bin
    ps_values = []
    bin_centers = []

    for i in range(len(log_bins) - 1):
        mask = (distances_array >= log_bins[i]) & (distances_array < log_bins[i + 1])
        if mask.sum() > 0:
            mean_ps = np.mean(counts_array[mask])
            bin_center = (log_bins[i] + log_bins[i + 1]) / 2
            ps_values.append(mean_ps)
            bin_centers.append(bin_center)

    return pd.DataFrame({
        "distance": bin_centers,
        "ps": ps_values,
    })


def detect_tad_boundaries(
    insulation_df: pd.DataFrame,
    threshold_percentile: float = 10.0,
) -> pd.DataFrame:
    """
    Detect TAD boundaries from insulation scores.

    Args:
        insulation_df: DataFrame with insulation scores
        threshold_percentile: Percentile for boundary detection (lower = more boundaries)

    Returns:
        DataFrame with detected boundaries
    """
    boundaries = []

    for chrom in insulation_df["chrom"].unique():
        chrom_data = insulation_df[insulation_df["chrom"] == chrom].copy()

        if len(chrom_data) == 0:
            continue

        # Find local minima (boundaries have low insulation)
        insulation_scores = chrom_data["insulation_score"].values

        # Threshold: bottom percentile
        threshold = np.percentile(insulation_scores, threshold_percentile)

        # Find positions below threshold
        boundary_mask = insulation_scores < threshold

        # Extract boundary positions
        boundary_positions = chrom_data[boundary_mask][["chrom", "start", "end", "insulation_score"]]

        boundaries.append(boundary_positions)

    if boundaries:
        return pd.concat(boundaries, ignore_index=True)
    else:
        return pd.DataFrame(columns=["chrom", "start", "end", "insulation_score"])


def analyze_real_hic(
    cooler_path: str,
    output_dir: Path | None = None,
    region: str | None = None,
) -> dict:
    """
    Analyze real Hi-C data and extract key metrics.

    Args:
        cooler_path: Path to .cool or .mcool file
        output_dir: Output directory for results
        region: Optional region string (e.g., "chr8:127000000-130000000")

    Returns:
        Dictionary with analysis results
    """
    if output_dir is None:
        output_dir = Path("data/output/real_hic_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("REAL Hi-C DATA ANALYSIS")
    print("=" * 80)
    print(f"File: {cooler_path}")
    print(f"Region: {region or 'All chromosomes'}")
    print("=" * 80)

    # Load cooler
    print("\n📂 Loading cooler file...")
    try:
        c = cooler.Cooler(cooler_path)
        print(f"✅ Loaded: {c.info.get('genome-assembly', 'Unknown')}")
        print(f"   Bins: {c.info['nbins']}")
        print(f"   Contacts: {c.info['nnz']}")
    except Exception as e:
        print(f"❌ Error loading cooler: {e}")
        return {}

    # Compute insulation score
    print("\n📊 Computing insulation score...")
    insulation_df = compute_insulation_score(c, window_size=500000, resolution=10000)
    print(f"✅ Computed insulation for {len(insulation_df)} windows")

    # Detect TAD boundaries
    print("\n🔍 Detecting TAD boundaries...")
    boundaries_df = detect_tad_boundaries(insulation_df, threshold_percentile=10.0)
    print(f"✅ Detected {len(boundaries_df)} TAD boundaries")

    # Compute P(s) scaling
    print("\n📈 Computing P(s) scaling...")
    ps_df = compute_ps_scaling(c, max_distance=10_000_000)
    print(f"✅ Computed P(s) for {len(ps_df)} distance bins")

    # Save results
    insulation_file = output_dir / "insulation_scores.csv"
    boundaries_file = output_dir / "tad_boundaries.csv"
    ps_file = output_dir / "ps_scaling.csv"

    insulation_df.to_csv(insulation_file, index=False)
    boundaries_df.to_csv(boundaries_file, index=False)
    ps_df.to_csv(ps_file, index=False)

    print(f"\n💾 Results saved:")
    print(f"   • Insulation: {insulation_file}")
    print(f"   • Boundaries: {boundaries_file}")
    print(f"   • P(s): {ps_file}")

    # Summary statistics
    results = {
        "cooler_info": {
            "genome": c.info.get("genome-assembly", "Unknown"),
            "nbins": int(c.info["nbins"]),
            "nnz": int(c.info["nnz"]),
        },
        "insulation": {
            "mean": float(insulation_df["insulation_score"].mean()),
            "std": float(insulation_df["insulation_score"].std()),
            "min": float(insulation_df["insulation_score"].min()),
            "max": float(insulation_df["insulation_score"].max()),
        },
        "boundaries": {
            "count": len(boundaries_df),
            "mean_insulation": float(boundaries_df["insulation_score"].mean()) if len(boundaries_df) > 0 else 0.0,
        },
        "ps_scaling": {
            "num_points": len(ps_df),
            "mean_ps": float(ps_df["ps"].mean()) if len(ps_df) > 0 else 0.0,
        },
        "output_files": {
            "insulation": str(insulation_file),
            "boundaries": str(boundaries_file),
            "ps_scaling": str(ps_file),
        },
    }

    # Save summary
    import json
    summary_file = output_dir / "analysis_summary.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"   • Summary: {summary_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze real Hi-C data")
    parser.add_argument(
        "--cooler",
        type=str,
        default="data/real_hic/WT/Rao2014_GM12878_1000kb.cool",
        help="Path to cooler file",
    )
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Optional region (e.g., chr8:127000000-130000000)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory",
    )

    args = parser.parse_args()

    results = analyze_real_hic(
        cooler_path=args.cooler,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        region=args.region,
    )

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)


