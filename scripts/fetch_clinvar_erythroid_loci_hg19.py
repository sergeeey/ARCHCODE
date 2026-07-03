#!/usr/bin/env python3
"""
Fetch ClinVar strict Pathogenic/Benign SNV/indel variants at BCL11A, KLF1, GATA1
(hg19/GRCh37), for exp_enhancer_proximity_replication.

Window: gene body +-50kb (captures known regulatory elements, e.g. the BCL11A
erythroid enhancer targeted by Casgevy is intronic, well within this window).
"""

import gzip
import io
import json
import os
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
OUT = ROOT / "data/input/clinvar_erythroid_loci_hg19.json"

FLANK = 50_000
LOCI = {
    "BCL11A": ("chr2", 60_677_655 - FLANK, 60_781_602 + FLANK),
    "KLF1": ("chr19", 12_995_236 - FLANK, 12_998_015 + FLANK),
    "GATA1": ("chrX", 48_644_948 - FLANK, 48_652_718 + FLANK),
}

PATH_SIGS = {"Pathogenic", "Likely pathogenic"}
BENIGN_SIGS = {"Benign", "Likely benign"}


def main() -> None:
    print("Downloading ClinVar variant_summary.txt.gz...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    result = {name: {"pathogenic": [], "benign": []} for name in LOCI}
    seen = set()

    with gzip.open(io.BytesIO(raw)) as gz:
        header = gz.readline().decode().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        for line in gz:
            row = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(row) <= max(col.values()):
                continue
            if row[col.get("Assembly", -1)] != "GRCh37":
                continue
            chrom_raw = row[col["Chromosome"]]
            chrom = "chr" + chrom_raw if not chrom_raw.startswith("chr") else chrom_raw

            for name, (locus_chrom, lo, hi) in LOCI.items():
                if chrom != locus_chrom:
                    continue
                try:
                    start = int(row[col["Start"]])
                    stop = int(row[col["Stop"]])
                except (ValueError, KeyError):
                    continue
                if not (lo <= start <= hi):
                    continue

                gene_symbols = {g.strip() for g in row[col.get("GeneSymbol", -1)].split("|")}
                if name not in gene_symbols:
                    continue

                sig = row[col.get("ClinicalSignificance", -1)]
                words = {w.strip() for w in sig.split("/")}
                is_path = bool(words & PATH_SIGS) and not (words & BENIGN_SIGS)
                is_benign = bool(words & BENIGN_SIGS) and not (words & PATH_SIGS)
                if not (is_path or is_benign):
                    continue

                vtype = row[col.get("Type", -1)]
                key = (name, chrom, start, stop)
                if key in seen:
                    continue
                seen.add(key)

                variant = {
                    "chrom": chrom,
                    "start": start,
                    "end": stop,
                    "type": vtype,
                    "sig": sig,
                    "name": row[col.get("Name", -1)],
                    "position_vcf": row[col.get("PositionVCF", -1)] if "PositionVCF" in col else None,
                    "ref_vcf": row[col.get("ReferenceAlleleVCF", -1)] if "ReferenceAlleleVCF" in col else None,
                    "alt_vcf": row[col.get("AlternateAlleleVCF", -1)] if "AlternateAlleleVCF" in col else None,
                }
                if is_path:
                    result[name]["pathogenic"].append(variant)
                else:
                    result[name]["benign"].append(variant)
                break  # a variant belongs to at most one locus window here

    for name in LOCI:
        n_p = len(result[name]["pathogenic"])
        n_b = len(result[name]["benign"])
        print(f"  {name}: {n_p} pathogenic, {n_b} benign")

    with open(OUT, "w") as f:
        json.dump(
            {
                "source": "ClinVar variant_summary.txt.gz (NCBI FTP)",
                "filter": "strict Pathogenic/Benign, GRCh37, gene body +-50kb",
                "loci": LOCI,
                "variants": result,
            },
            f,
            indent=2,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
