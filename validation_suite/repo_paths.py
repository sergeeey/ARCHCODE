"""Resolve ARCHCODE repository paths for validation_suite."""

from __future__ import annotations

import os
from pathlib import Path

_ENV = "ARCHCODE_ROOT"


def repo_root() -> Path:
    """Parent of validation_suite/. Override with ARCHCODE_ROOT."""
    env = os.environ.get(_ENV)
    if env:
        return Path(env).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def config_locus_dir() -> Path:
    return repo_root() / "config" / "locus"


def results_dir() -> Path:
    return repo_root() / "results"


def validation_suite_dir() -> Path:
    return repo_root() / "validation_suite"


def validation_results_dir() -> Path:
    return validation_suite_dir() / "results"
