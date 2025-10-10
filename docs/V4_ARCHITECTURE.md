# Evidence Toolkit v4.0 - Complete Architecture

**Version:** 4.0.0 | **Updated:** 2025-10-10
**Evolution:** v3.0 Clean Architecture → v3.1 AI Enhancements → v3.2 Intelligence → v3.3 Max Utilization → v4.0 Generators

---

## Executive Summary

Evidence Toolkit v4.0 is a professional forensic evidence analysis platform that transforms raw evidence files (documents, emails, images) into comprehensive legal-grade packages with **8 professional forensic reports**.

**Core Capabilities**:
- Multi-modal AI analysis (documents, images, emails) using OpenAI GPT-4o/GPT-4o-mini
- Content-addressed storage with automatic deduplication and chain of custody
- Cross-evidence correlation with legal pattern detection
- **NEW v4.0**: 9 specialized report generators producing 8 professional reports automatically
- 90% data utilization (extracting maximum value from AI analysis)
- £4,500 client deliverable value (8-9x increase from v3.3)

**Architecture Style**: Clean layered architecture with modular generators (Template Method pattern)

---

## Design Principles

### Core Principles (v3.0 Foundation)
1. **Single Package**: `src/evidence_toolkit/` - Flat, easy to navigate
2. **All Pydantic**: Consistent validation everywhere (48 models)
3. **Visible Data**: `data/` directory visible in git with `.gitkeep`
4. **Content-Addressed Storage**: SHA256-based deduplication
5. **Forensic Integrity**: Complete chain of custody tracking

### v4.0 Enhancements
6. **Modular Generators**: Specialized report generators following Template Method pattern
7. **Maximum Data Utilization**: Extract 90%+ value from AI-generated insights
8. **Zero Additional Costs**: Reuse v3.3 analysis data for all reports
9. **Conditional Generation**: Reports generated only when data available
10. **Professional Output**: Tribunal-ready Markdown reports

---

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Evidence Toolkit v4.0                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Input Layer          Pipeline Stages        Output Layer    │
│  ────────────         ────────────────       ────────────    │
│                                                               │
│  Evidence Files  →  1. INGEST          →  Client Package     │
│  (.pdf, .eml,       (Content-Addressed     (.zip file)       │
│   .jpg, etc.)        Storage)                                │
│                        ↓                                      │
│                     2. ANALYZE          →  8 Professional    │
│                       (AI-Powered           Reports:         │
│                        Type-Specific        - Executive      │
│                        Analysis)            - Forensic       │
│                        ↓                    - Financial      │
│                     3. CORRELATE        →  - Legal           │
│                       (Cross-Evidence       - Timeline       │
│                        Entity Matching,     - Statements     │
│                        Legal Patterns)      - Network        │
│                        ↓                    - Power          │
│                     4. PACKAGE          →                    │
│                       (v4.0 Generators  →  Chain of          │
│                        Architecture)        Custody          │
│                                             Tracking          │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure (v4.0)

```
evidence-toolkit/
├── src/
│   └── evidence_toolkit/           # Main package
│       ├── __init__.py              # Package exports
│       │
│       ├── core/                    # Core infrastructure
│       │   ├── models.py            # 48 Pydantic models (unified)
│       │   ├── storage.py           # Content-addressed storage
│       │   └── utils.py             # Shared utilities
│       │
│       ├── analyzers/               # AI analysis modules
│       │   ├── document.py          # Document AI (GPT-4o-mini)
│       │   ├── image.py             # Image AI (GPT-4o Vision)
│       │   ├── email.py             # Email AI (GPT-4o-mini)
│       │   ├── email_parser.py      # Email parsing utilities
│       │   └── correlation.py       # Cross-evidence analysis
│       │
│       ├── pipeline/                # Processing pipeline
│       │   ├── ingest.py            # Evidence ingestion
│       │   ├── analyze.py           # Analysis orchestration
│       │   ├── summary.py           # Correlation & summarization
│       │   ├── package.py           # Package generation (v4.0: uses generators)
│       │   └── batch.py             # Batch processing
│       │
│       ├── generators/              # [NEW v4.0] Report generators
│       │   ├── base.py              # BaseReportGenerator (Template Method)
│       │   ├── forensic_legal.py    # Forensic legal opinion
│       │   ├── financial_risk.py    # Financial risk assessment
│       │   ├── legal_patterns.py    # Legal patterns analysis
│       │   ├── timeline.py          # Timeline reconstruction
│       │   ├── quoted_statements.py # Quoted statements analysis
│       │   ├── relationship_network.py # Relationship network analysis
│       │   ├── power_dynamics.py    # Power dynamics analysis
│       │   └── image_ocr.py         # Image OCR aggregation
│       │
│       ├── domains/                 # Domain configurations
│       │   └── legal_config.py      # AI prompts, risk flags, configs
│       │
│       └── cli.py                   # CLI entry point (delegates to pipeline)
│
├── data/                            # Evidence storage (VISIBLE)
│   ├── cases/                       # Input: Evidence files by case
│   ├── storage/                     # Content-addressed storage
│   │   ├── raw/                     # Original files (sha256=<hash>/)
│   │   ├── derived/                 # Analysis results (analysis.v1.json)
│   │   └── cases/                   # Case-to-evidence mapping (hard links)
│   └── packages/                    # Output: Client deliverable ZIPs
│
├── docs/                            # Documentation (v4.0: reorganized)
│   ├── README.md                    # [NEW] Central docs index
│   ├── V4_ARCHITECTURE.md           # [NEW] This file
│   ├── V4_RELEASE_NOTES.md          # [NEW] v4.0 release notes
│   ├── module-docs/                 # Module documentation
│   ├── pipeline/                    # Pipeline stage docs
│   ├── api/                         # API reference
│   └── archive/                     # [NEW] Historical docs
│
├── CHANGELOG.md                     # [NEW] Version history
├── pyproject.toml                   # Package configuration
├── README.md                        # Project overview
└── CLAUDE.md                        # AI assistant guidance
```

---

## Component Architecture

### Core Components (`core/`)

#### Models (`models.py`) - 48 Pydantic Models

**Categories**:
1. **Base Types** (3 models):
   - `EvidenceType` - Enum for evidence types
   - `FileMetadata` - File properties
   - `ChainOfCustodyEvent` - Audit trail events

2. **AI Analysis Results** (15 models):
   - `DocumentEntity`, `DocumentAnalysisStructured` - Document AI
   - `ImageAnalysisStructured`, `ImageObject` - Image AI (Vision)
   - `EmailParticipant`, `EmailThreadAnalysis` - Email AI
   - `UnifiedAnalysis` - Multi-modal container

3. **Forensic Bundles** (8 models):
   - `EvidenceBundle` - Complete evidence package
   - `EvidenceSummary` - High-level summary
   - `CaseSummary` - Complete case analysis

4. **Cross-Evidence Analysis** (12 models):
   - `CorrelationAnalysis` - Cross-evidence patterns
   - `LegalPatternAnalysis` - Contradictions, corroboration
   - `CorrelatedEntity` - Entity matching results
   - `TimelineEvent` - Temporal events
   - `Contradiction`, `Corroboration`, `EvidenceGap` - Legal patterns

5. **Operation Results** (10 models):
   - `IngestionResult` - File ingestion
   - `AnalysisResult` - Analysis operations
   - `ExecutiveSummaryResponse` - AI summary (v3.2+)

**Key Features**:
- All models use Pydantic v2 for runtime validation
- Schema versioning for forensic compliance
- Confidence scoring on all AI-generated fields
- Model tracking (records which AI model generated data)

#### Storage (`storage.py`) - Content-Addressed System

**Class**: `EvidenceStorage`

**Key Methods**:
```python
def store_evidence(self, file_path: Path, case_id: str) -> str:
    """Store evidence with SHA256 hash, return hash."""

def get_evidence_path(self, sha256: str) -> Path:
    """Retrieve original evidence by hash."""

def store_analysis(self, sha256: str, analysis: UnifiedAnalysis):
    """Store analysis results for evidence."""

def get_analysis(self, sha256: str) -> UnifiedAnalysis:
    """Retrieve analysis results."""

def get_case_evidence(self, case_id: str) -> List[str]:
    """List all evidence SHA256s for a case."""

def add_chain_of_custody_event(self, sha256: str, event: ChainOfCustodyEvent):
    """Add audit trail event."""
```

**Storage Structure**:
```
data/storage/
├── raw/sha256=<hash>/
│   └── original.{ext}               # Immutable original file
├── derived/sha256=<hash>/
│   ├── metadata.json                # FileMetadata
│   ├── analysis.v1.json             # UnifiedAnalysis
│   └── chain_of_custody.json        # List[ChainOfCustodyEvent]
└── cases/<case-id>/
    └── <sha256>.{ext}               # Hard link to raw/
```

**Benefits**:
- Automatic deduplication (same file analyzed once)
- Multi-case evidence reuse (90%+ cost savings)
- Immutable originals (forensic integrity)
- Complete audit trail (chain of custody)

---

### Analyzers (`analyzers/`)

#### Document Analyzer (`document.py`)

**AI Model**: `gpt-4o-mini` (temperature=0)
**Prompt**: `DOCUMENT_ANALYSIS_PROMPT` from `legal_config.py`

**Analysis Output** (`DocumentAnalysisStructured`):
- Entity extraction (persons, organizations, dates, legal terms)
- Sentiment analysis (professional/neutral/hostile)
- Key topics identification
- Legal significance assessment
- Risk flags (threats, policy violations, etc.)
- **v3.1**: Relationships, quoted text, associated events

#### Image Analyzer (`image.py`)

**AI Model**: `gpt-4o` Vision (temperature=0)
**Prompt**: `IMAGE_ANALYSIS_PROMPT` from `legal_config.py`

**Analysis Output** (`ImageAnalysisStructured`):
- Scene description
- Object detection
- OCR text extraction
- People present (count, description)
- Evidence value assessment (high/medium/low)
- Forensic recommendations

#### Email Analyzer (`email.py`)

**AI Model**: `gpt-4o-mini` (temperature=0)
**Prompt**: `EMAIL_ANALYSIS_PROMPT` from `legal_config.py`

**Analysis Output** (`EmailThreadAnalysis`):
- Participant analysis with authority levels
- **v3.1**: Deference scoring (power dynamics)
- **v3.1**: Communication pattern classification
- Escalation detection
- Key topics per participant
- Timeline of email sequence

#### Correlation Analyzer (`correlation.py`)

**AI Model**: `gpt-4o-2024-08-06` (temperature=0)
**Prompt**: `CORRELATION_PROMPT` from `legal_config.py`

**Analysis Output** (`CorrelationAnalysis`):
- Cross-evidence entity matching
- Timeline reconstruction
- **v3.1**: Legal pattern detection (contradictions, corroboration, gaps)
- **v3.3**: Semantic timeline events
- **v3.3**: Relationship network extraction

---

### Pipeline (`pipeline/`)

#### Stage 1: Ingestion (`ingest.py`)

**Process**:
```
Input Files → SHA256 Hashing → Metadata Extraction → Storage
```

**Functions**:
- `ingest_evidence(path, storage, case_id)` - Single file
- `ingest_directory(path, storage, case_id)` - Batch ingestion
- `ingest_path(path, storage, case_id)` - Smart router

**Output**: `List[IngestionResult]`

#### Stage 2: Analysis (`analyze.py`)

**Process**:
```
SHA256 → Type Detection → AI Analysis → Label Generation → Storage
```

**Type Routing**:
- `.txt`, `.pdf` (text) → DocumentAnalyzer
- `.jpg`, `.png`, `.pdf` (scanned) → ImageAnalyzer (Vision)
- `.eml`, `.msg`, `.mbox` → EmailAnalyzer
- `.mp4`, `.mov`, `.mp3`, `.wav` → Basic ingestion (analysis pending)

**Function**: `analyze_evidence(sha256, storage, openai_client, case_id)`

**Output**: `UnifiedAnalysis` (stored in `data/storage/derived/`)

#### Stage 3: Correlation & Summary (`summary.py`)

**Process**:
```
Case ID → Load All Evidence → Entity Matching → Timeline → Legal Patterns → AI Summary
```

**Class**: `SummaryGenerator`

**Key Methods**:
```python
def generate_case_summary(self, case_id: str, ai_summary: bool, ai_resolve: bool) -> CaseSummary:
    """Generate complete case summary with correlation."""

def _calculate_overall_assessment(self, ...) -> Dict[str, Any]:
    """Aggregate data for generators (v3.3/v4.0)."""

# v3.3 Extraction Methods (feed generators):
def _extract_quoted_statements(self, ...)         # Speaker analysis
def _analyze_communication_patterns(self, ...)    # Email risk
def _extract_relationship_network(self, ...)      # Entity connections
def _extract_image_ocr_text(self, ...)            # Visual evidence text
def _extract_semantic_timeline(self, ...)         # Timeline events
def _extract_power_dynamics(self, ...)            # Email hierarchy
```

**Features**:
- **Chunked Summaries** (v3.2): Map-reduce for 50+ evidence pieces
- **AI Entity Resolution** (v3.2): Context-aware name matching (`--ai-resolve`)
- **Case Type Support** (v3.2): Domain-specific prompts (`--case-type`)
- **90% Data Utilization** (v3.3+): Comprehensive extraction methods

**Output**: `CaseSummary` with `overall_assessment` dict (feeds generators)

#### Stage 4: Package Generation (`package.py`)

**Process**:
```
Case Summary → Report Generation (v4.0 Generators) → Component Assembly → ZIP Creation
```

**Class**: `PackageGenerator`

**v4.0 Generator Integration**:
```python
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

# In create_client_package():
for generator_class in [
    ForensicLegalOpinionGenerator,
    FinancialRiskAssessmentGenerator,
    # ... all 8 generators
]:
    generator = generator_class(case_summary, reports_dir)
    if generator.has_data():
        report_path = generator.generate()
        print(f"✓ Generated: {report_path.name}")
```

**Package Structure**:
```
<case-id>_analysis_package_<timestamp>.zip
├── reports/
│   ├── executive_summary.txt            # v3.3 baseline
│   ├── forensic_legal_opinion.md        # [NEW v4.0]
│   ├── financial_risk_assessment.md     # [NEW v4.0]
│   ├── legal_patterns_analysis.md       # [NEW v4.0]
│   ├── timeline_reconstruction.md       # [NEW v4.0]
│   ├── quoted_statements_analysis.md    # [NEW v4.0]
│   ├── relationship_network_analysis.md # [NEW v4.0]
│   ├── power_dynamics_analysis.md       # [NEW v4.0]
│   └── image_ocr_analysis.md            # [NEW v4.0] (conditional)
├── analysis/
│   ├── case_analysis.json
│   └── [individual evidence analyses]
├── correlations/
│   └── correlation_analysis.json
├── evidence_catalog/
│   └── evidence_catalog.json
└── raw_evidence/                         # Optional
    └── [original files]
```

---

## v4.0 Generators Architecture

### Design Pattern: Template Method

**Base Class**: `BaseReportGenerator` (`generators/base.py`)

```python
class BaseReportGenerator(ABC):
    """Abstract base for all forensic report generators."""

    def __init__(self, case_summary: CaseSummary, output_dir: Path):
        self.case_summary = case_summary
        self.output_dir = output_dir

    # Template methods (implemented by subclasses)
    @abstractmethod
    def get_report_filename(self) -> str: ...

    @abstractmethod
    def get_report_title(self) -> str: ...

    @abstractmethod
    def has_data(self) -> bool: ...

    @abstractmethod
    def generate(self) -> Path: ...

    # Helper methods (available to all generators)
    def _build_header(self, subtitle: str) -> str: ...
    def _truncate_sha(self, sha256: str) -> str: ...
    def _safe_get(self, key: str, default: Any) -> Any: ...
    def _format_list_items(self, items: List[str]) -> str: ...
```

### Generator Implementation Pattern

**Phase 1 Generators** (Dict access):
```python
class ForensicLegalOpinionGenerator(BaseReportGenerator):
    def has_data(self) -> bool:
        forensic_summary = self._safe_get('_forensic_summary', '')
        return bool(forensic_summary)

    def generate(self) -> Path:
        # Access overall_assessment dictionary
        forensic_summary = self._safe_get('_forensic_summary', '')
        risk_assessment = self._safe_get('_forensic_risk_assessment', 'unknown')

        # Build Markdown report
        content = self._build_header(subtitle="Legal Risk Analysis")
        content += self._build_legal_opinion_section(...)

        # Write to file
        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')
        return report_path
```

**Phase 2 Generators** (Pydantic model access):
```python
class LegalPatternsGenerator(BaseReportGenerator):
    def has_data(self) -> bool:
        corr = self.case_summary.correlation_result
        return bool(corr.legal_patterns.contradictions or
                   corr.legal_patterns.corroboration_links)

    def generate(self) -> Path:
        # Access Pydantic model attributes directly
        corr = self.case_summary.correlation_result
        legal_patterns = corr.legal_patterns

        # Iterate over Pydantic model lists
        for contradiction in legal_patterns.contradictions:
            severity = contradiction.severity
            statement_1 = contradiction.statement_1
            # ... build report content
```

### All 9 Generators (v4.0)

| Generator | Phase | Lines | Data Source | Report Output |
|-----------|-------|-------|-------------|---------------|
| `forensic_legal.py` | 1 | 390 | `_forensic_*` (dict) | forensic_legal_opinion.md |
| `financial_risk.py` | 1 | 503 | `tribunal_probability` (dict) | financial_risk_assessment.md |
| `legal_patterns.py` | 2 | 565 | `correlation_result.legal_patterns` | legal_patterns_analysis.md |
| `timeline.py` | 2 | 459 | `correlation_result.timeline_events` | timeline_reconstruction.md |
| `quoted_statements.py` | 2 | 448 | `quoted_statements` (dict) | quoted_statements_analysis.md |
| `relationship_network.py` | 3 | 402 | `relationship_network` (dict) | relationship_network_analysis.md |
| `power_dynamics.py` | 3 | 294 | `power_dynamics` (dict) | power_dynamics_analysis.md |
| `image_ocr.py` | 3 | 275 | `image_ocr` (dict) | image_ocr_analysis.md |
| `base.py` | - | 255 | N/A | Abstract base class |

**Total**: 3,591 lines of generator code

### Generator Quality Standards

All generators produce Markdown reports with:
1. **Header**: Title, case ID, timestamp, evidence count
2. **Executive Summary**: 2-3 paragraphs of high-level findings
3. **Detailed Sections**: Organized by topic with H2 headers
4. **Tables**: For structured data (contradictions, timeline events, etc.)
5. **Evidence Citations**: Truncated SHA256s for readability (`abc12345`)
6. **Methodology**: How analysis was performed (optional)

### Conditional Generation

Generators implement `has_data()` to gracefully skip when data unavailable:

```python
# Example: Power Dynamics (requires email evidence)
def has_data(self) -> bool:
    power_data = self._safe_get('power_dynamics', {})
    participants = power_data.get('top_participants', [])
    return len(participants) > 0

# Output when skipped:
# ⊘ Skipped PowerDynamicsGenerator: Insufficient data
```

**Benefits**:
- Clean user experience (no errors)
- Conditional reports based on evidence types
- Example: Email-only case skips image OCR report

---

## Version Evolution

### v3.0 (October 5, 2025) - Clean Architecture
**Focus**: Eliminate complexity while preserving functionality

**Key Changes**:
- Single flat package (`src/evidence_toolkit/`)
- All models unified in `core/models.py` (48 Pydantic models)
- Visible data directories (`data/` with `.gitkeep`)
- CLI delegates to pipeline modules
- Validation gap fixed (correlation now Pydantic)

**Impact**:
- 64% smaller CLI (1,229 → 438 lines)
- 33% smaller models (1,071 → 715 lines)
- Clear structure, easy to navigate

### v3.1 (October 6, 2025) - AI Enhancements
**Focus**: Legal pattern detection and power dynamics

**Key Features**:
- Legal pattern detection (contradictions, corroboration, gaps)
- Power dynamics analysis in email threads
- Enhanced entity extraction (relationships, quotes, events)
- Temporal sequence analysis

**Data Utilization**: 65% (baseline)

### v3.2 (October 6, 2025) - Intelligence Layer
**Focus**: AI entity resolution and case type support

**Key Features**:
- AI entity resolution (`--ai-resolve`)
- Case type support (`--case-type workplace|contract|generic`)
- Chunked summaries for large cases (50+ evidence)
- Video/audio basic ingestion

**Data Utilization**: 75% (+10 points)

### v3.3 (October 8, 2025) - Maximum Data Utilization
**Focus**: Extract all captured AI data

**Key Features**:
- Phase A: Quoted statements, communication patterns (95%)
- Phase B: Semantic timeline, relationship networks, image OCR (98%)
- Insights-first report layout
- Zero additional AI costs

**Data Utilization**: 98% (+23 points)

### v4.0 (October 10, 2025) - Generators Architecture
**Focus**: Professional forensic reports at scale

**Key Features**:
- 9 specialized report generators (3,591 lines)
- 8 professional forensic reports automatically generated
- Template Method pattern for consistency
- Conditional generation based on evidence types
- Complete documentation overhaul

**Data Utilization**: 90% (report-focused subset of v3.3's 98%)
**Client Value**: £4,500 (8-9x increase from £500)
**Processing Overhead**: +5-10 seconds per case

---

## Data Flow

### Complete Pipeline Flow (v4.0)

```
┌─────────────────────────────────────────────────────────────────┐
│ INPUT: Evidence Files (.pdf, .eml, .jpg, .txt, etc.)          │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: INGESTION                                              │
│ ─────────────────────                                           │
│ • SHA256 hashing                                                │
│ • Metadata extraction (EXIF, file properties)                   │
│ • Content-addressed storage                                     │
│ • Chain of custody initialization                               │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STORAGE: data/storage/raw/sha256=<hash>/original.{ext}         │
│          data/storage/derived/sha256=<hash>/metadata.json      │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: ANALYSIS (AI-Powered)                                 │
│ ────────────────────────────────                                │
│ • Type detection (.txt → Document, .jpg → Image, etc.)         │
│ • AI analysis (OpenAI GPT-4o/4o-mini, temperature=0)           │
│ • Structured output (Pydantic validation)                       │
│ • Label generation                                              │
│   ┌────────────────────────────────────────────┐               │
│   │ DocumentAnalyzer → DocumentAnalysisStructured│              │
│   │ • Entities, sentiment, topics, risk flags   │              │
│   │ • v3.1: Relationships, quotes, events       │              │
│   ├────────────────────────────────────────────┤               │
│   │ ImageAnalyzer → ImageAnalysisStructured    │               │
│   │ • Scene, objects, OCR, people, value       │               │
│   ├────────────────────────────────────────────┤               │
│   │ EmailAnalyzer → EmailThreadAnalysis        │               │
│   │ • Participants, authority, deference       │               │
│   │ • v3.1: Power dynamics, patterns           │               │
│   └────────────────────────────────────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STORAGE: data/storage/derived/sha256=<hash>/analysis.v1.json   │
│          (UnifiedAnalysis with type-specific data)              │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: CORRELATION & SUMMARY                                 │
│ ────────────────────────────────────                            │
│ • Load all evidence for case                                    │
│ • Cross-evidence entity matching (v3.2: AI-powered)             │
│ • Timeline reconstruction (v3.3: semantic events)               │
│ • Legal pattern detection (v3.1: contradictions, corroboration) │
│ • Data aggregation (v3.3: 98% utilization):                     │
│   - Quoted statements by person                                 │
│   - Communication patterns                                      │
│   - Relationship networks                                       │
│   - Power dynamics                                              │
│   - Image OCR text                                              │
│ • AI executive summary generation                               │
│ • overall_assessment dict population (feeds v4.0 generators)    │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT: CaseSummary                                             │
│ • evidence_summaries: List[EvidenceSummary]                     │
│ • correlation_result: CorrelationAnalysis                       │
│ • overall_assessment: Dict[str, Any]  ← Feeds generators        │
│ • executive_summary: str                                        │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: PACKAGE GENERATION (v4.0 Generators)                  │
│ ──────────────────────────────────────────                      │
│ For each generator in [Forensic, Financial, Legal, ...]:       │
│   1. Check has_data() → Skip if no data                         │
│   2. Generate Markdown report                                   │
│   3. Save to reports/ directory                                 │
│                                                                  │
│ Generated Reports (8 total):                                    │
│ ✓ Executive Summary (v3.3 baseline)                             │
│ ✓ Forensic Legal Opinion                                        │
│ ✓ Financial Risk Assessment                                     │
│ ✓ Legal Patterns Analysis                                       │
│ ✓ Timeline Reconstruction                                       │
│ ✓ Quoted Statements Analysis                                    │
│ ✓ Relationship Network Analysis                                 │
│ ✓ Power Dynamics Analysis (conditional on email evidence)       │
│ ⊘ Image OCR Analysis (conditional on image evidence)            │
│                                                                  │
│ Component Assembly:                                             │
│ • Copy reports/ to package                                      │
│ • Copy analysis/ JSON files                                     │
│ • Copy correlations/ results                                    │
│ • Copy evidence_catalog/                                        │
│ • Optionally copy raw_evidence/                                 │
│ • Create ZIP archive                                            │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ OUTPUT: Client Package ZIP                                      │
│ <case-id>_analysis_package_<timestamp>.zip                      │
│ ├── reports/ (8 professional Markdown reports, 52-54KB)        │
│ ├── analysis/ (JSON structured data)                            │
│ ├── correlations/ (cross-evidence patterns)                     │
│ ├── evidence_catalog/ (inventory)                               │
│ └── raw_evidence/ (optional originals)                          │
│                                                                  │
│ VALUE: £4,500 (vs £500 in v3.3)                                 │
│ UTILIZATION: 90% of AI-generated data                           │
│ TRIBUNAL-READY: Complete forensic analysis package              │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Case Evidence Reuse

```
Evidence File (document.pdf)
       ↓
    INGEST (Case A)
       ↓
SHA256 Hash: abc123...
       ↓
ANALYZE (once)
       ├─────────────┐
       ↓             ↓
   Case A        Case B (add_to_case)
   Uses          Uses same analysis
   analysis      (no re-analysis!)
       ↓             ↓
   Package A     Package B
   (both use same analysis.v1.json)

COST SAVINGS: 90%+ on duplicate evidence
```

---

## AI Integration

### OpenAI Models Used

| Pipeline Stage | Model | Purpose | Temperature | Cost Impact |
|----------------|-------|---------|-------------|-------------|
| Document Analysis | `gpt-4o-mini` | Entity extraction, sentiment | 0 | Low (~$0.001-0.003) |
| Image Analysis | `gpt-4o` (Vision) | Scene description, OCR | 0 | Medium (~$0.003-0.008) |
| Email Analysis | `gpt-4o-mini` | Thread analysis, power dynamics | 0 | Low (~$0.002-0.005) |
| Correlation | `gpt-4o-2024-08-06` | Legal patterns, contradictions | 0 | Medium (~$0.01-0.02) |
| Executive Summary | `gpt-4o-2024-08-06` | Case-level insights | 0 | Medium (~$0.01-0.02) |
| v4.0 Generators | None | Format existing data | N/A | **Zero** |

**Key Points**:
- All analysis uses temperature=0 for deterministic results
- OpenAI Responses API ensures structured output
- v4.0 generators add zero AI cost (reuse existing data)
- Typical 20-file case: ~$0.10-0.30 total

### Prompt Engineering

All AI prompts centralized in `domains/legal_config.py`:

```python
# Document analysis (v3.1 enhanced)
DOCUMENT_ANALYSIS_PROMPT = """
Analyze this document for forensic legal investigation.

Extract:
1. Entities (persons, organizations, dates, legal terms)
   - Include relationships if clear (e.g., "sent email to...")
   - Include quoted text if legally significant
   - Include associated events for dates

2. Sentiment (professional/neutral/hostile)

3. Key topics (3-5 main subjects)

4. Legal significance (high/medium/low)

5. Risk flags (threats, admissions, policy violations, ...)
"""

# Email analysis (v3.1 power dynamics)
EMAIL_ANALYSIS_PROMPT = """
Analyze this email thread for forensic investigation.

Extract:
1. Participants with:
   - Authority level (executive/management/employee/external)
   - Deference score (0.0=dominant, 0.5=neutral, 1.0=deferential)
   - Dominant topics

2. Communication pattern:
   - professional, escalating, hostile, retaliatory

3. Escalation indicators
"""

# Case type variants (v3.2)
EXECUTIVE_SUMMARY_PROMPTS = {
    'generic': EXECUTIVE_SUMMARY_PROMPT_GENERIC,
    'workplace': EXECUTIVE_SUMMARY_PROMPT_WORKPLACE,
    'employment': EXECUTIVE_SUMMARY_PROMPT_WORKPLACE,  # Alias
    'contract': EXECUTIVE_SUMMARY_PROMPT_CONTRACT,
}
```

---

## Performance Characteristics

### Processing Times

| Evidence Count | Time | Breakdown |
|----------------|------|-----------|
| 5 files | 2-3 min | AI analysis dominant |
| 20 files | 6-8 min | Typical investigation |
| 50+ files | 15-20 min | Chunked summaries activate |
| 1,295 files | ~20 min | v3.3 stress test (98% images) |

**v4.0 Generator Overhead**: +5-10 seconds per case (all 8 generators)

### OpenAI API Costs

**Approximate costs per evidence piece**:
- Document: $0.001-0.003
- Email: $0.002-0.005
- Image: $0.003-0.008

**Per case**:
- 5 pieces: ~$0.01-0.03
- 20 pieces: ~$0.10-0.30
- 50+ pieces: ~$0.30-0.80

**v4.0 generators**: $0.00 (reuse existing analysis)

### Storage

**Per evidence piece**:
- Original file: 1x size
- Metadata: ~5KB
- Analysis: ~10-50KB
- Chain of custody: ~2KB

**Content-addressed benefits**:
- Duplicate evidence: analyzed once, stored once
- Multi-case reuse: 90%+ cost savings

---

## Forensic Integrity

### Deterministic Analysis

**Temperature = 0**:
- Same input → same output (reproducible)
- Critical for forensic grade results
- Enables re-analysis verification

**Structured Outputs**:
- Pydantic validation ensures schema compliance
- OpenAI Responses API guarantees format
- Confidence scoring on all AI fields

### Chain of Custody

Every operation logged:

```json
{
  "timestamp": "2025-10-10T14:30:00Z",
  "event_type": "analyze",
  "actor": "system",
  "description": "AI-powered analysis completed using gpt-4o-mini",
  "metadata": {
    "model": "gpt-4o-mini",
    "temperature": 0,
    "schema_version": "1.0.0"
  }
}
```

**Storage**: `data/storage/derived/sha256=<hash>/chain_of_custody.json`

### Audit Trail

Complete audit trail includes:
- **Ingestion**: When, by whom, from where
- **Analysis**: Which AI model, which prompt version
- **Correlation**: Which algorithm version
- **Package**: When generated, what included
- **Evidence Access**: Who accessed, when

---

## CLI Reference

### Core Commands

```bash
# Complete pipeline (all stages)
evidence-toolkit process-case <directory> --case-id <ID>

# Individual stages
evidence-toolkit ingest <directory> --case-id <ID>
evidence-toolkit analyze <sha256> --case-id <ID>
evidence-toolkit correlate --case-id <ID>
evidence-toolkit package --case-id <ID>

# Re-analysis (after model updates)
evidence-toolkit reanalyze --case-id <ID>
```

### Advanced Flags (v3.2+)

```bash
# AI entity resolution (context-aware name matching)
--ai-resolve

# Case type (domain-specific prompts)
--case-type workplace  # workplace, employment, contract, generic

# Examples
evidence-toolkit process-case data/cases/MY-CASE \
  --case-id MY-CASE \
  --case-type workplace \
  --ai-resolve
```

### Storage Management

```bash
evidence-toolkit storage stats       # Storage usage
evidence-toolkit storage cleanup     # Remove orphaned evidence
evidence-toolkit storage prune --case-id <ID>  # Clean specific case
```

### Case Management

```bash
evidence-toolkit case list           # List all cases
evidence-toolkit case show <ID>      # Case details
evidence-toolkit case evidence <ID>  # Evidence in case
```

---

## Testing

### Test Coverage (Target)

- **Ingestion**: 85% (core functions, error handling)
- **Analysis**: 90% (type routing, AI mocking)
- **Correlation**: 80% (entity matching, timeline)
- **Packaging**: 75% (component assembly, ZIP creation)
- **Generators**: 70% (has_data, report generation)

### Integration Tests

```bash
# Complete pipeline test
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify all 8 reports generated
ls data/packages/TEST-CASE_*/reports/*.md
```

### Stress Tests

**v3.3 Validation**: 1,295 evidence pieces (98% images)
- ✅ Chunked summarization activated (44 chunks)
- ✅ Image OCR aggregated (143 images with text)
- ✅ No memory leaks, linear scaling
- ✅ Processing time: ~20 minutes

---

## Dependencies

### Core Dependencies

```toml
# AI & Analysis
openai = ">=1.60"
pydantic = ">=2.8"

# Document Processing
pdfplumber = ">=0.9.0"
pdf2image = ">=1.17.0"

# Image Processing
Pillow = ">=10.0.0"
piexif = ">=1.1"

# Data Analysis
pandas = ">=2.0.0"
numpy = ">=2.0"

# Visualization
wordcloud = ">=1.9.4"
matplotlib = ">=3.7.0"
seaborn = ">=0.12.0"

# CLI
click = ">=8.0.0"
```

### Python Version

**Required**: Python 3.12+
**Recommended**: Use `uv` for fast package management

---

## Migration Guides

### v3.x → v4.0

**No breaking changes!** Fully backward compatible.

**What you get**:
- 8 professional forensic reports (automatic)
- Enhanced executive summary
- All v3.3 features preserved

**To upgrade**:
```bash
git pull origin main
uv pip install -e .
evidence-toolkit --version  # Should show 4.0.0
```

**To regenerate existing cases**:
```bash
# Re-package only (no re-analysis)
evidence-toolkit package --case-id MY-CASE
```

### v2.x → v3.x

**Breaking changes**: Package name and structure changed.

See `docs/archive/v3.0/V3_COMPLETE.md` for complete migration guide.

---

## Future Considerations

### Known Limitations (v4.0)

1. **Sequential Analysis**: Evidence analyzed one at a time (parallelization planned)
2. **Memory**: Large cases (1000+ evidence) load fully into memory
3. **Generator Output**: Only Markdown (PDF, HTML, DOCX planned)

### Planned Enhancements (v4.1+)

See `docs/v4.0/` directory for complete v4.x roadmap:

**Performance**:
- Async/await for concurrent processing (3-5x speedup)
- Streaming package generation
- Incremental correlation updates

**Features**:
- Audio/video transcript analysis
- Metadata forensics (EXIF tampering detection)
- Semantic similarity detection
- Visual network diagram generation (Mermaid/GraphViz)

**Architecture**:
- Hexagonal architecture with dependency injection
- Configuration-driven (YAML + env vars)
- Modular analyzer plugins

**Output Formats**:
- PDF report generation
- HTML interactive dashboards
- DOCX for Word compatibility

---

## Success Metrics

### v4.0 Achievements

**Data Utilization**:
- ✅ 90% (report-focused subset of v3.3's 98%)
- ✅ All major AI insights surfaced in reports

**Client Value**:
- ✅ £4,500 deliverable (8-9x increase from £500)
- ✅ 8 professional forensic reports
- ✅ Tribunal-ready quality

**Technical Quality**:
- ✅ 3,591 lines of generator code
- ✅ Template Method pattern for consistency
- ✅ Zero additional AI costs
- ✅ Conditional generation (clean UX)

**Documentation**:
- ✅ Central docs index (docs/README.md)
- ✅ Complete CHANGELOG.md
- ✅ Comprehensive architecture (this document)
- ✅ Archived historical docs

---

## Conclusion

Evidence Toolkit v4.0 represents a **major capability transformation** from a basic analysis tool to a premium forensic platform. The generators architecture (v3.4 Phases 1-3) enables automatic generation of 8 professional reports while maintaining zero additional AI costs through intelligent reuse of v3.3 analysis data.

**Key Takeaways**:
- **Professional Output**: 8 tribunal-ready forensic reports
- **Maximum Value**: £4,500 client deliverable (8-9x increase)
- **Zero Cost**: Reuses existing AI analysis (no new API calls)
- **Clean Architecture**: Modular generators following Template Method pattern
- **90% Utilization**: Maximum insights from every AI analysis

The architecture is built on the solid v3.0 foundation (clean structure, Pydantic everywhere, content-addressed storage) and enhanced through v3.1 (legal patterns, power dynamics), v3.2 (AI entity resolution, case types), and v3.3 (maximum data utilization), culminating in v4.0's professional report generation capability.

**Future**: v4.x roadmap includes performance improvements (async processing), additional output formats (PDF, HTML), and architectural enhancements (hexagonal design, configuration-driven) while preserving the forensic integrity and professional quality that define Evidence Toolkit.

---

**Document Version**: 4.0.0
**Last Updated**: 2025-10-10
**Next Review**: When v4.1 planning begins

*Evidence Toolkit - Professional forensic evidence analysis with AI-powered insights*
