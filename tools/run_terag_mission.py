"""
Run TERAG mission end-to-end through ARCHCODE adapter.

Usage:
    python tools/run_terag_mission.py --mission terag_missions/rs11_multichannel_memory.yaml
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integration.archcode_adapter import ArchcodeAdapter


def load_mission(mission_path: str | Path) -> dict:
    """
    Load mission configuration from YAML file.

    Args:
        mission_path: Path to mission YAML file

    Returns:
        Mission configuration dictionary
    """
    mission_path = Path(mission_path)
    if not mission_path.exists():
        raise FileNotFoundError(f"Mission file not found: {mission_path}")

    with open(mission_path, "r", encoding="utf-8") as f:
        mission = yaml.safe_load(f)

    return mission


def run_mission_e2e(mission_config: dict, output_dir: Path | None = None) -> dict:
    """
    Run mission end-to-end through ARCHCODE adapter.

    Args:
        mission_config: Mission configuration dictionary
        output_dir: Output directory for results (optional)

    Returns:
        Result dictionary from adapter
    """
    # Extract adapter mode
    adapter_config = mission_config.get("adapter", {})
    adapter_mode = adapter_config.get("mode", "fast")

    # Create adapter
    adapter = ArchcodeAdapter(mode=adapter_mode)

    # Prepare mission parameters
    mission_params = {
        "id": mission_config.get("mission", {}).get("id", "UNKNOWN"),
        "mission_type": mission_config.get("parameters", {}).get("mission_type"),
        "parameters": mission_config.get("parameters", {}),
    }

    print("=" * 80)
    print("TERAG MISSION E2E RUN")
    print("=" * 80)
    print(f"Mission ID: {mission_params['id']}")
    print(f"Mission Type: {mission_params['mission_type']}")
    print(f"Adapter Mode: {adapter_mode}")
    print("=" * 80)
    print()

    # Run mission
    result = adapter.run_mission(mission_params)

    # Print summary
    print("=" * 80)
    print("RESULT SUMMARY")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Execution Time: {result['execution_time_sec']}s")

    if result["status"] == "success":
        print(f"Data Keys: {list(result.get('data', {}).keys())}")
        if "phase_map" in result:
            print(f"Phase Map: Present ({len(result['phase_map'].get('nodes', []))} nodes)")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")

    print("=" * 80)
    print()

    # Save results if output_dir provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        mission_id = mission_params["id"]
        output_file = output_dir / f"{mission_id}_result.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, default=str)

        print(f"💾 Results saved: {output_file}")

    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run TERAG mission end-to-end through ARCHCODE adapter"
    )
    parser.add_argument(
        "--mission",
        type=str,
        required=True,
        help="Path to mission YAML file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/output",
        help="Output directory for results (default: data/output)",
    )

    args = parser.parse_args()

    try:
        # Load mission
        mission_config = load_mission(args.mission)

        # Run mission
        result = run_mission_e2e(mission_config, output_dir=args.output_dir)

        # Exit code based on status
        if result["status"] == "success":
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

