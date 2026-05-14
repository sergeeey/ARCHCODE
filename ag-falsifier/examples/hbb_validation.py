"""Example: HBB CAGE validation using ag-falsifier.

This example reproduces the ARCHCODE × AlphaGenome HBB validation
from the May 2026 analysis.
"""

import pandas as pd
import os
from ag_falsifier import AlphaGenomeValidator


def load_hbb_data():
    """
    Load HBB variant data from ARCHCODE project.

    Returns:
        pearls (DataFrame), controls (DataFrame)
    """
    # Load from alphagenome_pearl_vs_control.json
    data_path = "../../results/alphagenome_pearl_vs_control.json"

    import json

    with open(data_path) as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data["results"])

    # Split into pearls and controls
    pearls = df[df["group"] == "PEARL"].copy()
    controls = df[df["group"] == "CONTROL"].copy()

    # Add required columns
    pearls["Variant_ID"] = pearls["variant_id"]
    pearls["Category"] = pearls["category"]
    pearls["AlphaGenome_CAGE"] = pearls["cage_pct"]

    controls["Variant_ID"] = controls["variant_id"]
    controls["Category"] = controls["category"]
    controls["AlphaGenome_CAGE"] = controls["cage_pct"]

    return pearls, controls


def main():
    """Run HBB CAGE validation."""

    print("Loading HBB variant data...")
    pearls, controls = load_hbb_data()

    print(f"Loaded {len(pearls)} pearls, {len(controls)} controls")

    # Initialize validator
    validator = AlphaGenomeValidator(
        pearls=pearls,
        controls=controls,
        api_key=os.getenv("ALPHAGENOME_API_KEY", "not-needed-for-cached-data"),
        interval="chr11:5227000-5228000",
    )

    print("\nRunning validation with category-matched permutation...")

    # Run validation
    result = validator.validate(
        modality="CAGE",
        category_matched=True,
        permutation_test=True,
        n_permutations=10000,
        negative_controls=["shuffled_labels"],
        seed_sensitivity=[1, 7, 21, 42, 100],
    )

    # Print results
    print("\n" + "=" * 60)
    print("VALIDATION RESULT")
    print("=" * 60)
    print(f"Test validity: {result.test_validity}")
    print(f"p-value: {result.p_value:.2e}")
    print(f"Verdict: {result.verdict}")
    print(f"\nInterpretation: {result.interpretation}")

    if result.warning:
        print(f"\nWarning: {result.warning}")

    if result.insufficient_categories:
        print("\nInsufficient categories:")
        for category, info in result.insufficient_categories.items():
            print(
                f"  {category}: {info['pearl_count']} pearls, "
                f"{info['available_controls']} controls"
            )

    # Save ADR
    adr_path = "ADR_hbb_cage_validation.md"
    result.to_adr(adr_path)
    print(f"\nADR saved to: {adr_path}")

    # Save JSON
    json_path = "hbb_cage_validation_result.json"
    result.to_json(json_path)
    print(f"JSON results saved to: {json_path}")

    print("\n" + "=" * 60)
    print("Expected result (from May 2026 analysis):")
    print("  Test validity: PARTIAL")
    print("  Verdict: WEAK")
    print("  Reason: 15/20 pearls are promoter category with 0 controls")
    print("=" * 60)


if __name__ == "__main__":
    main()
