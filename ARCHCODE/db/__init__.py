"""
ARCHCODE Annotation Database

Pattern: annotate once → store in SQLite → query fast
Inspired by genechat-mcp.
"""

from .query import ARCHCODEDatabase, init_database, Variant, LocusSummary, ValidationResult

__all__ = [
    "ARCHCODEDatabase",
    "init_database",
    "Variant",
    "LocusSummary",
    "ValidationResult",
]
