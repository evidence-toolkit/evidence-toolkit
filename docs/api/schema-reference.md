# Evidence Toolkit Schema Architecture Summary

## Complete Schema System Overview

The Evidence Toolkit now features a comprehensive 3-tier schema architecture designed for forensic-grade evidence analysis:

### Tier 1: Individual Evidence Schemas
- **`images.v1.json`** - Forensic image analysis with AI-powered content detection
- **`document.v1.json`** - Document analysis with entity extraction and sentiment analysis
- **Email Analysis** - Currently implemented using UnifiedAnalysis format (email.v1.json planned)
- **Future**: `pdf.v1.json`, `audio.v1.json`, `video.v1.json`

### Tier 2: Cross-Evidence Analysis Schema
- **`cross-analysis.v1.json`** - Multi-evidence correlation and analysis

### Tier 3: Case-Level Aggregation (Future)
- Planned: `case-analysis.v1.json` for complete case summaries

## Schema Relationship Diagram

```
Evidence Toolkit Schema Architecture
╭─────────────────────────────────────────────────────────────╮
│                    Case Level (Future)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             case-analysis.v1.json                   │   │
│  │          (Complete case aggregation)                │   │
│  └─────────────────┬───────────────────────────────────┘   │
│                    │                                       │
│                    ▼                                       │
│                Cross-Evidence Level                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            cross-analysis.v1.json                   │   │
│  │     • Entity correlation across evidence            │   │
│  │     • Timeline analysis and pattern detection       │   │
│  │     • Narrative consistency scoring                 │   │
│  │     • Risk assessment and legal considerations      │   │
│  └─────┬───────────────────────────────┬───────────────┘   │
│        │                               │                   │
│        ▼                               ▼                   │
│  Individual Evidence Level                                 │
│  ┌─────────────┐              ┌─────────────────────────┐  │
│  │images.v1.json│              │   document.v1.json      │  │
│  │• Image content│              │  • Text analysis        │  │
│  │• Object detect│              │  • Entity extraction    │  │
│  │• OCR analysis │              │  • Sentiment analysis   │  │
│  │• Risk flags   │              │  • Legal significance   │  │
│  └─────────────┘              └─────────────────────────┘  │
│                                                            │
│        Evidence References (SHA256 + case_id)             │
╰─────────────────────────────────────────────────────────────╯
```

## Evidence Storage Pattern

### Evidence Directory Structure
Each piece of evidence creates a complete forensic package:

```
evidence/derived/sha256=<hash>/
├── analysis.v1.json        # Internal working format (UnifiedAnalysis)
├── evidence_bundle.v1.json # Schema-compliant forensic bundle
├── metadata.json           # File metadata (size, timestamps, MIME type)
└── chain_of_custody.json   # Complete audit trail
```

**Internal Analysis File (`analysis.v1.json`)**:
- Used by correlation analyzer and internal processing
- Contains rich analysis metadata and cross-references
- Flexible format optimized for computational processing

**Forensic Bundle File (`evidence_bundle.v1.json`)**:
- Strictly validates against schema (document.v1.json, images.v1.json)
- Used for client packages and legal deliverables
- Maintains forensic integrity and legal admissibility

## Key Design Principles

### 1. Reference-Based Architecture
- **Cross-analysis references individual evidence by SHA256**
- **No duplication of evidence data across schema levels**
- **Bi-directional traceability via case_id**
- **Immutable source evidence bundles**

### 2. Forensic Integrity
- **Complete chain of custody at every level**
- **SHA256 verification for all evidence references**
- **Deterministic analysis results (temperature=0)**
- **Comprehensive audit trails**

### 3. Schema Compliance
- **JSON Schema Draft-07 validation**
- **Strict additionalProperties: false**
- **Required field enforcement**
- **Pattern validation for SHA256, timestamps**

### 4. Future Extensibility
- **Evidence type enumeration supports new types**
- **Analysis method extension points**
- **Schema versioning strategy**
- **Backward compatibility mechanisms**

## Implementation Files

### Core Schema Files (Actual Locations)
```
# Cross-evidence analysis schema (root level)
schemas/cross-analysis.v1.json

# Individual evidence schemas (component-specific)
document-evidence-analyzer/schemas/document.v1.json    # Document evidence schema
image-analysis/schemas/images.v1.json                  # Image evidence schema
```

### Validation Infrastructure
```
├── validate_cross_analysis.py      # Primary validation script
├── scripts/validate_cross_analyses.sh  # CI/CD validation pipeline
└── test_cross_analysis_schema.py   # Schema testing framework
```

### Type-Safe Models
```
models/
└── cross_analysis_models.py        # Pydantic models for cross-analysis
```

### Examples and Documentation
```
├── examples/cross-analysis-example.json  # Working example
├── CROSS_ANALYSIS_SCHEMA_DESIGN.md      # Detailed architecture
└── SCHEMA_ARCHITECTURE_SUMMARY.md       # This file
```

## Validation Strategy

### 3-Layer Validation
1. **Schema Validation**: JSON Schema compliance
2. **Reference Validation**: Evidence bundle existence and validity
3. **Integrity Validation**: Cross-reference consistency and forensic requirements

### Validation Commands
```bash
# Cross-analysis validation (root level)
python validate_cross_analysis.py analysis.json --schema-only
python validate_cross_analysis.py analysis.json --comprehensive

# Document evidence bundle validation
cd document-evidence-analyzer
python -c "from src.document_analyzer.validation import DocumentValidator; \
  validator = DocumentValidator(); \
  validator.validate_bundle('evidence/derived/sha256=<hash>/evidence_bundle.v1.json')"

# Image evidence validation
cd image-analysis
uv run python validate_schema.py evidence/derived/sha256=<hash>/analysis.v1.json

# Evidence storage validation (check all files in evidence directory)
find document-evidence-analyzer/evidence/derived -name "evidence_bundle.v1.json" | head -5
find image-analysis/evidence/derived -name "analysis.v1.json" | head -5
```

## Cross-Analysis Capabilities

### Entity Correlation
- **Multi-evidence entity tracking** with confidence scoring
- **Semantic analysis** of entity roles and relationships
- **Extraction method tracking** (NLP, OCR, AI, manual)
- **Correlation confidence** assessment

### Timeline Analysis
- **Chronological event extraction** from all evidence types
- **Pattern detection** and sequence analysis
- **Timeline gap identification** with significance assessment
- **Legal significance** scoring for temporal patterns

### Narrative Consistency
- **Contradiction detection** across evidence types
- **Supporting evidence** group identification
- **Narrative theme** extraction with keyword analysis
- **Overall coherence** scoring

### Risk Assessment
- **Multi-factor risk analysis** including:
  - Data integrity risks
  - Tampering indicators
  - Timeline gaps and inconsistencies
  - Legal exposure assessment
- **Mitigation recommendations**
- **Severity classification**

## Legal Compliance Features

### Chain of Custody
- **Complete audit trail** for cross-analysis processes
- **Actor identification** and action logging
- **Evidence tracking** throughout analysis
- **Timestamp verification**

### Data Integrity
- **SHA256 verification** at every reference point
- **Immutable evidence** bundle preservation
- **Cryptographic validation** of evidence integrity
- **Reproducible analysis** requirements

### Admissibility Standards
- **Federal Rules of Evidence** compliance
- **Forensic-grade validation** requirements
- **Professional analysis** documentation
- **Expert testimony** support documentation

## Future Development Roadmap

### Phase 1: Core Implementation (Complete)
- ✅ Cross-analysis schema design
- ✅ Validation infrastructure
- ✅ Type-safe models
- ✅ CI/CD integration

### Phase 2: Evidence Type Expansion
- 📋 Email evidence schema (`email.v1.json`)
- 📋 PDF document schema (`pdf.v1.json`)
- 📋 Audio evidence schema (`audio.v1.json`)
- 📋 Video evidence schema (`video.v1.json`)

### Phase 3: Advanced Analysis
- 📋 Communication network analysis
- 📋 Geospatial correlation
- 📋 Advanced temporal clustering
- 📋 Sentiment flow analysis

### Phase 4: Case-Level Aggregation
- 📋 Case analysis schema (`case-analysis.v1.json`)
- 📋 Multi-case correlation
- 📋 Precedent analysis
- 📋 Legal strategy recommendations

## Performance and Scalability

### Design Considerations
- **Streaming analysis** for large evidence sets
- **Incremental correlation** for growing cases
- **Parallel processing** capabilities
- **Memory-efficient** reference architecture

### Storage Optimization
- **Content-addressed storage** prevents duplication
- **Hard-link organization** by detected labels
- **SQLite catalog** for fast querying
- **Hierarchical organization** by case and evidence type

## Usage Integration

### Document Analyzer Integration
```python
from document_analyzer.evidence_manager import EvidenceManager
from models.cross_analysis_models import CrossAnalysisBundle

# Process documents and images together
manager = EvidenceManager()
analysis = manager.create_cross_analysis(case_id, evidence_list)
```

### Image Analysis Integration
```python
from image_analysis.models import EvidenceBundle
from models.cross_analysis_models import CrossAnalysisBundle

# Correlate image and document evidence
correlator = CrossEvidenceAnalyzer()
results = correlator.analyze(image_bundles, document_bundles)
```

## Current Working Implementation

### Real Implementation Example: CORRELATION_TEST Case

The Evidence Toolkit successfully processed and correlated evidence from multiple types:

**Evidence Processed:**
```
Document Evidence:
- File: test_document.txt
- SHA256: 692df64a02916d716ce4af13556e8de7a94259eb6a10f41d7c4f8537b47ae3e3
- Analysis: 52 words, key themes: safety, john, manager, january, workplace

Email Evidence:
- File: test_email2.eml
- SHA256: 7352e3cd3676e4e1fbdde65aaf11421291cd877eb02e331fdebd4451f03c3810
- Analysis: Email thread, 3 participants, professional communication
```

**Cross-Evidence Correlation Results:**
```json
{
  "entity_correlations": [
    {
      "entity_name": "John",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "confidence_average": 0.60,
      "evidence_pieces": ["692df64a", "7352e3cd"]
    },
    {
      "entity_name": "Sarah",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "confidence_average": 0.60,
      "evidence_pieces": ["692df64a", "7352e3cd"]
    }
  ]
}
```

**Timeline Reconstruction:**
```
2025-09-28 14:31:47 - Document created (test_document.txt)
2025-09-28 14:31:55 - Email created (test_email2.eml)
2025-09-28 14:32:43 - Document AI analysis completed
2025-09-28 14:32:58 - Email AI analysis completed
2025-09-28 14:59:23 - Cross-evidence correlation analysis performed
```

**Client Package Generated:**
- Executive summary with AI-powered legal significance assessment
- Individual evidence analysis files
- Cross-evidence correlation analysis
- Complete evidence catalog with forensic metadata
- Professional documentation and methodology

### Cross-Analysis Implementation Status

**Currently Working:**
- ✅ Entity correlation across document and email evidence
- ✅ Timeline reconstruction from evidence metadata
- ✅ Professional client package generation
- ✅ Content-addressed storage with SHA256 linking

**Using Custom Format:**
- Cross-evidence analysis outputs custom correlation format
- Integration with cross-analysis.v1.json schema is planned enhancement

This architecture provides a robust, extensible foundation for forensic evidence analysis while maintaining the highest standards of legal admissibility and data integrity.