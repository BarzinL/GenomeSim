"""
Tests for genomesim.core.interfaces module.

This module tests the abstract interfaces:
- SequenceAnalyzer
- ScaleBridge
"""

import pytest
from genomesim.core.interfaces import SequenceAnalyzer, ScaleBridge
from genomesim.core.types import (
    SequenceScale,
    AnalysisType,
    GenomicFeature,
    Confidence,
    Provenance,
)
from typing import Dict, List, Any


class SimpleTestAnalyzer(SequenceAnalyzer):
    """Minimal implementation of SequenceAnalyzer for testing."""

    def __init__(self, param1: str = "default"):
        self._param1 = param1

    @property
    def name(self) -> str:
        return "SimpleTestAnalyzer"

    @property
    def analysis_type(self) -> AnalysisType:
        return AnalysisType.COMPOSITIONAL

    @property
    def input_scale(self) -> SequenceScale:
        return SequenceScale.NUCLEOTIDE

    @property
    def output_scale(self) -> SequenceScale:
        return SequenceScale.NUCLEOTIDE

    def analyze(self, sequence: str, sequence_id: str = None, **kwargs) -> List[GenomicFeature]:
        self.validate_sequence(sequence)
        # Simple analysis: return one feature spanning entire sequence
        conf = Confidence(
            score=1.0,
            method="direct_measurement",
            sources=["sequence_length"],
            supporting_evidence={"length": len(sequence)}
        )
        prov = Provenance.create_now(
            analyzer=self.name,
            version=self.get_version(),
            parameters=self.get_parameters(),
        )
        return [
            GenomicFeature(
                start=0,
                end=len(sequence),
                strand='+',
                feature_type='test_feature',
                confidence=conf,
                attributes={'length': len(sequence)},
                provenance=prov,
                sequence_id=sequence_id,
            )
        ]

    def get_parameters(self) -> Dict[str, Any]:
        return {"param1": self._param1}


class SimpleTestBridge(ScaleBridge):
    """Minimal implementation of ScaleBridge for testing."""

    @property
    def name(self) -> str:
        return "SimpleTestBridge"

    @property
    def input_scale(self) -> SequenceScale:
        return SequenceScale.MOTIF

    @property
    def output_scale(self) -> SequenceScale:
        return SequenceScale.GENE

    def bridge(
        self,
        lower_scale_features: List[GenomicFeature],
        **kwargs
    ) -> List[GenomicFeature]:
        # Simple bridge: combine all input features into one gene
        if not lower_scale_features:
            return []

        start = min(f.start for f in lower_scale_features)
        end = max(f.end for f in lower_scale_features)

        # Aggregate confidences
        confidences = [f.confidence.score for f in lower_scale_features]
        avg_conf = self.aggregate_confidence(confidences, method="weighted_average")

        conf = Confidence(
            score=avg_conf,
            method="aggregated",
            sources=["motif_integration"],
            supporting_evidence={"num_motifs": len(lower_scale_features)}
        )

        prov = Provenance.create_now(
            analyzer=self.name,
            version="0.1.0",
            parameters={},
            dependencies=[f.provenance.analyzer for f in lower_scale_features],
        )

        return [
            GenomicFeature(
                start=start,
                end=end,
                strand='+',
                feature_type='gene',
                confidence=conf,
                attributes={},
                provenance=prov,
            )
        ]


class TestSequenceAnalyzer:
    """Tests for SequenceAnalyzer interface."""

    def test_analyzer_instantiation(self):
        """Test that we can instantiate a concrete analyzer."""
        analyzer = SimpleTestAnalyzer(param1="test")
        assert analyzer.name == "SimpleTestAnalyzer"
        assert analyzer.analysis_type == AnalysisType.COMPOSITIONAL

    def test_analyzer_properties(self):
        """Test analyzer properties."""
        analyzer = SimpleTestAnalyzer()
        assert analyzer.input_scale == SequenceScale.NUCLEOTIDE
        assert analyzer.output_scale == SequenceScale.NUCLEOTIDE
        assert analyzer.get_parameters() == {"param1": "default"}

    def test_analyzer_analyze_method(self):
        """Test analyze() method."""
        analyzer = SimpleTestAnalyzer()
        sequence = "ATGCGATCGATCG"
        features = analyzer.analyze(sequence)

        assert len(features) == 1
        assert features[0].start == 0
        assert features[0].end == len(sequence)
        assert features[0].feature_type == 'test_feature'

    def test_analyzer_validate_sequence(self):
        """Test sequence validation."""
        analyzer = SimpleTestAnalyzer()

        # Valid sequences
        analyzer.validate_sequence("ATGC")
        analyzer.validate_sequence("atgc")
        analyzer.validate_sequence("ATGCN")  # N is valid (unknown base)

        # Invalid sequence
        with pytest.raises(ValueError, match="invalid characters"):
            analyzer.validate_sequence("ATGCXYZ")

    def test_analyzer_get_version(self):
        """Test get_version() method."""
        analyzer = SimpleTestAnalyzer()
        version = analyzer.get_version()
        assert isinstance(version, str)
        assert version == "0.1.0"  # From genomesim.__version__

    def test_analyzer_string_representation(self):
        """Test __str__ method."""
        analyzer = SimpleTestAnalyzer()
        s = str(analyzer)
        assert "SimpleTestAnalyzer" in s
        assert "compositional" in s
        assert "nucleotide" in s

    def test_analyzer_cannot_instantiate_abstract(self):
        """Test that we cannot instantiate the abstract base class."""
        with pytest.raises(TypeError):
            SequenceAnalyzer()


class TestScaleBridge:
    """Tests for ScaleBridge interface."""

    def test_bridge_instantiation(self):
        """Test that we can instantiate a concrete bridge."""
        bridge = SimpleTestBridge()
        assert bridge.name == "SimpleTestBridge"
        assert bridge.input_scale == SequenceScale.MOTIF
        assert bridge.output_scale == SequenceScale.GENE

    def test_bridge_method(self):
        """Test bridge() method."""
        bridge = SimpleTestBridge()

        # Create sample motif features
        conf = Confidence(0.8, "test", ["src"], {})
        prov = Provenance.create_now("TestAnalyzer", "1.0", {})

        motifs = [
            GenomicFeature(100, 120, '+', 'motif', conf, {}, prov),
            GenomicFeature(500, 520, '+', 'motif', conf, {}, prov),
            GenomicFeature(800, 820, '+', 'motif', conf, {}, prov),
        ]

        genes = bridge.bridge(motifs)
        assert len(genes) == 1
        assert genes[0].start == 100
        assert genes[0].end == 820
        assert genes[0].feature_type == 'gene'

    def test_bridge_aggregate_confidence_weighted_average(self):
        """Test aggregate_confidence() with weighted average."""
        bridge = SimpleTestBridge()

        confidences = [0.8, 0.6, 0.9]
        result = bridge.aggregate_confidence(confidences, method="weighted_average")
        assert result == pytest.approx(0.7667, abs=0.001)

        # With custom weights
        result = bridge.aggregate_confidence(
            confidences,
            method="weighted_average",
            weights=[2.0, 1.0, 1.0]
        )
        expected = (0.8 * 2.0 + 0.6 * 1.0 + 0.9 * 1.0) / 4.0
        assert result == pytest.approx(expected)

    def test_bridge_aggregate_confidence_minimum(self):
        """Test aggregate_confidence() with minimum."""
        bridge = SimpleTestBridge()

        confidences = [0.8, 0.6, 0.9]
        result = bridge.aggregate_confidence(confidences, method="minimum")
        assert result == 0.6

    def test_bridge_aggregate_confidence_geometric_mean(self):
        """Test aggregate_confidence() with geometric mean."""
        bridge = SimpleTestBridge()

        confidences = [0.8, 0.5, 0.9]
        result = bridge.aggregate_confidence(confidences, method="geometric_mean")
        expected = (0.8 * 0.5 * 0.9) ** (1/3)
        assert result == pytest.approx(expected)

    def test_bridge_aggregate_confidence_empty(self):
        """Test aggregate_confidence() with empty list."""
        bridge = SimpleTestBridge()
        result = bridge.aggregate_confidence([], method="weighted_average")
        assert result == 0.0

    def test_bridge_aggregate_confidence_invalid_method(self):
        """Test aggregate_confidence() with invalid method."""
        bridge = SimpleTestBridge()
        with pytest.raises(ValueError, match="Unknown aggregation method"):
            bridge.aggregate_confidence([0.8], method="invalid")

    def test_bridge_aggregate_confidence_weight_mismatch(self):
        """Test aggregate_confidence() with mismatched weights."""
        bridge = SimpleTestBridge()
        with pytest.raises(ValueError, match="Weights length"):
            bridge.aggregate_confidence(
                [0.8, 0.6],
                method="weighted_average",
                weights=[1.0, 1.0, 1.0]  # Wrong length
            )

    def test_bridge_string_representation(self):
        """Test __str__ method."""
        bridge = SimpleTestBridge()
        s = str(bridge)
        assert "SimpleTestBridge" in s
        assert "motif" in s
        assert "gene" in s

    def test_bridge_cannot_instantiate_abstract(self):
        """Test that we cannot instantiate the abstract base class."""
        with pytest.raises(TypeError):
            ScaleBridge()


class TestAnalyzerIntegration:
    """Integration tests for analyzers and bridges."""

    def test_analyzer_to_bridge_workflow(self):
        """Test typical workflow: analyzer → bridge."""
        # Step 1: Run analyzer
        analyzer = SimpleTestAnalyzer()
        sequence = "ATGCGATCGATCGATCGATCG"
        features = analyzer.analyze(sequence, sequence_id="test_seq")

        assert len(features) == 1
        assert features[0].sequence_id == "test_seq"

        # Step 2: Use bridge (simulated - our test bridge expects motifs)
        # In real use, you'd have a motif-finding analyzer first
        bridge = SimpleTestBridge()

        # Convert features to "motifs" for testing
        motif_features = [
            GenomicFeature(
                start=f.start,
                end=f.end,
                strand=f.strand,
                feature_type='motif',  # Change type
                confidence=f.confidence,
                attributes=f.attributes,
                provenance=f.provenance,
                sequence_id=f.sequence_id,
            )
            for f in features
        ]

        genes = bridge.bridge(motif_features)
        assert len(genes) == 1
        assert genes[0].feature_type == 'gene'

        # Check provenance tracking
        assert analyzer.name in genes[0].provenance.dependencies
