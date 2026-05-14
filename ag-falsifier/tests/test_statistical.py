"""Tests for statistical functions."""

import pytest
import pandas as pd
import numpy as np
from ag_falsifier.statistical import (
    category_matched_permutation,
    mann_whitney_test,
    shuffled_labels_test,
    seed_sensitivity_test,
    orthogonality_test,
)


@pytest.fixture
def mock_data():
    """Create mock variant data."""
    np.random.seed(42)

    df = pd.DataFrame(
        {
            "Variant_ID": [f"v{i}" for i in range(30)],
            "Category": ["promoter"] * 15 + ["enhancer"] * 15,
            "Pearl": [True] * 10 + [False] * 20,
            "AlphaGenome_CAGE": np.concatenate(
                [
                    np.random.normal(-15, 3, 10),  # Pearls
                    np.random.normal(-2, 2, 20),  # Controls
                ]
            ),
        }
    )

    pearls = df[df["Pearl"] == True]

    return df, pearls


def test_category_matched_permutation(mock_data):
    """Test category-matched permutation."""
    df, pearls = mock_data

    result = category_matched_permutation(
        df=df, pearls=pearls, n_perms=1000, seed=42, value_col="AlphaGenome_CAGE"
    )

    assert "p_value" in result
    assert "test_validity" in result
    assert result["test_validity"] in ["VALID", "PARTIAL", "INVALID"]
    assert 0 <= result["p_value"] <= 1


def test_category_matched_no_controls():
    """Test category-matched with missing controls."""
    # All pearls promoter, no promoter controls
    df = pd.DataFrame(
        {
            "Variant_ID": ["v1", "v2", "v3", "v4"],
            "Category": ["promoter", "promoter", "enhancer", "enhancer"],
            "Pearl": [True, True, False, False],
            "AlphaGenome_CAGE": [-15, -18, -2, -3],
        }
    )

    pearls = df[df["Pearl"] == True]

    result = category_matched_permutation(
        df=df, pearls=pearls, n_perms=100, seed=42, value_col="AlphaGenome_CAGE"
    )

    assert result["test_validity"] == "INVALID"
    assert "promoter" in result["insufficient_categories"]


def test_mann_whitney():
    """Test Mann-Whitney U test."""
    group1 = pd.Series([-15, -18, -12, -16])
    group2 = pd.Series([-2, -3, -1, -4])

    result = mann_whitney_test(group1, group2)

    assert "p_value" in result
    assert "U_statistic" in result
    assert "median_diff" in result
    assert result["p_value"] < 0.05  # Should be significant


def test_shuffled_labels(mock_data):
    """Test shuffled labels negative control."""
    df, _ = mock_data

    result = shuffled_labels_test(df=df, value_col="AlphaGenome_CAGE", n_perms=1000, seed=42)

    assert "p_value" in result
    assert "interpretation" in result
    # Shuffled labels should NOT be significant
    assert result["p_value"] > 0.01


def test_seed_sensitivity(mock_data):
    """Test seed sensitivity."""
    df, pearls = mock_data

    result = seed_sensitivity_test(
        df=df, pearls=pearls, seeds=[1, 7, 21, 42], n_perms=500, value_col="AlphaGenome_CAGE"
    )

    assert "p_values" in result
    assert len(result["p_values"]) == 4
    assert "p_value_range" in result
    assert "interpretation" in result


def test_orthogonality():
    """Test orthogonality detection."""
    np.random.seed(42)

    # Both methods separate groups, but uncorrelated
    method1 = pd.Series(
        np.concatenate(
            [
                np.random.normal(5, 1, 20),  # Group 1
                np.random.normal(10, 1, 20),  # Group 2
            ]
        )
    )

    method2 = pd.Series(
        np.concatenate(
            [
                np.random.normal(-15, 3, 20),  # Group 1
                np.random.normal(-2, 2, 20),  # Group 2
            ]
        )
    )

    labels = pd.Series([True] * 20 + [False] * 20)

    result = orthogonality_test(method1, method2, labels)

    assert "group_difference_p1" in result
    assert "group_difference_p2" in result
    assert "rank_correlation_rho" in result
    assert "interpretation" in result

    # Should detect orthogonality (both separate groups, low correlation)
    assert result["group_difference_p1"] < 0.05
    assert result["group_difference_p2"] < 0.05
