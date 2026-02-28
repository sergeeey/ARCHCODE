#!/usr/bin/env python3
"""
Download Pathogenic/LP + Benign/LB CFTR variants from ClinVar via NCBI E-utilities API.

ПОЧЕМУ отдельный скрипт: CFTR скачивает ОБОИХ (P/LP + B/LB) в один CSV,
в отличие от HBB где pathogenic и benign скачивались отдельными скриптами.
Это упрощает data flow для generate-unified-atlas.ts --locus cftr.

Output: data/cftr_variants.csv
"""

import requests
import csv
import time
import re
import json
from pathlib import Path
from collections import Counter

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

OUTPUT_CSV = Path(__file__).parent.parent / "data" / "cftr_variants.csv"
RAW_JSON = Path(__file__).parent.parent / "data" / "cftr_clinvar_raw.json"

# CFTR TAD window on chr7 (GRCh38)
CFTR_CHR = "7"
TAD_START = 117400000
TAD_END = 117717000

# CFTR gene body for reference
CFTR_GENE_START = 117480025
CFTR_GENE_END = 117668665


def esearch(query, retmax=5000):
    """Search ClinVar. CFTR has ~4,000+ variants so retmax=5000."""
    params = {"db": "clinvar", "term": query, "retmax": retmax, "retmode": "json"}
    print(f"Searching: {query[:100]}...")
    resp = requests.get(ESEARCH_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    ids = data["esearchresult"]["idlist"]
    total = int(data["esearchresult"]["count"])
    print(f"  Found {total}, retrieved {len(ids)} IDs")
    if total > retmax:
        print(f"  WARNING: {total} > {retmax}, increasing retmax...")
        return esearch(query, retmax=total + 500)
    return ids


def esummary_batch(ids, batch_size=20):
    """Fetch variant summaries with retry."""
    all_results = []
    total_batches = (len(ids) - 1) // batch_size + 1

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        batch_num = i // batch_size + 1
        params = {"db": "clinvar", "id": ",".join(batch), "retmode": "json"}

        if batch_num % 10 == 1 or batch_num == total_batches:
            print(f"  Batch {batch_num}/{total_batches}...", end=" ")

        for attempt in range(5):
            try:
                resp = requests.get(ESUMMARY_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result", {})
                count = 0
                for uid in batch:
                    if uid in result and isinstance(result[uid], dict):
                        all_results.append(result[uid])
                        count += 1
                if batch_num % 10 == 1 or batch_num == total_batches:
                    print(f"OK ({count})")
                break
            except Exception as e:
                wait = 3 * (attempt + 1)
                print(f"retry({wait}s)...", end=" ")
                time.sleep(wait)
        else:
            print("FAILED")

        # NCBI rate limit: 3 requests/second without API key
        time.sleep(0.4)

    return all_results


def classify_hgvs(hgvs):
    """Determine variant category from HGVS notation.

    Reused from download_benign_hbb.py — gene-agnostic logic.
    Added: inframe_deletion for F508del-type variants.
    """
    if not hgvs:
        return "other"
    h = str(hgvs)

    # Intronic (c.XXX-Ydup, c.XXX+Ydel, etc.)
    if re.search(r'c\.\d+[\+\-]\d+', h):
        return "intronic"
    # UTR
    if "c.*" in h or "c.+" in h:
        return "3_prime_UTR"
    if "c.-" in h and ">" in h:
        return "5_prime_UTR"
    # Frameshift
    if "fs" in h:
        return "frameshift"
    # Nonsense
    if "p." in h:
        after_p = h.split("p.")[-1]
        if "Ter" in after_p or ("*" in after_p and "=" not in after_p):
            return "nonsense"
    # In-frame deletion (e.g., F508del = p.Phe508del)
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+del', h):
        return "inframe_deletion"
    # In-frame insertion/duplication
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+.*ins', h) or re.search(r'p\.\(?[A-Z][a-z]{2}\d+.*dup', h):
        return "inframe_indel"
    # Synonymous (p.XXX= or p.(XXX=))
    if "p.(" in h and "=" in h:
        return "synonymous"
    if re.search(r'p\.[A-Z][a-z]{2}\d+=', h):
        return "synonymous"
    # Missense
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+[A-Z][a-z]{2}', h):
        return "missense"
    # Splice donor/acceptor (c.XXX+1, c.XXX-1, c.XXX+2, c.XXX-2)
    if re.search(r'c\.\d+[\+\-][12][^\d]', h) or re.search(r'c\.\d+[\+\-][12]$', h):
        return "splice_donor"
    # Simple substitution in coding region
    if re.search(r'c\.\d+[ACGT]>[ACGT]', h):
        return "synonymous"  # fallback — likely synonymous if no p. annotation

    return "other"


def parse_variant(rec):
    """Parse ClinVar esummary record for CFTR variants."""
    try:
        accession = rec.get("accession", "")
        if not accession:
            return None

        # Clinical significance — new API format
        clin_sig = ""
        gc = rec.get("germline_classification", {})
        if isinstance(gc, dict):
            clin_sig = gc.get("description", "")
        if not clin_sig:
            cs = rec.get("clinical_significance", {})
            if isinstance(cs, dict):
                clin_sig = cs.get("description", "")
            else:
                clin_sig = str(cs)

        clin_lower = clin_sig.lower()

        # Determine label: Pathogenic or Benign
        if "pathogenic" in clin_lower and "benign" not in clin_lower:
            label = "Pathogenic"
        elif "benign" in clin_lower and "pathogenic" not in clin_lower:
            label = "Benign"
        else:
            # Conflicting or VUS — skip
            return None

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
        if chr_val != CFTR_CHR:
            return None

        position = int(grch38.get("start", "0"))
        if position < TAD_START or position > TAD_END:
            return None

        # Get ref/alt from canonical_spdi (format: NC_000007.14:POS:REF:ALT)
        spdi = vs.get("canonical_spdi", "")
        ref, alt = "", ""
        if spdi:
            parts = spdi.split(":")
            if len(parts) == 4:
                ref = parts[2]
                alt = parts[3]

        # Fallback: parse from variant name
        if not ref or not alt:
            vname = vs.get("variation_name", "")
            m = re.search(r'([ACGT])>([ACGT])', vname)
            if m:
                ref, alt = m.group(1), m.group(2)

        # For deletions/insertions, ref/alt can be multi-base or empty
        # Accept variants even without clean ref/alt (for indels like F508del)
        if not ref and not alt:
            ref = "."
            alt = "."

        # Category from HGVS
        cdna = vs.get("cdna_change", "") or vs.get("variation_name", "")
        # Also try protein change for better classification
        protein = vs.get("protein_change", "") or ""
        hgvs_combined = cdna
        if protein and "p." not in cdna:
            hgvs_combined = f"{cdna} {protein}"
        category = classify_hgvs(hgvs_combined)

        return {
            "clinvar_id": accession,
            "chr": CFTR_CHR,
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
    import datetime
    print(f"CFTR ClinVar Download — {datetime.datetime.now().isoformat()}")
    print(f"TAD window: chr{CFTR_CHR}:{TAD_START:,}-{TAD_END:,}")
    print()

    # Search for Pathogenic/LP variants
    path_ids = esearch(
        'CFTR[gene] AND ("pathogenic"[clinical_significance] OR "likely pathogenic"[clinical_significance])'
    )

    # Search for Benign/LB variants
    benign_ids = esearch(
        'CFTR[gene] AND ("benign"[clinical_significance] OR "likely benign"[clinical_significance])'
    )

    # Combine (some may overlap, dedup later)
    all_ids = list(set(path_ids + benign_ids))
    print(f"\nCombined unique IDs: {len(all_ids)}")

    # Fetch summaries
    print("\nFetching summaries...")
    summaries = esummary_batch(all_ids)
    print(f"Fetched {len(summaries)} summaries")

    # Save raw JSON for reproducibility
    RAW_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_JSON, "w") as f:
        json.dump({
            "download_date": datetime.datetime.now().isoformat(),
            "pathogenic_ids_count": len(path_ids),
            "benign_ids_count": len(benign_ids),
            "combined_unique_ids": len(all_ids),
            "summaries_count": len(summaries),
        }, f, indent=2)
    print(f"Raw metadata saved: {RAW_JSON}")

    # Parse
    variants = []
    for s in summaries:
        v = parse_variant(s)
        if v:
            variants.append(v)

    print(f"\nParsed {len(variants)} valid CFTR-TAD variants")

    # Deduplicate by position+ref+alt
    seen = set()
    unique = []
    for v in variants:
        key = f"{v['position']}_{v['ref']}_{v['alt']}"
        if key not in seen:
            seen.add(key)
            unique.append(v)

    print(f"After dedup: {len(unique)} unique variants")

    # Save
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fields = ["clinvar_id", "chr", "position", "ref", "alt", "category",
              "hgvs_c", "hgvs_p", "clinical_significance", "label"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for v in unique:
            writer.writerow(v)

    print(f"\nSaved to {OUTPUT_CSV}")

    # Statistics
    path_count = sum(1 for v in unique if v["label"] == "Pathogenic")
    benign_count = sum(1 for v in unique if v["label"] == "Benign")
    print(f"  Pathogenic/LP: {path_count}")
    print(f"  Benign/LB:     {benign_count}")
    print(f"  Total:         {len(unique)}")

    cats = Counter(v["category"] for v in unique)
    print("\nBy category:")
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")

    sigs = Counter(v["clinical_significance"] for v in unique)
    print("\nBy clinical significance:")
    for sig, n in sigs.most_common():
        print(f"  {sig}: {n}")

    # Positional spread
    positions = [v["position"] for v in unique]
    if positions:
        spread = max(positions) - min(positions)
        print(f"\nPositional spread: {spread:,} bp ({spread/1000:.1f} kb)")
        print(f"  Min: {min(positions):,}")
        print(f"  Max: {max(positions):,}")

        # Check for F508del
        f508del = [v for v in unique if "508" in v.get("hgvs_c", "") or "508" in v.get("hgvs_p", "")]
        if f508del:
            print(f"\nF508del found: {f508del[0]['clinvar_id']} at pos {f508del[0]['position']:,}")
        else:
            print("\nWARNING: F508del not found — check variant parsing")

    return 0


if __name__ == "__main__":
    exit(main())
