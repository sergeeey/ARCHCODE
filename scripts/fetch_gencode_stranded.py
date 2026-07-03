#!/usr/bin/env python3
"""Re-fetch GENCODE v47 with strand info, to compute correct TSS (start for +, end for -)."""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/gencode.v47.basic.annotation.gtf.gz"
OUT = ROOT / "data/input/gencode_genes_all_chroms_stranded.json"


def main():
    print("Downloading GENCODE v47 (with strand)...")
    with urllib.request.urlopen(URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  {len(raw) // 1_000_000}MB downloaded, parsing...")

    genes = []
    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            line = line.decode("utf-8", errors="ignore")
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            if len(cols) < 9 or cols[2] != "gene":
                continue
            attrs = cols[8]
            if 'gene_type "protein_coding"' not in attrs:
                continue
            gene_name = None
            for part in attrs.split(";"):
                part = part.strip()
                if part.startswith("gene_name"):
                    gene_name = part.split('"')[1]
                    break
            if not gene_name:
                continue
            strand = cols[6]
            start, end = int(cols[3]), int(cols[4])
            tss = start if strand == "+" else end
            genes.append(
                {
                    "chrom": cols[0],
                    "start": start,
                    "end": end,
                    "strand": strand,
                    "tss": tss,
                    "gene": gene_name,
                }
            )

    print(f"  Total protein-coding genes: {len(genes)}")
    with open(OUT, "w") as f:
        json.dump(genes, f)
    print(f"  Saved: {OUT}")


if __name__ == "__main__":
    main()
