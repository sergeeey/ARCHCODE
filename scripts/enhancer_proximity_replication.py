#!/usr/bin/env python3
"""
exp_enhancer_proximity_replication: does distance to nearest K562 H3K27ac enhancer
discriminate ClinVar Pathogenic from Benign variants at BCL11A, KLF1, GATA1?

Pre-registered in claim.md BEFORE this script produced any results:
  - Per-locus analysis (BCL11A, KLF1, GATA1 tested INDEPENDENTLY, not pooled)
  - Category-matched control (VEP most_severe_consequence, via Ensembl VEP GRCh37 REST API)
  - Summary measures: Mann-Whitney U (continuous distance) + CMH odds ratio at 1kb
  - Benjamini-Hochberg FDR correction across the 3 loci
  - MCID: OR>=3 AND FDR-p<0.05 per locus for PROMOTE

Lesson applied from the original SNV pipeline's category-confound failure: variant
category (missense/nonsense/synonymous/intronic/etc.) is fetched from real VEP
annotation BEFORE any distance/enrichment analysis, and used to stratify the test --
not retrofitted after seeing a naive pooled result.
"""

import bisect
import gzip
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_FILE = ROOT / "data/input/clinvar_erythroid_loci_hg19.json"
H3K27AC_FILE = ROOT / "data/encode_cache/ENCFF252DWA_H3K27ac_K562_hg19.bed.gz"
VEP_CACHE_FILE = ROOT / "data/input/vep_annotations_erythroid_loci_cache.json"
RESULTS_FILE = ROOT / "experiments/exp_enhancer_proximity_replication/results.json"

VEP_URL = "https://grch37.rest.ensembl.org/vep/homo_sapiens/region"
VEP_BATCH_SIZE = 150
PROXIMITY_THRESHOLD_BP = 1000


def load_h3k27ac_peaks():
    by_chrom = defaultdict(list)
    with gzip.open(H3K27AC_FILE, "rt") as f:
        for line in f:
            cols = line.rstrip("\n").split("\t")
            chrom, start, end = cols[0], int(cols[1]), int(cols[2])
            by_chrom[chrom].append((start, end))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return by_chrom


def distance_to_nearest_peak(chrom, pos, peaks_index):
    peaks = peaks_index.get(chrom)
    if not peaks:
        return None
    starts = [p[0] for p in peaks]
    i = bisect.bisect_left(starts, pos)
    candidates = []
    for j in (i - 1, i):
        if 0 <= j < len(peaks):
            p_start, p_end = peaks[j]
            if p_start <= pos <= p_end:
                candidates.append(0)
            else:
                candidates.append(min(abs(pos - p_start), abs(pos - p_end)))
    return min(candidates) if candidates else None


VALID_BASES = set("ACGTN")


def valid_snv_fields(v):
    """True if position_vcf/ref_vcf/alt_vcf form a well-formed simple substitution
    VEP can parse -- filters out ClinVar CNV/large-SV rows that report position_vcf=-1,
    ref_vcf=alt_vcf="na" (these break the whole VEP batch request if included)."""
    pos, ref, alt = v.get("position_vcf"), v.get("ref_vcf"), v.get("alt_vcf")
    if not (pos and ref and alt):
        return False
    try:
        if int(pos) <= 0:
            return False
    except (TypeError, ValueError):
        return False
    if not ref or not alt:
        return False
    if not all(c in VALID_BASES for c in ref.upper()):
        return False
    if not all(c in VALID_BASES for c in alt.upper()):
        return False
    return True


def vep_query_batch(variant_strings):
    """POST a batch to Ensembl VEP GRCh37 REST API, return list of most_severe_consequence
    aligned to input order (or None on failure for that variant)."""
    payload = json.dumps({"variants": variant_strings}).encode()
    req = urllib.request.Request(
        VEP_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                results = json.loads(resp.read())
            by_input = {r.get("input"): r.get("most_severe_consequence") for r in results}
            return [by_input.get(v) for v in variant_strings]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2**attempt)
                continue
            print(f"    VEP HTTPError {e.code}: {e.read()[:300]}", file=sys.stderr)
            return [None] * len(variant_strings)
        except Exception as e:
            print(f"    VEP error: {e}", file=sys.stderr)
            time.sleep(1)
    return [None] * len(variant_strings)


def annotate_with_vep(clinvar_data):
    """Fetch (or load cached) most_severe_consequence for every variant with a valid
    PositionVCF/ref/alt triple, across all 3 loci."""
    if VEP_CACHE_FILE.exists():
        print(f"  VEP cache found: {VEP_CACHE_FILE}")
        with open(VEP_CACHE_FILE) as f:
            return json.load(f)

    cache = {}
    all_variants = []
    for _locus, groups in clinvar_data["variants"].items():
        for sig_group in ("pathogenic", "benign"):
            for v in groups[sig_group]:
                if not valid_snv_fields(v):
                    continue
                chrom_num = v["chrom"].replace("chr", "")
                vstr = f"{chrom_num} {v['position_vcf']} . {v['ref_vcf']} {v['alt_vcf']} . . ."
                all_variants.append(vstr)

    all_variants = sorted(set(all_variants))
    print(
        f"  Querying VEP for {len(all_variants)} unique variants in batches of {VEP_BATCH_SIZE}..."
    )

    for i in range(0, len(all_variants), VEP_BATCH_SIZE):
        batch = all_variants[i : i + VEP_BATCH_SIZE]
        consequences = vep_query_batch(batch)
        for vstr, cons in zip(batch, consequences):
            cache[vstr] = cons
        print(
            f"    ...{min(i + VEP_BATCH_SIZE, len(all_variants))}/{len(all_variants)} annotated",
            file=sys.stderr,
        )
        time.sleep(0.34)  # be polite to Ensembl's rate limit (~3 req/s)

    with open(VEP_CACHE_FILE, "w") as f:
        json.dump(cache, f)
    print(f"  Saved VEP cache: {VEP_CACHE_FILE}")
    return cache


def cochran_mantel_haenszel(buckets):
    num_or = den_or = num_stat = var_stat = 0.0
    for b in buckets.values():
        a, b_, c, d = b["path_close"], b["path_far"], b["benign_close"], b["benign_far"]
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
    chi2 = max(0.0, abs(num_stat) - 0.5) ** 2 / var_stat
    p_value = math.erfc(math.sqrt(chi2 / 2))
    return mh_or, p_value


def mann_whitney_u(path_dists, benign_dists):
    """Two-sided Mann-Whitney U test (normal approximation), no scipy dependency."""
    n1, n2 = len(path_dists), len(benign_dists)
    if n1 == 0 or n2 == 0:
        return float("nan"), float("nan")
    combined = [(d, 0) for d in path_dists] + [(d, 1) for d in benign_dists]
    combined.sort(key=lambda x: x[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    if sigma == 0:
        return u1, float("nan")
    z = (u1 - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2))
    return u1, p


def benjamini_hochberg(p_values):
    """Return FDR-adjusted p-values (BH procedure)."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    adjusted = [0.0] * n
    prev = 1.0
    for rank, (idx, p) in enumerate(reversed(indexed), start=1):
        bh_rank = n - rank + 1
        val = min(prev, p * n / bh_rank)
        adjusted[idx] = val
        prev = val
    return adjusted


def analyze_locus(locus_name, path_variants, benign_variants, vep_cache, peaks_index):
    def get_consequence(v):
        if not valid_snv_fields(v):
            return None
        chrom_num = v["chrom"].replace("chr", "")
        vstr = f"{chrom_num} {v['position_vcf']} . {v['ref_vcf']} {v['alt_vcf']} . . ."
        return vep_cache.get(vstr)

    def get_distance(v):
        pos = int(v["position_vcf"]) if v.get("position_vcf") else (v["start"] + v["end"]) // 2
        return distance_to_nearest_peak(v["chrom"], pos, peaks_index)

    path_records, benign_records = [], []
    for v in path_variants:
        d = get_distance(v)
        c = get_consequence(v)
        if d is not None and c is not None:
            path_records.append({"distance": d, "consequence": c})
    for v in benign_variants:
        d = get_distance(v)
        c = get_consequence(v)
        if d is not None and c is not None:
            benign_records.append({"distance": d, "consequence": c})

    print(
        f"  [{locus_name}] annotated: {len(path_records)} pathogenic, {len(benign_records)} benign"
    )

    path_dists = [r["distance"] for r in path_records]
    benign_dists = [r["distance"] for r in benign_records]
    u_stat, mw_p = mann_whitney_u(path_dists, benign_dists)

    buckets = defaultdict(
        lambda: {"path_close": 0, "path_far": 0, "benign_close": 0, "benign_far": 0}
    )
    for r in path_records:
        b = buckets[r["consequence"]]
        if r["distance"] <= PROXIMITY_THRESHOLD_BP:
            b["path_close"] += 1
        else:
            b["path_far"] += 1
    for r in benign_records:
        b = buckets[r["consequence"]]
        if r["distance"] <= PROXIMITY_THRESHOLD_BP:
            b["benign_close"] += 1
        else:
            b["benign_far"] += 1

    mh_or, cmh_p = cochran_mantel_haenszel(buckets)

    return {
        "locus": locus_name,
        "n_pathogenic": len(path_records),
        "n_benign": len(benign_records),
        "median_dist_pathogenic": sorted(path_dists)[len(path_dists) // 2] if path_dists else None,
        "median_dist_benign": sorted(benign_dists)[len(benign_dists) // 2]
        if benign_dists
        else None,
        "mann_whitney_u": u_stat,
        "mann_whitney_p": mw_p,
        "cmh_odds_ratio": round(mh_or, 4) if mh_or == mh_or else None,
        "cmh_p": cmh_p,
        "consequence_bucket_breakdown": dict(buckets),
    }


def main():
    print("=" * 60)
    print("exp_enhancer_proximity_replication: BCL11A / KLF1 / GATA1")
    print("=" * 60)

    print("\n[1/4] Loading ClinVar erythroid-loci variants...")
    with open(CLINVAR_FILE) as f:
        clinvar_data = json.load(f)

    print("\n[2/4] Loading K562 H3K27ac peaks (hg19, ENCFF252DWA)...")
    peaks_index = load_h3k27ac_peaks()
    n_peaks = sum(len(v) for v in peaks_index.values())
    print(f"  {n_peaks} peaks loaded")

    print("\n[3/4] Annotating variants with Ensembl VEP (GRCh37 REST API)...")
    vep_cache = annotate_with_vep(clinvar_data)
    print(f"  {len(vep_cache)} variants in VEP cache")

    print("\n[4/4] Per-locus analysis...")
    locus_results = []
    for locus_name in ("BCL11A", "KLF1", "GATA1"):
        groups = clinvar_data["variants"][locus_name]
        result = analyze_locus(
            locus_name, groups["pathogenic"], groups["benign"], vep_cache, peaks_index
        )
        locus_results.append(result)
        print(
            f"  [{locus_name}] median_dist path={result['median_dist_pathogenic']} benign={result['median_dist_benign']} "
            f"MW-p={result['mann_whitney_p']:.4f} CMH-OR={result['cmh_odds_ratio']} CMH-p={result['cmh_p']:.4f}"
        )

    mw_p_values = [r["mann_whitney_p"] for r in locus_results]
    fdr_adjusted = benjamini_hochberg(mw_p_values)
    for r, fdr_p in zip(locus_results, fdr_adjusted):
        r["mann_whitney_fdr_p"] = fdr_p

    print(f"\n{'=' * 60}")
    print("RESULTS (per-locus, FDR-corrected across 3 loci)")
    n_promote = 0
    for r in locus_results:
        or_val = r["cmh_odds_ratio"] or 0
        meets_mcid = or_val >= 3 and r["mann_whitney_fdr_p"] < 0.05
        if meets_mcid:
            n_promote += 1
        print(
            f"  {r['locus']}: OR={r['cmh_odds_ratio']} FDR-p={r['mann_whitney_fdr_p']:.4f} "
            f"{'MEETS MCID' if meets_mcid else 'does not meet MCID'}"
        )

    if n_promote >= 2:
        verdict = "PROMOTE"
    elif n_promote == 1:
        verdict = "REPEAT"
    else:
        verdict = "REJECT"
    print(
        f"\nVERDICT (per pre-registered go/no-go in claim.md): {verdict} ({n_promote}/3 loci meet MCID)"
    )

    out = {
        "evidence": "[VERIFIED-REAL] ClinVar 2026-07-02 + ENCODE K562 H3K27ac (ENCFF252DWA, hg19) + Ensembl VEP GRCh37 REST",
        "pre_registered_criteria": "PROMOTE: >=2/3 loci meet OR>=3 AND FDR-p<0.05. REPEAT: 1/3. REJECT: 0/3.",
        "proximity_threshold_bp": PROXIMITY_THRESHOLD_BP,
        "locus_results": locus_results,
        "n_loci_meeting_mcid": n_promote,
        "verdict": verdict,
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
