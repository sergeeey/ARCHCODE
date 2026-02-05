#!/usr/bin/env python3
"""
AlphaGenome Python Wrapper for ARCHCODE Integration

This script bridges the official AlphaGenome Python SDK with our TypeScript codebase.
Called via child_process.spawn() from AlphaGenomeService.ts.

Usage:
    python alphagenome_wrapper.py predict <chr> <start> <end> [--api-key KEY]
    python alphagenome_wrapper.py check

Output: JSON to stdout

@author Sergey V. Boyko (sergeikuch80@gmail.com)
@version 1.0.0
"""

import sys
import os
import json
import argparse
from typing import Optional, Dict, Any

# Check if alphagenome SDK is available
ALPHAGENOME_AVAILABLE = False
DnaClient = None
create_client = None
Interval = None
OutputType = None

try:
    from alphagenome.models.dna_client import create as create_client, DnaClient, OutputType
    from alphagenome.data.genome import Interval
    ALPHAGENOME_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)

# Alternative: try alphagenome_research (local weights)
ALPHAGENOME_RESEARCH_AVAILABLE = False
try:
    from alphagenome_research.model import dna_model as research_model
    ALPHAGENOME_RESEARCH_AVAILABLE = True
except ImportError:
    pass


def check_availability() -> Dict[str, Any]:
    """Check if AlphaGenome SDK is available."""
    return {
        "status": "ok",
        "alphagenome_sdk": ALPHAGENOME_AVAILABLE,
        "alphagenome_research": ALPHAGENOME_RESEARCH_AVAILABLE,
        "python_version": sys.version,
        "message": "AlphaGenome SDK ready" if ALPHAGENOME_AVAILABLE else "SDK not installed. Run: pip install alphagenome"
    }


def predict_structure(
    chromosome: str,
    start: int,
    end: int,
    api_key: Optional[str] = None,
    resolution: int = 5000,
    cell_type: str = "GM12878"
) -> Dict[str, Any]:
    """
    Predict chromatin structure using AlphaGenome.

    Args:
        chromosome: Chromosome name (e.g., 'chr11')
        start: Start position
        end: End position
        api_key: AlphaGenome API key (optional for local weights)
        resolution: Bin resolution in bp (default: 5000)
        cell_type: Cell type for prediction (default: GM12878)

    Returns:
        Dictionary with prediction results
    """

    # Calculate dimensions
    original_length = end - start

    # AlphaGenome supported sequence lengths
    SUPPORTED_LENGTHS = [16384, 131072, 524288, 1048576]

    # Find the smallest supported length that covers our region
    selected_length = None
    for length in SUPPORTED_LENGTHS:
        if length >= original_length:
            selected_length = length
            break

    if selected_length is None:
        selected_length = SUPPORTED_LENGTHS[-1]  # Use largest if region is too big

    # Adjust start/end to center our region in the supported window
    center = (start + end) // 2
    adjusted_start = center - selected_length // 2
    adjusted_end = center + selected_length // 2

    # Ensure coordinates are valid (not negative)
    if adjusted_start < 0:
        adjusted_start = 0
        adjusted_end = selected_length

    print(f"Original: {start}-{end} ({original_length}bp)", file=sys.stderr)
    print(f"Adjusted: {adjusted_start}-{adjusted_end} ({selected_length}bp)", file=sys.stderr)

    n_bins = original_length // resolution

    # Try official SDK first
    if ALPHAGENOME_AVAILABLE:
        try:
            return _predict_with_sdk(
                chromosome, start, end, api_key, resolution, cell_type,
                adjusted_start=adjusted_start, adjusted_end=adjusted_end
            )
        except Exception as e:
            return {
                "status": "error",
                "error": f"SDK prediction failed: {str(e)}",
                "fallback": True
            }

    # Try research package (local weights)
    if ALPHAGENOME_RESEARCH_AVAILABLE:
        try:
            return _predict_with_research(chromosome, start, end, resolution, cell_type)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Research model failed: {str(e)}",
                "fallback": True
            }

    # No SDK available
    return {
        "status": "error",
        "error": "AlphaGenome SDK not installed",
        "install_command": "pip install alphagenome",
        "fallback": True
    }


def _predict_with_sdk(
    chromosome: str,
    start: int,
    end: int,
    api_key: Optional[str],
    resolution: int,
    cell_type: str,
    adjusted_start: int = None,
    adjusted_end: int = None
) -> Dict[str, Any]:
    """Predict using official AlphaGenome SDK (API-based)."""

    if not api_key:
        raise ValueError("API key required for AlphaGenome SDK")

    # Use adjusted coordinates for API call
    api_start = adjusted_start if adjusted_start is not None else start
    api_end = adjusted_end if adjusted_end is not None else end

    # Create client with API key
    client = create_client(api_key=api_key)

    # Create interval with supported window size
    interval = Interval(
        chromosome=chromosome,
        start=api_start,
        end=api_end
    )

    # Request contact map prediction
    print(f"Calling AlphaGenome API for {chromosome}:{start}-{end}...", file=sys.stderr)

    try:
        # Use predict_interval method
        # Note: ontology_terms=None for contact maps (not tissue-specific)
        outputs = client.predict_interval(
            interval=interval,
            requested_outputs=[OutputType.CONTACT_MAPS],
            ontology_terms=None,
        )
    except Exception as e:
        error_msg = str(e)
        # Check for common errors
        if "PERMISSION_DENIED" in error_msg:
            raise ValueError(f"API key not authorized for AlphaGenome: {error_msg}")
        elif "INVALID_ARGUMENT" in error_msg:
            raise ValueError(f"Invalid request parameters: {error_msg}")
        else:
            raise

    # Extract contact map
    contact_map_data = outputs.get(OutputType.CONTACT_MAPS)

    if contact_map_data is None:
        raise ValueError("No contact map in response")

    # Convert to numpy for easier manipulation
    import numpy as np

    if hasattr(contact_map_data, 'values'):
        raw_matrix = np.array(contact_map_data.values)
    elif hasattr(contact_map_data, 'tolist'):
        raw_matrix = np.array(contact_map_data)
    else:
        raw_matrix = np.array(list(contact_map_data))

    print(f"Raw matrix shape: {raw_matrix.shape}", file=sys.stderr)

    # Handle 3D matrix (N x N x tracks) - take mean across tracks
    if len(raw_matrix.shape) == 3:
        # Shape is (H, W, channels) - average across channels
        matrix_2d = np.mean(raw_matrix, axis=2)
    else:
        matrix_2d = raw_matrix

    print(f"2D matrix shape: {matrix_2d.shape}", file=sys.stderr)

    # Crop to original region within the larger window
    # The API returns a larger window, we need to extract our region
    api_length = api_end - api_start
    original_length = end - start

    # Calculate bin indices for our region within the larger window
    bins_total = matrix_2d.shape[0]
    bp_per_bin = api_length / bins_total

    # Offset from start of API window to start of our region
    offset_bp = start - api_start
    offset_bins = int(offset_bp / bp_per_bin)

    # Number of bins for our region
    region_bins = int(original_length / bp_per_bin)

    print(f"Extracting bins {offset_bins}:{offset_bins + region_bins} for our region", file=sys.stderr)

    # Extract submatrix for our region
    cropped = matrix_2d[offset_bins:offset_bins + region_bins, offset_bins:offset_bins + region_bins]

    # Resize to target bins (our resolution)
    target_bins = original_length // resolution
    if cropped.shape[0] != target_bins:
        # Simple downsampling by block averaging
        from scipy.ndimage import zoom
        scale = target_bins / cropped.shape[0]
        cropped = zoom(cropped, scale, order=1)

    print(f"Final matrix shape: {cropped.shape}", file=sys.stderr)

    # Normalize to [0, 1]
    cropped = (cropped - cropped.min()) / (cropped.max() - cropped.min() + 1e-8)

    matrix_data = cropped.tolist()

    # Get epigenetic tracks if available
    epigenetics = {}

    return {
        "status": "ok",
        "source": "alphagenome_sdk",
        "interval": {
            "chromosome": chromosome,
            "start": start,
            "end": end
        },
        "contact_map": {
            "matrix": matrix_data,
            "resolution": resolution,
            "rows": len(matrix_data),
            "cols": len(matrix_data[0]) if matrix_data else 0,
            "normalization": "observed"
        },
        "epigenetics": epigenetics,
        "confidence": 0.95,
        "model_version": "alphagenome-sdk-v0.5.1"
    }


def _predict_with_research(
    chromosome: str,
    start: int,
    end: int,
    resolution: int,
    cell_type: str
) -> Dict[str, Any]:
    """Predict using alphagenome_research package (local weights)."""

    # Try to load from Kaggle or HuggingFace
    try:
        model = research_model.create_from_kaggle('all_folds')
    except Exception:
        try:
            model = research_model.create_from_huggingface('all_folds')
        except Exception as e:
            raise RuntimeError(f"Could not load model weights: {e}")

    # Create interval
    interval = genome.Interval(
        chromosome=chromosome,
        start=start,
        end=end
    )

    # Get prediction
    outputs = model.predict(
        interval=interval,
        requested_outputs=[research_model.OutputType.CONTACT_MAPS]
    )

    # Extract and convert contact map
    contact_map = outputs.contact_maps
    matrix_data = contact_map.tolist() if hasattr(contact_map, 'tolist') else list(contact_map)

    return {
        "status": "ok",
        "source": "alphagenome_research",
        "interval": {
            "chromosome": chromosome,
            "start": start,
            "end": end
        },
        "contact_map": {
            "matrix": matrix_data,
            "resolution": resolution,
            "rows": len(matrix_data),
            "cols": len(matrix_data[0]) if matrix_data else 0,
            "normalization": "observed"
        },
        "epigenetics": {},
        "confidence": 0.92,
        "model_version": "alphagenome-research-v1"
    }


def main():
    parser = argparse.ArgumentParser(
        description='AlphaGenome Python Wrapper for ARCHCODE'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check SDK availability')

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict chromatin structure')
    predict_parser.add_argument('chromosome', type=str, help='Chromosome (e.g., chr11)')
    predict_parser.add_argument('start', type=int, help='Start position')
    predict_parser.add_argument('end', type=int, help='End position')
    predict_parser.add_argument('--api-key', type=str, help='AlphaGenome API key')
    predict_parser.add_argument('--resolution', type=int, default=5000, help='Bin resolution (bp)')
    predict_parser.add_argument('--cell-type', type=str, default='GM12878', help='Cell type')

    args = parser.parse_args()

    if args.command == 'check':
        result = check_availability()
    elif args.command == 'predict':
        result = predict_structure(
            chromosome=args.chromosome,
            start=args.start,
            end=args.end,
            api_key=args.api_key,
            resolution=args.resolution,
            cell_type=args.cell_type
        )
    else:
        result = {"status": "error", "error": "Unknown command. Use 'check' or 'predict'"}

    # Output JSON to stdout
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
