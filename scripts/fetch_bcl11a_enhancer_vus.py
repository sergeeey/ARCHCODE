#!/usr/bin/env python3
"""
exp_bcl11a_enhancer_vus: are there ClinVar VUS in the known BCL11A erythroid enhancer
(Canver et al. 2015 Nature, DHS +55/+58/+62, ~12kb intronic region) that are candidates
for the same HbF-modifying mechanism as common GWAS SNPs (rs1427407 etc, Bauer et al.
2013 Science)?

Anchor: rs1427407 confirmed via Ensembl VEP GRCh37 REST API at chr2:60,718,043 (hg19),
consistent with its published "+62kb from TSS" naming (BCL11A TSS chr2:60,781,602, minus
strand). Window covers all 3 DHS sites (+55/+58/+62) with margin.

This is a DESCRIPTIVE/discovery experiment (EstimandOps L0: descriptive), not a hypothesis
test with a p-value -- the goal is to flag candidate variants for follow-up, not to test an
enrichment. Reports ALL VUS found in the window, regardless of count (0 is a valid, reportable
outcome, not a failure).
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
OUT = ROOT / "experiments/exp_bcl11a_enhancer_vus/clinvar_enhancer_variants.json"

# BCL11A erythroid enhancer, hg19/GRCh37, anchored on rs1427407 (VEP-confirmed chr2:60,718,043)
ENHANCER_CHROM = "chr2"
ENHANCER_START = 60_710_000
ENHANCER_END = 60_732_000


def main() -> None:
    print("Downloading ClinVar variant_summary.txt.gz...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    all_variants = []
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
            if chrom != ENHANCER_CHROM:
                continue
            try:
                start = int(row[col["Start"]])
                stop = int(row[col["Stop"]])
            except (ValueError, KeyError):
                continue
            if not (ENHANCER_START <= start <= ENHANCER_END):
                continue

            key = (chrom, start, stop)
            if key in seen:
                continue
            seen.add(key)

            variant = {
                "chrom": chrom,
                "start": start,
                "end": stop,
                "type": row[col.get("Type", -1)],
                "sig": row[col.get("ClinicalSignificance", -1)],
                "gene_symbol": row[col.get("GeneSymbol", -1)],
                "name": row[col.get("Name", -1)],
                "position_vcf": row[col.get("PositionVCF", -1)] if "PositionVCF" in col else None,
                "ref_vcf": row[col.get("ReferenceAlleleVCF", -1)]
                if "ReferenceAlleleVCF" in col
                else None,
                "alt_vcf": row[col.get("AlternateAlleleVCF", -1)]
                if "AlternateAlleleVCF" in col
                else None,
                "rs_number": row[col.get("RS# (dbSNP)", -1)] if "RS# (dbSNP)" in col else None,
            }
            all_variants.append(variant)

    print(
        f"  Found {len(all_variants)} ClinVar entries in the enhancer window "
        f"(chr2:{ENHANCER_START}-{ENHANCER_END})"
    )
    for v in all_variants:
        dist_from_rs1427407 = abs(int(v["start"]) - 60_718_043) if v.get("start") else None
        print(
            f"    {v['chrom']}:{v['start']} [{v['sig']}] {v['name']} "
            f"(gene={v['gene_symbol']}, ~{dist_from_rs1427407}bp from rs1427407)"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": "ClinVar variant_summary.txt.gz (NCBI FTP)",
                "window": f"{ENHANCER_CHROM}:{ENHANCER_START}-{ENHANCER_END} (hg19, BCL11A DHS+55/+58/+62)",
                "anchor": "rs1427407 at chr2:60,718,043 (VEP-confirmed, Bauer et al. 2013 Science)",
                "n_variants": len(all_variants),
                "variants": all_variants,
            },
            f,
            indent=2,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
