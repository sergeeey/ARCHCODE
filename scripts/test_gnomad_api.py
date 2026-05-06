#!/usr/bin/env python
"""Test gnomAD v4 GraphQL API structure."""

import requests
import json

GNOMAD_API = "https://gnomad.broadinstitute.org/api"

# Test 1: Simple query without populations
query_simple = """
{
  variant(dataset: gnomad_r4, variantId: "11-5227099-T-C") {
    variant_id
    genome {
      ac
      an
      af
    }
  }
}
"""

# Test 2: Query with populations field
query_with_pops = """
{
  variant(dataset: gnomad_r4, variantId: "11-5227099-T-C") {
    variant_id
    genome {
      ac
      an
      af
      populations {
        id
        ac
        an
        af
      }
    }
  }
}
"""

# Test 3: Alternative syntax for populations
query_alt = """
{
  variant(dataset: gnomad_r4, variantId: "11-5227099-T-C") {
    variant_id
    genome {
      ac
      an
      af
      faf95 {
        popmax
        popmax_population
      }
    }
  }
}
"""


def test_query(name, query):
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"{'='*60}")
    try:
        resp = requests.post(
            GNOMAD_API,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        print(f"Status code: {resp.status_code}")
        data = resp.json()
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    test_query("Simple (no populations)", query_simple)
    test_query("With populations field", query_with_pops)
    test_query("Alternative faf95 syntax", query_alt)
