# Client Package Generator

## Overview

The Client Package Generator creates professional forensic evidence packages suitable for legal proceedings and consulting engagements. It assembles all case analysis results, visualizations, reports, and documentation into a comprehensive deliverable package with optional inclusion of raw evidence files. The generator produces both directory-based packages and ZIP archives with complete metadata and documentation.

This module serves as the final stage of the Evidence Toolkit pipeline, transforming analytical results into client-ready deliverables with professional formatting and complete audit trails.

## Purpose & Scope

### What Package Generation Does
- Assembles complete case analysis into professional package
- Generates executive summaries and detailed reports
- Copies analysis files, visualizations, and evidence catalog
- Creates comprehensive documentation (README, methodology)
- Produces ZIP archives or directory packages
- Includes optional raw evidence files
- Generates package metadata for tracking

### What Package Generation Does NOT Do
- Evidence analysis (handled by analysis pipeline)
- Correlation analysis (handled by summary pipeline)
- Evidence modification or validation
- Package delivery or distribution

### Design Principles
1. **Professional Output**: Court-ready deliverables
2. **Complete Documentation**: Self-contained packages
3. **Flexible Formats**: ZIP or directory output
4. **Forensic Integrity**: Chain of custody preservation
5. **Client-Focused**: Organized for non-technical reviewers

## Module Structure

```
evidence_toolkit/pipeline/package.py
│
└── PackageGenerator              # Main package creation class
    ├─→ create_client_package()   # Main package creation
    ├─→ _create_package_structure()
    ├─→ _create_package_components()
    ├─→ _copy_evidence_analysis()
    ├─→ _copy_visualizations()
    ├─→ _create_evidence_catalog()
    ├─→ _create_correlation_report()
    ├─→ _create_documentation()
    ├─→ _copy_raw_evidence()
    ├─→ _create_zip_package()
    └─→ _create_package_metadata()
```

### Integration Points
```
src/evidence_toolkit/
├── pipeline/
│   ├── package.py               # This module
│   └── summary.py               # SummaryGenerator
│
├── core/
│   ├── models.py                # CaseSummary, CorrelationAnalysis
│   └── storage.py               # EvidenceStorage
│
└── cli.py                       # Package command
```

## API Reference

### `PackageGenerator`

Main class for creating client packages.

**Initialization:**
```python
class PackageGenerator:
    def __init__(self, storage: EvidenceStorage, openai_client=None):
        """Initialize package generator.

        Args:
            storage: EvidenceStorage instance for accessing evidence
            openai_client: Optional OpenAI client for AI summaries
        """
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `storage` | `EvidenceStorage` | Storage instance for evidence access |
| `summary_generator` | `SummaryGenerator` | Generator for case summaries |

---

### `PackageGenerator.create_client_package()`

Create comprehensive client package for a case.

**Signature:**
```python
def create_client_package(
    self,
    case_id: str,
    output_directory: Path,
    include_raw_evidence: bool = False,
    package_format: str = "zip"
) -> Dict[str, Any]
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `case_id` | `str` | Yes | - | Case identifier to package |
| `output_directory` | `Path` | Yes | - | Directory to create package in |
| `include_raw_evidence` | `bool` | No | `False` | Include original evidence files |
| `package_format` | `str` | No | `"zip"` | Format: 'zip' or 'directory' |

**Returns:**

| Type | Description |
|------|-------------|
| `Dict[str, Any]` | Package creation results with path, metadata, and component list |

**Return Dictionary:**
```python
{
    "success": True,
    "package_path": "/path/to/package.zip",
    "case_id": "CASE-001",
    "evidence_count": 10,
    "components": {
        "reports": ["executive_summary.txt"],
        "analysis": ["case_analysis.json", ...],
        "visualizations": [...],
        "evidence_catalog": ["evidence_catalog.json"],
        "correlations": ["correlation_analysis.json"],
        "documentation": ["README.md", "methodology.md"],
        "raw_evidence": [...]  # If include_raw_evidence=True
    },
    "metadata": {...}
}
```

**Exceptions:**

| Exception | When Raised |
|-----------|-------------|
| `Exception` | If package creation fails (cleans up partial package) |

**Example:**
```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

packager = PackageGenerator(storage, openai_client)
result = packager.create_client_package(
    case_id="CASE-001",
    output_directory=Path("data/packages"),
    include_raw_evidence=True,
    package_format="zip"
)

print(f"Package created: {result['package_path']}")
print(f"Evidence count: {result['evidence_count']}")
print(f"Components: {result['components']}")
```

## Package Structure

### Directory Layout

```
<case-id>_analysis_package_<timestamp>/
│
├── reports/                     # Executive summaries and reports
│   └── executive_summary.txt
│
├── analysis/                    # JSON analysis files
│   ├── case_analysis.json
│   ├── document_contract.pdf_2401112d.json
│   ├── email_thread.eml_7f3a8b9e.json
│   └── image_screenshot.jpg_9c8d6e5f.json
│
├── visualizations/              # Charts, word clouds, etc.
│   ├── document_contract_word_cloud.png
│   ├── document_contract_word_frequency.png
│   └── ...
│
├── evidence_catalog/            # Evidence inventory and metadata
│   └── evidence_catalog.json
│
├── correlations/                # Cross-evidence correlation
│   └── correlation_analysis.json
│
├── documentation/               # Package documentation
│   ├── README.md
│   └── methodology.md
│
├── raw_evidence/                # Original files (optional)
│   ├── document_contract.pdf
│   ├── email_thread.eml
│   └── image_screenshot.jpg
│
└── package_metadata.json        # Package metadata
```

### Package Naming Convention

```
<case-id>_analysis_package_<timestamp>.zip

Example:
CASE-2025-001_analysis_package_20251005_143000.zip
```

## Behavior

### Package Creation Flow

```
create_client_package(case_id, ...)
  ↓
1. Create package directory
   └─→ _create_package_structure()
       ├─→ reports/
       ├─→ analysis/
       ├─→ visualizations/
       ├─→ evidence_catalog/
       ├─→ correlations/
       ├─→ documentation/
       └─→ raw_evidence/
  ↓
2. Generate case summary
   └─→ SummaryGenerator.generate_case_summary()
  ↓
3. Create package components
   └─→ _create_package_components()
       ├─→ Executive summary report
       ├─→ Detailed JSON analysis
       ├─→ Individual evidence analysis
       ├─→ Visualizations (word clouds, charts)
       ├─→ Evidence catalog
       ├─→ Correlation report
       ├─→ Documentation (README, methodology)
       └─→ Raw evidence (optional)
  ↓
4. Create package metadata
   └─→ _create_package_metadata()
  ↓
5. Package output
   ├─→ ZIP: Create archive, remove directory
   └─→ Directory: Keep directory as-is
  ↓
6. Return results
```

### Component Generation

**1. Executive Summary Report** (`reports/executive_summary.txt`):
```python
# Generated using SummaryGenerator.format_summary_report()
formatted_report = summary_generator.format_summary_report(case_summary)
Path("reports/executive_summary.txt").write_text(formatted_report)
```

**2. Detailed JSON Analysis** (`analysis/case_analysis.json`):
```python
# Full case summary in JSON format
summary_generator.export_summary_to_json(
    case_summary,
    Path("analysis/case_analysis.json")
)
```

**3. Individual Evidence Analysis** (`analysis/`):
```python
# Copy individual analysis files with descriptive names
# Format: {type}_{filename}_{sha256}.json
for evidence in case_summary.evidence_summaries:
    src = storage.derived_dir / f"sha256={evidence.sha256}" / "analysis.v1.json"
    dst = package_dir / "analysis" / f"{evidence.evidence_type}_{safe_filename}_{sha256[:8]}.json"
    shutil.copy2(src, dst)
```

**4. Visualizations** (`visualizations/`):
```python
# Copy word clouds, frequency charts, etc.
for evidence in case_summary.evidence_summaries:
    if evidence.evidence_type == "document":
        # Look for visualization files
        viz_files = evidence_dir.glob("*.png")
        for viz_file in viz_files:
            # Copy with descriptive name
            dst_name = f"{evidence.evidence_type}_{safe_filename}_{viz_file.name}"
            shutil.copy2(viz_file, package_dir / "visualizations" / dst_name)
```

**5. Evidence Catalog** (`evidence_catalog/evidence_catalog.json`):
```python
catalog = {
    "case_id": case_id,
    "catalog_generated": datetime.now().isoformat(),
    "total_evidence_pieces": evidence_count,
    "evidence_types": evidence_types,
    "evidence_inventory": [
        {
            "filename": evidence.filename,
            "evidence_type": evidence.evidence_type,
            "sha256": evidence.sha256,
            "file_size_bytes": evidence.file_size,
            "analysis_confidence": evidence.analysis_confidence,
            "legal_significance": evidence.legal_significance,
            "risk_flags": evidence.risk_flags,
            "key_findings_summary": evidence.key_findings[:3],
            "chain_of_custody": f"derived/sha256={sha256}/chain_of_custody.json"
        }
        for evidence in case_summary.evidence_summaries
    ]
}
```

**6. Correlation Report** (`correlations/correlation_analysis.json`):
```python
# v3.1: Preserves all fields using Pydantic model_dump()
correlation_dict = case_summary.correlation_result.model_dump(mode='json')

# Truncate SHA256 hashes for readability (8 chars)
for corr in correlation_dict["entity_correlations"]:
    for occ in corr["evidence_occurrences"]:
        occ["evidence_sha256"] = occ["evidence_sha256"][:8]

for event in correlation_dict["timeline_events"]:
    event["evidence_sha256"] = event["evidence_sha256"][:8]

# v3.1: Truncate SHA256s in legal_patterns if present
if correlation_dict.get("legal_patterns"):
    for contradiction in correlation_dict["legal_patterns"].get("contradictions", []):
        contradiction["statement_1_source"] = contradiction["statement_1_source"][:8]
        contradiction["statement_2_source"] = contradiction["statement_2_source"][:8]

    for corroboration in correlation_dict["legal_patterns"].get("corroboration", []):
        corroboration["supporting_evidence"] = [
            sha[:8] for sha in corroboration["supporting_evidence"]
        ]

# Save with formatting
json.dump(correlation_dict, f, indent=2)
```

**v3.1 Enhancement:**
The correlation report now uses `model_dump(mode='json')` to properly serialize all Pydantic models, preserving v3.1 enhancement data:
- `legal_patterns`: AI-detected contradictions and corroborations
- `temporal_sequences`: Event patterns and sequences
- `timeline_gaps`: Identified timeline gaps

All SHA256 hashes are truncated to 8 characters for readability in client reports.

**Example Correlation Report (v3.1):**
```json
{
  "case_id": "CASE-001",
  "analysis_timestamp": "2025-10-05T14:30:00Z",
  "evidence_count": 10,
  "entity_correlations": [
    {
      "entity_name": "John Doe",
      "entity_type": "person",
      "occurrence_count": 5,
      "confidence_average": 0.95,
      "evidence_occurrences": [
        {"evidence_sha256": "2401112d", "context": "..."},
        {"evidence_sha256": "7f3a8b9e", "context": "..."}
      ]
    }
  ],
  "timeline_events": [
    {
      "timestamp": "2024-03-15T10:30:00Z",
      "evidence_sha256": "2401112d",
      "evidence_type": "email",
      "event_type": "communication",
      "description": "Termination notification email sent",
      "confidence": 0.92
    }
  ],
  "legal_patterns": {
    "contradictions": [
      {
        "statement_1": "No prior performance issues documented",
        "statement_1_source": "2401112d",
        "statement_2": "Multiple warnings issued over 6 months",
        "statement_2_source": "7f3a8b9e",
        "severity": "high",
        "confidence": 0.88
      }
    ],
    "corroboration": [
      {
        "claim": "Termination decision made after harassment complaint",
        "supporting_evidence": ["2401112d", "7f3a8b9e", "9c8d6e5f"],
        "confidence": 0.91
      }
    ]
  },
  "temporal_sequences": [
    {
      "sequence_type": "causal_chain",
      "events": [...],
      "confidence": 0.85
    }
  ],
  "timeline_gaps": [
    {
      "gap_start": "2024-03-01T00:00:00Z",
      "gap_end": "2024-03-15T00:00:00Z",
      "gap_duration_days": 14,
      "significance": "high",
      "context": "No evidence between harassment complaint and termination"
    }
  ]
}
```

**7. Documentation** (`documentation/`):
- `README.md` - Package overview, structure, key files
- `methodology.md` - Analysis methodology and technical standards

**8. Raw Evidence** (`raw_evidence/`, optional):
```python
if include_raw_evidence:
    for evidence in case_summary.evidence_summaries:
        src = storage.raw_dir / f"sha256={evidence.sha256}" / "original.*"
        dst = package_dir / "raw_evidence" / f"{evidence.evidence_type}_{evidence.filename}"
        shutil.copy2(src, dst)
```

### ZIP Archive Creation

```python
def _create_zip_package(package_dir: Path, zip_path: Path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path for archive
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
```

**Compression:**
- Uses `zipfile.ZIP_DEFLATED` for compression
- Preserves directory structure in archive
- File paths are relative to package root

### Error Handling & Cleanup

```python
try:
    # Create package
    _create_package_structure(package_dir)
    components = _create_package_components(...)
    # ...
except Exception as e:
    # Clean up on error
    if package_dir.exists():
        shutil.rmtree(package_dir)
    raise Exception(f"Failed to create client package: {e}")
```

**Error Safety:**
- Cleans up partial packages on failure
- Preserves original evidence (read-only operations)
- Safe to retry after failure

## Data Models

### Package Metadata

```json
{
  "package_info": {
    "created": "2025-10-05T14:30:00.123456Z",
    "case_id": "CASE-001",
    "evidence_count": 10,
    "evidence_types": ["document", "email", "image"],
    "generator": "Evidence Toolkit v3.0"
  },
  "analysis_summary": {
    "overall_legal_significance": "high",
    "total_risk_flags": 15,
    "entity_correlations": 12,
    "timeline_events": 25,
    "ai_analysis_included": true
  },
  "package_components": {
    "reports": ["executive_summary.txt"],
    "analysis": ["case_analysis.json", ...],
    "visualizations": [...],
    "evidence_catalog": ["evidence_catalog.json"],
    "correlations": ["correlation_analysis.json"],
    "documentation": ["README.md", "methodology.md"],
    "raw_evidence": [...]
  },
  "file_counts": {
    "reports": 1,
    "analysis": 11,
    "visualizations": 5,
    "evidence_catalog": 1,
    "correlations": 1,
    "documentation": 2,
    "raw_evidence": 10
  }
}
```

### Evidence Catalog Schema

```json
{
  "case_id": "CASE-001",
  "catalog_generated": "2025-10-05T14:30:00Z",
  "total_evidence_pieces": 10,
  "evidence_types": ["document", "email", "image"],
  "evidence_inventory": [
    {
      "filename": "contract.pdf",
      "evidence_type": "document",
      "sha256": "2401112d2c3bcc883a713fc238830307c1d596f74b28110d3137675529191c8c",
      "file_size_bytes": 102400,
      "analysis_confidence": 0.92,
      "legal_significance": "high",
      "risk_flags": ["retaliation", "termination"],
      "key_findings_summary": [
        "Employment termination letter with retaliatory language",
        "Extracted 15 entities including John Doe and Acme Corp",
        "High legal significance for wrongful termination case"
      ],
      "chain_of_custody": "derived/sha256=2401112d.../chain_of_custody.json"
    },
    {
      "filename": "email_thread.eml",
      "evidence_type": "email",
      "sha256": "7f3a8b9e...",
      "file_size_bytes": 25600,
      "analysis_confidence": 0.88,
      "legal_significance": "critical",
      "risk_flags": ["escalation", "harassment", "time_sensitive"],
      "key_findings_summary": [
        "Email thread with 5 participants",
        "Communication pattern: escalation",
        "Escalating conflict with retaliatory language detected"
      ],
      "chain_of_custody": "derived/sha256=7f3a8b9e.../chain_of_custody.json"
    }
  ]
}
```

**v3.1 Email Example:**
Email evidence now includes participant count extracted from the full `EmailThreadAnalysis` model, communication patterns, and comprehensive risk flags.

## Documentation Templates

### README.md Template

```markdown
# Evidence Analysis Package - Case {case_id}

## Package Contents

This package contains comprehensive forensic analysis of case {case_id}, generated on {timestamp}.

### Directory Structure

- **reports/**: Executive summaries and formatted reports
- **analysis/**: Detailed JSON analysis files for each piece of evidence
- **visualizations/**: Charts, word clouds, and other visual analysis outputs
- **evidence_catalog/**: Complete inventory of evidence with metadata
- **correlations/**: Cross-evidence correlation analysis and timeline reconstruction
- **documentation/**: This README and methodology documentation
- **raw_evidence/**: Original evidence files (if included)

### Evidence Summary

- **Total Evidence Pieces**: {evidence_count}
- **Evidence Types**: {evidence_types}
- **Cross-Evidence Correlations**: {correlation_count}
- **Timeline Events**: {timeline_events}

### Key Files

1. **reports/executive_summary.txt**: Main case summary with AI-generated insights
2. **analysis/case_analysis.json**: Complete structured analysis data
3. **evidence_catalog/evidence_catalog.json**: Comprehensive evidence inventory
4. **correlations/correlation_analysis.json**: Cross-evidence correlation results

### Methodology

This analysis was performed using the Evidence Toolkit, a forensic-grade evidence analysis system that provides:

- Content-addressed evidence storage with complete chain of custody
- AI-powered analysis using OpenAI's deterministic analysis models (temperature=0)
- Cross-evidence entity correlation and timeline reconstruction
- Professional legal significance assessment and risk evaluation

### Legal Compliance

All analysis results are generated using forensic-grade processes suitable for legal proceedings:

- Deterministic AI analysis with confidence scoring
- Complete audit trails and chain of custody documentation
- Schema validation for all structured outputs
- Professional risk assessment and legal significance evaluation

---
Generated: {timestamp}
Package Format: Professional Legal Evidence Analysis
```

### Methodology.md Template

```markdown
# Analysis Methodology

## Evidence Toolkit Analysis Process

### 1. Evidence Ingestion
- Content-addressed storage using SHA256 hashing
- Metadata extraction and preservation
- Chain of custody initialization

### 2. Individual Evidence Analysis
- **Documents**: Text analysis, word frequency, concept extraction
- **Images**: AI-powered scene analysis, OCR, object detection
- **Emails**: Thread reconstruction, sentiment analysis, escalation detection

### 3. Cross-Evidence Correlation
- Entity extraction and matching across evidence types
- Timeline reconstruction from metadata and content
- Pattern detection and relationship analysis
- AI-powered legal pattern detection (v3.1):
  - Contradiction identification across evidence
  - Corroboration detection for mutually supporting evidence
- Temporal sequence and timeline gap analysis (v3.1)

### 4. AI-Powered Insights
- OpenAI Responses API with deterministic settings (temperature=0)
- Legal significance assessment
- Risk evaluation and compliance checking
- Professional recommendations generation

### 5. Quality Assurance
- Schema validation for all structured outputs
- Confidence scoring for all analysis results
- Complete audit trail maintenance
- Professional report generation

## Technical Standards

- **Deterministic Analysis**: All AI analysis uses temperature=0 for reproducible results
- **Forensic Grade**: Complete chain of custody and audit trails
- **Schema Validation**: All outputs validated against canonical schemas
- **Professional Output**: Court-ready reports and documentation

## Legal Compliance

This methodology is designed for professional legal evidence analysis and maintains standards suitable for court proceedings.
```

## Validation & Compliance

### Input Validation
- Case ID must be non-empty
- Case must have generated case summary
- Output directory must be writable
- Package format must be 'zip' or 'directory'

### Output Validation
- All component files must be created successfully
- Package metadata must be valid JSON
- ZIP archive (if created) must be valid

### Forensic Integrity
- Original evidence is never modified (read-only access)
- Chain of custody is preserved (referenced, not copied)
- SHA256 hashes ensure evidence integrity
- Package metadata provides complete audit trail

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `Exception` (generic) | Package creation failed | Check error message, verify disk space, retry |
| `PermissionError` | Cannot write to output directory | Check permissions, use different directory |
| `FileNotFoundError` | Missing analysis or evidence file | Re-analyze evidence, verify case completeness |
| `zipfile.BadZipFile` | ZIP creation failed | Check disk space, verify file system |

### Error Handling Pattern

```python
try:
    result = packager.create_client_package(
        case_id="CASE-001",
        output_directory=Path("data/packages"),
        package_format="zip"
    )
    print(f"✅ Package created: {result['package_path']}")
except PermissionError:
    print(f"❌ Permission denied. Check output directory permissions.")
except Exception as e:
    print(f"❌ Package creation failed: {e}")
```

### Logging

Package operations use emoji-prefixed output:
- `📦` - Package operations
- `✅` - Success
- `⚠️` - Warning
- `❌` - Error

## Performance Considerations

### Time Complexity
- **Component assembly**: O(n) where n = number of evidence
- **File copying**: O(m) where m = total file size
- **ZIP creation**: O(m) for compression
- **Overall**: Dominated by file I/O

### Space Complexity
- **Package size**: 1.5-3× analysis size (includes docs, visualizations)
- **ZIP compression**: ~60-70% of uncompressed size
- **With raw evidence**: +100% (original files included)

### Disk Usage Example

```
Case with 10 evidence pieces (100 MB total):
- Analysis files: ~500 KB
- Visualizations: ~2 MB
- Documentation: ~50 KB
- Package metadata: ~20 KB
- Total (no raw): ~2.5 MB
- Total (with raw): ~102.5 MB
- ZIP (no raw): ~1.5 MB
- ZIP (with raw): ~70 MB (compression varies by file type)
```

### Optimization Notes
- File copying uses `shutil.copy2()` (efficient buffered I/O)
- ZIP uses `ZIP_DEFLATED` for compression
- Visualizations copied only if they exist (optional)
- Raw evidence inclusion is optional (reduces package size)

## Storage & Persistence

### Output Locations

```
data/packages/
├── CASE-001_analysis_package_20251005_143000.zip
├── CASE-002_analysis_package_20251005_150000/  # Directory format
└── ...
```

### Package Formats

**ZIP Archive** (default):
```bash
CASE-001_analysis_package_20251005_143000.zip
├── reports/
├── analysis/
├── visualizations/
├── evidence_catalog/
├── correlations/
├── documentation/
└── package_metadata.json
```

**Directory** (package_format="directory"):
```bash
CASE-001_analysis_package_20251005_143000/
├── reports/
├── analysis/
├── visualizations/
├── evidence_catalog/
├── correlations/
├── documentation/
└── package_metadata.json
```

## Testing

### Unit Tests

```python
import tempfile
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

def test_create_zip_package():
    """Test ZIP package creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage()
        packager = PackageGenerator(storage, openai_client=None)

        # Create package
        result = packager.create_client_package(
            case_id="TEST-001",
            output_directory=Path(tmpdir),
            package_format="zip"
        )

        # Verify
        assert result["success"]
        assert Path(result["package_path"]).exists()
        assert result["package_path"].endswith(".zip")
        assert result["evidence_count"] > 0

def test_create_directory_package():
    """Test directory package creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage()
        packager = PackageGenerator(storage, openai_client=None)

        # Create package
        result = packager.create_client_package(
            case_id="TEST-001",
            output_directory=Path(tmpdir),
            package_format="directory"
        )

        # Verify
        assert result["success"]
        package_path = Path(result["package_path"])
        assert package_path.exists()
        assert package_path.is_dir()
        assert (package_path / "package_metadata.json").exists()
```

### Integration Tests

```bash
# Full pipeline test with package
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify package
ls -la data/packages/
unzip -l data/packages/TEST-CASE_*.zip
```

### Test Coverage
- Package creation: ✅ Covered
- Component assembly: ✅ Covered
- ZIP creation: ✅ Covered
- Directory creation: ✅ Covered
- Error handling: ⚠️ Partial (needs more edge cases)

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.storage.EvidenceStorage` - Storage access
- `evidence_toolkit.pipeline.summary.SummaryGenerator` - Case summaries
- `evidence_toolkit.core.models.CaseSummary` - Case summary model

### External Dependencies
- `shutil` - File copying
- `zipfile` - ZIP archive creation
- `json` - JSON serialization
- `pathlib` - Path operations

## CLI Integration

```bash
# Create ZIP package (default)
uv run evidence-toolkit package --case-id CASE-001

# Create directory package
uv run evidence-toolkit package --case-id CASE-001 --format directory

# Include raw evidence
uv run evidence-toolkit package --case-id CASE-001 --include-raw

# Custom output directory
uv run evidence-toolkit package --case-id CASE-001 --output-dir /custom/path
```

**CLI Implementation** (`cli.py`):
```python
@app.command()
def package(
    case_id: str,
    output_dir: Path = Path("data/packages"),
    format: str = "zip",
    include_raw: bool = False
):
    """Create client package."""
    storage = EvidenceStorage()
    openai_client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

    packager = PackageGenerator(storage, openai_client)
    result = packager.create_client_package(
        case_id=case_id,
        output_directory=output_dir,
        include_raw_evidence=include_raw,
        package_format=format
    )

    print(f"📦 Package created: {result['package_path']}")
    print(f"   Evidence count: {result['evidence_count']}")
    print(f"   Components: {len(result['components'])} types")
```

## Migration Notes

### v2.0 → v3.0 Changes

**Old (v2.0):**
```python
from document_analyzer.client_packager import ClientPackager

packager = ClientPackager(evidence_manager)
packager.create_package(case_id="...")
```

**New (v3.0):**
```python
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
packager = PackageGenerator(storage)
result = packager.create_client_package(case_id="...")
```

**Breaking Changes:**
- Class renamed: `ClientPackager` → `PackageGenerator`
- Method renamed: `create_package()` → `create_client_package()`
- Import path changed: `document_analyzer.client_packager` → `evidence_toolkit.pipeline`
- Now uses `EvidenceStorage` instead of `EvidenceManager`
- Return type changed (now returns dict with detailed results)

**New Features (v3.1):**
- Legal patterns preserved in correlation report using `model_dump()`
- Temporal sequences included in correlation analysis
- Timeline gaps documented for investigative follow-up
- SHA256 hash truncation in all pattern data for readability
- Email participant data from full `EmailThreadAnalysis` model
- Enhanced documentation templates with v3.1 features

## Future Considerations

### Planned Enhancements
- **HTML packages**: Interactive web-based deliverables
- **PDF reports**: Professional PDF generation
- **Custom templates**: User-defined package structures
- **Digital signatures**: Package signing for authenticity
- **Encryption**: Encrypted packages for sensitive evidence

### Known Limitations
- Large cases may have slow package creation (file I/O bound)
- ZIP format has 4 GB limit (use directory format for larger cases)
- No incremental updates (must regenerate entire package)
- Documentation templates are fixed (not customizable)

### Technical Debt
- Some duplicate code in `_copy_*` methods (could be refactored)
- Hard-coded documentation templates (should be configurable)
- No streaming ZIP creation (loads entire package in memory)

## Examples

### Example 1: Basic ZIP Package
```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
packager = PackageGenerator(storage)

result = packager.create_client_package(
    case_id="CASE-001",
    output_directory=Path("data/packages"),
    package_format="zip"
)

print(f"Package: {result['package_path']}")
print(f"Size: {Path(result['package_path']).stat().st_size / 1024 / 1024:.2f} MB")
```

### Example 2: Directory Package with Raw Evidence
```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
packager = PackageGenerator(storage)

result = packager.create_client_package(
    case_id="CASE-001",
    output_directory=Path("data/packages"),
    include_raw_evidence=True,  # Include original files
    package_format="directory"   # Keep as directory
)

# Package remains as directory for easy browsing
package_path = Path(result['package_path'])
print(f"Package directory: {package_path}")
print(f"Raw evidence files: {len(result['components']['raw_evidence'])}")
```

### Example 3: Custom Output Location
```python
from pathlib import Path
from evidence_toolkit.pipeline import PackageGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
packager = PackageGenerator(storage)

# Custom output directory
custom_output = Path("/mnt/client-deliverables")
custom_output.mkdir(parents=True, exist_ok=True)

result = packager.create_client_package(
    case_id="CASE-001",
    output_directory=custom_output,
    package_format="zip"
)

print(f"Package delivered to: {result['package_path']}")
```

---

**This documentation provides complete reference for the client package generator, covering all package creation logic, component assembly, documentation generation, and delivery formats in Evidence Toolkit v3.0.**
