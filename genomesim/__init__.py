"""
GenomeSim: Ab Initio Genomics Platform with Epistemic Humility

Version: 0.1.0
License: AGPLv3
Author: Barzin Lotfabadi

An open-source platform for analyzing whole genome sequences from first principles.
Every prediction includes explicit confidence scores showing exactly which evidence
supports it and where uncertainty remains.
"""

__version__ = "0.1.0"
__author__ = "Barzin Lotfabadi"
__license__ = "AGPLv3"

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
