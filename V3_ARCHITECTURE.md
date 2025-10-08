# Evidence Toolkit v3.0 - Clean Architecture

**Version:** 3.0.0 | **Refactor Date:** 2025-10-05
**Goal:** Eliminate complexity while keeping perfect AI-powered analysis

---

## Design Principles

1. **Single Package**: `src/evidence_toolkit/` - no nesting
2. **All Pydantic**: Consistent validation everywhere
3. **Visible Data**: `data/` directory visible in git (with .gitkeep)
4. **No Legacy**: Remove retaliation analyzer (archive it)
5. **One Evidence Dir**: Single storage location (no dual directories)

---

## New Structure

```
evidence-toolkit/
├── src/
│   └── evidence_toolkit/           # Single flat package
│       ├── __init__.py
│       │
│       ├── core/                   # Core infrastructure
│       │   ├── __init__.py
│       │   ├── models.py           # ALL Pydantic models unified
│       │   ├── storage.py          # Content-addressed storage
│       │   └── utils.py            # Shared utilities
│       │
│       ├── analyzers/              # AI analysis modules
│       │   ├── __init__.py
│       │   ├── document.py         # Document AI analysis
│       │   ├── image.py            # Image AI analysis (Vision API)
│       │   ├── email.py            # Email AI analysis
│       │   └── correlation.py      # Cross-evidence correlation
│       │
│       ├── pipeline/               # Processing pipeline
│       │   ├── __init__.py
│       │   ├── ingest.py           # File ingestion
│       │   ├── analyze.py          # Analysis orchestration
│       │   └── package.py          # Client deliverable generation
│       │
│       ├── domains/                # Domain configurations
│       │   ├── __init__.py
│       │   └── legal_config.py     # Legal prompts and settings
│       │
│       └── cli.py                  # Single CLI entry point
│
├── data/                           # VISIBLE - Not gitignored!
│   ├── .gitkeep
│   ├── cases/                      # Input: Evidence files
│   │   └── .gitkeep
│   ├── storage/                    # Content-addressed evidence
│   │   ├── raw/                    # Original files (sha256=<hash>/)
│   │   ├── derived/                # Analysis results
│   │   └── .gitkeep
│   └── packages/                   # Output: Client deliverables
│       └── .gitkeep
│
├── archive/                        # Legacy code (not in package)
│   └── retaliation_analyzer.py    # Old standalone analyzer
│
├── tests/                          # Test suite
│   ├── test_analyzers.py
│   ├── test_pipeline.py
│   └── test_models.py
│
├── pyproject.toml                  # Single config
├── quick-start.sh                  # One-command pipeline
└── README.md                       # Clean documentation
```

---

## Key Changes from v2.0

### 1. Package Structure

**Old (v2.0)**:
```
document-evidence-analyzer/src/document_analyzer/
```

**New (v3.0)**:
```
src/evidence_toolkit/
```

**Why**: Simpler imports, easier to navigate, standard Python structure.

### 2. Models Consolidation

**Old (v2.0)**:
- `unified_models.py` - Analysis results
- `evidence_models.py` - Forensic bundles
- `models/cross_analysis_models.py` - Correlation (separate package!)
- `email_models.py` - Email analysis
- Dataclasses mixed with Pydantic

**New (v3.0)**:
```python
# src/evidence_toolkit/core/models.py
# ALL models in one place, ALL Pydantic

# Evidence Types
class EvidenceType(str, Enum): ...

# File Metadata
class FileMetadata(BaseModel): ...

# Analysis Results
class DocumentAnalysis(BaseModel): ...
class ImageAnalysis(BaseModel): ...
class EmailAnalysis(BaseModel): ...
class UnifiedAnalysis(BaseModel): ...

# Forensic Bundles
class EvidenceBundle(BaseModel): ...

# Cross-Evidence Analysis (NOW PYDANTIC!)
class CorrelationAnalysis(BaseModel): ...
class CrossAnalysisBundle(BaseModel): ...

# All others...
```

**Why**: Single source of truth, no hunting for models, consistent Pydantic validation.

### 3. Data Directory Visibility

**Old (v2.0)**:
```
evidence/       # HIDDEN by .gitignore
cases/          # HIDDEN by .gitignore
client_packages/  # HIDDEN by .gitignore
document-evidence-analyzer/evidence/  # ALSO HIDDEN (dual directory confusion!)
```

**New (v3.0)**:
```
data/
├── cases/      # VISIBLE (has .gitkeep)
├── storage/    # VISIBLE (has .gitkeep)
└── packages/   # VISIBLE (has .gitkeep)
```

**Why**: No confusion. You can SEE the structure. Git tracks the skeleton.

### 4. Legacy Code Removal

**Removed**:
- ❌ `retaliation_analyzer.py` → Archived (standalone, not in AI pipeline)
- ❌ Dual evidence directories (nested one gone)
- ❌ Dataclass models (all Pydantic now)

**Kept**:
- ✅ All AI analysis (documents, images, emails)
- ✅ Content-addressed storage
- ✅ Cross-evidence correlation
- ✅ Client package generation
- ✅ Multi-case support

---

## Migration Map

### Analyzers

| Old Location | New Location | Changes |
|-------------|-------------|---------|
| `document_analyzer/document_analyzer_core.py` | `evidence_toolkit/analyzers/document.py` | Cleaned imports |
| `document_analyzer/image_analyzer.py` | `evidence_toolkit/analyzers/image.py` | Cleaned imports |
| `document_analyzer/email_analyzer.py` | `evidence_toolkit/analyzers/email.py` | Cleaned imports |
| `document_analyzer/correlation_analyzer.py` | `evidence_toolkit/analyzers/correlation.py` | **Now uses Pydantic!** |
| `document_analyzer/retaliation_analyzer.py` | `archive/retaliation_analyzer.py` | **REMOVED from package** |

### Core Components

| Old Location | New Location | Changes |
|-------------|-------------|---------|
| `document_analyzer/evidence_manager.py` | `evidence_toolkit/core/storage.py` | Renamed, cleaner API |
| `document_analyzer/unified_models.py` | `evidence_toolkit/core/models.py` | Consolidated with others |
| `document_analyzer/evidence_models.py` | `evidence_toolkit/core/models.py` | Consolidated |
| `models/cross_analysis_models.py` | `evidence_toolkit/core/models.py` | Consolidated |
| `document_analyzer/email_models.py` | `evidence_toolkit/core/models.py` | Consolidated |

### Pipeline

| Old Location | New Location | Changes |
|-------------|-------------|---------|
| `document_analyzer/cli.py` (ingest) | `evidence_toolkit/pipeline/ingest.py` | Separated concerns |
| `document_analyzer/cli.py` (analyze) | `evidence_toolkit/pipeline/analyze.py` | Separated concerns |
| `document_analyzer/client_packager.py` | `evidence_toolkit/pipeline/package.py` | Renamed |
| `document_analyzer/cli.py` | `evidence_toolkit/cli.py` | Cleaned, delegates to pipeline |

---

## Import Changes

### Old (v2.0)
```python
from document_analyzer.evidence_manager import EvidenceManager
from document_analyzer.unified_models import UnifiedAnalysis
from models.cross_analysis_models import CrossAnalysisBundle
```

### New (v3.0)
```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import UnifiedAnalysis, CrossAnalysisBundle
```

**Why**: Shorter, clearer, everything in one package.

---

## CLI Changes

### Commands Stay The Same!

```bash
# Still works exactly the same
evidence-toolkit process-case cases/MY-CASE --case-id MY-CASE
evidence-toolkit ingest cases/MY-CASE --case-id MY-CASE
evidence-toolkit analyze <sha256> --case-id MY-CASE
evidence-toolkit correlate --case-id MY-CASE
evidence-toolkit package --case-id MY-CASE

# Quick start unchanged
./quick-start.sh cases/MY-CASE MY-CASE
```

**Removed**:
```bash
# This is gone (archived)
evidence-toolkit retaliation ./documents
```

---

## Validation Improvements

### Correlation Analysis - NOW PYDANTIC! ✅

**Old (v2.0)** - Dataclass:
```python
@dataclass
class CorrelationResult:
    case_id: str
    entity_correlations: List[EntityCorrelation]
    # No runtime validation!
```

**New (v3.0)** - Pydantic:
```python
class CorrelationAnalysis(BaseModel):
    case_id: str
    entity_correlations: List[CorrelatedEntity]
    # ✅ Full runtime validation
    # ✅ Schema compliance
    # ✅ IDE autocomplete
```

---

## Benefits

1. **Clearer Structure**: One package, logical organization
2. **Consistent Validation**: All Pydantic, no dataclasses
3. **No Hidden Directories**: `data/` visible with .gitkeep
4. **No Legacy Confusion**: Retaliation analyzer archived
5. **Easier Maintenance**: Single models file, clear separation
6. **Better DX**: Shorter imports, better IDE support

---

## Implementation Steps

1. ✅ Create refactor branch
2. Create new `src/evidence_toolkit/` structure
3. Consolidate all models → `core/models.py`
4. Move analyzers with Pydantic updates
5. Move pipeline components
6. Update CLI
7. Update `pyproject.toml`
8. Test full pipeline
9. Update documentation
10. Merge to main

---

**This architecture keeps everything you love, removes everything that confuses.**
