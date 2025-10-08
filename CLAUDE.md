# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Evidence Toolkit v3.3 - Maximum Data Utilization

**Version**: 3.3.0 | **Updated**: 2025-10-08

---

## ⚡ Quick Start

### Project Structure
```
evidence-toolkit/
├── src/evidence_toolkit/       # Main package (v3.3)
│   ├── core/                   # Models, storage, utilities
│   ├── analyzers/              # AI analysis modules
│   ├── pipeline/               # Processing pipeline
│   ├── domains/                # Domain configurations (v3.3: case types, forensic prompts)
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
- 🔍 **Forensic Summary**: 1,280-char detailed narrative analysis
- 💡 **Key Findings**: 3-5 bullet-point discoveries with evidence citations
- ⚖️ **Legal Implications**: 5 specific risk areas for case strategy
- 🎯 **Recommended Actions**: 5 strategic guidance items

**Report Structure:**
- Insights first (35-45% of report) - strategic analysis
- Supporting documentation last (55-65% of report) - appendix
- Transforms "glorified appendix" → executive-ready deliverable

**Data Utilization Achievement:**
- v3.1: 65% (forensic analysis generated but not displayed)
- v3.2: 80% (tribunal probability, financial exposure added)
- v3.3 Phase A: 95% (quoted statements, patterns extracted & displayed)
- v3.3 Phase B: 98% (image OCR, relationships, semantic timeline)
- v3.3 Phase B+: 98% (forensic content now prominently displayed)

**Zero Additional Cost:**
- All v3.3 features use existing v3.1 AI analysis data
- Pure display layer enhancements
- No new API calls required

---

## Documentation

- **[README.md](README.md)** - Getting started
- **[V3_ARCHITECTURE.md](V3_ARCHITECTURE.md)** - Complete architecture
- **[V3_COMPLETE.md](V3_COMPLETE.md)** - v3.0 refactor summary
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **docs/module-docs/** - Component documentation
