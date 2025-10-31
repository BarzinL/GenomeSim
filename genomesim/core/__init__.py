"""
Core types and interfaces for GenomeSim.

This module contains the fundamental building blocks for genomic analysis:
- Type definitions (scales, analysis types)
- Data structures (confidence, provenance, features)
- Abstract interfaces (analyzers, scale bridges)
"""

from genomesim.core.types import (
    SequenceScale,
    AnalysisType,
    Confidence,
    Provenance,
    GenomicFeature,
)
from genomesim.core.interfaces import (
    SequenceAnalyzer,
    ScaleBridge,
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
