# Core Concepts

**Tags**: #core #tutorial #concepts

This guide explains the fundamental concepts and type system that power GenomeSim.

## The Three Pillars

### 1. Epistemic Humility 🎯

**Principle**: We don't know everything, and we should be honest about it.

Every prediction in GenomeSim includes explicit confidence scores:

```python
confidence = Confidence(
    score=0.78,  # 78% confident
    method="homology-based",
    sources=["blast_evalue", "percent_identity", "alignment_coverage"],
    supporting_evidence={
        "blast_evalue": 1e-50,
        "percent_identity": 0.92,
        "alignment_coverage": 0.85
    }
)
```

**Why this matters**: Traditional tools often present predictions without uncertainty. A gene "predicted" with 0.3 confidence looks the same as one with 0.99 confidence. This leads to:
- False confidence in unreliable predictions
- Wasted experimental validation on low-confidence hits
- Bias when tools are trained on incomplete data

### 2. Provenance Tracking 📝

**Principle**: Every result should know exactly how it was obtained.

```python
provenance = Provenance(
    analyzer="ORFFinder",
    version="0.1.0",
    parameters={"min_length": 100, "start_codons": ["ATG"]},
    timestamp="2025-10-31T12:00:00Z",
    dependencies=[],
    references=["https://www.ncbi.nlm.nih.gov/orffinder/"]
)
```

**Why this matters**: Scientific reproducibility requires complete documentation of methods. Provenance enables:
- Exact reproduction of results
- Understanding what influenced predictions
- Tracking data lineage
- Identifying outdated analyses

### 3. Multi-Scale Integration 🔗

**Principle**: Biology operates across multiple scales simultaneously.

```
Nucleotide: ATGCGATCG... (base pairs)
    ↓
Motif: TATAAA (TATA box)
    ↓
Domain: DNA-binding domain
    ↓
Gene: Complete transcription unit
    ↓
Operon: Co-regulated genes
    ↓
Pathway: Metabolic pathway
    ↓
Phenotype: Observable trait
```

Evidence at each scale informs higher scales, with uncertainty propagating upward.

## Core Types

### SequenceScale

Represents the hierarchical levels of genomic organization:

```python
from genomesim.core import SequenceScale

# Individual bases
SequenceScale.NUCLEOTIDE

# Short patterns (TFBS, splice sites)
SequenceScale.MOTIF

# Functional units (protein domains)
SequenceScale.DOMAIN

# Complete genes
SequenceScale.GENE

# Gene clusters (primarily prokaryotic)
SequenceScale.OPERON

# Full chromosomes
SequenceScale.CHROMOSOME

# Complete genomes
SequenceScale.GENOME
```

**Scale comparison**:
```python
SequenceScale.NUCLEOTIDE < SequenceScale.GENE  # True
SequenceScale.GENOME > SequenceScale.MOTIF     # True
```

### AnalysisType

Categorizes different types of genomic analysis:

```python
from genomesim.core import AnalysisType

# What's physically there?
AnalysisType.STRUCTURAL  # ORFs, genes, exons

# What's the makeup?
AnalysisType.COMPOSITIONAL  # GC content, repeats

# What does it do?
AnalysisType.FUNCTIONAL  # Protein activity, pathways

# How did it get here?
AnalysisType.EVOLUTIONARY  # Conservation, homology

# How is it controlled?
AnalysisType.REGULATORY  # Promoters, enhancers
```

### Confidence

Quantifies uncertainty in predictions:

```python
from genomesim.core import Confidence

conf = Confidence(
    score=0.85,           # Must be 0.0 to 1.0
    method="ab initio",   # How computed
    sources=["orf", "codon_bias"],  # Contributing factors
    supporting_evidence={
        "orf": {"length": 500, "score": 0.9},
        "codon_bias": {"cai": 0.8}
    }
)

# Human-readable level
print(conf.get_level())  # "Very high"

# Combine confidences
other_conf = Confidence(0.75, "homology", ["blast"], {})
combined = conf.combine_with(other_conf, weight_self=0.5)
print(combined.score)  # 0.80 (average)
```

**Confidence levels**:
- 0.8 - 1.0: Very high
- 0.6 - 0.8: High
- 0.4 - 0.6: Moderate
- 0.2 - 0.4: Low
- 0.0 - 0.2: Very low

### Provenance

Tracks how results were obtained:

```python
from genomesim.core import Provenance

prov = Provenance.create_now(
    analyzer="GeneFinder",
    version="0.1.0",
    parameters={
        "min_length": 100,
        "confidence_threshold": 0.5
    },
    dependencies=["ORFFinder", "MotifScanner"],
    references=[
        "doi:10.1093/nar/gkz310",
        "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6323893/"
    ]
)
```

### GenomicFeature

The primary output of all analyzers:

```python
from genomesim.core import GenomicFeature

feature = GenomicFeature(
    start=1000,           # 0-based, inclusive
    end=2000,             # 0-based, exclusive
    strand='+',           # '+' or '-'
    feature_type='gene',
    confidence=conf,
    attributes={
        'name': 'hypothetical_protein',
        'id': 'gene_001',
        'function': 'DNA-binding'
    },
    provenance=prov,
    sequence_id='chr1'
)

# Methods
print(feature.length())  # 1000 bp
print(feature.overlaps(other_feature))  # True/False
print(feature.distance_to(other_feature))  # distance in bp
print(feature.to_gff3())  # GFF3 format line
```

## Interfaces

### SequenceAnalyzer

Base class for all genomic analyzers:

```python
from genomesim.core import SequenceAnalyzer

class MyAnalyzer(SequenceAnalyzer):
    @property
    def name(self) -> str:
        return "MyAnalyzer"

    @property
    def analysis_type(self) -> AnalysisType:
        return AnalysisType.STRUCTURAL

    @property
    def input_scale(self) -> SequenceScale:
        return SequenceScale.NUCLEOTIDE

    @property
    def output_scale(self) -> SequenceScale:
        return SequenceScale.GENE

    def analyze(self, sequence: str, **kwargs) -> List[GenomicFeature]:
        # Your analysis logic here
        pass

    def get_parameters(self) -> Dict:
        return {"param": "value"}
```

**Key requirements**:
1. Must compute explicit confidence
2. Must create proper provenance
3. Must validate input sequence
4. Must return GenomicFeature objects

### ScaleBridge

Integrates features across scales:

```python
from genomesim.core import ScaleBridge

class MyBridge(ScaleBridge):
    @property
    def name(self) -> str:
        return "MyBridge"

    @property
    def input_scale(self) -> SequenceScale:
        return SequenceScale.MOTIF

    @property
    def output_scale(self) -> SequenceScale:
        return SequenceScale.GENE

    def bridge(self, lower_scale_features, **kwargs):
        # Integrate motifs into gene predictions
        pass
```

## Workflows

### Simple Analysis

```python
from genomesim.analyzers import ORFFinder

# Create analyzer
finder = ORFFinder(min_length=100)

# Analyze sequence
sequence = "ATGCGATCG..."
features = finder.analyze(sequence)

# Inspect results
for feature in features:
    print(f"{feature.start}-{feature.end}: confidence {feature.confidence.score}")
```

### Multi-Evidence Integration

```python
from genomesim.analyzers import ORFFinder, MotifScanner, GeneFinder

# Run multiple analyzers
orf_finder = ORFFinder()
motif_scanner = MotifScanner()

orfs = orf_finder.analyze(sequence)
motifs = motif_scanner.analyze(sequence)

# Integrate evidence
gene_finder = GeneFinder()
genes = gene_finder.analyze(sequence, orfs=orfs, motifs=motifs)

# Check confidence breakdown
for gene in genes:
    print(f"Gene: {gene.attributes.get('name', 'unknown')}")
    print(f"  Overall confidence: {gene.confidence.score:.2f}")
    print(f"  Evidence:")
    for source, value in gene.confidence.supporting_evidence.items():
        print(f"    {source}: {value}")
```

### Scale Bridging

```python
# Low scale analysis
motifs = motif_scanner.analyze(sequence)

# Bridge to higher scale
bridge = SequenceToGeneBridge()
genes = bridge.bridge(motifs)

# Confidence has propagated
for gene in genes:
    # Gene confidence aggregated from motif confidences
    print(gene.confidence.score)
```

## Best Practices

### 1. Always Validate Inputs

```python
def analyze(self, sequence: str, **kwargs):
    # Use built-in validation
    self.validate_sequence(sequence)

    # Add custom validation
    if len(sequence) < self.min_length:
        raise ValueError(f"Sequence too short: {len(sequence)} < {self.min_length}")
```

### 2. Compute Meaningful Confidence

```python
# Bad: Arbitrary confidence
confidence = Confidence(0.5, "guess", ["?"], {})

# Good: Evidence-based confidence
confidence = Confidence(
    score=min(1.0, alignment_score / max_possible_score),
    method="alignment-based",
    sources=["alignment_score", "e_value"],
    supporting_evidence={
        "alignment_score": alignment_score,
        "e_value": e_value,
        "percent_identity": pct_id
    }
)
```

### 3. Use Provenance.create_now()

```python
# Automatically adds current timestamp
provenance = Provenance.create_now(
    analyzer=self.name,
    version=self.get_version(),
    parameters=self.get_parameters(),
)
```

### 4. Handle Edge Cases

```python
# Empty sequence
if not sequence:
    return []

# Ambiguous bases (N)
if sequence.count('N') / len(sequence) > 0.5:
    # Low confidence for high N content
    confidence_multiplier = 0.5
```

## Common Patterns

### Confidence Aggregation

```python
# Multiple independent evidence sources
confidences = [orf_conf, homology_conf, promoter_conf]
weights = [0.4, 0.4, 0.2]  # Importance of each

aggregated = sum(c * w for c, w in zip(confidences, weights))
```

### Provenance Chaining

```python
# Track dependencies
dependencies = [
    orf_feature.provenance.analyzer,
    motif_feature.provenance.analyzer,
]

provenance = Provenance.create_now(
    analyzer=self.name,
    version=self.get_version(),
    parameters=self.get_parameters(),
    dependencies=dependencies,  # Shows data lineage
)
```

---

**Next Steps**:
- [[creating-analyzers]] - Implement your own analyzer
- [[architecture]] - Understand the system design
- [[confidence-calculation]] - Deep dive on uncertainty

**References**:
- Python Type System: PEP 484
- Dataclasses: PEP 557
- Abstract Base Classes: PEP 3119
