#!/usr/bin/env python3
"""
CTCF distance analysis + ARCHCODE-only variant clustering.

ПОЧЕМУ: Если pearl/ARCHCODE-only варианты кластеризуются ближе к CTCF сайтам —
это механистическая гипотеза: "ARCHCODE detects CTCF barrier disruption".

Analyses:
1. Distance-to-nearest-CTCF for ALL variants (per locus)
2. Compare distributions: pearl vs non-pearl, ARCHCODE+ vs ARCHCODE-
3. Distance-to-nearest-enhancer for ALL variants
4. Cluster 54 ARCHCODE-only variants by genomic context
5. CTCF proximity enrichment test

Output:
  - results/ctcf_distance_analysis.json
  - Prints key findings to stdout

Usage: python scripts/ctcf_distance_analysis.py
"""

import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
CONFIG_DIR = PROJECT_ROOT / "config" / "locus"

ATLAS_FILES = {
    "HBB":   ("HBB_Unified_Atlas_95kb.csv", "hbb_95kb_subTAD.json"),
    "CFTR":  ("CFTR_Unified_Atlas_317kb.csv", "cftr_317kb.json"),
    "TP53":  ("TP53_Unified_Atlas_300kb.csv", "tp53_300kb.json"),
    "BRCA1": ("BRCA1_Unified_Atlas_400kb.csv", "brca1_400kb.json"),
    "MLH1":  ("MLH1_Unified_Atlas_300kb.csv", "mlh1_300kb.json"),
    "LDLR":  ("LDLR_Unified_Atlas_300kb.csv", "ldlr_300kb.json"),
    "SCN5A": ("SCN5A_Unified_Atlas_400kb.csv", "scn5a_400kb.json"),
    "TERT":  ("TERT_Unified_Atlas_300kb.csv", "tert_300kb.json"),
    "GJB2":  ("GJB2_Unified_Atlas_300kb.csv", "gjb2_300kb.json"),
}


def load_features(config_path):
    """Load CTCF and enhancer positions from locus config."""
    with open(config_path) as f:
        config = json.load(f)

    ctcf_positions = []
    for site in config.get("features", {}).get("ctcf_sites", []):
        ctcf_positions.append(site["position"])

    enhancer_positions = []
    for enh in config.get("features", {}).get("enhancers", []):
        enhancer_positions.append(enh["position"])

    return ctcf_positions, enhancer_positions


def min_distance(pos, targets):
    """Minimum absolute distance from pos to any target."""
    if not targets:
        return None
    return min(abs(pos - t) for t in targets)


def mann_whitney_u(x, y):
    """Simple Mann-Whitney U test (two-sided). Returns U statistic and approximate p-value."""
    if len(x) < 2 or len(y) < 2:
        return None, None
    nx, ny = len(x), len(y)
    # Rank all values
    combined = [(v, 'x') for v in x] + [(v, 'y') for v in y]
    combined.sort(key=lambda t: t[0])
    # Assign ranks (handle ties with average rank)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based
        for k in range(i, j):
            if combined[k] not in ranks:
                ranks[combined[k]] = []
            ranks[combined[k]].append(avg_rank)
        i = j

    # Sum of ranks for x
    rank_sum_x = 0
    for v in x:
        # Find this value's rank
        for val, group in combined:
            pass  # This approach is too complex, use simpler method

    # Simpler: just compute U directly
    u = 0
    for xi in x:
        for yi in y:
            if xi < yi:
                u += 1
            elif xi == yi:
                u += 0.5

    # Normal approximation for p-value
    mu = nx * ny / 2
    sigma = (nx * ny * (nx + ny + 1) / 12) ** 0.5
    if sigma == 0:
        return u, 1.0
    z = (u - mu) / sigma
    # Two-sided p-value (approximation using error function)
    import math
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return u, p


def analyze_locus(locus, atlas_file, config_file):
    """Analyze CTCF/enhancer distance patterns for one locus."""
    atlas_path = RESULTS_DIR / atlas_file
    config_path = CONFIG_DIR / config_file

    if not atlas_path.exists() or not config_path.exists():
        return None

    ctcf_pos, enh_pos = load_features(config_path)

    with open(atlas_path) as f:
        rows = list(csv.DictReader(f))

    results = []
    for r in rows:
        pos = int(r["Position_GRCh38"])
        lssim = float(r["ARCHCODE_LSSIM"]) if r.get("ARCHCODE_LSSIM") else None
        label = r.get("Label", "")
        pearl = r.get("Pearl", "false").lower() == "true"
        category = r.get("Category", "other")
        verdict = r.get("ARCHCODE_Verdict", "")

        if lssim is None:
            continue

        dist_ctcf = min_distance(pos, ctcf_pos)
        dist_enh = min_distance(pos, enh_pos)
        archcode_pos = lssim < 0.95  # universal threshold

        results.append({
            "locus": locus,
            "clinvar_id": r["ClinVar_ID"],
            "position": pos,
            "label": label,
            "category": category,
            "lssim": lssim,
            "pearl": pearl,
            "archcode_positive": archcode_pos,
            "dist_ctcf": dist_ctcf,
            "dist_enh": dist_enh,
        })

    return results


def main():
    print("=" * 72)
    print("CTCF DISTANCE & ARCHCODE-ONLY CLUSTERING ANALYSIS")
    print("=" * 72)

    all_variants = []
    for locus, (atlas, config) in ATLAS_FILES.items():
        variants = analyze_locus(locus, atlas, config)
        if variants:
            all_variants.extend(variants)
            print(f"  {locus}: {len(variants)} variants, "
                  f"{sum(1 for v in variants if v['dist_ctcf'] is not None)} with CTCF distance")

    print(f"\nTotal: {len(all_variants)} variants across {len(ATLAS_FILES)} loci")

    # ================================================================
    # 1. ARCHCODE-positive vs negative: CTCF distance
    # ================================================================
    print(f"\n{'=' * 72}")
    print("1. CTCF DISTANCE: ARCHCODE-positive vs negative")
    print(f"{'=' * 72}")

    arch_pos = [v for v in all_variants if v["archcode_positive"] and v["dist_ctcf"] is not None]
    arch_neg = [v for v in all_variants if not v["archcode_positive"] and v["dist_ctcf"] is not None]

    if arch_pos and arch_neg:
        pos_dists = [v["dist_ctcf"] for v in arch_pos]
        neg_dists = [v["dist_ctcf"] for v in arch_neg]
        u, p = mann_whitney_u(pos_dists, neg_dists)
        print(f"  ARCHCODE+: n={len(pos_dists)}, median CTCF dist={statistics.median(pos_dists):,.0f}bp, "
              f"mean={statistics.mean(pos_dists):,.0f}bp")
        print(f"  ARCHCODE-: n={len(neg_dists)}, median CTCF dist={statistics.median(neg_dists):,.0f}bp, "
              f"mean={statistics.mean(neg_dists):,.0f}bp")
        print(f"  Mann-Whitney U p-value: {p:.2e}" if p else "  Mann-Whitney: insufficient data")

    # Per-locus breakdown
    print(f"\n  Per-locus CTCF distance (ARCHCODE+ only):")
    for locus in ATLAS_FILES:
        locus_pos = [v for v in arch_pos if v["locus"] == locus]
        if locus_pos:
            dists = [v["dist_ctcf"] for v in locus_pos]
            print(f"    {locus:6s}: n={len(dists):4d}, median={statistics.median(dists):>8,.0f}bp, "
                  f"mean={statistics.mean(dists):>8,.0f}bp, min={min(dists):>6,.0f}bp")

    # ================================================================
    # 2. Pearl variants: CTCF & enhancer proximity
    # ================================================================
    print(f"\n{'=' * 72}")
    print("2. PEARL VARIANTS: CTCF & ENHANCER PROXIMITY")
    print(f"{'=' * 72}")

    pearls = [v for v in all_variants if v["pearl"]]
    non_pearls_path = [v for v in all_variants if not v["pearl"]
                       and v["label"] == "Pathogenic" and v["dist_ctcf"] is not None]

    if pearls:
        pearl_ctcf = [v["dist_ctcf"] for v in pearls if v["dist_ctcf"] is not None]
        pearl_enh = [v["dist_enh"] for v in pearls if v["dist_enh"] is not None]
        nonp_ctcf = [v["dist_ctcf"] for v in non_pearls_path]

        print(f"  Pearls (n={len(pearls)}):")
        if pearl_ctcf:
            print(f"    CTCF distance: median={statistics.median(pearl_ctcf):,.0f}bp, "
                  f"mean={statistics.mean(pearl_ctcf):,.0f}bp")
            # Zones
            z1 = sum(1 for d in pearl_ctcf if d <= 1000)
            z2 = sum(1 for d in pearl_ctcf if 1000 < d <= 5000)
            z3 = sum(1 for d in pearl_ctcf if 5000 < d <= 10000)
            z4 = sum(1 for d in pearl_ctcf if d > 10000)
            print(f"    ≤1kb: {z1}, 1-5kb: {z2}, 5-10kb: {z3}, >10kb: {z4}")
        if pearl_enh:
            print(f"    Enhancer distance: median={statistics.median(pearl_enh):,.0f}bp, "
                  f"mean={statistics.mean(pearl_enh):,.0f}bp")

        if nonp_ctcf and pearl_ctcf:
            print(f"\n  Non-pearl Pathogenic (n={len(nonp_ctcf)}):")
            print(f"    CTCF distance: median={statistics.median(nonp_ctcf):,.0f}bp, "
                  f"mean={statistics.mean(nonp_ctcf):,.0f}bp")
            u, p = mann_whitney_u(pearl_ctcf, nonp_ctcf)
            print(f"  Pearl vs Non-pearl Path Mann-Whitney p: {p:.2e}" if p else "  Insufficient data")

    # ================================================================
    # 3. ARCHCODE-only variants (LSSIM < 0.95, CADD < 20)
    # ================================================================
    print(f"\n{'=' * 72}")
    print("3. ARCHCODE-ONLY VARIANT CLUSTERING")
    print(f"{'=' * 72}")

    # Load CADD data from integrative benchmark
    benchmark_path = RESULTS_DIR / "integrative_benchmark.csv"
    cadd_map = {}
    if benchmark_path.exists():
        with open(benchmark_path) as f:
            for r in csv.DictReader(f):
                cid = r["ClinVar_ID"]
                cadd = r.get("CADD_Phred", "NA")
                if cadd not in ("NA", ""):
                    try:
                        cadd_map[cid] = float(cadd)
                    except ValueError:
                        pass

    # Find ARCHCODE-only: LSSIM < 0.95 AND (no CADD or CADD < 20)
    archcode_only = []
    for v in all_variants:
        if v["lssim"] < 0.95:
            cadd = cadd_map.get(v["clinvar_id"])
            if cadd is None or cadd < 20:
                v["cadd"] = cadd
                archcode_only.append(v)

    print(f"  ARCHCODE-only variants (LSSIM<0.95, CADD<20 or NA): {len(archcode_only)}")

    # Group by locus
    by_locus = defaultdict(list)
    for v in archcode_only:
        by_locus[v["locus"]].append(v)

    print(f"\n  By locus:")
    for locus in ATLAS_FILES:
        variants = by_locus.get(locus, [])
        if not variants:
            continue
        n_path = sum(1 for v in variants if v["label"] == "Pathogenic")
        n_ben = sum(1 for v in variants if v["label"] == "Benign")
        cats = defaultdict(int)
        for v in variants:
            cats[v["category"]] += 1
        cat_str = ", ".join(f"{c}:{n}" for c, n in sorted(cats.items(), key=lambda x: -x[1]))
        ctcf_dists = [v["dist_ctcf"] for v in variants if v["dist_ctcf"] is not None]
        median_ctcf = f"{statistics.median(ctcf_dists):,.0f}bp" if ctcf_dists else "N/A"
        print(f"    {locus:6s}: {len(variants):3d} ({n_path}P/{n_ben}B) "
              f"median CTCF={median_ctcf} [{cat_str}]")

    # True Positives vs False Positives analysis
    print(f"\n  True Positive vs False Positive Pattern:")
    tp = [v for v in archcode_only if v["label"] == "Pathogenic"]
    fp = [v for v in archcode_only if v["label"] == "Benign"]

    if tp:
        tp_ctcf = [v["dist_ctcf"] for v in tp if v["dist_ctcf"] is not None]
        tp_enh = [v["dist_enh"] for v in tp if v["dist_enh"] is not None]
        tp_cats = defaultdict(int)
        for v in tp:
            tp_cats[v["category"]] += 1
        print(f"    TRUE POSITIVES (Path, n={len(tp)}):")
        if tp_ctcf:
            print(f"      CTCF distance: median={statistics.median(tp_ctcf):,.0f}bp, "
                  f"mean={statistics.mean(tp_ctcf):,.0f}bp")
        if tp_enh:
            print(f"      Enhancer dist: median={statistics.median(tp_enh):,.0f}bp, "
                  f"mean={statistics.mean(tp_enh):,.0f}bp")
        print(f"      Categories: {dict(tp_cats)}")
        print(f"      Loci: {dict(defaultdict(int, {v['locus']: 1 for v in tp}))}")
        locus_counts = defaultdict(int)
        for v in tp:
            locus_counts[v["locus"]] += 1
        print(f"      Loci: {dict(locus_counts)}")

    if fp:
        fp_ctcf = [v["dist_ctcf"] for v in fp if v["dist_ctcf"] is not None]
        fp_enh = [v["dist_enh"] for v in fp if v["dist_enh"] is not None]
        fp_cats = defaultdict(int)
        for v in fp:
            fp_cats[v["category"]] += 1
        print(f"    FALSE POSITIVES (Ben, n={len(fp)}):")
        if fp_ctcf:
            print(f"      CTCF distance: median={statistics.median(fp_ctcf):,.0f}bp, "
                  f"mean={statistics.mean(fp_ctcf):,.0f}bp")
        if fp_enh:
            print(f"      Enhancer dist: median={statistics.median(fp_enh):,.0f}bp, "
                  f"mean={statistics.mean(fp_enh):,.0f}bp")
        print(f"      Categories: {dict(fp_cats)}")
        locus_counts = defaultdict(int)
        for v in fp:
            locus_counts[v["locus"]] += 1
        print(f"      Loci: {dict(locus_counts)}")

    if tp and fp:
        tp_ctcf = [v["dist_ctcf"] for v in tp if v["dist_ctcf"] is not None]
        fp_ctcf = [v["dist_ctcf"] for v in fp if v["dist_ctcf"] is not None]
        if tp_ctcf and fp_ctcf:
            u, p = mann_whitney_u(tp_ctcf, fp_ctcf)
            print(f"\n    TP vs FP CTCF distance Mann-Whitney p: {p:.2e}" if p else "")

    # ================================================================
    # 4. Distance-to-CTCF vs LSSIM correlation (all variants)
    # ================================================================
    print(f"\n{'=' * 72}")
    print("4. CTCF DISTANCE vs LSSIM (global pattern)")
    print(f"{'=' * 72}")

    # Bin variants by CTCF distance
    bins = [(0, 1000, "≤1kb"), (1000, 5000, "1-5kb"), (5000, 10000, "5-10kb"),
            (10000, 50000, "10-50kb"), (50000, 999999999, ">50kb")]

    print(f"  {'Zone':10s} {'N':>6s} {'Mean LSSIM':>11s} {'Path LSSIM':>11s} {'Ben LSSIM':>10s} {'Δ':>8s}")
    print(f"  {'─'*60}")

    for lo, hi, label in bins:
        zone_v = [v for v in all_variants if v["dist_ctcf"] is not None and lo <= v["dist_ctcf"] < hi]
        if not zone_v:
            continue
        all_lssim = [v["lssim"] for v in zone_v]
        path_l = [v["lssim"] for v in zone_v if v["label"] == "Pathogenic"]
        ben_l = [v["lssim"] for v in zone_v if v["label"] == "Benign"]
        delta = (statistics.mean(ben_l) - statistics.mean(path_l)) if path_l and ben_l else 0
        p_str = f"{statistics.mean(path_l):.6f}" if path_l else "N/A"
        b_str = f"{statistics.mean(ben_l):.6f}" if ben_l else "N/A"
        print(f"  {label:10s} {len(zone_v):>6d} {statistics.mean(all_lssim):>11.6f} "
              f"{p_str:>11s} {b_str:>10s} {delta:>8.4f}")

    # ================================================================
    # 5. Enhancer distance vs LSSIM
    # ================================================================
    print(f"\n{'=' * 72}")
    print("5. ENHANCER DISTANCE vs LSSIM (global pattern)")
    print(f"{'=' * 72}")

    enh_bins = [(0, 1000, "≤1kb"), (1000, 5000, "1-5kb"), (5000, 20000, "5-20kb"),
                (20000, 50000, "20-50kb"), (50000, 999999999, ">50kb")]

    print(f"  {'Zone':10s} {'N':>6s} {'Mean LSSIM':>11s} {'Path LSSIM':>11s} {'Ben LSSIM':>10s} {'Δ':>8s}")
    print(f"  {'─'*60}")

    for lo, hi, label in enh_bins:
        zone_v = [v for v in all_variants if v["dist_enh"] is not None and lo <= v["dist_enh"] < hi]
        if not zone_v:
            continue
        all_lssim = [v["lssim"] for v in zone_v]
        path_l = [v["lssim"] for v in zone_v if v["label"] == "Pathogenic"]
        ben_l = [v["lssim"] for v in zone_v if v["label"] == "Benign"]
        delta = (statistics.mean(ben_l) - statistics.mean(path_l)) if path_l and ben_l else 0
        p_str = f"{statistics.mean(path_l):.6f}" if path_l else "N/A"
        b_str = f"{statistics.mean(ben_l):.6f}" if ben_l else "N/A"
        print(f"  {label:10s} {len(zone_v):>6d} {statistics.mean(all_lssim):>11.6f} "
              f"{p_str:>11s} {b_str:>10s} {delta:>8.4f}")

    # Save results
    summary = {
        "total_variants": len(all_variants),
        "archcode_only_count": len(archcode_only),
        "archcode_only_by_locus": {
            locus: len(variants) for locus, variants in by_locus.items()
        },
        "archcode_only_tp": len(tp),
        "archcode_only_fp": len(fp),
    }

    if tp:
        tp_ctcf = [v["dist_ctcf"] for v in tp if v["dist_ctcf"] is not None]
        if tp_ctcf:
            summary["tp_ctcf_median"] = round(statistics.median(tp_ctcf))
            summary["tp_ctcf_mean"] = round(statistics.mean(tp_ctcf))

    if fp:
        fp_ctcf = [v["dist_ctcf"] for v in fp if v["dist_ctcf"] is not None]
        if fp_ctcf:
            summary["fp_ctcf_median"] = round(statistics.median(fp_ctcf))
            summary["fp_ctcf_mean"] = round(statistics.mean(fp_ctcf))

    output_json = RESULTS_DIR / "ctcf_distance_analysis.json"
    with open(output_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nJSON saved: {output_json}")


if __name__ == "__main__":
    main()
