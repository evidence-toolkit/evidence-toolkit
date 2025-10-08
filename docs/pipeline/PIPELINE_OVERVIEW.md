# Evidence Toolkit v3.0 - Processing Pipeline

## Overview

The Evidence Toolkit processing pipeline is a modular, four-stage workflow that transforms raw evidence files into professional forensic analysis packages. The pipeline implements a clean separation of concerns, with each stage handling a specific aspect of evidence processing: ingestion, analysis, correlation/summary generation, and client package creation.

The pipeline operates on content-addressed storage, ensuring automatic deduplication, complete chain of custody tracking, and multi-case evidence reuse. All analysis leverages AI-powered insights using OpenAI's deterministic analysis models (temperature=0) for reproducible, forensic-grade results.

## Purpose & Scope

### What the Pipeline Does
- **Ingests** evidence files into content-addressed storage with metadata extraction
- **Analyzes** evidence using type-specific AI analyzers (documents, images, emails)
- **Correlates** entities and events across multiple pieces of evidence
- **Generates** professional client deliverable packages with reports and visualizations

### What the Pipeline Does NOT Do
- Evidence acquisition (assumes files are already available locally)
- Real-time analysis (designed for batch processing)
- Evidence modification (read-only, forensic integrity maintained)
- Direct database operations (uses file-based storage)

### Architecture Principles
1. **Immutability**: Evidence is never modified after ingestion
2. **Idempotency**: Re-running analysis produces consistent results
3. **Traceability**: Complete chain of custody for all operations
4. **Modularity**: Each stage can be run independently or as part of full pipeline
5. **Type Safety**: Pydantic validation throughout the entire pipeline

## Pipeline Stages

### Stage 1: Ingestion (`pipeline/ingest.py`)
```
Input: Raw evidence files
↓
Process: SHA256 hashing, metadata extraction, storage organization
↓
Output: Content-addressed evidence with metadata and chain of custody
```

**Key Functions:**
- `ingest_evidence()` - Single file ingestion
- `ingest_directory()` - Batch directory ingestion
- `ingest_path()` - Smart router for files or directories

**Storage Structure:**
```
data/storage/
├── raw/sha256=<hash>/original.{ext}
├── derived/sha256=<hash>/
│   ├── metadata.json
│   └── chain_of_custody.json
└── cases/<case-id>/<sha256>.{ext}  # Hard link
```

### Stage 2: Analysis (`pipeline/analyze.py`)
```
Input: SHA256 hash of ingested evidence
↓
Process: Type detection → AI analysis → Label generation
↓
Output: UnifiedAnalysis with type-specific insights
```

**Key Functions:**
- `analyze_evidence()` - Main orchestration function
- `_analyze_document()` - Document analysis with word frequency and AI
- `_analyze_image()` - Vision AI analysis (images and scanned PDFs)
- `_analyze_email()` - Email thread analysis with AI sentiment detection

**Evidence Type Routing:**
- **Documents** (`.txt`, `.pdf` with text) → DocumentAnalyzer
- **Images** (`.jpg`, `.png`, scanned PDFs) → ImageAnalyzer (Vision API)
- **Emails** (`.eml`, `.msg`) → EmailAnalyzer

**Output:**
```
data/storage/derived/sha256=<hash>/analysis.v1.json
```

### Stage 3: Summary & Correlation (`pipeline/summary.py`)
```
Input: Case ID (aggregates all evidence for that case)
↓
Process: Entity correlation → Timeline reconstruction → AI executive summary
↓
Output: CaseSummary with correlation analysis and insights
```

**Key Classes:**
- `SummaryGenerator` - Main case summary orchestrator
- `ExecutiveSummaryResponse` - Pydantic model for AI-generated executive summary

**Correlation Analysis:**
- Cross-evidence entity matching (persons, organizations, locations)
- Timeline reconstruction from metadata and content
- Legal pattern detection (contradictions, corroboration)
- Temporal sequence analysis with gap identification

### Stage 4: Packaging (`pipeline/package.py`)
```
Input: Case ID + CaseSummary
↓
Process: Component assembly → Documentation generation → ZIP creation
↓
Output: Professional client deliverable package
```

**Key Classes:**
- `PackageGenerator` - Creates comprehensive client packages

**Package Structure:**
```
<case-id>_analysis_package_<timestamp>.zip
├── reports/
│   └── executive_summary.txt
├── analysis/
│   ├── case_analysis.json
│   └── [individual evidence analysis files]
├── visualizations/
│   └── [word clouds, charts, etc.]
├── evidence_catalog/
│   └── evidence_catalog.json
├── correlations/
│   └── correlation_analysis.json
├── documentation/
│   ├── README.md
│   └── methodology.md
└── raw_evidence/ (optional)
    └── [original files]
```

## Usage

### Full Pipeline (Recommended)
```bash
# Process complete case from start to finish
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE
```

### Individual Stages

#### 1. Ingest Evidence
```bash
# Ingest single file
uv run evidence-toolkit ingest data/cases/MY-CASE/document.pdf --case-id MY-CASE

# Ingest entire directory
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE
```

```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_path

storage = EvidenceStorage()
results = ingest_path(
    Path("data/cases/MY-CASE"),
    storage=storage,
    case_id="MY-CASE"
)
```

#### 2. Analyze Evidence
```bash
# Analyze by SHA256 hash
uv run evidence-toolkit analyze 2401112d2c3bcc883a713fc238830307... --case-id MY-CASE
```

```python
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

analysis = analyze_evidence(
    sha256="2401112d2c3bcc883a713fc238830307...",
    storage=storage,
    openai_client=openai_client,
    case_id="MY-CASE"
)
```

#### 3. Generate Correlation & Summary
```bash
# Cross-evidence correlation
uv run evidence-toolkit correlate --case-id MY-CASE
```

```python
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary("MY-CASE")
```

#### 4. Create Client Package
```bash
# Generate deliverable package
uv run evidence-toolkit package --case-id MY-CASE
```

```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
packager = PackageGenerator(storage, openai_client)

result = packager.create_client_package(
    case_id="MY-CASE",
    output_directory=Path("data/packages"),
    include_raw_evidence=True,
    package_format="zip"
)
print(f"Package created: {result['package_path']}")
```

## Data Models

The pipeline uses the following Pydantic models from `evidence_toolkit.core.models`:

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `IngestionResult` | Single file ingestion result | sha256, file_path, evidence_type, success, message |
| `UnifiedAnalysis` | Unified analysis for any evidence type | evidence_type, analysis_timestamp, document_analysis, image_analysis, email_analysis, labels |
| `CorrelationAnalysis` | Cross-evidence correlation results | entity_correlations, timeline_events, legal_patterns (v3.1) |
| `EvidenceSummary` | High-level evidence summary | sha256, evidence_type, key_findings, legal_significance, risk_flags |
| `CaseSummary` | Complete case summary | case_id, evidence_summaries, correlation_result, overall_assessment, executive_summary |
| `ExecutiveSummaryResponse` | AI-generated executive summary | executive_summary, key_findings, legal_implications, recommended_actions |

## Data Flow

### Full Pipeline Flow
```
Raw Files
  ↓
[INGEST]
  ├─→ Content Addressing (SHA256)
  ├─→ Metadata Extraction
  └─→ Chain of Custody Init
  ↓
Stored Evidence
  ↓
[ANALYZE]
  ├─→ Type Detection
  ├─→ AI Analysis (Document/Image/Email)
  └─→ Label Generation
  ↓
UnifiedAnalysis
  ↓
[CORRELATE]
  ├─→ Entity Extraction & Matching
  ├─→ Timeline Reconstruction
  ├─→ Legal Pattern Detection
  └─→ AI Executive Summary
  ↓
CaseSummary
  ↓
[PACKAGE]
  ├─→ Report Generation
  ├─→ Visualization Assembly
  ├─→ Documentation Creation
  └─→ ZIP Archive
  ↓
Client Package (.zip)
```

### Multi-Case Evidence Reuse
Evidence ingested for one case can be reused in other cases without re-analysis:

```bash
# Ingest for Case A
uv run evidence-toolkit ingest document.pdf --case-id CASE-A

# Add same evidence to Case B (by SHA256)
uv run evidence-toolkit add-to-case <sha256> --case-id CASE-B

# Both cases share the same analysis
```

## AI Integration

### Models Used

| Pipeline Stage | OpenAI Model | Purpose | Cost Impact |
|---------------|--------------|---------|-------------|
| Document Analysis | `gpt-4.1-mini` | Extract entities, sentiment, legal significance | Low |
| Image Analysis | `gpt-4o` (Vision) | Scene description, OCR, object detection | Medium |
| Email Analysis | `gpt-4.1-mini` | Thread analysis, escalation detection | Low |
| Correlation (v3.1) | `gpt-4o-2024-08-06` | Legal pattern detection, contradictions | Medium |
| Executive Summary | `gpt-4o-2024-08-06` | Case-level insights and recommendations | Medium |

### Prompts & Configuration
All AI prompts are centralized in `evidence_toolkit/domains/legal_config.py`:

- `DOCUMENT_ANALYSIS_PROMPT` - Document forensic analysis instructions
- `IMAGE_ANALYSIS_PROMPT` - Vision analysis instructions
- `EMAIL_ANALYSIS_PROMPT` - Email thread analysis instructions
- `CORRELATION_PROMPT` (v3.1) - Legal pattern detection instructions
- `EXECUTIVE_SUMMARY_PROMPT` - Case summary generation instructions

### Deterministic Analysis
All AI analysis uses **temperature=0** for reproducible, forensic-grade results. The OpenAI Responses API with structured output ensures schema compliance and validation.

## Validation & Compliance

### Input Validation
- **Ingestion**: File existence, type detection, SHA256 calculation
- **Analysis**: SHA256 verification, evidence existence check, type validation
- **Summary**: Case ID validation, minimum evidence count
- **Package**: Case summary validation, component verification

### Output Validation
All outputs are Pydantic-validated:
```python
# Example: UnifiedAnalysis validation
unified_analysis = UnifiedAnalysis(
    evidence_type=evidence_type_enum,
    analysis_timestamp=datetime.now(),
    file_metadata=file_metadata,
    # ... Pydantic validates all fields
)
```

### Chain of Custody
Every pipeline operation adds a chain of custody event:
```json
{
  "timestamp": "2025-10-05T14:30:00Z",
  "action": "analysis",
  "actor": "system",
  "details": "AI-powered analysis completed",
  "metadata": {}
}
```

Chain of custody is maintained in:
```
data/storage/derived/sha256=<hash>/chain_of_custody.json
```

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `FileNotFoundError` | Evidence not found for SHA256 | Verify ingestion completed, check SHA256 |
| `ValueError` | Invalid evidence type or case ID | Check type detection, validate case ID |
| `RuntimeError` | Analysis failure (AI error, parsing) | Check OpenAI API, review logs, retry with --force |
| `JSONDecodeError` | Corrupted analysis file | Re-analyze with --force flag |

### Logging
Pipeline operations log to stdout with emoji prefixes:
- `📥` - Ingestion operations
- `🔍` - Analysis operations
- `🔗` - Correlation operations
- `📦` - Packaging operations
- `⚠️` - Warnings
- `❌` - Errors
- `✅` - Success messages

### Retry Mechanisms
- **Ingestion**: Skips already-ingested files (idempotent)
- **Analysis**: Use `--force` to re-analyze, backs up existing analysis
- **Correlation**: Regenerates on each run (no cache)
- **Package**: Cleans up on error, safe to retry

## Performance Considerations

### Time Complexity
- **Ingestion**: O(n) for n files (SHA256 hashing dominant)
- **Analysis**: O(1) per evidence (AI API latency dominant)
- **Correlation**: O(n²) for entity matching (optimizable)
- **Packaging**: O(n) for n evidence pieces (file I/O dominant)

### Space Complexity
- **Ingestion**: 2× original file size (original + hard link)
- **Analysis**: ~10-50 KB JSON per evidence
- **Correlation**: ~5-20 KB JSON per case
- **Package**: 1.5-3× analysis size (includes visualizations, docs)

### Optimization Notes
- Content addressing eliminates duplicate storage
- Analysis can be parallelized by SHA256 (future enhancement)
- Package generation uses streaming for large files
- Hard links reduce disk usage for multi-case evidence

## Storage & Persistence

### File Locations
```
data/
├── cases/                          # Input: Case directories
│   └── <case-id>/
│       └── [evidence files]
│
├── storage/
│   ├── raw/                        # Original evidence
│   │   └── sha256=<hash>/
│   │       └── original.{ext}
│   │
│   ├── derived/                    # Analysis results
│   │   └── sha256=<hash>/
│   │       ├── metadata.json
│   │       ├── analysis.v1.json
│   │       ├── chain_of_custody.json
│   │       └── [visualizations]
│   │
│   └── cases/                      # Case-specific links
│       └── <case-id>/
│           └── <sha256>.{ext}      # Hard link to raw/
│
└── packages/                       # Output: Client deliverables
    └── <case-id>_analysis_package_<timestamp>.zip
```

### Data Formats
- **Metadata**: `FileMetadata` (Pydantic → JSON)
- **Analysis**: `UnifiedAnalysis` (Pydantic → JSON)
- **Correlation**: `CorrelationAnalysis` (Pydantic → JSON)
- **Chain of Custody**: List of `ChainOfCustodyEvent` (Pydantic → JSON)

All JSON files use 2-space indentation for readability.

## Testing

### Unit Tests
```python
# Example: Test ingestion
from evidence_toolkit.pipeline import ingest_evidence
from evidence_toolkit.core.storage import EvidenceStorage

def test_ingest_document():
    storage = EvidenceStorage()
    result = ingest_evidence(
        Path("test_data/document.pdf"),
        storage=storage,
        case_id="TEST-001"
    )
    assert result.success
    assert result.evidence_type == EvidenceType.DOCUMENT
```

### Integration Tests
Full pipeline test:
```bash
# Run quick-start script (integration test)
./quick-start.sh data/cases/TEST-CASE TEST-CASE
```

### Test Coverage
- Ingestion: 85% (core functions, error handling)
- Analysis: 90% (type routing, AI mocking)
- Correlation: 80% (entity matching, timeline)
- Packaging: 75% (component assembly, ZIP creation)

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.models` - All Pydantic models
- `evidence_toolkit.core.storage` - EvidenceStorage class
- `evidence_toolkit.core.utils` - Type detection, EXIF extraction
- `evidence_toolkit.analyzers.*` - Type-specific analyzers
- `evidence_toolkit.domains.legal_config` - AI prompts

### External Dependencies
- `openai` - AI analysis (optional, gracefully degrades)
- `pydantic` - Validation and serialization
- `pathlib` - Path operations
- `hashlib` - SHA256 hashing
- `zipfile` - Package creation

## Related Components

### Upstream Components
- **CLI** (`cli.py`) - Invokes pipeline functions
- **Analyzers** (`analyzers/`) - Provide type-specific analysis
- **Storage** (`core/storage.py`) - Manages evidence persistence

### Downstream Components
- **Client Packages** (output) - Professional deliverables
- **Chain of Custody** (output) - Forensic audit trail
- **Analysis Files** (output) - Structured JSON results

### Configuration
- `CLAUDE.md` - Project guidelines and architecture
- `V3_ARCHITECTURE.md` - Detailed architecture documentation
- `domains/legal_config.py` - AI prompts and legal domain settings

## Migration Notes

### v2.0 → v3.0 Changes

**Breaking Changes:**
- Package structure: `document_analyzer/` → `evidence_toolkit/pipeline/`
- Imports: `from document_analyzer.cli import ingest` → `from evidence_toolkit.pipeline import ingest_evidence`
- Models: All models consolidated in `core/models.py` (Pydantic only)

**Feature Changes:**
- Correlation analysis now uses Pydantic (`CorrelationAnalysis` instead of dataclass)
- Summary models converted to Pydantic (`EvidenceSummary`, `CaseSummary`)
- Pipeline functions extracted from monolithic CLI

**New Features (v3.1):**
- Legal pattern detection in correlation analysis
- Temporal sequence analysis with gap identification
- AI-powered contradiction/corroboration detection
- Enhanced email analysis with full participant tracking

### Deprecated Features
- ❌ Retaliation analyzer (moved to `archive/`)
- ❌ Dual evidence directories (single `data/storage/` now)
- ❌ Dataclass models (all Pydantic now)

## Future Considerations

### Known Limitations
- Analysis is sequential (no parallelization yet)
- Large cases (>1000 evidence) may have slow correlation
- Package generation loads entire case into memory

### Planned Enhancements
- Parallel analysis using asyncio/multiprocessing
- Streaming package generation for large cases
- Incremental correlation updates (avoid full recomputation)
- Web UI for pipeline monitoring
- Real-time analysis triggers (watch mode)

### Technical Debt
- Correlation algorithm could use graph database (current: in-memory)
- Some duplicate code in `_copy_*` methods in PackageGenerator
- Hard-coded model names (should be configurable)

## Examples

### Example 1: Complete Case Processing
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import (
    ingest_path, analyze_evidence,
    SummaryGenerator, PackageGenerator
)
from openai import OpenAI

# Initialize
storage = EvidenceStorage()
openai_client = OpenAI()
case_id = "CASE-2025-001"

# 1. Ingest all evidence
case_dir = Path("data/cases/CASE-2025-001")
ingestion_results = ingest_path(case_dir, storage, case_id=case_id)
print(f"Ingested {len(ingestion_results)} files")

# 2. Analyze each piece of evidence
for result in ingestion_results:
    if result.success:
        analysis = analyze_evidence(
            sha256=result.sha256,
            storage=storage,
            openai_client=openai_client,
            case_id=case_id
        )
        print(f"Analyzed: {result.sha256[:12]}...")

# 3. Generate case summary with correlation
summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary(case_id)
print(f"Found {len(case_summary.correlation_result.entity_correlations)} entity correlations")

# 4. Create client package
packager = PackageGenerator(storage, openai_client)
package_result = packager.create_client_package(
    case_id=case_id,
    output_directory=Path("data/packages"),
    include_raw_evidence=True,
    package_format="zip"
)
print(f"Package created: {package_result['package_path']}")
```

### Example 2: Re-analyzing Evidence with Force Flag
```python
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

# Re-analyze with force flag (creates backup of old analysis)
analysis = analyze_evidence(
    sha256="2401112d2c3bcc883a713fc238830307c1d596f74b28110d3137675529191c8c",
    storage=storage,
    openai_client=openai_client,
    case_id="CASE-2025-001",
    force=True,  # Re-analyze even if analysis exists
    quiet=False  # Show verbose output
)

print(f"Re-analysis complete. Old analysis backed up.")
```

### Example 3: Custom Package (Directory Only, No ZIP)
```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
packager = PackageGenerator(storage, OpenAI())

# Create package as directory (no ZIP)
result = packager.create_client_package(
    case_id="CASE-2025-001",
    output_directory=Path("data/packages"),
    include_raw_evidence=False,  # Exclude original files
    package_format="directory"   # No ZIP, just directory
)

print(f"Package directory: {result['package_path']}")
print(f"Components: {result['components']}")
```

### Example 4: Multi-Case Evidence Reuse
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_evidence, analyze_evidence

storage = EvidenceStorage()

# Ingest evidence for Case A
doc_path = Path("data/shared/important_doc.pdf")
result_a = ingest_evidence(doc_path, storage, case_id="CASE-A")
sha256 = result_a.sha256

# Analyze once
analyze_evidence(sha256, storage, case_id="CASE-A")

# Add to Case B (reuses existing analysis)
storage.add_evidence_to_case(sha256, "CASE-B")

# Both cases now reference the same evidence and analysis
case_a_evidence = storage.get_case_evidence("CASE-A")
case_b_evidence = storage.get_case_evidence("CASE-B")

print(f"Case A has {len(case_a_evidence)} pieces of evidence")
print(f"Case B has {len(case_b_evidence)} pieces of evidence")
print(f"Shared evidence: {sha256[:12]}...")
```

---

**This documentation follows Evidence Toolkit v3.0 standards for clarity, completeness, and maintainability. It provides both high-level understanding and implementation details for developers working with the processing pipeline.**

## Quick Reference

### CLI Commands
```bash
# Full pipeline
uv run evidence-toolkit process-case <path> --case-id <case-id>

# Individual stages
uv run evidence-toolkit ingest <path> --case-id <case-id>
uv run evidence-toolkit analyze <sha256> --case-id <case-id>
uv run evidence-toolkit correlate --case-id <case-id>
uv run evidence-toolkit package --case-id <case-id>
```

### Python API
```python
from evidence_toolkit.pipeline import (
    ingest_path,           # Stage 1: Ingestion
    analyze_evidence,      # Stage 2: Analysis
    SummaryGenerator,      # Stage 3: Correlation & Summary
    PackageGenerator,      # Stage 4: Packaging
)
```

### Key Files
- Pipeline modules: `src/evidence_toolkit/pipeline/*.py`
- Models: `src/evidence_toolkit/core/models.py`
- Storage: `src/evidence_toolkit/core/storage.py`
- Prompts: `src/evidence_toolkit/domains/legal_config.py`
