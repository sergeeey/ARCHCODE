#!/usr/bin/env python3
"""
EXPLORATORY follow-up to exp_orphan_enhancers (REJECT, OR=1.22, genome-wide/all-tissues).

Three independent blind agents (2026-07-02 audit, see .claude/memory/activeContext.md)
converged on the same recommendation: the genome-wide test pooled all 131 ABC biosamples
indiscriminately, while the ONE strong surviving signal in this project (enhancer proximity,
OR=34.05) came specifically from a tissue-matched (K562 erythroid) HBB analysis. This script
restricts the SAME analysis to erythroid-lineage ABC biosamples only.

IMPORTANT INTEGRITY NOTE: this is EXPLORATORY, not confirmatory. The decision to stratify by
tissue was made AFTER seeing the pooled genome-wide result was null -- this is post-hoc
subgroup analysis, the same class of risk already flagged in this project for the TP53
splice_region signal (null_results/20260605-..., "likely a statistical fluke in an
underpowered sub-analysis"). A positive result here is a NEW hypothesis to pre-register and
confirm on held-out data, NOT a reversal of the original REJECT verdict.

Original pre-registered script (untouched): scripts/orphan_enhancer_analysis.py
"""

import gzip
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)

from orphan_enhancer_analysis import (  # noqa: E402 -- needs sys.path.insert above first
    ABC_FILE,
    ABC_SCORE_MIN,
    GENCODE_FILE,
    GENE_COUNTS_FILE,
    VUS_FILE,
    build_buckets,
    cochran_mantel_haenszel,
    load_gene_tss_index,
    load_vus_index,
    nearest_gene,
    submission_bucket,
)

ERYTHROID_CELL_TYPES = {
    "K562-Roadmap",
    "CD34-positive_mobilized-Roadmap",
    "erythroblast-Corces2016",
    "megakaryocyte-erythroid_progenitor-Corces2016",
}

RESULTS_FILE = ROOT / "experiments/exp_orphan_enhancers/results_tissue_matched_exploratory.json"

# HBB locus, hg19/GRCh37 (matches this experiment's genome build)
HBB_CHROM = "chr11"
HBB_WINDOW_START = 5_100_000
HBB_WINDOW_END = 5_350_000  # +-125kb around HBB gene body, matches typical LCR-inclusive window


def stream_erythroid_enhancers(gene_index, gene_counts, locus_filter=None):
    n_seen = 0
    n_kept = 0
    with gzip.open(ABC_FILE, "rt", errors="ignore") as f:
        header = f.readline().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        required = ("chr", "start", "end", "class", "TargetGene", "ABC.Score", "CellType")
        max_col = max(col[k] for k in required)
        for line in f:
            n_seen += 1
            if n_seen % 3_000_000 == 0:
                print(f"    ...{n_seen:,} rows scanned, {n_kept:,} kept", file=sys.stderr)
            row = line.rstrip("\n").split("\t")
            if len(row) <= max_col:
                continue
            cell_type = row[col["CellType"]]
            if cell_type not in ERYTHROID_CELL_TYPES:
                continue
            chrom = row[col["chr"]]
            if locus_filter and not (chrom == locus_filter[0]):
                continue
            cls = row[col["class"]]
            if cls == "promoter":
                continue
            try:
                score = float(row[col["ABC.Score"]])
            except ValueError:
                continue
            if score < ABC_SCORE_MIN:
                continue
            try:
                start = int(row[col["start"]])
                end = int(row[col["end"]])
            except ValueError:
                continue
            if locus_filter:
                _, lo, hi = locus_filter
                if not (lo <= start <= hi or lo <= end <= hi):
                    continue
            target_gene = row[col["TargetGene"]]
            nearest = nearest_gene(chrom, (start + end) // 2, gene_index)
            is_orphan = nearest is not None and nearest != target_gene
            n_kept += 1
            yield {
                "chrom": chrom,
                "start": start,
                "end": end,
                "target_gene": target_gene,
                "nearest_gene": nearest,
                "orphan": is_orphan,
                "cell_type": cell_type,
                "abc_score": score,
                "bucket": submission_bucket(nearest, gene_counts),
            }
    print(f"    Total scanned: {n_seen:,}, kept (erythroid enhancer): {n_kept:,}", file=sys.stderr)


def summarize(buckets, n_records, label):
    total_orphan_vus = sum(b["orphan_vus"] for b in buckets.values())
    total_orphan_n = sum(b["orphan_n"] for b in buckets.values())
    total_regular_vus = sum(b["regular_vus"] for b in buckets.values())
    total_regular_n = sum(b["regular_n"] for b in buckets.values())
    mh_or, mh_p = cochran_mantel_haenszel(buckets)
    print(f"  [{label}] unique enhancer intervals: {n_records}")
    print(f"  [{label}] orphan_n={total_orphan_n} regular_n={total_regular_n}")
    print(f"  [{label}] CMH OR={mh_or} p={mh_p}")
    return {
        "label": label,
        "n_orphan": total_orphan_n,
        "n_regular": total_regular_n,
        "orphan_vus_rate": round(total_orphan_vus / total_orphan_n, 6) if total_orphan_n else None,
        "regular_vus_rate": round(total_regular_vus / total_regular_n, 6)
        if total_regular_n
        else None,
        "mh_odds_ratio": round(mh_or, 4) if mh_or == mh_or else None,
        "mh_p_value": mh_p,
        "bucket_breakdown": dict(buckets),
    }


def main():
    print("=" * 60)
    print("EXPLORATORY: tissue-matched (erythroid) orphan-enhancer retest")
    print("Post-hoc follow-up to REJECT verdict — see script docstring for integrity caveat")
    print("=" * 60)

    print("\n[1/3] Loading GENCODE (hg19) + ClinVar VUS (hg19) + gene counts...")
    gene_index = load_gene_tss_index(GENCODE_FILE)
    vus_index, n_vus = load_vus_index(VUS_FILE)
    with open(GENE_COUNTS_FILE) as f:
        gene_counts = json.load(f)
    print(f"  {n_vus} VUS variants loaded")

    print("\n[2/3] Streaming ABC predictions, erythroid biosamples ONLY, genome-wide...")
    enhancers = list(stream_erythroid_enhancers(gene_index, gene_counts))
    buckets, n_records = build_buckets(enhancers, vus_index)
    genome_wide_result = summarize(buckets, n_records, "erythroid-only, genome-wide")

    print(
        f"\n[3/3] Streaming ABC predictions, erythroid biosamples, HBB locus ONLY (chr11:{HBB_WINDOW_START}-{HBB_WINDOW_END})..."
    )
    hbb_enhancers = list(
        stream_erythroid_enhancers(
            gene_index, gene_counts, locus_filter=(HBB_CHROM, HBB_WINDOW_START, HBB_WINDOW_END)
        )
    )
    hbb_buckets, hbb_n_records = build_buckets(hbb_enhancers, vus_index)
    hbb_result = summarize(hbb_buckets, hbb_n_records, "erythroid-only, HBB locus")

    print(f"\n{'=' * 60}")
    print("RESULTS (EXPLORATORY — post-hoc subgroup, not a confirmatory test)")
    print("  Original genome-wide/all-tissue (REJECT): OR=1.221, p~0, n=661,294")
    print(
        f"  Erythroid-only, genome-wide: OR={genome_wide_result['mh_odds_ratio']} p={genome_wide_result['mh_p_value']} n_orphan={genome_wide_result['n_orphan']} n_regular={genome_wide_result['n_regular']}"
    )
    print(
        f"  Erythroid-only, HBB locus:   OR={hbb_result['mh_odds_ratio']} p={hbb_result['mh_p_value']} n_orphan={hbb_result['n_orphan']} n_regular={hbb_result['n_regular']}"
    )

    out = {
        "status": "EXPLORATORY — post-hoc subgroup analysis, not pre-registered, not confirmatory",
        "integrity_note": "Decision to stratify by tissue was made AFTER seeing the pooled null result. A positive finding here requires independent pre-registered confirmation before being treated as PROMOTE-grade evidence.",
        "original_rejected_result": {
            "OR": 1.2215,
            "p": 6.264803166810001e-39,
            "n": 661294,
            "scope": "genome-wide, all 131 biosamples, held-out chroms",
        },
        "erythroid_genome_wide": genome_wide_result,
        "erythroid_hbb_locus": hbb_result,
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
