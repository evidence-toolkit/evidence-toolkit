# Documentation: Core Models Module

## Overview

The `evidence_toolkit.core.models` module is the **single source of truth** for all Pydantic data models in Evidence Toolkit v3.0. This consolidated module eliminates the complexity of hunting across multiple files by providing every model needed for forensic evidence management, AI-powered analysis, cross-evidence correlation, and legal-grade evidence packaging in one place.

This module represents a major architectural improvement over v2.0, where models were scattered across 5+ different files and used an inconsistent mix of Pydantic models and dataclasses. In v3.0, **everything is Pydantic**, ensuring runtime validation, schema compliance, and forensic integrity throughout the evidence processing pipeline.

## Purpose & Scope

### What This Module Does
- **Defines ALL data structures** used throughout Evidence Toolkit
- **Enforces runtime validation** via Pydantic v2 for forensic compliance
- **Provides deterministic schema** for OpenAI Responses API integration
- **Maintains chain of custody** tracking structures
- **Supports multi-modal evidence** (documents, emails, images, audio, video)
- **Enables cross-evidence correlation** with validated models
- **Ensures legal-grade integrity** through strict field constraints

### What This Module Is NOT Responsible For
- **Storage operations** - handled by `evidence_toolkit.core.storage`
- **AI analysis logic** - handled by `evidence_toolkit.analyzers.*`
- **Data persistence** - models are pure data structures
- **Business logic** - models only validate structure, not implement behavior

## Model Categories

The module organizes 40+ models into 8 logical categories:

1. **Base Types & Enums** - Evidence types, file metadata, chain of custody
2. **AI Analysis Models** - OpenAI Responses API structured outputs
3. **Unified Analysis** - Multi-modal evidence containers for client packages
4. **Forensic Bundles** - Legal-grade evidence packages with full audit trails
5. **Cross-Evidence Analysis** - Correlation and timeline reconstruction (NOW PYDANTIC!)
6. **Legal Pattern Analysis** - AI-powered contradiction/corroboration detection (v3.1)
7. **Case Summary & Reporting** - Aggregated case views
8. **Operation Results** - Ingestion, export, and storage management outcomes

---

## Architecture

### Module Structure
```
src/evidence_toolkit/
├── core/
│   ├── models.py           # ← THIS MODULE (ALL models)
│   ├── storage.py          # Uses models for storage operations
│   └── utils.py            # Helper functions
├── analyzers/
│   ├── document.py         # Returns DocumentAnalysis
│   ├── email.py            # Returns EmailThreadAnalysis
│   ├── image.py            # Returns ImageAnalysisStructured
│   └── correlation.py      # Returns CorrelationAnalysis
└── pipeline/
    ├── analyze.py          # Orchestrates analysis, uses UnifiedAnalysis
    └── package.py          # Generates client packages
```

### Schema Versions
```python
SCHEMA_VERSION = "1.0.0"                    # Main evidence bundle schema
CROSS_ANALYSIS_SCHEMA_VERSION = "1.0.0"    # Cross-evidence schema
```

---

## Category 1: Base Types & Enums

### EvidenceType (Enum)
**Purpose**: Classify evidence by type for routing to appropriate analyzers

**Values**:
| Value | Description | Analyzer |
|-------|-------------|----------|
| `DOCUMENT` | Text documents, PDFs (non-email) | DocumentAnalyzer |
| `IMAGE` | Photos, screenshots, diagrams | ImageAnalyzer (Vision) |
| `EMAIL` | Email files (.eml, .msg) | EmailAnalyzer |
| `PDF` | PDF documents | DocumentAnalyzer |
| `AUDIO` | Audio recordings | (Planned) |
| `VIDEO` | Video files | (Planned) |
| `OTHER` | Unclassified evidence | (Manual review) |

**Usage**:
```python
from evidence_toolkit.core.models import EvidenceType

evidence_type = EvidenceType.EMAIL
# Automatically routes to EmailAnalyzer
```

### FileMetadata
**Purpose**: Basic file metadata for any evidence type, extracted during ingestion

**Key Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `filename` | str | Yes | Original filename |
| `file_size` | int | Yes | Size in bytes |
| `mime_type` | Optional[str] | No | MIME type (e.g., "application/pdf") |
| `created_time` | str | Yes | File creation timestamp (ISO 8601) |
| `modified_time` | str | Yes | Last modification timestamp (ISO 8601) |
| `extension` | str | Yes | File extension (e.g., ".pdf") |
| `sha256` | str | Yes | SHA256 hash identifier |

**Validation**:
- SHA256 must be 64 hexadecimal characters (enforced in related models)
- Timestamps must be parseable date strings

**Usage**:
```python
metadata = FileMetadata(
    filename="complaint.pdf",
    file_size=245678,
    mime_type="application/pdf",
    created_time="2024-03-15T10:30:00Z",
    modified_time="2024-03-15T10:30:00Z",
    extension=".pdf",
    sha256="abc123..."
)
```

### ChainOfCustodyEvent
**Purpose**: Track evidence handling for legal admissibility

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | When the event occurred |
| `event_type` | str | Type: "ingest", "analyze", "export", "case_association" |
| `actor` | str | Who performed the action (user, system) |
| `description` | str | Human-readable description |
| `metadata` | Optional[Dict[str, Any]] | Additional context |

**Forensic Compliance**:
- Every evidence touch is logged
- Immutable once written (append-only)
- Used in legal discovery

**Usage**:
```python
event = ChainOfCustodyEvent(
    timestamp=datetime.now(),
    event_type="analyze",
    actor="evidence-toolkit-v3.0",
    description="AI analysis completed with gpt-4o-2024-08-06",
    metadata={"model": "gpt-4o-2024-08-06", "confidence": 0.95}
)
```

---

## Category 2: AI Analysis Models (OpenAI Responses API)

These models define the **exact structured response format** for OpenAI's Responses API, ensuring deterministic, reproducible, forensic-grade analysis.

### DocumentEntity
**Purpose**: Extract legally significant entities from documents with relationships and context

**Key Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | The extracted entity text |
| `type` | Literal | Yes | "person", "organization", "date", "legal_term" |
| `confidence` | float | Yes | 0.0-1.0 confidence score |
| `context` | str | Yes | Surrounding text where found |
| `relationship` | Optional[str] | No | v3.1: Relationship to other entities |
| `quoted_text` | Optional[str] | No | v3.1: Exact quote if legally significant |
| `associated_event` | Optional[str] | No | v3.1: Event for date entities |

**v3.1 Layer 1 Enhancements**:
- **Relationship tracking**: Captures entity relationships (e.g., "sent email to Rachel Hemmings", "mentioned by Paul Boucherat", "copied on email to HR")
- **Quoted statements**: Extracts verbatim quotes for legally significant statements including admissions, threats, policy violations, and obligations
- **Event association**: Links date entities to specific events (e.g., "meeting with HR", "deadline for response", "complaint filed")

**OpenAI Best Practice**:
```python
# ✅ Correct: Optional[str] = None (not str = "")
# This follows OpenAI's recommended pattern for optional structured fields
relationship: Optional[str] = Field(default=None, ...)
quoted_text: Optional[str] = Field(default=None, ...)
associated_event: Optional[str] = Field(default=None, ...)
```

**Usage Example**:
```python
entity = DocumentEntity(
    name="Paul Boucherat",
    type="person",
    confidence=0.96,
    context="Email from Paul Boucherat to Rachel Hemmings regarding workplace complaint",
    relationship="sent email to Rachel Hemmings",
    quoted_text="This behavior will not be tolerated and will have consequences",
    associated_event=None  # Only populated for date entities
)
```


### DocumentAnalysis
**Purpose**: Complete structured analysis of document content for legal evidence processing

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `summary` | str | Executive summary of document content |
| `entities` | List[DocumentEntity] | Extracted entities with confidence scores |
| `document_type` | Literal | "email", "letter", "contract", "filing" |
| `sentiment` | Literal | "hostile", "neutral", "professional" |
| `legal_significance` | Literal | "critical", "high", "medium", "low" |
| `risk_flags` | List[Literal] | Risk factors (see below) |
| `confidence_overall` | float | 0.0-1.0 overall confidence |

**Risk Flags**:
- `threatening` - Threatening language detected
- `deadline` - Time-sensitive deadline present
- `pii` - Personal Identifiable Information
- `confidential` - Confidentiality markings/content
- `time_sensitive` - Urgent action required
- `retaliation_indicators` - Potential retaliation pattern
- `harassment` - Harassment indicators
- `discrimination` - Discrimination indicators

**Forensic Configuration**:
```python
class Config:
    json_encoders = {
        float: lambda v: round(v, 4)  # Consistent 4-decimal precision
    }
```

**Usage** (OpenAI Responses API):
```python
from openai import OpenAI
from evidence_toolkit.core.models import DocumentAnalysis

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{"role": "user", "content": document_text}],
    response_format={"type": "json_schema", "json_schema": {
        "name": "document_analysis",
        "schema": DocumentAnalysis.model_json_schema(),
        "strict": True
    }}
)

analysis = DocumentAnalysis.model_validate_json(completion.choices[0].message.content)
```

### ImageAnalysisStructured
**Purpose**: Forensic-grade image analysis using OpenAI Vision API

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `scene_description` | str | Detailed visual scene description |
| `detected_text` | Optional[str] | OCR text extraction |
| `detected_objects` | List[str] | Visible objects, people, items |
| `people_present` | bool | Whether people are visible |
| `timestamps_visible` | bool | Whether timestamps/dates visible |
| `potential_evidence_value` | Literal | "low", "medium", "high" |
| `analysis_notes` | str | Additional forensic observations |
| `confidence_overall` | float | 0.0-1.0 overall confidence |
| `risk_flags` | List[Literal] | Quality/tampering flags |

**Risk Flags**:
- `low_quality` - Image quality too poor for reliable analysis
- `tampering_suspected` - Signs of digital manipulation
- `metadata_missing` - EXIF metadata stripped/missing
- `unclear_content` - Content ambiguous or unclear

**Usage**:
```python
from openai import OpenAI
from evidence_toolkit.core.models import ImageAnalysisStructured

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o-2024-08-06",
    messages=[{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    }],
    response_format={"type": "json_schema", "json_schema": {
        "name": "image_analysis",
        "schema": ImageAnalysisStructured.model_json_schema(),
        "strict": True
    }}
)

analysis = ImageAnalysisStructured.model_validate_json(completion.choices[0].message.content)
```

### EmailThreadAnalysis
**Purpose**: Complete forensic analysis of email threads with power dynamics and escalation tracking

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `thread_summary` | str | Executive summary focusing on legal significance |
| `participants` | List[EmailParticipant] | All participants with authority analysis |
| `communication_pattern` | Literal | "professional", "escalating", "hostile", "retaliatory" |
| `sentiment_progression` | List[float] | Per-email sentiment (0.0=hostile, 1.0=professional) |
| `escalation_events` | List[EscalationEvent] | Detected escalation points |
| `legal_significance` | Literal | "critical", "high", "medium", "low" |
| `risk_flags` | List[Literal] | Legal risk indicators |
| `timeline_reconstruction` | List[str] | Chronological event summary |
| `confidence_overall` | float | 0.0-1.0 overall confidence |

**Sub-Models**:

#### EmailParticipant
| Field | Type | Description |
|-------|------|-------------|
| `email_address` | str | Email address |
| `display_name` | Optional[str] | Display name if available |
| `role` | Literal | "sender", "recipient", "cc", "bcc" |
| `authority_level` | Literal | "executive", "management", "employee", "external" |
| `confidence` | float | Authority level assessment confidence |
| `message_count` | int | v3.1: Number of messages sent by this participant in the thread |
| `deference_score` | float | v3.1: Communication deference (0.0=highly dominant/controlling, 0.5=neutral, 1.0=highly deferential) |
| `dominant_topics` | List[str] | v3.1: Topics this participant drove or controlled in the conversation |

#### EscalationEvent
| Field | Type | Description |
|-------|------|-------------|
| `email_position` | int | Position in thread (0-based index) |
| `escalation_type` | Literal | "tone_change", "new_recipient", "authority_escalation", "threat", "deadline" |
| `confidence` | float | Detection confidence |
| `description` | str | Detailed escalation description |
| `context` | str | Supporting text |

**v3.1 Layer 1 Power Dynamics Analysis**:
- **Message volume tracking**: Counts messages sent by each participant to identify communication patterns
- **Deference pattern analysis**: Scores communication style from dominant (0.0) to deferential (1.0) based on language, tone, and response patterns
- **Topic control identification**: Detects which participants drive or control specific conversation topics, useful for identifying power dynamics in workplace disputes

**Usage**:
```python
analysis = EmailThreadAnalysis(
    thread_summary="HR complaint escalated from employee to management with hostile response",
    participants=[
        EmailParticipant(
            email_address="employee@company.com",
            display_name="Jane Doe",
            role="sender",
            authority_level="employee",
            confidence=0.95,
            message_count=3,
            deference_score=0.8,  # Highly deferential
            dominant_topics=[]
        ),
        EmailParticipant(
            email_address="manager@company.com",
            display_name="John Smith",
            role="recipient",
            authority_level="management",
            confidence=0.95,
            message_count=2,
            deference_score=0.2,  # Highly dominant
            dominant_topics=["deadline", "consequences"]
        )
    ],
    communication_pattern="escalating",
    sentiment_progression=[0.7, 0.5, 0.3],  # Deteriorating
    escalation_events=[
        EscalationEvent(
            email_position=1,
            escalation_type="tone_change",
            confidence=0.9,
            description="Tone shifted from professional to hostile",
            context="I will not tolerate this behavior"
        )
    ],
    legal_significance="high",
    risk_flags=["threatening", "retaliation"],
    timeline_reconstruction=[
        "2024-03-01: Initial complaint filed",
        "2024-03-05: Manager responds with threats",
        "2024-03-10: Employee escalates to HR"
    ],
    confidence_overall=0.92
)
```

---

## Category 3: Unified Analysis (Client Package Format)

### UnifiedAnalysis
**Purpose**: Unified container for any evidence type, used in client deliverable packages

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `evidence_type` | EvidenceType | Type of evidence |
| `analysis_timestamp` | datetime | When analysis was performed |
| `file_metadata` | FileMetadata | File information |
| `case_ids` | List[str] | Cases this evidence belongs to (v3.0+) |
| `case_id` | Optional[str] | Deprecated: Use case_ids instead |
| `document_analysis` | Optional[DocumentAnalysisResult] | For documents |
| `image_analysis` | Optional[ImageAnalysisResult] | For images |
| `email_analysis` | Optional[EmailThreadAnalysis] | For emails (v3.1+) |
| `chain_of_custody` | List[ChainOfCustodyEvent] | Audit trail |
| `exif_data` | Optional[Dict[str, Any]] | For images |
| `email_metadata` | Optional[Dict[str, Any]] | For emails (headers) |
| `labels` | List[str] | Categories/tags |
| `notes` | Optional[str] | Additional notes |

**Multi-Case Support**:
```python
@model_validator(mode='after')
def sync_case_fields(self):
    """Auto-sync case_id and case_ids for backward compatibility."""
    if self.case_id and not self.case_ids:
        self.case_ids = [self.case_id]
    elif self.case_ids and not self.case_id:
        self.case_id = self.case_ids[0] if self.case_ids else None
    return self
```

**Sub-Models**:

#### DocumentAnalysisResult
Legacy word frequency + AI analysis:
| Field | Type | Description |
|-------|------|-------------|
| `total_words` | int | Total word count |
| `unique_words` | int | Unique word count |
| `word_frequency` | Dict[str, int] | Word frequency map |
| `top_words` | List[tuple] | Top 20 most frequent |
| `wordcloud_file` | Optional[str] | Path to word cloud image |
| `frequency_chart_file` | Optional[str] | Path to frequency chart |
| `openai_model` | Optional[str] | AI model used |
| `ai_summary` | Optional[str] | AI-generated summary |
| `entities` | Optional[List[Dict]] | Extracted entities |
| `document_type` | Optional[str] | Document classification |
| `sentiment` | Optional[str] | Sentiment analysis |
| `legal_significance` | Optional[str] | Legal importance |
| `risk_flags` | Optional[List[str]] | Risk indicators |
| `analysis_confidence` | Optional[float] | Overall confidence |

#### ImageAnalysisResult
| Field | Type | Description |
|-------|------|-------------|
| `openai_model` | str | AI model used |
| `openai_response` | Dict[str, Any] | Raw OpenAI response |
| `detected_objects` | Optional[List[str]] | Objects found |
| `detected_text` | Optional[str] | OCR text |
| `scene_description` | Optional[str] | Scene description |
| `analysis_confidence` | Optional[float] | Overall confidence |

**Usage**:
```python
unified = UnifiedAnalysis(
    evidence_type=EvidenceType.EMAIL,
    analysis_timestamp=datetime.now(),
    file_metadata=metadata,
    case_ids=["CASE-2024-001", "CASE-2024-002"],  # Multi-case support
    email_analysis=EmailThreadAnalysis(...),
    email_metadata={"Subject": "Re: Complaint", "From": "..."},
    chain_of_custody=[event1, event2],
    labels=["retaliation", "HR"]
)
```

---

## Category 4: Forensic Bundles (Legal-Grade Evidence Packages)

These models follow the **document.v1.json schema** for forensic evidence storage.

### EvidenceBundle
**Purpose**: Complete evidence bundle for forensic storage with full audit trail

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | Literal["1.0.0"] | Fixed schema version |
| `case_id` | Optional[str] | Case identifier |
| `evidence` | EvidenceCore | Core evidence metadata |
| `chain_of_custody` | List[ChainOfCustodyEntry] | Complete audit trail |
| `analyses` | List[DocumentAnalysisRecord] | Analysis records |

**Forensic Compliance**:
```python
class Config:
    json_encoders = {
        datetime: lambda dt: dt.isoformat(),  # ISO 8601 timestamps
        float: lambda v: round(v, 4)          # Consistent precision
    }
```

**Sub-Models**:

#### EvidenceCore
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `evidence_id` | str | - | Unique identifier (typically SHA256) |
| `sha256` | str | Pattern: ^[a-f0-9]{64}$ | SHA256 hash |
| `mime_type` | str | - | MIME type |
| `bytes` | int | >= 1 | File size |
| `ingested_at` | datetime | - | Ingestion timestamp |
| `source_path` | str | - | Original file path |

#### ChainOfCustodyEntry
| Field | Type | Description |
|-------|------|-------------|
| `ts` | datetime | Event timestamp |
| `actor` | str | Who performed action |
| `action` | str | Action: "ingest", "analyze", "export" |
| `note` | Optional[str] | Additional notes |

#### DocumentAnalysisRecord
| Field | Type | Description |
|-------|------|-------------|
| `analysis_id` | str | Unique analysis identifier |
| `created_at` | datetime | When analysis was performed |
| `model` | AnalysisModelInfo | AI model information |
| `parameters` | AnalysisParameters | Analysis parameters |
| `outputs` | DocumentAnalysis | Structured results |
| `confidence_overall` | float | Overall confidence |

#### AnalysisModelInfo
| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Model name (e.g., "gpt-4o-2024-08-06") |
| `revision` | str | Model revision/version |

#### AnalysisParameters
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `temperature` | Optional[float] | <= 0.0 | Temperature (≤0 for deterministic) |
| `prompt_hash` | Optional[str] | - | SHA256 hash of prompt |
| `token_usage_in` | Optional[int] | - | Input tokens |
| `token_usage_out` | Optional[int] | - | Output tokens |

**Storage Location**:
```
data/storage/derived/sha256=<hash>/evidence_bundle.v1.json
```

**Usage**:
```python
bundle = EvidenceBundle(
    schema_version="1.0.0",
    case_id="CASE-2024-001",
    evidence=EvidenceCore(
        evidence_id="abc123...",
        sha256="abc123...",
        mime_type="application/pdf",
        bytes=245678,
        ingested_at=datetime.now(),
        source_path="/original/path/complaint.pdf"
    ),
    chain_of_custody=[
        ChainOfCustodyEntry(
            ts=datetime.now(),
            actor="evidence-toolkit-v3.0",
            action="ingest",
            note="Initial ingestion from case directory"
        )
    ],
    analyses=[
        DocumentAnalysisRecord(
            analysis_id="analysis-001",
            created_at=datetime.now(),
            model=AnalysisModelInfo(name="gpt-4o-2024-08-06", revision="2024-08-06"),
            parameters=AnalysisParameters(temperature=0.0, prompt_hash="def456..."),
            outputs=DocumentAnalysis(...),
            confidence_overall=0.95
        )
    ]
)
```

---

## Category 5: Cross-Evidence Analysis (NOW PYDANTIC! - v3.0 Fix)

**Major v3.0 Improvement**: Correlation models converted from dataclasses to Pydantic for consistency and validation.

### CorrelationAnalysis
**Purpose**: Results of cross-evidence correlation analysis across multiple evidence pieces

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `case_id` | str | Case identifier |
| `evidence_count` | int | Number of evidence pieces analyzed |
| `entity_correlations` | List[CorrelatedEntity] | Entities found in 2+ pieces |
| `timeline_events` | List[TimelineEvent] | Chronological events |
| `analysis_timestamp` | datetime | When analysis was performed |
| `temporal_sequences` | List[Dict[str, Any]] | AI-classified event patterns (e.g., retaliation sequences) |
| `timeline_gaps` | List[Dict[str, Any]] | Suspicious gaps in evidence timeline |
| `legal_patterns` | Optional[LegalPatternAnalysis] | **v3.1**: AI-detected contradictions, corroboration, and evidence gaps |

**v3.0 → v3.1 Evolution**:
- **v3.0**: Converted from dataclass to Pydantic for validation consistency
- **v3.1**: Added `legal_patterns` field for AI-powered contradiction and corroboration detection

**v3.0 Validation**:
```python
class Config:
    json_encoders = {
        datetime: lambda dt: dt.isoformat(),
        float: lambda v: round(v, 4)
    }
```

**Sub-Models**:

#### CorrelatedEntity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `entity_name` | str | - | Canonical entity name |
| `entity_type` | str | - | Entity type (person, org, etc.) |
| `occurrence_count` | int | >= 2 | Number of evidence pieces |
| `confidence_average` | float | 0.0-1.0 | Average confidence |
| `evidence_occurrences` | List[Dict] | - | Details of each occurrence |

#### TimelineEvent
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `timestamp` | datetime | - | Event timestamp |
| `evidence_sha256` | str | Pattern: ^[a-f0-9]{64}$ | Source evidence |
| `evidence_type` | str | - | Evidence type |
| `event_type` | str | - | Temporal event type |
| `description` | str | - | Event description |
| `confidence` | float | 0.0-1.0 | Extraction confidence |
| `ai_classification` | Optional[Dict] | - | AI pattern classification |

#### EvidenceOccurrence
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `evidence_sha256` | str | Pattern: ^[a-f0-9]{64}$ | Evidence containing entity |
| `context` | str | - | Context where entity appears |
| `confidence` | float | 0.0-1.0 | Entity match confidence |

**Usage**:
```python
correlation = CorrelationAnalysis(
    case_id="CASE-2024-001",
    evidence_count=5,
    entity_correlations=[
        CorrelatedEntity(
            entity_name="Rachel Hemmings",
            entity_type="person",
            occurrence_count=3,
            confidence_average=0.95,
            evidence_occurrences=[
                {"evidence_sha256": "abc123...", "context": "Email sender"},
                {"evidence_sha256": "def456...", "context": "Mentioned in complaint"}
            ]
        )
    ],
    timeline_events=[
        TimelineEvent(
            timestamp=datetime(2024, 3, 1, 10, 0),
            evidence_sha256="abc123...",
            evidence_type="email",
            event_type="communication",
            description="Initial complaint sent",
            confidence=0.95,
            ai_classification={"pattern": "retaliation_sequence", "severity": 0.8}
        )
    ],
    analysis_timestamp=datetime.now(),
    temporal_sequences=[],
    timeline_gaps=[]
)
```

---

## Category 6: Legal Pattern Analysis (v3.1 Layer 1 - AI-Powered Cross-Evidence Insights)

**New in v3.1**: AI-powered pattern detection for identifying contradictions, corroboration, and evidence gaps across multiple pieces of evidence.

### LegalPatternAnalysis
**Purpose**: AI-powered detection of contradictions, corroboration, and evidence gaps across evidence pieces

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `contradictions` | List[Contradiction] | Conflicting statements detected across evidence |
| `corroboration` | List[CorroborationLink] | Evidence supporting the same claims |
| `evidence_gaps` | List[str] | Identified gaps or missing evidence |
| `pattern_summary` | str | Overall summary of detected legal patterns |
| `confidence` | float | Overall confidence in pattern detection (0.0-1.0) |

**Forensic Value**:
- **Contradiction detection**: Identifies conflicting statements that may indicate dishonesty or memory issues
- **Corroboration analysis**: Finds multiple pieces of evidence supporting the same facts, strengthening case
- **Gap identification**: Highlights missing evidence or timeline gaps that need investigation

**Sub-Models**:

#### Contradiction
| Field | Type | Description |
|-------|------|-------------|
| `statement_1` | str | First statement |
| `statement_1_source` | str | SHA256 of source |
| `statement_2` | str | Conflicting statement |
| `statement_2_source` | str | SHA256 of source |
| `contradiction_type` | Literal | "factual", "temporal", "attribution" |
| `severity` | float | 0.0-1.0 severity score |
| `explanation` | str | Why these conflict |

**Example**:
```python
contradiction = Contradiction(
    statement_1="I never received the complaint",
    statement_1_source="abc123...",
    statement_2="I responded to the complaint on March 5th",
    statement_2_source="def456...",
    contradiction_type="factual",
    severity=0.9,
    explanation="Manager claims both receiving and not receiving the complaint"
)
```

#### CorroborationLink
| Field | Type | Description |
|-------|------|-------------|
| `claim` | str | Claim being corroborated |
| `supporting_evidence` | List[str] | SHA256s of supporting evidence |
| `corroboration_strength` | Literal | "weak", "moderate", "strong" |
| `explanation` | str | How evidence corroborates |

**Example**:
```python
corroboration = CorroborationLink(
    claim="Meeting occurred on March 1st, 2024",
    supporting_evidence=["abc123...", "def456...", "ghi789..."],
    corroboration_strength="strong",
    explanation="Email, calendar invite, and meeting notes all confirm March 1st date"
)
```

**Complete Usage Example**:
```python
# Create legal pattern analysis from cross-evidence correlation
patterns = LegalPatternAnalysis(
    contradictions=[
        Contradiction(
            statement_1="I never received the harassment complaint",
            statement_1_source="sha256=abc123...",  # Manager's denial statement
            statement_2="I addressed the complaint on March 5th in our meeting",
            statement_2_source="sha256=def456...",  # Manager's email response
            contradiction_type="factual",
            severity=0.95,
            explanation="Manager contradicts himself by claiming both not receiving and addressing the complaint"
        ),
        Contradiction(
            statement_1="The incident occurred on March 10th",
            statement_1_source="sha256=ghi789...",  # Witness statement
            statement_2="The incident occurred on March 8th",
            statement_2_source="sha256=jkl012...",  # Complainant statement
            contradiction_type="temporal",
            severity=0.7,
            explanation="Two-day discrepancy in incident date between witness and complainant"
        )
    ],
    corroboration=[
        CorroborationLink(
            claim="Manager used threatening language during March 5th meeting",
            supporting_evidence=[
                "sha256=abc123...",  # Meeting notes
                "sha256=def456...",  # Email follow-up referencing threats
                "sha256=ghi789..."   # Witness statement
            ],
            corroboration_strength="strong",
            explanation="Three independent sources confirm threatening language: meeting notes, email reference, and witness testimony"
        )
    ],
    evidence_gaps=[
        "No direct evidence of alleged March 3rd follow-up meeting",
        "Missing email thread referenced in complaint dated March 2nd",
        "No HR documentation of initial complaint receipt"
    ],
    pattern_summary="Strong retaliation pattern with contradictory manager statements and well-corroborated threatening behavior. Timeline gaps suggest missing evidence.",
    confidence=0.88
)

# Integrate with CorrelationAnalysis
correlation = CorrelationAnalysis(
    case_id="CASE-2024-001",
    evidence_count=5,
    entity_correlations=[...],
    timeline_events=[...],
    analysis_timestamp=datetime.now(),
    temporal_sequences=[...],
    timeline_gaps=[...],
    legal_patterns=patterns  # v3.1 enhancement
)
```

---

## Category 7: Case Summary & Reporting

### EvidenceSummary
**Purpose**: High-level summary of a single evidence item for case reports

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `sha256` | str | SHA256 identifier |
| `evidence_type` | str | Type (document, email, image) |
| `filename` | str | Original filename |
| `file_size` | int | Size in bytes (validated >= 0) |
| `analysis_confidence` | Optional[float] | AI confidence score (0.0-1.0) |
| `key_findings` | List[str] | Bullet points of findings |
| `legal_significance` | Optional[str] | Significance level (critical, high, medium, low) |
| `risk_flags` | List[str] | Risk indicators |

**v3.1 Pydantic Conversion**:
- **Converted from @dataclass to Pydantic BaseModel** for consistency with all other models
- **Added runtime validation**: `file_size >= 0`, `analysis_confidence 0.0-1.0`
- **Improved serialization**: Consistent JSON encoding with other models

**Usage**:
```python
summary = EvidenceSummary(
    sha256="abc123...",
    evidence_type="email",
    filename="complaint.eml",
    file_size=15000,
    analysis_confidence=0.95,
    key_findings=[
        "Employee filed formal harassment complaint",
        "Manager responded with threats",
        "HR escalation documented"
    ],
    legal_significance="critical",
    risk_flags=["retaliation", "threatening"]
)
```

### CaseSummary
**Purpose**: Complete case summary with all evidence and aggregated analysis

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `case_id` | str | Case identifier |
| `generation_timestamp` | datetime | When summary was generated |
| `evidence_count` | int | Total evidence items (validated >= 0) |
| `evidence_types` | List[str] | Types present |
| `evidence_summaries` | List[EvidenceSummary] | Per-evidence summaries |
| `correlation_result` | CorrelationAnalysis | Cross-evidence analysis (includes v3.1 legal_patterns) |
| `overall_assessment` | Dict[str, Any] | Aggregated metrics |
| `executive_summary` | Optional[str] | AI-generated summary |

**v3.1 Pydantic Conversion**:
- **Converted from @dataclass to Pydantic BaseModel** for consistency with all other models
- **Added runtime validation**: `evidence_count >= 0`
- **Improved serialization**: Consistent JSON encoding with datetime/float handling
- **Enhanced correlation**: Now includes v3.1 legal_patterns for contradiction/corroboration analysis

**Usage**:
```python
case = CaseSummary(
    case_id="CASE-2024-001",
    generation_timestamp=datetime.now(),
    evidence_count=5,
    evidence_types=["email", "document", "image"],
    evidence_summaries=[summary1, summary2],
    correlation_result=correlation,
    overall_assessment={
        "risk_level": "high",
        "legal_significance": "critical",
        "key_parties": ["Rachel Hemmings", "John Smith"]
    },
    executive_summary="Strong evidence of retaliation pattern..."
)
```

---

## Category 8: Operation Results

### IngestionResult
**Purpose**: Result of evidence ingestion operation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `sha256` | str | Evidence SHA256 |
| `file_path` | str | Original file path |
| `evidence_type` | EvidenceType | Evidence type |
| `metadata` | Optional[FileMetadata] | File metadata |
| `storage_path` | str | Storage location |
| `success` | bool | Whether ingestion succeeded |
| `message` | Optional[str] | Status/error message |

**Usage**:
```python
result = IngestionResult(
    sha256="abc123...",
    file_path="/cases/MY-CASE/complaint.pdf",
    evidence_type=EvidenceType.DOCUMENT,
    metadata=metadata,
    storage_path="/data/storage/raw/sha256=abc123.../original.pdf",
    success=True,
    message="Successfully ingested and linked to case MY-CASE"
)
```

### ExportResult
**Purpose**: Result of evidence export operation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `sha256` | str | Evidence SHA256 |
| `export_path` | str | Export destination |
| `analysis_included` | bool | Whether analysis was exported |
| `success` | bool | Whether export succeeded |
| `message` | Optional[str] | Status/error message |

### StorageStats
**Purpose**: Storage statistics for reporting (used by `evidence-toolkit storage stats`)

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `total_evidence` | int | Total evidence items |
| `evidence_by_type` | Dict[str, int] | Breakdown by type |
| `total_cases` | int | Number of cases |
| `total_labels` | int | Number of label categories |
| `storage_size_mb` | float | Total storage size (MB) |
| `raw_size_mb` | float | Raw evidence size (MB) |
| `derived_size_mb` | float | Analysis size (MB) |
| `orphaned_files` | int | Files not linked to any case |

### CaseInfo
**Purpose**: Case metadata for display in case management commands

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `case_id` | str | Case identifier |
| `evidence_count` | int | Number of evidence items |
| `evidence_types` | List[str] | Types present |
| `last_modified` | datetime | Last modification time |
| `total_size_mb` | float | Total size (MB) |

### CleanupResult
**Purpose**: Result of storage cleanup operation

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `broken_links_removed` | int | Broken hard links removed |
| `empty_dirs_removed` | int | Empty directories removed |
| `orphaned_files` | int | Orphaned files found |
| `dry_run` | bool | Whether this was a dry-run |

---

## Validation & Compliance

### Input Validation

All models use Pydantic v2 for automatic validation:

```python
from pydantic import Field

class DocumentEntity(BaseModel):
    confidence: float = Field(..., ge=0.0, le=1.0)  # Must be 0.0-1.0
    type: Literal["person", "organization", "date", "legal_term"]  # Enum constraint
```

**Common Constraints**:
- **SHA256 hashes**: `pattern=r"^[a-f0-9]{64}$"`
- **Confidence scores**: `ge=0.0, le=1.0` (0.0 to 1.0 inclusive)
- **Occurrence counts**: `ge=2` (correlations require 2+ matches)
- **File sizes**: `ge=1` (must be at least 1 byte)
- **Temperature**: `le=0.0` (≤0 for deterministic AI analysis)

### Output Validation

Models enforce forensic compliance through `Config`:

```python
class Config:
    json_encoders = {
        datetime: lambda dt: dt.isoformat(),  # ISO 8601 timestamps
        float: lambda v: round(v, 4)          # Consistent 4-decimal precision
    }
```

**Benefits**:
- **Reproducible timestamps**: ISO 8601 format
- **Consistent floating-point**: 4-decimal precision for confidence scores
- **Schema compliance**: Validates against OpenAI Responses API schemas

### Chain of Custody

Chain of custody is maintained through:
1. **ChainOfCustodyEvent** - Append-only event log
2. **ChainOfCustodyEntry** - Forensic bundle audit trail
3. **Immutable timestamps** - ISO 8601 format for legal admissibility

---

## Error Handling

### Common Validation Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `ValidationError: confidence must be <= 1.0` | Confidence > 1.0 | Normalize confidence scores before validation |
| `ValidationError: sha256 does not match pattern` | Invalid SHA256 format | Ensure SHA256 is lowercase, 64 hex characters |
| `ValidationError: occurrence_count must be >= 2` | Correlation with < 2 matches | Filter correlations to only include 2+ occurrences |
| `ValidationError: missing required field` | Missing required field | Check model schema with `.model_json_schema()` |

### Debugging Validation

```python
from pydantic import ValidationError

try:
    analysis = DocumentAnalysis(**data)
except ValidationError as e:
    print(e.json(indent=2))  # Pretty-print validation errors
```

---

## Performance Considerations

### Time Complexity
- **Model validation**: O(n) where n = number of fields
- **Nested validation**: O(n * m) where m = average nesting depth

### Space Complexity
- **Models are lightweight**: Only store data, no business logic
- **Large lists**: `entity_correlations`, `timeline_events` can grow with evidence count

### Optimization Notes
- Use `model_validate()` instead of `model_validate_json()` when data is already dict
- Use `model_dump()` instead of `model_dump_json()` when dict output is sufficient
- Cache `model_json_schema()` results to avoid regeneration

---

## Storage & Persistence

### File Locations

Models are persisted to:

```
data/storage/
├── derived/sha256=<hash>/
│   ├── analysis.v1.json          # UnifiedAnalysis
│   ├── evidence_bundle.v1.json   # EvidenceBundle
│   └── metadata.json             # FileMetadata
└── cases/<case-id>/
    └── cross_analysis.json       # CorrelationAnalysis
```

### Data Format

All models serialize to **JSON** using Pydantic:

```python
# Serialize to JSON string
json_str = model.model_dump_json(indent=2)

# Serialize to dict
data = model.model_dump()

# Deserialize from JSON
model = DocumentAnalysis.model_validate_json(json_str)

# Deserialize from dict
model = DocumentAnalysis.model_validate(data)
```

---

## Version History & Migration Guide

### v3.1 Layer 1 Enhancements (2025-10-05)

**New AI-Powered Features**:

1. **DocumentEntity Enhancements** (Legal Context):
   - `relationship: Optional[str]` - Captures entity relationships (e.g., "sent email to Rachel Hemmings")
   - `quoted_text: Optional[str]` - Extracts verbatim legally significant statements
   - `associated_event: Optional[str]` - Links date entities to specific events

2. **EmailParticipant Power Dynamics**:
   - `message_count: int` - Tracks message volume per participant
   - `deference_score: float` - Analyzes communication deference (0.0=dominant, 1.0=deferential)
   - `dominant_topics: List[str]` - Identifies topics controlled by participant

3. **Legal Pattern Analysis Models** (NEW):
   - `LegalPatternAnalysis` - AI-powered cross-evidence pattern detection
   - `Contradiction` - Conflicting statements across evidence
   - `CorroborationLink` - Evidence supporting same claims
   - Added to `CorrelationAnalysis.legal_patterns` field

4. **Pydantic Conversions** (Consistency):
   - `EvidenceSummary`: Converted from @dataclass to Pydantic BaseModel
   - `CaseSummary`: Converted from @dataclass to Pydantic BaseModel
   - Added runtime validation for all fields

**Migration from v3.0 to v3.1**:
```python
# v3.0: Basic entity extraction
entity = DocumentEntity(
    name="Person Name",
    type="person",
    confidence=0.95,
    context="Found in document"
)

# v3.1: Enhanced with relationship and quotes
entity = DocumentEntity(
    name="Person Name",
    type="person",
    confidence=0.95,
    context="Found in document",
    relationship="sent threatening email to colleague",  # NEW
    quoted_text="This will not be tolerated"  # NEW
)

# v3.1: Add legal pattern analysis to correlation
correlation = CorrelationAnalysis(
    case_id="CASE-001",
    evidence_count=5,
    entity_correlations=[...],
    timeline_events=[...],
    analysis_timestamp=datetime.now(),
    temporal_sequences=[...],
    timeline_gaps=[...],
    legal_patterns=LegalPatternAnalysis(  # NEW in v3.1
        contradictions=[...],
        corroboration=[...],
        evidence_gaps=[...],
        pattern_summary="...",
        confidence=0.88
    )
)
```

### v3.0 Major Refactor (2025-09-XX)

**Major Architectural Changes**:

1. **Models Consolidation**: 5+ files → 1 file (`core/models.py`)
2. **All Pydantic**: Dataclasses converted to Pydantic (including `CorrelationAnalysis`)
3. **Import Path Changes**:
   ```python
   # ❌ Old (v2.0)
   from document_analyzer.unified_models import UnifiedAnalysis
   from models.cross_analysis_models import CrossAnalysisBundle

   # ✅ New (v3.0)
   from evidence_toolkit.core.models import UnifiedAnalysis, CorrelationAnalysis
   ```

4. **Multi-Case Support**: `case_id` → `case_ids` (backward compatible via validator)
5. **CorrelationAnalysis**: Converted from @dataclass to Pydantic BaseModel
6. **Validation Consistency**: All models now use Pydantic v2 validation

### Breaking Changes Summary

**v3.0 → v3.1**:
- **None** - All new fields are optional or have defaults

**v2.0 → v3.0**:
- Import paths changed (old imports will fail)
- `CrossAnalysisBundle` renamed to `CorrelationAnalysis`
- `case_id` deprecated in favor of `case_ids` (backward compatible via validator)

---

## Dependencies

### Internal Dependencies
- **None** - Models are self-contained data structures

### External Dependencies
- `pydantic>=2.0` - Runtime validation
- `typing` - Type hints
- `enum` - Enumerations
- `datetime` - Timestamps

---

## Related Components

### Upstream Components (Who Creates These Models)
- **evidence_toolkit.analyzers.document** → `DocumentAnalysis`
- **evidence_toolkit.analyzers.image** → `ImageAnalysisStructured`
- **evidence_toolkit.analyzers.email** → `EmailThreadAnalysis`
- **evidence_toolkit.analyzers.correlation** → `CorrelationAnalysis`
- **evidence_toolkit.pipeline.ingest** → `IngestionResult`, `FileMetadata`
- **evidence_toolkit.pipeline.package** → `UnifiedAnalysis`, `CaseSummary`

### Downstream Components (Who Uses These Models)
- **evidence_toolkit.core.storage** - Reads/writes all models to disk
- **evidence_toolkit.pipeline.analyze** - Orchestrates analysis using models
- **evidence_toolkit.pipeline.package** - Generates client packages
- **evidence_toolkit.cli** - Displays model data in CLI commands

### Configuration
- **domains/legal_config.py** - Prompt templates for AI analysis
- **CLAUDE.md** - Project guidance
- **V3_ARCHITECTURE.md** - Architecture documentation

---

## Testing

### Unit Tests

```python
from evidence_toolkit.core.models import DocumentEntity, DocumentAnalysis

def test_document_entity_validation():
    """Test DocumentEntity field validation."""
    entity = DocumentEntity(
        name="Test Person",
        type="person",
        confidence=0.95,
        context="Found in document",
        relationship="mentioned by Manager"
    )
    assert entity.confidence == 0.95
    assert entity.type == "person"

def test_document_analysis_risk_flags():
    """Test DocumentAnalysis with risk flags."""
    analysis = DocumentAnalysis(
        summary="Test summary",
        entities=[],
        document_type="email",
        sentiment="hostile",
        legal_significance="high",
        risk_flags=["threatening", "retaliation_indicators"],
        confidence_overall=0.9
    )
    assert "threatening" in analysis.risk_flags
    assert analysis.sentiment == "hostile"
```

### Integration Tests

```python
def test_full_evidence_bundle():
    """Test complete EvidenceBundle creation."""
    bundle = EvidenceBundle(
        schema_version="1.0.0",
        case_id="TEST-001",
        evidence=EvidenceCore(
            evidence_id="test-id",
            sha256="a" * 64,
            mime_type="application/pdf",
            bytes=1000,
            ingested_at=datetime.now(),
            source_path="/test/path.pdf"
        ),
        chain_of_custody=[
            ChainOfCustodyEntry(
                ts=datetime.now(),
                actor="test-system",
                action="ingest",
                note="Test ingestion"
            )
        ],
        analyses=[]
    )

    # Serialize and deserialize
    json_str = bundle.model_dump_json()
    restored = EvidenceBundle.model_validate_json(json_str)
    assert restored.case_id == "TEST-001"
```

### Test Coverage
- **100% model validation** - All constraints tested
- **Serialization round-trips** - All models tested for JSON serialization/deserialization
- **Schema compliance** - OpenAI Responses API schemas validated

---

## Examples

### Example 1: Full Pipeline - Document Analysis

```python
from evidence_toolkit.core.models import (
    EvidenceType,
    FileMetadata,
    DocumentAnalysis,
    DocumentEntity,
    DocumentAnalysisResult,
    UnifiedAnalysis,
    ChainOfCustodyEvent
)
from datetime import datetime

# 1. Create file metadata
metadata = FileMetadata(
    filename="employee_complaint.pdf",
    file_size=125000,
    mime_type="application/pdf",
    created_time="2024-03-15T10:30:00Z",
    modified_time="2024-03-15T10:30:00Z",
    extension=".pdf",
    sha256="abc123def456..." * 4  # 64 chars
)

# 2. AI analysis (from OpenAI Responses API)
ai_analysis = DocumentAnalysis(
    summary="Employee harassment complaint filed against manager John Smith",
    entities=[
        DocumentEntity(
            name="Jane Doe",
            type="person",
            confidence=0.95,
            context="Complainant employee",
            relationship="filed complaint against John Smith",
            quoted_text="I have been subjected to hostile work environment"
        ),
        DocumentEntity(
            name="John Smith",
            type="person",
            confidence=0.98,
            context="Accused manager",
            relationship="supervisor of Jane Doe"
        ),
        DocumentEntity(
            name="March 1, 2024",
            type="date",
            confidence=0.92,
            context="Date of first incident",
            associated_event="Initial harassment incident"
        )
    ],
    document_type="filing",
    sentiment="hostile",
    legal_significance="critical",
    risk_flags=["harassment", "retaliation_indicators", "time_sensitive"],
    confidence_overall=0.94
)

# 3. Create document analysis result (includes legacy word frequency)
doc_result = DocumentAnalysisResult(
    total_words=500,
    unique_words=250,
    word_frequency={"harassment": 15, "hostile": 8},
    top_words=[("harassment", 15), ("hostile", 8)],
    openai_model="gpt-4o-2024-08-06",
    ai_summary=ai_analysis.summary,
    entities=[e.model_dump() for e in ai_analysis.entities],
    document_type=ai_analysis.document_type,
    sentiment=ai_analysis.sentiment,
    legal_significance=ai_analysis.legal_significance,
    risk_flags=ai_analysis.risk_flags,
    analysis_confidence=ai_analysis.confidence_overall
)

# 4. Create unified analysis (client package format)
unified = UnifiedAnalysis(
    evidence_type=EvidenceType.DOCUMENT,
    analysis_timestamp=datetime.now(),
    file_metadata=metadata,
    case_ids=["CASE-2024-001"],
    document_analysis=doc_result,
    chain_of_custody=[
        ChainOfCustodyEvent(
            timestamp=datetime.now(),
            event_type="ingest",
            actor="evidence-toolkit-v3.0",
            description="Evidence ingested into case CASE-2024-001"
        ),
        ChainOfCustodyEvent(
            timestamp=datetime.now(),
            event_type="analyze",
            actor="gpt-4o-2024-08-06",
            description="AI analysis completed",
            metadata={"confidence": 0.94}
        )
    ],
    labels=["harassment", "complaint", "critical"]
)

# 5. Serialize for storage
with open("data/storage/derived/sha256=abc123.../analysis.v1.json", "w") as f:
    f.write(unified.model_dump_json(indent=2))
```

### Example 2: Cross-Evidence Correlation

```python
from evidence_toolkit.core.models import (
    CorrelationAnalysis,
    CorrelatedEntity,
    TimelineEvent,
    LegalPatternAnalysis,
    Contradiction,
    CorroborationLink
)
from datetime import datetime

# 1. Create correlation analysis
correlation = CorrelationAnalysis(
    case_id="CASE-2024-001",
    evidence_count=5,
    entity_correlations=[
        CorrelatedEntity(
            entity_name="Jane Doe",
            entity_type="person",
            occurrence_count=4,
            confidence_average=0.96,
            evidence_occurrences=[
                {"evidence_sha256": "abc123...", "context": "Complainant"},
                {"evidence_sha256": "def456...", "context": "Email sender"},
                {"evidence_sha256": "ghi789...", "context": "Meeting attendee"},
                {"evidence_sha256": "jkl012...", "context": "HR complaint"}
            ]
        ),
        CorrelatedEntity(
            entity_name="John Smith",
            entity_type="person",
            occurrence_count=3,
            confidence_average=0.94,
            evidence_occurrences=[
                {"evidence_sha256": "abc123...", "context": "Accused manager"},
                {"evidence_sha256": "def456...", "context": "Email recipient"},
                {"evidence_sha256": "mno345...", "context": "Denial statement"}
            ]
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
        ),
        TimelineEvent(
            timestamp=datetime(2024, 3, 5, 14, 30),
            evidence_sha256="def456...",
            evidence_type="email",
            event_type="communication",
            description="Employee reported incident to HR",
            confidence=0.95,
            ai_classification={"pattern": "reporting", "severity": 0.6}
        ),
        TimelineEvent(
            timestamp=datetime(2024, 3, 10, 9, 0),
            evidence_sha256="ghi789...",
            evidence_type="email",
            event_type="retaliation",
            description="Manager threatened employee after complaint",
            confidence=0.88,
            ai_classification={"pattern": "retaliation_sequence", "severity": 0.9}
        )
    ],
    analysis_timestamp=datetime.now(),
    temporal_sequences=[
        {
            "pattern": "retaliation_sequence",
            "events": ["incident", "reporting", "retaliation"],
            "severity": 0.9,
            "confidence": 0.87
        }
    ],
    timeline_gaps=[
        {
            "gap_start": "2024-03-05",
            "gap_end": "2024-03-10",
            "duration_days": 5,
            "significance": "Missing evidence between complaint and retaliation"
        }
    ],
    legal_patterns=LegalPatternAnalysis(
        contradictions=[
            Contradiction(
                statement_1="I never received any complaint from Jane",
                statement_1_source="mno345...",
                statement_2="I addressed Jane's concerns on March 6th",
                statement_2_source="def456...",
                contradiction_type="factual",
                severity=0.92,
                explanation="Manager claims both not receiving and addressing the complaint"
            )
        ],
        corroboration=[
            CorroborationLink(
                claim="Harassment incident occurred on March 1st",
                supporting_evidence=["abc123...", "def456...", "ghi789..."],
                corroboration_strength="strong",
                explanation="Complaint, HR email, and witness statement all confirm March 1st"
            )
        ],
        evidence_gaps=[
            "No direct evidence of alleged March 3rd follow-up meeting",
            "Missing email thread referenced in complaint (March 2nd)"
        ],
        pattern_summary="Strong retaliation pattern with contradictory manager statements and corroborated timeline",
        confidence=0.89
    )
)

# 2. Serialize for storage
with open("data/storage/cases/CASE-2024-001/cross_analysis.json", "w") as f:
    f.write(correlation.model_dump_json(indent=2))
```

### Example 3: Email Thread Analysis

```python
from evidence_toolkit.core.models import (
    EmailThreadAnalysis,
    EmailParticipant,
    EscalationEvent
)

# Create comprehensive email thread analysis
email_analysis = EmailThreadAnalysis(
    thread_summary="HR complaint escalated with hostile managerial response and retaliation threats",
    participants=[
        EmailParticipant(
            email_address="jane.doe@company.com",
            display_name="Jane Doe",
            role="sender",
            authority_level="employee",
            confidence=0.95,
            message_count=3,
            deference_score=0.75,  # Deferential
            dominant_topics=[]
        ),
        EmailParticipant(
            email_address="john.smith@company.com",
            display_name="John Smith",
            role="recipient",
            authority_level="management",
            confidence=0.95,
            message_count=2,
            deference_score=0.15,  # Highly dominant
            dominant_topics=["consequences", "performance review", "deadline"]
        ),
        EmailParticipant(
            email_address="hr@company.com",
            display_name="HR Department",
            role="cc",
            authority_level="management",
            confidence=0.90,
            message_count=1,
            deference_score=0.5,  # Neutral
            dominant_topics=["policy"]
        )
    ],
    communication_pattern="escalating",
    sentiment_progression=[0.7, 0.5, 0.3, 0.2],  # Deteriorating tone
    escalation_events=[
        EscalationEvent(
            email_position=1,
            escalation_type="tone_change",
            confidence=0.92,
            description="Manager's tone shifted from professional to hostile",
            context="I will not tolerate this insubordination"
        ),
        EscalationEvent(
            email_position=2,
            escalation_type="authority_escalation",
            confidence=0.88,
            description="Employee escalated to HR (cc'd on response)",
            context="CC: HR Department"
        ),
        EscalationEvent(
            email_position=3,
            escalation_type="threat",
            confidence=0.95,
            description="Manager threatened performance review consequences",
            context="This will be reflected in your next performance review"
        )
    ],
    legal_significance="critical",
    risk_flags=["threatening", "retaliation", "hostile_takeover"],
    timeline_reconstruction=[
        "2024-03-05 10:00 - Employee filed initial complaint",
        "2024-03-05 14:30 - Manager responded with hostile tone",
        "2024-03-06 09:00 - Employee escalated to HR",
        "2024-03-06 11:00 - Manager sent retaliatory threat"
    ],
    confidence_overall=0.91
)

print(f"Thread pattern: {email_analysis.communication_pattern}")
print(f"Escalations detected: {len(email_analysis.escalation_events)}")
print(f"Risk flags: {email_analysis.risk_flags}")
```

---

## Future Considerations

### Planned Enhancements
1. **Audio/Video Analysis Models** - Models for AUDIO and VIDEO evidence types
2. **Multi-Language Support** - Language field in analysis models
3. **Advanced Timeline Analysis** - Graph-based timeline reconstruction
4. **Witness Statement Models** - Structured witness testimony analysis
5. **Privilege Logging** - Attorney-client privilege tracking

### Known Limitations
1. **Large Entity Lists** - No pagination for entity correlations (may impact performance with 1000+ entities)
2. **Timeline Resolution** - Events are datetime-granular (no sub-second precision)
3. **Fixed Schema Versions** - Schema migrations not yet automated

### Technical Debt
1. **Backwards Compatibility** - `case_id` deprecated but maintained via validator
2. **Legacy Word Frequency** - `DocumentAnalysisResult` still includes word frequency (may remove in v4.0)

---

## API Reference Summary

### Key Models by Use Case

**Evidence Ingestion**:
- `FileMetadata`
- `IngestionResult`
- `ChainOfCustodyEvent`

**AI Analysis**:
- `DocumentAnalysis`, `DocumentEntity`
- `ImageAnalysisStructured`
- `EmailThreadAnalysis`, `EmailParticipant`, `EscalationEvent`

**Client Packages**:
- `UnifiedAnalysis`
- `DocumentAnalysisResult`
- `ImageAnalysisResult`

**Forensic Storage**:
- `EvidenceBundle`
- `EvidenceCore`
- `DocumentAnalysisRecord`
- `ChainOfCustodyEntry`

**Cross-Evidence**:
- `CorrelationAnalysis`
- `CorrelatedEntity`
- `TimelineEvent`
- `LegalPatternAnalysis`

**Case Reporting**:
- `CaseSummary`
- `EvidenceSummary`

**Storage Management**:
- `StorageStats`
- `CaseInfo`
- `CleanupResult`

---

## Quick Reference

### Common Imports
```python
# Base types
from evidence_toolkit.core.models import (
    EvidenceType,
    FileMetadata,
    ChainOfCustodyEvent
)

# AI analysis
from evidence_toolkit.core.models import (
    DocumentAnalysis,
    DocumentEntity,
    ImageAnalysisStructured,
    EmailThreadAnalysis
)

# Client packages
from evidence_toolkit.core.models import (
    UnifiedAnalysis,
    DocumentAnalysisResult,
    ImageAnalysisResult
)

# Forensic bundles
from evidence_toolkit.core.models import (
    EvidenceBundle,
    EvidenceCore,
    DocumentAnalysisRecord
)

# Cross-evidence
from evidence_toolkit.core.models import (
    CorrelationAnalysis,
    CorrelatedEntity,
    TimelineEvent,
    LegalPatternAnalysis
)

# Case summary
from evidence_toolkit.core.models import (
    CaseSummary,
    EvidenceSummary
)

# Operations
from evidence_toolkit.core.models import (
    IngestionResult,
    ExportResult,
    StorageStats,
    CaseInfo,
    CleanupResult
)
```

---

**This documentation provides complete coverage of the Evidence Toolkit v3.0 core models module, following forensic/legal documentation standards for clarity, completeness, and maintainability.**
