#!/usr/bin/env python3
"""Fetch GENCODE hg19/GRCh37 gene annotations with strand, to match the ABC
model predictions file's genome build (confirmed empirically: NOC2L TSS in
ABC file = 894679, matches hg19 GRCh37 annotation 894689; hg38 = 959309)."""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

# GENCODE lift37 = GRCh38 annotation coordinates lifted back to GRCh37/hg19,
# the standard GENCODE-maintained hg19 gene set (avoids using the frozen old
# GENCODE 19 annotation, which has different gene models).
URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/GRCh37_mapping/gencode.v47lift37.basic.annotation.gtf.gz"
OUT = ROOT / "data/input/gencode_genes_hg19_stranded.json"


def main():
    print("Downloading GENCODE v47lift37 (hg19/GRCh37, with strand)...")
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

    # Sanity check against the empirically-confirmed NOC2L hg19 TSS
    noc2l = [g for g in genes if g["gene"] == "NOC2L"]
    print(f"  Sanity check NOC2L: {noc2l} (expect TSS near 894679/894689)")


if __name__ == "__main__":
    main()
