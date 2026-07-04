#!/usr/bin/env python3
"""
Prepare MLH1 variant list for AlphaGenome API calls.

Target: N=10-15 pathogenic + N=10-15 benign
Focus: Splice-relevant variants (frameshift, splice_region, 5'UTR)
Priority: SNV > small indels > large deletions
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"


def is_snv(row):
    """Check if variant is a single nucleotide variant."""
    ref = str(row["Ref"])
    alt = str(row["Alt"])

    # Skip structural variants
    if ref == "." or alt == ".":
        return False

    # SNV: single base change
    if len(ref) == 1 and len(alt) == 1:
        return True

    return False


def is_small_indel(row):
    """Check if variant is a small indel (1-10bp)."""
    ref = str(row["Ref"])
    alt = str(row["Alt"])

    if ref == "." or alt == ".":
        return False

    if 1 <= abs(len(ref) - len(alt)) <= 10:
        return True

    return False


def main():
    # Load MLH1 atlas
    df = pd.read_csv(RESULTS_DIR / "MLH1_Unified_Atlas_300kb.csv")

    print(f"Total MLH1 variants: {len(df)}")
    print()

    # Filter pathogenic
    pathogenic = df[
        df["ClinVar_Significance"].isin(
            ["Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic"]
        )
    ].copy()

    # Filter benign
    benign = df[df["ClinVar_Significance"].isin(["Benign", "Likely benign"])].copy()

    print(f"Pathogenic: {len(pathogenic)}")
    print(f"Benign: {len(benign)}")
    print()

    # Add variant type flags
    pathogenic["is_snv"] = pathogenic.apply(is_snv, axis=1)
    pathogenic["is_small_indel"] = pathogenic.apply(is_small_indel, axis=1)

    benign["is_snv"] = benign.apply(is_snv, axis=1)
    benign["is_small_indel"] = benign.apply(is_small_indel, axis=1)

    # Focus on splice-relevant categories
    splice_cats = ["splice_region", "splice_donor", "splice_acceptor", "frameshift", "5_prime_UTR"]

    # Pathogenic splice variants
    splice_path = pathogenic[pathogenic["Category"].isin(splice_cats)].copy()

    # Priority 1: SNV splice variants
    snv_splice = splice_path[splice_path["is_snv"]].copy()
    print(f"SNV splice-relevant pathogenic: {len(snv_splice)}")
    print(snv_splice["Category"].value_counts())
    print()

    # Priority 2: Small indels if not enough SNVs
    small_indel_splice = splice_path[splice_path["is_small_indel"]].copy()
    print(f"Small indel splice-relevant pathogenic: {len(small_indel_splice)}")
    print()

    # Select top 15 pathogenic
    # Prefer splice_region and splice_donor (direct splicing impact)
    # Then frameshift (indirect splicing via NMD)

    priority_cats = ["splice_donor", "splice_region", "frameshift", "5_prime_UTR"]

    selected_path = []
    for cat in priority_cats:
        cat_vars = snv_splice[snv_splice["Category"] == cat]

        # Take first 5 from each category (or all if < 5)
        n_take = min(5, len(cat_vars))
        selected_path.append(cat_vars.head(n_take))

        if len(pd.concat(selected_path)) >= 15:
            break

    pathogenic_list = pd.concat(selected_path).head(15)

    print(f"Selected pathogenic variants: {len(pathogenic_list)}")
    print(pathogenic_list["Category"].value_counts())
    print()

    # Select benign controls (matching categories if possible)
    benign_splice = benign[benign["Category"].isin(splice_cats)].copy()
    benign_snv = benign_splice[benign_splice["is_snv"]].copy()

    print(f"Benign splice-relevant SNV: {len(benign_snv)}")
    print(benign_snv["Category"].value_counts())
    print()

    benign_list = benign_snv.head(15)

    # Combine
    final_list = pd.concat(
        [pathogenic_list.assign(Group="PATHOGENIC"), benign_list.assign(Group="BENIGN")]
    )

    # Select relevant columns
    output_cols = [
        "ClinVar_ID",
        "Position_GRCh38",
        "Ref",
        "Alt",
        "HGVS_c",
        "Category",
        "ClinVar_Significance",
        "ARCHCODE_LSSIM",
        "VEP_Score",
        "Group",
    ]

    final_list = final_list[output_cols]

    # Save
    output_path = RESULTS_DIR / "mlh1_variant_list_for_alphagenome.csv"
    final_list.to_csv(output_path, index=False)

    print(f"Saved to: {output_path}")
    print(f"Total variants: {len(final_list)}")
    print()
    print("Group breakdown:")
    print(final_list["Group"].value_counts())
    print()
    print("Category breakdown:")
    print(final_list.groupby("Group")["Category"].value_counts())
    print()
    print("Sample (first 5):")
    print(final_list.head())


if __name__ == "__main__":
    main()
