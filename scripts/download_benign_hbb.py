#!/usr/bin/env python3
"""
Download Benign/Likely Benign HBB variants from ClinVar via NCBI E-utilities API.
Output: data/hbb_benign_variants.csv
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

OUTPUT_CSV = Path(__file__).parent.parent / "data" / "hbb_benign_variants.csv"

# HBB region on chr11 (GRCh38) — extended for promoter/regulatory
HBB_START = 5223000
HBB_END = 5228000


def esearch(query, retmax=1000):
    """Search ClinVar."""
    params = {"db": "clinvar", "term": query, "retmax": retmax, "retmode": "json"}
    print(f"Searching: {query[:80]}...")
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    ids = data["esearchresult"]["idlist"]
    total = int(data["esearchresult"]["count"])
    print(f"  Found {total}, retrieved {len(ids)} IDs")
    return ids


def esummary_batch(ids, batch_size=20):
    """Fetch variant summaries with retry."""
    all_results = []
    total_batches = (len(ids) - 1) // batch_size + 1

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        batch_num = i // batch_size + 1
        params = {"db": "clinvar", "id": ",".join(batch), "retmode": "json"}

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
                print(f"OK ({count})")
                break
            except Exception:
                wait = 3 * (attempt + 1)
                print(f"retry({wait}s)...", end=" ")
                time.sleep(wait)
        else:
            print("FAILED")

        time.sleep(2)

    return all_results


def classify_hgvs(hgvs):
    """Determine variant category from HGVS notation."""
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
    # Synonymous (p.XXX= or c.NNN[ACGT]>[ACGT] without p. change)
    if "p.(" in h and "=" in h:
        return "synonymous"
    # Missense
    if re.search(r'p\.\(?[A-Z][a-z]{2}\d+[A-Z][a-z]{2}', h):
        return "missense"
    # Nonsense
    if "Ter" in h or "*" in h.split("p.")[-1] if "p." in h else "":
        return "nonsense"
    # Frameshift
    if "fs" in h:
        return "frameshift"
    # Simple substitution in coding region
    if re.search(r'c\.\d+[ACGT]>[ACGT]', h):
        return "synonymous"  # most benign coding SNVs are synonymous

    return "other"


def parse_variant(rec):
    """Parse ClinVar esummary record."""
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

        if "benign" not in clin_sig.lower():
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
        if chr_val != "11":
            return None

        position = int(grch38.get("start", "0"))
        if position < HBB_START or position > HBB_END:
            return None

        # Get ref/alt from canonical_spdi (format: NC_000011.10:POS:REF:ALT)
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

        if not ref or not alt:
            return None

        # Category from HGVS
        cdna = vs.get("cdna_change", "") or vs.get("variation_name", "")
        category = classify_hgvs(cdna)

        return {
            "clinvar_id": accession,
            "chr": "11",
            "position": position,
            "ref": ref,
            "alt": alt,
            "category": category,
            "hgvs_c": cdna,
            "hgvs_p": "",
            "clinical_significance": clin_sig,
        }
    except Exception:
        return None


def main():
    # Search for Benign + Likely Benign HBB variants
    ids = esearch('HBB[gene] AND ("benign"[clinical_significance] OR "likely benign"[clinical_significance])')

    if not ids:
        print("No variants found!")
        return 1

    # Fetch summaries
    summaries = esummary_batch(ids)
    print(f"\nFetched {len(summaries)} summaries")

    # Parse
    variants = []
    for s in summaries:
        v = parse_variant(s)
        if v:
            variants.append(v)

    print(f"Parsed {len(variants)} valid HBB-region variants")

    # Deduplicate
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
              "hgvs_c", "hgvs_p", "clinical_significance"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for v in unique:
            writer.writerow(v)

    print(f"\nSaved to {OUTPUT_CSV}")
    print(f"Total: {len(unique)} Benign/LB HBB variants")

    cats = Counter(v["category"] for v in unique)
    print("\nBy category:")
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")

    sigs = Counter(v["clinical_significance"] for v in unique)
    print("\nBy significance:")
    for sig, n in sigs.most_common():
        print(f"  {sig}: {n}")

    return 0


if __name__ == "__main__":
    exit(main())
