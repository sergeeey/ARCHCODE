"""Utility functions for ag-falsifier."""

from typing import Dict, List
import pandas as pd


def validate_dataframe(
    df: pd.DataFrame, required_columns: List[str], name: str = "DataFrame"
) -> None:
    """
    Validate DataFrame has required columns.

    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        name: Name for error messages

    Raises:
        ValueError: If required columns are missing
    """
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(
            f"{name} missing required columns: {missing}\n" f"Available columns: {list(df.columns)}"
        )


def categorize_variants(df: pd.DataFrame, category_col: str = "Category") -> Dict[str, int]:
    """
    Count variants by category.

    Args:
        df: DataFrame with variants
        category_col: Column name for categories

    Returns:
        Dict mapping category -> count
    """
    return df[category_col].value_counts().to_dict()


def calculate_effect_size(group1: pd.Series, group2: pd.Series) -> float:
    """
    Calculate Cohen's d effect size.

    Args:
        group1: First group values
        group2: Second group values

    Returns:
        Cohen's d (standardized mean difference)
    """
    mean_diff = group1.mean() - group2.mean()
    pooled_std = (
        ((len(group1) - 1) * group1.std() ** 2 + (len(group2) - 1) * group2.std() ** 2)
        / (len(group1) + len(group2) - 2)
    ) ** 0.5

    return mean_diff / pooled_std if pooled_std > 0 else 0.0


def variance_check(series: pd.Series, cv_threshold: float = 0.10) -> Dict[str, float]:
    """
    Check variance diagnostics for correlation analysis.

    Low variance (CV < 10%) → rank correlation unreliable.

    Args:
        series: Values to check
        cv_threshold: Coefficient of variation threshold

    Returns:
        Dict with cv, mean, std, variance_ok
    """
    mean = series.mean()
    std = series.std()
    cv = std / abs(mean) if mean != 0 else 0

    return {"cv": cv, "mean": mean, "std": std, "variance_ok": cv >= cv_threshold}


def format_p_value(p: float) -> str:
    """
    Format p-value for display.

    Args:
        p: p-value

    Returns:
        Formatted string (e.g., "4.2e-6" or "0.023")
    """
    if p < 0.001:
        return f"{p:.1e}"
    else:
        return f"{p:.3f}"
