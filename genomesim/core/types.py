"""
Core type definitions for GenomeSim.

This module defines the fundamental types used throughout the platform:
- SequenceScale: Hierarchical genomic scales (nucleotide → genome)
- AnalysisType: Categories of genomic analysis
- Confidence: Quantified uncertainty in predictions
- Provenance: Complete tracking of how results were obtained
- GenomicFeature: A predicted feature in the genome
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SequenceScale(Enum):
    """
    Hierarchical genomic scales.

    Genomic features exist across multiple scales, from individual nucleotides
    to complete genomes. Analysis at each scale informs the next, with
    uncertainty propagating upward.
    """

    NUCLEOTIDE = "nucleotide"  # Individual bases (A, T, G, C)
    MOTIF = "motif"  # Short patterns (6-20 bp): TFBS, splice sites
    DOMAIN = "domain"  # Functional units: protein domains, RNA structures
    GENE = "gene"  # Complete genes with regulatory elements
    OPERON = "operon"  # Gene clusters (primarily prokaryotic)
    CHROMOSOME = "chromosome"  # Full chromosomes
    GENOME = "genome"  # Complete genomes

    def __lt__(self, other: "SequenceScale") -> bool:
        """Define ordering for scale hierarchy."""
        if not isinstance(other, SequenceScale):
            return NotImplemented

        order = [
            SequenceScale.NUCLEOTIDE,
            SequenceScale.MOTIF,
            SequenceScale.DOMAIN,
            SequenceScale.GENE,
            SequenceScale.OPERON,
            SequenceScale.CHROMOSOME,
            SequenceScale.GENOME,
        ]
        return order.index(self) < order.index(other)

    def __gt__(self, other: "SequenceScale") -> bool:
        """Define ordering for scale hierarchy."""
        if not isinstance(other, SequenceScale):
            return NotImplemented
        return not self.__lt__(other) and self != other


class AnalysisType(Enum):
    """
    Categories of genomic analysis.

    Different types of analysis answer different questions about the genome:
    - STRUCTURAL: What's physically there?
    - COMPOSITIONAL: What's the makeup?
    - FUNCTIONAL: What does it do?
    - EVOLUTIONARY: How did it get here?
    - REGULATORY: How is it controlled?
    """

    STRUCTURAL = "structural"  # Physical structure: ORFs, genes, exons
    COMPOSITIONAL = "compositional"  # Sequence composition: GC content, repeats
    FUNCTIONAL = "functional"  # Biological function: protein activity, pathways
    EVOLUTIONARY = "evolutionary"  # Evolutionary history: conservation, homology
    REGULATORY = "regulatory"  # Gene regulation: promoters, enhancers, TFBSs


@dataclass
class Confidence:
    """
    Quantified uncertainty in genomic predictions.

    Every prediction in GenomeSim must include explicit confidence scores
    showing exactly which evidence supports it and where uncertainty remains.
    This "epistemic humility" is core to the platform's philosophy.

    Attributes:
        score: Confidence level between 0.0 (no confidence) and 1.0 (certain)
        method: Description of how confidence was computed
        sources: List of factors contributing to uncertainty
        supporting_evidence: Detailed breakdown of evidence supporting prediction

    Example:
        >>> conf = Confidence(
        ...     score=0.85,
        ...     method="homology-based",
        ...     sources=["blast_evalue", "percent_identity", "alignment_coverage"],
        ...     supporting_evidence={
        ...         "blast_evalue": 1e-50,
        ...         "percent_identity": 0.92,
        ...         "alignment_coverage": 0.98
        ...     }
        ... )
    """

    score: float
    method: str
    sources: List[str]
    supporting_evidence: Dict[str, Any]

    def __post_init__(self):
        """Validate confidence score is in valid range [0.0, 1.0]."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.score}")

        if not self.sources:
            raise ValueError("Confidence must have at least one source")

    def __str__(self) -> str:
        """Human-readable confidence description."""
        level = self.get_level()
        return f"Confidence: {self.score:.3f} ({level}) via {self.method}"

    def get_level(self) -> str:
        """
        Convert numeric confidence to human-readable level.

        Returns:
            String describing confidence level:
            - "Very low" (0.0 - 0.2)
            - "Low" (0.2 - 0.4)
            - "Moderate" (0.4 - 0.6)
            - "High" (0.6 - 0.8)
            - "Very high" (0.8 - 1.0)
        """
        if self.score >= 0.8:
            return "Very high"
        elif self.score >= 0.6:
            return "High"
        elif self.score >= 0.4:
            return "Moderate"
        elif self.score >= 0.2:
            return "Low"
        else:
            return "Very low"

    def combine_with(self, other: "Confidence", weight_self: float = 0.5) -> "Confidence":
        """
        Combine this confidence with another, using weighted average.

        Args:
            other: Another confidence score to combine with
            weight_self: Weight for this confidence (0.0 to 1.0)

        Returns:
            New Confidence object with combined score and merged evidence
        """
        if not 0.0 <= weight_self <= 1.0:
            raise ValueError("weight_self must be between 0.0 and 1.0")

        weight_other = 1.0 - weight_self
        combined_score = (self.score * weight_self) + (other.score * weight_other)

        # Merge sources and evidence
        combined_sources = list(set(self.sources + other.sources))
        combined_evidence = {**self.supporting_evidence, **other.supporting_evidence}

        return Confidence(
            score=combined_score,
            method=f"combined({self.method}, {other.method})",
            sources=combined_sources,
            supporting_evidence=combined_evidence,
        )


@dataclass
class Provenance:
    """
    Complete tracking of how a result was obtained.

    Every result in GenomeSim knows exactly how it was produced, enabling
    reproducibility and allowing users to understand the analysis pipeline.

    Attributes:
        analyzer: Unique identifier for the analyzer that produced this result
        version: Software version (semantic versioning)
        parameters: Analysis parameters used
        timestamp: ISO 8601 timestamp of when analysis was performed
        dependencies: List of other results that fed into this analysis
        references: Publications, databases, or resources used

    Example:
        >>> prov = Provenance(
        ...     analyzer="ORFFinder",
        ...     version="0.1.0",
        ...     parameters={"min_length": 100, "start_codons": ["ATG"]},
        ...     timestamp="2025-10-31T12:00:00Z",
        ...     dependencies=[],
        ...     references=["https://www.ncbi.nlm.nih.gov/orffinder/"]
        ... )
    """

    analyzer: str
    version: str
    parameters: Dict[str, Any]
    timestamp: str
    dependencies: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Timestamp must be in ISO 8601 format, got: {self.timestamp}")

    @staticmethod
    def create_now(
        analyzer: str,
        version: str,
        parameters: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
    ) -> "Provenance":
        """
        Create Provenance with current timestamp.

        Args:
            analyzer: Name of the analyzer
            version: Software version
            parameters: Analysis parameters
            dependencies: Optional list of dependencies
            references: Optional list of references

        Returns:
            Provenance object with current timestamp
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        return Provenance(
            analyzer=analyzer,
            version=version,
            parameters=parameters,
            timestamp=timestamp,
            dependencies=dependencies or [],
            references=references or [],
        )


@dataclass
class GenomicFeature:
    """
    A predicted feature in the genome.

    GenomicFeatures are the primary output of GenomeSim analyzers. Each feature
    represents a region of the genome with predicted properties, complete with
    confidence scores and provenance tracking.

    Attributes:
        start: 0-based start position (inclusive)
        end: 0-based end position (exclusive)
        strand: DNA strand ('+' for forward, '-' for reverse)
        feature_type: Type of feature (e.g., "gene", "promoter", "exon")
        confidence: Confidence in this prediction
        attributes: Additional feature-specific attributes
        provenance: How this feature was predicted

    Example:
        >>> feature = GenomicFeature(
        ...     start=1000,
        ...     end=2500,
        ...     strand='+',
        ...     feature_type='gene',
        ...     confidence=Confidence(0.85, "ab initio", ["orf", "homology"], {}),
        ...     attributes={'name': 'hypothetical_protein', 'reading_frame': 0},
        ...     provenance=Provenance.create_now("GeneFinder", "0.1.0", {})
        ... )
    """

    start: int
    end: int
    strand: str
    feature_type: str
    confidence: Confidence
    attributes: Dict[str, Any]
    provenance: Provenance
    sequence_id: Optional[str] = None  # Chromosome/contig identifier

    def __post_init__(self):
        """Validate feature coordinates and strand."""
        if self.start < 0:
            raise ValueError(f"Start position must be non-negative, got {self.start}")

        if self.end <= self.start:
            raise ValueError(
                f"End position must be greater than start, got start={self.start}, end={self.end}"
            )

        if self.strand not in ("+", "-"):
            raise ValueError(f"Strand must be '+' or '-', got {self.strand}")

    def length(self) -> int:
        """Return the length of this feature in base pairs."""
        return self.end - self.start

    def overlaps(self, other: "GenomicFeature") -> bool:
        """
        Check if this feature overlaps with another feature.

        Args:
            other: Another GenomicFeature to check for overlap

        Returns:
            True if features overlap, False otherwise
        """
        # Features must be on same sequence to overlap
        if self.sequence_id and other.sequence_id:
            if self.sequence_id != other.sequence_id:
                return False

        # Check coordinate overlap
        return not (self.end <= other.start or other.end <= self.start)

    def distance_to(self, other: "GenomicFeature") -> int:
        """
        Calculate distance to another feature.

        Args:
            other: Another GenomicFeature

        Returns:
            Distance in base pairs (0 if overlapping, negative if on different sequences)
        """
        # Can't compute distance if on different sequences
        if self.sequence_id and other.sequence_id:
            if self.sequence_id != other.sequence_id:
                return -1

        if self.overlaps(other):
            return 0

        # Distance is minimum gap between features
        if self.end <= other.start:
            return other.start - self.end
        else:
            return self.start - other.end

    def to_gff3(self) -> str:
        """
        Convert feature to GFF3 format line.

        Returns:
            GFF3-formatted string (without trailing newline)
        """
        seqid = self.sequence_id or "."
        source = self.provenance.analyzer
        ftype = self.feature_type
        start = self.start + 1  # GFF3 uses 1-based coordinates
        end = self.end
        score = f"{self.confidence.score:.3f}"
        strand = self.strand
        phase = "."

        # Build attributes string
        attr_parts = []
        if "id" in self.attributes:
            attr_parts.append(f"ID={self.attributes['id']}")
        if "name" in self.attributes:
            attr_parts.append(f"Name={self.attributes['name']}")

        # Add confidence details
        attr_parts.append(f"confidence={self.confidence.score:.3f}")
        attr_parts.append(f"confidence_method={self.confidence.method}")

        # Add other attributes
        for key, value in self.attributes.items():
            if key not in ("id", "name"):
                attr_parts.append(f"{key}={value}")

        attributes = ";".join(attr_parts)

        return (
            f"{seqid}\t{source}\t{ftype}\t{start}\t{end}\t{score}\t{strand}\t{phase}\t{attributes}"
        )

    def __str__(self) -> str:
        """Human-readable feature description."""
        return (
            f"{self.feature_type} at {self.sequence_id or '?'}:{self.start}-{self.end} "
            f"({self.strand}) [confidence: {self.confidence.score:.3f}]"
        )
