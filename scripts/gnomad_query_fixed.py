"""
gnomAD Query Script — Fixed Version

Fixes for 92% query failure:
1. Correct variant ID format (remove "chr" prefix for gnomAD v4)
2. Distinguish query_failed from AC=0
3. Add retry logic with exponential backoff
4. Validate response structure before classification
"""

import requests
import time
import json
import sys
from typing import Optional, Dict, Any

GNOMAD_API = "https://gnomad.broadinstitute.org/api"


def query_gnomad_v4(
    chrom: str, pos: int, ref: str, alt: str, delay: float = 0.5, max_retries: int = 3
) -> Dict[str, Any]:
    """
    Query gnomAD v4 for variant allele frequency.

    Args:
        chrom: Chromosome (e.g., "chr11" or "11")
        pos: Position (GRCh38)
        ref: Reference allele
        alt: Alternate allele
        delay: Delay between requests (seconds)
        max_retries: Maximum retry attempts

    Returns:
        Dict with keys: variant_id, ac, an, af, status, source
    """

    # FIX #1: Remove "chr" prefix for gnomAD v4 API
    chrom_clean = chrom.replace("chr", "")

    # Build variant ID (gnomAD v4 format: chrom-pos-ref-alt, no "chr" prefix)
    variant_id = f"{chrom_clean}-{pos}-{ref}-{alt}"

    # GraphQL query
    query = """
    query VariantQuery($variantId: String!, $dataset: DatasetId!) {
      variant(variantId: $variantId, dataset: $dataset) {
        variant_id
        chrom
        pos
        ref
        alt
        genome {
          ac
          an
          af
        }
      }
    }
    """

    variables = {"variantId": variant_id, "dataset": "gnomad_r4"}

    # Retry loop with exponential backoff
    for attempt in range(max_retries):
        try:
            # Send request
            response = requests.post(
                GNOMAD_API,
                json={"query": query, "variables": variables},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            # Check HTTP status
            if response.status_code != 200:
                print(f"  WARNING: HTTP {response.status_code} for {variant_id}", file=sys.stderr)
                time.sleep(delay * (2**attempt))  # Exponential backoff
                continue

            # Parse JSON
            data = response.json()

            # FIX #2: Validate response structure
            if "errors" in data:
                print(f"  GraphQL ERROR for {variant_id}: {data['errors']}", file=sys.stderr)
                return {
                    "variant_id": variant_id,
                    "ac": None,
                    "an": None,
                    "af": None,
                    "status": "api_error",
                    "source": f"graphql_error: {data['errors'][0]['message']}",
                }

            if "data" not in data or data["data"] is None:
                print(f"  NULL DATA for {variant_id}", file=sys.stderr)
                return {
                    "variant_id": variant_id,
                    "ac": None,
                    "an": None,
                    "af": None,
                    "status": "query_failed",
                    "source": "null_data_response",
                }

            variant_data = data["data"].get("variant")

            if variant_data is None:
                # Variant not in gnomAD v4
                return {
                    "variant_id": variant_id,
                    "ac": None,
                    "an": None,
                    "af": None,
                    "status": "not_in_gnomad",
                    "source": "variant_not_found",
                }

            # Extract genome data
            genome = variant_data.get("genome")

            if genome is None:
                # Variant exists but no genome data (exome-only?)
                return {
                    "variant_id": variant_id,
                    "ac": None,
                    "an": None,
                    "af": None,
                    "status": "no_genome_data",
                    "source": "genome_field_null",
                }

            # FIX #3: Distinguish AC=null from AC=0
            ac = genome.get("ac")
            an = genome.get("an")
            af = genome.get("af")

            if ac is None:
                # AC field missing (multi-allelic or not queryable)
                status = "NOT_QUERYABLE"
                source = "ac_field_missing"
            elif ac == 0:
                # Real absence in population
                status = "ABSENT"
                source = "gnomad_v4_confirmed"
            else:
                # Present in population
                status = "PRESENT"
                source = "gnomad_v4_confirmed"

            # Rate limiting
            time.sleep(delay)

            return {
                "variant_id": variant_id,
                "ac": ac,
                "an": an,
                "af": af,
                "status": status,
                "source": source,
            }

        except requests.exceptions.Timeout:
            print(
                f"  TIMEOUT for {variant_id} (attempt {attempt+1}/{max_retries})", file=sys.stderr
            )
            time.sleep(delay * (2**attempt))

        except requests.exceptions.RequestException as e:
            print(f"  REQUEST ERROR for {variant_id}: {e}", file=sys.stderr)
            time.sleep(delay * (2**attempt))

        except Exception as e:
            print(f"  UNEXPECTED ERROR for {variant_id}: {e}", file=sys.stderr)
            time.sleep(delay * (2**attempt))

    # All retries failed
    return {
        "variant_id": variant_id,
        "ac": None,
        "an": None,
        "af": None,
        "status": "query_failed",
        "source": f"max_retries_exceeded_{max_retries}",
    }


def test_query():
    """Test query with known variant."""

    # HBB IVS-II-1 (G>A) — known pathogenic variant, should be absent
    print("Testing gnomAD query with HBB IVS-II-1 (chr11-5227002-G-A)...")
    print()

    result = query_gnomad_v4(chrom="chr11", pos=5227002, ref="G", alt="A", delay=1.0)

    print(json.dumps(result, indent=2))
    print()

    if result["status"] == "query_failed":
        print("❌ Query FAILED — variant ID format or API issue")
        print(f"   Source: {result['source']}")
    elif result["status"] == "not_in_gnomad":
        print("⚠️  Variant NOT IN gnomAD v4 (may be ultra-rare or GRCh37 coordinate)")
    elif result["status"] == "ABSENT":
        print(f"✅ Query SUCCESS — variant ABSENT (AC=0, AN={result['an']})")
    elif result["status"] == "PRESENT":
        print(f"✅ Query SUCCESS — variant PRESENT (AC={result['ac']}, AF={result['af']})")
    else:
        print(f"⚠️  Query status: {result['status']}")


if __name__ == "__main__":
    test_query()
