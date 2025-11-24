"""Boundary Collapse Simulator - Main collapse simulation engine."""

import random
from typing import Any

from src.boundary_collapse.models import (
    BoundaryState,
    CollapseEvent,
    CollapseEventType,
    CollapseResult,
)


class BoundaryCollapseSimulator:
    """
    Simulate TAD boundary collapse under various conditions.

    Models:
    - Methylation-induced collapse
    - CTCF mutation/loss
    - TE insertion effects
    - Non-B DNA conflicts
    - Transcription competition
    """

    def __init__(self, config: dict, vizir_configs: dict | None = None) -> None:
        """
        Initialize collapse simulator.

        Args:
            config: Configuration from boundary_collapse.yaml
            vizir_configs: Optional VIZIR configs (S1, L2, L1)
        """
        self.config = config
        self.vizir_configs = vizir_configs or {}

        # Load collapse triggers
        self.triggers = config.get("collapse_triggers", {})
        self.dynamics = config.get("collapse_dynamics", {})
        self.consequences = config.get("consequences", {})

    def simulate_methylation_event(
        self, boundary_state: BoundaryState, delta: float
    ) -> CollapseEvent:
        """
        Simulate methylation spike event.

        Args:
            boundary_state: Current boundary state
            delta: Methylation level increase

        Returns:
            CollapseEvent
        """
        new_methylation = min(1.0, boundary_state.methylation_level + delta)
        threshold = self.triggers.get("methylation", {}).get("threshold", 0.7)

        magnitude = 1.0 if new_methylation >= threshold else new_methylation / threshold

        return CollapseEvent(
            event_type=CollapseEventType.METHYLATION_SPIKE,
            position=boundary_state.position,
            magnitude=magnitude,
            metadata={"delta": delta, "new_methylation": new_methylation},
        )

    def simulate_ctcf_loss(
        self, boundary_state: BoundaryState, affinity_drop: float = 0.5
    ) -> CollapseEvent:
        """
        Simulate CTCF loss/mutation event.

        Args:
            boundary_state: Current boundary state
            affinity_drop: CTCF affinity reduction

        Returns:
            CollapseEvent
        """
        new_strength = max(0.0, boundary_state.ctcf_strength - affinity_drop)
        threshold = self.triggers.get("ctcf_mutation", {}).get(
            "strength_reduction", 0.5
        )

        magnitude = (
            1.0 if affinity_drop >= threshold else affinity_drop / threshold
        )

        return CollapseEvent(
            event_type=CollapseEventType.CTCF_LOSS,
            position=boundary_state.position,
            magnitude=magnitude,
            metadata={"affinity_drop": affinity_drop, "new_strength": new_strength},
        )

    def simulate_te_insertion(
        self, boundary_state: BoundaryState, wapl_recruiting: bool = True
    ) -> CollapseEvent:
        """
        Simulate TE insertion event.

        Args:
            boundary_state: Current boundary state
            wapl_recruiting: Whether TE recruits WAPL

        Returns:
            CollapseEvent
        """
        magnitude = 0.7 if wapl_recruiting else 0.3

        return CollapseEvent(
            event_type=CollapseEventType.TE_INSERTION,
            position=boundary_state.position,
            magnitude=magnitude,
            metadata={"wapl_recruiting": wapl_recruiting},
        )

    def calculate_collapse_probability(
        self, boundary_state: BoundaryState, events: list[CollapseEvent]
    ) -> float:
        """
        Calculate collapse probability from events.

        Args:
            boundary_state: Current boundary state
            events: List of collapse events

        Returns:
            Collapse probability (0.0-1.0)
        """
        if not events:
            return 0.0

        # Base probability from boundary stability
        base_probability = 1.0 - boundary_state.stability_score

        # Event contributions
        event_probabilities = []
        for event in events:
            trigger_config = self.triggers.get(event.event_type.value, {})
            collapse_prob = trigger_config.get("collapse_probability", 0.5)
            event_probabilities.append(event.magnitude * collapse_prob)

        # Combine probabilities (multiplicative)
        combined_probability = base_probability
        for prob in event_probabilities:
            combined_probability = 1.0 - (1.0 - combined_probability) * (
                1.0 - prob
            )

        return min(1.0, combined_probability)

    def simulate_collapse_dynamics(
        self,
        boundary_state: BoundaryState,
        events: list[CollapseEvent],
        time_steps: int = 100,
    ) -> tuple[bool, float | None]:
        """
        Simulate collapse dynamics over time.

        Args:
            boundary_state: Initial boundary state
            events: List of collapse events
            time_steps: Number of time steps

        Returns:
            Tuple of (collapse_occurred, collapse_time)
        """
        collapse_probability = self.calculate_collapse_probability(
            boundary_state, events
        )

        # Check for sudden collapse
        sudden_prob = self.dynamics.get("sudden_collapse", {}).get("probability", 0.1)
        if random.random() < sudden_prob * collapse_probability:
            return True, 0.0

        # Gradual collapse
        if self.dynamics.get("gradual_collapse", {}).get("enabled", True):
            decay_rate = self.dynamics["gradual_collapse"].get("decay_rate", 0.01)
            min_strength = self.dynamics["gradual_collapse"].get("min_strength", 0.2)

            current_strength = boundary_state.ctcf_strength
            for t in range(time_steps):
                current_strength -= decay_rate * collapse_probability
                if current_strength <= min_strength:
                    return True, float(t)

        # Check final collapse probability
        if random.random() < collapse_probability:
            return True, float(time_steps)

        return False, None

    def run_collapse_scenario(
        self,
        boundary_id: str,
        boundary_state: BoundaryState,
        events: list[dict[str, Any]],
    ) -> CollapseResult:
        """
        Run collapse scenario simulation.

        Args:
            boundary_id: Boundary identifier
            boundary_state: Initial boundary state
            events: List of event dictionaries with 'type' and parameters

        Returns:
            CollapseResult
        """
        # Convert event dicts to CollapseEvent objects
        collapse_events = []
        for event_dict in events:
            event_type_str = event_dict.get("type", "")
            if event_type_str == "methylation_spike":
                event = self.simulate_methylation_event(
                    boundary_state, event_dict.get("delta", 0.0)
                )
            elif event_type_str == "ctcf_loss":
                affinity_drop = event_dict.get("affinity_drop", 0.5)
                if isinstance(event_dict.get("effect"), (int, float)):
                    affinity_drop = event_dict.get("effect", 0.5)
                event = self.simulate_ctcf_loss(boundary_state, affinity_drop)
            elif event_type_str == "te_insertion":
                event = self.simulate_te_insertion(
                    boundary_state, event_dict.get("wapl_recruiting", True)
                )
            else:
                continue  # Skip unknown event types
            collapse_events.append(event)

        # Calculate collapse probability
        collapse_probability = self.calculate_collapse_probability(
            boundary_state, collapse_events
        )

        # Simulate collapse dynamics
        collapse_occurred, collapse_time = self.simulate_collapse_dynamics(
            boundary_state, collapse_events
        )

        # Calculate stability after events
        stability_after = boundary_state.stability_score
        if collapse_occurred:
            stability_after = 0.0
        else:
            # Reduce stability based on events
            for event in collapse_events:
                stability_after *= 1.0 - event.magnitude * 0.3
            stability_after = max(0.0, stability_after)

        # Calculate risks (will be implemented in risk_scoring.py)
        enhancer_hijacking_risk = 0.0  # Placeholder
        oncogenic_risk = 0.0  # Placeholder
        total_risk_score = collapse_probability

        return CollapseResult(
            boundary_id=boundary_id,
            boundary_position=boundary_state.position,
            collapse_probability=collapse_probability,
            collapse_occurred=collapse_occurred,
            collapse_time=collapse_time,
            events=collapse_events,
            enhancer_hijacking_risk=enhancer_hijacking_risk,
            oncogenic_risk=oncogenic_risk,
            total_risk_score=total_risk_score,
            stability_before=boundary_state.stability_score,
            stability_after=stability_after,
        )

