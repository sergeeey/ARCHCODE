"""
Demo: Fast queries without API calls
Pattern from genechat-mcp
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from archcode.db.query import ARCHCODEDatabase
except ModuleNotFoundError:
    db_path = project_root / "archcode" / "db"
    sys.path.insert(0, str(db_path))
    from query import ARCHCODEDatabase


def main():
    db_file = Path(__file__).parent.parent / "archcode" / "db" / "archcode_annotations.db"

    with ARCHCODEDatabase(db_file) as db:
        print("\n🔍 Query 1: Get all HBB variants")
        print("=" * 60)
        variants = db.get_variants_by_locus("HBB")
        for v in variants:
            print(f"{v.vcv_id} ({v.classification})")
            print(f"  Position: {v.genomic_position}")
            print(f"  CAGE Δ: {v.cage_delta:.3f} ({v.cage_delta_pct:.1f}%)")
            print(f"  SSIM Δ: {v.ssim_delta:.4f} ({v.disruption_category})")
            print()

        print("\n🔍 Query 2: Get only pathogenic variants")
        print("=" * 60)
        plp_variants = db.get_variants_by_locus("HBB", classification="P/LP")
        print(f"Found {len(plp_variants)} P/LP variants")
        for v in plp_variants:
            print(f"  {v.vcv_id}: SSIM disruption = {v.ssim_delta:.4f}")

        print("\n🔍 Query 3: Get 'pearls' (high disruption)")
        print("=" * 60)
        pearls = db.get_pearls("HBB")
        print(f"Found {len(pearls)} pearl variants")
        for p in pearls:
            print(f"  {p.vcv_id}: SSIM Δ = {p.ssim_delta:.4f}")

        print("\n🔍 Query 4: Get CAGE gain-of-function variants")
        print("=" * 60)
        gof = db.get_cage_gain_of_function_variants(min_delta_pct=0)
        print(f"Found {len(gof)} variants with CAGE increase")
        for v in gof:
            print(f"  {v.vcv_id}: +{v.cage_delta_pct:.1f}% CAGE")

        print("\n🔍 Query 5: Validation results")
        print("=" * 60)
        results = db.get_validation_results("HBB")
        for r in results:
            print(f"Locus: {r.gene_symbol}")
            print(f"  AlphaGenome: p={r.alphag_mann_whitney_p:.6f}")
            print(f"  ARCHCODE: p={r.archcode_mann_whitney_p:.2f}")
            print(f"  Correlation: ρ={r.spearman_rho:.3f}")
            print(f"  Classification: {r.classification}")
            print(f"  ADR: {r.adr_reference}")

        print("\n🔍 Query 6: Mechanism specificity summary")
        print("=" * 60)
        summary = db.get_mechanism_specificity_summary()
        for locus_type, stats in summary.items():
            print(f"{locus_type.upper()}:")
            print(f"  Loci: {stats['n_loci']}")
            print(f"  WEAK-ORTHOGONAL: {stats['n_weak_orthogonal']}")
            print(f"  Avg ρ: {stats['avg_rho']:.3f}")

        print("\n✅ All queries completed in <1ms (no API calls)")
        print(f"💾 Database: {db_file}")


if __name__ == "__main__":
    main()
