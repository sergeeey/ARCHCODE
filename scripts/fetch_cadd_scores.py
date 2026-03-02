#!/usr/bin/env python3
"""
Fetch CADD scores for variants via Ensembl VEP REST API.

ПОЧЕМУ: effectStrength в ARCHCODE использует categorical mapping (nonsense=0.1,
intronic=0.8). Это создаёт circular dependency: category → effectStrength → SSIM → AUC.
CADD scores — continuous, per-variant scores, которые разрывают эту связь.

Usage:
    python scripts/fetch_cadd_scores.py --locus hbb
    python scripts/fetch_cadd_scores.py --locus brca1
    python scripts/fetch_cadd_scores.py --locus all

Output: Adds cadd_phred, cadd_raw columns to VEP result CSV files.
"""

import csv
import json
import time
import argparse
import requests
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VEP_POST_URL = "https://rest.ensembl.org/vep/human/region"
BATCH_SIZE = 200  # Ensembl limit
RATE_LIMIT_PAUSE = 1.0  # seconds between batches

# ПОЧЕМУ: locus → VEP CSV file mapping. Pathogenic and benign files separate.
LOCUS_VEP_FILES: dict[str, list[str]] = {
    "hbb": [
        "data/hbb_vep_results.csv",
        "data/hbb_benign_vep_results.csv",
    ],
    "cftr": [
        "data/cftr_vep_results.csv",
        "data/cftr_benign_vep_results.csv",
    ],
    "tp53": [
        "data/tp53_vep_results.csv",
        "data/tp53_benign_vep_results.csv",
    ],
    "brca1": [
        "data/brca1_vep_results.csv",
        "data/brca1_benign_vep_results.csv",
    ],
    "mlh1": [
        "data/mlh1_vep_results.csv",
        "data/mlh1_benign_vep_results.csv",
    ],
    "ldlr": [
        "data/ldlr_vep_results.csv",
        "data/ldlr_benign_vep_results.csv",
    ],
    "scn5a": [
        "data/scn5a_vep_results.csv",
        "data/scn5a_benign_vep_results.csv",
    ],
}


def variant_to_vep_input(chr: str, pos: str, ref: str, alt: str) -> Optional[str]:
    """Convert variant to Ensembl VEP input format: 'chr pos end allele_string strand'.

    ПОЧЕМУ формат: VEP REST POST endpoint принимает варианты в формате
    'chr start end allele_string strand'. Для SNVs: start=end=pos.
    Для deletions/insertions — нужна специальная обработка.
    """
    pos_int = int(pos)

    if len(ref) == 1 and len(alt) == 1:
        # SNV
        return f"{chr} {pos_int} {pos_int} {ref}/{alt} 1"
    elif len(ref) > len(alt):
        # Deletion
        # ПОЧЕМУ: VEP deletion format = start+1 to start+len(deleted)
        # ref=TTTTTT alt=TTTTT → deletion of 1 T at specific position
        deleted = ref[len(alt):]
        start = pos_int + len(alt)
        end = start + len(deleted) - 1
        return f"{chr} {start} {end} {deleted}/- 1"
    elif len(alt) > len(ref):
        # Insertion
        # ПОЧЕМУ: VEP insertion format = pos to pos-1 (signals insertion point)
        inserted = alt[len(ref):]
        start = pos_int + len(ref) - 1
        end = start  # insertion between start and start+1
        return f"{chr} {start} {end + 1} -/{inserted} 1"
    else:
        # MNV (multi-nucleotide variant)
        end = pos_int + len(ref) - 1
        return f"{chr} {pos_int} {end} {ref}/{alt} 1"


def fetch_cadd_batch(variants_batch: list[dict]) -> dict[str, dict]:
    """Query Ensembl VEP REST API for a batch of variants with CADD scores.

    Returns: {clinvar_id: {cadd_phred: float, cadd_raw: float}}
    """
    # Build VEP input strings
    vep_inputs = []
    id_map = {}  # vep_input_str → clinvar_id (for matching results back)

    for v in variants_batch:
        vep_str = variant_to_vep_input(v["chr"], v["position"], v["ref"], v["alt"])
        if vep_str:
            vep_inputs.append(vep_str)
            # ПОЧЕМУ: key = chr:pos:ref>alt для уникальной идентификации
            key = f"{v['chr']}:{v['position']}:{v['ref']}>{v['alt']}"
            id_map[key] = v["clinvar_id"]

    if not vep_inputs:
        return {}

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"variants": vep_inputs, "CADD": 1}

    try:
        resp = requests.post(
            VEP_POST_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if resp.status_code == 429:
            # Rate limited — wait and retry
            retry_after = int(resp.headers.get("Retry-After", 5))
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            resp = requests.post(
                VEP_POST_URL, headers=headers, json=payload, timeout=120
            )

        resp.raise_for_status()
        results = resp.json()
    except requests.RequestException as e:
        print(f"  API error: {e}")
        return {}

    # Parse CADD scores from response
    cadd_scores = {}
    for result in results:
        # Extract position info to match back
        input_str = result.get("input", "")
        parts = input_str.split()
        if len(parts) >= 4:
            chr_r = parts[0]
            pos_r = parts[1]
            alleles = parts[3].split("/")
            ref_r = alleles[0] if alleles[0] != "-" else ""
            alt_r = alleles[1] if len(alleles) > 1 and alleles[1] != "-" else ""

        # Get CADD from transcript_consequences
        cadd_phred = None
        cadd_raw = None

        for tc in result.get("transcript_consequences", []):
            if "cadd_phred" in tc:
                cadd_phred = tc["cadd_phred"]
                cadd_raw = tc.get("cadd_raw")
                break

        # Also check intergenic_consequences
        if cadd_phred is None:
            for ic in result.get("intergenic_consequences", []):
                if "cadd_phred" in ic:
                    cadd_phred = ic["cadd_phred"]
                    cadd_raw = ic.get("cadd_raw")
                    break

        # Match back to clinvar_id using input string
        # Try to find matching variant
        matched_id = None
        for key, cid in id_map.items():
            chr_k, pos_k, allele_k = key.split(":")
            ref_k, alt_k = allele_k.split(">")
            # Direct position match for SNVs
            if chr_k == chr_r and pos_k == pos_r and len(ref_k) == 1 and len(alt_k) == 1:
                if ref_k == ref_r and alt_k == alt_r:
                    matched_id = cid
                    break
            # For indels, use the input string match
            elif input_str == variant_to_vep_input(chr_k, pos_k, ref_k, alt_k):
                matched_id = cid
                break

        if matched_id and cadd_phred is not None:
            cadd_scores[matched_id] = {
                "cadd_phred": cadd_phred,
                "cadd_raw": cadd_raw,
            }

    return cadd_scores


def process_vep_file(filepath: Path) -> int:
    """Add CADD scores to a VEP results CSV file.

    Returns number of variants with CADD scores found.
    """
    if not filepath.exists():
        print(f"  SKIP: {filepath} not found")
        return 0

    # Read existing data
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    print(f"  Processing {filepath.name}: {len(rows)} variants")

    # Check if CADD already present
    if "cadd_phred" in fieldnames:
        existing = sum(1 for r in rows if r.get("cadd_phred", ""))
        print(f"    CADD already present ({existing}/{len(rows)} filled)")
        if existing == len(rows):
            return existing

    # Prepare variant dicts for API
    variants = []
    for row in rows:
        variants.append({
            "clinvar_id": row["clinvar_id"],
            "chr": row["chr"],
            "position": row["position"],
            "ref": row["ref"],
            "alt": row["alt"],
        })

    # Fetch in batches
    all_cadd: dict[str, dict] = {}
    n_batches = (len(variants) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(variants), BATCH_SIZE):
        batch = variants[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        print(f"    Batch {batch_num}/{n_batches} ({len(batch)} variants)...")

        cadd_results = fetch_cadd_batch(batch)
        all_cadd.update(cadd_results)

        if batch_num < n_batches:
            time.sleep(RATE_LIMIT_PAUSE)

    print(f"    Got CADD scores for {len(all_cadd)}/{len(rows)} variants")

    # Update CSV with CADD scores
    if "cadd_phred" not in fieldnames:
        fieldnames.extend(["cadd_phred", "cadd_raw"])

    for row in rows:
        cid = row["clinvar_id"]
        if cid in all_cadd:
            row["cadd_phred"] = all_cadd[cid]["cadd_phred"]
            row["cadd_raw"] = all_cadd[cid]["cadd_raw"]
        else:
            row.setdefault("cadd_phred", "")
            row.setdefault("cadd_raw", "")

    # Write back
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return len(all_cadd)


def main():
    parser = argparse.ArgumentParser(description="Fetch CADD scores via Ensembl VEP")
    parser.add_argument(
        "--locus",
        required=True,
        help="Locus name (hbb, brca1, ...) or 'all'",
    )
    args = parser.parse_args()

    locus = args.locus.lower()
    if locus == "all":
        loci = list(LOCUS_VEP_FILES.keys())
    else:
        if locus not in LOCUS_VEP_FILES:
            print(f"ERROR: Unknown locus '{locus}'. Available: {list(LOCUS_VEP_FILES.keys())}")
            return
        loci = [locus]

    total_found = 0
    total_variants = 0

    for loc in loci:
        print(f"\n=== {loc.upper()} ===")
        for rel_path in LOCUS_VEP_FILES[loc]:
            filepath = PROJECT_ROOT / rel_path
            found = process_vep_file(filepath)
            total_found += found

            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    total_variants += sum(1 for _ in f) - 1  # minus header

    print(f"\n{'='*50}")
    print(f"Total: {total_found}/{total_variants} variants with CADD scores")
    print(f"Coverage: {total_found/total_variants*100:.1f}%" if total_variants > 0 else "")


if __name__ == "__main__":
    main()
