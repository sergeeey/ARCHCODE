"""Boundary Collapse Models - Event types and data structures."""

from dataclasses import dataclass
from enum import Enum


class CollapseEventType(Enum):
    """Types of boundary collapse events."""

    METHYLATION_SPIKE = "methylation_spike"
    CTCF_MUTATION = "ctcf_mutation"
    CTCF_LOSS = "ctcf_loss"
    TE_INSERTION = "te_insertion"
    NONB_DNA_CONFLICT = "nonb_dna_conflict"
    TRANSCRIPTION_COMPETITION = "transcription_competition"


@dataclass
class CollapseEvent:
    """Single collapse event."""

    event_type: CollapseEventType
    position: int
    magnitude: float  # 0.0-1.0: Event strength
    metadata: dict | None = None  # Additional event data


@dataclass
class CollapseResult:
    """Result of boundary collapse simulation."""

    boundary_id: str
    boundary_position: int
    collapse_probability: float  # 0.0-1.0
    collapse_occurred: bool
    collapse_time: float | None  # Time step when collapse occurred
    events: list[CollapseEvent]
    enhancer_hijacking_risk: float  # 0.0-1.0
    oncogenic_risk: float  # 0.0-1.0
    total_risk_score: float  # Combined risk score
    stability_before: float  # Stability score before events
    stability_after: float  # Stability score after events


@dataclass
class EnhancerPromoterPair:
    """Enhancer-promoter pair for hijacking risk calculation."""

    enhancer_position: int
    promoter_position: int
    gene_name: str
    distance: int  # Genomic distance (bp)
    is_oncogenic: bool  # Known oncogenic pair (e.g., MYC-TERT)


@dataclass
class BoundaryState:
    """Current state of a boundary."""

    position: int
    ctcf_strength: float
    methylation_level: float
    stability_score: float
    barrier_strengths: list[float]
    te_motif_effects: list[float]







