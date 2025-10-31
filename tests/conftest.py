"""
Pytest configuration and shared fixtures.

This module provides common fixtures used across the test suite.
"""

import pytest

from genomesim.core.types import Confidence, GenomicFeature, Provenance


@pytest.fixture
def sample_confidence():
    """Fixture providing a sample Confidence object."""
    return Confidence(
        score=0.85,
        method="test_method",
        sources=["test_source_1", "test_source_2"],
        supporting_evidence={
            "test_source_1": 0.9,
            "test_source_2": 0.8,
        },
    )


@pytest.fixture
def sample_provenance():
    """Fixture providing a sample Provenance object."""
    return Provenance(
        analyzer="TestAnalyzer",
        version="0.1.0",
        parameters={"param1": "value1", "param2": 42},
        timestamp="2025-10-31T12:00:00Z",
        dependencies=["dep1", "dep2"],
        references=["http://example.com/ref1"],
    )


@pytest.fixture
def sample_feature(sample_confidence, sample_provenance):
    """Fixture providing a sample GenomicFeature object."""
    return GenomicFeature(
        start=1000,
        end=2000,
        strand="+",
        feature_type="gene",
        confidence=sample_confidence,
        attributes={"name": "test_gene", "id": "gene_001"},
        provenance=sample_provenance,
        sequence_id="chr1",
    )


@pytest.fixture
def sample_sequence():
    """Fixture providing a sample DNA sequence."""
    return "ATGCGATCGATCGATCGATCGATCGATCGATCG"


@pytest.fixture
def sample_protein_coding_sequence():
    """Fixture providing a sample protein-coding sequence with ORF."""
    # ATG (start) ... TAA (stop)
    return (
        "ATGGCATCGATCGATCGATCGATCGATCGATCG"
        "ATCGATCGATCGATCGATCGATCGATCGATCGA"
        "TCGATCGATCGATCGATCGATAA"
    )
