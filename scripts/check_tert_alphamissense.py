#!/usr/bin/env python3
"""
Check AlphaMissense scores for TERT C228T and C250T hotspots

Hypothesis: AlphaMissense will classify these as ambiguous/benign
because they are absent from gnomAD (somatic, not germline).

TERT hotspots (GRCh38):
- C228T: chr5:1295228 C>T (creates ETS binding site)
- C250T: chr5:1295250 C>T (creates ETS binding site)

AlphaGenome CAGE results (from 2026-05-09):
- C228T: +33.7% CAGE increase (gain-of-function)
- C250T: +53.1% CAGE increase (gain-of-function)
"""

import gzip
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
AM_FILE = PROJECT_ROOT / "data" / "alphamissense" / "AlphaMissense_hg38.tsv.gz"

# TERT hotspots (GRCh38 coordinates)
HOTSPOTS = {
    "C228T": {"chr": "5", "pos": 1295228, "ref": "C", "alt": "T", "vcv": "VCV001299388"},
    "C250T": {"chr": "5", "pos": 1295250, "ref": "C", "alt": "T", "vcv": "VCV002443072"},
}

# AlphaGenome results for comparison
ALPHAGENOME_RESULTS = {
    "C228T": {"cage_delta_pct": 33.7, "interpretation": "gain-of-function"},
    "C250T": {"cage_delta_pct": 53.1, "interpretation": "gain-of-function"},
}


def parse_alphamissense_line(line: str) -> dict:
    """
    Parse AlphaMissense TSV line.

    Format (header):
    #CHROM  POS  REF  ALT  genome  uniprot_id  transcript_id  protein_variant
    am_pathogenicity  am_class
    """
    parts = line.strip().split("\t")
    if len(parts) < 10:
        return None

    return {
        "chrom": parts[0],
        "pos": int(parts[1]),
        "ref": parts[2],
        "alt": parts[3],
        "genome": parts[4],
        "uniprot_id": parts[5],
        "transcript_id": parts[6],
        "protein_variant": parts[7],
        "am_pathogenicity": float(parts[8]) if parts[8] != "." else None,
        "am_class": parts[9] if parts[9] != "." else None,
    }


def find_hotspot_scores():
    """Extract AlphaMissense scores for TERT C228T and C250T."""

    if not AM_FILE.exists():
        print(f"ERROR: AlphaMissense file not found: {AM_FILE}")
        print("Run download first.")
        sys.exit(1)

    print("Searching AlphaMissense predictions for TERT hotspots...")
    print(f"File: {AM_FILE}")
    print()

    found = {name: None for name in HOTSPOTS.keys()}

    with gzip.open(AM_FILE, "rt") as f:
        for i, line in enumerate(f):
            if line.startswith("#"):
                continue

            row = parse_alphamissense_line(line)
            if not row:
                continue

            # Check if this is a TERT hotspot
            for name, hotspot in HOTSPOTS.items():
                if (
                    row["chrom"] == hotspot["chr"]
                    and row["pos"] == hotspot["pos"]
                    and row["ref"] == hotspot["ref"]
                    and row["alt"] == hotspot["alt"]
                ):
                    found[name] = row
                    print(
                        f"✓ Found {name} (chr{hotspot['chr']}:{hotspot['pos']} {hotspot['ref']}>{hotspot['alt']})"
                    )

            # Early exit if both found
            if all(v is not None for v in found.values()):
                print(f"\nBoth hotspots found after {i+1} lines.")
                break

    return found


def print_results(found: dict):
    """Print comparison table."""

    print("\n" + "=" * 80)
    print("TERT HOTSPOTS: AlphaMissense vs AlphaGenome")
    print("=" * 80)
    print()

    for name in ["C228T", "C250T"]:
        hotspot = HOTSPOTS[name]
        am_row = found[name]
        ag_result = ALPHAGENOME_RESULTS[name]

        print(f"## {name} — chr{hotspot['chr']}:{hotspot['pos']} {hotspot['ref']}>{hotspot['alt']}")
        print(f"ClinVar: {hotspot['vcv']}")
        print()

        if am_row:
            print(f"AlphaMissense:")
            print(f"  Pathogenicity: {am_row['am_pathogenicity']:.4f}")
            print(f"  Class:         {am_row['am_class']}")
            print(f"  Protein:       {am_row['protein_variant']}")
            print(f"  Transcript:    {am_row['transcript_id']}")
        else:
            print(f"AlphaMissense: NOT FOUND")
            print(f"  → Variant is non-coding or outside AlphaMissense scope")

        print()
        print(f"AlphaGenome CAGE:")
        print(f"  Delta:         {ag_result['cage_delta_pct']:+.1f}%")
        print(f"  Interpretation: {ag_result['interpretation']}")
        print()

        # Analysis
        if am_row:
            am_class = am_row["am_class"]
            if am_class in ["likely_benign", "ambiguous"]:
                print(f"⚠️  AlphaMissense BLIND SPOT CONFIRMED")
                print(f"    AlphaMissense: {am_class} (missed gain-of-function)")
                print(
                    f"    AlphaGenome:   {ag_result['interpretation']} (+{ag_result['cage_delta_pct']:.1f}% CAGE)"
                )
                print(f"    → Population-frequency-based models miss somatic hotspots")
            else:
                print(f"✓  AlphaMissense detected pathogenicity")
                print(f"    But mechanism is CAGE gain-of-function, not protein disruption")
        else:
            print(f"⚠️  AlphaMissense BLIND SPOT CONFIRMED (non-coding)")
            print(f"    AlphaMissense: no prediction (promoter region)")
            print(
                f"    AlphaGenome:   {ag_result['interpretation']} (+{ag_result['cage_delta_pct']:.1f}% CAGE)"
            )
            print(f"    → AlphaMissense scope limited to coding variants")

        print()
        print("-" * 80)
        print()


def main():
    found = find_hotspot_scores()
    print_results(found)

    # Save results
    output_file = PROJECT_ROOT / "results" / "tert_alphamissense_check.json"
    import json

    result = {
        "hotspots": {},
        "hypothesis": "AlphaMissense classifies TERT C228T/C250T as ambiguous/benign (somatic blind spot)",
        "date": "2026-05-09",
    }

    for name in ["C228T", "C250T"]:
        hotspot = HOTSPOTS[name]
        am_row = found[name]
        ag_result = ALPHAGENOME_RESULTS[name]

        result["hotspots"][name] = {
            "position": f"chr{hotspot['chr']}:{hotspot['pos']}",
            "variant": f"{hotspot['ref']}>{hotspot['alt']}",
            "clinvar_id": hotspot["vcv"],
            "alphamissense": {
                "found": am_row is not None,
                "pathogenicity": am_row["am_pathogenicity"] if am_row else None,
                "class": am_row["am_class"] if am_row else None,
                "protein_variant": am_row["protein_variant"] if am_row else None,
            },
            "alphagenome": {
                "cage_delta_pct": ag_result["cage_delta_pct"],
                "interpretation": ag_result["interpretation"],
            },
            "blind_spot_confirmed": (
                am_row is None or am_row["am_class"] in ["likely_benign", "ambiguous"]
            ),
        }

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Results saved: {output_file}")


if __name__ == "__main__":
    main()
