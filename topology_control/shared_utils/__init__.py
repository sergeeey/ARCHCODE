"""
Shared utilities for Active Topological Regulation (ATR) Framework

Modules:
- topology_utils: knots, catenanes, linking numbers, TOP2 strand passage
- graph_utils: Laplacian, spectral analysis, percolation, contact graphs
- phase_utils: free energy, order parameters, phase transitions, condensates
"""

from .topology_utils import (
    TopologicalState,
    calculate_complexity,
    gauss_linking_integral,
    detect_knot_simplified,
    calculate_catenation_simple,
    strand_passage_random,
    strand_passage_angle_bias,
    strand_passage_curvature_bias,
    create_simple_ring,
    create_linked_rings,
)

from .graph_utils import (
    SpectralProperties,
    compute_laplacian,
    spectral_decomposition,
    algebraic_connectivity,
    fiedler_vector,
    spectral_perturbation,
    modularity,
    percolation_giant_component,
    contact_graph_from_hic,
    tad_boundaries_from_laplacian,
    snp_edge_perturbation,
)

from .phase_utils import (
    PhaseState,
    landau_free_energy,
    equilibrium_order_parameter,
    phase_diagram_scan,
    nucleation_barrier,
    threshold_response,
    condensate_probability,
    snp_phase_effect,
    compaction_free_energy,
    accessibility_from_compaction,
)

__all__ = [
    # Topology
    "TopologicalState",
    "calculate_complexity",
    "gauss_linking_integral",
    "detect_knot_simplified",
    "calculate_catenation_simple",
    "strand_passage_random",
    "strand_passage_angle_bias",
    "strand_passage_curvature_bias",
    "create_simple_ring",
    "create_linked_rings",
    # Graph
    "SpectralProperties",
    "compute_laplacian",
    "spectral_decomposition",
    "algebraic_connectivity",
    "fiedler_vector",
    "spectral_perturbation",
    "modularity",
    "percolation_giant_component",
    "contact_graph_from_hic",
    "tad_boundaries_from_laplacian",
    "snp_edge_perturbation",
    # Phase
    "PhaseState",
    "landau_free_energy",
    "equilibrium_order_parameter",
    "phase_diagram_scan",
    "nucleation_barrier",
    "threshold_response",
    "condensate_probability",
    "snp_phase_effect",
    "compaction_free_energy",
    "accessibility_from_compaction",
]

__version__ = "0.1.0"
