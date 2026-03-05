"""
Formal monotonicity test: ΔLSSIM vs distance to nearest enhancer.

Tests PR Gate Blocker B5: "No formal proof of monotonicity
relative to biological distance to enhancer."

Approach: empirical test across all 9 loci with enhancer annotations.
Bins variants by distance to nearest H3K27ac peak, computes mean ΔLSSIM
per bin, and tests for monotonic decrease (closer = more disruption).

Result: Spearman correlation of bin midpoint vs ΔLSSIM,
plus strict monotonicity check on binned means.
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import stats

PROJECT = Path(__file__).parent.parent

LOCI = [
    ("HBB", "hbb_95kb_subTAD.json", "UNIFIED_ATLAS_SUMMARY_95kb.json"),
]

# Atlas files for multi-locus
ATLAS_FILES = {
    "HBB": "HBB_Unified_Atlas.csv",
    "CFTR": "CFTR_Unified_Atlas_317kb.csv",
    "TP53": "TP53_Unified_Atlas_300kb.csv",
    "BRCA1": "BRCA1_Unified_Atlas_400kb.csv",
    "MLH1": "MLH1_Unified_Atlas_300kb.csv",
    "LDLR": "LDLR_Unified_Atlas_300kb.csv",
    "SCN5A": "SCN5A_Unified_Atlas_400kb.csv",
    "TERT": "TERT_Unified_Atlas_300kb.csv",
    "GJB2": "GJB2_Unified_Atlas_300kb.csv",
}

CONFIG_FILES = {
    "HBB": "hbb_95kb_subTAD.json",
    "CFTR": "cftr_317kb.json",
    "TP53": "tp53_300kb.json",
    "BRCA1": "brca1_400kb.json",
    "MLH1": "mlh1_300kb.json",
    "LDLR": "ldlr_300kb.json",
    "SCN5A": "scn5a_400kb.json",
    "TERT": "tert_300kb.json",
    "GJB2": "gjb2_300kb.json",
}

BINS = [(0, 1000), (1000, 5000), (5000, 20000), (20000, 50000), (50000, 200000)]
BIN_LABELS = ["≤1kb", "1-5kb", "5-20kb", "20-50kb", ">50kb"]


def load_enhancer_positions(config_path: Path) -> list[int]:
    """Extract enhancer midpoints from locus config."""
    with open(config_path) as f:
        config = json.load(f)
    enhancers = config.get("features", {}).get("enhancers", [])
    positions = []
    for e in enhancers:
        if isinstance(e, dict):
            pos = e.get("position") or e.get("pos")
            if pos is not None:
                positions.append(int(pos))
        elif isinstance(e, (int, float)):
            positions.append(int(e))
    return positions


def min_distance(pos: int, targets: list[int]) -> int:
    """Minimum distance from pos to any target."""
    if not targets:
        return 999999
    return min(abs(pos - t) for t in targets)


def load_atlas_csv(path: Path) -> list[dict]:
    """Load atlas CSV and return list of variant dicts."""
    variants = []
    with open(path) as f:
        for row in csv.DictReader(f):
            lssim = row.get("ARCHCODE_LSSIM", "")
            label = row.get("Label", "")
            pos = row.get("Position_GRCh38", "") or row.get("Position", "")
            if lssim and label and pos:
                try:
                    variants.append({
                        "pos": int(pos),
                        "lssim": float(lssim),
                        "label": label,
                    })
                except ValueError:
                    pass
    return variants


def load_atlas_json(path: Path) -> list[dict]:
    """Load HBB JSON atlas."""
    with open(path) as f:
        data = json.load(f)

    variants = []
    if isinstance(data, dict) and "variants" in data:
        for v in data["variants"]:
            pos = v.get("position") or v.get("pos")
            lssim = v.get("lssim") or v.get("ARCHCODE_LSSIM")
            label = v.get("label") or v.get("Label")
            if pos and lssim and label:
                variants.append({
                    "pos": int(pos),
                    "lssim": float(lssim),
                    "label": str(label),
                })
    return variants


def analyze_locus(locus: str) -> dict | None:
    """Analyze distance-LSSIM relationship for one locus."""
    config_path = PROJECT / "config" / "locus" / CONFIG_FILES[locus]
    enh_positions = load_enhancer_positions(config_path)

    if not enh_positions:
        return None

    atlas_file = ATLAS_FILES[locus]
    atlas_path = PROJECT / "results" / atlas_file
    if not atlas_path.exists():
        return None

    variants = load_atlas_csv(atlas_path)

    if not variants:
        return None

    # Compute distance to nearest enhancer for each variant
    for v in variants:
        v["enh_dist"] = min_distance(v["pos"], enh_positions)

    # Split by label
    path_vars = [v for v in variants if "athogenic" in v["label"]]
    ben_vars = [v for v in variants if "enign" in v["label"]]

    if not path_vars or not ben_vars:
        return None

    # Bin analysis
    bin_results = []
    for (lo, hi), label in zip(BINS, BIN_LABELS):
        p_in_bin = [v for v in path_vars if lo <= v["enh_dist"] < hi]
        b_in_bin = [v for v in ben_vars if lo <= v["enh_dist"] < hi]

        if p_in_bin and b_in_bin:
            p_mean = np.mean([v["lssim"] for v in p_in_bin])
            b_mean = np.mean([v["lssim"] for v in b_in_bin])
            delta = b_mean - p_mean
            bin_results.append({
                "bin": label,
                "lo": lo,
                "hi": hi,
                "midpoint": (lo + hi) / 2,
                "n_path": len(p_in_bin),
                "n_ben": len(b_in_bin),
                "path_mean_lssim": round(float(p_mean), 6),
                "ben_mean_lssim": round(float(b_mean), 6),
                "delta_lssim": round(float(delta), 6),
            })

    if len(bin_results) < 2:
        return None

    # Monotonicity test: ΔLSSIM should decrease with distance
    deltas = [b["delta_lssim"] for b in bin_results]
    midpoints = [b["midpoint"] for b in bin_results]

    # Spearman: negative correlation = closer to enhancer → larger delta
    rho, p_val = stats.spearmanr(midpoints, deltas)

    # Strict monotonicity check
    is_monotone = all(deltas[i] >= deltas[i+1] for i in range(len(deltas)-1))

    # Approximate monotonicity (allowing 1 violation)
    violations = sum(1 for i in range(len(deltas)-1) if deltas[i] < deltas[i+1])

    return {
        "locus": locus,
        "n_enhancers": len(enh_positions),
        "n_path": len(path_vars),
        "n_ben": len(ben_vars),
        "bins": bin_results,
        "spearman_rho": round(float(rho), 4),
        "spearman_p": float(f"{p_val:.4e}"),
        "strictly_monotone": is_monotone,
        "monotonicity_violations": violations,
    }


def main():
    results = []
    all_deltas = []
    all_midpoints = []

    print("=" * 70)
    print("MONOTONICITY TEST: ΔLSSIM vs Distance to Nearest Enhancer")
    print("=" * 70)

    for locus in ATLAS_FILES:
        r = analyze_locus(locus)
        if r is None:
            print(f"\n{locus}: SKIP (no enhancer data or insufficient variants)")
            continue

        results.append(r)
        print(f"\n{locus} ({r['n_enhancers']} enhancers, {r['n_path']}P/{r['n_ben']}B):")
        print(f"  {'Bin':<10} {'N_P':>5} {'N_B':>5} {'ΔLSSIM':>10} {'P_mean':>10} {'B_mean':>10}")
        for b in r["bins"]:
            print(f"  {b['bin']:<10} {b['n_path']:>5} {b['n_ben']:>5} "
                  f"{b['delta_lssim']:>10.6f} {b['path_mean_lssim']:>10.6f} "
                  f"{b['ben_mean_lssim']:>10.6f}")

        print(f"  Spearman ρ = {r['spearman_rho']:.4f} (p = {r['spearman_p']:.4e})")
        print(f"  Strictly monotone: {'YES' if r['strictly_monotone'] else 'NO'}"
              f" ({r['monotonicity_violations']} violations)")

        for b in r["bins"]:
            all_deltas.append(b["delta_lssim"])
            all_midpoints.append(b["midpoint"])

    # Pooled test across all loci
    if len(all_deltas) >= 3:
        rho, p = stats.spearmanr(all_midpoints, all_deltas)
        print(f"\n{'=' * 70}")
        print(f"POOLED MONOTONICITY (all loci, {len(all_deltas)} bins):")
        print(f"  Spearman ρ = {rho:.4f} (p = {p:.4e})")
        print(f"  Direction: {'CONFIRMED (negative = closer → larger delta)' if rho < 0 else 'NOT CONFIRMED'}")
        print(f"{'=' * 70}")

        pooled = {
            "pooled_spearman_rho": round(float(rho), 4),
            "pooled_spearman_p": float(f"{p:.4e}"),
            "pooled_n_bins": len(all_deltas),
            "direction_confirmed": bool(rho < 0),
        }
    else:
        pooled = {}

    # Save results
    output = {
        "test": "Monotonicity: ΔLSSIM vs enhancer distance",
        "hypothesis": "ΔLSSIM decreases monotonically with distance to nearest enhancer",
        "method": "Spearman rank correlation of bin midpoints vs ΔLSSIM",
        "bins": BIN_LABELS,
        "per_locus": results,
        **pooled,
    }

    out_path = PROJECT / "results" / "monotonicity_test_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
