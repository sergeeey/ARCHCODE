"""Statistical tests for falsification-first validation."""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu, spearmanr


def category_matched_permutation(
    df: pd.DataFrame,
    pearls: pd.DataFrame,
    n_perms: int,
    seed: int,
    value_col: str = "AlphaGenome_CAGE",
) -> Dict:
    """
    Category-matched permutation test.

    Null hypothesis: Random variants FROM SAME CATEGORY as pearls
    show similar values as pearls.

    Args:
        df: Combined DataFrame (pearls + controls)
        pearls: Pearl DataFrame
        n_perms: Number of permutations
        seed: Random seed
        value_col: Column name for values to test

    Returns:
        Dict with p_value, test_validity, insufficient_categories, warning
    """
    np.random.seed(seed)

    # Get pearl category distribution
    pearl_categories = pearls["Category"].value_counts().to_dict()

    # Track categories with insufficient controls
    insufficient_categories = {}

    # Observed statistic (median of pearls)
    observed = pearls[value_col].median()

    # Permutation distribution
    null_distribution = []

    for iteration in range(n_perms):
        sampled_variants = []

        for category, count in pearl_categories.items():
            # Pool: non-pearl variants in this category
            category_pool = df[(df["Category"] == category) & (df["Pearl"] == False)]

            if len(category_pool) == 0:
                # CRITICAL: No non-pearl controls in this category
                if category not in insufficient_categories:
                    insufficient_categories[category] = {
                        "pearl_count": count,
                        "available_controls": 0,
                        "action": "SKIPPED (no controls available)",
                    }
                continue  # Skip this category

            # Sample (with replacement if needed)
            sample = category_pool.sample(
                n=count, replace=(len(category_pool) < count), random_state=seed + iteration
            )
            sampled_variants.append(sample)

        if sampled_variants:
            sampled_df = pd.concat(sampled_variants, ignore_index=True)
            null_stat = sampled_df[value_col].median()
            null_distribution.append(null_stat)

    # Calculate p-value (two-tailed)
    null_distribution = np.array(null_distribution)
    p_value = np.mean(np.abs(null_distribution - 0) >= np.abs(observed - 0))

    # Determine test validity
    total_pearls = sum(pearl_categories.values())
    skipped_pearls = sum(
        v["pearl_count"] for v in insufficient_categories.values() if v["available_controls"] == 0
    )

    if skipped_pearls == 0:
        test_validity = "VALID"
        warning = None
    elif skipped_pearls < total_pearls:
        test_validity = "PARTIAL"
        warning = (
            f"{skipped_pearls}/{total_pearls} pearls skipped "
            f"(no controls in {len(insufficient_categories)} categories)"
        )
    else:
        test_validity = "INVALID"
        warning = "All pearls skipped (no category-matched controls available)"

    return {
        "p_value": p_value,
        "test_validity": test_validity,
        "insufficient_categories": insufficient_categories,
        "warning": warning,
        "observed": observed,
        "null_median": np.median(null_distribution),
        "null_std": np.std(null_distribution),
    }


def mann_whitney_test(group1: pd.Series, group2: pd.Series) -> Dict:
    """
    Mann-Whitney U test (non-parametric).

    Args:
        group1: First group values
        group2: Second group values

    Returns:
        Dict with p_value, U_statistic, median_diff
    """
    u_stat, p_value = mannwhitneyu(group1, group2, alternative="two-sided")

    return {
        "p_value": p_value,
        "U_statistic": u_stat,
        "median_diff": group1.median() - group2.median(),
        "group1_median": group1.median(),
        "group2_median": group2.median(),
    }


def shuffled_labels_test(
    df: pd.DataFrame, value_col: str = "AlphaGenome_CAGE", n_perms: int = 1000, seed: int = 42
) -> Dict:
    """
    Negative control: shuffled labels.

    If labels are shuffled randomly, p-value should be >>0.05.
    If p<0.05, the test is detecting noise, not signal.

    Args:
        df: DataFrame with Pearl column and value_col
        value_col: Column name for values
        n_perms: Number of permutations
        seed: Random seed

    Returns:
        Dict with p_value, interpretation
    """
    np.random.seed(seed)

    observed_diff = (
        df[df["Pearl"] == True][value_col].median() - df[df["Pearl"] == False][value_col].median()
    )

    null_diffs = []
    for i in range(n_perms):
        shuffled = df.copy()
        shuffled["Pearl"] = np.random.permutation(shuffled["Pearl"].values)

        null_diff = (
            shuffled[shuffled["Pearl"] == True][value_col].median()
            - shuffled[shuffled["Pearl"] == False][value_col].median()
        )
        null_diffs.append(null_diff)

    null_diffs = np.array(null_diffs)
    p_value = np.mean(np.abs(null_diffs) >= np.abs(observed_diff))

    interpretation = (
        "PASS (p≥0.05, no signal in shuffled labels)"
        if p_value >= 0.05
        else f"WARNING: Shuffled labels significant (p={p_value:.4f})"
    )

    return {
        "p_value": p_value,
        "interpretation": interpretation,
        "observed_diff": observed_diff,
        "null_median": np.median(null_diffs),
    }


def seed_sensitivity_test(
    df: pd.DataFrame,
    pearls: pd.DataFrame,
    seeds: List[int],
    n_perms: int,
    value_col: str = "AlphaGenome_CAGE",
) -> Dict:
    """
    Test sensitivity to random seed.

    Stable result: p-value similar across seeds.
    Unstable result: p-value varies wildly.

    Args:
        df: Combined DataFrame
        pearls: Pearl DataFrame
        seeds: List of random seeds to test
        n_perms: Number of permutations per seed
        value_col: Column name for values

    Returns:
        Dict with p_values, range, interpretation
    """
    p_values = []

    for seed in seeds:
        result = category_matched_permutation(
            df=df, pearls=pearls, n_perms=n_perms, seed=seed, value_col=value_col
        )
        p_values.append(result["p_value"])

    p_min = min(p_values)
    p_max = max(p_values)
    p_range = p_max - p_min

    interpretation = (
        "STABLE (p-value consistent across seeds)"
        if p_range < 0.01
        else f"UNSTABLE (p-value range: {p_min:.4f} to {p_max:.4f})"
    )

    return {
        "p_values": p_values,
        "p_value_range": [p_min, p_max],
        "range_width": p_range,
        "interpretation": interpretation,
    }


def orthogonality_test(
    method1_scores: pd.Series, method2_scores: pd.Series, labels: pd.Series
) -> Dict:
    """
    Test if two methods measure orthogonal mechanisms.

    Orthogonal: Both separate groups (Mann-Whitney p<0.05),
                but no rank correlation (Spearman ρ≈0).

    Args:
        method1_scores: First method scores
        method2_scores: Second method scores
        labels: Group labels (True/False or 0/1)

    Returns:
        Dict with group_diff_p, rank_corr_rho, rank_corr_p, interpretation
    """
    # Group difference for both methods
    mw1 = mann_whitney_test(method1_scores[labels == True], method1_scores[labels == False])

    mw2 = mann_whitney_test(method2_scores[labels == True], method2_scores[labels == False])

    # Rank correlation between methods
    rho, rho_p = spearmanr(method1_scores, method2_scores)

    # Interpretation
    if mw1["p_value"] < 0.05 and mw2["p_value"] < 0.05 and abs(rho) < 0.3:
        interpretation = "ORTHOGONAL_MECHANISMS (both detect groups, no rank correlation)"
    elif mw1["p_value"] < 0.05 and mw2["p_value"] < 0.05 and abs(rho) >= 0.5:
        interpretation = "CONCORDANT (both detect groups, strong correlation)"
    elif abs(rho) >= 0.5:
        interpretation = "CORRELATED (methods measure similar signal)"
    else:
        interpretation = "INDEPENDENT (no clear relationship)"

    return {
        "group_difference_p1": mw1["p_value"],
        "group_difference_p2": mw2["p_value"],
        "rank_correlation_rho": rho,
        "rank_correlation_p": rho_p,
        "interpretation": interpretation,
    }
