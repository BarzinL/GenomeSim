#!/usr/bin/env python
"""
Basic example demonstrating GenomeSim's core data types.

This example shows how to work with:
- SequenceScale and AnalysisType enums
- Confidence with explicit uncertainty quantification
- Provenance for complete tracking
- GenomicFeature as the output format
"""

from genomesim.core import (
    SequenceScale,
    AnalysisType,
    Confidence,
    Provenance,
    GenomicFeature,
)


def main():
    print("GenomeSim Basic Types Example")
    print("=" * 50)

    # 1. Working with Scales
    print("\n1. Sequence Scales:")
    print(f"   Nucleotide scale: {SequenceScale.NUCLEOTIDE.value}")
    print(f"   Gene scale: {SequenceScale.GENE.value}")
    print(f"   Nucleotide < Gene: {SequenceScale.NUCLEOTIDE < SequenceScale.GENE}")

    # 2. Analysis Types
    print("\n2. Analysis Types:")
    for atype in AnalysisType:
        print(f"   {atype.name}: {atype.value}")

    # 3. Creating Confidence
    print("\n3. Confidence with Uncertainty:")
    conf = Confidence(
        score=0.78,
        method="homology-based prediction",
        sources=["blast_evalue", "percent_identity", "alignment_coverage"],
        supporting_evidence={
            "blast_evalue": 1e-50,
            "percent_identity": 0.92,
            "alignment_coverage": 0.85,
        },
    )
    print(f"   Score: {conf.score:.2f}")
    print(f"   Level: {conf.get_level()}")
    print(f"   Method: {conf.method}")
    print(f"   Evidence:")
    for source, value in conf.supporting_evidence.items():
        print(f"     - {source}: {value}")

    # 4. Combining Confidences
    print("\n4. Combining Multiple Confidence Scores:")
    conf2 = Confidence(
        score=0.65,
        method="structural prediction",
        sources=["orf_length", "codon_bias"],
        supporting_evidence={"orf_length": 500, "codon_bias": 0.7},
    )
    combined = conf.combine_with(conf2, weight_self=0.6)
    print(f"   Conf1: {conf.score:.2f}")
    print(f"   Conf2: {conf2.score:.2f}")
    print(f"   Combined (60/40 weight): {combined.score:.2f}")

    # 5. Provenance Tracking
    print("\n5. Provenance Tracking:")
    prov = Provenance.create_now(
        analyzer="ExampleAnalyzer",
        version="0.1.0",
        parameters={"min_length": 100, "threshold": 0.5},
        dependencies=["ORFFinder", "MotifScanner"],
        references=["https://doi.org/10.1093/nar/example"],
    )
    print(f"   Analyzer: {prov.analyzer}")
    print(f"   Version: {prov.version}")
    print(f"   Timestamp: {prov.timestamp}")
    print(f"   Parameters: {prov.parameters}")
    print(f"   Dependencies: {', '.join(prov.dependencies)}")

    # 6. Creating a Genomic Feature
    print("\n6. Genomic Feature:")
    feature = GenomicFeature(
        start=1000,
        end=2500,
        strand="+",
        feature_type="gene",
        confidence=conf,
        attributes={"name": "hypothetical_protein", "id": "gene_001"},
        provenance=prov,
        sequence_id="chr1",
    )
    print(f"   {feature}")
    print(f"   Length: {feature.length()} bp")
    print(f"   Confidence: {feature.confidence.score:.2f} ({feature.confidence.get_level()})")

    # 7. GFF3 Export
    print("\n7. GFF3 Format Export:")
    gff3_line = feature.to_gff3()
    print(f"   {gff3_line}")

    # 8. Feature Comparison
    print("\n8. Feature Comparison:")
    feature2 = GenomicFeature(
        start=2400,
        end=3000,
        strand="+",
        feature_type="gene",
        confidence=conf2,
        attributes={"name": "gene_002"},
        provenance=prov,
        sequence_id="chr1",
    )
    print(f"   Feature 1: {feature.start}-{feature.end}")
    print(f"   Feature 2: {feature2.start}-{feature2.end}")
    print(f"   Overlap: {feature.overlaps(feature2)}")
    print(f"   Distance: {feature.distance_to(feature2)} bp")

    print("\n" + "=" * 50)
    print("Example complete!")


if __name__ == "__main__":
    main()
