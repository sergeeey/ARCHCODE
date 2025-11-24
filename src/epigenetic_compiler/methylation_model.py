"""Methylation Model - CpG methylation dynamics."""

from dataclasses import dataclass


@dataclass
class CpGSite:
    """CpG methylation site."""

    position: int  # Genomic position (bp)
    methylation_level: float  # 0.0 (unmethylated) to 1.0 (fully methylated)
    ctcf_bound: bool  # Whether CTCF is bound


class MethylationModel:
    """
    CpG Methylation Dynamics Model.

    Engineering Unknown L3: CpG methylation threshold for CTCF inactivation.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize methylation model.

        Args:
            config: Configuration from epigenetic_compiler.yaml
        """
        self.config = config.get("methylation_parameters", {})
        self.methylation_rate = self.config.get("methylation_rate", 0.01)
        self.demethylation_rate = self.config.get("demethylation_rate", 0.001)
        self.ctcf_threshold = self.config.get("ctcf_inactivation_threshold", 0.7)

        self.cpg_sites: dict[int, CpGSite] = {}

    def add_cpg_site(self, position: int, initial_methylation: float = 0.0) -> None:
        """
        Add CpG site to model.

        Args:
            position: Genomic position
            initial_methylation: Initial methylation level
        """
        self.cpg_sites[position] = CpGSite(
            position=position,
            methylation_level=initial_methylation,
            ctcf_bound=True,
        )

    def update_methylation(self, time_step: float) -> None:
        """
        Update methylation levels for one time step.

        Args:
            time_step: Time step duration
        """
        for site in self.cpg_sites.values():
            # Stochastic methylation/demethylation
            import random

            if random.random() < self.methylation_rate * time_step:
                site.methylation_level = min(1.0, site.methylation_level + 0.1)

            if random.random() < self.demethylation_rate * time_step:
                site.methylation_level = max(0.0, site.methylation_level - 0.1)

            # Check CTCF inactivation
            if site.methylation_level >= self.ctcf_threshold:
                site.ctcf_bound = False
            else:
                site.ctcf_bound = True

    def get_boundary_strength(self, position: int) -> float:
        """
        Get boundary strength based on methylation.

        Args:
            position: Genomic position

        Returns:
            Boundary strength (0.0-1.0)
        """
        site = self.cpg_sites.get(position)
        if site is None:
            return 1.0  # Default strength

        if site.ctcf_bound:
            return 1.0 - site.methylation_level
        else:
            return 0.0  # CTCF inactivated







