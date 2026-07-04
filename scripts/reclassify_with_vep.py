#!/usr/bin/env python3
"""
Reclassify ClinVar variants using Ensembl VEP REST API.

ПОЧЕМУ: ClinVar esummary часто не возвращает protein-level HGVS (hgvs_p),
из-за чего все coding SNVs попадают в "synonymous" по дефолту.
Этот скрипт использует Ensembl VEP для получения реальных consequence terms
и protein change annotations.

Usage:
    python scripts/reclassify_with_vep.py data/tert_variants.csv
    python scripts/reclassify_with_vep.py data/gjb2_variants.csv
"""

import csv
import json
import re
import sys
import time
import argparse
import requests
from pathlib import Path
from collections import Counter

VEP_URL = "https://rest.ensembl.org/vep/human/region"
BATCH_SIZE = 200  # Ensembl VEP POST limit
RATE_LIMIT = 0.5  # seconds between batches

# Map VEP consequence_terms → our category system
VEP_TO_CATEGORY = {
    "transcript_ablation": "frameshift",
    "splice_acceptor_variant": "splice_donor",
    "splice_donor_variant": "splice_donor",
    "stop_gained": "nonsense",
    "frameshift_variant": "frameshift",
    "stop_lost": "nonsense",
    "start_lost": "nonsense",
    "inframe_insertion": "inframe_indel",
    "inframe_deletion": "inframe_deletion",
    "missense_variant": "missense",
    "protein_altering_variant": "missense",
    "splice_region_variant": "splice_region",
    "synonymous_variant": "synonymous",
    "stop_retained_variant": "synonymous",
    "coding_sequence_variant": "other",
    "5_prime_UTR_variant": "5_prime_UTR",
    "3_prime_UTR_variant": "3_prime_UTR",
    "intron_variant": "intronic",
    "upstream_gene_variant": "5_prime_UTR",
    "downstream_gene_variant": "3_prime_UTR",
    "non_coding_transcript_exon_variant": "other",
    "non_coding_transcript_variant": "other",
    "NMD_transcript_variant": "other",
    "intergenic_variant": "other",
}

# Priority order (more severe = lower index)
SEVERITY_ORDER = [
    "nonsense", "frameshift", "splice_donor", "splice_region",
    "missense", "inframe_deletion", "inframe_indel",
    "5_prime_UTR", "3_prime_UTR", "synonymous", "intronic", "other",
]


def vep_batch_query(variants: list[dict]) -> dict:
    """Query VEP for a batch of variants.

    Args:
        variants: list of dicts with chr, position, ref, alt

    Returns:
        dict mapping "chr:pos:ref/alt" → {"consequence": str, "amino_acids": str, "hgvs_p": str}
    """
    # Build VEP input format: "chr pos pos allele strand"
    vep_inputs = []
    key_map = {}  # VEP input string → original key

    for v in variants:
        chr_val = v["chr"]
        pos = int(v["position"])
        ref = v["ref"]
        alt = v["alt"]

        if not ref or not alt or ref == "." or alt == ".":
            continue

        # VEP expects: "chr start end allele_string strand"
        vep_str = f"{chr_val} {pos} {pos} {ref}/{alt} 1"
        vep_inputs.append(vep_str)
        key = f"{chr_val}:{pos}:{ref}/{alt}"
        key_map[f"{chr_val}_{pos}_{ref}/{alt}"] = key

    if not vep_inputs:
        return {}

    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"variants": vep_inputs}

    for attempt in range(5):
        try:
            resp = requests.post(VEP_URL, json=payload, headers=headers, timeout=120)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 5))
                print(f"  Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            wait = 3 * (attempt + 1)
            print(f"  Error: {e}, retry in {wait}s...", flush=True)
            time.sleep(wait)
    else:
        print("  FAILED after 5 attempts", flush=True)
        return {}

    results = {}
    for entry in resp.json():
        input_str = entry.get("input", "")
        # Parse: "chr pos pos ref/alt strand" → key
        parts = input_str.split()
        if len(parts) < 5:
            continue
        chr_v, pos_v = parts[0], parts[1]
        allele_str = parts[3]  # "ref/alt"
        entry_key = f"{chr_v}:{pos_v}:{allele_str}"

        # Find the most severe protein-coding consequence
        best_consequence = None
        best_aa = ""
        best_hgvs_p = ""
        best_severity = len(SEVERITY_ORDER)

        for tc in entry.get("transcript_consequences", []):
            if tc.get("biotype") != "protein_coding":
                continue

            for term in tc.get("consequence_terms", []):
                cat = VEP_TO_CATEGORY.get(term, "other")
                try:
                    sev = SEVERITY_ORDER.index(cat)
                except ValueError:
                    sev = len(SEVERITY_ORDER)

                if sev < best_severity:
                    best_severity = sev
                    best_consequence = cat
                    best_aa = tc.get("amino_acids", "")
                    # Build hgvs_p from amino acids
                    if best_aa and "/" in best_aa:
                        ref_aa, alt_aa = best_aa.split("/")
                        ppos = tc.get("protein_start", "?")
                        best_hgvs_p = f"p.{ref_aa}{ppos}{alt_aa}"
                    elif best_aa and "/" not in best_aa:
                        ppos = tc.get("protein_start", "?")
                        best_hgvs_p = f"p.{best_aa}{ppos}="

        if best_consequence:
            results[entry_key] = {
                "consequence": best_consequence,
                "amino_acids": best_aa,
                "hgvs_p": best_hgvs_p,
            }

    return results


def main():
    parser = argparse.ArgumentParser(description="Reclassify variants with Ensembl VEP")
    parser.add_argument("input_csv", help="Input CSV (e.g., data/tert_variants.csv)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write output, just report")
    args = parser.parse_args()

    input_path = Path(args.input_csv)
    if not input_path.exists():
        print(f"ERROR: {input_path} not found")
        sys.exit(1)

    # Read variants
    with open(input_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    print(f"=== VEP Reclassification: {input_path.name} ===")
    print(f"Total variants: {len(rows)}")

    # Find variants needing reclassification:
    # coding SNVs classified as "synonymous" with empty hgvs_p
    needs_vep = []
    for i, r in enumerate(rows):
        if (r["category"] == "synonymous"
                and not r.get("hgvs_p", "")
                and re.search(r"c\.\d+[ACGT]>[ACGT]", r.get("hgvs_c", ""))):
            needs_vep.append((i, r))

    print(f"Variants needing VEP: {len(needs_vep)}")

    if not needs_vep:
        print("Nothing to reclassify!")
        return

    # Query VEP in batches
    total_batches = (len(needs_vep) - 1) // BATCH_SIZE + 1
    reclassified = 0
    category_changes = Counter()

    for batch_idx in range(0, len(needs_vep), BATCH_SIZE):
        batch = needs_vep[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = batch_idx // BATCH_SIZE + 1
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} variants)...", end=" ", flush=True)

        vep_input = [{"chr": r["chr"], "position": r["position"],
                       "ref": r["ref"], "alt": r["alt"]} for _, r in batch]

        results = vep_batch_query(vep_input)

        # Apply reclassification
        for row_idx, r in batch:
            key = f"{r['chr']}:{r['position']}:{r['ref']}/{r['alt']}"
            if key in results:
                vep_result = results[key]
                old_cat = rows[row_idx]["category"]
                new_cat = vep_result["consequence"]

                if old_cat != new_cat:
                    rows[row_idx]["category"] = new_cat
                    category_changes[f"{old_cat} → {new_cat}"] += 1
                    reclassified += 1

                if vep_result["hgvs_p"]:
                    rows[row_idx]["hgvs_p"] = vep_result["hgvs_p"]

        print(f"done ({len(results)} resolved)", flush=True)
        time.sleep(RATE_LIMIT)

    print(f"\nReclassified: {reclassified}/{len(needs_vep)}")
    print("\nCategory changes:")
    for change, count in category_changes.most_common():
        print(f"  {change}: {count}")

    # Final category distribution
    final_cats = Counter(r["category"] for r in rows)
    print("\nFinal category distribution:")
    for cat, n in final_cats.most_common():
        print(f"  {cat}: {n}")

    # Save
    if not args.dry_run:
        # Backup original
        backup = input_path.with_suffix(".csv.bak")
        input_path.rename(backup)
        print(f"\nBackup: {backup}")

        with open(input_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

        print(f"Saved: {input_path}")
    else:
        print("\n[DRY RUN] No files written")


if __name__ == "__main__":
    main()
