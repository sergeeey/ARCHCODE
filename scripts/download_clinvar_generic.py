#!/usr/bin/env python3
"""
Generic ClinVar variant downloader for any gene locus.

ПОЧЕМУ generic: вместо отдельного скрипта на каждый ген (download_clinvar_cftr.py,
download_clinvar_tp53.py), один скрипт с параметром --gene. Переиспользует
всю логику парсинга CFTR-скрипта, но принимает конфиг из JSON.

Usage:
    python scripts/download_clinvar_generic.py --gene TP53
    python scripts/download_clinvar_generic.py --gene BRCA1
    python scripts/download_clinvar_generic.py --gene MLH1

Output: data/{gene_lower}_variants.csv
"""

import requests
import csv
import time
import re
import json
import sys
import argparse
from pathlib import Path
from collections import Counter
import datetime

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

# Gene-specific chromosome mapping
GENE_CHR = {
    "TP53": "17", "BRCA1": "17", "BRCA2": "13", "MLH1": "3",
    "MSH2": "2", "MSH6": "2", "APC": "5", "RB1": "13",
    "VHL": "3", "SCN5A": "3", "KCNQ1": "11", "KCNH2": "7",
    "LMNA": "1", "LDLR": "19", "FBN1": "15", "MYH7": "14",
    "MYBPC3": "11", "RYR1": "19", "PKD1": "16", "COL3A1": "2",
    "CFTR": "7", "HBB": "11",
}


def esearch(query: str, retmax: int = 10000) -> list:
    """Search ClinVar with auto-expansion."""
    params = {"db": "clinvar", "term": query, "retmax": retmax, "retmode": "json"}
    print(f"  Searching: {query[:80]}...")
    resp = requests.get(ESEARCH_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    ids = data["esearchresult"]["idlist"]
    total = int(data["esearchresult"]["count"])
    print(f"  Found {total}, retrieved {len(ids)} IDs")
    if total > retmax:
        print(f"  Expanding retmax to {total + 500}...")
        return esearch(query, retmax=total + 500)
    return ids


def esummary_batch(ids: list, batch_size: int = 20) -> list:
    """Fetch variant summaries in batches."""
    all_results = []
    total_batches = (len(ids) - 1) // batch_size + 1

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        batch_num = i // batch_size + 1
        params = {"db": "clinvar", "id": ",".join(batch), "retmode": "json"}

        if batch_num % 20 == 1 or batch_num == total_batches:
            print(f"  Batch {batch_num}/{total_batches}...", end=" ", flush=True)

        for attempt in range(5):
            try:
                resp = requests.get(ESUMMARY_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result", {})
                for uid in batch:
                    if uid in result and isinstance(result[uid], dict):
                        all_results.append(result[uid])
                if batch_num % 20 == 1 or batch_num == total_batches:
                    print("OK")
                break
            except Exception:
                wait = 3 * (attempt + 1)
                print(f"retry({wait}s)...", end=" ", flush=True)
                time.sleep(wait)
        else:
            print("FAILED")

        time.sleep(0.4)  # NCBI rate limit

    return all_results


def classify_hgvs(hgvs: str) -> str:
    """Determine variant category from HGVS notation."""
    if not hgvs:
        return "other"
    h = str(hgvs)

    if re.search(r'c\.\d+[\+\-]\d+', h):
        return "intronic"
    if "c.*" in h or "c.+" in h:
        return "3_prime_UTR"
    if "c.-" in h and ">" in h:
        return "5_prime_UTR"
    if "fs" in h:
        return "frameshift"
    if "p." in h:
        after_p = h.split("p.")[-1]
        if "Ter" in after_p or ("*" in after_p and "=" not in after_p):
            return "nonsense"
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+del', h):
        return "inframe_deletion"
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+.*ins', h) or re.search(r'p\.\(?[A-Z][a-z]{2}\d+.*dup', h):
        return "inframe_indel"
    if "p.(" in h and "=" in h:
        return "synonymous"
    if re.search(r'p\.[A-Z][a-z]{2}\d+=', h):
        return "synonymous"
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+[A-Z][a-z]{2}', h):
        return "missense"
    if re.search(r'c\.\d+[\+\-][12][^\d]', h) or re.search(r'c\.\d+[\+\-][12]$', h):
        return "splice_donor"
    if re.search(r'c\.\d+[ACGT]>[ACGT]', h):
        return "synonymous"

    return "other"


def parse_variant(rec: dict, gene: str, expected_chr: str,
                  window_start: int = 0, window_end: int = 999_999_999) -> dict | None:
    """Parse ClinVar esummary record."""
    try:
        accession = rec.get("accession", "")
        if not accession:
            return None

        # Clinical significance
        clin_sig = ""
        gc = rec.get("germline_classification", {})
        if isinstance(gc, dict):
            clin_sig = gc.get("description", "")
        if not clin_sig:
            cs = rec.get("clinical_significance", {})
            clin_sig = cs.get("description", "") if isinstance(cs, dict) else str(cs)

        clin_lower = clin_sig.lower()
        if "pathogenic" in clin_lower and "benign" not in clin_lower:
            label = "Pathogenic"
        elif "benign" in clin_lower and "pathogenic" not in clin_lower:
            label = "Benign"
        else:
            return None  # VUS or conflicting

        # Variation set
        vs_list = rec.get("variation_set", [])
        if not vs_list:
            return None
        vs = vs_list[0] if isinstance(vs_list, list) else vs_list

        # GRCh38 location
        locs = vs.get("variation_loc", [])
        grch38 = None
        for loc in locs:
            if "GRCh38" in loc.get("assembly_name", ""):
                grch38 = loc
                break
        if not grch38:
            return None

        chr_val = grch38.get("chr", "")
        if chr_val != expected_chr:
            return None

        position = int(grch38.get("start", "0"))
        if position < window_start or position > window_end:
            return None

        # Ref/alt from canonical_spdi
        spdi = vs.get("canonical_spdi", "")
        ref, alt = "", ""
        if spdi:
            parts = spdi.split(":")
            if len(parts) == 4:
                ref, alt = parts[2], parts[3]
        if not ref or not alt:
            vname = vs.get("variation_name", "")
            m = re.search(r'([ACGT])>([ACGT])', vname)
            if m:
                ref, alt = m.group(1), m.group(2)
        if not ref and not alt:
            ref, alt = ".", "."

        # Category
        cdna = vs.get("cdna_change", "") or vs.get("variation_name", "")
        protein = vs.get("protein_change", "") or ""
        hgvs_combined = cdna
        if protein and "p." not in cdna:
            hgvs_combined = f"{cdna} {protein}"
        category = classify_hgvs(hgvs_combined)

        return {
            "clinvar_id": accession,
            "chr": expected_chr,
            "position": position,
            "ref": ref,
            "alt": alt,
            "category": category,
            "hgvs_c": cdna,
            "hgvs_p": protein,
            "clinical_significance": clin_sig,
            "label": label,
        }
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Download ClinVar variants for any gene")
    parser.add_argument("--gene", required=True, help="Gene symbol (e.g., TP53, BRCA1)")
    parser.add_argument("--window-start", type=int, default=0, help="Window start (GRCh38)")
    parser.add_argument("--window-end", type=int, default=999_999_999, help="Window end (GRCh38)")
    args = parser.parse_args()

    gene = args.gene.upper()
    expected_chr = GENE_CHR.get(gene)
    if not expected_chr:
        print(f"ERROR: Unknown gene {gene}. Add it to GENE_CHR mapping.")
        sys.exit(1)

    # Try to load window from locus config
    config_patterns = [
        f"config/locus/{gene.lower()}_*.json",
        f"config/locus/{gene.lower()}.json",
    ]
    for pattern in config_patterns:
        import glob
        matches = glob.glob(pattern)
        if matches:
            with open(matches[0]) as f:
                cfg = json.load(f)
            window = cfg.get("window", {})
            if args.window_start == 0:
                args.window_start = window.get("start", 0)
            if args.window_end == 999_999_999:
                args.window_end = window.get("end", 999_999_999)
            print(f"Loaded window from {matches[0]}: {args.window_start:,}-{args.window_end:,}")
            break

    output_csv = Path(f"data/{gene.lower()}_variants.csv")
    raw_json = Path(f"data/{gene.lower()}_clinvar_raw.json")

    print(f"=== ClinVar Download: {gene} ===")
    print(f"Date: {datetime.datetime.now().isoformat()}")
    print(f"Chr: {expected_chr}")
    print(f"Window: {args.window_start:,} - {args.window_end:,}")
    print()

    # Search P/LP
    path_ids = esearch(
        f'{gene}[gene] AND ("pathogenic"[clinical_significance] OR "likely pathogenic"[clinical_significance])'
    )

    # Search B/LB
    benign_ids = esearch(
        f'{gene}[gene] AND ("benign"[clinical_significance] OR "likely benign"[clinical_significance])'
    )

    all_ids = list(set(path_ids + benign_ids))
    print(f"\nCombined unique IDs: {len(all_ids)}")

    # Fetch
    print("\nFetching summaries...")
    summaries = esummary_batch(all_ids)
    print(f"Fetched {len(summaries)} summaries")

    # Save raw metadata
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_json, "w") as f:
        json.dump({
            "gene": gene,
            "download_date": datetime.datetime.now().isoformat(),
            "pathogenic_ids_count": len(path_ids),
            "benign_ids_count": len(benign_ids),
            "combined_unique_ids": len(all_ids),
            "summaries_count": len(summaries),
            "window": {"start": args.window_start, "end": args.window_end},
        }, f, indent=2)

    # Parse
    variants = []
    for s in summaries:
        v = parse_variant(s, gene, expected_chr, args.window_start, args.window_end)
        if v:
            variants.append(v)

    # Dedup
    seen = set()
    unique = []
    for v in variants:
        key = f"{v['position']}_{v['ref']}_{v['alt']}"
        if key not in seen:
            seen.add(key)
            unique.append(v)

    print(f"\nParsed: {len(variants)}, unique: {len(unique)}")

    # Save CSV
    fields = ["clinvar_id", "chr", "position", "ref", "alt", "category",
              "hgvs_c", "hgvs_p", "clinical_significance", "label"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for v in unique:
            writer.writerow(v)

    print(f"\nSaved: {output_csv}")

    # Stats
    path_count = sum(1 for v in unique if v["label"] == "Pathogenic")
    benign_count = sum(1 for v in unique if v["label"] == "Benign")
    print(f"  Pathogenic/LP: {path_count}")
    print(f"  Benign/LB:     {benign_count}")
    print(f"  Total:         {len(unique)}")

    cats = Counter(v["category"] for v in unique)
    print("\nBy category:")
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")

    positions = [v["position"] for v in unique]
    if positions:
        spread = max(positions) - min(positions)
        print(f"\nSpread: {spread:,} bp ({spread/1000:.1f} kb)")


if __name__ == "__main__":
    main()
