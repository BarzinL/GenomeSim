"""
Tests for genomesim.core.types module.

This module tests all core data types including:
- SequenceScale enum
- AnalysisType enum
- Confidence dataclass
- Provenance dataclass
- GenomicFeature dataclass
"""

from datetime import datetime

import pytest

from genomesim.core.types import (
    AnalysisType,
    Confidence,
    GenomicFeature,
    Provenance,
    SequenceScale,
)


class TestSequenceScale:
    """Tests for SequenceScale enum."""

    def test_all_scales_defined(self):
        """Test that all expected scales are defined."""
        expected = {"NUCLEOTIDE", "MOTIF", "DOMAIN", "GENE", "OPERON", "CHROMOSOME", "GENOME"}
        actual = {scale.name for scale in SequenceScale}
        assert actual == expected

    def test_scale_ordering(self):
        """Test that scales are correctly ordered."""
        assert SequenceScale.NUCLEOTIDE < SequenceScale.MOTIF
        assert SequenceScale.MOTIF < SequenceScale.DOMAIN
        assert SequenceScale.DOMAIN < SequenceScale.GENE
        assert SequenceScale.GENE < SequenceScale.OPERON
        assert SequenceScale.OPERON < SequenceScale.CHROMOSOME
        assert SequenceScale.CHROMOSOME < SequenceScale.GENOME

    def test_scale_greater_than(self):
        """Test greater than comparison."""
        assert SequenceScale.GENOME > SequenceScale.NUCLEOTIDE
        assert SequenceScale.GENE > SequenceScale.MOTIF


class TestAnalysisType:
    """Tests for AnalysisType enum."""

    def test_all_types_defined(self):
        """Test that all expected analysis types are defined."""
        expected = {"STRUCTURAL", "COMPOSITIONAL", "FUNCTIONAL", "EVOLUTIONARY", "REGULATORY"}
        actual = {atype.name for atype in AnalysisType}
        assert actual == expected

    def test_type_values(self):
        """Test that enum values are lowercase."""
        for atype in AnalysisType:
            assert atype.value == atype.name.lower()


class TestConfidence:
    """Tests for Confidence dataclass."""

    def test_valid_confidence_creation(self):
        """Test creating a valid Confidence object."""
        conf = Confidence(
            score=0.75, method="test", sources=["source1"], supporting_evidence={"source1": 0.75}
        )
        assert conf.score == 0.75
        assert conf.method == "test"
        assert conf.sources == ["source1"]

    def test_confidence_score_bounds(self):
        """Test that confidence score must be between 0 and 1."""
        # Valid bounds
        Confidence(0.0, "test", ["s"], {})
        Confidence(1.0, "test", ["s"], {})

        # Invalid bounds
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            Confidence(-0.1, "test", ["s"], {})

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            Confidence(1.1, "test", ["s"], {})

    def test_confidence_requires_sources(self):
        """Test that confidence must have at least one source."""
        with pytest.raises(ValueError, match="at least one source"):
            Confidence(0.5, "test", [], {})

    def test_confidence_levels(self):
        """Test get_level() method."""
        assert Confidence(0.9, "test", ["s"], {}).get_level() == "Very high"
        assert Confidence(0.7, "test", ["s"], {}).get_level() == "High"
        assert Confidence(0.5, "test", ["s"], {}).get_level() == "Moderate"
        assert Confidence(0.3, "test", ["s"], {}).get_level() == "Low"
        assert Confidence(0.1, "test", ["s"], {}).get_level() == "Very low"

    def test_confidence_string_representation(self):
        """Test __str__ method."""
        conf = Confidence(0.75, "homology", ["blast"], {})
        s = str(conf)
        assert "0.75" in s or "0.750" in s
        assert "High" in s
        assert "homology" in s

    def test_confidence_combination(self):
        """Test combine_with() method."""
        conf1 = Confidence(0.8, "method1", ["s1"], {"s1": 1})
        conf2 = Confidence(0.6, "method2", ["s2"], {"s2": 2})

        # Equal weights
        combined = conf1.combine_with(conf2, weight_self=0.5)
        assert combined.score == 0.7  # (0.8 + 0.6) / 2

        # Different weights
        combined = conf1.combine_with(conf2, weight_self=0.75)
        assert combined.score == pytest.approx(0.75)  # 0.8 * 0.75 + 0.6 * 0.25

        # Combined sources
        assert set(combined.sources) == {"s1", "s2"}

        # Combined evidence
        assert combined.supporting_evidence == {"s1": 1, "s2": 2}

    def test_confidence_combination_invalid_weight(self):
        """Test that invalid weights raise error."""
        conf1 = Confidence(0.8, "m1", ["s"], {})
        conf2 = Confidence(0.6, "m2", ["s"], {})

        with pytest.raises(ValueError, match="weight_self must be between"):
            conf1.combine_with(conf2, weight_self=1.5)


class TestProvenance:
    """Tests for Provenance dataclass."""

    def test_valid_provenance_creation(self):
        """Test creating a valid Provenance object."""
        prov = Provenance(
            analyzer="TestAnalyzer",
            version="1.0.0",
            parameters={"param": "value"},
            timestamp="2025-10-31T12:00:00Z",
        )
        assert prov.analyzer == "TestAnalyzer"
        assert prov.version == "1.0.0"
        assert prov.parameters == {"param": "value"}

    def test_provenance_timestamp_validation(self):
        """Test that timestamp must be ISO 8601 format."""
        # Valid formats
        Provenance("test", "1.0", {}, "2025-10-31T12:00:00Z")
        Provenance("test", "1.0", {}, "2025-10-31T12:00:00+00:00")

        # Invalid format
        with pytest.raises(ValueError, match="ISO 8601 format"):
            Provenance("test", "1.0", {}, "2025/10/31 12:00")

    def test_provenance_create_now(self):
        """Test create_now() factory method."""
        from datetime import timezone

        before = datetime.now(timezone.utc)
        prov = Provenance.create_now(
            analyzer="TestAnalyzer",
            version="1.0.0",
            parameters={"test": True},
        )
        after = datetime.now(timezone.utc)

        # Parse timestamp
        ts = datetime.fromisoformat(prov.timestamp.replace("Z", "+00:00"))

        # Should be created between before and after
        assert before <= ts <= after
        assert prov.analyzer == "TestAnalyzer"

    def test_provenance_with_dependencies(self):
        """Test provenance with dependencies."""
        prov = Provenance.create_now(
            analyzer="IntegrationAnalyzer",
            version="1.0.0",
            parameters={},
            dependencies=["ORFFinder", "MotifScanner"],
        )
        assert prov.dependencies == ["ORFFinder", "MotifScanner"]

    def test_provenance_with_references(self):
        """Test provenance with references."""
        prov = Provenance.create_now(
            analyzer="HomologySearch",
            version="1.0.0",
            parameters={},
            references=["https://www.ncbi.nlm.nih.gov/"],
        )
        assert prov.references == ["https://www.ncbi.nlm.nih.gov/"]


class TestGenomicFeature:
    """Tests for GenomicFeature dataclass."""

    def test_valid_feature_creation(self, sample_confidence, sample_provenance):
        """Test creating a valid GenomicFeature."""
        feature = GenomicFeature(
            start=100,
            end=200,
            strand="+",
            feature_type="gene",
            confidence=sample_confidence,
            attributes={},
            provenance=sample_provenance,
        )
        assert feature.start == 100
        assert feature.end == 200
        assert feature.strand == "+"

    def test_feature_coordinate_validation(self, sample_confidence, sample_provenance):
        """Test that feature coordinates are validated."""
        # Start must be non-negative
        with pytest.raises(ValueError, match="non-negative"):
            GenomicFeature(-1, 100, "+", "gene", sample_confidence, {}, sample_provenance)

        # End must be greater than start
        with pytest.raises(ValueError, match="greater than start"):
            GenomicFeature(100, 100, "+", "gene", sample_confidence, {}, sample_provenance)

        with pytest.raises(ValueError, match="greater than start"):
            GenomicFeature(100, 50, "+", "gene", sample_confidence, {}, sample_provenance)

    def test_feature_strand_validation(self, sample_confidence, sample_provenance):
        """Test that strand must be + or -."""
        # Valid strands
        GenomicFeature(0, 100, "+", "gene", sample_confidence, {}, sample_provenance)
        GenomicFeature(0, 100, "-", "gene", sample_confidence, {}, sample_provenance)

        # Invalid strand
        with pytest.raises(ValueError, match="Strand must be"):
            GenomicFeature(0, 100, "?", "gene", sample_confidence, {}, sample_provenance)

    def test_feature_length(self, sample_feature):
        """Test length() method."""
        assert sample_feature.length() == 1000  # 2000 - 1000

    def test_feature_overlaps(self, sample_confidence, sample_provenance):
        """Test overlaps() method."""
        feature1 = GenomicFeature(
            100, 200, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )
        feature2 = GenomicFeature(
            150, 250, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )
        feature3 = GenomicFeature(
            250, 350, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )
        feature4 = GenomicFeature(
            100, 200, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr2"
        )

        # Overlapping features
        assert feature1.overlaps(feature2)
        assert feature2.overlaps(feature1)

        # Non-overlapping features
        assert not feature1.overlaps(feature3)
        assert not feature3.overlaps(feature1)

        # Different chromosomes
        assert not feature1.overlaps(feature4)

    def test_feature_distance(self, sample_confidence, sample_provenance):
        """Test distance_to() method."""
        feature1 = GenomicFeature(
            100, 200, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )
        feature2 = GenomicFeature(
            150, 250, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )
        feature3 = GenomicFeature(
            300, 400, "+", "gene", sample_confidence, {}, sample_provenance, sequence_id="chr1"
        )

        # Overlapping = distance 0
        assert feature1.distance_to(feature2) == 0

        # Gap of 100 bp
        assert feature1.distance_to(feature3) == 100
        assert feature3.distance_to(feature1) == 100

    def test_feature_to_gff3(self, sample_feature):
        """Test to_gff3() method."""
        gff3 = sample_feature.to_gff3()

        # Should be tab-separated with 9 fields
        fields = gff3.split("\t")
        assert len(fields) == 9

        # Check key fields
        assert fields[0] == "chr1"  # seqid
        assert fields[2] == "gene"  # type
        assert fields[3] == "1001"  # start (1-based)
        assert fields[4] == "2000"  # end
        assert fields[6] == "+"  # strand

        # Check attributes field contains confidence
        assert "confidence=" in fields[8]

    def test_feature_string_representation(self, sample_feature):
        """Test __str__ method."""
        s = str(sample_feature)
        assert "gene" in s
        assert "chr1" in s
        assert "1000" in s
        assert "2000" in s
        assert "+" in s
