# Core Models - Quick Reference

**Location**: `src/evidence_toolkit/core/models.py`
**All models are Pydantic v2** - Runtime validation, schema compliance, forensic integrity

---

## Import Cheat Sheet

```python
# Everything in one place!
from evidence_toolkit.core.models import (
    # Base Types
    EvidenceType, FileMetadata, ChainOfCustodyEvent,

    # AI Analysis (OpenAI Responses API)
    DocumentAnalysis, DocumentEntity,
    ImageAnalysisStructured,
    EmailThreadAnalysis, EmailParticipant, EscalationEvent,

    # Client Packages
    UnifiedAnalysis, DocumentAnalysisResult, ImageAnalysisResult,

    # Forensic Bundles
    EvidenceBundle, EvidenceCore, DocumentAnalysisRecord,

    # Cross-Evidence (NOW PYDANTIC!)
    CorrelationAnalysis, CorrelatedEntity, TimelineEvent,

    # v3.1 Legal Patterns
    LegalPatternAnalysis, Contradiction, CorroborationLink,

    # Case Summary
    CaseSummary, EvidenceSummary,

    # Operations
    IngestionResult, ExportResult, StorageStats, CaseInfo, CleanupResult
)
```

---

## Model Categories (8 Categories, 40+ Models)

| Category | Models | Purpose |
|----------|--------|---------|
| **Base Types** | EvidenceType, FileMetadata, ChainOfCustodyEvent | Core evidence infrastructure |
| **AI Analysis** | DocumentAnalysis, ImageAnalysisStructured, EmailThreadAnalysis | OpenAI structured outputs |
| **Client Packages** | UnifiedAnalysis, DocumentAnalysisResult, ImageAnalysisResult | Client deliverables |
| **Forensic Bundles** | EvidenceBundle, EvidenceCore, DocumentAnalysisRecord | Legal-grade storage |
| **Cross-Evidence** | CorrelationAnalysis, CorrelatedEntity, TimelineEvent | Multi-evidence correlation |
| **Legal Patterns** | LegalPatternAnalysis, Contradiction, CorroborationLink | AI pattern detection (**v3.1**) |
| **Case Summary** | CaseSummary, EvidenceSummary | Aggregated reporting (Pydantic in **v3.1**) |
| **Operations** | IngestionResult, ExportResult, StorageStats | Operation results |

---

## Common Workflows

### 1. Evidence Ingestion
```python
from evidence_toolkit.core.models import FileMetadata, IngestionResult, ChainOfCustodyEvent
from datetime import datetime

metadata = FileMetadata(
    filename="complaint.pdf",
    file_size=125000,
    mime_type="application/pdf",
    created_time="2024-03-15T10:30:00Z",
    modified_time="2024-03-15T10:30:00Z",
    extension=".pdf",
    sha256="abc123..." * 4  # 64 hex chars
)

result = IngestionResult(
    sha256=metadata.sha256,
    file_path="/cases/MY-CASE/complaint.pdf",
    evidence_type=EvidenceType.DOCUMENT,
    metadata=metadata,
    storage_path="/data/storage/raw/sha256=abc123.../original.pdf",
    success=True,
    message="Successfully ingested"
)
```

### 2. AI Document Analysis (with v3.1 enhancements)
```python
from evidence_toolkit.core.models import DocumentAnalysis, DocumentEntity

analysis = DocumentAnalysis(
    summary="Employee harassment complaint",
    entities=[
        DocumentEntity(
            name="Jane Doe",
            type="person",
            confidence=0.95,
            context="Complainant",
            relationship="filed complaint against manager",  # v3.1: Entity relationships
            quoted_text="I have been harassed"  # v3.1: Legally significant quotes
        ),
        DocumentEntity(
            name="March 5, 2024",
            type="date",
            confidence=0.92,
            context="Date of meeting mentioned in complaint",
            associated_event="HR meeting regarding harassment"  # v3.1: Event context
        )
    ],
    document_type="filing",
    sentiment="hostile",
    legal_significance="critical",
    risk_flags=["harassment", "retaliation_indicators"],
    confidence_overall=0.94
)
```

### 3. Email Thread Analysis (with v3.1 power dynamics)
```python
from evidence_toolkit.core.models import EmailThreadAnalysis, EmailParticipant, EscalationEvent

email_analysis = EmailThreadAnalysis(
    thread_summary="Complaint escalated with hostile response",
    participants=[
        EmailParticipant(
            email_address="employee@company.com",
            role="sender",
            authority_level="employee",
            confidence=0.95,
            message_count=3,  # v3.1: Message volume tracking
            deference_score=0.8,  # v3.1: Deferential communication style
            dominant_topics=[]  # v3.1: No topics controlled
        ),
        EmailParticipant(
            email_address="manager@company.com",
            role="recipient",
            authority_level="management",
            confidence=0.95,
            message_count=2,  # v3.1: Lower volume but dominant
            deference_score=0.15,  # v3.1: Highly dominant/controlling
            dominant_topics=["consequences", "performance review"]  # v3.1: Controlled topics
        )
    ],
    communication_pattern="escalating",
    sentiment_progression=[0.7, 0.5, 0.3],  # Deteriorating
    escalation_events=[
        EscalationEvent(
            email_position=1,
            escalation_type="tone_change",
            confidence=0.92,
            description="Tone shifted to hostile",
            context="I will not tolerate this"
        )
    ],
    legal_significance="critical",
    risk_flags=["threatening", "retaliation"],
    timeline_reconstruction=["2024-03-01: Complaint filed", ...],
    confidence_overall=0.91
)
```

### 4. Cross-Evidence Correlation (with v3.1 legal patterns)
```python
from evidence_toolkit.core.models import (
    CorrelationAnalysis, CorrelatedEntity, TimelineEvent,
    LegalPatternAnalysis, Contradiction, CorroborationLink
)

correlation = CorrelationAnalysis(
    case_id="CASE-2024-001",
    evidence_count=5,
    entity_correlations=[
        CorrelatedEntity(
            entity_name="Jane Doe",
            entity_type="person",
            occurrence_count=4,  # >= 2 required
            confidence_average=0.96,
            evidence_occurrences=[...]
        )
    ],
    timeline_events=[
        TimelineEvent(
            timestamp=datetime(2024, 3, 1, 10, 0),
            evidence_sha256="abc123...",
            evidence_type="document",
            event_type="incident",
            description="First harassment incident",
            confidence=0.92,
            ai_classification={"pattern": "harassment", "severity": 0.8}
        )
    ],
    analysis_timestamp=datetime.now(),
    temporal_sequences=[...],
    timeline_gaps=[...],
    legal_patterns=LegalPatternAnalysis(  # v3.1: NEW AI pattern detection
        contradictions=[
            Contradiction(
                statement_1="I never received the complaint",
                statement_1_source="sha256=abc123...",
                statement_2="I responded to the complaint on March 5th",
                statement_2_source="sha256=def456...",
                contradiction_type="factual",
                severity=0.92,
                explanation="Manager contradicts himself about receiving complaint"
            )
        ],
        corroboration=[
            CorroborationLink(
                claim="Harassment incident occurred on March 1st",
                supporting_evidence=["sha256=abc...", "sha256=def...", "sha256=ghi..."],
                corroboration_strength="strong",
                explanation="Three independent sources confirm date"
            )
        ],
        evidence_gaps=["Missing March 3rd meeting evidence", "No HR complaint receipt"],
        pattern_summary="Strong retaliation pattern with contradictory statements",
        confidence=0.89
    )
)
```

### 5. Client Package
```python
from evidence_toolkit.core.models import UnifiedAnalysis, DocumentAnalysisResult

unified = UnifiedAnalysis(
    evidence_type=EvidenceType.DOCUMENT,
    analysis_timestamp=datetime.now(),
    file_metadata=metadata,
    case_ids=["CASE-2024-001"],  # Multi-case support (v3.0)
    document_analysis=DocumentAnalysisResult(
        total_words=500,
        unique_words=250,
        word_frequency={"harassment": 15},
        top_words=[("harassment", 15)],
        openai_model="gpt-4o-2024-08-06",
        ai_summary="Complaint...",
        entities=[...],
        legal_significance="critical",
        risk_flags=["harassment"],
        analysis_confidence=0.94
    ),
    chain_of_custody=[...],
    labels=["harassment", "critical"]
)

# Serialize
with open("analysis.v1.json", "w") as f:
    f.write(unified.model_dump_json(indent=2))
```

---

## Evidence Types (Enum)

```python
class EvidenceType(str, Enum):
    DOCUMENT = "document"  # → DocumentAnalyzer
    IMAGE = "image"        # → ImageAnalyzer (Vision)
    EMAIL = "email"        # → EmailAnalyzer
    PDF = "pdf"            # → DocumentAnalyzer
    AUDIO = "audio"        # (Planned)
    VIDEO = "video"        # (Planned)
    OTHER = "other"        # (Manual review)
```

---

## Risk Flags Reference

### Document Risk Flags
```python
risk_flags: List[Literal[
    "threatening",              # Threatening language
    "deadline",                 # Time-sensitive deadline
    "pii",                      # Personal Identifiable Information
    "confidential",             # Confidentiality markings
    "time_sensitive",           # Urgent action required
    "retaliation_indicators",   # Potential retaliation
    "harassment",               # Harassment indicators
    "discrimination"            # Discrimination indicators
]]
```

### Email Risk Flags
```python
risk_flags: List[Literal[
    "threatening",              # Threatening language
    "harassment",               # Harassment indicators
    "discrimination",           # Discrimination indicators
    "retaliation",              # Retaliation pattern
    "deadline",                 # Time-sensitive deadline
    "pii",                      # Personal information
    "confidential",             # Confidential content
    "hostile_takeover",         # Hostile communication takeover
    "policy_violation"          # Policy violation detected
]]
```

### Image Risk Flags
```python
risk_flags: List[Literal[
    "low_quality",              # Poor image quality
    "tampering_suspected",      # Digital manipulation signs
    "metadata_missing",         # EXIF data stripped
    "unclear_content"           # Ambiguous content
]]
```

---

## Validation Constraints

| Constraint | Field Examples | Rule |
|------------|---------------|------|
| **SHA256** | `sha256`, `evidence_sha256` | `pattern=r"^[a-f0-9]{64}$"` (64 hex chars) |
| **Confidence** | `confidence`, `confidence_overall` | `ge=0.0, le=1.0` (0.0-1.0 inclusive) |
| **Occurrence Count** | `occurrence_count` | `ge=2` (correlations require 2+) |
| **File Size** | `file_size`, `bytes` | `ge=1` (at least 1 byte) |
| **Temperature** | `temperature` | `le=0.0` (≤0 for deterministic) |
| **Literal Types** | `document_type`, `sentiment` | Fixed enum values |

---

## Forensic Compliance

All models with timestamps/floats use consistent encoding:

```python
class Config:
    json_encoders = {
        datetime: lambda dt: dt.isoformat(),  # ISO 8601
        float: lambda v: round(v, 4)          # 4-decimal precision
    }
```

**Benefits**:
- ISO 8601 timestamps for legal admissibility
- Consistent 4-decimal floating-point precision
- Reproducible serialization

---

## Version Evolution

### v3.1 Layer 1 (2025-10-05) - AI-Powered Enhancements

**New Models**:
- `LegalPatternAnalysis` - Cross-evidence contradiction/corroboration detection
- `Contradiction` - Conflicting statements across evidence
- `CorroborationLink` - Evidence supporting same claims

**Enhanced Models**:
- **DocumentEntity**: Added `relationship`, `quoted_text`, `associated_event` for legal context
- **EmailParticipant**: Added `message_count`, `deference_score`, `dominant_topics` for power dynamics
- **CorrelationAnalysis**: Added `legal_patterns` field for AI pattern analysis
- **EvidenceSummary**: Converted from @dataclass to Pydantic BaseModel
- **CaseSummary**: Converted from @dataclass to Pydantic BaseModel

**Key Benefits**:
- **Relationship tracking**: Understand entity connections across evidence
- **Power dynamics**: Analyze communication patterns and control
- **Pattern detection**: AI identifies contradictions and corroboration automatically
- **Full Pydantic**: Complete validation consistency across all models

### v3.0 vs v2.0 Changes

| Aspect | v2.0 | v3.0 |
|--------|------|------|
| **Files** | 5+ separate files | 1 unified file |
| **Validation** | Mixed Pydantic/dataclass | ALL Pydantic |
| **CorrelationAnalysis** | @dataclass | Pydantic BaseModel |
| **Case Support** | Single case (`case_id`) | Multi-case (`case_ids`) |
| **Imports** | `from models.cross_analysis_models import ...` | `from evidence_toolkit.core.models import ...` |

---

## Common Validation Errors

```python
from pydantic import ValidationError

# SHA256 must be 64 hex characters (lowercase)
sha256 = "ABC123..."  # ❌ Wrong: uppercase, too short
sha256 = "abc123..." * 4  # ✅ Correct: 64 lowercase hex chars

# Confidence must be 0.0-1.0
confidence = 1.5  # ❌ Wrong: > 1.0
confidence = 0.95  # ✅ Correct: 0.0-1.0

# Occurrence count must be >= 2 for correlations
occurrence_count = 1  # ❌ Wrong: < 2
occurrence_count = 3  # ✅ Correct: >= 2

# Debug validation errors
try:
    model = DocumentAnalysis(**data)
except ValidationError as e:
    print(e.json(indent=2))  # Pretty-print errors
```

---

## Storage Paths

| Model | Storage Path |
|-------|-------------|
| `UnifiedAnalysis` | `data/storage/derived/sha256=<hash>/analysis.v1.json` |
| `EvidenceBundle` | `data/storage/derived/sha256=<hash>/evidence_bundle.v1.json` |
| `FileMetadata` | `data/storage/derived/sha256=<hash>/metadata.json` |
| `CorrelationAnalysis` | `data/storage/cases/<case-id>/cross_analysis.json` |
| `CaseSummary` | `data/packages/<case-id>/case_summary.json` |

---

## OpenAI Integration Pattern

```python
from openai import OpenAI
from evidence_toolkit.core.models import DocumentAnalysis

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": document_text}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "document_analysis",
            "schema": DocumentAnalysis.model_json_schema(),  # Auto-generate schema
            "strict": True  # Enforce schema compliance
        }
    }
)

# Validate response
analysis = DocumentAnalysis.model_validate_json(
    completion.choices[0].message.content
)
```

---

## Serialization Shortcuts

```python
# To JSON string
json_str = model.model_dump_json(indent=2)

# To dict
data = model.model_dump()

# From JSON string
model = DocumentAnalysis.model_validate_json(json_str)

# From dict
model = DocumentAnalysis.model_validate(data)

# Get schema (for OpenAI)
schema = DocumentAnalysis.model_json_schema()
```

---

## Related Documentation

- **Full API Docs**: `/home/bch/dev/00_RELEASE/evidence-toolkit/docs/api/models.md`
- **Architecture**: `/home/bch/dev/00_RELEASE/evidence-toolkit/V3_ARCHITECTURE.md`
- **Project Guide**: `/home/bch/dev/00_RELEASE/evidence-toolkit/CLAUDE.md`
- **Getting Started**: `/home/bch/dev/00_RELEASE/evidence-toolkit/README.md`

---

**Quick reference for Evidence Toolkit v3.0 Core Models - All Pydantic, Single Source of Truth**
