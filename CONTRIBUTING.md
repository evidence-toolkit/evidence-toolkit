# Contributing to Evidence Toolkit

Thank you for considering contributing to Evidence Toolkit! This document provides guidelines and best practices for contributing to the project.

## 🎯 Project Philosophy

**Core Principles:**
- **Avoid over-engineering**: Simple, direct solutions preferred over complex abstractions
- **Domain-agnostic core**: 95% of toolkit is domain-independent
- **Minimal configuration**: Domain behavior via ~100-line config files, no plugin systems
- **Forensic integrity**: All changes must preserve chain of custody and deterministic analysis
- **Cost efficiency**: Minimize AI API calls through smart caching and reuse

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.12+ (required)
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- OpenAI API key for AI-powered analysis
- Git for version control

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit

# Install in editable mode
pip install -e .
# OR using uv (recommended)
uv pip install -e .

# Set up OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Verify installation
python validate_environment.py
.venv/bin/document-analyzer --help
```

**⚠️ Important**: Always work from the root directory with the unified `.venv` environment.

## 📁 Repository Structure

```
evidence-toolkit/
├── document-evidence-analyzer/       # Main analysis engine
│   └── src/
│       ├── document_analyzer/        # Core analyzers (generic)
│       └── domains/                  # Domain configurations
│           └── legal_config.py       # Legal domain (default)
├── archive/                          # Archived legacy code
│   └── image-analysis-legacy-*/      # Previous image-analysis structure
├── schemas/                          # JSON schemas for validation
├── tests/                            # Test suite
├── pyproject.toml                    # Package configuration
└── README.md                         # Project overview
```

## 🔧 Development Workflow

### 1. Create a Feature Branch

```bash
# Create and checkout feature branch
git checkout -b feature/your-feature-name

# OR for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Your Changes

**Code Organization:**
- **Generic functionality**: Goes in `document_analyzer/` modules
- **Domain-specific config**: Goes in `domains/your_domain_config.py`
- **Tests**: Add to `tests/` with matching structure
- **Documentation**: Update relevant `.md` files

**Coding Standards:**
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Use Pydantic models for data validation
- Add docstrings for public functions and classes
- Prefer explicit over implicit (clarity over cleverness)

### 3. Test Your Changes

```bash
# Run test suite
pytest tests/

# Test CLI commands
.venv/bin/document-analyzer --help
.venv/bin/document-analyzer process-case cases/test-case TEST-001

# Validate schema compliance
python validate_cross_analysis.py --comprehensive

# Test installation works
pip install -e . --force-reinstall --no-deps
```

### 4. Commit Your Changes

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(correlation): Add temporal gap detection for timeline analysis"
git commit -m "fix(email): Handle missing subject headers gracefully"
git commit -m "docs: Update QUICKSTART with multi-case examples"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push -u origin feature/your-feature-name

# Create PR via GitHub interface
# Ensure PR description includes:
# - What changes were made
# - Why they were needed
# - How to test them
# - Any breaking changes
```

## 🎨 Code Style Guidelines

### Python Code Style

```python
# Good: Clear, explicit, type-hinted
def analyze_document(
    content: str,
    case_id: str,
    domain_config: Any = None
) -> DocumentAnalysisResult:
    """
    Analyze document content using AI.

    Args:
        content: Raw document text
        case_id: Case identifier for this analysis
        domain_config: Optional domain configuration module

    Returns:
        Structured analysis result with entities and risk flags
    """
    # Implementation here
    pass

# Bad: Unclear, no types, no docs
def analyze(c, id):
    # What does this do?
    pass
```

### Pydantic Models

```python
# Good: Clear field descriptions, validation
class DocumentAnalysis(BaseModel):
    """AI-generated document analysis output."""

    summary: str = Field(
        description="Concise summary of document content"
    )
    entities: List[DocumentEntity] = Field(
        default_factory=list,
        description="Extracted entities with confidence scores"
    )
    confidence_overall: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall confidence in analysis (0.0-1.0)"
    )
```

### Domain Configuration

```python
# Good: Clear prompts, documented flags
# domains/corporate_config.py

DOCUMENT_ANALYSIS_PROMPT = """
You are analyzing corporate documents for compliance and risk assessment.

Focus on:
1. Policy violations and ethical concerns
2. Financial irregularities or fraud indicators
3. Regulatory compliance issues
4. Internal control weaknesses

Provide confidence scores (0.0-1.0) for all findings.
"""

CRITICAL_RISK_FLAGS = {
    'fraud_indicators',
    'policy_violation',
    'ethical_breach',
    'regulatory_noncompliance'
}
```

## 🧪 Testing Guidelines

### Writing Tests

```python
# tests/test_correlation.py
import pytest
from document_analyzer.correlation_analyzer import CorrelationAnalyzer

def test_entity_canonicalization():
    """Test that entity name variants are properly canonicalized."""
    analyzer = CorrelationAnalyzer(case_id="TEST-001")

    # Test name normalization
    assert analyzer.canonicalize_name("John Q. Smith") == "John Smith"
    assert analyzer.canonicalize_name("J. Smith") == "J Smith"
    assert analyzer.canonicalize_name("john smith") == "John Smith"

def test_multi_case_evidence_reuse():
    """Test that evidence can be associated with multiple cases."""
    # Setup: Create evidence in CASE-001
    # Test: Add same evidence to CASE-002
    # Assert: case_ids contains both, analysis not re-run
    pass
```

### Test Coverage

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test CLI commands and workflows
- **Schema validation**: Ensure all outputs validate against schemas
- **Domain tests**: Test domain configurations independently

## 📝 Documentation Guidelines

### Code Documentation

```python
def analyze_email_thread(
    email_content: str,
    case_id: str
) -> EmailThreadAnalysis:
    """
    Analyze email thread for legal significance and escalation patterns.

    This function uses OpenAI's Responses API with temperature=0 for
    deterministic results suitable for legal evidence processing.

    Args:
        email_content: Raw email text including headers
        case_id: Case identifier for tracking

    Returns:
        EmailThreadAnalysis with participants, escalation events,
        and risk flags

    Raises:
        ValueError: If email_content is empty or invalid
        OpenAIError: If AI analysis fails

    Example:
        >>> analysis = analyze_email_thread(email_text, "CASE-001")
        >>> print(analysis.communication_pattern)
        'escalating'
    """
```

### User Documentation

When adding features, update:
- `README.md` - High-level feature description
- `QUICKSTART.md` - Usage examples
- `DATA_OUTPUTS.md` - New data structures
- `CLAUDE.md` - Development guidance

## 🎯 Contribution Areas

### High-Priority Contributions

**1. Domain Configurations**
- Create new domain configs (corporate, journalism, research)
- Enhance legal domain with specialized prompts
- Document domain best practices

**2. Analysis Enhancements**
- Improve entity extraction accuracy
- Add new temporal pattern detections
- Enhance cross-evidence correlation

**3. Testing & Validation**
- Increase test coverage
- Add edge case tests
- Performance benchmarking

**4. Documentation**
- User guides for specific workflows
- API reference documentation
- Tutorial videos or examples

### Domain Configuration Contributions

Creating a new domain is highly valuable:

1. **Copy existing domain**: `cp domains/legal_config.py domains/your_domain_config.py`
2. **Modify prompts**: Tailor AI prompts for your domain
3. **Define risk flags**: Domain-specific flags (e.g., journalism: `'misinformation'`, `'source_credibility'`)
4. **Test thoroughly**: Ensure prompts produce good results
5. **Document usage**: Add examples to README

## 🚫 What NOT to Contribute

- **Over-engineered solutions**: Plugin systems, complex abstractions when simple config works
- **Breaking changes**: Without discussion and migration path
- **Untested code**: All PRs must include tests
- **Non-deterministic analysis**: AI analysis must use temperature ≤ 0.2 for forensic integrity
- **Security vulnerabilities**: No credential harvesting, malicious code analysis

## 🔍 Code Review Process

All contributions go through review:

1. **Automated checks**: Tests, linting, schema validation
2. **Architecture review**: Aligns with domain-agnostic principles
3. **Code quality**: Readable, maintainable, well-documented
4. **Testing**: Adequate test coverage for changes
5. **Documentation**: User-facing changes documented

**Review criteria:**
- ✅ Tests pass
- ✅ Follows coding standards
- ✅ Documentation updated
- ✅ No over-engineering
- ✅ Preserves forensic integrity
- ✅ Backward compatible (or migration path provided)

## 🐛 Bug Reports

**Good bug report includes:**
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (Python version, OS)
- Error messages and stack traces
- Sample data if relevant (sanitized!)

**Template:**
```markdown
## Bug Description
[Clear description]

## Steps to Reproduce
1. Run command: `.venv/bin/document-analyzer ...`
2. Observe error: ...

## Expected Behavior
Should have generated...

## Actual Behavior
Instead got error: ...

## Environment
- Python version: 3.12.2
- OS: Ubuntu 22.04
- Evidence Toolkit version: 2.0.0
```

## 💡 Feature Requests

**Good feature request includes:**
- Use case and motivation
- Proposed solution
- Alternative approaches considered
- Willingness to implement (optional)

## 🤝 Community Guidelines

- **Be respectful**: Constructive feedback only
- **Be patient**: Maintainers are often volunteers
- **Be helpful**: Answer questions, help others
- **Be thorough**: Well-documented contributions save time

## 📧 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and community support
- **Documentation**: Check README, QUICKSTART, DATA_OUTPUTS first

## 🎖️ Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- Git commit co-authorship where applicable

---

**Thank you for contributing to Evidence Toolkit!**

Your contributions help build better tools for legal professionals, journalists, researchers, and anyone who needs robust evidence analysis.
