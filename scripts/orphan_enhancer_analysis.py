#!/usr/bin/env python3
"""
exp_orphan_enhancers: Are ClinVar VUS enriched near "orphan" enhancers
(ABC-predicted target gene != nearest gene) vs "regular" enhancers?

Pre-registered in claim.md BEFORE this script produced any results:
  - Calibration set: chr1-chr11 (parameter exploration allowed only here)
  - Held-out confirmatory set: chr12-chr22, chrX (no changes after seeing this)
  - Go criterion: OR>=2.0 AND p<0.01 (Cochran-Mantel-Haenszel, stratified) on held-out set

Confound control: match orphan vs regular enhancers by nearest-gene ClinVar
submission-volume bucket (proxy for how heavily a region has been clinically
sequenced) before comparing VUS enrichment -- avoids the "well-studied genes
have more VUS regardless of mechanism" trap.

Statistics: Cochran-Mantel-Haenszel test for stratified 2x2 tables (closed-form,
O(number of buckets)) -- the standard classical test for exactly this design
(exposure vs outcome association, controlling for a matching covariate).
"""

import bisect
import gzip
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

ABC_FILE = ROOT / "data/input/abc_predictions/AllPredictions.txt.gz"
GENCODE_FILE = ROOT / "data/input/gencode_genes_hg19_stranded.json"
VUS_FILE = ROOT / "data/input/clinvar_vus_hg19.json"
GENE_COUNTS_FILE = ROOT / "data/input/clinvar_gene_submission_counts_hg19.json"
RESULTS_FILE = ROOT / "experiments/exp_orphan_enhancers/results.json"

CALIBRATION_CHROMS = {f"chr{i}" for i in range(1, 12)}
HELDOUT_CHROMS = {f"chr{i}" for i in range(12, 23)} | {"chrX"}
ABC_SCORE_MIN = 0.02  # standard ABC threshold (file is pre-filtered at 0.015, use stricter)


def load_gene_tss_index(path):
    """Per-chromosome sorted list of (tss_position, gene_symbol) for nearest-gene lookup."""
    with open(path) as f:
        genes = json.load(f)
    by_chrom = defaultdict(list)
    for g in genes:
        tss = g["tss"]  # strand-correct TSS (start for +, end for -)
        by_chrom[g["chrom"]].append((tss, g["gene"]))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return by_chrom


def nearest_gene(chrom, pos, gene_index):
    lst = gene_index.get(chrom)
    if not lst:
        return None
    positions = [x[0] for x in lst]
    i = bisect.bisect_left(positions, pos)
    candidates = []
    if i < len(lst):
        candidates.append(lst[i])
    if i > 0:
        candidates.append(lst[i - 1])
    if not candidates:
        return None
    best = min(candidates, key=lambda x: abs(x[0] - pos))
    return best[1]


def load_vus_index(path):
    with open(path) as f:
        data = json.load(f)
    by_chrom = defaultdict(list)
    for v in data["variants"]:
        by_chrom[v["chrom"]].append((v["start"], v["end"]))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return by_chrom, data["n"]


def has_vus_overlap(chrom, start, end, vus_index):
    lst = vus_index.get(chrom)
    if not lst:
        return False
    starts = [x[0] for x in lst]
    i = bisect.bisect_left(starts, start)
    for j in range(max(0, i - 5), min(len(lst), i + 5)):
        v_start, v_end = lst[j]
        if v_start <= end and v_end >= start:
            return True
    return False


def submission_bucket(gene, gene_counts):
    n = gene_counts.get(gene, 0) if gene else 0
    if n == 0:
        return "none"
    elif n < 10:
        return "low"
    elif n < 100:
        return "medium"
    else:
        return "high"


def stream_abc_enhancers(gene_index, gene_counts, chroms_filter):
    """Stream ABC file, yield dicts for enhancer rows in the given chromosome set."""
    n_seen = 0
    n_kept = 0
    with gzip.open(ABC_FILE, "rt", errors="ignore") as f:
        header = f.readline().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        required = ("chr", "start", "end", "class", "TargetGene", "ABC.Score", "CellType")
        max_col = max(col[k] for k in required)
        for line in f:
            n_seen += 1
            if n_seen % 2_000_000 == 0:
                print(f"    ...{n_seen:,} rows scanned, {n_kept:,} kept", file=sys.stderr)
            row = line.rstrip("\n").split("\t")
            if len(row) <= max_col:
                continue
            chrom = row[col["chr"]]
            if chrom not in chroms_filter:
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
            target_gene = row[col["TargetGene"]]
            cell_type = row[col["CellType"]]

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
    print(
        f"    Total scanned: {n_seen:,}, kept (enhancer, score>={ABC_SCORE_MIN}): {n_kept:,}",
        file=sys.stderr,
    )


def build_buckets(enhancers, vus_index):
    """Deduplicate enhancer rows by genomic interval, tag VUS overlap, group into
    submission-volume-matched strata (buckets) with 2x2 (orphan x VUS) counts."""
    by_interval = defaultdict(list)
    for e in enhancers:
        by_interval[(e["chrom"], e["start"], e["end"])].append(e)

    buckets = defaultdict(
        lambda: {"orphan_vus": 0, "orphan_n": 0, "regular_vus": 0, "regular_n": 0}
    )
    n_records = 0
    for (chrom, start, end), rows in by_interval.items():
        orphan_votes = sum(1 for r in rows if r["orphan"])
        is_orphan = orphan_votes > len(rows) / 2
        bucket_key = rows[0]["bucket"]
        vus_hit = has_vus_overlap(chrom, start, end, vus_index)

        b = buckets[bucket_key]
        if is_orphan:
            b["orphan_n"] += 1
            b["orphan_vus"] += int(vus_hit)
        else:
            b["regular_n"] += 1
            b["regular_vus"] += int(vus_hit)
        n_records += 1

    return buckets, n_records


def cochran_mantel_haenszel(buckets):
    """Stratified (matched-control) test for orphan-vs-regular VUS enrichment.

    Standard closed-form CMH statistic for stratified 2x2 tables -- the correct classical
    test for this design (exposure-outcome association controlling for a matching stratum),
    computed in O(number of buckets) rather than by permutation simulation over millions
    of individual records.
    """
    num_or = 0.0
    den_or = 0.0
    num_stat = 0.0
    var_stat = 0.0

    for b in buckets.values():
        a = b["orphan_vus"]
        b_ = b["orphan_n"] - a
        c = b["regular_vus"]
        d = b["regular_n"] - c
        n = a + b_ + c + d
        if n < 2:
            continue

        num_or += (a * d) / n
        den_or += (b_ * c) / n

        expected_a = ((a + b_) * (a + c)) / n
        variance_a = ((a + b_) * (c + d) * (a + c) * (b_ + d)) / (n * n * (n - 1))

        num_stat += a - expected_a
        var_stat += variance_a

    mh_or = (num_or / den_or) if den_or > 0 else float("nan")

    if var_stat <= 0:
        return mh_or, float("nan")

    chi2 = max(0.0, abs(num_stat) - 0.5) ** 2 / var_stat  # continuity-corrected
    # 1-df chi-square survival function via X = Z^2: P(chi2_1 >= x) = erfc(sqrt(x/2))
    p_value = math.erfc(math.sqrt(chi2 / 2))
    return mh_or, p_value


def summarize(buckets, n_records, label):
    total_orphan_vus = sum(b["orphan_vus"] for b in buckets.values())
    total_orphan_n = sum(b["orphan_n"] for b in buckets.values())
    total_regular_vus = sum(b["regular_vus"] for b in buckets.values())
    total_regular_n = sum(b["regular_n"] for b in buckets.values())

    orphan_rate = total_orphan_vus / total_orphan_n if total_orphan_n else 0
    regular_rate = total_regular_vus / total_regular_n if total_regular_n else 0

    mh_or, mh_p = cochran_mantel_haenszel(buckets)

    print(f"  [{label}] unique enhancer intervals: {n_records}")
    print(f"  [{label}] orphan_n={total_orphan_n} regular_n={total_regular_n}")
    print(f"  [{label}] CMH OR={mh_or:.3f} p={mh_p:.6f}")

    return {
        "label": label,
        "n_orphan": total_orphan_n,
        "n_regular": total_regular_n,
        "orphan_vus_rate": round(orphan_rate, 6),
        "regular_vus_rate": round(regular_rate, 6),
        "mh_odds_ratio": round(mh_or, 4) if mh_or == mh_or else None,  # NaN check
        "mh_p_value": mh_p,
        "bucket_breakdown": dict(buckets),
    }


def main():
    print("=" * 60)
    print("exp_orphan_enhancers: ABC orphan status vs ClinVar VUS density")
    print("=" * 60)

    print("\n[1/4] Loading GENCODE gene index...")
    gene_index = load_gene_tss_index(GENCODE_FILE)
    print(f"  {sum(len(v) for v in gene_index.values())} genes indexed")

    print("\n[2/4] Loading ClinVar VUS + gene submission counts...")
    vus_index, n_vus = load_vus_index(VUS_FILE)
    with open(GENE_COUNTS_FILE) as f:
        gene_counts = json.load(f)
    print(f"  {n_vus} VUS variants, {len(gene_counts)} genes with submission counts")

    print("\n[3/4] Streaming ABC predictions (calibration set: chr1-11)...")
    calib_enhancers = stream_abc_enhancers(gene_index, gene_counts, CALIBRATION_CHROMS)
    calib_buckets, calib_n = build_buckets(calib_enhancers, vus_index)
    calib_result = summarize(calib_buckets, calib_n, "calibration (chr1-11)")

    print("\n[4/4] Streaming ABC predictions (HELD-OUT set: chr12-22,X)...")
    heldout_enhancers = stream_abc_enhancers(gene_index, gene_counts, HELDOUT_CHROMS)
    heldout_buckets, heldout_n = build_buckets(heldout_enhancers, vus_index)
    heldout_result = summarize(heldout_buckets, heldout_n, "held-out (chr12-22,X)")

    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(
        f"  Calibration: OR={calib_result['mh_odds_ratio']} p={calib_result['mh_p_value']:.6f} "
        f"(n_orphan={calib_result['n_orphan']}, n_regular={calib_result['n_regular']})"
    )
    print(
        f"  Held-out:    OR={heldout_result['mh_odds_ratio']} p={heldout_result['mh_p_value']:.6f} "
        f"(n_orphan={heldout_result['n_orphan']}, n_regular={heldout_result['n_regular']})"
    )
    print()

    ho_or = heldout_result["mh_odds_ratio"] or 0.0
    ho_p = heldout_result["mh_p_value"]
    if ho_or >= 2.0 and ho_p < 0.01:
        verdict = "PROMOTE"
    elif (1.3 <= ho_or < 2.0) or (0.01 <= ho_p < 0.05):
        verdict = "REPEAT"
    else:
        verdict = "REJECT"
    print(f"VERDICT (per pre-registered go/no-go in claim.md): {verdict}")

    out = {
        "evidence": "[VERIFIED-REAL] ABC model (Nasser et al. 2021, 131 biosamples) + ClinVar VUS genome-wide 2026-07-01",
        "statistics_method": "Cochran-Mantel-Haenszel, stratified by ClinVar submission-volume bucket (none/low/medium/high)",
        "calibration": calib_result,
        "heldout": heldout_result,
        "verdict": verdict,
        "pre_registered_criteria": "PROMOTE: OR>=2.0 AND p<0.01 on held-out. REPEAT: 1.3<=OR<2.0 or 0.01<=p<0.05. REJECT: otherwise.",
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
