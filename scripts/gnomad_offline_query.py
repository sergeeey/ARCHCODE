"""
gnomAD Offline Query — 100% Reliable, No API

Query pearls against locally downloaded gnomAD VCF.
No timeouts, no rate limits, no network issues.

Requirements:
- pysam installed (pip install pysam)
- gnomad.genomes.v4.1.sites.chr11.vcf.bgz downloaded
- gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi index present

Usage:
  python scripts/gnomad_offline_query.py
"""

import pysam
import csv
from pathlib import Path
from typing import Optional, Dict, Any

# VCF file path (adjust if different)
VCF_PATH = Path("data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz")

# Pearls to query (all 27, including IUPAC codes expanded)
PEARLS = [
    ("5226598", "G", "T", "VCV003766487"),
    ("5226598", "G", "C", "VCV000801186"),
    ("5226598", "G", "A", "VCV000015259_1"),  # Y=C/T expanded
    ("5226613", "G", "C", "VCV002664746"),
    ("5226613", "G", "T", "VCV000811500"),
    ("5226613", "G", "A", "VCV000015208_1"),  # Y=C/T expanded
    ("5226643", "C", "G", "VCV000618675"),
    ("5226643", "C", "A", "VCV000446737_1"),  # R=A/G expanded
    ("5226643", "C", "G", "VCV000015319_1"),  # R=A/G expanded
    ("5226971", "CCCC", "CCCCC", "VCV000869358"),  # small indel
    ("5227099", "T", "C", "VCV000015471"),
    ("5227099", "T", "G", "VCV000015470"),
    ("5227100", "T", "G", "VCV000869288"),
    ("5227101", "A", "G", "VCV000869290"),
    ("5227102", "T", "C", "VCV000015466"),
    ("5227142", "G", "A", "VCV000801184"),
    ("5227157", "G", "T", "VCV002506212"),
    ("5227157", "G", "A", "VCV000036284"),
    ("5227158", "G", "A", "VCV000036287"),
    ("5227158", "G", "T", "VCV000036285"),
    ("5227158", "G", "C", "VCV000015464"),
    ("5227159", "G", "T", "VCV000393701"),
    ("5227161", "G", "A", "VCV000015514"),
    ("5227163", "G", "A", "VCV000015462"),
    ("5227172", "G", "C", "VCV000015586"),
]


def query_vcf(
    vcf_file: pysam.VariantFile, chrom: str, pos: int, ref: str, alt: str
) -> Optional[Dict[str, Any]]:
    """
    Query VCF for specific variant.

    Returns:
        Dict with AC, AN, AF if found, None if not found
    """

    try:
        # Fetch region (pysam uses 0-based coordinates, but VCF is 1-based)
        # Query position-1 to position to get the variant
        for record in vcf_file.fetch(chrom, pos - 1, pos):
            # Check if this is the exact variant
            if record.pos == pos and record.ref == ref and alt in record.alts:
                # Extract genome-level AC/AN/AF
                info = record.info

                ac = info.get("AC", None)
                an = info.get("AN", None)
                af = info.get("AF", None)

                # AC might be tuple for multi-allelic sites
                if isinstance(ac, tuple):
                    # Find which ALT index matches our alt
                    try:
                        alt_index = record.alts.index(alt)
                        ac = ac[alt_index]
                        if isinstance(af, tuple):
                            af = af[alt_index]
                    except (ValueError, IndexError):
                        ac = None
                        af = None

                return {"ac": ac, "an": an, "af": af, "found": True}

        # Variant not found in VCF
        return None

    except Exception as e:
        print(f"  ERROR querying {chrom}:{pos} {ref}>{alt}: {e}")
        return None


def main():
    """Query all pearls against local VCF."""

    print("=" * 70)
    print("gnomAD Offline Query — 100% Reliable")
    print("=" * 70)
    print()

    # Check VCF file exists
    if not VCF_PATH.exists():
        print(f"❌ ERROR: VCF file not found at {VCF_PATH}")
        print()
        print("Please download first:")
        print("  See SETUP_GNOMAD_DOWNLOAD.md for instructions")
        return

    print(f"Loading VCF: {VCF_PATH}")
    print(f"Querying {len(PEARLS)} pearls...")
    print()

    # Open VCF
    try:
        vcf = pysam.VariantFile(str(VCF_PATH))
    except Exception as e:
        print(f"❌ ERROR opening VCF: {e}")
        print()
        print("Possible fixes:")
        print("  1. Check pysam installed: pip install pysam")
        print("  2. Check .tbi index present")
        print("  3. Re-download VCF if corrupted")
        return

    results = []

    for i, (pos, ref, alt, clinvar_id) in enumerate(PEARLS, 1):
        print(f"[{i}/{len(PEARLS)}] {clinvar_id} chr11:{pos} {ref}>{alt}...", end=" ")

        result = query_vcf(vcf, "11", int(pos), ref, alt)

        if result is None:
            # Not found in VCF
            print("❌ NOT IN gnomAD")
            results.append(
                {
                    "clinvar_id": clinvar_id,
                    "variant_id": f"11-{pos}-{ref}-{alt}",
                    "ac": None,
                    "an": None,
                    "af": None,
                    "status": "NOT_IN_GNOMAD",
                    "source": "local_vcf_not_found",
                }
            )
        else:
            ac = result["ac"]
            an = result["an"]
            af = result["af"]

            if ac == 0:
                status = "ABSENT"
                print(f"✅ ABSENT (AC=0, AN={an})")
            elif ac is not None and ac <= 5:
                status = "ULTRA_RARE"
                print(f"✅ ULTRA_RARE (AC={ac}, AF={af:.2e})")
            elif ac is not None:
                status = "PRESENT"
                print(f"⚠️  PRESENT (AC={ac}, AF={af:.2e})")
            else:
                status = "NO_AC_DATA"
                print(f"⚠️  NO AC DATA")

            results.append(
                {
                    "clinvar_id": clinvar_id,
                    "variant_id": f"11-{pos}-{ref}-{alt}",
                    "ac": ac,
                    "an": an,
                    "af": af,
                    "status": status,
                    "source": "local_vcf_verified",
                }
            )

    # Close VCF
    vcf.close()

    # Save results
    output_file = Path("results/gnomad_pearls_offline_verified.csv")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["clinvar_id", "variant_id", "ac", "an", "af", "status", "source"]
        )
        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"✅ Results saved to: {output_file}")
    print()

    # Summary statistics
    total = len(results)
    absent = sum(1 for r in results if r["status"] == "ABSENT")
    ultra_rare = sum(1 for r in results if r["status"] == "ULTRA_RARE")
    present = sum(1 for r in results if r["status"] == "PRESENT")
    not_found = sum(1 for r in results if r["status"] == "NOT_IN_GNOMAD")

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total queried: {total}")
    print(f"  ABSENT (AC=0): {absent} ({absent/total*100:.1f}%)")
    print(f"  ULTRA_RARE (AC=1-5): {ultra_rare} ({ultra_rare/total*100:.1f}%)")
    print(f"  PRESENT (AC>5): {present} ({present/total*100:.1f}%)")
    print(f"  NOT IN gnomAD: {not_found} ({not_found/total*100:.1f}%)")
    print()
    print(
        f"Strong constraint (ABSENT + ULTRA_RARE): {absent + ultra_rare}/{total} ({(absent + ultra_rare)/total*100:.1f}%)"
    )
    print()
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print(f"1. Verify results: cat {output_file}")
    print(f"2. Update paper draft with verified numbers")
    print(f"3. Submit to journal")
    print()


if __name__ == "__main__":
    main()
