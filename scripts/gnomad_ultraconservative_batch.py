"""
gnomAD Ultra-Conservative Batch Query

Settings that WORK:
- 5 second timeout
- 3 second pause between requests
- Single variant per request
- Retry once on timeout

Estimated runtime: 27 variants × 8s = ~4 minutes
"""

import requests
import json
import time
import csv
from pathlib import Path

GNOMAD_API = "https://gnomad.broadinstitute.org/api"

# Pearl variants to query (simple SNVs only, no IUPAC codes)
PEARLS = [
    ("5226598", "G", "T", "VCV003766487"),
    ("5226598", "G", "C", "VCV000801186"),
    ("5226613", "G", "C", "VCV002664746"),
    ("5226613", "G", "T", "VCV000811500"),
    ("5226643", "C", "G", "VCV000618675"),
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


def query_variant(pos, ref, alt, clinvar_id, retry=True):
    """Query single variant with ultra-conservative settings."""

    variant_id = f"11-{pos}-{ref}-{alt}"

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

    variables = {"variantId": variant_id, "dataset": "gnomad_r4"}

    try:
        response = requests.post(
            GNOMAD_API,
            json={"query": query, "variables": variables},
            headers={"Content-Type": "application/json"},
            timeout=5,  # 5 second timeout
        )

        data = response.json()

        # Check for errors
        if "errors" in data:
            return {
                "clinvar_id": clinvar_id,
                "variant_id": variant_id,
                "ac": None,
                "an": None,
                "af": None,
                "status": "api_error",
                "source": str(data["errors"]),
            }

        # Extract variant data
        variant = data.get("data", {}).get("variant")

        if variant is None:
            return {
                "clinvar_id": clinvar_id,
                "variant_id": variant_id,
                "ac": None,
                "an": None,
                "af": None,
                "status": "not_in_gnomad",
                "source": "variant_not_found",
            }

        genome = variant.get("genome")

        if genome is None:
            return {
                "clinvar_id": clinvar_id,
                "variant_id": variant_id,
                "ac": None,
                "an": None,
                "af": None,
                "status": "no_genome_data",
                "source": "genome_field_null",
            }

        ac = genome.get("ac")
        an = genome.get("an")
        af = genome.get("af")

        if ac == 0:
            status = "ABSENT"
        elif ac is not None and ac <= 5:
            status = "ULTRA_RARE"
        elif ac is not None:
            status = "PRESENT"
        else:
            status = "NOT_QUERYABLE"

        return {
            "clinvar_id": clinvar_id,
            "variant_id": variant_id,
            "ac": ac,
            "an": an,
            "af": af,
            "status": status,
            "source": "gnomad_r4_verified",
        }

    except requests.exceptions.Timeout:
        if retry:
            print(f"  Timeout, retrying once...")
            time.sleep(5)  # Extra pause before retry
            return query_variant(pos, ref, alt, clinvar_id, retry=False)
        else:
            return {
                "clinvar_id": clinvar_id,
                "variant_id": variant_id,
                "ac": None,
                "an": None,
                "af": None,
                "status": "timeout",
                "source": "timeout_after_retry",
            }

    except Exception as e:
        return {
            "clinvar_id": clinvar_id,
            "variant_id": variant_id,
            "ac": None,
            "an": None,
            "af": None,
            "status": "exception",
            "source": str(e),
        }


def main():
    """Query all pearls and save results."""

    print("Starting ultra-conservative batch query...")
    print(f"Variants to query: {len(PEARLS)}")
    print(f"Estimated time: ~{len(PEARLS) * 8} seconds (~{len(PEARLS) * 8 / 60:.1f} minutes)")
    print()

    results = []

    for i, (pos, ref, alt, clinvar_id) in enumerate(PEARLS, 1):
        print(f"[{i}/{len(PEARLS)}] Querying {clinvar_id} (11-{pos}-{ref}-{alt})...")

        result = query_variant(pos, ref, alt, clinvar_id)
        results.append(result)

        # Print result
        if result["status"] == "ABSENT":
            print(f"  ✅ ABSENT (AC=0)")
        elif result["status"] == "ULTRA_RARE":
            print(f"  ✅ ULTRA_RARE (AC={result['ac']}, AF={result['af']:.2e})")
        elif result["status"] == "PRESENT":
            print(f"  ⚠️  PRESENT (AC={result['ac']}, AF={result['af']:.2e})")
        elif result["status"] == "not_in_gnomad":
            print(f"  ⚠️  NOT IN gnomAD v4")
        else:
            print(f"  ❌ {result['status']}: {result['source']}")

        # Ultra-conservative pause (3 seconds)
        time.sleep(3)

    # Save results
    output_file = Path("results/gnomad_pearls_verified.csv")

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["clinvar_id", "variant_id", "ac", "an", "af", "status", "source"]
        )
        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"✅ Results saved to {output_file}")
    print()

    # Summary statistics
    total = len(results)
    absent = sum(1 for r in results if r["status"] == "ABSENT")
    ultra_rare = sum(1 for r in results if r["status"] == "ULTRA_RARE")
    present = sum(1 for r in results if r["status"] == "PRESENT")
    not_found = sum(1 for r in results if r["status"] == "not_in_gnomad")
    failed = sum(1 for r in results if r["status"] in ["timeout", "api_error", "exception"])

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total queried: {total}")
    print(f"  ABSENT (AC=0): {absent} ({absent/total*100:.1f}%)")
    print(f"  ULTRA_RARE (AC=1-5): {ultra_rare} ({ultra_rare/total*100:.1f}%)")
    print(f"  PRESENT (AC>5): {present} ({present/total*100:.1f}%)")
    print(f"  NOT IN gnomAD: {not_found} ({not_found/total*100:.1f}%)")
    print(f"  FAILED: {failed} ({failed/total*100:.1f}%)")
    print()
    print(
        f"Strong constraint (ABSENT + ULTRA_RARE): {absent + ultra_rare}/{total} ({(absent + ultra_rare)/total*100:.1f}%)"
    )


if __name__ == "__main__":
    main()
