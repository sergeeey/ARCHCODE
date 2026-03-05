#!/usr/bin/env python3
"""
Generic ClinVar variant downloader for any ARCHCODE locus.

Downloads P/LP and B/LB variants from ClinVar E-utilities API,
filtered to the genomic window defined in the locus config.

Usage:
  python scripts/download_clinvar_generic.py HBA1
  python scripts/download_clinvar_generic.py HBA1 --config config/locus/hba1_300kb.json
  python scripts/download_clinvar_generic.py HBA1 --max-variants 5000
"""

import argparse
import csv
import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

PROJECT = Path(__file__).parent.parent

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def find_config(gene: str) -> Path:
    """Find locus config for a gene."""
    config_dir = PROJECT / "config" / "locus"
    candidates = sorted(config_dir.glob(f"{gene.lower()}_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No config found for {gene} in {config_dir}")
    return candidates[0]


def load_config(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def esearch(gene: str, significance: str, retmax: int = 10000) -> list[str]:
    """Search ClinVar for variant UIDs."""
    query = f'{gene}[gene] AND {significance}[clinical significance] AND "single nucleotide variant"[variant type]'
    params = urllib.parse.urlencode({
        "db": "clinvar",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
    })
    url = f"{EUTILS_BASE}/esearch.fcgi?{params}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())
    ids = data.get("esearchresult", {}).get("idlist", [])
    count = int(data.get("esearchresult", {}).get("count", 0))
    print(f"  esearch [{significance}]: {count} total, fetched {len(ids)} UIDs")
    return ids


def esummary_batch(uids: list[str], batch_size: int = 200) -> list[dict]:
    """Fetch variant summaries in batches."""
    results = []
    for i in range(0, len(uids), batch_size):
        batch = uids[i:i + batch_size]
        params = urllib.parse.urlencode({
            "db": "clinvar",
            "id": ",".join(batch),
            "retmode": "json",
        })
        url = f"{EUTILS_BASE}/esummary.fcgi?{params}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
        result = data.get("result", {})
        for uid in batch:
            if uid in result:
                results.append(result[uid])
        if i + batch_size < len(uids):
            time.sleep(0.5)
    return results


def parse_variant(summary: dict, chrom: str, win_start: int, win_end: int) -> dict | None:
    """Parse a ClinVar summary into a variant record, filtering by window."""
    genes = summary.get("genes", [])
    variation_set = summary.get("variation_set", [])

    for vs in variation_set:
        for var in vs.get("variation_loc", []):
            if var.get("assembly_name") == "GRCh38":
                vchr = var.get("chr", "")
                start = int(var.get("start", 0))
                stop = int(var.get("stop", 0))

                norm_chrom = chrom.replace("chr", "")
                if vchr != norm_chrom and vchr != chrom:
                    return None

                if start < win_start or stop > win_end:
                    return None

                # ClinVar API uses germline_classification (not clinical_significance)
                gc = summary.get("germline_classification") or summary.get("clinical_significance") or {}
                clin_sig = gc.get("description", "") if isinstance(gc, dict) else str(gc)
                review_status = gc.get("review_status", "") if isinstance(gc, dict) else ""
                title = summary.get("title", "")
                accession = summary.get("accession", "")

                return {
                    "uid": summary.get("uid", ""),
                    "accession": accession,
                    "title": title,
                    "chrom": f"chr{vchr}" if not vchr.startswith("chr") else vchr,
                    "pos_start": start,
                    "pos_end": stop,
                    "pos_relative": start - win_start,
                    "clinical_significance": clin_sig,
                    "gene": genes[0].get("symbol", "") if genes else "",
                    "review_status": review_status,
                }
    return None


def download_variants(gene: str, config: dict, max_variants: int = 10000) -> list[dict]:
    """Download and filter ClinVar variants for a locus."""
    window = config["window"]
    chrom = window["chromosome"]
    win_start = window["start"]
    win_end = window["end"]

    abs_start = win_start
    abs_end = win_end

    print(f"\nDownloading ClinVar variants for {gene}")
    print(f"Window: {chrom}:{abs_start}-{abs_end} (GRCh38)")

    all_variants = []

    for sig_label, sig_query in [
        ("pathogenic", "pathogenic"),
        ("likely pathogenic", "likely pathogenic"),
        ("benign", "benign"),
        ("likely benign", "likely benign"),
    ]:
        uids = esearch(gene, sig_query, retmax=max_variants)
        if not uids:
            continue

        summaries = esummary_batch(uids)
        for s in summaries:
            var = parse_variant(s, chrom, win_start, win_end)
            if var:
                all_variants.append(var)
        time.sleep(1)

    # Deduplicate by accession
    seen = set()
    unique = []
    for v in all_variants:
        key = v["accession"]
        if key not in seen:
            seen.add(key)
            unique.append(v)

    print(f"\nTotal unique variants in window: {len(unique)}")

    path_count = sum(1 for v in unique if "pathogenic" in v["clinical_significance"].lower())
    benign_count = sum(1 for v in unique if "benign" in v["clinical_significance"].lower())
    print(f"  Pathogenic/Likely pathogenic: {path_count}")
    print(f"  Benign/Likely benign: {benign_count}")

    return unique


def save_csv(variants: list[dict], output_path: Path):
    """Save variants to CSV."""
    if not variants:
        print("No variants to save!")
        return

    fieldnames = [
        "uid", "accession", "title", "chrom", "pos_start", "pos_end",
        "pos_relative", "clinical_significance", "gene", "review_status",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(variants)
    print(f"Saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Download ClinVar variants for ARCHCODE locus")
    parser.add_argument("gene", help="Gene symbol (e.g. HBA1)")
    parser.add_argument("--config", help="Path to locus config JSON")
    parser.add_argument("--max-variants", type=int, default=10000)
    parser.add_argument("--output", help="Output CSV path")
    args = parser.parse_args()

    gene = args.gene.upper()

    if args.config:
        config_path = Path(args.config)
    else:
        config_path = find_config(gene)
    print(f"Using config: {config_path}")

    config = load_config(config_path)
    variants = download_variants(gene, config, args.max_variants)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = PROJECT / "data" / f"clinvar_{gene.lower()}_variants.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)

    save_csv(variants, output_path)
    return variants


if __name__ == "__main__":
    main()
