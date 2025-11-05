# Contributing to GenomeSim

Thank you for your interest in contributing to GenomeSim! We welcome contributions from everyone, whether you're fixing a bug, adding a feature, improving documentation, or proposing new analysis methods.

## 🎯 Project Philosophy

Before contributing, please understand GenomeSim's core principles:

1. **Epistemic Humility**: Every prediction must include explicit confidence scores
2. **Provenance Tracking**: All results must track how they were obtained
3. **Plugin Architecture**: New analyzers should follow the standard interfaces
4. **Test Coverage**: All code must have comprehensive tests (>80% coverage)
5. **Type Safety**: Full type hints required for all public functions

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/GenomeSim.git
cd GenomeSim

# Add upstream remote
git remote add upstream https://github.com/BarzinL/GenomeSim.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev,ml,api,docs]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Types of Contributions

### 🔬 Adding a New Analyzer

Analyzers are the core of GenomeSim. To add a new analyzer:

1. **Implement the Interface**: Inherit from `SequenceAnalyzer`
2. **Compute Confidence**: Explicitly calculate confidence scores
3. **Track Provenance**: Use `Provenance.create_now()`
4. **Add Tests**: Comprehensive unit tests required
5. **Document**: Include docstrings and examples

Example structure:

```python
from genomesim.core import SequenceAnalyzer, AnalysisType, SequenceScale
from genomesim.core import GenomicFeature, Confidence, Provenance

class MyAnalyzer(SequenceAnalyzer):
    """
    Brief description of what this analyzer does.

    Attributes:
        param1: Description of parameter

    Example:
        >>> analyzer = MyAnalyzer(param1=value)
        >>> features = analyzer.analyze(sequence)
    """

    def __init__(self, param1: int = 100):
        self._param1 = param1

    @property
    def name(self) -> str:
        return "MyAnalyzer"

    @property
    def analysis_type(self) -> AnalysisType:
        return AnalysisType.STRUCTURAL  # Or appropriate type

    @property
    def input_scale(self) -> SequenceScale:
        return SequenceScale.NUCLEOTIDE

    @property
    def output_scale(self) -> SequenceScale:
        return SequenceScale.GENE  # Or appropriate scale

    def analyze(self, sequence: str, sequence_id: str = None, **kwargs):
        # 1. Validate input
        self.validate_sequence(sequence)

        # 2. Perform analysis
        # ... your analysis logic ...

        # 3. Compute confidence explicitly
        confidence = Confidence(
            score=0.85,  # Calculate based on evidence
            method="description of method",
            sources=["source1", "source2"],
            supporting_evidence={
                "source1": value1,
                "source2": value2,
            }
        )

        # 4. Create provenance
        provenance = Provenance.create_now(
            analyzer=self.name,
            version=self.get_version(),
            parameters=self.get_parameters(),
        )

        # 5. Return features
        return [
            GenomicFeature(
                start=start,
                end=end,
                strand=strand,
                feature_type="gene",  # Or appropriate type
                confidence=confidence,
                attributes={},  # Add relevant attributes
                provenance=provenance,
                sequence_id=sequence_id,
            )
        ]

    def get_parameters(self):
        return {"param1": self._param1}
```

Place your analyzer in `genomesim/analyzers/my_analyzer.py`

### 🧪 Writing Tests

Every analyzer must have comprehensive tests. Create `tests/test_my_analyzer.py`:

```python
import pytest
from genomesim.analyzers import MyAnalyzer

class TestMyAnalyzer:
    def test_analyzer_basic_functionality(self):
        """Test basic analyzer operation."""
        analyzer = MyAnalyzer()
        sequence = "ATGCGATCG..."
        features = analyzer.analyze(sequence)

        assert len(features) > 0
        assert all(f.confidence.score >= 0.0 for f in features)
        assert all(f.confidence.score <= 1.0 for f in features)

    def test_analyzer_confidence_calculation(self):
        """Test that confidence is calculated correctly."""
        # ... test confidence computation ...

    def test_analyzer_provenance_tracking(self):
        """Test that provenance is tracked."""
        analyzer = MyAnalyzer()
        features = analyzer.analyze("ATGC")

        assert features[0].provenance.analyzer == "MyAnalyzer"
        assert "param1" in features[0].provenance.parameters
```

### 🐛 Fixing Bugs

1. Check if an issue exists; if not, create one
2. Reference the issue in your branch name: `fix/issue-123-description`
3. Add a test that reproduces the bug
4. Fix the bug
5. Verify the test passes

### 📚 Improving Documentation

Documentation improvements are always welcome:

- **Docstrings**: Add or improve function/class documentation
- **Examples**: Add usage examples in `examples/`
- **Guides**: Improve user or developer guides in `docs/`
- **README**: Clarify unclear sections

### 🎨 Code Style

We use automated formatting and linting:

```bash
# Format code
black genomesim tests

# Sort imports
isort genomesim tests

# Check style
flake8 genomesim tests

# Type check
mypy genomesim
```

Pre-commit hooks will run these automatically.

## ✅ Pull Request Process

### 1. Before Submitting

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black genomesim tests`
- [ ] Imports are sorted: `isort genomesim tests`
- [ ] No linting errors: `flake8 genomesim tests`
- [ ] Type hints are correct: `mypy genomesim`
- [ ] Coverage is maintained: `pytest --cov`
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated (if applicable)

### 2. Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(analyzers): add RepeatDetector for tandem repeats

Implements detection of tandem repeats using dynamic programming.
Includes confidence calculation based on repeat perfection.

Fixes #42
```

```
fix(types): correct confidence validation bounds

Confidence score validation was incorrectly rejecting 1.0.
Now accepts the full valid range [0.0, 1.0].

Fixes #56
```

### 3. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (black, isort)
- [ ] Type hints added
- [ ] All tests pass
```

### 4. Review Process

1. Automated checks must pass (GitHub Actions)
2. At least one maintainer review required
3. Address review feedback
4. Maintainer will merge when approved

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_types.py          # Core type tests
├── test_interfaces.py     # Interface tests
├── analyzers/
│   ├── test_orf_finder.py
│   ├── test_motif_scanner.py
│   └── ...
└── integration/
    └── test_pipeline.py   # End-to-end tests
```

### Test Coverage

We maintain >80% code coverage. Check coverage:

```bash
pytest --cov=genomesim --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Markers

Use pytest markers for organizing tests:

```python
@pytest.mark.slow
def test_large_genome_analysis():
    """Test on large genome (slow)."""
    pass

@pytest.mark.integration
def test_full_pipeline():
    """Integration test."""
    pass

@pytest.mark.ml
def test_enformer_wrapper():
    """Test requiring ML dependencies."""
    pass
```

Run specific test groups:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Only integration tests
```

## 📊 Performance Considerations

When adding features, consider performance:

1. **Profile first**: Use `cProfile` or `line_profiler`
2. **Optimize algorithms**: Choose appropriate data structures
3. **Add benchmarks**: Document performance characteristics
4. **Parallel processing**: Use multiprocessing where appropriate

Example benchmark:

```python
def test_analyzer_performance(benchmark):
    """Benchmark analyzer on typical input."""
    analyzer = MyAnalyzer()
    sequence = "A" * 10000  # 10kb sequence

    result = benchmark(analyzer.analyze, sequence)
    assert len(result) > 0
```

## 🔐 Security Considerations

- Never commit sensitive data (genomes, API keys)
- Use `.gitignore` to exclude data files
- Report security issues privately to barzin@duck.com
- Do not include patient data in tests

## 📄 License

By contributing, you agree that your contributions will be licensed under the AGPLv3 license. You retain copyright to your contributions.

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We do not tolerate harassment or discrimination.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Respecting differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behaviors:**
- Harassment, trolling, or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations can be reported to barzin@duck.com. All complaints will be reviewed and investigated.

## 💬 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Feature Requests**: Open a GitHub Issue with `enhancement` label
- **Chat**: Coming soon (Discord/Slack)

## 🎓 Learning Resources

New to genomics or computational biology?

- **Primer on Genomics**: See `docs/primers/genomics_basics.md`
- **Algorithm Explanations**: See `docs/algorithms/`
- **Example Notebooks**: See `examples/`

## 🌟 Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md for releases
- Academic papers using their contributions (with permission)

Thank you for contributing to GenomeSim! Together we're building transparent, accessible genomic analysis tools for everyone.

---

**Questions?** Open a discussion or email barzin@bart.network
