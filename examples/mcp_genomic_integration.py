"""Example: Integration of MCP Genomic Data Server with ARCHCODE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

from mcp_genomic_data.tools import (
    fetch_ctcf_chipseq,
    fetch_genomic_sequence,
    fetch_methylation_data,
    fetch_te_annotations,
    search_gene,
)
from src.archcode_core.pipeline import ARCHCODEPipeline, load_pipeline_configs
from src.boundary_stability import StabilityCalculator


async def main() -> None:
    """Example of MCP genomic data integration with ARCHCODE."""
    print("=" * 60)
    print("MCP Genomic Data + ARCHCODE Integration Example")
    print("=" * 60)

    # 1. Search for gene (MYC - oncogene)
    print("\n1. Searching for MYC gene...")
    myc_gene = await search_gene("MYC", assembly="hg38")
    print(f"   Found: {myc_gene['chromosome']}:{myc_gene['start']}-{myc_gene['end']}")

    # 2. Fetch genomic sequence around MYC
    print("\n2. Fetching genomic sequence...")
    sequence = await fetch_genomic_sequence(
        chromosome=myc_gene["chromosome"],
        start=myc_gene["start"] - 50000,
        end=myc_gene["end"] + 50000,
    )
    print(f"   Sequence length: {sequence['length']} bp")

    # 3. Fetch CTCF ChIP-seq data
    print("\n3. Fetching CTCF ChIP-seq data...")
    ctcf_data = await fetch_ctcf_chipseq(
        chromosome=myc_gene["chromosome"],
        start=myc_gene["start"] - 50000,
        end=myc_gene["end"] + 50000,
        cell_type="GM12878",
    )
    print(f"   Found {ctcf_data['total_peaks']} CTCF peaks")

    # 4. Fetch TE annotations
    print("\n4. Fetching TE annotations...")
    te_data = await fetch_te_annotations(
        chromosome=myc_gene["chromosome"],
        start=myc_gene["start"] - 50000,
        end=myc_gene["end"] + 50000,
    )
    print(f"   Found {te_data['total_elements']} TE elements")

    # 5. Fetch methylation data
    print("\n5. Fetching methylation data...")
    methylation_data = await fetch_methylation_data(
        chromosome=myc_gene["chromosome"],
        start=myc_gene["start"] - 50000,
        end=myc_gene["end"] + 50000,
    )
    print(f"   Found {methylation_data['total_sites']} CpG sites")

    # 6. Integrate with ARCHCODE Pipeline
    print("\n6. Integrating with ARCHCODE Pipeline...")
    archcode_config, stability_config = load_pipeline_configs()
    pipeline = ARCHCODEPipeline(
        archcode_config=archcode_config,
        stability_config=stability_config,
    )

    # Add boundaries from CTCF peaks
    for peak in ctcf_data["peaks"]:
        pipeline.add_boundary(
            position=peak["start"],
            strength=peak["strength"],
            barrier_type="ctcf",
        )

    # Calculate average methylation level
    avg_methylation = sum(
        site["methylation_level"] for site in methylation_data["cpg_sites"]
    ) / len(methylation_data["cpg_sites"])

    # Analyze stability for boundaries
    print("\n7. Analyzing boundary stability...")
    barrier_strengths_map = {}
    methylation_map = {}
    te_motif_map = {}

    for boundary in pipeline.boundaries:
        # Map methylation (simplified - use average)
        methylation_map[boundary.position] = avg_methylation

        # Map TE effects (simplified)
        te_effects = [0.1 if te["family"] == "LTR" else 0.0 for te in te_data["te_elements"]]
        te_motif_map[boundary.position] = te_effects[:2] if te_effects else []

    predictions = pipeline.analyze_all_boundaries(
        barrier_strengths_map=barrier_strengths_map,
        methylation_map=methylation_map,
        te_motif_map=te_motif_map,
    )

    print(f"\n   Analyzed {len(predictions)} boundaries:")
    for pred in predictions:
        print(
            f"   Position {pred.position}: "
            f"{pred.stability_category} (score={pred.stability_score:.3f})"
        )

    print("\n" + "=" * 60)
    print("✅ MCP + ARCHCODE Integration Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())








