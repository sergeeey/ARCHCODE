#!/usr/bin/env python3
"""
Filter STAR SJ.out.tab by STAR manual criteria and count novel junctions in HBB locus.

EXPLORATORY only. n=1 per condition. Do not use for strong manuscript claims without
biological replicates. Normalize by sequencing depth when comparing counts.

STAR SJ.out.tab: col1=chr, col2=start, col3=end, col4=strand, col5=motif,
  col6=annotated (0=novel), col7=unique_reads, col8=multimap, col9=max_overhang.
Filter: motif>0, annotated==0, unique_reads>5. Region: chr11 5,220,000-5,230,000 (HBB).

Usage:
  python scripts/filter_star_novel_junctions_hbb.py WT.SJ.out.tab B6.SJ.out.tab A2.SJ.out.tab
  python scripts/filter_star_novel_junctions_hbb.py WT.SJ.out.tab B6.SJ.out.tab A2.SJ.out.tab --depth-json path/to/depth.json

Output: JSON + print summary. Optional --depth-json: file with keys WT, B6, A2 and HBB read counts for normalization.
"""

import argparse
import csv
import json
from pathlib import Path

HBB_CHR = "11"
HBB_START = 5_220_000
HBB_END = 5_230_000
MIN_UNIQUE_READS = 6

# Default depths (HBB locus reads) from check_sequencing_depth.py output if not provided
DEFAULT_DEPTH = {
    "WT": 424_685,
    "B6": 736_251,
    "A2": 1_278_373,
}


def load_depth_json(path: Path) -> dict:
    """Load depth from check_sequencing_depth output or similar {sample: hbb_reads}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "samples" in data:
        return {s["name"]: s.get("hbb_reads", 0) for s in data["samples"]}
    return data


def count_novel_hbb(sj_path: Path, min_reads: int = MIN_UNIQUE_READS) -> int:
    """Count novel junctions in HBB region from STAR SJ.out.tab."""
    count = 0
    with open(sj_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if not row or row[0].startswith("#"):
                continue
            try:
                chrom = row[0].lstrip("chr")
                start = int(row[1])
                end = int(row[2])
                motif = row[4]
                annotated = int(row[5])
                unique_reads = int(row[6])
            except (ValueError, IndexError):
                continue
            if chrom != HBB_CHR or start < HBB_START or end > HBB_END:
                continue
            if motif == "0" or annotated != 0 or unique_reads < min_reads:
                continue
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Count novel HBB junctions from STAR SJ.out.tab (exploratory, n=1)."
    )
    parser.add_argument(
        "sj_files",
        nargs=3,
        type=Path,
        metavar=("WT_SJ", "B6_SJ", "A2_SJ"),
        help="Paths to WT, B6, A2 STAR SJ.out.tab files",
    )
    parser.add_argument(
        "--min-reads",
        type=int,
        default=MIN_UNIQUE_READS,
        help=f"Minimum unique reads per junction (default {MIN_UNIQUE_READS})",
    )
    parser.add_argument(
        "--depth-json",
        type=Path,
        default=None,
        help="JSON with sample names and HBB read counts for normalization",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Write JSON result to this path",
    )
    args = parser.parse_args()
    
    names = ["WT", "B6", "A2"]
    counts = {}
    for name, path in zip(names, args.sj_files):
        if not path.exists():
            print(f"ERROR: file not found: {path}")
            return 1
        counts[name] = count_novel_hbb(path, min_reads=args.min_reads)
    
    depth = DEFAULT_DEPTH.copy()
    if args.depth_json and args.depth_json.exists():
        depth.update(load_depth_json(args.depth_json))
    
    normalized = {}
    for name in names:
        d = depth.get(name, 1)
        normalized[name] = (counts[name] / (d / 1_000_000)) if d else 0
    
    result = {
        "disclaimer": "Exploratory; n=1 per condition; do not use for strong manuscript claims.",
        "filter": {"motif": ">0", "annotated": "==0", "unique_reads": f">= {args.min_reads}"},
        "region": f"chr{HBB_CHR}:{HBB_START}-{HBB_END}",
        "raw_counts": counts,
        "depth_hbb_reads": depth,
        "normalized_per_million": normalized,
    }
    
    print("=" * 60)
    print("  STAR novel junctions (HBB locus) — EXPLORATORY")
    print("=" * 60)
    print()
    print("Raw counts (novel only, filter applied):")
    for name in names:
        print(f"  {name}: {counts[name]}")
    print()
    print("Normalized (per million HBB reads):")
    for name in names:
        print(f"  {name}: {normalized[name]:.1f}")
    print()
    print("(Interpret with caution: n=1, depth may differ between samples.)")
    print()
    
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Written: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())
