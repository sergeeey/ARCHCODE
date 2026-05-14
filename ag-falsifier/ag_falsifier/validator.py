"""Core validator class for AlphaGenome variant predictions."""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import pandas as pd
import json
from datetime import datetime

from .statistical import (
    category_matched_permutation,
    mann_whitney_test,
    shuffled_labels_test,
    seed_sensitivity_test,
)
from .adr import generate_adr


@dataclass
class ValidationResult:
    """Result of AlphaGenome validation."""

    test_validity: str  # "VALID" / "PARTIAL" / "INVALID"
    p_value: float
    verdict: str  # "PASS" / "WEAK" / "FAIL"
    interpretation: str
    warning: Optional[str] = None

    # Detailed results
    group_difference_p: Optional[float] = None
    rank_correlation_rho: Optional[float] = None
    rank_correlation_p: Optional[float] = None
    insufficient_categories: Optional[Dict] = None
    seed_sensitivity: Optional[Dict] = None
    negative_controls: Optional[Dict] = None

    # Metadata
    timestamp: str = ""
    modality: str = "CAGE"
    n_pearls: int = 0
    n_controls: int = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_adr(self, path: str) -> None:
        """Generate ADR (Architectural Decision Record)."""
        adr_content = generate_adr(self)
        with open(path, "w", encoding="utf-8") as f:
            f.write(adr_content)

    def to_json(self, path: str) -> None:
        """Export results to JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)


class AlphaGenomeValidator:
    """Falsification-first validator for AlphaGenome predictions."""

    def __init__(
        self,
        pearls: pd.DataFrame,
        controls: pd.DataFrame,
        api_key: str,
        interval: Optional[str] = None,
    ):
        """
        Initialize validator.

        Args:
            pearls: DataFrame with structural fragility candidates
            controls: DataFrame with benign controls
            api_key: AlphaGenome API key
            interval: Genomic interval (auto-detect if None)
        """
        self.pearls = pearls
        self.controls = controls
        self.api_key = api_key
        self.interval = interval

        # Validate required columns
        required = ["Variant_ID", "Category", "AlphaGenome_CAGE"]
        for df_name, df in [("pearls", pearls), ("controls", controls)]:
            missing = [col for col in required if col not in df.columns]
            if missing:
                raise ValueError(f"{df_name} missing columns: {missing}")

    def validate(
        self,
        modality: str = "CAGE",
        category_matched: bool = True,
        permutation_test: bool = True,
        n_permutations: int = 10000,
        negative_controls: Optional[List[str]] = None,
        seed_sensitivity: Optional[List[int]] = None,
        alpha: float = 0.01,
    ) -> ValidationResult:
        """
        Run validation with automatic controls.

        Args:
            modality: AlphaGenome modality (CAGE, ATAC, RNA_SEQ, etc.)
            category_matched: Auto-match controls by category
            permutation_test: Run permutation test
            n_permutations: Number of permutations
            negative_controls: List of negative control types
            seed_sensitivity: List of random seeds to test
            alpha: Significance threshold

        Returns:
            ValidationResult with verdict and detailed diagnostics
        """
        if negative_controls is None:
            negative_controls = ["shuffled_labels"]
        if seed_sensitivity is None:
            seed_sensitivity = [1, 7, 21, 42, 100]

        # Combine datasets
        df = pd.concat(
            [self.pearls.assign(Pearl=True), self.controls.assign(Pearl=False)], ignore_index=True
        )

        # Primary test: category-matched permutation (if enabled)
        if category_matched and permutation_test:
            cat_result = category_matched_permutation(
                df=df,
                pearls=self.pearls,
                n_perms=n_permutations,
                seed=42,
                value_col=f"AlphaGenome_{modality}",
            )

            test_validity = cat_result["test_validity"]
            p_value = cat_result["p_value"]
            warning = cat_result.get("warning")
            insufficient_categories = cat_result.get("insufficient_categories")
        else:
            # Fallback: simple Mann-Whitney
            mw_result = mann_whitney_test(
                self.pearls[f"AlphaGenome_{modality}"], self.controls[f"AlphaGenome_{modality}"]
            )
            test_validity = "VALID"
            p_value = mw_result["p_value"]
            warning = None
            insufficient_categories = None

        # Negative controls
        neg_control_results = {}
        if "shuffled_labels" in negative_controls:
            shuffled = shuffled_labels_test(df, value_col=f"AlphaGenome_{modality}")
            neg_control_results["shuffled_labels"] = shuffled

        # Seed sensitivity
        seed_results = None
        if len(seed_sensitivity) > 1:
            seed_results = seed_sensitivity_test(
                df=df,
                pearls=self.pearls,
                seeds=seed_sensitivity,
                n_perms=n_permutations,
                value_col=f"AlphaGenome_{modality}",
            )

        # Generate verdict
        verdict = self._generate_verdict(
            test_validity=test_validity,
            p_value=p_value,
            alpha=alpha,
            negative_controls=neg_control_results,
            seed_sensitivity=seed_results,
        )

        # Interpretation
        interpretation = self._interpret_result(
            verdict=verdict, test_validity=test_validity, p_value=p_value, warning=warning
        )

        return ValidationResult(
            test_validity=test_validity,
            p_value=p_value,
            verdict=verdict,
            interpretation=interpretation,
            warning=warning,
            insufficient_categories=insufficient_categories,
            seed_sensitivity=seed_results,
            negative_controls=neg_control_results,
            modality=modality,
            n_pearls=len(self.pearls),
            n_controls=len(self.controls),
        )

    def _generate_verdict(
        self,
        test_validity: str,
        p_value: float,
        alpha: float,
        negative_controls: Dict,
        seed_sensitivity: Optional[Dict],
    ) -> str:
        """Generate PASS/WEAK/FAIL verdict."""

        # Priority 0: Check test validity FIRST
        if test_validity == "INVALID":
            return "FAIL"

        if test_validity == "PARTIAL":
            return "WEAK"

        # Priority 1: Check p-value
        if p_value >= 0.05:
            return "FAIL"

        if p_value >= alpha:
            return "WEAK"

        # Priority 2: Check negative controls
        if negative_controls:
            for control_name, control_result in negative_controls.items():
                if control_result.get("p_value", 1.0) < 0.05:
                    return "WEAK"  # Control also significant = problem

        # Priority 3: Check seed sensitivity
        if seed_sensitivity:
            p_range = seed_sensitivity.get("p_value_range", [0, 0])
            if p_range[1] > 0.05:
                return "WEAK"  # Unstable across seeds

        return "PASS"

    def _interpret_result(
        self, verdict: str, test_validity: str, p_value: float, warning: Optional[str]
    ) -> str:
        """Generate human-readable interpretation."""

        if verdict == "FAIL":
            if test_validity == "INVALID":
                return "Test INVALID: hypothesis cannot be tested with available data"
            else:
                return f"Null hypothesis NOT rejected (p={p_value:.4f})"

        if verdict == "WEAK":
            if test_validity == "PARTIAL":
                return f"Test PARTIAL: {warning}"
            else:
                return f"Marginal significance (p={p_value:.4f}, threshold 0.01)"

        # PASS
        return f"Validated: pearls show significant {self.pearls.columns[0]} disruption (p={p_value:.2e})"
