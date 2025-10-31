"""
Core types and interfaces for GenomeSim.

This module contains the fundamental building blocks for genomic analysis:
- Type definitions (scales, analysis types)
- Data structures (confidence, provenance, features)
- Abstract interfaces (analyzers, scale bridges)
"""

from genomesim.core.interfaces import (
    ScaleBridge,
    SequenceAnalyzer,
)
from genomesim.core.types import (
    AnalysisType,
    Confidence,
    GenomicFeature,
    Provenance,
    SequenceScale,
)

__all__ = [
    "SequenceScale",
    "AnalysisType",
    "Confidence",
    "Provenance",
    "GenomicFeature",
    "SequenceAnalyzer",
    "ScaleBridge",
]
