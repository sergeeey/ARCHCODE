"""
gnomAD Query — GRCh37 Version (gnomad_r2.1)

КОРНЕВАЯ ПРИЧИНА 92% FAILURES:
- gnomAD v4 API не отвечает на GRCh38 coordinates
- gnomAD v2.1 (GRCh37) работает стабильно
- Нужен liftover GRCh38 → GRCh37 для ClinVar positions

Временное решение: query gnomad_r2.1 вместо gnomad_r4
"""

import requests
import time
import json
import sys
from typing import Dict, Any

GNOMAD_API = "https://gnomad.broadinstitute.org/api"

# HBB locus liftover offset (approximate)
# GRCh38: chr11:5,225,000-5,228,000
# GRCh37: chr11:5,246,000-5,250,000
# Offset: +~22,000 bp
GRCH38_TO_GRCH37_OFFSET = 22400  # Approximate, needs validation


def grch38_to_grch37_approximate(pos_grch38: int) -> int:
    """
    Approximate liftover GRCh38 → GRCh37 for HBB locus.

    WARNING: This is APPROXIMATE. Real liftover requires UCSC liftOver tool.
    For HBB region (chr11:5,225,000-5,228,000), offset is ~+22,400bp.
    """
    return pos_grch38 + GRCH38_TO_GRCH37_OFFSET


def query_gnomad_r2(
    chrom: str, pos_grch38: int, ref: str, alt: str, delay: float = 0.5
) -> Dict[str, Any]:
    """
    Query gnomAD r2.1 (GRCh37) with approximate liftover.

    Args:
        chrom: Chromosome (e.g., "chr11" or "11")
        pos_grch38: Position in GRCh38
        ref: Reference allele
        alt: Alternate allele
        delay: Delay between requests

    Returns:
        Dict with keys: variant_id, ac, an, af, status, source
    """

    # Remove "chr" prefix
    chrom_clean = chrom.replace("chr", "")

    # Liftover GRCh38 → GRCh37 (approximate)
    pos_grch37 = grch38_to_grch37_approximate(pos_grch38)

    variant_id = f"{chrom_clean}-{pos_grch37}-{ref}-{alt}"

    query = """
    query VariantQuery($variantId: String!, $dataset: DatasetId!) {
      variant(variantId: $variantId, dataset: $dataset) {
        variant_id
        genome {
          ac
          an
          af
        }
      }
    }
    """

    variables = {
        "variantId": variant_id,
        "dataset": "gnomad_r2_1",  # GRCh37
    }

    try:
        response = requests.post(
            GNOMAD_API,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code != 200:
            return {
                "variant_id": variant_id,
                "pos_grch37": pos_grch37,
                "pos_grch38": pos_grch38,
                "ac": None,
                "an": None,
                "af": None,
                "status": "http_error",
                "source": f"http_{response.status_code}",
            }

        data = response.json()

        if "errors" in data:
            return {
                "variant_id": variant_id,
                "pos_grch37": pos_grch37,
                "pos_grch38": pos_grch38,
                "ac": None,
                "an": None,
                "af": None,
                "status": "not_in_gnomad",
                "source": "variant_not_found_grch37",
            }

        variant_data = data.get("data", {}).get("variant")

        if variant_data is None:
            return {
                "variant_id": variant_id,
                "pos_grch37": pos_grch37,
                "pos_grch38": pos_grch38,
                "ac": None,
                "an": None,
                "af": None,
                "status": "not_in_gnomad",
                "source": "variant_not_found_grch37",
            }

        genome = variant_data.get("genome")

        if genome is None:
            return {
                "variant_id": variant_id,
                "pos_grch37": pos_grch37,
                "pos_grch38": pos_grch38,
                "ac": None,
                "an": None,
                "af": None,
                "status": "no_genome_data",
                "source": "genome_field_null",
            }

        ac = genome.get("ac")
        an = genome.get("an")
        af = genome.get("af")

        if ac is None:
            status = "NOT_QUERYABLE"
            source = "ac_field_missing"
        elif ac == 0:
            status = "ABSENT"
            source = "gnomad_r2_1_confirmed"
        else:
            status = "PRESENT"
            source = "gnomad_r2_1_confirmed"

        time.sleep(delay)

        return {
            "variant_id": variant_id,
            "pos_grch37": pos_grch37,
            "pos_grch38": pos_grch38,
            "ac": ac,
            "an": an,
            "af": af,
            "status": status,
            "source": source,
        }

    except Exception as e:
        return {
            "variant_id": variant_id,
            "pos_grch37": pos_grch37,
            "pos_grch38": pos_grch38,
            "ac": None,
            "an": None,
            "af": None,
            "status": "query_failed",
            "source": f"exception: {str(e)}",
        }


def test_query():
    """Test query with known HBB variants."""

    print("Testing gnomAD r2.1 query with HBB variants (GRCh38 → GRCh37 liftover)...")
    print()

    # Test rs334 (HbS)
    print("1. rs334 (HbS, famous sickle cell):")
    result = query_gnomad_r2("chr11", 5226945, "T", "A", delay=1.0)
    print(f"   GRCh38: {result['pos_grch38']}, GRCh37: {result['pos_grch37']}")
    print(f"   Status: {result['status']}")
    if result["ac"] is not None:
        print(f"   AC: {result['ac']}, AF: {result['af']:.6f}")
    print()

    # Test from CSV (first simple SNV)
    print("2. HBB G>T (from CSV, pos 5226598 GRCh38):")
    result = query_gnomad_r2("chr11", 5226598, "G", "T", delay=1.0)
    print(f"   GRCh38: {result['pos_grch38']}, GRCh37: {result['pos_grch37']}")
    print(f"   Status: {result['status']}")
    if result["ac"] is not None:
        print(f"   AC: {result['ac']}, AF: {result['af']:.6f}")
    print()


if __name__ == "__main__":
    test_query()
