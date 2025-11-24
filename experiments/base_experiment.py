"""Base Experiment Framework for ARCHCODE."""

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.vizir.config_loader import VIZIRConfigLoader
from src.vizir.integrity import compute_config_hashes, record_run


@dataclass
class ExperimentResult:
    """Experiment result container."""

    experiment_id: str
    timestamp: str
    profiles: dict[str, str]
    hypotheses: dict[str, str]
    metrics: dict[str, Any]
    config_hash: str


class BaseExperiment:
    """
    Base class for ARCHCODE experiments.

    Provides:
    - VIZIR config loading
    - Run provenance tracking
    - Result serialization
    """

    def __init__(
        self,
        experiment_id: str,
        output_dir: Path = Path("data/output"),
    ) -> None:
        """
        Initialize experiment.

        Args:
            experiment_id: Unique experiment identifier
            output_dir: Output directory for results
        """
        self.experiment_id = experiment_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.loader = VIZIRConfigLoader()
        self.profiles: dict[str, str] = {}
        self.hypotheses: dict[str, str] = {}

    def load_hypothesis_profile(
        self, unknown_id: str, hypothesis: str, layer: str
    ) -> dict[str, Any]:
        """
        Load hypothesis profile.

        Args:
            unknown_id: Unknown ID (P1, S1, L1, etc.)
            hypothesis: Hypothesis name (hypothesis_a, hypothesis_b)
            layer: Layer type (physical, structural, logical)

        Returns:
            Hypothesis parameters
        """
        self.hypotheses[unknown_id] = hypothesis
        return self.loader.load_hypothesis(unknown_id, hypothesis, layer)

    def record_experiment_run(self) -> str:
        """
        Record experiment run in provenance log.

        Returns:
            Config hash
        """
        config_hash = hashlib.sha256(
            json.dumps(compute_config_hashes(), sort_keys=True).encode()
        ).hexdigest()

        record_run(
            profiles=self.profiles,
            hypotheses=self.hypotheses,
            config_hash=config_hash,
        )

        return config_hash

    def save_result(self, result: ExperimentResult) -> Path:
        """
        Save experiment result.

        Args:
            result: Experiment result

        Returns:
            Path to saved result file
        """
        # Save JSON
        json_path = self.output_dir / f"{self.experiment_id}_result.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2)

        return json_path

    def run(self) -> ExperimentResult:
        """
        Run experiment (to be implemented by subclasses).

        Returns:
            Experiment result
        """
        raise NotImplementedError("Subclasses must implement run()")

