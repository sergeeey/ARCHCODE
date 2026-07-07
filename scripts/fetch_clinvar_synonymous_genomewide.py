#!/usr/bin/env python3
"""exp_synonymous_codon_optimality: fetch ClinVar SNVs genome-wide (GRCh37)
that are synonymous (silent) coding changes, strict Pathogenic/Likely
pathogenic vs Benign/Likely benign, identified directly from ClinVar's own
`Name` protein-change notation (e.g. p.Val352Val, or p.Val352=) -- no VEP
consequence call needed for this filtering step (VEP is used later, only to
fetch REF/ALT codon triplets for the variants that pass this filter).
"""

import gzip
import io
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
OUT = ROOT / "data/input/clinvar_synonymous_variants.json"

PATH_SIGS = {"Pathogenic", "Likely pathogenic"}
BENIGN_SIGS = {"Benign", "Likely benign"}

# p.Val352Val (explicit same-aa) or p.Val352= (ClinVar's synonymous shorthand)
SYNONYMOUS_RE = re.compile(r"p\.([A-Za-z]{3})(\d+)(=|[A-Za-z]{3})\)")


def is_synonymous(name: str) -> bool:
    m = SYNONYMOUS_RE.search(name)
    if not m:
        return False
    ref_aa, _pos, alt_aa = m.groups()
    return alt_aa == "=" or alt_aa.lower() == ref_aa.lower()


def main() -> None:
    print("Downloading ClinVar variant_summary.txt.gz...")
    with urllib.request.urlopen(CLINVAR_URL, timeout=300) as resp:
        raw = resp.read()
    print(f"  Downloaded {len(raw) // 1_000_000}MB, parsing...")

    result = {"pathogenic": [], "benign": []}
    seen = set()
    n_scanned = 0
    n_snv = 0
    n_synonymous_candidates = 0

    with gzip.open(io.BytesIO(raw)) as gz:
        header = gz.readline().decode().strip().split("\t")
        col = {h: i for i, h in enumerate(header)}
        for line in gz:
            n_scanned += 1
            row = line.decode("utf-8", errors="ignore").strip().split("\t")
            if len(row) <= max(col.values()):
                continue
            if row[col.get("Assembly", -1)] != "GRCh37":
                continue
            if row[col.get("Type", -1)] != "single nucleotide variant":
                continue
            n_snv += 1

            name = row[col.get("Name", -1)]
            if not is_synonymous(name):
                continue
            n_synonymous_candidates += 1

            sig = row[col.get("ClinicalSignificance", -1)]
            words = {w.strip() for w in sig.split("/")}
            is_path = bool(words & PATH_SIGS) and not (words & BENIGN_SIGS)
            is_benign = bool(words & BENIGN_SIGS) and not (words & PATH_SIGS)
            if not (is_path or is_benign):
                continue

            chrom_raw = row[col["Chromosome"]]
            chrom = "chr" + chrom_raw if not chrom_raw.startswith("chr") else chrom_raw
            try:
                start = int(row[col["Start"]])
            except (ValueError, KeyError):
                continue

            pos_vcf = row[col.get("PositionVCF", -1)] if "PositionVCF" in col else None
            ref_vcf = (
                row[col.get("ReferenceAlleleVCF", -1)] if "ReferenceAlleleVCF" in col else None
            )
            alt_vcf = (
                row[col.get("AlternateAlleleVCF", -1)] if "AlternateAlleleVCF" in col else None
            )

            key = (chrom, start, pos_vcf, ref_vcf, alt_vcf)
            if key in seen:
                continue
            seen.add(key)

            variant = {
                "chrom": chrom,
                "start": start,
                "gene_symbol": row[col.get("GeneSymbol", -1)],
                "name": name,
                "sig": sig,
                "position_vcf": pos_vcf,
                "ref_vcf": ref_vcf,
                "alt_vcf": alt_vcf,
            }
            (result["pathogenic"] if is_path else result["benign"]).append(variant)

    print(
        f"  Scanned {n_scanned} rows, {n_snv} GRCh37 SNVs, "
        f"{n_synonymous_candidates} synonymous-name-pattern candidates"
    )
    print(
        f"  Final: {len(result['pathogenic'])} pathogenic, {len(result['benign'])} benign "
        f"(strict P/B, excl. VUS/conflicting)"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": "ClinVar variant_summary.txt.gz (NCBI FTP)",
                "filter": "GRCh37 SNV, Name field indicates synonymous (p.XxxNNNXxx same aa, or p.XxxNNN=), strict Pathogenic/Benign",
                "n_pathogenic": len(result["pathogenic"]),
                "n_benign": len(result["benign"]),
                "variants": result,
            },
            f,
            indent=2,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
