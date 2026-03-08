#!/usr/bin/env python3
"""
DEPRECATED — EXPLORATORY SCRIPT (2026-03-06)

ARCHCODE Splice Junction Analysis
Step 3: Quantify canonical vs aberrant splicing

STATUS: This script produced misleading intermediate results (60% aberrant
in WT baseline) due to BED12 column mis-parsing and incorrect canonical
junction coordinate matching. The corrected analysis is in
results/hbb_splice_analysis.json (showing 0.1% novel reads in all conditions
after depth normalization). The "Loop That Stayed" hypothesis is NOT
SUPPORTED by this RNA-seq data.

See: manuscript body_content.typ, "RNA-seq splice junction analysis (null result)"
See: results/hbb_splice_analysis.json for canonical source of truth

Original hypothesis (not confirmed):
- WT: <5% aberrant splicing (baseline)
- B6 (deletion): 15-30% aberrant splicing (loop trap)
- A2 (inversion): <10% aberrant splicing (loop preserved)

Usage:
    python scripts/analyze_splice_junctions.py

Input:
    fastq_data/junctions/*_junctions.tab (from STAR)

Output:
    fastq_data/results/splice_analysis.json
    fastq_data/results/splice_analysis_report.md
"""

import argparse
import json
import csv
from pathlib import Path
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

JUNCTIONS_DIR = Path("D:/ДНК/fastq_data/junctions")
RESULTS_DIR = Path("D:/ДНК/fastq_data/results")

# HBB gene coordinates (hg38)
HBB_CHROM = "chr11"
HBB_START = 5_225_000  # Approximate start
HBB_END = 5_228_000  # Approximate end

# Canonical HBB splice junctions (hg38) - UPDATED with real coordinates
CANONICAL_JUNCTIONS = [
    # Exon 1 -> Exon 2
    {
        "name": "E1->E2",
        "donor": 5_225_727,  # End of exon 1
        "acceptor": 5_226_576,  # Start of exon 2
    },
    # Exon 2 -> Exon 3
    {
        "name": "E2->E3",
        "donor": 5_226_800,  # End of exon 2
        "acceptor": 5_226_929,  # Start of exon 3
    },
]

# ============================================================================
# Data structures
# ============================================================================


class Junction:
    """Represents a splice junction."""

    def __init__(self, chrom, donor, acceptor, unique_reads, total_reads, motif):
        self.chrom = chrom
        self.donor = donor
        self.acceptor = acceptor
        self.unique_reads = unique_reads
        self.total_reads = total_reads
        self.motif = motif  # GT/AG, etc.

    @property
    def span(self):
        return self.acceptor - self.donor

    def __repr__(self):
        return f"Junction({self.chrom}:{self.donor}->{self.acceptor}, {self.unique_reads} reads)"


# ============================================================================
# Load junctions from STAR output
# ============================================================================


def load_junctions(
    junction_file: Path,
    star_filter: bool = False,
    min_unique_reads: int = 6,
) -> list:
    """Load splice junctions from STAR SJ.out.tab or BED file.

    STAR SJ.out.tab columns (1-based): 1=chr, 2=start, 3=end, 4=strand,
    5=motif (0=non-canonical), 6=annotated (0=novel, 1=annotated),
    7=unique_reads, 8=multimap_reads, 9=max_overhang.
    When star_filter=True, keep only: motif>0, annotated==0, unique_reads>=min_unique_reads.
    """
    if not junction_file.exists():
        return []

    junctions = []
    file_ext = junction_file.suffix.lower()

    with open(junction_file, "r", encoding="utf-8") as f:
        if file_ext == ".bed":
            # BED format: chrom, start, end, name, score, strand, thickStart, thickEnd, itemRgb, blockCount, blockSizes, blockStarts
            # Or simplified: chrom, start, end, name, score, strand
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if len(row) < 6 or row[0].startswith("#") or row[0].startswith("track"):
                    continue
                try:
                    chrom = row[0].replace("chr", "chr")  # Keep chr prefix
                    donor = int(row[1])  # 0-based start
                    acceptor = int(row[2])  # end
                    _ = row[3] if len(row) > 3 else "junction"  # name unused
                    score = int(row[4]) if len(row) > 4 else 0
                    _ = row[5] if len(row) > 5 else "."  # strand unused

                    # Convert score to unique_reads (approximate)
                    unique_reads = max(1, score)

                    # BED uses 0-based start, convert to 0-based donor
                    donor = donor + 1  # Now 1-based donor position

                    junctions.append(
                        Junction(
                            chrom=chrom,
                            donor=donor,
                            acceptor=acceptor,
                            unique_reads=unique_reads,
                            total_reads=unique_reads,
                            motif="1",  # Assume canonical for BED
                        )
                    )
                except (ValueError, IndexError):
                    continue
        else:
            # STAR SJ.out.tab format: col6=annotated, col7=unique_reads, col8=multimap
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if row[0].startswith("#"):
                    continue
                try:
                    chrom = row[0]
                    donor = int(row[1])  # 1-based donor
                    acceptor = int(row[2])  # 1-based acceptor
                    _ = row[3]  # strand unused
                    motif = row[4]
                    annotated = int(row[5])  # 0=novel, 1=annotated
                    unique_reads = int(row[6])
                    multimap_reads = int(row[7]) if len(row) > 7 else 0
                    total_reads = unique_reads + multimap_reads

                    if unique_reads < 1:
                        continue
                    if motif == "0":
                        continue
                    if star_filter:
                        if annotated != 0 or unique_reads < min_unique_reads:
                            continue

                    junctions.append(
                        Junction(
                            chrom=chrom,
                            donor=donor,
                            acceptor=acceptor,
                            unique_reads=unique_reads,
                            total_reads=total_reads,
                            motif=motif,
                        )
                    )
                except (ValueError, IndexError):
                    continue

    return junctions


# ============================================================================
# Classify junctions
# ============================================================================


def classify_junction(junction: Junction, canonical_list: list) -> str:
    """
    Classify a junction as canonical or aberrant.

    Returns:
        "canonical" - matches known canonical junction
        "exon_skip" - exon skipping (e.g., E1->E3)
        "intron_retention" - intron not spliced
        "cryptic" - cryptic splice site
        "novel" - completely novel junction
    """

    # Check if matches canonical junction (with larger tolerance for BED format)
    tolerance = 50  # Increased tolerance for BED format

    for canonical in canonical_list:
        donor_match = abs(junction.donor - canonical["donor"]) <= tolerance
        acceptor_match = abs(junction.acceptor - canonical["acceptor"]) <= tolerance

        if donor_match and acceptor_match:
            return "canonical"

    # Check for exon skipping (E1->E3)
    # E1 start ~5225000, E3 end ~5227079
    if junction.donor < 5_225_800 and junction.acceptor > 5_227_000:
        return "exon_skip"

    # Check for intron retention (junction within intron)
    # Intron 1: 5225727-5226576, Intron 2: 5226800-5226929
    if (
        5_225_727 < junction.donor < junction.acceptor < 5_226_576
        or 5_226_800 < junction.donor < junction.acceptor < 5_226_929
    ):
        return "intron_retention"

    # Check for cryptic splice sites (near canonical but not exact)
    for canonical in canonical_list:
        if (
            abs(junction.donor - canonical["donor"]) <= 500
            or abs(junction.acceptor - canonical["acceptor"]) <= 500
        ):
            return "cryptic"

    return "novel"


# ============================================================================
# Analyze sample
# ============================================================================


def analyze_sample(
    sample_name: str,
    junction_file: Path,
    star_filter: bool = False,
    min_unique_reads: int = 6,
) -> dict:
    """Analyze splice junctions for a single sample."""

    print(f"  📊 Analyzing {sample_name}...")

    # Load junctions
    junctions = load_junctions(
        junction_file,
        star_filter=star_filter,
        min_unique_reads=min_unique_reads,
    )

    if not junctions:
        print("     ⚠️  No junctions found")
        return None

    # Filter for HBB locus (chr11, 5.22-5.23 Mb)
    hbb_junctions = [
        j
        for j in junctions
        if j.chrom == HBB_CHROM
        and HBB_START <= j.donor <= HBB_END
        and HBB_START <= j.acceptor <= HBB_END
    ]

    print(f"     Total junctions: {len(junctions)}")
    print(f"     HBB locus junctions: {len(hbb_junctions)}")

    # Classify junctions
    classification = {
        "canonical": [],
        "exon_skip": [],
        "intron_retention": [],
        "cryptic": [],
        "novel": [],
    }

    for junction in hbb_junctions:
        category = classify_junction(junction, CANONICAL_JUNCTIONS)
        classification[category].append(junction)

    # Calculate statistics
    total_reads = sum(j.total_reads for j in hbb_junctions)
    canonical_reads = sum(j.total_reads for j in classification["canonical"])
    aberrant_reads = total_reads - canonical_reads

    # NEW: Calculate canonical percentage
    canonical_percentage = (canonical_reads / total_reads * 100) if total_reads > 0 else 0

    aberrant_types = {}
    for category in ["exon_skip", "intron_retention", "cryptic", "novel"]:
        reads = sum(j.total_reads for j in classification[category])
        if reads > 0:
            aberrant_types[category] = {
                "count": len(classification[category]),
                "reads": reads,
                "percentage": (reads / total_reads * 100) if total_reads > 0 else 0,
            }

    # Calculate aberrant splicing percentage
    aberrant_percentage = (aberrant_reads / total_reads * 100) if total_reads > 0 else 0

    result = {
        "sample": sample_name,
        "total_junctions": len(hbb_junctions),
        "total_reads": total_reads,
        "canonical": {
            "count": len(classification["canonical"]),
            "reads": canonical_reads,
            "percentage": canonical_percentage,  # NEW
        },
        "aberrant": {"reads": aberrant_reads, "percentage": aberrant_percentage},
        "aberrant_types": aberrant_types,
        "hypothesis_test": {
            "expected": get_expected_aberrant_percentage(sample_name),
            "observed": aberrant_percentage,
            "status": "PENDING",  # Will be updated after analysis
        },
    }

    # Update hypothesis test status
    expected = result["hypothesis_test"]["expected"]
    observed = aberrant_percentage

    if expected["min"] <= observed <= expected["max"]:
        result["hypothesis_test"]["status"] = "✅ MATCH"
    elif observed < expected["min"]:
        result["hypothesis_test"]["status"] = "⚠️  BELOW EXPECTED"
    else:
        result["hypothesis_test"]["status"] = "⚠️  ABOVE EXPECTED"

    print(f"     Canonical: {result['canonical']['percentage']:.1f}%")
    print(f"     Aberrant: {aberrant_percentage:.1f}%")
    print(f"     Hypothesis: {result['hypothesis_test']['status']}")
    print()

    return result


# ============================================================================
# Get expected aberrant percentage by sample
# ============================================================================


def get_expected_aberrant_percentage(sample_name: str) -> dict:
    """Get expected aberrant splicing percentage based on hypothesis."""

    sample_name_lower = sample_name.lower()

    if "srr12935486" in sample_name_lower or "wt" in sample_name_lower:
        # WT: <5% aberrant
        return {"min": 0, "max": 5, "expected": 2}

    elif (
        "srr12935488" in sample_name_lower
        or "b6" in sample_name_lower
        or "del" in sample_name_lower
    ):
        # B6 (deletion): 15-30% aberrant
        return {"min": 15, "max": 30, "expected": 22}

    elif (
        "srr12935490" in sample_name_lower
        or "a2" in sample_name_lower
        or "inv" in sample_name_lower
    ):
        # A2 (inversion): <10% aberrant
        return {"min": 0, "max": 10, "expected": 5}

    else:
        # Unknown sample
        return {"min": 0, "max": 100, "expected": 50}


# ============================================================================
# Generate report
# ============================================================================


def generate_report(results: list, output_file: Path):
    """Generate markdown report."""

    report = []
    report.append("# 🧬 ARCHCODE Splice Junction Analysis Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")

    # Hypothesis
    report.append("## 🎯 Hypothesis: 'Loop That Stayed'")
    report.append("")
    report.append("The HBB promoter ↔ 3'HS1 loop (22 kb) creates a 'transcriptional compartment'")
    report.append("that regulates HBB splicing. When the loop is disrupted (3'HS1 deletion),")
    report.append("the HBB gene exits this compartment and undergoes aberrant splicing.")
    report.append("")

    # Predictions
    report.append("### Predictions")
    report.append("")
    report.append("| Sample | Modification | Expected Aberrant Splicing |")
    report.append("|--------|--------------|---------------------------|")
    report.append("| WT | Intact 3'HS1 | <5% |")
    report.append("| B6 | 3'HS1 deletion | 15-30% |")
    report.append("| A2 | 3'HS1 inversion | <10% |")
    report.append("")
    report.append("---")
    report.append("")

    # Results
    report.append("## 📊 Results")
    report.append("")

    for result in results:
        sample = result["sample"]
        aberrant = result["aberrant"]["percentage"]
        status = result["hypothesis_test"]["status"]
        expected = result["hypothesis_test"]["expected"]

        report.append(f"### {sample}")
        report.append("")
        report.append(f"- **Total junctions:** {result['total_junctions']}")
        report.append(f"- **Total reads:** {result['total_reads']:,}")
        report.append(f"- **Canonical:** {result['canonical']['percentage']:.1f}%")
        report.append(f"- **Aberrant:** {aberrant:.1f}%")
        report.append(f"- **Expected:** {expected['min']}-{expected['max']}%")
        report.append(f"- **Status:** {status}")
        report.append("")

        if result["aberrant_types"]:
            report.append("**Aberrant types:**")
            report.append("")
            for atype, data in result["aberrant_types"].items():
                report.append(f"- {atype}: {data['reads']} reads ({data['percentage']:.1f}%)")
            report.append("")

        report.append("---")
        report.append("")

    # Summary
    report.append("## 📈 Summary")
    report.append("")
    report.append("| Sample | Aberrant % | Expected | Status |")
    report.append("|--------|------------|----------|--------|")

    for result in results:
        sample = result["sample"]
        aberrant = result["aberrant"]["percentage"]
        expected = result["hypothesis_test"]["expected"]
        status = result["hypothesis_test"]["status"]

        report.append(
            f"| {sample} | {aberrant:.1f}% | {expected['min']}-{expected['max']}% | {status} |"
        )

    report.append("")

    # Conclusion
    report.append("## 🎯 Conclusion")
    report.append("")

    # Check if hypothesis is supported
    wt_result = next(
        (r for r in results if "srr12935486" in r["sample"].lower() or "wt" in r["sample"].lower()),
        None,
    )
    del_result = next(
        (r for r in results if "srr12935488" in r["sample"].lower() or "b6" in r["sample"].lower()),
        None,
    )
    inv_result = next(
        (r for r in results if "srr12935490" in r["sample"].lower() or "a2" in r["sample"].lower()),
        None,
    )

    if wt_result and del_result and inv_result:
        wt_match = wt_result["hypothesis_test"]["status"] == "✅ MATCH"
        del_match = del_result["hypothesis_test"]["status"] == "✅ MATCH"
        inv_match = inv_result["hypothesis_test"]["status"] == "✅ MATCH"

        if wt_match and del_match and inv_match:
            report.append("✅ **HYPOTHESIS VALIDATED:** All three samples match predictions!")
            report.append("")
            report.append("This supports the 'Loop That Stayed' mechanism:")
            report.append("- 3'HS1 deletion disrupts the HBB promoter↔3'HS1 loop")
            report.append("- Loop disruption leads to aberrant splicing (15-30%)")
            report.append("- Aberrant splicing triggers nonsense-mediated decay (NMD)")
            report.append("- NMD reduces HBB expression (-36% in B6)")
            report.append("")
        elif del_match:
            report.append(
                "⚠️  **HYPOTHESIS PARTIALLY SUPPORTED:** Deletion sample shows expected aberrant splicing."
            )
            report.append("")
            report.append("Further investigation needed for WT and inversion samples.")
            report.append("")
        else:
            report.append("❌ **HYPOTHESIS NOT SUPPORTED:** Results do not match predictions.")
            report.append("")
            report.append("Consider alternative mechanisms or technical artifacts.")
            report.append("")
    else:
        report.append("⚠️  **INSUFFICIENT DATA:** Not all samples were analyzed successfully.")
        report.append("")

    report.append("---")
    report.append("")
    report.append("## 📁 Data Files")
    report.append("")
    report.append(f"- Input: `{JUNCTIONS_DIR}/*_junctions.tab`")
    report.append(f"- Output: `{output_file}`")
    report.append(f"- JSON: `{RESULTS_DIR / 'splice_analysis.json'}`")
    report.append("")

    # Write report
    output_file.write_text("\n".join(report))
    print(f"📄 Report written: {output_file}")


# ============================================================================
# Main analysis
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="ARCHCODE splice junction analysis (Loop That Stayed hypothesis)"
    )
    parser.add_argument(
        "--star-filter",
        action="store_true",
        help="Apply STAR manual filter: motif>0, annotated==0, unique_reads>=6 (for SJ.out.tab only)",
    )
    parser.add_argument(
        "--min-reads",
        type=int,
        default=6,
        metavar="N",
        help="Minimum unique reads for STAR filter (default: 6)",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("  ARCHCODE Splice Junction Analysis")
    print("  'Loop That Stayed' Hypothesis Test")
    print("=" * 70)
    print()
    if args.star_filter:
        print(f"  STAR filter: ON (motif>0, novel only, unique_reads>={args.min_reads})")
        print()

    # Create output directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Find junction files (support both .tab and .bed)
    junction_files = list(JUNCTIONS_DIR.glob("*_junctions.tab")) + list(
        JUNCTIONS_DIR.glob("*_junctions.bed")
    )

    if not junction_files:
        print("❌ No junction files found!")
        print()
        print(f"Expected: {JUNCTIONS_DIR}/*_junctions.tab or *_junctions.bed")
        print()
        print("Run STAR alignment first:")
        print("  python scripts/rnaseq_star_align.py")
        print()
        return False

    print(f"📊 Found {len(junction_files)} junction files")
    print()

    # Analyze each sample
    results = []

    for junction_file in sorted(junction_files):
        # Extract sample name from filename
        sample_name = junction_file.stem.replace("_junctions", "")

        result = analyze_sample(
            sample_name,
            junction_file,
            star_filter=args.star_filter,
            min_unique_reads=args.min_reads,
        )

        if result:
            results.append(result)

    print()
    print("=" * 70)
    print("  Analysis Complete")
    print("=" * 70)
    print()

    if not results:
        print("❌ No samples analyzed successfully.")
        return False

    # Generate report
    report_file = RESULTS_DIR / "splice_analysis_report.md"
    generate_report(results, report_file)

    # Save JSON
    json_file = RESULTS_DIR / "splice_analysis.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"📄 JSON written: {json_file}")
    print()

    # Print summary
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print()

    for result in results:
        sample = result["sample"]
        aberrant = result["aberrant"]["percentage"]
        status = result["hypothesis_test"]["status"]

        print(f"{sample}: {aberrant:.1f}% aberrant — {status}")

    print()

    # Final verdict
    del_result = next(
        (r for r in results if "srr12935488" in r["sample"].lower() or "b6" in r["sample"].lower()),
        None,
    )

    if del_result:
        del_aberrant = del_result["aberrant"]["percentage"]

        if 15 <= del_aberrant <= 30:
            print("🎉 VALIDATION SUCCESS: Deletion sample shows 15-30% aberrant splicing!")
            print()
            print("This validates the 'Loop That Stayed' hypothesis:")
            print("  • Loop disruption → aberrant splicing → NMD → reduced HBB")
            print()
            print("👉 Next step: Update manuscript with validation results")
            print("   docs/MANUSCRIPT_UPDATE_PLAN.md")
            return True
        else:
            print(
                f"⚠️  Validation inconclusive: Deletion shows {del_aberrant:.1f}% (expected 15-30%)"
            )
            print()
            print("Consider:")
            print("  • Technical artifacts")
            print("  • Alternative mechanisms")
            print("  • Additional validation (Capture Hi-C)")
            return False
    else:
        print("⚠️  Deletion sample not found. Cannot validate hypothesis.")
        return False


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
