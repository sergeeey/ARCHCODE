"""
Bio-Metrics Engine for real Hi-C data analysis.

Provides functions for computing key bioinformatics metrics:
- Insulation Score
- TAD calling
- Compartment analysis
- P(s) curve
- Pearson correlation matrix
- Aggregate Peak Analysis (APA)
"""

from archcode_bio.analysis.insulation import compute_insulation
from archcode_bio.analysis.tad_calls import call_tads
from archcode_bio.analysis.compartments import compute_compartments
from archcode_bio.analysis.ps_curve import compute_ps_curve
from archcode_bio.analysis.pearson import compute_pearson_matrix
from archcode_bio.analysis.apa import compute_apa

__all__ = [
    "compute_insulation",
    "call_tads",
    "compute_compartments",
    "compute_ps_curve",
    "compute_pearson_matrix",
    "compute_apa",
]


