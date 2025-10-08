# Evidence Toolkit

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991.svg)](https://openai.com/)
[![Version](https://img.shields.io/badge/version-3.3.0-green.svg)](https://github.com/evidence-toolkit/evidence-toolkit)

**AI-powered forensic evidence analysis for legal, corporate, and investigative use**

The Evidence Toolkit analyzes documents, emails, and images to produce professional client deliverables with AI-powered insights, cross-evidence correlation, timeline reconstruction, and complete chain of custody tracking.

---

## What It Does

Transform a folder of evidence files into a professional forensic analysis package with AI-powered insights:

**Input**: Documents (PDF, TXT), emails (EML), images (JPG, PNG)
**Output**: ZIP package with executive summary, entity correlations, timeline, risk assessment, and original evidence

**v3.3 NEW**: Maximum Data Utilization (95%→98% AI data surfaced) + insights-first reporting (forensic summary, key findings, legal implications, recommended actions)

**Example**: 5 evidence files → 3-minute analysis → Professional client package ready for legal proceedings

---

## Quick Start

### 👉 [5-Minute Quick Start Guide](QUICKSTART.md)

**New to the toolkit?** Start here for complete installation and first-run walkthrough.

### Try It Now

```bash
# 1. Install
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit
pip install -e .

# 2. Set API key
export OPENAI_API_KEY="your-key-here"

# 3. Test with sample evidence (2-3 minutes)
./quick-start.sh examples/sample-case-quickstart QUICKSTART-TEST

# 4. View results
cat data/packages/QUICKSTART-TEST*/reports/executive_summary.txt
```

**What you'll get**: Professional ZIP package with AI analysis of 5 evidence pieces (documents, email, images).

---

## How It Works

### 1. Organize Your Evidence

Place evidence files in a case directory:

```bash
# Standard approach - create case in data/cases/
mkdir -p data/cases/MY-CASE-2024

# Add your evidence files
cp /path/to/evidence/*.pdf data/cases/MY-CASE-2024/
cp /path/to/emails/*.eml data/cases/MY-CASE-2024/
cp /path/to/photos/*.jpg data/cases/MY-CASE-2024/
```

**Note**: Any directory works with the CLI, but `data/cases/` is our standard convention.

**Supported formats**:
- Documents: `.txt`, `.pdf`
- Emails: `.eml` (standard email format)
- Images: `.jpg`, `.jpeg`, `.png`

### 2. Run Analysis

**One-command complete pipeline**:
```bash
# Processes: ingest → analyze → correlate → package
evidence-toolkit process-case data/cases/MY-CASE-2024 --case-id MY-CASE-2024
```

**Or use individual steps**:
```bash
# Step 1: Ingest evidence into content-addressed storage
evidence-toolkit ingest data/cases/MY-CASE-2024 --case-id MY-CASE-2024

# Step 2: Analyze each piece (by SHA256 hash)
evidence-toolkit analyze <sha256-hash> --case-id MY-CASE-2024

# Step 3: Find correlations across evidence
evidence-toolkit correlate --case-id MY-CASE-2024

# Step 4: Generate client package
evidence-toolkit package --case-id MY-CASE-2024
```

### 3. Receive Professional Package

**Output location**: `data/packages/MY-CASE-2024_analysis_package_TIMESTAMP.zip`

**Package contains**:

```
MY-CASE-2024_analysis_package_20251005_142530/
├── reports/
│   └── executive_summary.txt          # AI-generated case summary
├── analysis/
│   ├── case_analysis.json             # Complete structured data
│   └── [individual evidence analyses]  # Per-file AI analysis
├── correlations/
│   └── correlation_analysis.json      # Cross-evidence patterns
├── evidence_catalog/
│   └── evidence_catalog.json          # Evidence inventory
├── documentation/
│   ├── README.md                      # Package guide
│   └── methodology.md                 # Analysis process
└── raw_evidence/
    └── [original files]               # Your evidence files
```

**Key deliverables**:
- **Executive Summary**: AI-generated overview with legal significance assessment
- **Entity Correlations**: People, organizations, dates appearing across multiple evidence pieces
- **Timeline Reconstruction**: Events from file metadata, email dates, and document content
- **Risk Assessment**: Flagged issues (harassment, retaliation, compliance violations)
- **Chain of Custody**: Complete audit trail for all evidence handling

---

## Core Features

### AI-Powered Analysis

**Documents**:
- Entity extraction (people, organizations, dates, legal terms)
- **v3.1**: Relationship tracking, verbatim quote extraction, event association
- Sentiment analysis (hostile, neutral, professional)
- Legal significance scoring (critical, high, medium, low)
- Risk flag identification (harassment, discrimination, retaliation)

**Emails**:
- Thread reconstruction and participant mapping
- Authority level detection (employee, manager, executive)
- **v3.1 NEW**: Power dynamics analysis (dominance/deference scoring, topic control)
- Communication pattern assessment
- Escalation event detection

**Images**:
- AI vision analysis using GPT-4 Vision
- OCR text extraction
- EXIF metadata extraction (timestamps, location, camera info)
- Scene description and object detection

### Cross-Evidence Correlation

- **Entity Matching**: Find same people/organizations across documents, emails, images
- **Timeline Reconstruction**: Combine file dates, email timestamps, EXIF data
- **Pattern Detection**: Identify temporal clusters, suspicious gaps, event sequences
- **Relationship Mapping**: Connect evidence pieces through shared entities
- **v3.1 NEW**: Legal Pattern Detection:
  - **Contradictions**: Identify conflicting statements across evidence (factual, temporal, attribution)
  - **Corroboration**: Find evidence supporting the same claims (weak/moderate/strong)
  - **Evidence Gaps**: Detect missing witnesses, documentation, unexplained absences

### Forensic Integrity

**Content-Addressed Storage**: Files stored by SHA256 hash in `data/storage/`

```
data/storage/
├── raw/sha256=<hash>/
│   └── original.pdf                   # Immutable original file
├── derived/sha256=<hash>/
│   ├── metadata.json                  # File information
│   ├── analysis.v1.json               # AI analysis results
│   ├── chain_of_custody.json          # Complete audit trail
│   └── evidence_bundle.v1.json        # Forensic bundle
└── cases/MY-CASE-2024/
    └── <sha256>.pdf                   # Hard link to original
```

**Why content-addressed storage?**
- **Deduplication**: Same file in multiple cases = analyzed once, stored once
- **Integrity**: SHA256 hash prevents tampering, verifies authenticity
- **Multi-case support**: Evidence can belong to multiple investigations
- **Cost savings**: Reuse AI analysis across cases without re-processing

### Chain of Custody

Every operation is logged with timestamps and actor identification:

```json
{
  "ts": "2025-10-05T14:25:30.123Z",
  "actor": "investigator@firm.com",
  "action": "ingest",
  "note": "Evidence file ingested from data/cases/CASE-2024/document.pdf"
}
```

**Audit trail includes**:
- File ingestion with source path
- AI analysis with model version and parameters
- Case associations and modifications
- Package generation events

---

## CLI Commands Reference

### Complete Pipeline

```bash
# Full workflow: ingest → analyze → correlate → package
evidence-toolkit process-case <directory> --case-id <ID>

# Example
evidence-toolkit process-case data/cases/WORKPLACE-2024 --case-id WORKPLACE-2024
```

### Individual Operations

```bash
# Ingest evidence files
evidence-toolkit ingest <directory> --case-id <ID>

# Analyze specific evidence (requires SHA256 hash from ingest)
evidence-toolkit analyze <sha256> --case-id <ID>

# Run cross-evidence correlation
evidence-toolkit correlate --case-id <ID>

# Generate client package
evidence-toolkit package --case-id <ID> [--include-raw]

# Re-analyze all evidence in a case (useful after model updates)
evidence-toolkit reanalyze --case-id <ID>
```

### Storage Management

```bash
# View storage statistics
evidence-toolkit storage stats

# Clean up orphaned evidence (not in any case)
evidence-toolkit storage cleanup [--dry-run] [--force]

# Prune specific case evidence
evidence-toolkit storage prune --case-id <ID> [--dry-run] [--force]
```

### Case Management

```bash
# List all cases
evidence-toolkit case list [--detailed]

# Show specific case details
evidence-toolkit case show <case-id>

# List evidence in a case
evidence-toolkit case evidence <case-id>
```

### Version Information

```bash
# Show toolkit version
evidence-toolkit version

# Show version with component info
evidence-toolkit --version
```

---

## What Makes This Forensic-Grade?

### Deterministic AI Analysis

- **Temperature = 0**: Same input always produces same output (reproducible)
- **Structured Output**: Pydantic validation ensures schema compliance
- **Confidence Scoring**: Every finding includes confidence metrics (0.0-1.0)
- **Model Tracking**: Analysis records which AI model and version was used

### Legal Compliance

- **Federal Rules of Evidence**: Analysis methodology supports admissibility
- **Expert Testimony Ready**: Complete methodology documentation included
- **GDPR Compliant**: Data processing follows privacy regulations
- **Professional Standards**: Court-ready executive summaries and reports

### Professional Deliverables

Every package includes:
- Executive summary with AI-powered insights
- Individual evidence analysis files (JSON format)
- Cross-evidence correlation results
- Timeline reconstruction with confidence scores
- Evidence catalog with metadata
- Complete methodology documentation
- Original evidence files (optional)

---

## Advanced Usage

### Multi-Case Evidence Reuse

The same evidence file can belong to multiple cases without re-analysis:

```bash
# Analyze evidence once
evidence-toolkit process-case data/cases/CASE-A --case-id CASE-A

# Add same evidence to another case (no re-analysis!)
evidence-toolkit ingest data/cases/CASE-A --case-id CASE-B

# Both packages include the analysis, but AI ran only once
evidence-toolkit package --case-id CASE-A
evidence-toolkit package --case-id CASE-B
```

**Cost savings**: If 5 cases share 10 documents, you pay for 10 analyses instead of 50.

### Domain Configuration

Customize AI analysis prompts for your domain:

```python
# src/evidence_toolkit/domains/legal_config.py (default)
DOCUMENT_ANALYSIS_PROMPT = "You are a forensic document analyzer..."
CRITICAL_RISK_FLAGS = {'retaliation', 'harassment', 'discrimination'}

# Create your own domain configuration
# src/evidence_toolkit/domains/custom_config.py
DOCUMENT_ANALYSIS_PROMPT = "You are analyzing evidence for [your domain]..."
```

**Current domains**:
- `legal_config.py` - Legal evidence analysis (workplace investigations)

**Extensible**: Add corporate, journalism, or research configurations as needed.

### Python API Usage

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers import DocumentAnalyzer, CorrelationAnalyzer
from evidence_toolkit.pipeline import PackageGenerator

# Initialize storage
storage = EvidenceStorage("data/storage")

# Ingest evidence
result = storage.ingest_file(
    file_path="data/cases/MY-CASE/document.pdf",
    case_id="MY-CASE",
    actor="investigator@firm.com"
)

# Analyze document
analyzer = DocumentAnalyzer()
analysis = analyzer.analyze_with_ai(text_content)

# Run correlation analysis
correlator = CorrelationAnalyzer(storage)
correlations = correlator.analyze_case_correlations("MY-CASE")

# Generate package
packager = PackageGenerator(storage)
package = packager.create_client_package("MY-CASE", "data/packages/")
```

---

## Architecture

### Package Structure

```
evidence-toolkit/
├── src/evidence_toolkit/          # Main package (v3.0)
│   ├── core/                      # Storage, models, utilities
│   │   ├── models.py              # 48 Pydantic models (unified)
│   │   ├── storage.py             # Content-addressed storage
│   │   └── utils.py               # Shared utilities
│   ├── analyzers/                 # AI analysis modules
│   │   ├── document.py            # Document + AI analysis
│   │   ├── email.py               # Email threading + analysis
│   │   ├── email_parser.py        # EML file parsing
│   │   ├── image.py               # Vision AI + EXIF
│   │   └── correlation.py         # Cross-evidence correlation
│   ├── pipeline/                  # Processing pipeline
│   │   ├── ingest.py              # Evidence ingestion
│   │   ├── analyze.py             # Analysis orchestration
│   │   ├── summary.py             # Case summary generation
│   │   └── package.py             # Client deliverable creation
│   ├── domains/                   # Domain configurations
│   │   └── legal_config.py        # Legal analysis settings
│   └── cli.py                     # CLI entry point
├── data/                          # Evidence and output
│   ├── cases/                     # Input: Your evidence files
│   ├── storage/                   # Content-addressed evidence
│   └── packages/                  # Output: Client deliverables
└── examples/                      # Sample evidence
    └── sample-case-quickstart/    # Ready-to-use test case
```

### Key Design Principles

**v3.0 Clean Architecture**:
- Single unified package (`src/evidence_toolkit/`)
- All Pydantic validation (48 models in `core/models.py`)
- Content-addressed storage with SHA256 hashing
- Domain-agnostic core (95%) + thin config layer (5%)
- Visible data structure (`data/` in git with .gitkeep)

**Why Pydantic everywhere?**
- Runtime validation prevents corrupt analysis data
- Type safety catches errors during development
- JSON serialization works automatically
- Schema evolution is manageable
- Forensic integrity through validation

---

## Installation & Setup

### Requirements

- **Python 3.12+** (required)
- **OpenAI API key** (required for AI analysis)
- **UV or pip** (package manager)

### Installation

```bash
# Clone repository
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit

# Install with pip
pip install -e .

# Or install with UV (faster)
pip install uv
uv pip install -e .

# Verify installation
evidence-toolkit --version
# Expected: Evidence Toolkit v3.0.0
```

### Configure OpenAI API Key

```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Verify Setup

```bash
# Test with sample case (2-3 minutes)
./quick-start.sh examples/sample-case-quickstart QUICKSTART-TEST

# Check package was created
ls -lh data/packages/QUICKSTART-TEST*.zip

# View executive summary
cat data/packages/QUICKSTART-TEST*/reports/executive_summary.txt
```

---

## Performance & Costs

### Processing Times

| Evidence Count | Processing Time | Notes |
|---------------|-----------------|-------|
| 5 files       | 2-3 minutes     | Mixed: docs, emails, images |
| 20 files      | 6-8 minutes     | Typical small case |
| 50 files      | 15-20 minutes   | Medium investigation |
| 100+ files    | 30-40 minutes   | Large corporate case |

**Factors affecting speed**:
- Image analysis takes longer (Vision API)
- PDF text extraction varies by file size
- Email thread reconstruction is fast
- Correlation scales linearly with evidence count

### OpenAI API Costs (Approximate)

| Operation | Model | Cost per Item |
|-----------|-------|---------------|
| Document analysis | gpt-4.1-mini | $0.001-0.003 |
| Email analysis | gpt-4.1-mini | $0.002-0.005 |
| Image analysis | gpt-4-vision | $0.003-0.008 |
| Executive summary | gpt-4.1-mini | $0.01-0.02 |

**Example case costs**:
- 5-piece test case: ~$0.02-0.04
- 20-piece investigation: ~$0.10-0.30
- 50-piece corporate case: ~$0.30-0.80

**Cost optimization**: Content-addressed storage means duplicate evidence is analyzed once and reused across cases.

---

## Troubleshooting

### "OPENAI_API_KEY not set"

```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set for current session
export OPENAI_API_KEY="your-key"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
```

### "No evidence found for case"

```bash
# Verify case directory exists
ls -la data/cases/MY-CASE

# Check evidence was ingested
evidence-toolkit case show MY-CASE

# Re-ingest if needed
evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE
```

### "Analysis failed" or "AI analysis disabled"

1. Verify OpenAI API key is set and valid
2. Check internet connection for API access
3. Review error messages for specific issues
4. Check OpenAI API status: https://status.openai.com/

### "Package generation failed"

```bash
# Ensure correlation ran successfully
evidence-toolkit correlate --case-id MY-CASE

# Check output directory permissions
ls -ld data/packages/

# Try again with verbose output
evidence-toolkit package --case-id MY-CASE
```

---

## Documentation

### User Guides
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute walkthrough (start here!)
- **[Architecture Documentation](V3_ARCHITECTURE.md)** - Complete v3.0 design
- **[Quick Start Example](examples/QUICKSTART_EXAMPLE.md)** - Testing guide

### Development
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[v3.0 Complete](V3_COMPLETE.md)** - Refactor summary and achievements
- **[Developer Reference](CLAUDE.md)** - Quick reference for developers

---

## Support & Community

### Getting Help
- **GitHub Issues**: https://github.com/evidence-toolkit/evidence-toolkit/issues
- **Documentation**: Review guides above
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) for common workflows

### Contributing
Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code standards
- Pull request process
- Domain configuration examples

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Version

**Current**: v3.3.0 (Released October 2025)

**What's new in v3.3** (Maximum Data Utilization):
- **Phase A**: Quoted statement aggregation by person, communication pattern risk assessment (95% data utilization)
- **Phase B+**: Semantic timeline events, relationship network extraction, image OCR aggregation (98% data utilization)
- **Report Restructuring**: Insights-first layout (forensic summary → key findings → legal implications → actions)
- **Zero Additional Cost**: All enhancements extract existing AI-generated data without new API calls

**v3.2 Features**:
- **AI Entity Resolution**: Context-aware name matching with `--ai-resolve` flag
- **Case Type Support**: Domain-specific prompts (generic, workplace, contract) via `--case-type`
- **Chunked Summaries**: Map-reduce pattern handles 50+ evidence pieces efficiently

**v3.1 AI Enhancements**:
- **Legal Pattern Detection**: AI-powered contradiction, corroboration, and evidence gap analysis
- **Power Dynamics Analysis**: Email participant dominance/deference scoring for workplace investigations
- **Enhanced Entity Extraction**: Relationship tracking, verbatim quotes, event association

**v3.0 Foundation**:
- Single unified package architecture (`src/evidence_toolkit/`)
- All Pydantic validation (32 models consolidated)
- 64% smaller CLI with pipeline delegation
- Visible data structure (`data/` directory)

See [V3_COMPLETE.md](V3_COMPLETE.md) for v3.0 details and [docs/V3.3_SESSION_SUMMARY.md](docs/V3.3_SESSION_SUMMARY.md) for v3.3 development history.

---

*Built for professional legal evidence analysis with forensic integrity and chain of custody tracking.*
