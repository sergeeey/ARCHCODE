"""Hi-C Benchmarking Library for ARCHCODE.

Модуль для работы с Hi-C данными и сравнения симуляций с реальными данными.
"""

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cooler
import numpy as np
import pandas as pd
from scipy import sparse

try:
    import cooltools
    from cooltools import insulation, expected_cis
    COOLTOOLS_AVAILABLE = True
except ImportError:
    COOLTOOLS_AVAILABLE = False
    warnings.warn("cooltools not available. Some features will be limited.")


@dataclass
class HiCMetrics:
    """Структура для хранения метрик Hi-C."""

    p_s: pd.DataFrame  # P(s) scaling curve
    insulation: pd.DataFrame  # Insulation scores
    resolution: int  # Resolution in bp


def load_real_cooler(
    path: str | Path,
    region: Optional[str] = None,
    resolution: Optional[int] = None,
) -> cooler.Cooler:
    """
    Load a cooler file, handling URI strings.

    Args:
        path: Path to cooler file or URI string (e.g., "test.mcool::/resolutions/10000")
        region: Optional region string (e.g., "chr1:1000000-2000000")
        resolution: Optional resolution (for .mcool files)

    Returns:
        Cooler object

    Examples:
        >>> c = load_real_cooler("data.cool")
        >>> c = load_real_cooler("data.mcool::/resolutions/10000")
    """
    path_str = str(path)

    # Handle URI format: "file.mcool::/resolutions/10000"
    if "::" in path_str:
        file_path, uri = path_str.split("::", 1)
        c = cooler.Cooler(f"{file_path}::{uri}")
    else:
        c = cooler.Cooler(path_str)

    # Extract sub-region if specified
    if region:
        c = c.matrix(balance=False).fetch(region)

    return c


def simulation_to_cooler(
    matrix: np.ndarray,
    resolution: int,
    chrom_name: str = "chrSim",
    output_path: Optional[str | Path] = None,
) -> cooler.Cooler:
    """
    Convert numpy array to .cool format.

    Args:
        matrix: Contact matrix (2D numpy array)
        resolution: Resolution in bp
        chrom_name: Chromosome name (default: "chrSim")
        output_path: Optional path to save .cool file

    Returns:
        Cooler object

    Note:
        Creates a valid cooler structure with bins, pixels, and chromsizes.
    """
    n_bins = matrix.shape[0]
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Matrix must be square")

    # Create bins DataFrame
    bins = pd.DataFrame(
        {
            "chrom": [chrom_name] * n_bins,
            "start": np.arange(n_bins) * resolution,
            "end": (np.arange(n_bins) + 1) * resolution,
        }
    )

    # Create chromsizes DataFrame
    chromsize = (n_bins * resolution,)
    chromsizes = pd.Series({chrom_name: chromsize[0]})

    # Create pixels DataFrame from matrix
    # Convert dense matrix to sparse COO format
    coo = sparse.coo_matrix(matrix)
    pixels = pd.DataFrame(
        {
            "bin1_id": coo.row,
            "bin2_id": coo.col,
            "count": coo.data.astype(np.float64),
        }
    )

    # Create cooler
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        cooler.create_cooler(
            str(output_path),
            bins=bins,
            pixels=pixels,
            ordered=True,
            dtypes={"count": np.float64},
        )
        c = cooler.Cooler(str(output_path))
    else:
        # Create in-memory cooler
        # For simplicity, we'll create a temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".cool", delete=False) as tmp:
            tmp_path = tmp.name

        cooler.create_cooler(
            tmp_path,
            bins=bins,
            pixels=pixels,
            ordered=True,
            dtypes={"count": np.float64},
        )
        c = cooler.Cooler(tmp_path)

    return c


def compute_metrics(
    cooler_obj: cooler.Cooler,
    window_size: int = 10,
    ignore_diags: int = 2,
) -> HiCMetrics:
    """
    Compute Hi-C metrics (P(s) and Insulation).

    Args:
        cooler_obj: Cooler object
        window_size: Window size for insulation (in bins)
        ignore_diags: Number of diagonals to ignore for P(s)

    Returns:
        HiCMetrics dataclass

    Note:
        Handles potential API changes in cooltools and NaN values gracefully.
    """
    if not COOLTOOLS_AVAILABLE:
        raise ImportError("cooltools is required for metric computation")

    resolution = cooler_obj.binsize

    # Calculate P(s) scaling
    try:
        # Try new API first
        if hasattr(expected_cis, "expected_cis"):
            p_s = expected_cis.expected_cis(cooler_obj, ignore_diags=ignore_diags)
        else:
            # Fallback to older API
            p_s = expected_cis(cooler_obj, ignore_diags=ignore_diags)
    except Exception as e:
        warnings.warn(f"Error computing P(s): {e}. Using fallback method.")
        # Fallback: manual calculation
        matrix = cooler_obj.matrix(balance=False)[:]
        p_s = _compute_p_s_manual(matrix, resolution, ignore_diags)

    # Calculate Insulation Score
    try:
        insulation_df = insulation(
            cooler_obj,
            window_bp=window_size * resolution,
            ignore_diags=ignore_diags,
        )
        # Handle NaNs
        insulation_df = insulation_df.fillna(0.0)
    except Exception as e:
        warnings.warn(f"Error computing insulation: {e}. Using fallback method.")
        # Fallback: manual calculation
        matrix = cooler_obj.matrix(balance=False)[:]
        insulation_df = _compute_insulation_manual(matrix, window_size)

    return HiCMetrics(
        p_s=p_s,
        insulation=insulation_df,
        resolution=resolution,
    )


def _compute_p_s_manual(
    matrix: np.ndarray,
    resolution: int,
    ignore_diags: int = 2,
) -> pd.DataFrame:
    """
    Manual P(s) calculation (fallback).

    Args:
        matrix: Contact matrix
        resolution: Resolution in bp
        ignore_diags: Number of diagonals to ignore

    Returns:
        DataFrame with columns ['dist', 'count.avg']
    """
    n = matrix.shape[0]
    distances = []
    counts = []

    for diag in range(ignore_diags, n):
        dist = diag * resolution
        diag_values = np.diag(matrix, k=diag)
        avg_count = np.nanmean(diag_values)

        if not np.isnan(avg_count):
            distances.append(dist)
            counts.append(avg_count)

    return pd.DataFrame({"dist": distances, "count.avg": counts})


def _compute_insulation_manual(
    matrix: np.ndarray,
    window_size: int,
) -> pd.DataFrame:
    """
    Manual Insulation calculation (fallback).

    Args:
        matrix: Contact matrix
        window_size: Window size in bins

    Returns:
        DataFrame with insulation scores
    """
    n = matrix.shape[0]
    insulation_scores = []

    for i in range(n):
        start = max(0, i - window_size)
        end = min(n, i + window_size + 1)

        # Diamond insulation: sum contacts in diamond around bin i
        diamond_sum = 0.0
        for j in range(start, end):
            for k in range(start, end):
                if abs(j - i) + abs(k - i) <= window_size:
                    diamond_sum += matrix[j, k]

        insulation_scores.append(diamond_sum)

    # Convert to DataFrame
    insulation_df = pd.DataFrame(
        {
            "chrom": ["chrSim"] * n,
            "start": np.arange(n) * 10000,  # Default resolution
            "end": (np.arange(n) + 1) * 10000,
            "insulation_score": insulation_scores,
        }
    )

    return insulation_df


def synchronize_bins(
    real_cooler: cooler.Cooler,
    sim_matrix: np.ndarray,
    sim_resolution: int,
) -> tuple[cooler.Cooler, np.ndarray]:
    """
    Synchronize bins between real and simulated data.

    Args:
        real_cooler: Real Hi-C cooler object
        sim_matrix: Simulated contact matrix
        sim_resolution: Resolution of simulated matrix (bp)

    Returns:
        (trimmed_real_cooler, trimmed_sim_matrix)

    Raises:
        ValueError: If bin counts cannot be synchronized
    """
    real_resolution = real_cooler.binsize
    real_n_bins = len(real_cooler.bins())

    sim_n_bins = sim_matrix.shape[0]

    # Check if resolutions match
    if real_resolution != sim_resolution:
        warnings.warn(
            f"Resolution mismatch: real={real_resolution}, sim={sim_resolution}. "
            "Trimming to match bin counts."
        )

    # Trim to match bin counts
    if real_n_bins > sim_n_bins:
        # Trim real data
        real_matrix = real_cooler.matrix(balance=False)[:sim_n_bins, :sim_n_bins]
        trimmed_real_cooler = simulation_to_cooler(
            real_matrix, real_resolution, chrom_name="chrReal"
        )
        trimmed_sim_matrix = sim_matrix
    elif sim_n_bins > real_n_bins:
        # Trim simulated data
        trimmed_sim_matrix = sim_matrix[:real_n_bins, :real_n_bins]
        trimmed_real_cooler = real_cooler
    else:
        # Already matched
        trimmed_real_cooler = real_cooler
        trimmed_sim_matrix = sim_matrix

    return trimmed_real_cooler, trimmed_sim_matrix









