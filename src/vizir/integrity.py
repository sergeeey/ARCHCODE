"""VIZIR Integrity - Configuration hashing and run provenance tracking."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA256 hash of file.

    Args:
        file_path: Path to file

    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def compute_config_hashes(config_root: Path = Path("config")) -> dict[str, str]:
    """
    Compute hashes for all configuration files.

    Args:
        config_root: Root directory for config files

    Returns:
        Dictionary mapping file paths to hashes
    """
    hashes = {}
    config_path = Path(config_root)

    # Hash all YAML files in config/
    for config_file in config_path.rglob("*.yaml"):
        relative_path = config_file.relative_to(config_path)
        hashes[str(relative_path)] = compute_file_hash(config_file)

    return hashes


def compute_directory_hash(directory: Path) -> str:
    """
    Compute combined hash of all files in directory.

    Args:
        directory: Directory path

    Returns:
        Combined hash
    """
    if not directory.exists():
        return ""

    file_hashes = []
    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file():
            file_hashes.append(compute_file_hash(file_path))

    combined = "".join(file_hashes)
    return hashlib.sha256(combined.encode()).hexdigest()


def record_run(
    profiles: dict[str, str],
    hypotheses: dict[str, str],
    config_hash: str,
    timestamp: str | None = None,
    output_path: Path = Path(".vizir/provenance.log"),
) -> None:
    """
    Record experiment run in provenance log.

    Args:
        profiles: Dictionary mapping unknown IDs to profile names
        hypotheses: Dictionary mapping unknown IDs to hypothesis names
        config_hash: Hash of configuration files
        timestamp: Timestamp (defaults to current time)
        output_path: Path to provenance log file
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Format log entry
    entry = {
        "timestamp": timestamp,
        "profiles": profiles,
        "hypotheses": hypotheses,
        "config_hash": config_hash,
    }

    # Append to log file
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def update_integrity_ledger(
    ledger_path: Path = Path(".vizir/integrity_ledger.json"),
) -> dict[str, Any]:
    """
    Update integrity ledger with current config hashes.

    Args:
        ledger_path: Path to integrity ledger

    Returns:
        Updated ledger dictionary
    """
    # Load existing ledger or create new
    if ledger_path.exists():
        with open(ledger_path, encoding="utf-8") as f:
            ledger = json.load(f)
    else:
        ledger = {
            "version": "1.0.0-alpha",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "entries": [],
        }

    # Compute current hashes
    config_hashes = compute_config_hashes()
    data_input_hash = compute_directory_hash(Path("data/input"))

    # Update entries
    ledger["entries"] = [
        {
            "path": "config/",
            "hash": hashlib.sha256(
                json.dumps(config_hashes, sort_keys=True).encode()
            ).hexdigest(),
            "description": "All configuration files",
            "checksum_algorithm": "sha256",
            "file_hashes": config_hashes,
        },
        {
            "path": "data/input/",
            "hash": data_input_hash,
            "description": "Input genomic data",
            "checksum_algorithm": "sha256",
        },
    ]

    ledger["last_updated"] = datetime.now().isoformat()

    # Save updated ledger
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    return ledger


def verify_integrity(
    ledger_path: Path = Path(".vizir/integrity_ledger.json"),
) -> dict[str, bool]:
    """
    Verify integrity of configuration files against ledger.

    Args:
        ledger_path: Path to integrity ledger

    Returns:
        Dictionary mapping paths to verification status
    """
    if not ledger_path.exists():
        return {"error": "Ledger not found"}

    with open(ledger_path, encoding="utf-8") as f:
        ledger = json.load(f)

    verification_results = {}

    # Verify config files
    current_config_hashes = compute_config_hashes()
    ledger_config_entry = next(
        (e for e in ledger["entries"] if e["path"] == "config/"), None
    )

    if ledger_config_entry:
        ledger_file_hashes = ledger_config_entry.get("file_hashes", {})
        for file_path, current_hash in current_config_hashes.items():
            ledger_hash = ledger_file_hashes.get(file_path)
            verification_results[f"config/{file_path}"] = current_hash == ledger_hash

    # Verify data/input
    current_data_hash = compute_directory_hash(Path("data/input"))
    ledger_data_entry = next(
        (e for e in ledger["entries"] if e["path"] == "data/input/"), None
    )

    if ledger_data_entry:
        verification_results["data/input/"] = (
            current_data_hash == ledger_data_entry["hash"]
        )

    return verification_results








