"""Output Exporters - Export ARCHCODE results to various formats."""

import json
from pathlib import Path
from typing import Any

import pandas as pd


class JSONExporter:
    """Export results to JSON format."""

    @staticmethod
    def export(
        data: dict[str, Any],
        output_path: Path,
        indent: int = 2,
        include_metadata: bool = True,
    ) -> Path:
        """
        Export data to JSON.

        Args:
            data: Data dictionary
            output_path: Output file path
            indent: JSON indentation
            include_metadata: Include ARCHCODE metadata

        Returns:
            Path to exported file
        """
        export_data = data.copy()

        if include_metadata:
            export_data["metadata"] = {
                "format_version": "1.0",
                "exporter": "ARCHCODE JSONExporter",
                "schema": "archcode_results_v1",
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=indent)

        return output_path


class CSVExporter:
    """Export results to CSV format."""

    @staticmethod
    def export_boundaries(
        boundaries: list[dict[str, Any]], output_path: Path
    ) -> Path:
        """
        Export boundaries to CSV.

        Args:
            boundaries: List of boundary dictionaries
            output_path: Output file path

        Returns:
            Path to exported file
        """
        df = pd.DataFrame(boundaries)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path

    @staticmethod
    def export_stability_predictions(
        predictions: list[dict[str, Any]], output_path: Path
    ) -> Path:
        """
        Export stability predictions to CSV.

        Args:
            predictions: List of prediction dictionaries
            output_path: Output file path

        Returns:
            Path to exported file
        """
        df = pd.DataFrame(predictions)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path

    @staticmethod
    def export_collapse_results(
        collapse_results: dict[int, dict[str, Any]], output_path: Path
    ) -> Path:
        """
        Export collapse results to CSV.

        Args:
            collapse_results: Dictionary of collapse results
            output_path: Output file path

        Returns:
            Path to exported file
        """
        rows = []
        for position, result in collapse_results.items():
            row = {"position": position, **result}
            rows.append(row)

        df = pd.DataFrame(rows)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path


class VIZIRLogExporter:
    """Export to VIZIR log format."""

    @staticmethod
    def export(
        results: dict[str, Any],
        experiment_id: str,
        output_path: Path,
        config_hash: str | None = None,
    ) -> Path:
        """
        Export results to VIZIR log format.

        Args:
            results: Results dictionary
            experiment_id: Experiment identifier
            output_path: Output file path
            config_hash: Configuration hash (optional)

        Returns:
            Path to exported file
        """
        log_entry = {
            "experiment_id": experiment_id,
            "results": results,
            "config_hash": config_hash,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return output_path


class ARCHCODEExporter:
    """
    Unified ARCHCODE exporter.

    Combines all export formats.
    """

    def __init__(self, output_dir: Path = Path("data/output")) -> None:
        """
        Initialize exporter.

        Args:
            output_dir: Output directory
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.json_exporter = JSONExporter()
        self.csv_exporter = CSVExporter()
        self.vizir_exporter = VIZIRLogExporter()

    def export_full_pipeline_results(
        self,
        results: dict[str, Any],
        experiment_id: str,
        formats: list[str] | None = None,
        config_hash: str | None = None,
    ) -> dict[str, Path]:
        """
        Export full pipeline results in multiple formats.

        Args:
            results: Full pipeline results
            experiment_id: Experiment identifier
            formats: List of formats (json, csv, vizir) - defaults to all
            config_hash: Configuration hash

        Returns:
            Dictionary mapping format to output path
        """
        if formats is None:
            formats = ["json", "csv", "vizir"]

        exported_paths = {}

        # JSON export
        if "json" in formats:
            json_path = self.output_dir / f"{experiment_id}_full_results.json"
            exported_paths["json"] = self.json_exporter.export(
                results, json_path
            )

        # CSV exports
        if "csv" in formats:
            if "boundaries" in results:
                boundaries_path = (
                    self.output_dir / f"{experiment_id}_boundaries.csv"
                )
                exported_paths["csv_boundaries"] = (
                    self.csv_exporter.export_boundaries(
                        results["boundaries"], boundaries_path
                    )
                )

            if "stability_predictions" in results:
                stability_path = (
                    self.output_dir / f"{experiment_id}_stability.csv"
                )
                exported_paths["csv_stability"] = (
                    self.csv_exporter.export_stability_predictions(
                        results["stability_predictions"], stability_path
                    )
                )

            if "collapse_results" in results and results["collapse_results"]:
                collapse_path = (
                    self.output_dir / f"{experiment_id}_collapse.csv"
                )
                exported_paths["csv_collapse"] = (
                    self.csv_exporter.export_collapse_results(
                        results["collapse_results"], collapse_path
                    )
                )

        # VIZIR log export
        if "vizir" in formats:
            vizir_path = self.output_dir / f"{experiment_id}.vizirlog"
            exported_paths["vizir"] = self.vizir_exporter.export(
                results, experiment_id, vizir_path, config_hash
            )

        return exported_paths








