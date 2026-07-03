#!/usr/bin/env python3
"""
Fetch genome-wide ClinVar VUS (Uncertain significance) variants.

Unlike prior ARCHCODE-SV work, which filtered to strict Pathogenic/Benign
structural variants only, this script keeps ALL variant types (SNV, indel,
etc.) with ClinicalSignificance == "Uncertain significance" exactly (no
conflicting, no "Uncertain significance/other"), genome-wide, for the
exp_orphan_enhancers experiment.

Also extracts per-gene ClinVar submission counts (all significances) as a
confound-control covariate (proxy for how heavily a gene/region has been
clinically sequenced).
"""

import gzip
import io
import json
import os
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
OUT_VUS = ROOT / "data/input/clinvar_vus_genomewide.json"
OUT_GENE_COUNTS = ROOT / "data/input/clinvar_gene_submission_counts.json"


def main() -> None:
    if OUT_VUS.exists() and OUT_GENE_COUNTS.exists():
        print(f"Already cached: {OUT_VUS}, {OUT_GENE_COUNTS}")
        return

    print("Downloading ClinVar variant_summary.txt.gz (~440MB decompressed)...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    vus_variants = []
    gene_submission_counts = Counter()
    seen = set()

    with gzip.open(io.BytesIO(raw)) as gz:
        header = gz.readline().decode().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        for line in gz:
            row = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(row) <= max(col.values()):
                continue
            assembly = row[col.get("Assembly", -1)] if "Assembly" in col else ""
            if assembly != "GRCh38":
                continue
            chrom_raw = row[col["Chromosome"]]
            if chrom_raw in ("", "na", "Un") or "|" in chrom_raw:
                continue
            chrom = "chr" + chrom_raw if not chrom_raw.startswith("chr") else chrom_raw

            gene = row[col.get("GeneSymbol", -1)] if "GeneSymbol" in col else ""
            if gene and gene != "-":
                gene_submission_counts[gene.split("|")[0]] += 1

            sig = row[col.get("ClinicalSignificance", -1)] if "ClinicalSignificance" in col else ""
            if sig.strip() != "Uncertain significance":
                continue

            try:
                start = int(row[col["Start"]])
                stop = int(row[col["Stop"]])
            except (ValueError, KeyError):
                continue

            key = (chrom, start, stop)
            if key in seen:
                continue
            seen.add(key)

            vus_variants.append(
                {
                    "chrom": chrom,
                    "start": start,
                    "end": stop,
                    "gene": gene.split("|")[0] if gene and gene != "-" else None,
                    "type": row[col.get("Type", -1)] if "Type" in col else "",
                    "name": row[col.get("Name", -1)] if "Name" in col else "",
                }
            )

    print(f"  VUS variants (genome-wide, GRCh38): {len(vus_variants)}")
    print(f"  Genes with >=1 ClinVar submission: {len(gene_submission_counts)}")

    with open(OUT_VUS, "w") as f:
        json.dump(
            {
                "source": "ClinVar variant_summary.txt.gz (NCBI FTP)",
                "filter": "ClinicalSignificance == 'Uncertain significance' exactly, GRCh38, genome-wide, all variant types",
                "n": len(vus_variants),
                "variants": vus_variants,
            },
            f,
        )
    print(f"  Saved: {OUT_VUS}")

    with open(OUT_GENE_COUNTS, "w") as f:
        json.dump(dict(gene_submission_counts), f)
    print(f"  Saved: {OUT_GENE_COUNTS}")


if __name__ == "__main__":
    main()
