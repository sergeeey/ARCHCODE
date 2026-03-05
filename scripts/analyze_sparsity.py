#!/usr/bin/env python3
"""
Analyze matrix sparsity/health for ARCHCODE result JSON files.

Supports:
1) JSON files with embedded matrices (e.g. diagnostic_matrices.json)
2) Benchmark JSON files without matrices (reports dimensional metadata + warning)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def is_numeric_matrix_like(obj: Any) -> bool:
    """Return True if object looks like 2D numeric matrix."""
    if not isinstance(obj, list) or not obj:
        return False
    if not all(isinstance(row, list) for row in obj):
        return False
    # allow ragged lists, we validate after np.array conversion
    return True


def matrix_stats(name: str, arr: np.ndarray) -> dict[str, Any]:
    """Compute health metrics for a matrix."""
    flat = arr.ravel()
    finite_mask = np.isfinite(flat)
    finite = flat[finite_mask]
    zeros = np.count_nonzero(finite == 0)

    return {
        "name": name,
        "shape": tuple(arr.shape),
        "dtype": str(arr.dtype),
        "total_cells": int(flat.size),
        "finite_cells": int(finite.size),
        "nan_or_inf_cells": int(flat.size - finite.size),
        "zero_cells": int(zeros),
        "sparsity_zero_fraction": float(zeros / finite.size) if finite.size else 1.0,
        "min": float(np.min(finite)) if finite.size else None,
        "max": float(np.max(finite)) if finite.size else None,
        "mean": float(np.mean(finite)) if finite.size else None,
        "std": float(np.std(finite)) if finite.size else None,
    }


def extract_embedded_matrices(data: Any, prefix: str = "") -> list[tuple[str, np.ndarray]]:
    """Recursively find matrix-like lists and convert to numpy arrays."""
    found: list[tuple[str, np.ndarray]] = []
    if isinstance(data, dict):
        for k, v in data.items():
            child = f"{prefix}.{k}" if prefix else k
            found.extend(extract_embedded_matrices(v, child))
    elif is_numeric_matrix_like(data):
        try:
            arr = np.array(data, dtype=float)
            if arr.ndim == 2:
                found.append((prefix or "matrix", arr))
        except Exception:
            pass
    elif isinstance(data, list):
        for i, v in enumerate(data):
            child = f"{prefix}[{i}]"
            found.extend(extract_embedded_matrices(v, child))
    return found


def print_benchmark_metadata(data: dict[str, Any]) -> None:
    """Print useful metadata when matrices are not embedded."""
    locus = data.get("locus")
    window = data.get("window", {})
    print(f"  locus: {locus}")
    if window:
        print(
            f"  window: {window.get('chromosome')}:{window.get('start')}-{window.get('end')}"
        )
        print(
            f"  matrix target bins: {window.get('n_bins')} @ {window.get('resolution_bp')} bp"
        )

    if "alphagenome" in data:
        ag = data["alphagenome"]
        print("  alphagenome metadata:")
        print(f"    contact_map_shape: {ag.get('contact_map_shape')}")
        print(f"    contact_map_resolution: {ag.get('contact_map_resolution')}")
        print(f"    cell_line: {ag.get('cell_line')}")
    if "akita" in data:
        ak = data["akita"]
        print("  akita metadata:")
        print(f"    contact_map_shape: {ak.get('contact_map_shape')}")
        print(f"    contact_map_resolution: {ak.get('contact_map_resolution')}")
        print(f"    cell_type: {ak.get('cell_type')}")

    cor = data.get("correlations")
    if isinstance(cor, dict):
        print("  correlations:")
        for k, v in cor.items():
            if isinstance(v, dict) and "pearson_r" in v:
                print(f"    {k}: pearson_r={v['pearson_r']:.4f}, n={v.get('n')}")

    print("  note: no embedded matrices found in this file.")


def analyze_file(path: Path) -> int:
    print(f"\n=== {path} ===")
    if not path.exists():
        print("  ERROR: file not found")
        return 1

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ERROR: cannot parse JSON ({e})")
        return 1

    matrices = extract_embedded_matrices(data)
    if not matrices:
        if isinstance(data, dict):
            print_benchmark_metadata(data)
        else:
            print("  no embedded matrices found.")
        return 0

    for name, arr in matrices:
        stats = matrix_stats(name, arr)
        print(
            f"  [{stats['name']}] shape={stats['shape']} "
            f"sparsity={stats['sparsity_zero_fraction']:.2%} "
            f"nan/inf={stats['nan_or_inf_cells']} "
            f"min={stats['min']:.6f} max={stats['max']:.6f}"
        )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze matrix sparsity for ARCHCODE result JSON files"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="JSON files to analyze (e.g., results/diagnostic_matrices.json)",
    )
    args = parser.parse_args()

    code = 0
    for f in args.files:
        code |= analyze_file(Path(f))
    raise SystemExit(code)


if __name__ == "__main__":
    main()

