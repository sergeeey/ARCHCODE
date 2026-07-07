#!/usr/bin/env python3
"""exp_synonymous_codon_optimality: does Delta codon-usage-frequency (ALT minus
REF codon, Kazusa human table) discriminate ClinVar Pathogenic from Benign
synonymous SNVs? Pre-registered in claim.md BEFORE this script produced any
results: Mann-Whitney U (primary, all variants) + Cliff's delta effect size,
plus one pre-registered sensitivity check (restrict to >=10bp from nearest
GENCODE exon/intron boundary, to reduce splice-driven confounding), BH-FDR
corrected across the 2 tests.
"""

import bisect
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_FILE = ROOT / "data/input/clinvar_synonymous_variants.json"
CODON_USAGE_FILE = ROOT / "data/input/codon_usage_human_kazusa.json"
EXON_BOUNDARIES_FILE = ROOT / "data/input/gencode_exon_boundaries_hg19.json"
VEP_CACHE_FILE = ROOT / "data/input/vep_codons_cache_synonymous.json"
RESULTS_FILE = ROOT / "experiments/exp_synonymous_codon_optimality/results.json"

VEP_URL = "https://grch37.rest.ensembl.org/vep/homo_sapiens/region"
VEP_BATCH_SIZE = 150
SPLICE_DISTANCE_THRESHOLD_BP = 10
# Pre-registered in claim.md addendum (2026-07-07), before any VEP call or test statistic:
# genome-wide fetch found 829 pathogenic vs 685,044 benign -- subsample benign for VEP budget.
BENIGN_SAMPLE_SIZE = 5000
BENIGN_SAMPLE_SEED = 42

VALID_BASES = set("ACGTN")


def valid_snv_fields(v):
    pos, ref, alt = v.get("position_vcf"), v.get("ref_vcf"), v.get("alt_vcf")
    if not (pos and ref and alt):
        return False
    try:
        if int(pos) <= 0:
            return False
    except (TypeError, ValueError):
        return False
    if not all(c in VALID_BASES for c in ref.upper()):
        return False
    if not all(c in VALID_BASES for c in alt.upper()):
        return False
    return len(ref) == 1 and len(alt) == 1  # true SNV, not MNV


def vep_query_batch(variant_strings):
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
            out = {}
            for r in results:
                codons = None
                for tc in r.get("transcript_consequences", []):
                    if "synonymous_variant" in tc.get("consequence_terms", []) and tc.get("codons"):
                        codons = tc["codons"]
                        break
                if codons is None:
                    for tc in r.get("transcript_consequences", []):
                        if tc.get("codons"):
                            codons = tc["codons"]
                            break
                out[r.get("input")] = codons
            return [out.get(v) for v in variant_strings]
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


def annotate_codons(all_variants):
    """all_variants: list of vstr. Returns {vstr: 'cGc/cAc' or None}.
    Resumable: loads any partial cache from a prior interrupted run and only
    queries the remaining unique variants; saves incrementally every batch so
    an interruption never loses more than one batch of work."""
    cache = {}
    if VEP_CACHE_FILE.exists():
        with open(VEP_CACHE_FILE) as f:
            cache = json.load(f)
        print(f"  Resuming from partial VEP cache: {len(cache)} variants already annotated")

    unique = sorted(set(all_variants))
    remaining = [v for v in unique if v not in cache]
    print(
        f"  Querying VEP for {len(remaining)} remaining unique variants "
        f"(of {len(unique)} total) in batches of {VEP_BATCH_SIZE}..."
    )
    for i in range(0, len(remaining), VEP_BATCH_SIZE):
        batch = remaining[i : i + VEP_BATCH_SIZE]
        codons = vep_query_batch(batch)
        for vstr, c in zip(batch, codons):
            cache[vstr] = c
        with open(VEP_CACHE_FILE, "w") as f:
            json.dump(cache, f)
        print(
            f"    ...{len(cache)}/{len(unique)} annotated (cache saved)",
            file=sys.stderr,
        )
        time.sleep(0.34)

    with open(VEP_CACHE_FILE, "w") as f:
        json.dump(cache, f)
    print(f"  Saved VEP codons cache: {VEP_CACHE_FILE}")
    return cache


def delta_usage(codons_str, usage_table):
    if not codons_str or "/" not in codons_str:
        return None
    ref_raw, alt_raw = codons_str.split("/")
    ref_codon, alt_codon = ref_raw.upper(), alt_raw.upper()
    ref_entry = usage_table.get(ref_codon)
    alt_entry = usage_table.get(alt_codon)
    if not ref_entry or not alt_entry:
        return None
    return alt_entry["per_thousand"] - ref_entry["per_thousand"]


def distance_to_nearest_boundary(chrom, pos, boundaries_by_chrom):
    positions = boundaries_by_chrom.get(chrom)
    if not positions:
        return None
    i = bisect.bisect_left(positions, pos)
    candidates = []
    if i < len(positions):
        candidates.append(abs(positions[i] - pos))
    if i > 0:
        candidates.append(abs(pos - positions[i - 1]))
    return min(candidates) if candidates else None


def mann_whitney_u(group1, group2):
    """Two-sided Mann-Whitney U test (normal approximation), no scipy dependency.
    Returns (U1, p_value, cliffs_delta)."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return float("nan"), float("nan"), float("nan")
    combined = [(d, 0) for d in group1] + [(d, 1) for d in group2]
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
    cliffs_delta = (2 * u1 / (n1 * n2)) - 1
    if sigma == 0:
        return u1, float("nan"), cliffs_delta
    z = (u1 - mu) / sigma
    p = math.erfc(abs(z) / math.sqrt(2))
    return u1, p, cliffs_delta


def benjamini_hochberg(p_values):
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


def main():
    with open(CLINVAR_FILE) as f:
        clinvar = json.load(f)
    with open(CODON_USAGE_FILE) as f:
        usage_table = json.load(f)["codons"]
    with open(EXON_BOUNDARIES_FILE) as f:
        boundaries_by_chrom = json.load(f)["boundaries_by_chrom"]

    path_variants = clinvar["variants"]["pathogenic"]
    benign_variants_full = clinvar["variants"]["benign"]
    print(
        f"Loaded {len(path_variants)} pathogenic, {len(benign_variants_full)} benign "
        f"synonymous ClinVar SNVs (full population)"
    )
    if len(benign_variants_full) > BENIGN_SAMPLE_SIZE:
        benign_variants = random.Random(BENIGN_SAMPLE_SEED).sample(
            benign_variants_full, BENIGN_SAMPLE_SIZE
        )
        print(
            f"  Subsampled benign to {len(benign_variants)} "
            f"(seed={BENIGN_SAMPLE_SEED}, pre-registered in claim.md addendum)"
        )
    else:
        benign_variants = benign_variants_full

    def vstr(v):
        chrom_num = v["chrom"].replace("chr", "")
        return f"{chrom_num} {v['position_vcf']} . {v['ref_vcf']} {v['alt_vcf']} . . ."

    all_vstrs = []
    for v in path_variants + benign_variants:
        if valid_snv_fields(v):
            all_vstrs.append(vstr(v))

    codons_cache = annotate_codons(all_vstrs)

    def build_records(variants):
        records = []
        n_no_codons = n_no_boundary = 0
        for v in variants:
            if not valid_snv_fields(v):
                continue
            codons_str = codons_cache.get(vstr(v))
            du = delta_usage(codons_str, usage_table)
            if du is None:
                n_no_codons += 1
                continue
            pos = int(v["position_vcf"])
            dist = distance_to_nearest_boundary(v["chrom"], pos, boundaries_by_chrom)
            if dist is None:
                n_no_boundary += 1
                continue
            records.append(
                {"delta_usage": du, "boundary_distance": dist, "gene": v.get("gene_symbol")}
            )
        print(
            f"    excluded: {n_no_codons} no codons/usage match, {n_no_boundary} no boundary data"
        )
        return records

    path_records = build_records(path_variants)
    benign_records = build_records(benign_variants)
    print(
        f"Annotated: {len(path_records)} pathogenic, {len(benign_records)} benign (usable records)"
    )

    # Primary test: all annotated variants
    path_du_all = [r["delta_usage"] for r in path_records]
    benign_du_all = [r["delta_usage"] for r in benign_records]
    u_primary, p_primary, delta_primary = mann_whitney_u(path_du_all, benign_du_all)

    # Sensitivity check: restrict to >=10bp from nearest exon/intron boundary
    path_du_far = [
        r["delta_usage"]
        for r in path_records
        if r["boundary_distance"] >= SPLICE_DISTANCE_THRESHOLD_BP
    ]
    benign_du_far = [
        r["delta_usage"]
        for r in benign_records
        if r["boundary_distance"] >= SPLICE_DISTANCE_THRESHOLD_BP
    ]
    u_sens, p_sens, delta_sens = mann_whitney_u(path_du_far, benign_du_far)

    p_adj = benjamini_hochberg([p_primary, p_sens])

    def median(xs):
        s = sorted(xs)
        n = len(s)
        if n == 0:
            return None
        mid = n // 2
        return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2.0

    results = {
        "n_pathogenic_total": len(path_variants),
        "n_benign_total": len(benign_variants),
        "primary": {
            "n_pathogenic": len(path_du_all),
            "n_benign": len(benign_du_all),
            "median_delta_usage_pathogenic": median(path_du_all),
            "median_delta_usage_benign": median(benign_du_all),
            "mann_whitney_U": u_primary,
            "p_value": p_primary,
            "cliffs_delta": delta_primary,
            "p_value_bh": p_adj[0],
        },
        "sensitivity_splice_distance_ge_10bp": {
            "n_pathogenic": len(path_du_far),
            "n_benign": len(benign_du_far),
            "median_delta_usage_pathogenic": median(path_du_far),
            "median_delta_usage_benign": median(benign_du_far),
            "mann_whitney_U": u_sens,
            "p_value": p_sens,
            "cliffs_delta": delta_sens,
            "p_value_bh": p_adj[1],
        },
        "mcid": "abs(cliffs_delta) >= 0.2 AND p_value_bh < 0.05",
    }

    print(json.dumps(results, indent=2))

    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
