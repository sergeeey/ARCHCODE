"""Loop Extrusion Engine - Core simulation logic."""

from dataclasses import dataclass
from enum import Enum


class ExtrusionMode(Enum):
    """Extrusion asymmetry modes."""

    SYMMETRIC = "symmetric"
    ONE_SIDED = "one_sided"
    ASYMMETRIC = "asymmetric"


@dataclass
class ExtrusionEvent:
    """Single loop extrusion event."""

    start_position: int  # Genomic position (bp)
    end_position: int  # Genomic position (bp)
    cohesin_id: int  # Unique cohesin identifier
    direction: int  # +1 or -1
    speed: float  # Extrusion speed (bp/time)


@dataclass
class Boundary:
    """TAD boundary representation."""

    position: int  # Genomic position (bp)
    strength: float  # Boundary strength (0.0-1.0)
    barrier_type: str  # "ctcf", "rloop", "pol2"
    insulation_score: float  # Insulation score
    is_bookmarked: bool = True  # RS-10: CTCF bookmarking status
    effective_strength: float | None = None  # RS-10: Phase-adjusted strength


class LoopExtrusionEngine:
    """
    Loop Extrusion Engine - 1D simulation of TAD formation.

    Models cohesin-mediated loop extrusion with boundary barriers.
    """

    def __init__(
        self, config: dict, vizir_configs: dict | None = None, cell_phase: str = "interphase"
    ) -> None:
        """
        Initialize extrusion engine.

        Args:
            config: Configuration dictionary from archcode_engine.yaml
            vizir_configs: Optional VIZIR P/S/L configs (P1, P2, P3)
            cell_phase: "interphase" or "mitosis" (v1.1: phase-dependent symmetry)
        """
        self.config = config
        self.extrusion_params = config["extrusion_parameters"]
        self.boundary_params = config["boundary_parameters"]
        self.tad_params = config["tad_parameters"]
        self.cell_phase = cell_phase  # v1.1: phase-dependent symmetry

        # Load VIZIR configs if provided
        self.vizir_configs = vizir_configs or {}
        self._apply_vizir_configs()

        # v1.1: NIPBL velocity multiplier (default 1.0)
        self.nipbl_velocity_multiplier = self.extrusion_params.get("nipbl_velocity_multiplier", 1.0)
        
        # v1.1: WAPL lifetime factor (default 1.0)
        self.wapl_lifetime_factor = self.extrusion_params.get("wapl_lifetime_factor", 1.0)

        # State
        self.extrusion_events: list[ExtrusionEvent] = []
        self.boundaries: list[Boundary] = []
        self.current_time: float = 0.0

    def _apply_vizir_configs(self) -> None:
        """Apply VIZIR Engineering Unknown configurations."""
        # P1: Extrusion Symmetry (v1.1: Phase-dependent)
        if "P1" in self.vizir_configs:
            p1 = self.vizir_configs["P1"]
            params = p1.get("parameters", {})
            
            # v1.1: Phase-specific symmetry
            if "interphase_cohesin" in params and self.cell_phase == "interphase":
                interphase = params["interphase_cohesin"]
                self.extrusion_params["extrusion_mode"] = "symmetric"
                self.extrusion_params["symmetry_bias"] = interphase.get("symmetry_bias", 0.05)
            elif "mitotic_condensin" in params and self.cell_phase == "mitosis":
                mitotic = params["mitotic_condensin"]
                self.extrusion_params["extrusion_mode"] = "asymmetric"
                self.extrusion_params["anchor_stability"] = mitotic.get("anchor_stability", "HIGH")
            
            # Legacy support
            if "extrusion_mode" in params:
                mode = params["extrusion_mode"]
                if mode.get("asymmetric"):
                    self.extrusion_params["extrusion_mode"] = "asymmetric"
                elif mode.get("one_sided"):
                    self.extrusion_params["extrusion_mode"] = "one_sided"
            
            if "direction_bias" in params:
                bias = params["direction_bias"]
                self.extrusion_params["direction_bias"] = {
                    "left_probability": bias.get("left_probability", 0.5),
                    "right_probability": bias.get("right_probability", 0.5),
                }

        # P2: Supercoiling
        if "P2" in self.vizir_configs:
            p2 = self.vizir_configs["P2"]
            params = p2.get("parameters", {})
            if "supercoiling_generation" in params:
                self.extrusion_params["supercoiling"] = params["supercoiling_generation"]

        # P3: Cohesin Loading (v1.1: NIPBL Velocity Multiplier)
        if "P3" in self.vizir_configs:
            p3 = self.vizir_configs["P3"]
            params = p3.get("parameters", {})
            
            # v1.1: NIPBL velocity multiplier
            if "nipbl_velocity_multiplier" in params:
                multipliers = params["nipbl_velocity_multiplier"]
                # Use wild_type as default, or allow override
                self.nipbl_velocity_multiplier = multipliers.get("wild_type", 1.0)
                # Check for CdLS conditions
                if "cdls_haploinsufficient" in multipliers:
                    # Could be set via config
                    pass
            
            # v1.1: WAPL lifetime factor
            if "wapl_lifetime_factor" in params:
                factors = params["wapl_lifetime_factor"]
                self.wapl_lifetime_factor = factors.get("wild_type", 1.0)
            
            # Legacy support
            if "loading_site_selection" in params:
                self.extrusion_params["loading_mode"] = params["loading_site_selection"].get("mode", "random")
                self.extrusion_params["loading_probability"] = params["loading_site_selection"].get("probability", 0.01)

    def load_cohesin(self, position: int) -> ExtrusionEvent | None:
        """
        Load cohesin at specified position.

        Args:
            position: Genomic position for cohesin loading

        Returns:
            ExtrusionEvent if loading successful, None otherwise
        """
        # TODO: Implement NIPBL site selection (Risk P1)
        # Placeholder: always load
        
        # v1.1: Apply NIPBL velocity multiplier
        base_speed = self.extrusion_params.get("extrusion_speed", 1.0)
        effective_speed = base_speed * self.nipbl_velocity_multiplier
        
        cohesin_id = len(self.extrusion_events)
        event = ExtrusionEvent(
            start_position=position,
            end_position=position,
            cohesin_id=cohesin_id,
            direction=1,
            speed=effective_speed,  # v1.1: NIPBL-adjusted speed
        )
        self.extrusion_events.append(event)
        return event

    def update_extrusion(self, time_step: float) -> None:
        """
        Update extrusion events for one time step.

        Args:
            time_step: Time step duration
        """
        # v1.1: Apply WAPL lifetime factor (affects processivity)
        effective_time_step = time_step * self.wapl_lifetime_factor
        
        events_to_remove = []
        for i, event in enumerate(self.extrusion_events):
            # Check for boundary collisions BEFORE moving
            # This prevents moving past strong boundaries
            if self._check_boundary_collision(event):
                continue  # Stop extrusion at strong boundary

            # Extrude loop
            # v1.1: Processivity = Rate(NIPBL) × Lifetime(WAPL)
            distance = event.speed * effective_time_step
            new_position = event.end_position + event.direction * int(distance)
            
            # Check if new position would cross a strong boundary
            # Weak boundaries (< 0.5) allow passage
            blocked = False
            for boundary in self.boundaries:
                effective_strength = boundary.effective_strength if boundary.effective_strength is not None else boundary.strength
                # Check if we're crossing a strong boundary
                if (event.end_position < boundary.position <= new_position or 
                    event.end_position > boundary.position >= new_position):
                    if effective_strength > 0.5:  # Strong boundary blocks
                        blocked = True
                        break
            
            if not blocked:
                event.end_position = new_position
            else:
                # Stop at strong boundary
                continue
            
            # v1.1: WAPL-mediated unloading (simplified)
            # In full model, this would check for WAPL recruitment sites
            # Handle edge case: zero lifetime → immediate unloading
            if self.wapl_lifetime_factor <= 0:
                events_to_remove.append(i)
                continue
            
            unload_probability = 0.01 / self.wapl_lifetime_factor  # Inverse of lifetime
            import random
            if random.random() < unload_probability:
                events_to_remove.append(i)

        # Remove unloaded cohesins
        for i in reversed(events_to_remove):
            self.extrusion_events.pop(i)

        self.current_time += time_step

    def _check_boundary_collision(self, event: ExtrusionEvent) -> bool:
        """
        Check if extrusion event collides with boundary.

        Args:
            event: Extrusion event to check

        Returns:
            True if collision detected (strong boundary blocks)
        """
        for boundary in self.boundaries:
            # Check if event has reached or passed boundary position
            # Use effective_strength if available, otherwise use strength
            effective_strength = boundary.effective_strength if boundary.effective_strength is not None else boundary.strength
            
            # Check collision: event reaches boundary position
            if event.end_position >= boundary.position:
                # Strong boundaries (> 0.5) block extrusion
                if effective_strength > 0.5:  # Threshold
                    return True
                # Weak boundaries (< 0.5) don't block - extrusion continues
        return False

    def detect_tads(self) -> list[tuple[int, int]]:
        """
        Detect TAD boundaries from current state.

        Returns:
            List of (start, end) TAD positions
        """
        # TODO: Implement TAD detection algorithm
        # Placeholder: return empty list
        return []

