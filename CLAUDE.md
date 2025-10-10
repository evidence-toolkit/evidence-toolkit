# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Do not make wild claims about the project or what it does. 
---

## Evidence Toolkit v4.0 - Generators Architecture

**Version**: 4.0.0 | **Updated**: 2025-10-10

---

## ⚡ Quick Start

### Project Structure
```
evidence-toolkit/
├── src/evidence_toolkit/       # Main package (v4.0)
│   ├── core/                   # Models, storage, utilities
│   ├── analyzers/              # AI analysis modules
│   ├── pipeline/               # Processing pipeline
│   ├── generators/             # [NEW v4.0] Report generators (9 generators, 8 reports)
│   ├── domains/                # Domain configurations (case types, forensic prompts)
│   └── cli.py                  # CLI entry point
├── data/                       # Visible data directories
│   ├── cases/                  # Input: Your evidence files
│   ├── storage/                # Content-addressed evidence
│   └── packages/               # Output: Client deliverables
└── data_backup_*/              # Test data backups (gitignored)
```

### Always Use UV
```bash
# This project uses UV for speed
uv run evidence-toolkit --help
uv pip install -e .
uv sync
```

**Important**: We ALWAYS use `uv` commands run from root with the root `.venv`.

---

## Architecture Overview

### Core Principles
1. **Single Package**: `src/evidence_toolkit/` - no nesting
2. **All Pydantic**: Consistent validation everywhere (48 models)
3. **Visible Data**: `data/` directory visible in git
4. **AI-Powered**: Documents, emails, images all analyzed with OpenAI Responses API

### Content-Addressed Storage
Evidence is stored by SHA256 hash for automatic deduplication:
```
data/storage/
├── raw/sha256=<hash>/original.pdf
├── derived/sha256=<hash>/
│   ├── metadata.json
│   ├── analysis.v1.json
│   └── chain_of_custody.json
└── cases/<case-id>/
    └── <sha256>.pdf  # Hard link
```

---

## Key v3.1 Changes

**v3.0 Foundation**:
- Models: 5 files → 1 unified `core/models.py` (ALL Pydantic!)
- CLI: smaller, delegates to pipeline
- Validation: CorrelationAnalysis now Pydantic (was dataclass)
- Structure: `src/evidence_toolkit/` (was `document-evidence-analyzer/`)

**v3.1 AI Enhancements**:
- Legal pattern detection: contradictions, corroboration, evidence gaps
- Power dynamics analysis: deference scoring in email threads
- Enhanced entity extraction: relationships, quoted text, associated events
- Temporal analysis: sequences, timeline gaps

**v3.2 Features**:
- **AI Entity Resolution**: Context-aware name matching ("John" → "John Smith") using `--ai-resolve`
- **Case Type Support**: Domain-specific prompts (generic, workplace, contract) via `--case-type`
- **Chunked Summaries**: Map-reduce pattern handles 50+ evidence pieces efficiently
- **Video/Audio Ingestion**: Basic ingestion support (analysis coming in future version)

---

## Common Commands

```bash
# Full pipeline (ingest → analyze → correlate → package)
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# v3.2: Workplace case with AI entity resolution
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE \
  --case-type workplace --ai-resolve

# Re-analyze with latest AI models (v3.1+ features)
uv run evidence-toolkit reanalyze --case-id MY-CASE

# Individual steps
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE
uv run evidence-toolkit correlate --case-id MY-CASE --ai-resolve  # v3.2: AI entity matching
uv run evidence-toolkit package --case-id MY-CASE --case-type workplace  # v3.2: Domain-specific
```

---

## Import Patterns

### ✅ v3.1 Imports (use these)
```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    UnifiedAnalysis, CorrelationAnalysis,
    LegalPatternAnalysis, EntityMatchResult
)
from evidence_toolkit.analyzers import DocumentAnalyzer, CorrelationAnalyzer
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.domains import legal_config
```

### ❌ v2.0 Imports (avoid these)
```python
# DON'T USE
from document_analyzer.evidence_manager import EvidenceManager
from models.cross_analysis_models import CrossAnalysisBundle
```

---

## v3.1 Features

### Legal Pattern Detection
AI analyzes cross-evidence patterns for:
- **Contradictions**: Conflicting statements (factual, temporal, attribution)
- **Corroboration**: Evidence supporting same claims (weak/moderate/strong)
- **Evidence Gaps**: Missing witnesses, documentation, communications

### Power Dynamics Analysis
Email threads analyzed for:
- **Deference scoring**: 0.0=dominant, 0.5=neutral, 1.0=deferential
- **Dominant topics**: Subjects each participant controlled
- **Authority levels**: Executive/management/employee/external

---

## v3.2 Features

### AI Entity Resolution (`--ai-resolve`)
Context-aware name matching using OpenAI:
- Handles informal vs formal names ("Paul" vs "Paul Boucherat")
- Resolves nicknames and abbreviations ("Bob" vs "Robert Smith")
- Uses organization, role, email domain for disambiguation
- Conservative bias for forensic accuracy (false negatives > false positives)
- Cost: ~$0.01-0.05 per case, ~10-20s processing time

### Case Type Support (`--case-type`)
Domain-specific executive summary prompts:
- **`generic`**: General legal matters (default)
- **`workplace`/`employment`**: Employment law focus (ACAS compliance, tribunal risk, etc.)
- **`contract`**: Commercial dispute focus
- Tailored analysis for each case type
- See [docs/CASE_TYPES.md](docs/CASE_TYPES.md)

### Chunked Summaries
Map-reduce pattern for large cases:
- Automatically activates for 50+ evidence pieces
- Breaks evidence into 30-item chunks
- Generates chunk summaries, then combines for final executive summary
- Prevents OpenAI context overflow
- Enables cases with 100+ evidence pieces

---

## v3.3 Features - Maximum Data Utilization

**Goal:** Maximize AI-generated insights reaching client deliverables (65% → 98% data utilization)

### Phase A: Aggregated Pattern Data (95% utilization)
**Quoted Statements Extraction:**
- Extracts direct quotes from documents with speaker attribution
- Sentiment analysis per person (professional/hostile/neutral)
- Risk indicator flagging (threats, admissions, policy violations)
- Top 5 most relevant speakers with statement counts

**Communication Pattern Analysis:**
- Email thread pattern classification (professional/escalating/hostile/retaliatory)
- Risk level assessment across email corpus
- Pattern distribution metrics for trend analysis

### Phase B: Hidden Evidence Data (98% utilization)
**Image OCR Aggregation:**
- Extracts detected text from image evidence
- Groups by evidence value (high/medium/low)
- Highlights images with people present and visible timestamps
- Sample OCR extractions in reports

**Relationship Network Extraction:**
- Parses entity relationships for escalation chains
- Email communication mapping (sender → recipient)
- Identifies key players by connection count
- Network visualization data for power dynamics

**Semantic Timeline Events:**
- Extracts date entities with associated event descriptions
- Creates timeline entries from narrative documents
- Multiple date format parsing (ISO, UK, US formats)
- Enriches timeline beyond just document timestamps

### Phase B+: Forensic Display Restructuring
**Executive-First Report Layout:**
- 🔍 **Executive Summary**: Client-ready strategic narrative (enhanced AI analysis)
- 💡 **Key Findings**: 3-5 bullet-point discoveries with evidence citations
- ⚖️ **Legal Risk Assessment**: Tribunal probability %, financial exposure estimates (enhanced)
- 📋 **Forensic Legal Analysis**:
  - Legal implications: 4-5 specific statutory risks (PIDA, vicarious liability, trust breach)
  - Strategic recommendations: 5 forensic investigation/defense actions
- 🎯 **Recommended Actions**: Urgent client-facing deadlines (enhanced)

**Dual-Layer Analysis:**
- **Forensic Layer** (AI Call #1): Evidence-based legal foundation, statutory citations, investigation strategy
- **Enhanced Layer** (AI Call #2): Client-ready risk quantification, tribunal %, settlement ranges
- Both layers displayed separately to provide complementary perspectives

**Report Structure:**
- Insights first (35-45% of report) - strategic analysis
- Supporting documentation last (55-65% of report) - appendix
- Transforms "glorified appendix" → executive-ready deliverable

**Data Utilization Achievement:**
- v3.1: 65% (forensic analysis generated but not displayed)
- v3.2: 80% (tribunal probability, financial exposure added)
- v3.3 Phase A: 95% (quoted statements, patterns extracted & displayed)
- v3.3 Phase B: 98% (image OCR, relationships, semantic timeline)
- v3.3 Phase B+: 100% (ALL forensic + enhanced data now displayed in reports)

**Zero Additional Cost:**
- All v3.3 features use existing v3.1 AI analysis data
- Pure display layer enhancements
- No new API calls required

---

## v4.0 Features - Generators Architecture

**Goal:** Transform toolkit from basic analysis to premium forensic platform with 8 professional reports

### Professional Report Generators (v3.4 Phases 1-3)

Evidence Toolkit v4.0 automatically generates **8 professional forensic reports** from a single case:

1. **Executive Summary** - AI-generated case overview (v3.3 baseline, insights-first)
2. **Forensic Legal Opinion** - Statutory risk analysis and legal implications
3. **Financial Risk Assessment** - Tribunal probability and settlement range estimates
4. **Legal Patterns Analysis** - Contradictions, corroboration, evidence gaps
5. **Timeline Reconstruction** - Chronological event mapping with gap analysis
6. **Quoted Statements Analysis** - Person-by-person breakdown with sentiment
7. **Relationship Network Analysis** - Entity connections and key player identification
8. **Power Dynamics Analysis** - Email authority hierarchy (conditional on email evidence)
9. **Image OCR Analysis** - Text extraction from visual evidence (conditional on images)

### Architecture: Template Method Pattern

**Base Class**: `BaseReportGenerator` (`generators/base.py`)
- Provides common formatting utilities (`_build_header`, `_truncate_sha`, etc.)
- Defines template methods: `has_data()`, `generate()`, `get_report_filename()`
- Each generator inherits and implements required methods

**9 Specialized Generators** (3,591 lines total):
```
src/evidence_toolkit/generators/
├── base.py                      # 255 lines - Abstract base class
├── forensic_legal.py            # 390 lines - Legal opinion
├── financial_risk.py            # 503 lines - Tribunal/settlement
├── legal_patterns.py            # 565 lines - Contradictions/gaps
├── timeline.py                  # 459 lines - Chronological events
├── quoted_statements.py         # 448 lines - Speaker analysis
├── relationship_network.py      # 402 lines - Entity connections
├── power_dynamics.py            # 294 lines - Email hierarchy
└── image_ocr.py                 # 275 lines - Visual text extraction
```

### Import Patterns (v4.0)

```python
# Access generators
from evidence_toolkit.generators import (
    ForensicLegalOpinionGenerator,
    FinancialRiskAssessmentGenerator,
    LegalPatternsGenerator,
    TimelineGenerator,
    QuotedStatementsGenerator,
    RelationshipNetworkGenerator,
    PowerDynamicsGenerator,
    ImageOCRGenerator,
)

# Use in package generation
generator = ForensicLegalOpinionGenerator(case_summary, reports_dir)
if generator.has_data():
    report_path = generator.generate()
```

### Data Access Patterns (CRITICAL!)

**Dictionary fields** (overall_assessment):
```python
# Use _safe_get() for dict access
forensic_summary = self._safe_get('_forensic_summary', '')
tribunal_prob = self._safe_get('tribunal_probability', 0)
```

**Pydantic model fields** (correlation_result):
```python
# Access Pydantic attributes directly (NOT with .get())
corr = self.case_summary.correlation_result
legal_patterns = corr.legal_patterns  # LegalPatternAnalysis model
contradictions = legal_patterns.contradictions  # List[Contradiction]

# NEVER use .get() on Pydantic models!
# ❌ legal_patterns.get('contradictions')  # AttributeError!
# ✅ legal_patterns.contradictions          # Correct!
```

### Value Transformation

**Client Deliverable Value**:
- v3.3: £500 (single executive summary)
- v4.0: **£4,500** (8 professional forensic reports)
- **8-9x increase** in client deliverable value

**Data Utilization**:
- v3.3: 98% (maximum extraction from AI data)
- v4.0: 90% (report-focused subset, all major insights surfaced)

**Additional Cost**:
- **Zero** - All generators reuse existing v3.3 AI analysis data
- Processing overhead: +5-10 seconds per case (generator execution only)

### Conditional Generation

Generators check `has_data()` before generating:
- **Power Dynamics**: Requires email evidence → skipped for document-only cases
- **Image OCR**: Requires images with detected text → skipped otherwise
- User sees clean output: `⊘ Skipped PowerDynamicsGenerator: Insufficient data`

---

## Documentation

- **[README.md](README.md)** - Getting started
- **[CHANGELOG.md](CHANGELOG.md)** - Complete version history (v3.0-v4.0)
- **[docs/README.md](docs/README.md)** - Central documentation navigation hub
- **[docs/V4_ARCHITECTURE.md](docs/V4_ARCHITECTURE.md)** - Complete v4.0 architecture
- **[docs/V4_RELEASE_NOTES.md](docs/V4_RELEASE_NOTES.md)** - v4.0 release documentation
- **[docs/module-docs/GENERATORS.md](docs/module-docs/GENERATORS.md)** - Generators architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **docs/archive/** - Historical documentation (v3.0, v3.3 session notes)
