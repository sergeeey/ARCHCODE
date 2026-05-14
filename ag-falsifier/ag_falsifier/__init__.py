"""ag-falsifier: Falsification-First Validation for AlphaGenome Predictions

Prevents validation theater via automatic statistical controls.
"""

from .validator import AlphaGenomeValidator, ValidationResult

__version__ = "0.1.0-alpha"
__all__ = ["AlphaGenomeValidator", "ValidationResult"]
