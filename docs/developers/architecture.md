# GenomeSim Architecture

**Tags**: #core #reference #architecture

This document provides a comprehensive overview of GenomeSim's architecture, design patterns, and key components.

## Design Principles

### 1. Plugin Architecture

All analysis methods are pluggable modules. This enables:
- **Extensibility**: Easy to add new analyzers
- **Swappability**: Replace implementations without changing pipelines
- **Comparability**: Run multiple methods on same data
- **Testability**: Mock components for testing

### 2. Explicit Uncertainty

Every prediction must quantify its uncertainty:
- **Confidence scores**: Always between 0.0 and 1.0
- **Evidence breakdown**: What supports this prediction?
- **Source tracking**: What contributes to uncertainty?
- **Method description**: How was confidence computed?

### 3. Complete Provenance

Every result tracks:
- Which analyzer produced it
- What version of software
- What parameters were used
- What data sources contributed
- When the analysis was performed

### 4. Type Safety

- Full type hints on all public APIs
- Validation at data structure boundaries
- Enum types for categorical values
- Dataclasses for structured data

## Core Type System

### Hierarchical Scales

```python
SequenceScale.NUCLEOTIDE → MOTIF → DOMAIN → GENE → OPERON → CHROMOSOME → GENOME
```

Analysis flows from lower scales to higher scales, with uncertainty propagating upward.

### Analysis Categories

```python
class AnalysisType(Enum):
    STRUCTURAL      # What's physically there?
    COMPOSITIONAL   # What's the makeup?
    FUNCTIONAL      # What does it do?
    EVOLUTIONARY    # How did it get here?
    REGULATORY      # How is it controlled?
```

### Core Data Structures

```python
@dataclass
class Confidence:
    score: float              # 0.0 to 1.0
    method: str               # How computed
    sources: List[str]        # Contributing factors
    supporting_evidence: Dict # Evidence details

@dataclass
class Provenance:
    analyzer: str
    version: str
    parameters: Dict
    timestamp: str
    dependencies: List[str]
    references: List[str]

@dataclass
class GenomicFeature:
    start: int
    end: int
    strand: str
    feature_type: str
    confidence: Confidence
    attributes: Dict
    provenance: Provenance
    sequence_id: Optional[str]
```

## Component Architecture

### Analyzers

Base class: `SequenceAnalyzer`

All analyzers implement:
- `name`: Unique identifier
- `analysis_type`: Category of analysis
- `input_scale` / `output_scale`: Scales operated on
- `analyze()`: Core analysis method
- `get_parameters()`: Current configuration

Analyzer lifecycle:
1. Instantiate with parameters
2. Validate input sequence
3. Perform analysis
4. Compute confidence
5. Create provenance
6. Return GenomicFeature objects

### Scale Bridges

Base class: `ScaleBridge`

Bridges integrate features across scales:
- Input: Features from lower scale(s)
- Output: Features at higher scale
- Aggregates confidence scores
- Tracks all input dependencies

Example: `MotifToGeneBridge`
- Input: Motifs (promoters, splice sites)
- Output: Genes
- Logic: Combine regulatory signals into gene predictions

### Registries

Pattern: Registry of available components

```python
class AnalyzerRegistry:
    """Registry of available analyzers."""

    def register(self, analyzer_class):
        """Register an analyzer."""

    def get(self, name: str) -> SequenceAnalyzer:
        """Retrieve analyzer by name."""

    def list_available(self) -> List[str]:
        """List all registered analyzers."""
```

Enables:
- Dynamic discovery
- Plugin loading
- Configuration-driven pipelines

## Data Flow

### Simple Pipeline

```
Sequence → ORFFinder → ORF Features
```

### Multi-Evidence Pipeline

```
Sequence → ORFFinder → ORFs ──┐
        → MotifScanner → Motifs ├→ GeneFinder → Genes
        → GCAnalyzer → GC Content ┘
```

### Multi-Scale Pipeline

```
Nucleotides → Motifs → Domains → Genes → Pathways → Phenotypes
              ↓         ↓          ↓         ↓          ↓
           Confidence propagates and aggregates upward
```

## Confidence Propagation

### Single Source
```python
confidence = Confidence(
    score=0.85,
    method="homology",
    sources=["blast_evalue"],
    supporting_evidence={"blast_evalue": 1e-50}
)
```

### Multiple Sources (Weighted Average)
```python
# ORF structure: 0.8
# Homology: 0.9
# Promoter: 0.6
combined_score = 0.3 * 0.8 + 0.4 * 0.9 + 0.3 * 0.6
# = 0.78
```

### Aggregation Methods
- **Weighted average**: Balance multiple sources
- **Minimum**: Conservative (weakest link)
- **Geometric mean**: Penalize low confidences

## Directory Structure

```
GenomeSim/
├── genomesim/              # Python package
│   ├── core/              # Core types and interfaces
│   │   ├── types.py       # Data structures
│   │   └── interfaces.py  # Abstract base classes
│   │
│   ├── analyzers/         # Concrete analyzers
│   │   ├── orf_finder.py
│   │   ├── motif_scanner.py
│   │   └── gc_analyzer.py
│   │
│   ├── bridges/           # Scale bridges
│   │   └── sequence_to_gene.py
│   │
│   ├── ml/                # ML model wrappers
│   │   ├── enformer.py
│   │   └── spliceai.py
│   │
│   └── utils/             # Utilities
│       ├── sequence.py
│       └── file_io.py
│
├── tests/                 # Test suite
│   ├── test_types.py
│   ├── test_interfaces.py
│   └── analyzers/
│
├── examples/              # Usage examples
├── docs/                  # Documentation
└── genomesim-desktop/    # Desktop app (Phase 3+)
```

## Extension Points

### Adding a New Analyzer

1. Inherit from `SequenceAnalyzer`
2. Implement required methods
3. Add to `genomesim/analyzers/`
4. Write tests in `tests/analyzers/`
5. Document in `docs/analyzers/`
6. Add to analyzer registry

### Adding a New Scale Bridge

1. Inherit from `ScaleBridge`
2. Implement `bridge()` method
3. Handle confidence aggregation
4. Track provenance dependencies

### Adding ML Integration

1. Wrap external model in analyzer interface
2. Download/cache model weights
3. Convert inputs to model format
4. Convert outputs to GenomicFeature
5. Compute confidence from model uncertainty

## Performance Considerations

### Scalability Targets

- E. coli genome (4.6 Mb): < 1 minute
- Human chromosome (100-250 Mb): < 1 hour
- Full human genome (3.2 Gb): < 24 hours

### Optimization Strategies

1. **Lazy loading**: Only load data as needed
2. **Streaming**: Process sequences in chunks
3. **Parallel processing**: Multiprocessing for independent analyses
4. **GPU acceleration**: For ML models and intensive computation
5. **Caching**: Store intermediate results

### Memory Management

- Stream large FASTA files (don't load entire genome)
- Use generators for feature iteration
- Clear caches periodically
- Profile memory usage

## Testing Strategy

### Unit Tests
- Test each analyzer independently
- Mock external dependencies
- Test edge cases (empty sequence, all Ns)
- Verify confidence bounds (0.0 to 1.0)
- Check provenance tracking

### Integration Tests
- Test multi-analyzer pipelines
- Verify scale bridging
- Test confidence propagation
- End-to-end workflows

### Performance Tests
- Benchmark on known datasets
- Profile bottlenecks
- Monitor memory usage
- Scalability tests (small → large genomes)

## Security Considerations

### Data Privacy
- Local processing (no cloud upload)
- Secure file handling
- No telemetry by default
- Encryption options for results

### Code Safety
- Input validation
- Type checking
- Bounds checking
- Safe file operations

## Future Architecture

### Phase 3+: Desktop Application

```
Desktop App (Tauri)
├── Rust Backend
│   ├── File I/O
│   ├── Process management
│   └── IPC with Python
│
└── React Frontend
    ├── Genome Browser
    ├── Feature Table
    └── Visualization

↕ (FastAPI)

Python Backend (GenomeSim)
└── Analysis Engine
```

### Phase 7: Distributed Processing

```
Coordinator
├── Task Queue
├── Worker 1: ORF Finding
├── Worker 2: Motif Scanning
├── Worker 3: Homology Search
└── Worker 4: Result Aggregation
```

---

**See Also**:
- [[core-concepts]] - Understanding the type system
- [[creating-analyzers]] - How to implement analyzers
- [[confidence-calculation]] - Computing uncertainty

**References**:
- Design Patterns: Gang of Four
- Plugin Architecture: PEP 302
- Type System: PEP 484, PEP 526
