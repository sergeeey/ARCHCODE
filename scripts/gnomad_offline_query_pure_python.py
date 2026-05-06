"""
gnomAD Offline Query — Pure Python (No Dependencies)

Works with only Python stdlib (gzip). No pysam, no bcftools needed.
Slower than pysam but 100% compatible with Windows.

Requirements:
- Python 3.7+
- Downloaded VCF: data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz
- Index file: data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz.tbi

Usage:
  python scripts/gnomad_offline_query_pure_python.py
"""

import gzip
import csv
from pathlib import Path
from typing import Optional, Dict, Any

# VCF file path
VCF_PATH = Path("data/gnomad.genomes.v4.1.sites.chr11.vcf.bgz")

# Pearls to query (all 25, including IUPAC codes expanded)
PEARLS = [
    ("5226598", "G", "T", "VCV003766487"),
    ("5226598", "G", "C", "VCV000801186"),
    ("5226598", "G", "A", "VCV000015259_1"),  # Y=C/T expanded
    ("5226613", "G", "C", "VCV002664746"),
    ("5226613", "G", "T", "VCV000811500"),
    ("5226613", "G", "A", "VCV000015208_1"),  # Y=C/T expanded
    ("5226643", "C", "G", "VCV000618675"),
    ("5226643", "C", "A", "VCV000446737_1"),  # R=A/G expanded
    ("5226643", "C", "G", "VCV000015319_1"),  # R=A/G expanded (duplicate G?)
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


def parse_info_field(info_str: str) -> Dict[str, Any]:
    """Parse VCF INFO field into dict."""
    info = {}
    for item in info_str.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            info[key] = value
        else:
            info[item] = True
    return info


def query_vcf_sequential(
    vcf_path: Path, target_pos: int, ref: str, alt: str
) -> Optional[Dict[str, Any]]:
    """
    Query VCF for specific variant (sequential scan).

    WARNING: This is SLOW for full chr11 VCF (24GB).
    Only practical for small region queries.

    Returns:
        Dict with AC, AN, AF if found, None if not found
    """
    with gzip.open(vcf_path, "rt") as f:
        for line in f:
            # Skip header lines
            if line.startswith("#"):
                continue

            fields = line.strip().split("\t")
            if len(fields) < 8:
                continue

            chrom = fields[0]
            pos = int(fields[1])
            vcf_ref = fields[3]
            vcf_alts = fields[4].split(",")
            info_str = fields[7]

            # Check if this is our variant
            if pos == target_pos and vcf_ref == ref and alt in vcf_alts:
                info = parse_info_field(info_str)

                # Get AC, AN, AF
                ac = info.get("AC")
                an = info.get("AN")
                af = info.get("AF")

                # Handle multi-allelic sites
                if ac and "," in ac:
                    alt_index = vcf_alts.index(alt)
                    ac_values = ac.split(",")
                    ac = int(ac_values[alt_index]) if alt_index < len(ac_values) else None
                    if af and "," in af:
                        af_values = af.split(",")
                        af = float(af_values[alt_index]) if alt_index < len(af_values) else None
                else:
                    ac = int(ac) if ac else None
                    af = float(af) if af else None

                an = int(an) if an else None

                return {"ac": ac, "an": an, "af": af, "found": True}

            # Early exit if we passed the target position
            # (VCF is sorted by position)
            if pos > target_pos:
                break

    return None


def query_vcf_region(
    vcf_path: Path, target_pos: int, ref: str, alt: str, window: int = 1000
) -> Optional[Dict[str, Any]]:
    """
    Query VCF with region filtering (faster but still sequential).

    Reads only lines within ±window bp of target position.
    Still slow for full chr11 but better than full scan.
    """
    start_pos = target_pos - window
    end_pos = target_pos + window

    with gzip.open(vcf_path, "rt") as f:
        in_region = False

        for line in f:
            if line.startswith("#"):
                continue

            fields = line.strip().split("\t")
            if len(fields) < 8:
                continue

            pos = int(fields[1])

            # Skip until we reach the region
            if pos < start_pos:
                continue

            # We're in the region
            if start_pos <= pos <= end_pos:
                in_region = True

                vcf_ref = fields[3]
                vcf_alts = fields[4].split(",")
                info_str = fields[7]

                # Check if this is our variant
                if pos == target_pos and vcf_ref == ref and alt in vcf_alts:
                    info = parse_info_field(info_str)

                    ac = info.get("AC")
                    an = info.get("AN")
                    af = info.get("AF")

                    # Handle multi-allelic
                    if ac and "," in ac:
                        alt_index = vcf_alts.index(alt)
                        ac_values = ac.split(",")
                        ac = int(ac_values[alt_index]) if alt_index < len(ac_values) else None
                        if af and "," in af:
                            af_values = af.split(",")
                            af = float(af_values[alt_index]) if alt_index < len(af_values) else None
                    else:
                        ac = int(ac) if ac else None
                        af = float(af) if af else None

                    an = int(an) if an else None

                    return {"ac": ac, "an": an, "af": af, "found": True}

            # Exit if we passed the region
            elif pos > end_pos and in_region:
                break

    return None


def main():
    """Query all pearls against local VCF."""

    print("=" * 70)
    print("gnomAD Offline Query — Pure Python (No Dependencies)")
    print("=" * 70)
    print()

    # Check VCF file exists
    if not VCF_PATH.exists():
        print(f"❌ ERROR: VCF file not found at {VCF_PATH}")
        print()
        print("Please download first:")
        print("  See SETUP_GNOMAD_DOWNLOAD.md for instructions")
        return

    vcf_size_gb = VCF_PATH.stat().st_size / (1024**3)
    print(f"Loading VCF: {VCF_PATH} ({vcf_size_gb:.1f} GB)")
    print(f"Querying {len(PEARLS)} pearls...")
    print()
    print("⚠️  WARNING: This uses sequential scan (no tabix index)")
    print("   Expected time: ~5-10 minutes for all 25 pearls")
    print()

    results = []

    for i, (pos, ref, alt, clinvar_id) in enumerate(PEARLS, 1):
        print(f"[{i}/{len(PEARLS)}] {clinvar_id} chr11:{pos} {ref}>{alt}...", end=" ", flush=True)

        # Query with region filtering (±1000bp window)
        result = query_vcf_region(VCF_PATH, int(pos), ref, alt, window=1000)

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
                    "source": "local_vcf_pure_python",
                }
            )

    # Save results
    output_file = Path("results/gnomad_pearls_offline_verified.csv")
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["clinvar_id", "variant_id", "ac", "an", "af", "status", "source"],
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
        f"Strong constraint (ABSENT + ULTRA_RARE): {absent + ultra_rare}/{total} "
        f"({(absent + ultra_rare)/total*100:.1f}%)"
    )
    print()
    print("=" * 70)
    print("PERFORMANCE NOTE")
    print("=" * 70)
    print("This script uses sequential scan (no tabix index).")
    print("For faster queries, install pysam or bcftools.")
    print()


if __name__ == "__main__":
    main()
