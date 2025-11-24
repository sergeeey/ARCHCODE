"""VIZIR Config Loader - Load and validate P/S/L Engineering Unknowns."""

from pathlib import Path
from typing import Any

import yaml


class VIZIRConfigLoader:
    """
    Load and validate VIZIR Engineering Unknown configurations.

    Supports:
    - Physical layer (P1-P3)
    - Structural layer (S1-S3)
    - Logical layer (L1-L3)
    """

    def __init__(self, config_root: Path | str = "config") -> None:
        """
        Initialize config loader.

        Args:
            config_root: Root directory for config files
        """
        self.config_root = Path(config_root)
        self.physical_dir = self.config_root / "physical"
        self.structural_dir = self.config_root / "structural"
        self.logical_dir = self.config_root / "logical"

    def load_physical(self, unknown_id: str) -> dict[str, Any]:
        """
        Load physical layer unknown.

        Args:
            unknown_id: Unknown ID (P1, P2, P3)

        Returns:
            Configuration dictionary
        """
        matches = list(self.physical_dir.glob(f"{unknown_id}_*.yaml"))

        if not matches:
            raise FileNotFoundError(f"Config not found: {unknown_id}")

        with open(matches[0], encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_structural(self, unknown_id: str) -> dict[str, Any]:
        """
        Load structural layer unknown.

        Args:
            unknown_id: Unknown ID (S1, S2, S3)

        Returns:
            Configuration dictionary
        """
        matches = list(self.structural_dir.glob(f"{unknown_id}_*.yaml"))

        if not matches:
            raise FileNotFoundError(f"Config not found: {unknown_id}")

        with open(matches[0], encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_logical(self, unknown_id: str) -> dict[str, Any]:
        """
        Load logical layer unknown.

        Args:
            unknown_id: Unknown ID (L1, L2, L3)

        Returns:
            Configuration dictionary
        """
        matches = list(self.logical_dir.glob(f"{unknown_id}_*.yaml"))

        if not matches:
            raise FileNotFoundError(f"Config not found: {unknown_id}")

        with open(matches[0], encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_hypothesis(
        self, unknown_id: str, hypothesis: str, layer: str = "physical"
    ) -> dict[str, Any]:
        """
        Load specific hypothesis from unknown.

        Args:
            unknown_id: Unknown ID (P1, S1, L1, etc.)
            hypothesis: Hypothesis name (hypothesis_a, hypothesis_b)
            layer: Layer type (physical, structural, logical)

        Returns:
            Hypothesis parameters
        """
        if layer == "physical":
            config = self.load_physical(unknown_id)
        elif layer == "structural":
            config = self.load_structural(unknown_id)
        elif layer == "logical":
            config = self.load_logical(unknown_id)
        else:
            raise ValueError(f"Unknown layer: {layer}")

        if "hypotheses" not in config:
            raise KeyError(f"No hypotheses in {unknown_id}")

        if hypothesis not in config["hypotheses"]:
            raise KeyError(f"Hypothesis {hypothesis} not found in {unknown_id}")

        return config["hypotheses"][hypothesis]

    def load_all_physical(self) -> dict[str, dict[str, Any]]:
        """Load all physical layer unknowns."""
        configs = {}
        for config_file in self.physical_dir.glob("P*.yaml"):
            unknown_id = config_file.stem.split("_")[0]
            with open(config_file, encoding="utf-8") as f:
                configs[unknown_id] = yaml.safe_load(f)
        return configs

    def load_all_structural(self) -> dict[str, dict[str, Any]]:
        """Load all structural layer unknowns."""
        configs = {}
        for config_file in self.structural_dir.glob("S*.yaml"):
            unknown_id = config_file.stem.split("_")[0]
            with open(config_file, encoding="utf-8") as f:
                configs[unknown_id] = yaml.safe_load(f)
        return configs

    def load_all_logical(self) -> dict[str, dict[str, Any]]:
        """Load all logical layer unknowns."""
        configs = {}
        for config_file in self.logical_dir.glob("L*.yaml"):
            unknown_id = config_file.stem.split("_")[0]
            with open(config_file, encoding="utf-8") as f:
                configs[unknown_id] = yaml.safe_load(f)
        return configs

    def get_integration_path(self, unknown_id: str, layer: str) -> dict[str, Any]:
        """
        Get integration information for unknown.

        Args:
            unknown_id: Unknown ID
            layer: Layer type

        Returns:
            Integration information (module, parameter_path, etc.)
        """
        if layer == "physical":
            config = self.load_physical(unknown_id)
        elif layer == "structural":
            config = self.load_structural(unknown_id)
        elif layer == "logical":
            config = self.load_logical(unknown_id)
        else:
            raise ValueError(f"Unknown layer: {layer}")

        return config.get("integration", {})

