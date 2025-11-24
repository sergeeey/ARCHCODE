"""Boundary Collapse Simulator - Simulate TAD boundary collapse and consequences."""

__version__ = "1.0.0-alpha"

from src.boundary_collapse.models import (
    BoundaryState,
    CollapseEvent,
    CollapseEventType,
    CollapseResult,
    EnhancerPromoterPair,
)
from src.boundary_collapse.risk_scoring import RiskScorer
from src.boundary_collapse.scenarios import CollapseScenarios
from src.boundary_collapse.simulator import BoundaryCollapseSimulator

__all__ = [
    "BoundaryCollapseSimulator",
    "RiskScorer",
    "CollapseScenarios",
    "BoundaryState",
    "CollapseEvent",
    "CollapseEventType",
    "CollapseResult",
    "EnhancerPromoterPair",
]
