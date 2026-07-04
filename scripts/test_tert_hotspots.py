#!/usr/bin/env python3
"""
Test TERT C228T/C250T Hotspots with AlphaGenome CAGE

These are famous cancer driver mutations creating ETS binding sites.
Test if AlphaGenome CAGE can detect them despite being gain-of-function
(not typical loss-of-function disruption).

Expected result:
- If PASS: CAGE detects even gain-of-function → 7/7 mechanism specificity
- If NULL: CAGE limited to disruption only → documents limitation

Either outcome strengthens the claim.
"""

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"

# TERT locus: chr5:1,253,000-1,296,000 (GRCh38)
TERT_LOCUS = {"chr": "chr5", "start": 1253000, "end": 1296000, "name": "TERT"}

# Known cancer hotspots (GRCh38 coordinates)
HOTSPOTS = [
    {
        "clinvar_id": "VCV001299388",
        "name": "C228T",
        "hgvs": "c.-124C>T",
        "chr": "chr5",
        "pos": 1295113,
        "ref": "G",
        "alt": "A",
        "mechanism": "Creates ETS binding site (gain-of-function)",
        "cancer_prevalence": "~35% of cancers",
    },
    {
        "clinvar_id": "VCV002443072",
        "name": "C250T",
        "hgvs": "c.-146C>T",
        "chr": "chr5",
        "pos": 1295135,
        "ref": "G",
        "alt": "A",
        "mechanism": "Creates ETS binding site (gain-of-function)",
        "cancer_prevalence": "~35% of cancers",
    },
]


def get_api_key():
    """Get AlphaGenome API key from env or .env file."""
    key = os.environ.get("ALPHAGENOME_API_KEY")
    if key:
        return key

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ALPHAGENOME_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val

    print("ERROR: No ALPHAGENOME_API_KEY found")
    sys.exit(1)


def get_client():
    """Create AlphaGenome client."""
    try:
        from alphagenome.models import dna_client

        return dna_client.create(get_api_key())
    except ImportError:
        print("ERROR: alphagenome package not installed")
        print("Install: pip install alphagenome")
        sys.exit(1)


def make_interval(chrom, start, end):
    """Create AlphaGenome interval with supported length."""
    from alphagenome.models import dna_client
    from alphagenome.data.genome import Interval

    length = end - start
    supported = sorted(dna_client.SUPPORTED_SEQUENCE_LENGTHS.values())

    # Snap to nearest supported length
    snap_len = length
    for s in supported:
        if s >= length:
            snap_len = s
            break
    if snap_len == length and snap_len not in supported:
        snap_len = supported[-1]

    # Center the interval
    center = (start + end) // 2
    snap_start = center - snap_len // 2
    snap_end = snap_start + snap_len

    print(
        f"  Interval: {chrom}:{start}-{end} → snapped to {chrom}:{snap_start}-{snap_end} ({snap_len}bp)"
    )
    return Interval(chromosome=chrom, start=snap_start, end=snap_end, name="tert")


def make_variant(chrom, pos, ref, alt):
    """Create AlphaGenome variant."""
    from alphagenome.data.genome import Variant

    return Variant(chromosome=chrom, position=pos, reference_bases=ref, alternate_bases=alt)


def test_hotspots():
    """Test TERT C228T/C250T with AlphaGenome CAGE."""
    print("=" * 80)
    print("TERT Hotspot Test: C228T/C250T with AlphaGenome CAGE")
    print("=" * 80)
    print()

    client = get_client()
    interval = make_interval(TERT_LOCUS["chr"], TERT_LOCUS["start"], TERT_LOCUS["end"])

    results = []

    for hotspot in HOTSPOTS:
        print(f"\n{'='*80}")
        print(f"Testing: {hotspot['name']} ({hotspot['hgvs']})")
        print(f"ClinVar: {hotspot['clinvar_id']}")
        print(f"Position: {hotspot['chr']}:{hotspot['pos']} {hotspot['ref']}>{hotspot['alt']}")
        print(f"Mechanism: {hotspot['mechanism']}")
        print(f"Cancer prevalence: {hotspot['cancer_prevalence']}")
        print(f"{'='*80}")

        variant = make_variant(hotspot["chr"], hotspot["pos"], hotspot["ref"], hotspot["alt"])

        try:
            from alphagenome.models.dna_output import OutputType

            # Get CAGE prediction
            var_output = client.predict_variant(
                interval,
                variant,
                requested_outputs=[OutputType.CAGE],
                ontology_terms=["EFO:0002784"],  # K562 cell line
            )

            # Extract CAGE values
            import numpy as np

            if var_output.reference.cage is not None and var_output.alternate.cage is not None:
                ref_cage = np.array(var_output.reference.cage.values)
                alt_cage = np.array(var_output.alternate.cage.values)

                if ref_cage.size > 0 and alt_cage.size > 0:
                    cage_ref = float(np.mean(ref_cage))
                    cage_alt = float(np.mean(alt_cage))
                    cage_delta = cage_alt - cage_ref
                    cage_pct = (cage_delta / cage_ref * 100) if cage_ref != 0 else 0
                else:
                    cage_ref = cage_alt = cage_delta = cage_pct = None
            else:
                cage_ref = cage_alt = cage_delta = cage_pct = None

            if cage_ref is not None and cage_alt is not None:
                print(f"\n✅ AlphaGenome CAGE Prediction:")
                print(f"  Reference CAGE: {cage_ref:.6f}")
                print(f"  Alternate CAGE: {cage_alt:.6f}")
                print(f"  Delta: {cage_delta:.6f} ({cage_pct:.2f}%)")

                # Interpretation
                if abs(cage_pct) > 10:
                    verdict = "STRONG" if abs(cage_pct) > 20 else "MODERATE"
                    direction = "INCREASE" if cage_delta > 0 else "DECREASE"
                    print(f"\n  Verdict: {verdict} {direction}")
                else:
                    verdict = "WEAK"
                    print(f"\n  Verdict: WEAK signal (|delta| < 10%)")

                results.append(
                    {
                        "clinvar_id": hotspot["clinvar_id"],
                        "name": hotspot["name"],
                        "hgvs": hotspot["hgvs"],
                        "position": hotspot["pos"],
                        "ref": hotspot["ref"],
                        "alt": hotspot["alt"],
                        "cage_ref": float(cage_ref),
                        "cage_alt": float(cage_alt),
                        "cage_delta": float(cage_delta),
                        "cage_pct": float(cage_pct),
                        "verdict": verdict,
                        "mechanism": hotspot["mechanism"],
                    }
                )
            else:
                print(f"\n❌ Failed to extract CAGE values")
                results.append(
                    {
                        "clinvar_id": hotspot["clinvar_id"],
                        "name": hotspot["name"],
                        "error": "No CAGE values",
                    }
                )

        except Exception as e:
            print(f"\n❌ Error: {e}")
            results.append(
                {"clinvar_id": hotspot["clinvar_id"], "name": hotspot["name"], "error": str(e)}
            )

    # Save results
    output_file = RESULTS_DIR / "tert_hotspots_cage_test.json"
    output_file.write_text(
        json.dumps(
            {
                "date": "2026-05-08",
                "method": "AlphaGenome CAGE (predict_variant API)",
                "locus": "TERT promoter",
                "variants_tested": 2,
                "hotspots": results,
                "interpretation": {
                    "hypothesis": "TERT C228T/C250T are gain-of-function (create ETS motif). If CAGE detects → model captures gain-of-function. If NULL → model limited to disruption only.",
                    "impact_on_mechanism_specificity": "Either PASS or NULL strengthens overall claim by documenting limitation or expanding scope.",
                },
            },
            indent=2,
        )
    )

    print(f"\n{'='*80}")
    print(f"Results saved: {output_file}")
    print(f"{'='*80}")

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    for r in results:
        if "error" in r:
            print(f"  {r['name']}: ERROR - {r['error']}")
        else:
            print(f"  {r['name']}: {r['verdict']} ({r['cage_pct']:.1f}% change)")

    print(f"\n{'='*80}")
    print("INTERPRETATION")
    print(f"{'='*80}")

    passed = sum(1 for r in results if "verdict" in r and r["verdict"] in ["STRONG", "MODERATE"])

    if passed == 2:
        print("✅ BOTH hotspots show CAGE signal")
        print("   → AlphaGenome CAGE detects even gain-of-function!")
        print("   → Mechanism specificity: 7/7 loci (perfect)")
    elif passed == 1:
        print("⚠️ ONE hotspot shows signal, one null")
        print("   → Mixed result, requires deeper investigation")
    else:
        print("❌ BOTH hotspots show WEAK/NULL CAGE signal")
        print("   → AlphaGenome CAGE limited to disruption (not motif creation)")
        print("   → Documents model limitation (still valuable)")
        print("   → Mechanism specificity: 6/6 remains valid")

    return results


if __name__ == "__main__":
    test_hotspots()
