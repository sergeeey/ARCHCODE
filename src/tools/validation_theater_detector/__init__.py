"""Validation Theater Detector — автоматическая детекция synthetic data marked as [VERIFIED].

Предотвращает validation theater: когда synthetic/mock данные выдаются за реальную валидацию.

Key patterns detected:
- Synthetic data markers (np.random.seed, mock_*, create_synthetic_*)
- Embedded test cases (inline data without external API/file source)
- Round perfect metrics (F1=1.000, precision=1.0, 100% success)
- Zero failures across 5+ independent tests

Based on: ТОП-10 postmortem (May 2026), ARCHCODE falsification lessons.

Example:
    from validation_theater_detector import detect_theater

    findings = detect_theater('src/', recursive=True)
    for finding in findings:
        if finding.severity == 'HIGH':
            print(f"⚠️  {finding.file}:{finding.line} — {finding.message}")
"""

__version__ = "0.1.0"
__author__ = "Sergey Kuchinsky"

from .core import (
    detect_theater,
    TheaterFinding,
    Severity,
)

__all__ = [
    "detect_theater",
    "TheaterFinding",
    "Severity",
]
