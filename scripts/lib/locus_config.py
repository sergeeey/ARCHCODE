"""
Locus configuration loader for ARCHCODE Python scripts.

ПОЧЕМУ зеркалируем TS: correlate_hic_archcode.py и extract_k562_hbb.py
дублировали те же константы что и generate-unified-atlas.ts.
Один JSON конфиг — один source of truth.
"""

import json
import math
from pathlib import Path
from argparse import ArgumentParser
from typing import Any

# Root of the project (scripts/lib/../../ = project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

CONFIG_DIR = PROJECT_ROOT / "config" / "locus"

ALIASES: dict[str, str] = {
    "30kb": "hbb_30kb_v2.json",
    "95kb": "hbb_95kb_subTAD.json",
    "cftr": "cftr_317kb.json",
}


def resolve_locus_path(arg: str) -> Path:
    """Resolve a locus shorthand ('30kb', '95kb') or filename to a full path."""
    filename = ALIASES.get(arg, arg)
    full_path = Path(filename) if "/" in filename or "\\" in filename else CONFIG_DIR / filename

    if not full_path.exists():
        available = ", ".join(ALIASES.keys())
        raise FileNotFoundError(
            f"Locus config not found: {full_path}\n"
            f"Available aliases: {available}"
        )
    return full_path


def load_locus_config(file_path: Path) -> dict[str, Any]:
    """Load and validate a locus configuration from JSON."""
    with open(file_path) as f:
        config = json.load(f)

    w = config["window"]
    expected_bins = math.ceil((w["end"] - w["start"]) / w["resolution_bp"])
    if w["n_bins"] != expected_bins:
        raise ValueError(
            f"n_bins mismatch in {file_path}: declared {w['n_bins']}, "
            f"computed {expected_bins} from ({w['end']}-{w['start']})/{w['resolution_bp']}"
        )

    return config


def add_locus_argument(parser: ArgumentParser, default: str = "30kb") -> None:
    """Add --locus argument to an argparse parser."""
    parser.add_argument(
        "--locus",
        default=default,
        help=f"Locus config alias or filename (default: {default}). Aliases: {', '.join(ALIASES.keys())}",
    )
