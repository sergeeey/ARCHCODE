"""Risk Analyzer - VIZIR risk matrix management."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Risk:
    """Risk representation."""

    risk_id: str
    category: str
    uncertainty: float
    impact_on_model: float
    priority: float
    description: str
    affected_modules: list[str]
    status: str


class RiskAnalyzer:
    """VIZIR Risk Analyzer - Manage and analyze engineering unknowns."""

    def __init__(self, risk_matrix_dir: Path) -> None:
        """
        Initialize risk analyzer.

        Args:
            risk_matrix_dir: Directory containing risk YAML files
        """
        self.risk_matrix_dir = risk_matrix_dir
        self.risks: dict[str, Risk] = {}
        self._load_risks()

    def _load_risks(self) -> None:
        """Load all risk files from risk_matrix directory."""
        if not self.risk_matrix_dir.exists():
            return

        for risk_file in self.risk_matrix_dir.glob("*.yaml"):
            if risk_file.name == "CHANGELOG.md":
                continue
            try:
                with open(risk_file, encoding="utf-8") as f:
                    risk_data = yaml.safe_load(f)
                    risk = Risk(
                        risk_id=risk_data["risk_id"],
                        category=risk_data["category"],
                        uncertainty=risk_data["uncertainty"],
                        impact_on_model=risk_data["impact_on_model"],
                        priority=risk_data["priority"],
                        description=risk_data.get("description", ""),
                        affected_modules=risk_data.get("affected_modules", []),
                        status=risk_data.get("status", "open"),
                    )
                    self.risks[risk.risk_id] = risk
            except Exception as e:
                print(f"Warning: Failed to load risk file {risk_file}: {e}")

    def get_risk(self, risk_id: str) -> Risk | None:
        """
        Get risk by ID.

        Args:
            risk_id: Risk identifier (e.g., "P1", "S1", "L1")

        Returns:
            Risk if found, None otherwise
        """
        return self.risks.get(risk_id)

    def get_risks_by_category(self, category: str) -> list[Risk]:
        """
        Get all risks in category.

        Args:
            category: Risk category ("Physical", "Syntax", "Logic")

        Returns:
            List of risks
        """
        return [r for r in self.risks.values() if r.category == category]

    def get_critical_risks(self, threshold: float = 0.7) -> list[Risk]:
        """
        Get risks with priority above threshold.

        Args:
            threshold: Priority threshold

        Returns:
            List of critical risks
        """
        return [r for r in self.risks.values() if r.priority >= threshold]







