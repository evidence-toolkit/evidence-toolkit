# Evidence Toolkit Pipeline Documentation

**Version:** 3.0.0 | **Last Updated:** 2025-10-05

This directory contains comprehensive documentation for the Evidence Toolkit v3.0 processing pipeline - a modular, four-stage workflow that transforms raw evidence files into professional forensic analysis packages.

## Documentation Index

### 📋 [Pipeline Overview](PIPELINE_OVERVIEW.md)
Complete overview of the four-stage pipeline architecture, data flow, and integration points.

**Topics Covered:**
- Pipeline architecture and design principles
- Stage-by-stage processing flow
- Data models and validation
- AI integration and deterministic analysis
- Multi-case evidence reuse
- Performance considerations
- Quick reference and examples

**Start here for:** High-level understanding of the complete pipeline.

---

### 📥 [Ingestion Pipeline](ingest.md)
Detailed documentation for evidence ingestion into content-addressed storage.

**Topics Covered:**
- File ingestion (single file, directory, smart routing)
- SHA256-based content addressing
- Metadata extraction and chain of custody
- Deduplication logic
- Storage structure and hard links
- Error handling and performance

**Start here for:** Understanding how evidence enters the system.

**Key Functions:**
- `ingest_evidence()` - Single file ingestion
- `ingest_directory()` - Batch directory ingestion
- `ingest_path()` - Smart router for files or directories
- `print_ingestion_summary()` - Human-readable results

---

### 🔍 [Analysis Pipeline](analyze.md)
Comprehensive guide to evidence analysis orchestration and type-specific analyzers.

**Topics Covered:**
- Evidence type detection and routing
- Type-specific analysis (documents, images, emails)
- Label generation for categorization
- AI-powered analysis with OpenAI
- Force re-analysis with backup
- Chain of custody tracking

**Start here for:** Understanding how evidence is analyzed with AI.

**Key Functions:**
- `analyze_evidence()` - Main orchestration function
- `_analyze_document()` - Document analysis
- `_analyze_image()` - Image/PDF vision analysis
- `_analyze_email()` - Email thread analysis
- `_generate_labels()` - Label generation

---

### 🔗 [Summary & Correlation](summary.md)
In-depth documentation for case-level summary generation and cross-evidence correlation.

**Topics Covered:**
- Case summary generation
- Cross-evidence entity correlation
- Timeline reconstruction
- Legal pattern detection (v3.1)
- AI executive summary generation
- JSON and text report export

**Start here for:** Understanding how individual evidence is correlated into case insights.

**Key Classes:**
- `SummaryGenerator` - Main case summary orchestrator
- `ExecutiveSummaryResponse` - AI-generated executive summary model
- `EvidenceSummary` - Per-evidence summary (Pydantic, v3.1)
- `CaseSummary` - Complete case summary (Pydantic, v3.1)

---

### 📦 [Package Generator](package.md)
Complete guide to creating professional client deliverable packages.

**Topics Covered:**
- Package structure and components
- Report generation (executive summary, evidence catalog)
- Visualization assembly
- Documentation creation (README, methodology)
- ZIP and directory package formats
- Raw evidence inclusion options

**Start here for:** Understanding how analysis results become client deliverables.

**Key Classes:**
- `PackageGenerator` - Creates comprehensive client packages

---

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Evidence Toolkit Pipeline                │
└─────────────────────────────────────────────────────────────┘

  📥 STAGE 1: INGESTION
  ├─→ Raw files (PDF, images, emails, etc.)
  ├─→ SHA256 hashing (content addressing)
  ├─→ Metadata extraction
  ├─→ Chain of custody initialization
  └─→ Deduplication & storage
      │
      ↓
  🔍 STAGE 2: ANALYSIS
  ├─→ Type detection (document/image/email)
  ├─→ Route to type-specific analyzer
  ├─→ AI-powered analysis (OpenAI)
  ├─→ Label generation
  └─→ UnifiedAnalysis result
      │
      ↓
  🔗 STAGE 3: CORRELATION & SUMMARY
  ├─→ Entity extraction & matching
  ├─→ Timeline reconstruction
  ├─→ Legal pattern detection (AI, v3.1)
  ├─→ Overall assessment calculation
  └─→ AI executive summary generation
      │
      ↓
  📦 STAGE 4: PACKAGING
  ├─→ Component assembly (reports, analysis, visualizations)
  ├─→ Documentation generation (README, methodology)
  ├─→ Evidence catalog creation
  ├─→ Correlation report
  └─→ ZIP archive or directory package
```

## Quick Start Examples

### Complete Pipeline (CLI)
```bash
# Process entire case from start to finish
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE
```

### Individual Stages (CLI)
```bash
# Stage 1: Ingest
uv run evidence-toolkit ingest data/cases/MY-CASE --case-id MY-CASE

# Stage 2: Analyze
uv run evidence-toolkit analyze <sha256> --case-id MY-CASE

# Stage 3: Correlate & Summarize
uv run evidence-toolkit correlate --case-id MY-CASE

# Stage 4: Package
uv run evidence-toolkit package --case-id MY-CASE
```

### Python API
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import (
    ingest_path,
    analyze_evidence,
    SummaryGenerator,
    PackageGenerator
)
from openai import OpenAI

# Initialize
storage = EvidenceStorage()
openai_client = OpenAI()
case_id = "CASE-001"

# Stage 1: Ingest
results = ingest_path(Path("data/cases/CASE-001"), storage, case_id)

# Stage 2: Analyze
for result in results:
    if result.success:
        analyze_evidence(result.sha256, storage, openai_client, case_id)

# Stage 3: Summarize
summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary(case_id)

# Stage 4: Package
packager = PackageGenerator(storage, openai_client)
package_result = packager.create_client_package(
    case_id=case_id,
    output_directory=Path("data/packages"),
    package_format="zip"
)

print(f"Package: {package_result['package_path']}")
```

## Key Features

### ✅ Content-Addressed Storage
- SHA256-based deduplication
- Multi-case evidence reuse
- Complete chain of custody
- Immutable evidence storage

### ✅ AI-Powered Analysis
- OpenAI deterministic models (temperature=0)
- Type-specific analyzers (documents, images, emails)
- Entity extraction and correlation
- Legal significance assessment
- Risk flag detection

### ✅ Cross-Evidence Correlation
- Entity matching across evidence types
- Timeline reconstruction
- Legal pattern detection (contradictions, corroboration)
- Temporal sequence analysis with gap identification

### ✅ Professional Deliverables
- Executive summaries
- Evidence catalogs
- Correlation reports
- Comprehensive documentation
- ZIP or directory packages

## Data Models (Pydantic)

All pipeline components use Pydantic models for validation:

| Model | Module | Purpose |
|-------|--------|---------|
| `IngestionResult` | `core/models.py` | Single file ingestion result |
| `UnifiedAnalysis` | `core/models.py` | Unified analysis for any evidence type |
| `CorrelationAnalysis` | `core/models.py` | Cross-evidence correlation results |
| `EvidenceSummary` | `core/models.py` | High-level evidence summary (v3.1) |
| `CaseSummary` | `core/models.py` | Complete case summary (v3.1) |
| `ExecutiveSummaryResponse` | `pipeline/summary.py` | AI-generated executive summary |

See [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md#data-models) for complete model reference.

## Storage Structure

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

See [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md#storage--persistence) for detailed storage documentation.

## AI Integration

### Models Used by Stage

| Stage | Model | API | Purpose |
|-------|-------|-----|---------|
| Analysis (Documents) | `gpt-4.1-mini` | Responses | Entity extraction, sentiment, legal significance |
| Analysis (Images) | `gpt-4o` | Vision | Scene description, OCR, object detection |
| Analysis (Emails) | `gpt-4.1-mini` | Responses | Thread analysis, escalation detection |
| Correlation (v3.1) | `gpt-4o-2024-08-06` | Responses | Legal pattern detection, contradictions |
| Summary | `gpt-4o-2024-08-06` | Responses | Executive summary, case insights |

### Prompts Location
All AI prompts are centralized in `src/evidence_toolkit/domains/legal_config.py`:
- `DOCUMENT_ANALYSIS_PROMPT`
- `IMAGE_ANALYSIS_PROMPT`
- `EMAIL_ANALYSIS_PROMPT`
- `CORRELATION_PROMPT` (v3.1)
- `EXECUTIVE_SUMMARY_PROMPT`

### Deterministic Analysis
**All AI analysis uses temperature=0** for reproducible, forensic-grade results.

## Performance Considerations

### Time Complexity by Stage

| Stage | Complexity | Dominant Operation |
|-------|------------|-------------------|
| Ingestion | O(n × m) | SHA256 hashing (n files, m avg size) |
| Analysis | O(n) | AI API calls (one per evidence) |
| Correlation | O(n²) | Entity matching (optimizable) |
| Packaging | O(n) | File I/O (assembly and copying) |

### Optimization Notes
- Content addressing eliminates duplicate storage
- Analysis results are cached (re-analysis only with --force)
- Correlation can be parallelized (future enhancement)
- Package generation uses streaming for large files

See individual component docs for detailed performance analysis.

## Error Handling

### Common Errors Across Pipeline

| Error | Cause | Recovery |
|-------|-------|----------|
| `FileNotFoundError` | Evidence not found | Verify ingestion, check SHA256 |
| `ValueError` | Invalid type or case ID | Check detection, validate input |
| `RuntimeError` | Analysis/save failed | Check permissions, API keys, retry |
| `OpenAI APIError` | AI analysis failed | Check API key, rate limits, retry |

### Logging Conventions
- `📥` - Ingestion operations
- `🔍` - Analysis operations
- `🔗` - Correlation operations
- `📦` - Packaging operations
- `✅` - Success
- `⚠️` - Warning
- `❌` - Error

## Testing

### Unit Tests
Each component has comprehensive unit tests. See individual docs for test examples.

### Integration Tests
```bash
# Full pipeline integration test
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify results
uv run evidence-toolkit list --case-id TEST-CASE --detailed
ls -la data/packages/
```

### Test Coverage
- Ingestion: 85%
- Analysis: 90%
- Correlation: 80%
- Packaging: 75%

## Migration from v2.0

### Breaking Changes
- Package structure: `document_analyzer/` → `evidence_toolkit/pipeline/`
- Imports: All pipeline functions moved to `evidence_toolkit.pipeline`
- Models: All consolidated in `core/models.py` (Pydantic only)
- Correlation: Now uses Pydantic instead of dataclass

### Migration Guide
See [PIPELINE_OVERVIEW.md](PIPELINE_OVERVIEW.md#migration-notes) for complete migration guide.

**Quick migration:**
```python
# Old (v2.0)
from document_analyzer.cli import ingest_command, analyze_command
ingest_command(path="...", case_id="...")
analyze_command(sha256="...", case_id="...")

# New (v3.0)
from evidence_toolkit.pipeline import ingest_path, analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
results = ingest_path(Path("..."), storage, case_id="...")
analysis = analyze_evidence(sha256="...", storage=storage, case_id="...")
```

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.models` - All Pydantic models
- `evidence_toolkit.core.storage` - EvidenceStorage class
- `evidence_toolkit.core.utils` - Utilities (type detection, EXIF)
- `evidence_toolkit.analyzers.*` - Type-specific analyzers
- `evidence_toolkit.domains.legal_config` - AI prompts

### External Dependencies
- `openai` - AI analysis (optional, gracefully degrades)
- `pydantic` - Validation and serialization
- `pathlib` - Path operations
- `hashlib` - SHA256 hashing
- `zipfile` - Package creation

## Related Documentation

### Project Documentation
- [CLAUDE.md](../../CLAUDE.md) - Project guidelines and architecture
- [V3_ARCHITECTURE.md](../../V3_ARCHITECTURE.md) - Detailed architecture
- [V3_COMPLETE.md](../../V3_COMPLETE.md) - Refactor summary
- [README.md](../../README.md) - Getting started guide

### Component Documentation
- `docs/analyzers/` - Type-specific analyzer documentation (if exists)
- `docs/core/` - Core module documentation (if exists)

## Contributing

When adding features to the pipeline:
1. Follow the modular design (separate concerns)
2. Use Pydantic for all data models
3. Maintain chain of custody for all operations
4. Add comprehensive docstrings
5. Update this documentation
6. Add unit and integration tests

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed contribution guidelines.

## Support & Contact

For questions about the pipeline:
1. Check the relevant component documentation (links above)
2. Review examples in this README
3. See [QUICKSTART.md](../../QUICKSTART.md) for practical guides
4. Refer to [V3_ARCHITECTURE.md](../../V3_ARCHITECTURE.md) for architecture details

---

**This documentation provides complete reference for the Evidence Toolkit v3.0 processing pipeline. Each component is documented in detail with examples, API references, and best practices.**

**Last Updated:** 2025-10-05 | **Version:** 3.0.0
