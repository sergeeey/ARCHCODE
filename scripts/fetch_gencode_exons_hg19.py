#!/usr/bin/env python3
"""exp_synonymous_codon_optimality sensitivity check: fetch GENCODE v47lift37
(hg19/GRCh37) exon boundaries genome-wide, to compute each ClinVar variant's
distance to the nearest exon/intron boundary (splice-proximity confound
control -- synonymous variants near a splice junction can be pathogenic via
splicing disruption, not codon optimality; see claim.md sensitivity check).

Same source/build as scripts/fetch_gencode_hg19_stranded.py (which fetches
gene-level records only) -- this script filters for "exon" feature rows
instead of "gene" rows from the same GTF.
"""

import gzip
import io
import json
import os
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_47/GRCh37_mapping/gencode.v47lift37.basic.annotation.gtf.gz"
OUT = ROOT / "data/input/gencode_exon_boundaries_hg19.json"


def main() -> None:
    print("Downloading GENCODE v47lift37 (hg19/GRCh37) for exon boundaries...")
    with urllib.request.urlopen(URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  {len(raw) // 1_000_000}MB downloaded, parsing exon rows...")

    boundaries_by_chrom = defaultdict(set)
    n_exons = 0
    with gzip.open(io.BytesIO(raw)) as gz:
        for line in gz:
            line = line.decode("utf-8", errors="ignore")
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            if len(cols) < 9 or cols[2] != "exon":
                continue
            n_exons += 1
            chrom, start, end = cols[0], int(cols[3]), int(cols[4])
            boundaries_by_chrom[chrom].add(start)
            boundaries_by_chrom[chrom].add(end)

    print(
        f"  {n_exons} exon rows -> {sum(len(v) for v in boundaries_by_chrom.values())} unique boundary positions"
    )

    out = {chrom: sorted(positions) for chrom, positions in boundaries_by_chrom.items()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": URL,
                "note": "unique exon start+end genomic positions per chromosome, hg19/GRCh37, GENCODE v47lift37 basic",
                "boundaries_by_chrom": out,
            },
            f,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
