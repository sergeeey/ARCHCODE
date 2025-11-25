"""Risk Scoring - Enhancer hijacking and oncogenic risk calculation."""

from src.boundary_collapse.models import (
    CollapseResult,
    EnhancerPromoterPair,
)


class RiskScorer:
    """
    Calculate enhancer hijacking and oncogenic risks.

    Models:
    - Enhancer hijacking probability
    - Oncogenic contact risk
    - Combined risk scoring
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize risk scorer.

        Args:
            config: Configuration from boundary_collapse.yaml
        """
        self.config = config
        self.consequences = config.get("consequences", {})
        self.risk_scoring = config.get("risk_scoring", {})

    def calculate_enhancer_hijacking_risk(
        self,
        collapse_result: CollapseResult,
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> float:
        """
        Calculate enhancer hijacking risk.

        Args:
            collapse_result: Collapse simulation result
            enhancer_promoter_pairs: List of enhancer-promoter pairs

        Returns:
            Hijacking risk score (0.0-1.0)
        """
        if not collapse_result.collapse_occurred:
            return 0.0

        max_distance = self.consequences.get("enhancer_hijacking", {}).get(
            "max_distance", 1000000
        )
        hijacking_prob = self.consequences.get("enhancer_hijacking", {}).get(
            "hijacking_probability", 0.3
        )

        # Find pairs within distance
        nearby_pairs = [
            pair
            for pair in enhancer_promoter_pairs
            if abs(pair.enhancer_position - collapse_result.boundary_position)
            <= max_distance
            and abs(pair.promoter_position - collapse_result.boundary_position)
            <= max_distance
        ]

        if not nearby_pairs:
            return 0.0

        # Calculate risk based on distance and collapse probability
        risks = []
        for pair in nearby_pairs:
            distance_factor = 1.0 - (pair.distance / max_distance)
            risk = collapse_result.collapse_probability * distance_factor * hijacking_prob
            risks.append(risk)

        return min(1.0, max(risks) if risks else 0.0)

    def calculate_oncogenic_risk(
        self,
        collapse_result: CollapseResult,
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> float:
        """
        Calculate oncogenic contact risk.

        Args:
            collapse_result: Collapse simulation result
            enhancer_promoter_pairs: List of enhancer-promoter pairs

        Returns:
            Oncogenic risk score (0.0-1.0)
        """
        if not collapse_result.collapse_occurred:
            return 0.0

        # Find oncogenic pairs
        oncogenic_pairs = [
            pair for pair in enhancer_promoter_pairs if pair.is_oncogenic
        ]

        if not oncogenic_pairs:
            return 0.0

        max_distance = self.consequences.get("enhancer_hijacking", {}).get(
            "max_distance", 1000000
        )
        risk_multiplier = self.consequences.get("oncogenic_contacts", {}).get(
            "risk_multiplier", 2.0
        )

        # Check if boundary collapse enables oncogenic contacts
        nearby_oncogenic = [
            pair
            for pair in oncogenic_pairs
            if abs(pair.enhancer_position - collapse_result.boundary_position)
            <= max_distance
        ]

        if not nearby_oncogenic:
            return 0.0

        # Calculate oncogenic risk
        base_risk = collapse_result.collapse_probability
        oncogenic_risk = base_risk * risk_multiplier

        return min(1.0, oncogenic_risk)

    def calculate_total_risk_score(
        self,
        collapse_result: CollapseResult,
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> float:
        """
        Calculate total risk score.

        Args:
            collapse_result: Collapse simulation result
            enhancer_promoter_pairs: List of enhancer-promoter pairs

        Returns:
            Total risk score (0.0-1.0)
        """
        hijacking_risk = self.calculate_enhancer_hijacking_risk(
            collapse_result, enhancer_promoter_pairs
        )
        oncogenic_risk = self.calculate_oncogenic_risk(
            collapse_result, enhancer_promoter_pairs
        )

        # Weighted combination
        weights = self.risk_scoring.get("risk_scoring", {})
        collapse_weight = weights.get("collapse_risk_weight", 0.4)
        hijacking_weight = weights.get("hijacking_risk_weight", 0.3)
        oncogenic_weight = weights.get("oncogenic_risk_weight", 0.3)

        total_risk = (
            collapse_result.collapse_probability * collapse_weight
            + hijacking_risk * hijacking_weight
            + oncogenic_risk * oncogenic_weight
        )

        return min(1.0, total_risk)

    def update_collapse_result_with_risks(
        self,
        collapse_result: CollapseResult,
        enhancer_promoter_pairs: list[EnhancerPromoterPair],
    ) -> CollapseResult:
        """
        Update collapse result with calculated risks.

        Args:
            collapse_result: Collapse simulation result
            enhancer_promoter_pairs: List of enhancer-promoter pairs

        Returns:
            Updated CollapseResult
        """
        enhancer_hijacking_risk = self.calculate_enhancer_hijacking_risk(
            collapse_result, enhancer_promoter_pairs
        )
        oncogenic_risk = self.calculate_oncogenic_risk(
            collapse_result, enhancer_promoter_pairs
        )
        total_risk_score = self.calculate_total_risk_score(
            collapse_result, enhancer_promoter_pairs
        )

        # Update result
        collapse_result.enhancer_hijacking_risk = enhancer_hijacking_risk
        collapse_result.oncogenic_risk = oncogenic_risk
        collapse_result.total_risk_score = total_risk_score

        return collapse_result










