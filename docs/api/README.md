# Evidence Toolkit v3.0 - API Documentation

**Complete API reference for Evidence Toolkit v3.0**

---

## Available Documentation

### Core Models Module
- **[Complete Models Documentation](models.md)** (1,601 lines, 54 KB)
  - Comprehensive reference for all 40+ Pydantic models
  - Detailed explanations, usage examples, validation rules
  - Forensic compliance and legal-grade evidence handling
  - Complete migration guide from v2.0 to v3.0

- **[Models Quick Reference](models-quick-reference.md)** (432 lines, 13 KB)
  - Condensed cheat sheet for rapid development
  - Common workflows and import patterns
  - Validation constraints and risk flags
  - Serialization shortcuts and storage paths

---

## Documentation Coverage

### Core Models (`src/evidence_toolkit/core/models.py`)

**Status**: ✅ **Complete** (100% documented)

| Category | Models Documented | Description |
|----------|------------------|-------------|
| **Base Types & Enums** | 4 models | Evidence types, file metadata, chain of custody |
| **AI Analysis Models** | 7 models | OpenAI Responses API structured outputs |
| **Unified Analysis** | 3 models | Multi-modal evidence containers |
| **Forensic Bundles** | 6 models | Legal-grade evidence packages |
| **Cross-Evidence Analysis** | 4 models | Correlation and timeline reconstruction |
| **Legal Pattern Analysis** | 3 models | AI-powered contradiction/corroboration (v3.1) |
| **Case Summary & Reporting** | 2 models | Aggregated case views |
| **Operation Results** | 5 models | Ingestion, export, storage management |
| **Total** | **40+ models** | All Pydantic, single source of truth |

---

## Quick Navigation

### By Use Case

**Need to ingest evidence?**
→ See [models.md - Category 1: Base Types](models.md#category-1-base-types--enums)
- `FileMetadata`
- `IngestionResult`
- `ChainOfCustodyEvent`

**Need to perform AI analysis?**
→ See [models.md - Category 2: AI Analysis Models](models.md#category-2-ai-analysis-models-openai-responses-api)
- `DocumentAnalysis`, `DocumentEntity`
- `ImageAnalysisStructured`
- `EmailThreadAnalysis`, `EmailParticipant`, `EscalationEvent`

**Need to create client packages?**
→ See [models.md - Category 3: Unified Analysis](models.md#category-3-unified-analysis-client-package-format)
- `UnifiedAnalysis`
- `DocumentAnalysisResult`
- `ImageAnalysisResult`

**Need forensic evidence bundles?**
→ See [models.md - Category 4: Forensic Bundles](models.md#category-4-forensic-bundles-legal-grade-evidence-packages)
- `EvidenceBundle`
- `EvidenceCore`
- `DocumentAnalysisRecord`

**Need cross-evidence correlation?**
→ See [models.md - Category 5: Cross-Evidence Analysis](models.md#category-5-cross-evidence-analysis-now-pydantic---v30-fix)
- `CorrelationAnalysis`
- `CorrelatedEntity`
- `TimelineEvent`

**Need legal pattern detection?**
→ See [models.md - Category 6: Legal Pattern Analysis](models.md#category-6-legal-pattern-analysis-v31---ai-powered-insights)
- `LegalPatternAnalysis`
- `Contradiction`
- `CorroborationLink`

**Need case summaries?**
→ See [models.md - Category 7: Case Summary & Reporting](models.md#category-7-case-summary--reporting)
- `CaseSummary`
- `EvidenceSummary`

**Need operation results?**
→ See [models.md - Category 8: Operation Results](models.md#category-8-operation-results)
- `StorageStats`
- `CaseInfo`
- `CleanupResult`

---

## Quick Start Examples

### Import Everything You Need
```python
from evidence_toolkit.core.models import (
    # Base
    EvidenceType, FileMetadata, ChainOfCustodyEvent,

    # AI Analysis
    DocumentAnalysis, EmailThreadAnalysis, ImageAnalysisStructured,

    # Client Packages
    UnifiedAnalysis,

    # Cross-Evidence
    CorrelationAnalysis, LegalPatternAnalysis
)
```

### Basic Workflow
```python
# 1. Ingest evidence
metadata = FileMetadata(filename="complaint.pdf", sha256="abc123...", ...)
result = IngestionResult(sha256=metadata.sha256, success=True, ...)

# 2. Analyze with AI
analysis = DocumentAnalysis(
    summary="Harassment complaint",
    legal_significance="critical",
    risk_flags=["harassment", "retaliation_indicators"],
    ...
)

# 3. Create client package
unified = UnifiedAnalysis(
    evidence_type=EvidenceType.DOCUMENT,
    file_metadata=metadata,
    document_analysis=DocumentAnalysisResult(...),
    chain_of_custody=[...],
    ...
)

# 4. Correlate across evidence
correlation = CorrelationAnalysis(
    case_id="CASE-2024-001",
    entity_correlations=[...],
    timeline_events=[...],
    legal_patterns=LegalPatternAnalysis(
        contradictions=[...],
        corroboration=[...],
        ...
    )
)
```

Full examples: [models.md - Examples](models.md#examples)

---

## Documentation Style Guide

### Used Throughout
- **Forensic/Legal Focus**: All documentation emphasizes legal admissibility and chain of custody
- **OpenAI Integration**: Details on using models with OpenAI Responses API
- **v3.0 Improvements**: Clear migration paths from v2.0
- **v3.1 Enhancements**: Layer 1 features (power dynamics, legal patterns)
- **Validation Details**: Pydantic constraints, error handling
- **Real-World Examples**: Harassment complaint case study

---

## Key v3.0 Architectural Changes

From [models.md - Migration Notes](models.md#migration-notes-v20--v30):

1. **Models Consolidation**: 5 files → 1 file (`core/models.py`)
2. **All Pydantic**: Dataclasses converted (including `CorrelationAnalysis`)
3. **Shorter Imports**: `from evidence_toolkit.core.models import ...`
4. **Multi-Case Support**: `case_id` → `case_ids` (backward compatible)
5. **v3.1 AI Patterns**: Legal pattern detection, power dynamics analysis

---

## Validation Reference

### Common Constraints
- **SHA256**: `pattern=r"^[a-f0-9]{64}$"` (64 lowercase hex chars)
- **Confidence**: `ge=0.0, le=1.0` (0.0-1.0 inclusive)
- **Correlations**: `occurrence_count >= 2` (minimum 2 matches)
- **File Sizes**: `bytes >= 1` (at least 1 byte)
- **Deterministic AI**: `temperature <= 0.0`

Full validation details: [models-quick-reference.md - Validation Constraints](models-quick-reference.md#validation-constraints)

---

## Forensic Compliance

All models enforce:
- **ISO 8601 timestamps** for legal admissibility
- **4-decimal float precision** for consistent confidence scores
- **SHA256 validation** for evidence integrity
- **Chain of custody tracking** for audit trails

Details: [models.md - Validation & Compliance](models.md#validation--compliance)

---

## Related Documentation

### Project Documentation
- **[README.md](../../README.md)** - Getting started
- **[CLAUDE.md](../../CLAUDE.md)** - Project guidance for AI assistants
- **[V3_ARCHITECTURE.md](../../V3_ARCHITECTURE.md)** - Complete architecture
- **[V3_COMPLETE.md](../../V3_COMPLETE.md)** - Refactor summary

### User Guides
- **[docs/user-guides/](../user-guides/)** - End-user documentation

### Development
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)** - How to contribute
- **[tests/](../../tests/)** - Test suite

### Legacy (v2.0)
- **[archive/](../../archive/)** - v2.0 legacy code and docs

---

## Module Dependencies

### Core Models Module
- **Internal**: None (self-contained)
- **External**: `pydantic>=2.0`, `typing`, `enum`, `datetime`

### Who Uses Models
- `evidence_toolkit.core.storage` - Reads/writes models to disk
- `evidence_toolkit.analyzers.*` - Returns analysis models
- `evidence_toolkit.pipeline.*` - Orchestrates using models
- `evidence_toolkit.cli` - Displays model data

Details: [models.md - Related Components](models.md#related-components)

---

## File Locations

**Documentation**:
- `/home/bch/dev/00_RELEASE/evidence-toolkit/docs/api/models.md` (complete reference)
- `/home/bch/dev/00_RELEASE/evidence-toolkit/docs/api/models-quick-reference.md` (cheat sheet)

**Source Code**:
- `/home/bch/dev/00_RELEASE/evidence-toolkit/src/evidence_toolkit/core/models.py` (all models)

**Storage Paths** (model serialization):
- `data/storage/derived/sha256=<hash>/analysis.v1.json` (UnifiedAnalysis)
- `data/storage/derived/sha256=<hash>/evidence_bundle.v1.json` (EvidenceBundle)
- `data/storage/cases/<case-id>/cross_analysis.json` (CorrelationAnalysis)
- `data/packages/<case-id>/case_summary.json` (CaseSummary)

---

## Contributing to Documentation

When updating the models module:

1. **Update models.py** - Make code changes
2. **Update models.md** - Add/modify model documentation
3. **Update models-quick-reference.md** - Update cheat sheet
4. **Update this README** - If new categories added
5. **Run tests** - Ensure validation works: `uv run pytest tests/test_models.py`

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for full guidelines.

---

## Feedback & Support

**Found an issue?** Open an issue on GitHub
**Need clarification?** Check [models.md](models.md) for detailed explanations
**Want a quick answer?** Check [models-quick-reference.md](models-quick-reference.md)

---

**Evidence Toolkit v3.0 API Documentation - Forensic-Grade Evidence Management**

Last Updated: 2025-10-05
