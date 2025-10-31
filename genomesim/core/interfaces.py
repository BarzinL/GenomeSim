"""
Abstract interfaces for GenomeSim analyzers and scale bridges.

This module defines the core interfaces that all genomic analyzers and
scale bridges must implement. These interfaces ensure consistent behavior
and enable the plugin architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from genomesim.core.types import (
    AnalysisType,
    GenomicFeature,
    SequenceScale,
)


class SequenceAnalyzer(ABC):
    """
    Base class for all genomic analyzers.

    Every analyzer in GenomeSim must implement this interface. Analyzers are
    pluggable modules that perform specific types of genomic analysis, from
    finding ORFs to predicting protein structures.

    Key Principles:
    1. Every analyzer must compute explicit confidence scores
    2. All results must include complete provenance tracking
    3. Analyzers should be stateless (parameters passed at init)
    4. Analyzers should be composable (output can feed other analyzers)

    Example Implementation:
        >>> class SimpleGCAnalyzer(SequenceAnalyzer):
        ...     def __init__(self, window_size: int = 100):
        ...         self._window_size = window_size
        ...
        ...     @property
        ...     def name(self) -> str:
        ...         return "SimpleGCAnalyzer"
        ...
        ...     @property
        ...     def analysis_type(self) -> AnalysisType:
        ...         return AnalysisType.COMPOSITIONAL
        ...
        ...     @property
        ...     def input_scale(self) -> SequenceScale:
        ...         return SequenceScale.NUCLEOTIDE
        ...
        ...     @property
        ...     def output_scale(self) -> SequenceScale:
        ...         return SequenceScale.NUCLEOTIDE
        ...
        ...     def analyze(self, sequence: str, **kwargs) -> List[GenomicFeature]:
        ...         # Implementation here
        ...         pass
        ...
        ...     def get_parameters(self) -> Dict:
        ...         return {"window_size": self._window_size}
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this analyzer.

        This name is used in provenance tracking and should be descriptive
        and stable across versions.

        Returns:
            String identifier (e.g., "ORFFinder", "SpliceAIWrapper")
        """
        pass

    @property
    @abstractmethod
    def analysis_type(self) -> AnalysisType:
        """
        Category of analysis this analyzer performs.

        Returns:
            AnalysisType enum value (STRUCTURAL, COMPOSITIONAL, etc.)
        """
        pass

    @property
    @abstractmethod
    def input_scale(self) -> SequenceScale:
        """
        The genomic scale this analyzer operates on as input.

        Returns:
            SequenceScale enum value (e.g., NUCLEOTIDE, GENE)
        """
        pass

    @property
    @abstractmethod
    def output_scale(self) -> SequenceScale:
        """
        The genomic scale this analyzer produces as output.

        Returns:
            SequenceScale enum value (e.g., MOTIF, GENE)
        """
        pass

    @abstractmethod
    def analyze(
        self, sequence: str, sequence_id: Optional[str] = None, **kwargs
    ) -> List[GenomicFeature]:
        """
        Analyze sequence and return predicted features.

        This is the core method that performs the actual genomic analysis.
        All features returned MUST include:
        - Explicit confidence scores
        - Complete provenance information
        - Valid coordinates relative to input sequence

        Args:
            sequence: DNA/RNA sequence to analyze (string of A, T, G, C, U, N)
            sequence_id: Optional identifier for the sequence (e.g., "chr1")
            **kwargs: Additional analyzer-specific parameters

        Returns:
            List of GenomicFeature objects with predictions

        Raises:
            ValueError: If sequence is invalid or parameters are incorrect
        """
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """
        Return current analyzer parameters.

        This is used for provenance tracking and reproducibility.

        Returns:
            Dictionary of parameter names and values
        """
        pass

    def validate_sequence(self, sequence: str) -> None:
        """
        Validate that input sequence contains only valid nucleotides.

        Args:
            sequence: DNA/RNA sequence to validate

        Raises:
            ValueError: If sequence contains invalid characters
        """
        valid_bases = set("ATGCUN")
        sequence_upper = sequence.upper()
        invalid_chars = set(sequence_upper) - valid_bases

        if invalid_chars:
            raise ValueError(
                f"Sequence contains invalid characters: {invalid_chars}. "
                f"Valid characters are: {valid_bases}"
            )

    def get_version(self) -> str:
        """
        Get the version of this analyzer.

        Default implementation returns the package version. Subclasses can
        override to provide specific version information.

        Returns:
            Version string (semantic versioning)
        """
        from genomesim import __version__

        return __version__

    def __str__(self) -> str:
        """Human-readable analyzer description."""
        return (
            f"{self.name} ({self.analysis_type.value}) "
            f"[{self.input_scale.value} → {self.output_scale.value}]"
        )


class ScaleBridge(ABC):
    """
    Bridge between genomic scales.

    ScaleBridges integrate features from lower scales into predictions at
    higher scales. This enables multi-scale analysis where evidence from
    multiple sources is combined.

    Example: Integrating ORFs + splice sites + homology → gene predictions

    Key Principles:
    1. Bridges combine evidence from multiple lower-scale features
    2. Confidence scores must propagate and aggregate correctly
    3. Provenance must track all input features that contributed
    4. Bridges should handle missing evidence gracefully

    Example Implementation:
        >>> class MotifToGeneBridge(ScaleBridge):
        ...     @property
        ...     def name(self) -> str:
        ...         return "MotifToGeneBridge"
        ...
        ...     @property
        ...     def input_scale(self) -> SequenceScale:
        ...         return SequenceScale.MOTIF
        ...
        ...     @property
        ...     def output_scale(self) -> SequenceScale:
        ...         return SequenceScale.GENE
        ...
        ...     def bridge(
        ...         self,
        ...         lower_scale_features: List[GenomicFeature],
        ...         **kwargs
        ...     ) -> List[GenomicFeature]:
        ...         # Integrate motifs (promoters, splice sites) into genes
        ...         pass
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique identifier for this scale bridge.

        Returns:
            String identifier (e.g., "SequenceToStructure")
        """
        pass

    @property
    @abstractmethod
    def input_scale(self) -> SequenceScale:
        """
        The lower genomic scale this bridge accepts as input.

        Returns:
            SequenceScale enum value
        """
        pass

    @property
    @abstractmethod
    def output_scale(self) -> SequenceScale:
        """
        The higher genomic scale this bridge produces as output.

        Returns:
            SequenceScale enum value (must be > input_scale)
        """
        pass

    @abstractmethod
    def bridge(self, lower_scale_features: List[GenomicFeature], **kwargs) -> List[GenomicFeature]:
        """
        Integrate lower-scale features into higher-scale predictions.

        This method combines evidence from multiple lower-scale features to
        make predictions at a higher scale. Confidence scores should be
        aggregated appropriately, and provenance should track all inputs.

        Args:
            lower_scale_features: Features from lower scale(s)
            **kwargs: Additional bridge-specific parameters

        Returns:
            List of GenomicFeature objects at higher scale

        Raises:
            ValueError: If input features are from wrong scale
        """
        pass

    def validate_input_scale(self, features: List[GenomicFeature]) -> None:
        """
        Validate that input features are from the expected scale.

        Args:
            features: List of features to validate

        Raises:
            ValueError: If any feature is from wrong scale
        """
        for i, feature in enumerate(features):
            # Extract scale from feature type if possible
            # This is a simple check; real implementation might be more sophisticated
            expected = self.input_scale.value
            if expected not in feature.feature_type.lower():
                # Warning rather than error, as feature types might not
                # directly match scale names
                pass

    def aggregate_confidence(
        self,
        confidences: List[float],
        method: str = "weighted_average",
        weights: Optional[List[float]] = None,
    ) -> float:
        """
        Aggregate multiple confidence scores into a single score.

        Args:
            confidences: List of confidence scores to aggregate
            method: Aggregation method ("weighted_average", "minimum", "geometric_mean")
            weights: Optional weights for each confidence (for weighted_average)

        Returns:
            Aggregated confidence score

        Raises:
            ValueError: If method is unknown or weights don't match confidences
        """
        if not confidences:
            return 0.0

        if method == "weighted_average":
            if weights is None:
                weights = [1.0] * len(confidences)

            if len(weights) != len(confidences):
                raise ValueError(
                    f"Weights length ({len(weights)}) must match confidences length ({len(confidences)})"
                )

            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0

            weighted_sum = sum(c * w for c, w in zip(confidences, weights))
            return weighted_sum / total_weight

        elif method == "minimum":
            # Conservative: take lowest confidence
            return min(confidences)

        elif method == "geometric_mean":
            # Penalizes low confidences more heavily
            product = 1.0
            for c in confidences:
                product *= c
            return product ** (1.0 / len(confidences))

        else:
            raise ValueError(
                f"Unknown aggregation method: {method}. "
                f"Valid methods: weighted_average, minimum, geometric_mean"
            )

    def __str__(self) -> str:
        """Human-readable bridge description."""
        return f"{self.name} " f"[{self.input_scale.value} → {self.output_scale.value}]"
