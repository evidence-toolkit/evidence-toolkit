# Cross-Evidence Analysis Schema Architecture

This document provides the complete architecture design for cross-evidence analysis in the Evidence Toolkit, enabling forensic-grade correlation and analysis across multiple evidence types.

## Architecture Overview

The cross-evidence analysis system builds upon the existing evidence bundle architecture to provide:

- **Entity Correlation**: Track entities across multiple evidence pieces
- **Timeline Analysis**: Chronological analysis with pattern detection
- **Narrative Consistency**: Contradiction detection and coherence scoring
- **Risk Assessment**: Forensic integrity and legal exposure evaluation
- **Chain of Custody**: Complete audit trail for cross-analysis processes

## Schema Relationships

```
Evidence Toolkit Schema Hierarchy
├── Individual Evidence Schemas
│   ├── images.v1.json (forensic image analysis)
│   ├── document.v1.json (document analysis)
│   └── [future: email.v1.json, pdf.v1.json, audio.v1.json, video.v1.json]
│
└── Cross-Analysis Schema
    ├── cross-analysis.v1.json (cross-evidence correlation)
    ├── References individual evidence bundles by SHA256
    ├── Maintains independent analysis results
    └── Provides aggregated insights across evidence types
```

### Relationship Model

The cross-analysis schema operates through **reference-based composition**:

1. **Evidence References**: Links to individual evidence bundles via SHA256 and file paths
2. **Independent Analysis**: Cross-analysis results are stored separately from individual evidence
3. **Bi-directional Traceability**: Evidence bundles can be linked to cross-analyses via case_id
4. **Immutable Source**: Original evidence bundles remain unchanged during cross-analysis

## Schema Components

### Core Structure

```json
{
  "schema_version": "1.0.0",
  "case_id": "CASE-2024-001",
  "analysis_metadata": { ... },
  "evidence_references": [ ... ],
  "chain_of_custody": [ ... ],
  "analysis_results": { ... }
}
```

### Evidence References

Each evidence piece is referenced with complete metadata:

```json
{
  "evidence_id": "DOC-001",
  "sha256": "a1b2c3...",
  "evidence_type": "document",
  "bundle_path": "evidence/derived/sha256=a1b2c3.../analysis.v1.json",
  "ingested_at": "2024-01-15T10:30:00Z",
  "source_metadata": { ... }
}
```

### Analysis Results Structure

#### Entity Correlation
- **Correlated Entities**: Entities appearing across multiple evidence pieces
- **Confidence Scoring**: 0.0-1.0 confidence for each correlation
- **Semantic Analysis**: Role analysis and relationship patterns
- **Extraction Tracking**: Method used for entity extraction (NLP, OCR, AI, manual)

#### Timeline Analysis
- **Temporal Events**: Chronologically ordered events with confidence scores
- **Pattern Detection**: Sequence analysis and legal significance assessment
- **Gap Analysis**: Identification of significant timeline gaps
- **Event Types**: Document creation, communication, meetings, deadlines, incidents

#### Narrative Consistency
- **Contradiction Detection**: Temporal, factual, entity, and narrative conflicts
- **Supporting Evidence**: Groups of mutually reinforcing evidence
- **Narrative Themes**: Common themes with keyword analysis
- **Consistency Scoring**: Overall coherence assessment

#### Risk Assessment
- **Risk Factors**: Data integrity, tampering, gaps, conflicts, discrepancies
- **Severity Levels**: Low, medium, high, critical classifications
- **Mitigation Recommendations**: Actionable guidance for identified risks
- **Legal Exposure**: Assessment of potential legal implications

## Validation Strategy

### Multi-Layer Validation

1. **Schema Validation**: JSON Schema validation against cross-analysis.v1.json
2. **Reference Validation**: Verify referenced evidence bundles exist and are valid
3. **Integrity Validation**: Cross-reference SHA256s and ensure data consistency
4. **Forensic Validation**: Chain of custody completeness and actor verification

### Validation Tools

#### Primary Validator: `validate_cross_analysis.py`

```bash
# Schema-only validation
python validate_cross_analysis.py analysis.json --schema-only

# Default validation (schema + integrity)
python validate_cross_analysis.py analysis.json

# Comprehensive validation (schema + references + integrity)
python validate_cross_analysis.py analysis.json --comprehensive
```

#### CI/CD Pipeline: `scripts/validate_cross_analyses.sh`

```bash
# Validate all cross-analysis files in project
./scripts/validate_cross_analyses.sh

# Comprehensive validation with fail-fast
FAIL_FAST=true ./scripts/validate_cross_analyses.sh --comprehensive --force

# Schema-only validation for specific directory
./scripts/validate_cross_analyses.sh --schema-only ./evidence/
```

### Validation Checks

#### Schema Compliance
- JSON Schema Draft-07 validation
- Required field presence
- Data type and format validation
- Enum value compliance
- Pattern matching (SHA256, timestamps)

#### Reference Integrity
- Evidence bundle file existence
- Referenced evidence schema validation
- SHA256 hash verification
- Case ID consistency
- Source metadata accuracy

#### Cross-Reference Validation
- All evidence references used in analysis results
- No orphaned references in analysis
- Confidence score ranges (0.0-1.0)
- Timestamp chronological consistency
- Actor and action audit trail completeness

## Storage Architecture

### File System Layout

```
evidence/
├── raw/sha256=<hash>/                    # Original evidence files
├── derived/sha256=<hash>/               # Individual evidence analysis
│   ├── analysis.v1.json                # Evidence bundle (images/documents)
│   ├── metadata.json                   # Technical metadata
│   └── chain_of_custody.json          # Individual custody trail
├── cross-analysis/                     # Cross-evidence analysis results
│   ├── case-<id>/                      # Organized by case
│   │   ├── cross-analysis.<timestamp>.v1.json
│   │   └── audit_trail.json
│   └── global/                         # Cross-case analyses
└── labels/<label>/                     # Content-based organization
```

### Database Integration

The cross-analysis schema integrates with the existing SQLite evidence catalog:

```sql
-- Extension to existing evidence tables
CREATE TABLE cross_analyses (
    analysis_id TEXT PRIMARY KEY,
    case_id TEXT,
    created_at TIMESTAMP,
    analyst TEXT,
    analysis_type TEXT,
    confidence_overall REAL,
    file_path TEXT,
    evidence_count INTEGER
);

CREATE TABLE cross_analysis_evidence (
    analysis_id TEXT,
    evidence_sha256 TEXT,
    evidence_type TEXT,
    FOREIGN KEY (analysis_id) REFERENCES cross_analyses(analysis_id),
    FOREIGN KEY (evidence_sha256) REFERENCES evidence(sha256)
);
```

## Future Extensibility

### Evidence Type Expansion

The schema is designed to support future evidence types:

#### Planned Evidence Types
- **Email**: Email message analysis with thread correlation
- **PDF**: Multi-page document analysis with embedded content
- **Audio**: Speech-to-text analysis with speaker identification
- **Video**: Multi-modal analysis (visual, audio, metadata)

#### Extension Pattern

New evidence types follow the established pattern:

1. Create type-specific schema (e.g., `email.v1.json`)
2. Add evidence type to cross-analysis enum
3. Implement type-specific entity extraction
4. Update validation tools for new evidence paths

### Analysis Method Extension

#### Additional Analysis Types
- **Communication Network Analysis**: Relationship mapping across evidence
- **Geospatial Analysis**: Location correlation across evidence types
- **Temporal Clustering**: Advanced timeline pattern recognition
- **Sentiment Flow Analysis**: Emotional trajectory across evidence

#### Schema Versioning Strategy

```json
{
  "schema_version": "1.1.0",  // Minor version for backward-compatible additions
  "schema_version": "2.0.0",  // Major version for breaking changes
  "analysis_metadata": {
    "version": "2.1.0",       // Analysis algorithm version
    // ... existing fields ...
    "extensions": {           // Forward-compatibility mechanism
      "geospatial_analysis": { ... },
      "network_analysis": { ... }
    }
  }
}
```

## Implementation Guidelines

### Creating Cross-Analysis Results

1. **Evidence Collection**: Gather all evidence bundles for a case
2. **Validation Pre-Check**: Ensure all referenced evidence is valid
3. **Analysis Execution**: Run cross-correlation algorithms
4. **Result Generation**: Build cross-analysis bundle with all components
5. **Schema Validation**: Validate against canonical schema before storage
6. **Audit Trail**: Record complete chain of custody for the analysis

### Quality Assurance

#### Forensic Standards
- **Deterministic Results**: All analysis must be reproducible
- **Complete Audit Trail**: Every action logged with timestamp and actor
- **Data Integrity**: SHA256 verification at every step
- **Chain of Custody**: Unbroken custody trail for legal admissibility

#### Performance Considerations
- **Incremental Analysis**: Support for adding evidence to existing cross-analysis
- **Caching Strategy**: Cache correlation results for large evidence sets
- **Parallel Processing**: Multi-threaded analysis for large cases
- **Memory Management**: Streaming analysis for very large evidence collections

## Usage Examples

### Basic Cross-Analysis Workflow

```python
from models.cross_analysis_models import CrossAnalysisBundle, AnalysisType

# Create cross-analysis bundle
analysis = CrossAnalysisBundle(
    case_id="CASE-2024-001",
    analysis_metadata=AnalysisMetadata(
        analysis_id="CROSS-001",
        created_at=datetime.now(),
        analyst="forensic-system",
        analysis_type=AnalysisType.COMPREHENSIVE,
        version="1.0.0"
    ),
    evidence_references=[...],
    analysis_results=AnalysisResults(
        confidence_overall=0.85,
        entity_correlation=...,
        timeline_analysis=...,
        narrative_consistency=...,
        risk_assessment=...
    )
)

# Validate before storage
from jsonschema import validate
validate(analysis.dict(), cross_analysis_schema)
```

### CI/CD Integration

```yaml
# .github/workflows/evidence-validation.yml
name: Evidence Validation
on: [push, pull_request]

jobs:
  validate-schemas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install jsonschema pydantic
      - name: Validate Cross-Analysis Files
        run: |
          FAIL_FAST=true ./scripts/validate_cross_analyses.sh --comprehensive --force
```

## Legal Compliance

### Evidence Standards
- **Federal Rules of Evidence**: Maintains admissibility standards
- **Chain of Custody**: Complete audit trail for legal proceedings
- **Data Integrity**: Cryptographic verification of evidence integrity
- **Reproducibility**: All analysis results must be reproducible

### Privacy and Security
- **PII Detection**: Risk flags for personally identifiable information
- **Access Control**: Audit trail includes actor identification
- **Confidentiality**: Support for confidential evidence markers
- **Retention Policy**: Schema supports evidence retention metadata

This architecture provides a robust, extensible foundation for cross-evidence analysis while maintaining the highest standards of forensic integrity and legal admissibility.