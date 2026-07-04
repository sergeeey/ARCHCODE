#!/usr/bin/env python3
"""
Fetch CADD v1.7 scores for all ARCHCODE variants via Ensembl VEP REST API.

ПОЧЕМУ Ensembl VEP, а не прямой CADD API:
- VEP API поддерживает батчи по 200 вариантов (vs 1 позиция у CADD API)
- VEP возвращает CADD для SNVs И indels
- Прямой CADD API = "experimental", не для тысяч вариантов

Usage:
    python scripts/fetch_cadd_scores.py                 # all loci
    python scripts/fetch_cadd_scores.py --locus CFTR     # single locus
    python scripts/fetch_cadd_scores.py --resume         # resume from cache

Output: results/cadd_scores_<LOCUS>.csv for each locus
"""

import csv
import json
import time
import argparse
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
CACHE_DIR = PROJECT_ROOT / "data" / "cadd_cache"

VEP_POST_URL = "https://rest.ensembl.org/vep/human/region"
BATCH_SIZE = 200  # Ensembl limit
RATE_LIMIT_PAUSE = 1.0  # seconds between batches

# Unified atlas files — source of truth for all variants
LOCI = {
    "CFTR":  {"file": "CFTR_Unified_Atlas_317kb.csv",  "chrom": "7"},
    "TP53":  {"file": "TP53_Unified_Atlas_300kb.csv",   "chrom": "17"},
    "BRCA1": {"file": "BRCA1_Unified_Atlas_400kb.csv",  "chrom": "17"},
    "MLH1":  {"file": "MLH1_Unified_Atlas_300kb.csv",   "chrom": "3"},
    "LDLR":  {"file": "LDLR_Unified_Atlas_300kb.csv",   "chrom": "19"},
    "SCN5A": {"file": "SCN5A_Unified_Atlas_400kb.csv",  "chrom": "3"},
    "TERT":  {"file": "TERT_Unified_Atlas_300kb.csv",   "chrom": "5"},
    "GJB2":  {"file": "GJB2_Unified_Atlas_300kb.csv",   "chrom": "13"},
}
# HBB already scored — skip


def load_cache(locus: str) -> dict:
    cache_file = CACHE_DIR / f"cadd_cache_{locus}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return {}


def save_cache(locus: str, cache: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_DIR / f"cadd_cache_{locus}.json", "w") as f:
        json.dump(cache, f)


def variant_to_vep_input(chrom: str, pos: str, ref: str, alt: str) -> str | None:
    """Convert to Ensembl VEP input format: 'chr start end allele_string strand'."""
    pos_int = int(pos)

    if len(ref) == 1 and len(alt) == 1:
        return f"{chrom} {pos_int} {pos_int} {ref}/{alt} 1"
    elif len(ref) > len(alt):
        # Deletion
        deleted = ref[len(alt):]
        start = pos_int + len(alt)
        end = start + len(deleted) - 1
        return f"{chrom} {start} {end} {deleted}/- 1"
    elif len(alt) > len(ref):
        # Insertion
        inserted = alt[len(ref):]
        start = pos_int + len(ref) - 1
        return f"{chrom} {start} {start + 1} -/{inserted} 1"
    else:
        # MNV
        end = pos_int + len(ref) - 1
        return f"{chrom} {pos_int} {end} {ref}/{alt} 1"


def extract_cadd_from_vep(result: dict) -> tuple[float | None, float | None]:
    """Extract CADD phred and raw scores from VEP response."""
    for key in ("transcript_consequences", "intergenic_consequences",
                "regulatory_feature_consequences", "motif_feature_consequences"):
        for item in result.get(key, []):
            if "cadd_phred" in item:
                return item["cadd_phred"], item.get("cadd_raw")
    return None, None


def fetch_batch(variants: list[dict], chrom: str) -> dict[str, dict]:
    """Fetch CADD scores for a batch of variants via Ensembl VEP."""
    vep_inputs = []
    input_to_id = {}

    for v in variants:
        vep_str = variant_to_vep_input(chrom, v["pos"], v["ref"], v["alt"])
        if vep_str:
            vep_inputs.append(vep_str)
            input_to_id[vep_str] = v["id"]

    if not vep_inputs:
        return {}

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"variants": vep_inputs, "CADD": 1}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(VEP_POST_URL, headers=headers, json=payload, timeout=120)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", 10))
                print(f"    Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after)
                continue

            if resp.status_code == 503:
                print(f"    Server busy, retrying in 30s (attempt {attempt+1}/{max_retries})...")
                time.sleep(30)
                continue

            resp.raise_for_status()
            results = resp.json()
            break
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"    Error: {e}, retrying in 10s...")
                time.sleep(10)
            else:
                print(f"    Failed after {max_retries} attempts: {e}")
                return {}
    else:
        return {}

    # Parse results
    scores = {}
    for r in results:
        input_str = r.get("input", "")
        cadd_phred, cadd_raw = extract_cadd_from_vep(r)
        if input_str in input_to_id and cadd_phred is not None:
            scores[input_to_id[input_str]] = {
                "cadd_phred": cadd_phred,
                "cadd_raw": cadd_raw,
            }

    return scores


def process_locus(locus: str, info: dict, resume: bool = False):
    """Process all variants for a single locus."""
    filepath = RESULTS_DIR / info["file"]
    chrom = info["chrom"]
    output_file = RESULTS_DIR / f"cadd_scores_{locus}.csv"

    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    print(f"\n{'='*60}")
    print(f"{locus} (chr{chrom}): {total} variants")
    print(f"{'='*60}")

    # Load cache
    cache = load_cache(locus) if resume else {}
    if cache:
        print(f"  Cache loaded: {len(cache)} entries")

    # Prepare variants, skip cached
    to_fetch = []
    for row in rows:
        cid = row["ClinVar_ID"]
        if cid not in cache:
            to_fetch.append({
                "id": cid,
                "pos": row["Position_GRCh38"],
                "ref": row["Ref"],
                "alt": row["Alt"],
            })

    print(f"  Need to fetch: {len(to_fetch)} (cached: {len(cache)})")

    # Fetch in batches
    n_batches = (len(to_fetch) + BATCH_SIZE - 1) // BATCH_SIZE if to_fetch else 0
    fetched = 0

    for i in range(0, len(to_fetch), BATCH_SIZE):
        batch = to_fetch[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{n_batches} ({len(batch)} variants)...", end=" ", flush=True)

        scores = fetch_batch(batch, chrom)
        for cid, score_data in scores.items():
            cache[cid] = score_data
        fetched += len(scores)
        print(f"got {len(scores)} scores")

        # Save cache every 5 batches
        if batch_num % 5 == 0:
            save_cache(locus, cache)

        if batch_num < n_batches:
            time.sleep(RATE_LIMIT_PAUSE)

    # Final cache save
    save_cache(locus, cache)

    # Write output CSV
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ClinVar_ID", "Position_GRCh38", "Ref", "Alt",
                         "Category", "CADD_Phred", "CADD_Raw"])
        scored = 0
        for row in rows:
            cid = row["ClinVar_ID"]
            cadd = cache.get(cid, {})
            phred = cadd.get("cadd_phred", "NA")
            raw = cadd.get("cadd_raw", "NA")
            if phred != "NA":
                scored += 1
            writer.writerow([
                cid, row["Position_GRCh38"], row["Ref"], row["Alt"],
                row["Category"], phred, raw,
            ])

    print(f"\n  DONE: {scored}/{total} scored ({scored/total*100:.1f}%)")
    print(f"  Output: {output_file}")
    return scored, total


def main():
    parser = argparse.ArgumentParser(description="Fetch CADD v1.7 scores via Ensembl VEP")
    parser.add_argument("--locus", help="Single locus (CFTR, TP53, etc.) or omit for all")
    parser.add_argument("--resume", action="store_true", help="Resume from cache")
    args = parser.parse_args()

    if args.locus:
        locus = args.locus.upper()
        if locus not in LOCI:
            print(f"ERROR: Unknown locus '{locus}'. Available: {list(LOCI.keys())}")
            return
        loci_to_process = {locus: LOCI[locus]}
    else:
        loci_to_process = LOCI

    print("CADD v1.7 Score Fetcher for ARCHCODE")
    print(f"Loci: {', '.join(loci_to_process.keys())}")
    print(f"API: Ensembl VEP REST + CADD plugin")
    print(f"Batch size: {BATCH_SIZE}, rate limit: {RATE_LIMIT_PAUSE}s")
    if args.resume:
        print("Mode: RESUME from cache")

    total_scored = 0
    total_variants = 0

    for locus, info in loci_to_process.items():
        scored, total = process_locus(locus, info, args.resume)
        total_scored += scored
        total_variants += total

    print(f"\n{'='*60}")
    print(f"ALL DONE: {total_scored}/{total_variants} scored "
          f"({total_scored/total_variants*100:.1f}%)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
