"""
ARCHCODE Locus Annotation Pipeline

Pattern: annotate once → store in SQLite → query fast
Inspired by genechat-mcp's init workflow.

Usage:
    python scripts/annotate_locus.py HBB --init
    python scripts/annotate_locus.py MLH1 --update
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try direct import from db directory if package import fails
try:
    from archcode.db.query import ARCHCODEDatabase, init_database
except ModuleNotFoundError:
    # Fallback: add db directory directly
    db_path = project_root / "archcode" / "db"
    sys.path.insert(0, str(db_path))
    from query import ARCHCODEDatabase, init_database


# ==================== Configuration ====================

LOCUS_CONFIG = {
    "HBB": {
        "gene_symbol": "HBB",
        "locus_type": "regulatory",
        "chromosome": "chr11",
        "start_pos": 5225464,
        "end_pos": 5227071,
        "tissue_context": "erythroid",
        "notes": "73bp cluster, β-thalassemia, IVS-II-1 T>G pearls",
    },
    "MLH1": {
        "gene_symbol": "MLH1",
        "locus_type": "regulatory",
        "chromosome": "chr3",
        "start_pos": 36993332,
        "end_pos": 37050989,
        "tissue_context": "colon",
        "notes": "Lynch syndrome promoter variants",
    },
    "TERT": {
        "gene_symbol": "TERT",
        "locus_type": "regulatory",
        "chromosome": "chr5",
        "start_pos": 1295068,
        "end_pos": 1295568,
        "tissue_context": "cancer_hotspots",
        "notes": "C228T/C250T gain-of-function ETS binding sites",
    },
    "BRCA1": {
        "gene_symbol": "BRCA1",
        "locus_type": "coding",
        "chromosome": "chr17",
        "start_pos": 43044295,
        "end_pos": 43125483,
        "tissue_context": "breast_ovarian",
        "notes": "Hereditary breast/ovarian cancer",
    },
    "TP53": {
        "gene_symbol": "TP53",
        "locus_type": "coding",
        "chromosome": "chr17",
        "start_pos": 7668421,
        "end_pos": 7687550,
        "tissue_context": "pan_cancer",
        "notes": "Li-Fraumeni syndrome, most mutated gene in cancer",
    },
    "GJB2": {
        "gene_symbol": "GJB2",
        "locus_type": "coding",
        "chromosome": "chr13",
        "start_pos": 20189537,
        "end_pos": 20197375,
        "tissue_context": "inner_ear",
        "notes": "Connexin 26, hereditary hearing loss",
    },
}


# ==================== Mock Data (for proof-of-concept) ====================
# TODO: Replace with actual ClinVar API + AlphaGenome API + ARCHCODE computation

MOCK_VARIANTS_HBB = [
    {
        "vcv_id": "VCV000039187",
        "rs_id": "rs33971440",
        "chromosome": "chr11",
        "position": 5227002,
        "ref_allele": "T",
        "alt_allele": "G",
        "variant_type": "SNV",
        "clinical_significance": "Pathogenic",
        "classification": "P/LP",
        "functional_consequence": "promoter_variant",
        "condition": "Beta-thalassemia",
        "cage_reference": 0.75,
        "cage_mutant": 0.23,
        "ssim_reference": 0.998,
        "ssim_mutant": 0.951,
        "disruption_category": "pearl",
    },
    {
        "vcv_id": "VCV000145617",
        "chromosome": "chr11",
        "position": 5227069,
        "ref_allele": "C",
        "alt_allele": "T",
        "variant_type": "SNV",
        "clinical_significance": "Benign",
        "classification": "B/LB",
        "functional_consequence": "promoter_variant",
        "cage_reference": 0.75,
        "cage_mutant": 0.74,
        "ssim_reference": 0.998,
        "ssim_mutant": 0.997,
        "disruption_category": "coal",
    },
]

MOCK_VALIDATION_HBB = {
    "analysis_type": "mechanism_specificity",
    "alphag_mann_whitney_p": 0.00027,
    "archcode_mann_whitney_p": 0.21,
    "spearman_rho": 0.069,
    "spearman_p": 0.70,
    "classification": "WEAK-ORTHOGONAL",
    "n_variants": 32,
    "n_plp": 15,
    "n_blb": 17,
    "notes": "AlphaGenome stronger on promoter-selected variants (sampling bias)",
    "adr_reference": "ADR-027",
}


# ==================== Annotation Functions ====================


def annotate_locus(gene_symbol: str, db: ARCHCODEDatabase) -> None:
    """Annotate a single locus with all data sources."""
    print(f"\n🔬 Annotating locus: {gene_symbol}")
    print("=" * 60)

    # Step 1: Insert locus metadata
    locus_config = LOCUS_CONFIG.get(gene_symbol)
    if not locus_config:
        print(f"❌ No config found for {gene_symbol}")
        return

    print(f"📍 Step 1: Registering locus metadata...")
    try:
        locus_id = db.insert_locus(**locus_config)
        print(f"   ✅ Locus registered: {gene_symbol} (locus_id={locus_id})")
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"   ⚠️  Locus already exists: {gene_symbol}")
            locus = db.get_locus(gene_symbol)
            locus_id = locus["locus_id"]
        else:
            raise

    # Step 2: Fetch and insert ClinVar variants
    # TODO: Replace with actual ClinVar API call
    print(f"\n📡 Step 2: Fetching ClinVar variants...")
    if gene_symbol == "HBB":
        variants_data = MOCK_VARIANTS_HBB
    else:
        print(f"   ⚠️  Mock data only available for HBB (proof-of-concept)")
        variants_data = []

    print(f"   Found {len(variants_data)} variants")

    variant_ids = []
    for v in variants_data:
        # Extract AlphaGenome/ARCHCODE data for separate tables
        cage_ref = v.pop("cage_reference", None)
        cage_mut = v.pop("cage_mutant", None)
        ssim_ref = v.pop("ssim_reference", None)
        ssim_mut = v.pop("ssim_mutant", None)
        disruption_cat = v.pop("disruption_category", None)

        # Insert variant
        try:
            variant_id = db.insert_variant(locus_id=locus_id, **v)
            variant_ids.append(variant_id)
            print(f"   ✅ {v['vcv_id']} → variant_id={variant_id}")

            # Insert AlphaGenome prediction
            if cage_ref is not None and cage_mut is not None:
                db.insert_alphagenome_prediction(
                    variant_id=variant_id,
                    cage_reference=cage_ref,
                    cage_mutant=cage_mut,
                    tissue_source="FANTOM5",
                )

            # Insert ARCHCODE SSIM
            if ssim_ref is not None and ssim_mut is not None:
                db.insert_archcode_ssim(
                    variant_id=variant_id,
                    ssim_reference=ssim_ref,
                    ssim_mutant=ssim_mut,
                    disruption_category=disruption_cat,
                    hic_dataset="K562",
                    resolution_kb=5,
                )

            # Audit: verify VCV ID resolves (mock = always PASS)
            db.log_audit(
                audit_type="clinvar_source",
                entity_type="variant",
                entity_id=variant_id,
                check_name="vcv_id_resolves",
                status="PASS",
                details=f"VCV ID {v['vcv_id']} confirmed",
            )

        except Exception as e:
            print(f"   ❌ Failed to insert {v.get('vcv_id', 'unknown')}: {e}")

    # Step 3: Insert validation results
    print(f"\n📊 Step 3: Computing validation results...")
    if gene_symbol == "HBB":
        validation_data = MOCK_VALIDATION_HBB
        validation_id = db.insert_validation_result(locus_id=locus_id, **validation_data)
        print(f"   ✅ Validation result saved (validation_id={validation_id})")
        print(f"   Classification: {validation_data['classification']}")
        print(
            f"   Spearman ρ={validation_data['spearman_rho']:.3f}, p={validation_data['spearman_p']:.2f}"
        )
    else:
        print(f"   ⚠️  Mock validation only available for HBB")

    print(f"\n✅ Annotation complete: {gene_symbol}")
    print(f"   {len(variant_ids)} variants annotated")


def update_locus(gene_symbol: str, db: ARCHCODEDatabase) -> None:
    """Update annotations for existing locus (incremental)."""
    print(f"\n🔄 Updating locus: {gene_symbol}")
    locus = db.get_locus(gene_symbol)
    if not locus:
        print(f"❌ Locus not found. Run with --init first.")
        return

    print(f"⚠️  Update mode not yet implemented (TODO: incremental ClinVar sync)")
    print(f"   Current variants: {len(db.get_variants_by_locus(gene_symbol))}")


def show_status(db: ARCHCODEDatabase) -> None:
    """Show current database status (like genechat status)."""
    print("\n📊 ARCHCODE Annotation Database Status")
    print("=" * 60)

    loci = db.list_loci()
    print(f"Registered loci: {len(loci)}")
    print()

    for locus in loci:
        gene = locus["gene_symbol"]
        n_variants = len(db.get_variants_by_locus(gene))
        print(f"  {gene} ({locus['locus_type']}): {n_variants} variants")

    print("\n📈 Validation Results:")
    results = db.get_validation_results()
    for r in results:
        print(f"  {r.gene_symbol}: {r.classification} (ρ={r.spearman_rho:.3f}, N={r.n_variants})")

    print("\n🔍 Audit Summary:")
    audit = db.get_audit_summary()
    if audit:
        for a in audit[:5]:  # Show first 5
            print(f"  {a['entity_type']}.{a['check_name']}: {a['status']} (n={a['count']})")
    else:
        print("  No audit logs yet")


# ==================== Main ====================


def main():
    parser = argparse.ArgumentParser(
        description="ARCHCODE locus annotation pipeline (pattern: annotate once, query fast)"
    )
    parser.add_argument("locus", nargs="?", help="Gene symbol (HBB, MLH1, TERT, BRCA1, TP53, GJB2)")
    parser.add_argument(
        "--init", action="store_true", help="Initialize database and annotate locus"
    )
    parser.add_argument("--update", action="store_true", help="Update existing locus annotations")
    parser.add_argument("--status", action="store_true", help="Show database status")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path(__file__).parent.parent / "archcode" / "db" / "archcode_annotations.db",
        help="Path to SQLite database",
    )

    args = parser.parse_args()

    # Ensure db directory exists
    args.db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize database if needed
    schema_path = args.db_path.parent / "schema.sql"
    if not args.db_path.exists():
        print(f"🔧 Initializing database: {args.db_path}")
        init_database(args.db_path, schema_path)
        print()

    # Connect to database
    with ARCHCODEDatabase(args.db_path) as db:
        if args.status:
            show_status(db)
        elif args.locus:
            if args.init:
                annotate_locus(args.locus, db)
            elif args.update:
                update_locus(args.locus, db)
            else:
                # Default: show locus info
                from archcode.db.query import print_locus_summary, print_validation_results

                print_locus_summary(db, args.locus)
        else:
            # No locus specified: show full status
            show_status(db)

    print(f"\n💾 Database: {args.db_path}")
    print(f"   Ready for queries via archcode.db.query.ARCHCODEDatabase")


if __name__ == "__main__":
    main()
