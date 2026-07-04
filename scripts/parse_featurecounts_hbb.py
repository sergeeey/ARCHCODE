#!/usr/bin/env python3
"""
Parse featureCounts gene-count output and report HBB counts for WT/B6/A2.

Use after running featureCounts on Galaxy EU (see docs/GALAXY_EU_STAR_DOWNSTREAM.md).
Output: JSON (raw + normalized counts), optional bar plot.
Interpretation: exploratory only; n=1 per condition.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# Gene ID for HBB in common annotations (Ensembl, RefSeq)
HBB_IDS = {"HBB", "ENSG00000244734", "NM_000518", "HBB "}


def parse_featurecounts(path: Path) -> tuple[dict[str, int], list[str], dict[str, int]]:
    """
    Read featureCounts output (tab-separated).
    Returns (gene_id -> total_count for row, sample_names, sample -> column_index).
    First column is gene identifier; columns after Length (or first 6) are sample counts.
    """
    sample_names: list[str] = []
    sample_cols: dict[str, int] = {}
    gene_totals: dict[str, int] = {}

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts:
                continue
            first = (parts[0] or "").strip()
            if first.startswith("#"):
                continue
            if first == "Geneid" or first.startswith("Geneid"):
                for j, name in enumerate(parts[6:], start=6):
                    sn = name.strip().rstrip("/").strip()
                    if sn:
                        sample_names.append(sn)
                        sample_cols[sn] = j
                continue
            try:
                gene_id = (parts[0] or "").strip()
                if not gene_id:
                    continue
                start_col = 6 if len(parts) > 6 else 1
                total = 0
                for j in range(start_col, len(parts)):
                    try:
                        total += int(parts[j])
                    except ValueError:
                        pass
                gene_totals[gene_id] = total
                if not sample_cols and start_col < len(parts):
                    for j in range(start_col, len(parts)):
                        sample_cols[f"sample_{j}"] = j
                    sample_names = list(sample_cols.keys())
            except (IndexError, ValueError):
                continue

    if not sample_cols and gene_totals:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if parts and not (parts[0] or "").strip().startswith("#"):
                    for j in range(1, len(parts)):
                        sample_names.append(f"sample_{j}")
                        sample_cols[f"sample_{j}"] = j
                    break
    return gene_totals, sample_names, sample_cols


def get_hbb_counts(
    path: Path,
) -> tuple[dict[str, int], dict[str, float], list[str], dict[str, int]]:
    """
    Get raw counts and CPM-like normalized counts for HBB per sample.
    Returns (raw_counts, normalized_counts, sample_order, library_sizes).
    """
    gene_totals, sample_names, sample_cols = parse_featurecounts(path)
    if not sample_cols:
        return {}, {}, [], {}

    # Find HBB row: exact match or gene_id containing HBB
    hbb_key = None
    for gid in gene_totals:
        if gid in HBB_IDS or (gid.strip() in HBB_IDS) or gid.strip().startswith("HBB"):
            hbb_key = gid
            break
    if hbb_key is None:
        return {}, {}, list(sample_cols.keys()), {}

    # Re-read file to get per-sample counts for HBB
    raw: dict[str, int] = {}
    library_sizes: dict[str, int] = {}

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts:
                continue
            first = (parts[0] or "").strip()
            if first.startswith("#") or first == "Geneid":
                continue
            if first != hbb_key:
                continue
            for name, col in sample_cols.items():
                if col < len(parts):
                    try:
                        raw[name] = int(parts[col])
                    except ValueError:
                        raw[name] = 0
            break

    # Library size = sum of counts in that column (all genes)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= 6:
                continue
            if (parts[0] or "").strip().startswith("#") or (parts[0] or "").strip() == "Geneid":
                continue
            for name, col in sample_cols.items():
                if col < len(parts):
                    try:
                        library_sizes[name] = library_sizes.get(name, 0) + int(parts[col])
                    except ValueError:
                        pass

    normalized: dict[str, float] = {}
    for name in raw:
        lib = library_sizes.get(name) or 1
        # CPM-like: counts per million (per sample)
        normalized[name] = (raw[name] / lib) * 1e6 if lib else 0.0

    sample_order = [s for s in sample_names if s in raw]
    return raw, normalized, sample_order, library_sizes


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse featureCounts output and report HBB expression (WT/B6/A2)."
    )
    parser.add_argument(
        "featurecounts_file",
        nargs="?",
        type=Path,
        default=None,
        help="Path to featureCounts gene count output (tab-separated).",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=None,
        help="Path to featureCounts output (alternative to positional argument).",
    )
    parser.add_argument(
        "-o",
        "--output-json",
        type=Path,
        default=None,
        help="Output JSON path (default: results/hbb_featurecounts.json).",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Write bar plot to results/hbb_featurecounts_comparison.png.",
    )
    args = parser.parse_args()

    path = args.input or args.featurecounts_file
    if not path:
        raise SystemExit("Provide featureCounts file: path as argument or --input <path>")
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")

    raw, normalized, sample_order, library_sizes = get_hbb_counts(path)
    if not raw:
        raise SystemExit(
            "HBB row not found in featureCounts file. Check that the file contains a row with Geneid HBB (or ENSG00000244734)."
        )

    out_json = args.output_json or RESULTS_DIR / "hbb_featurecounts.json"
    out_json = out_json if out_json.is_absolute() else PROJECT_ROOT / out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "source_file": str(path.resolve()),
        "gene": "HBB",
        "samples": sample_order,
        "raw_counts": raw,
        "normalized_cpm": {k: round(v, 4) for k, v in normalized.items()},
        "library_sizes": library_sizes,
        "interpretation": "Exploratory; n=1 per condition. Normalization = counts per million (per-sample library size).",
    }
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(f"HBB counts written: {out_json}")
    for s in sample_order:
        print(f"  {s}: raw={raw.get(s, 0)}, CPM={normalized.get(s, 0):.2f}")

    if args.plot and sample_order:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            x = range(len(sample_order))
            ax.bar(x, [raw.get(s, 0) for s in sample_order], color="steelblue", edgecolor="black")
            ax.set_xticks(x)
            ax.set_xticklabels(sample_order, rotation=15)
            ax.set_ylabel("HBB raw counts")
            ax.set_title("HBB expression (featureCounts)\nExploratory, n=1 per condition")
            fig.tight_layout()
            plot_path = RESULTS_DIR / "hbb_featurecounts_comparison.png"
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(plot_path, dpi=150)
            plt.close(fig)
            print(f"Plot saved: {plot_path}")
        except ImportError:
            print("matplotlib not available; skipping plot (use --plot only if installed).")


if __name__ == "__main__":
    main()
