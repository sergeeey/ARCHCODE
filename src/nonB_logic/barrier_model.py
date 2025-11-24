"""Energy Barrier Model - G4, Z-DNA, R-loops."""

from dataclasses import dataclass
from enum import Enum


class BarrierType(Enum):
    """Types of energy barriers."""

    G4 = "g4"
    Z_DNA = "z_dna"
    RLOOP = "rloop"


@dataclass
class EnergyBarrier:
    """Energy barrier representation."""

    position: int  # Genomic position (bp)
    barrier_type: BarrierType
    strength: float  # Barrier strength (0.0-1.0)
    energy: float  # Energy value (kcal/mol or arbitrary)


class G4Model:
    """
    G4 Formation Model.

    Engineering Unknown L2: G4 formation conditions in vivo.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize G4 model.

        Args:
            config: Configuration from nonB_logic.yaml
        """
        self.config = config.get("g4_parameters", {})
        self.formation_energy = self.config.get("formation_energy", 0.0)
        self.stability_threshold = self.config.get("stability_threshold", 0.5)

    def detect_g4(self, sequence: str, position: int) -> EnergyBarrier | None:
        """
        Detect G4 formation potential.

        Args:
            sequence: DNA sequence
            position: Genomic position

        Returns:
            EnergyBarrier if G4 detected, None otherwise
        """
        # TODO: Implement G4 detection algorithm
        # Placeholder: return None
        return None

    def calculate_stability(self, sequence: str) -> float:
        """
        Calculate G4 stability score.

        Args:
            sequence: G4-forming sequence

        Returns:
            Stability score (0.0-1.0)
        """
        # TODO: Implement stability calculation
        return 0.0


class ZDNAModel:
    """
    Z-DNA Transition Model.

    Z-DNA formation is CONTROLLED by:
    1. Sequence preference: alternating purine-pyrimidine (especially GC repeats)
    2. Negative supercoiling (torque): transcription creates negative supercoiling
    3. Ionic conditions: high salt concentrations stabilize Z-DNA
    4. Protein binding: ZBP1, ADAR1 specifically bind Z-DNA

    Engineering Unknown L1: B → Z-DNA transition threshold.
    """

    def __init__(self, config: dict, vizir_configs: dict | None = None) -> None:
        """
        Initialize Z-DNA model.

        Args:
            config: Configuration from nonB_logic.yaml
            vizir_configs: Optional VIZIR S3/L1 configs
        """
        self.config = config.get("z_dna_parameters", {})
        # v1.1: Use critical_sigma if available, otherwise transition_threshold
        self.transition_threshold = self.config.get("critical_sigma", self.config.get("transition_threshold", -0.06))
        self.sequence_preference_weight = self.config.get("sequence_preference_weight", 0.6)
        self.torque_weight = self.config.get("torque_weight", 0.3)
        self.ionic_stabilization = self.config.get("ionic_stabilization", 0.1)
        self.min_gc_repeat_length = self.config.get("min_gc_repeat_length", 6)
        
        # Load VIZIR configs if provided
        self.vizir_configs = vizir_configs or {}
        self._apply_vizir_configs()

    def _apply_vizir_configs(self) -> None:
        """Apply VIZIR Engineering Unknown configurations."""
        # S3: Non-B DNA
        if "S3" in self.vizir_configs:
            s3 = self.vizir_configs["S3"]
            params = s3.get("parameters", {})
            if "zdna_formation" in params:
                self.config.update(params["zdna_formation"])
        
        # L1: Z-DNA Formation Logic
        if "L1" in self.vizir_configs:
            l1 = self.vizir_configs["L1"]
            params = l1.get("parameters", {})
            if "formation_logic" in params:
                self.sequence_preference_weight = params["formation_logic"].get("sequence_score_weight", 0.6)
                self.torque_weight = params["formation_logic"].get("torque_weight", 0.3)
                # Update config for detect_zdna method
                self.config.update({
                    "sequence_weight": self.sequence_preference_weight,
                    "torque_weight": self.torque_weight,
                    "transcription_weight": params["formation_logic"].get("transcription_weight", 0.1),
                })

    def detect_zdna(
        self,
        sequence: str,
        position: int,
        torque: float,
        transcription_active: bool = False,
    ) -> EnergyBarrier | None:
        """
        Detect Z-DNA formation potential.

        Z-DNA forms when:
        - Sequence has GC repeats (alternating purine-pyrimidine)
        - Negative supercoiling (torque < threshold)
        - Transcription creates negative supercoiling ahead of polymerase

        Args:
            sequence: DNA sequence (should be GC-rich alternating)
            position: Genomic position
            torque: Applied torque (negative = supercoiling)
            transcription_active: Whether transcription is active nearby

        Returns:
            EnergyBarrier if Z-DNA detected, None otherwise
        """
        # 1. Check sequence preference
        sequence_score = self._calculate_sequence_preference(sequence)
        if sequence_score < 0.3:  # Not Z-DNA favorable sequence
            return None

        # 2. Check torque condition
        # Negative torque (supercoiling) promotes Z-DNA
        torque_score = 0.0
        if torque < self.transition_threshold:
            # More negative torque = higher Z-DNA probability
            torque_score = min(1.0, abs(torque) / abs(self.transition_threshold))

        # 3. Transcription effect: creates negative supercoiling
        if transcription_active:
            torque_score = max(torque_score, 0.5)  # Boost from transcription

        # 4. Combined probability
        formation_probability = (
            sequence_score * self.sequence_preference_weight
            + torque_score * self.torque_weight
            + self.ionic_stabilization
        )

        if formation_probability > 0.5:  # Threshold for barrier formation
            barrier_strength = min(1.0, formation_probability)
            # Z-DNA barrier strength correlates with formation probability
            return EnergyBarrier(
                position=position,
                barrier_type=BarrierType.Z_DNA,
                strength=barrier_strength * self.config.get("barrier_strength", 0.6),
                energy=formation_probability * 10.0,  # Arbitrary energy scale
            )

        return None

    def _calculate_sequence_preference(self, sequence: str) -> float:
        """
        Calculate Z-DNA sequence preference score.

        Z-DNA prefers:
        - Alternating purine-pyrimidine (GC, GT, AC, AT)
        - GC repeats are most favorable
        - Minimum length requirement

        Args:
            sequence: DNA sequence to analyze

        Returns:
            Preference score (0.0-1.0)
        """
        if len(sequence) < self.min_gc_repeat_length:
            return 0.0

        # Check for GC repeats (most favorable)
        gc_count = sequence.upper().count("GC")
        cg_count = sequence.upper().count("CG")
        gc_repeat_score = (gc_count + cg_count) / len(sequence)

        # Check for alternating pattern
        alternating_score = self._check_alternating_pattern(sequence)

        # Combined score
        return (gc_repeat_score * 0.7 + alternating_score * 0.3)

    def _check_alternating_pattern(self, sequence: str) -> float:
        """
        Check if sequence has alternating purine-pyrimidine pattern.

        Args:
            sequence: DNA sequence

        Returns:
            Alternating pattern score (0.0-1.0)
        """
        if len(sequence) < 2:
            return 0.0

        purines = {"A", "G"}
        pyrimidines = {"C", "T"}

        alternating_count = 0
        for i in range(len(sequence) - 1):
            base1 = sequence[i].upper()
            base2 = sequence[i + 1].upper()

            # Check if alternating purine-pyrimidine
            if (base1 in purines and base2 in pyrimidines) or (
                base1 in pyrimidines and base2 in purines
            ):
                alternating_count += 1

        return alternating_count / (len(sequence) - 1)


class RLoopModel:
    """R-loop Formation Model."""

    def __init__(self, config: dict) -> None:
        """
        Initialize R-loop model.

        Args:
            config: Configuration from nonB_logic.yaml
        """
        self.config = config.get("rloop_parameters", {})
        self.formation_probability = self.config.get("formation_probability", 0.1)

    def detect_rloop(self, sequence: str, position: int) -> EnergyBarrier | None:
        """
        Detect R-loop formation potential.

        Args:
            sequence: DNA sequence
            position: Genomic position

        Returns:
            EnergyBarrier if R-loop detected, None otherwise
        """
        # TODO: Implement R-loop detection
        return None


class BarrierHierarchy:
    """Barrier hierarchy and interaction logic."""

    def __init__(self, config: dict, vizir_configs: dict | None = None) -> None:
        """
        Initialize barrier hierarchy.

        Args:
            config: Configuration from nonB_logic.yaml
            vizir_configs: Optional VIZIR S3 config
        """
        self.config = config.get("energy_barriers", {})
        self.hierarchy = self.config.get("hierarchy", ["g4", "z_dna", "rloop"])
        self.interaction_mode = self.config.get("interaction_mode", "additive")
        
        # Load VIZIR configs if provided
        self.vizir_configs = vizir_configs or {}
        self._apply_vizir_configs()

    def _apply_vizir_configs(self) -> None:
        """Apply VIZIR Engineering Unknown configurations."""
        # S3: Non-B DNA
        if "S3" in self.vizir_configs:
            s3 = self.vizir_configs["S3"]
            params = s3.get("parameters", {})
            if "hierarchy" in params:
                hierarchy_map = {
                    "g4_priority": "g4",
                    "zdna_priority": "z_dna",
                    "rloop_priority": "rloop",
                }
                priorities = [
                    (params["hierarchy"].get("g4_priority", 1), "g4"),
                    (params["hierarchy"].get("zdna_priority", 2), "z_dna"),
                    (params["hierarchy"].get("rloop_priority", 3), "rloop"),
                ]
                priorities.sort()
                self.hierarchy = [p[1] for p in priorities]

    def combine_barriers(self, barriers: list[EnergyBarrier]) -> float:
        """
        Combine multiple barriers according to hierarchy.

        Args:
            barriers: List of barriers at same position

        Returns:
            Combined barrier strength
        """
        if not barriers:
            return 0.0

        if self.interaction_mode == "additive":
            return sum(b.strength for b in barriers)
        elif self.interaction_mode == "max":
            return max(b.strength for b in barriers)
        else:
            return sum(b.strength for b in barriers)  # Default to additive

