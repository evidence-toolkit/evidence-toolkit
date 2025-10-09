# Evidence Toolkit

[![Version](https://img.shields.io/badge/version-3.3.0-success.svg)](CHANGELOG.md)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991.svg)](https://openai.com/)

**AI-powered forensic evidence analysis for workplace investigations, legal cases, and compliance reviews.**

Transform a folder of evidence files into professional forensic analysis packages with AI-powered insights, cross-evidence correlation, and complete chain of custody tracking.

---

## Quick Start

```bash
# Install
git clone https://github.com/your-org/evidence-toolkit.git
cd evidence-toolkit
uv pip install -e .

# Configure
export OPENAI_API_KEY="your-key-here"

# Run analysis
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# View results
ls data/packages/
```

**[→ Full Quick Start Guide](QUICKSTART.md)**

---

## What It Does

**Input**: Documents (PDF, TXT), emails (EML), images (JPG, PNG)
**Output**: Professional ZIP package with executive summary, correlations, timeline, and forensic reports

### Key Features

- **AI Analysis**: Entity extraction, sentiment analysis, legal risk assessment
- **Cross-Evidence Correlation**: Find connections across documents, emails, and images
- **Timeline Reconstruction**: Automatic chronology from metadata and semantic events (v3.3)
- **Power Dynamics**: Email hierarchy and communication pattern analysis
- **Relationship Networks**: Escalation chains and communication mapping (v3.3)
- **Image OCR Aggregation**: Extract and analyze text from visual evidence (v3.3)
- **Chain of Custody**: Complete audit trail for legal compliance
- **Content-Addressed Storage**: SHA256-based deduplication and integrity verification
- **98% Data Utilization**: Maximum insights from every AI analysis (v3.3)

### Example Use Cases

- Workplace harassment investigations
- Employment tribunal evidence preparation
- Corporate compliance reviews
- Legal discovery and e-discovery support
- Whistleblower complaint analysis

---

## Architecture

### Content-Addressed Storage

Evidence is stored by SHA256 hash for automatic deduplication:

```
data/storage/
├── raw/sha256=<hash>/           # Immutable originals
├── derived/sha256=<hash>/       # AI analysis, metadata
└── cases/<case-id>/             # Hard links to evidence
```

**Benefits**: Same file analyzed once, used everywhere. 90%+ cost savings on multi-case workflows.

### Processing Pipeline

```
Ingest → Analyze → Correlate → Package
  ↓         ↓          ↓           ↓
SHA256   AI analysis  Entity    ZIP with
hashing  (GPT-4o)    matching   reports
```

### Tech Stack

- **Core**: Python 3.12+, Pydantic (48 models), content-addressed storage
- **AI**: OpenAI GPT-4o-mini (analysis), GPT-4o (vision)
- **Formats**: PDF, TXT, EML, JPG, PNG
- **Output**: JSON structured data, markdown reports, ZIP packages

---

## Installation

### Prerequisites

- Python 3.12+
- OpenAI API key

### Using UV (Recommended)

```bash
pip install uv
uv pip install -e .
uv run evidence-toolkit --version
```

### Using pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
evidence-toolkit --version
```

---

## Usage

### Basic Workflow

```bash
# 1. Add evidence files
mkdir -p data/cases/MY-CASE
cp /path/to/evidence/* data/cases/MY-CASE/

# 2. Run complete pipeline
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# 3. View package
ls -lh data/packages/MY-CASE*.zip
```

### Advanced Features

**AI Entity Resolution** (v3.2):
```bash
# Context-aware name matching ("John" → "John Smith")
uv run evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --ai-resolve
```

**Case Type Support** (v3.2):
```bash
# Domain-specific analysis prompts
uv run evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --case-type workplace
```

**Individual Steps**:
```bash
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE
uv run evidence-toolkit correlate --case-id MY-CASE
uv run evidence-toolkit package --case-id MY-CASE
```

---

## Output Package

```
MY-CASE_analysis_package_20251009_143000/
├── reports/
│   └── executive_summary.txt          # AI-generated case summary
├── analysis/
│   ├── case_analysis.json             # Structured forensic data
│   └── [individual analyses]          # Per-evidence AI analysis
├── correlations/
│   └── correlation_analysis.json      # Cross-evidence patterns
├── evidence_catalog/
│   └── evidence_catalog.json          # Evidence inventory
└── raw_evidence/
    └── [original files]               # Your evidence files
```

### Executive Summary Includes (v3.3 Enhanced)

- **Forensic Summary**: Detailed narrative analysis (1,280-char insights-first)
- **Key Findings**: 3-5 bullet-point discoveries with evidence citations
- **Legal Implications**: 5 specific risk areas for case strategy
- **Recommended Actions**: 5 strategic guidance items
- **Quoted Statements**: Direct quotes by person with sentiment analysis (v3.3)
- **Communication Patterns**: Email risk classification and pattern distribution (v3.3)
- **Relationship Network**: Key players and connection mapping (v3.3)
- **Image OCR Analysis**: Text extraction from visual evidence (v3.3)
- **Entity Correlations**: People/orgs appearing across evidence
- **Timeline Analysis**: Event chronology with semantic events (v3.3)

---

## Performance & Costs

### Processing Times

| Evidence Count | Time | Notes |
|----------------|------|-------|
| 5 files        | 2-3 min | Mixed: docs, emails, images |
| 20 files       | 6-8 min | Typical investigation |
| 50+ files      | 15-20 min | Large case (chunked summaries) |

### OpenAI API Costs (Approximate)

- Document analysis: ~$0.001-0.003 per doc
- Email analysis: ~$0.002-0.005 per thread
- Image analysis: ~$0.003-0.008 per image
- Executive summary: ~$0.01-0.02 per case

**Example**: 20-piece case ≈ $0.10-0.30 total

**Cost optimization**: Content-addressed storage means duplicate evidence is analyzed once and reused across cases.

---

## CLI Reference

### Core Commands

```bash
# Complete pipeline
evidence-toolkit process-case <directory> --case-id <ID>

# Individual steps
evidence-toolkit ingest <directory> --case-id <ID>
evidence-toolkit analyze <sha256> --case-id <ID>
evidence-toolkit correlate --case-id <ID>
evidence-toolkit package --case-id <ID>

# Re-analysis (after model updates)
evidence-toolkit reanalyze --case-id <ID>
```

### Case Management

```bash
evidence-toolkit case list           # List all cases
evidence-toolkit case show <ID>      # Case details
evidence-toolkit case evidence <ID>  # Evidence in case
```

### Storage Management

```bash
evidence-toolkit storage stats       # Storage usage
evidence-toolkit storage cleanup     # Remove orphaned evidence
evidence-toolkit storage prune --case-id <ID>  # Clean specific case
```

---

## Forensic Integrity

### Deterministic AI Analysis

- **Temperature = 0**: Reproducible results (same input → same output)
- **Structured Output**: Pydantic validation ensures schema compliance
- **Confidence Scoring**: Every finding includes confidence metrics
- **Model Tracking**: Analysis records AI model version used

### Chain of Custody

Every operation logged with timestamps and actor identification:

```json
{
  "ts": "2025-10-09T14:30:45.123Z",
  "actor": "investigator@firm.com",
  "action": "ingest",
  "note": "Evidence file ingested from data/cases/CASE-001/document.pdf"
}
```

---

## Version History

**Current**: v3.3.0 (October 2025)

### v3.3 - Maximum Data Utilization
- Quoted statement aggregation by person
- Communication pattern risk assessment
- Semantic timeline extraction
- Relationship network analysis
- Insights-first report layout
- **98% data utilization** (up from 65%)

### v3.2 - Intelligence Enhancements
- AI entity resolution with context-aware matching
- Case type support (generic, workplace, contract)
- Chunked summaries for 50+ evidence pieces

### v3.1 - AI Enhancements
- Legal pattern detection (contradictions, corroboration, gaps)
- Power dynamics analysis (email hierarchy, dominance scoring)
- Enhanced entity extraction (relationships, quotes)

### v3.0 - Foundation
- Unified Pydantic architecture (48 models)
- Content-addressed storage with SHA256
- Clean pipeline design

---

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Architecture Documentation](V3_ARCHITECTURE.md)** - Complete design
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Case Types](docs/CASE_TYPES.md)** - Domain-specific analysis

---

## Contributing

Contributions welcome! Areas of interest:

- **Domain configurations**: Corporate, journalism, research use cases
- **Analyzer improvements**: New evidence types, enhanced AI prompts
- **Integrations**: Case management systems, e-discovery tools
- **Documentation**: Tutorials, examples, use case guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/evidence-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/evidence-toolkit/discussions)
- **Documentation**: [Project Wiki](https://github.com/your-org/evidence-toolkit/wiki)

---

*Built for ethical workplace investigations and legal evidence analysis with forensic integrity.*
