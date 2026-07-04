#!/usr/bin/env python3
"""
Batch ARCHCODE Auto-Config Pipeline

Generates locus configs for a list of clinically important genes.

Usage:
  python scripts/batch_auto_config.py                     # default gene list
  python scripts/batch_auto_config.py --genes MYC,FGFR3   # custom list
  python scripts/batch_auto_config.py --file genes.txt     # from file (one per line)
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Import pipeline
sys.path.insert(0, str(Path(__file__).parent))
from auto_config_pipeline import generate_config

PROJECT = Path(__file__).parent.parent

# Clinically important genes with known regulatory architecture
# Prioritized by: ClinVar variant count, known enhancers, clinical relevance
DEFAULT_GENES = [
    # Tier 1: High ClinVar count, well-characterized regulatory elements
    "HBA1",    # alpha-thalassemia, super-enhancer, same pathway as HBB
    "MYC",     # cancer super-enhancer, most studied 3D locus
    "BCL11A",  # HbF repressor, sickle cell therapeutic target
    "SOX9",    # campomelic dysplasia, desert enhancers 1Mb away
    "SHH",     # holoprosencephaly, ZRS enhancer 1Mb away
    # Tier 2: Strong regulatory biology
    "GATA1",   # X-linked anemia, erythroid TF
    "KLF1",    # hereditary spherocytosis, erythroid TF
    "PAX6",    # aniridia, long-range enhancers
    "FGFR3",   # achondroplasia, craniosynostosis
    "RB1",     # retinoblastoma, tumor suppressor
    # Tier 3: Cardiac/neuro with ENCODE data
    "KCNQ1",   # long QT, imprinted locus
    "MECP2",   # Rett syndrome, X-linked
    "FMR1",    # fragile X, CGG expansion
    "DMD",     # Duchenne, largest human gene
    "NF1",     # neurofibromatosis, complex regulatory
    # Tier 4: Additional cancer genes
    "APC",     # familial polyposis
    "PTEN",    # cowden syndrome
    "RET",     # MEN2, super-enhancer
    "RUNX1",   # AML, erythroid context
    "ETV6",    # leukemia, translocation partner
]


def main():
    parser = argparse.ArgumentParser(description="Batch ARCHCODE Auto-Config")
    parser.add_argument("--genes", help="Comma-separated gene list")
    parser.add_argument("--file", help="File with gene names (one per line)")
    parser.add_argument("--cell-type", default="K562", help="Default cell type")
    parser.add_argument("--padding", type=int, default=150000, help="Padding in bp")
    parser.add_argument("--resolution", type=int, default=1000, help="Resolution in bp")
    parser.add_argument("--skip-existing", action="store_true", help="Skip genes with existing configs")
    args = parser.parse_args()

    if args.genes:
        genes = [g.strip() for g in args.genes.split(",")]
    elif args.file:
        with open(args.file) as f:
            genes = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    else:
        genes = DEFAULT_GENES

    config_dir = PROJECT / "config" / "locus"
    results = {"success": [], "failed": [], "skipped": []}

    print(f"Batch config generation: {len(genes)} genes")
    print(f"Cell type: {args.cell_type}, Padding: {args.padding}bp, Resolution: {args.resolution}bp")
    print("=" * 60)

    for i, gene in enumerate(genes, 1):
        print(f"\n[{i}/{len(genes)}] Processing {gene}...")

        # Check existing
        if args.skip_existing:
            existing = list(config_dir.glob(f"{gene.lower()}_*.json"))
            if existing:
                print(f"   SKIPPED: {existing[0].name} already exists")
                results["skipped"].append(gene)
                continue

        try:
            config = generate_config(
                gene_symbol=gene,
                cell_type=args.cell_type,
                padding=args.padding,
                resolution_bp=args.resolution,
            )
            results["success"].append({
                "gene": gene,
                "config_id": config["id"],
                "ctcf_count": len(config["features"]["ctcf_sites"]),
                "enhancer_count": len(config["features"]["enhancers"]),
                "gene_count": len(config["features"]["genes"]),
            })
            time.sleep(1)  # rate limit between genes
        except Exception as e:
            print(f"   FAILED: {e}")
            results["failed"].append({"gene": gene, "error": str(e)})
            time.sleep(1)

    # Summary
    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    print("=" * 60)
    print(f"Success: {len(results['success'])}")
    print(f"Failed:  {len(results['failed'])}")
    print(f"Skipped: {len(results['skipped'])}")

    if results["success"]:
        print("\nGenerated configs:")
        for r in results["success"]:
            print(f"  {r['gene']:10s} → {r['config_id']:20s} (CTCF: {r['ctcf_count']}, Enh: {r['enhancer_count']}, Genes: {r['gene_count']})")

    if results["failed"]:
        print("\nFailed:")
        for r in results["failed"]:
            print(f"  {r['gene']:10s} → {r['error'][:60]}")

    # Save summary
    summary_path = PROJECT / "results" / "batch_config_summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSummary saved: {summary_path}")


if __name__ == "__main__":
    main()
