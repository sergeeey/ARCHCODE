"""
Validation Theater Detector

Автоматическая детекция synthetic data marked as [VERIFIED] —
предотвращает validation theater (circular logic in testing).

Основные паттерны:
- Synthetic data markers (np.random, mock_*, create_synthetic_*)
- Round perfect metrics (F1=1.000, precision=1.0, 100% success)
- Zero failures (all tests pass, no edge cases)
- Inline synthetic (embedded test cases in validation code)

Author: Sergey Boyko (ARCHCODE Project)
Date: 2026-05-14
License: MIT
"""

__version__ = "0.1.0"
__author__ = "Sergey Boyko"

from .detector import ValidationTheaterDetector, check_file, check_directory

__all__ = [
    "ValidationTheaterDetector",
    "check_file",
    "check_directory",
]
