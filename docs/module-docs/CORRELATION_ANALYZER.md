# Documentation: Correlation Analyzer

## Overview

The Correlation Analyzer module (`src/evidence_toolkit/analyzers/correlation.py`) is the cross-evidence analysis engine that identifies patterns, relationships, and connections across multiple pieces of evidence in a case. It extracts entities from AI-analyzed evidence, correlates them using deterministic name canonicalization, constructs forensic timelines, and detects legal patterns including contradictions, corroboration, and evidence gaps.

This module transforms isolated evidence analysis into a cohesive narrative by finding entities that appear across multiple evidence pieces, reconstructing event timelines, and identifying legally significant temporal patterns. It represents the culmination of the Evidence Toolkit's forensic analysis capabilities, providing the cross-evidence insights that are critical for legal proceedings.

## Purpose & Scope

### What It Does
- **Entity Correlation**: Extracts entities from AI-analyzed evidence (documents, emails, images) and finds entities appearing in multiple pieces
- **Deterministic Name Matching**: Uses robust canonicalization algorithm to match entity name variants (e.g., "John Q. Smith", "Smith, John", "John Smith")
- **Timeline Reconstruction**: Builds chronological event sequence from evidence metadata, email dates, EXIF timestamps, and document references
- **Temporal Pattern Detection**: Identifies legally significant event clusters (retaliation sequences, escalation patterns, communication bursts)
- **Timeline Gap Analysis**: Detects suspicious gaps in evidence (potential spoliation, missing communications, investigation blind spots)
- **AI Pattern Detection (v3.1)**: Uses OpenAI Responses API to detect contradictions, corroboration, and evidence gaps across evidence
- **Forensic Validation**: All outputs validated with Pydantic models for legal compliance

### What It Does NOT Do
- Does NOT analyze individual evidence pieces (that's handled by DocumentAnalyzer, EmailAnalyzer, ImageAnalyzer)
- Does NOT modify or access raw evidence files (uses analyzed results from derived/ storage)
- Does NOT perform semantic entity matching (uses deterministic string-based canonicalization)
- Does NOT predict or speculate (provides evidence-based analysis only)

### Why This Exists
Cross-evidence correlation is essential for:
1. **Credibility Assessment**: Identify conflicting witness statements
2. **Timeline Reconstruction**: Build coherent chronology from fragmented evidence
3. **Pattern Recognition**: Detect retaliation sequences, escalation patterns, evidence tampering
4. **Relationship Mapping**: Understand who communicated with whom, when, and about what
5. **Evidence Quality**: Identify gaps, inconsistencies, and corroboration
6. **Legal Strategy**: Provide actionable insights for case preparation

## Usage

### Basic Usage

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

# Initialize storage
storage = EvidenceStorage("data/storage")

# Create analyzer (without AI pattern detection)
analyzer = CorrelationAnalyzer(storage)

# Analyze all correlations for a case
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Access results
print(f"Evidence pieces analyzed: {result.evidence_count}")
print(f"Entities found in multiple pieces: {len(result.entity_correlations)}")
print(f"Timeline events: {len(result.timeline_events)}")

# Top correlated entities
for entity in result.entity_correlations[:5]:
    print(f"- {entity.entity_name} ({entity.entity_type}): {entity.occurrence_count} occurrences")
    print(f"  Confidence: {entity.confidence_average:.2f}")
```

### Advanced Usage with AI Pattern Detection (v3.1)

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer
from openai import OpenAI

# Initialize storage and OpenAI client
storage = EvidenceStorage("data/storage")
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Create analyzer with AI pattern detection enabled
analyzer = CorrelationAnalyzer(
    storage,
    openai_client=openai_client,
    verbose=True
)

# Analyze correlations (includes AI pattern detection)
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Access AI-detected patterns
if result.legal_patterns:
    print(f"Contradictions detected: {len(result.legal_patterns.contradictions)}")
    print(f"Corroboration links: {len(result.legal_patterns.corroboration)}")
    print(f"Evidence gaps: {len(result.legal_patterns.evidence_gaps)}")

    # Example: Print contradictions
    for contradiction in result.legal_patterns.contradictions:
        print(f"\nContradiction ({contradiction.contradiction_type}):")
        print(f"  Statement 1: {contradiction.statement_1}")
        print(f"  Source: {contradiction.statement_1_source[:8]}")
        print(f"  Statement 2: {contradiction.statement_2}")
        print(f"  Source: {contradiction.statement_2_source[:8]}")
        print(f"  Severity: {contradiction.severity:.2f}")
```

### AI Entity Resolution (v3.2) - Advanced Correlation

**Purpose**: Use AI to resolve ambiguous entity name matches that deterministic canonicalization misses

**When to Use**:
- Cases with nicknames or informal names ("Paul" vs "Paul Boucherat")
- Multiple people with similar names ("John Smith" in Finance vs "John Smith" in HR)
- Cross-cultural name variations ("李明" vs "Ming Li")
- Complex legal cases where precision is critical

**How It Works**:
1. String canonicalization finds obvious correlations (e.g., "John Smith" = "Smith, John")
2. AI compares remaining single-evidence entities with existing correlations
3. AI also compares unmatched singles with each other to bootstrap new correlations
4. Uses context (organization, role, email domain, events) to make matching decisions
5. Conservative bias: false negatives preferred over false positives (forensic accuracy)

**Usage Example**:

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer
from openai import OpenAI

# Initialize with OpenAI client for AI entity resolution
storage = EvidenceStorage("data/storage")
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

analyzer = CorrelationAnalyzer(
    storage,
    openai_client=openai_client,
    verbose=True
)

# Enable AI entity resolution with ai_resolve=True
result = analyzer.analyze_case_correlations("CASE-2024-001", ai_resolve=True)

# Compare correlation counts
print(f"Entities correlated: {len(result.entity_correlations)}")
print(f"(Without AI, string matching found fewer correlations)")

# Example: AI matched "Paul" → "Paul Boucherat" using email context
for entity in result.entity_correlations:
    if "paul" in entity.entity_name.lower():
        print(f"\nEntity: {entity.entity_name}")
        print(f"Appears in: {entity.occurrence_count} evidence pieces")
        for occ in entity.evidence_occurrences:
            print(f"  - {occ['original_name']} (confidence: {occ['confidence']:.2f})")
            print(f"    Context: {occ['context'][:80]}...")
```

**CLI Usage**:

```bash
# Standard correlation (deterministic matching only)
uv run evidence-toolkit correlate --case-id MY-CASE

# Enhanced correlation with AI entity resolution (v3.2)
uv run evidence-toolkit correlate --case-id MY-CASE --ai-resolve

# Full pipeline with AI resolution
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE --ai-resolve
```

**Performance Notes**:
- Adds ~10-20 seconds for AI calls (limited to 50 comparisons max)
- Only compares person entities (skips email addresses, organizations, dates)
- Skips entities already matched by string canonicalization
- Verbose mode shows AI matching decisions in real-time

**Cost Considerations**:
- Uses `gpt-4o-mini` model (fast and cost-effective)
- Typical cost: ~$0.01-0.05 per case (50 AI calls × ~500 tokens each)
- Only runs when explicitly enabled with `ai_resolve=True` or `--ai-resolve`

### Entity Canonicalization Example

```python
from evidence_toolkit.analyzers.correlation import canonicalize_entity_name

# Example: Matching name variants
variants = [
    "John Q. Smith",
    "Smith, John",
    "John Smith",
    "J. Smith"
]

for name in variants:
    base, short, initials = canonicalize_entity_name(name)
    print(f"{name:20s} -> base={base}, short={short}, initials={initials}")

# Output:
# John Q. Smith        -> base=john q smith, short=john smith, initials=j q s
# Smith, John          -> base=john smith, short=john smith, initials=j s
# John Smith           -> base=john smith, short=john smith, initials=j s
# J. Smith             -> base=j smith, short=j smith, initials=j s
```

### CLI Usage

```bash
# Full case processing (includes correlation analysis)
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE

# Standalone correlation analysis (after evidence is analyzed)
uv run evidence-toolkit correlate --case-id MY-CASE

# v3.2: AI entity resolution for edge cases (nicknames, initials, etc.)
uv run evidence-toolkit correlate --case-id MY-CASE --ai-resolve

# Generate client package (includes correlation report)
uv run evidence-toolkit package --case-id MY-CASE
```

**When to use `--ai-resolve`**:
- Entity name variations that string matching misses ("Paul" vs "P. Boucherat")
- Nickname matching ("Bob" vs "Robert Smith")
- Complex legal cases where precision is critical
- **Note**: Adds ~10-20s for AI calls (50 comparison limit)

## Architecture

### Module Structure

```
src/evidence_toolkit/
├── analyzers/
│   ├── correlation.py          # THIS MODULE
│   ├── document.py             # Provides entity data for correlation
│   ├── email.py                # Provides participant data for correlation
│   └── image.py                # Provides OCR text for correlation
│
├── core/
│   ├── models.py               # CorrelationAnalysis, CorrelatedEntity, TimelineEvent
│   └── storage.py              # EvidenceStorage for accessing analyzed evidence
│
├── domains/
│   └── legal_config.py         # CORRELATION_PATTERN_PROMPT, CRITICAL_RISK_FLAGS
│
└── pipeline/
    ├── analyze.py              # Populates entity data used by correlation
    └── package.py              # Consumes correlation results for client packages
```

### Data Flow

```
Individual Evidence Analysis (per file)
        ↓
AI Entity Extraction (DocumentEntity, EmailParticipant objects)
        ↓
Storage (analysis.v1.json in derived/sha256=<hash>/)
        ↓
Correlation Analyzer (reads all case evidence)
        ↓
Entity Extraction (pulls entities from all evidence)
        ↓
Canonicalization (normalize name variants)
        ↓
Correlation Detection (find entities in 2+ pieces)
        ↓
Timeline Reconstruction (extract temporal events)
        ↓
Pattern Detection (temporal sequences, gaps, AI patterns)
        ↓
CorrelationAnalysis (Pydantic validated output)
        ↓
Client Package (correlation_analysis.json)
```

### Data Models

The Correlation Analyzer uses the following Pydantic models from `core/models.py`:

#### CorrelatedEntity
```python
class CorrelatedEntity(BaseModel):
    entity_name: str                      # Canonical display name
    entity_type: str                      # person, organization, email_address, etc.
    occurrence_count: int                 # Number of evidence pieces (≥2)
    confidence_average: float             # Average confidence across occurrences
    evidence_occurrences: List[Dict]      # Details of each occurrence
```

#### TimelineEvent
```python
class TimelineEvent(BaseModel):
    timestamp: datetime                   # When the event occurred
    evidence_sha256: str                  # Source evidence
    evidence_type: str                    # document, email, image
    event_type: str                       # communication, photo_taken, file_created, etc.
    description: str                      # Human-readable description
    confidence: float                     # Extraction confidence (0.0-1.0)
    ai_classification: Optional[Dict]     # AI-detected pattern metadata
```

#### CorrelationAnalysis (Output)
```python
class CorrelationAnalysis(BaseModel):
    case_id: str                          # Case identifier
    evidence_count: int                   # Evidence pieces analyzed
    entity_correlations: List[CorrelatedEntity]  # Entities in 2+ pieces
    timeline_events: List[TimelineEvent]  # Chronological event sequence
    temporal_sequences: List[Dict]        # Detected event patterns
    timeline_gaps: List[Dict]             # Suspicious timeline gaps
    legal_patterns: Optional[LegalPatternAnalysis]  # v3.1: AI-detected patterns
    analysis_timestamp: datetime          # When analysis was performed
```

#### LegalPatternAnalysis (v3.1)
```python
class LegalPatternAnalysis(BaseModel):
    contradictions: List[Contradiction]   # Conflicting statements
    corroboration: List[CorroborationLink]  # Supporting evidence
    evidence_gaps: List[str]              # Missing evidence
    pattern_summary: str                  # AI-generated overview
    confidence: float                     # Overall pattern confidence
```

## API Reference

### Main Class: CorrelationAnalyzer

#### Constructor

```python
def __init__(
    self,
    evidence_storage: EvidenceStorage,
    openai_client: Optional[Any] = None,
    verbose: bool = True
)
```

**Parameters**:
- `evidence_storage`: EvidenceStorage instance for accessing analyzed evidence
- `openai_client`: Optional OpenAI client for v3.1 AI pattern detection (if None, pattern detection is skipped)
- `verbose`: Enable verbose output for pattern detection progress

**Example**:
```python
storage = EvidenceStorage("data/storage")
analyzer = CorrelationAnalyzer(storage, openai_client=None, verbose=True)
```

#### analyze_case_correlations()

```python
def analyze_case_correlations(self, case_id: str) -> CorrelationAnalysis
```

**Purpose**: Main entry point - analyzes all correlations for a case

**Parameters**:
- `case_id`: Case identifier to analyze

**Returns**: CorrelationAnalysis Pydantic model with complete results

**Process**:
1. Get all evidence for case from storage
2. Extract entities from each evidence piece
3. Find correlations (entities in 2+ pieces)
4. Extract timeline events
5. Detect temporal patterns and gaps
6. Run AI pattern detection (if enabled)
7. Return validated CorrelationAnalysis

**Example**:
```python
result = analyzer.analyze_case_correlations("CASE-2024-001")
print(f"Found {len(result.entity_correlations)} correlated entities")
```

### Key Functions

#### canonicalize_entity_name()

```python
def canonicalize_entity_name(name: str) -> Tuple[str, str, str]
```

**Purpose**: Deterministic entity name normalization for robust matching across evidence

**Algorithm**:
1. Unicode normalization (NFKC - compatibility composition)
2. Collapse multiple spaces
3. Case folding (casefold() - better than lower() for Unicode)
4. Role variant normalization (e.g., "Chief Executive Officer" → "ceo")
5. "Last, First" format handling (e.g., "Smith, John" → "John Smith")
6. Word extraction (alphanumeric only)
7. Generate three variants:
   - **base**: All words joined (e.g., "john q smith")
   - **short**: First + last only (e.g., "john smith")
   - **initials**: First letter of each word (e.g., "j q s")

**Parameters**:
- `name`: Entity name to canonicalize

**Returns**: Tuple of (base_form, short_form, initials)

**Examples**:
```python
>>> canonicalize_entity_name("John Q. Smith")
("john q smith", "john smith", "j q s")

>>> canonicalize_entity_name("Smith, John")
("john smith", "john smith", "j s")

>>> canonicalize_entity_name("Chief Executive Officer")
("ceo", "ceo", "c")

>>> canonicalize_entity_name("Paul Boucherat")
("paul boucherat", "paul boucherat", "p b")
```

**Rationale**: This deterministic algorithm enables robust entity matching without AI/ML:
- Handles name variants (full name, short form, initials)
- Handles different formats ("First Last", "Last, First")
- Handles role abbreviations (CEO, CFO, HR)
- Unicode-safe (handles accents, special characters)
- Deterministic (same input → same output, every time)

#### _extract_entities_from_evidence()

```python
def _extract_entities_from_evidence(
    self,
    evidence_items: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]
```

**Purpose**: Extract all entities from analyzed evidence

**Process**:
1. For each evidence piece:
   - **Documents**: Extract DocumentEntity objects from AI analysis (entities field)
   - **Emails**: Extract EmailParticipant objects (email addresses + display names)
   - **Images**: Extract OCR text entities (capitalized words)
2. Canonicalize each entity name
3. Index by all variants (base, short, initials) for robust matching

**Returns**: Dictionary mapping canonical names to entity occurrences

**Example**:
```python
# Input: 3 evidence pieces
# Output: {'john smith': [occ1, occ2, occ3], 'paul boucherat': [occ1, occ2], ...}
entities = analyzer._extract_entities_from_evidence(evidence_items)
```

#### _find_entity_correlations()

```python
def _find_entity_correlations(
    self,
    all_entities: Dict[str, List[Dict[str, Any]]]
) -> List[CorrelatedEntity]
```

**Purpose**: Find entities appearing in multiple evidence pieces with deduplication

**Algorithm**:
1. For each canonical name bucket:
   - Get unique original names (handles variant indexing)
   - Get unique evidence pieces (same entity may appear via multiple variants)
   - If entity appears in 2+ pieces → create correlation
2. Deduplication: Keep highest confidence occurrence per evidence piece
3. Calculate average confidence across all occurrences
4. Determine most common entity type (majority vote)
5. Select best display name (longest proper name)
6. Sort by occurrence count, then confidence

**Returns**: List of CorrelatedEntity models (sorted by importance)

**Example**:
```python
# Input: {'john smith': [occ1, occ2, occ3], ...}
# Output: [CorrelatedEntity(name='John Smith', count=3, conf=0.92), ...]
correlations = analyzer._find_entity_correlations(entities)
```

#### _extract_timeline_events()

```python
def _extract_timeline_events(
    self,
    evidence_items: List[Dict[str, Any]]
) -> List[TimelineEvent]
```

**Purpose**: Extract chronological events from evidence metadata and content

**Event Sources**:
1. **File metadata**: Created time, modified time
2. **Analysis metadata**: Analysis timestamp
3. **Email headers**: Send/receive dates (parsed with email.utils.parsedate_to_datetime)
4. **EXIF data**: Photo capture timestamps (DateTimeOriginal)
5. **Document content**: Date entity references (parsed with dateutil.parser)

**AI Classification**: Attaches AI-detected metadata to timeline events:
- Communication pattern (professional, escalating, hostile, retaliatory)
- Risk flags (retaliation, harassment, discrimination)
- Legal significance (critical, high, medium, low)
- Escalation count (number of escalation events detected)

**Returns**: List of TimelineEvent models (unsorted - caller sorts)

**Example**:
```python
# Input: Evidence with email dates, EXIF timestamps, document references
# Output: [TimelineEvent(ts=2024-01-15, type='communication', ...), ...]
events = analyzer._extract_timeline_events(evidence_items)
```

#### _detect_temporal_sequences()

```python
def _detect_temporal_sequences(
    self,
    timeline_events: List[TimelineEvent],
    temporal_window_hours: int = 72
) -> List[Dict]
```

**Purpose**: Detect legally significant temporal patterns (retaliation sequences, escalation patterns)

**Algorithm**:
1. Filter to forensically relevant events (exclude ingestion artifacts like file_created, analysis_performed)
2. For each high-value anchor event:
   - High/critical legal significance
   - Hostile/retaliatory communication pattern
   - Retaliation/harassment/discrimination risk flags
3. Find nearby events within temporal window (default 72 hours = 3 days)
4. Assess pattern significance:
   - Critical risk flags present → high significance
   - Critical legal significance → high significance
   - Multiple events (3+) in window → medium significance
5. Return sequence metadata with risk flags

**Returns**: List of detected sequences with legal significance assessment

**Example**:
```python
# Input: Timeline with hostile email followed by termination within 48 hours
# Output: [{'anchor_event': {...}, 'related_events': [...], 'legal_significance': 'high'}]
sequences = analyzer._detect_temporal_sequences(timeline_events)
```

#### _detect_timeline_gaps()

```python
def _detect_timeline_gaps(
    self,
    timeline_events: List[TimelineEvent],
    significant_gap_hours: int = 168
) -> List[Dict]
```

**Purpose**: Identify suspicious gaps in evidence timeline (potential spoliation, missing communications)

**Algorithm**:
1. Filter to forensically relevant events (exclude ingestion artifacts)
2. For each consecutive pair of events:
   - Calculate gap duration
   - If gap > threshold (default 168 hours = 7 days) → flag as significant
3. Assess significance:
   - 30+ days → high significance
   - 14-30 days → medium significance
   - 7-14 days → low significance

**Returns**: List of detected gaps with significance assessment

**Example**:
```python
# Input: Timeline with 21-day gap between communications
# Output: [{'gap_duration_days': 21, 'significance': 'medium', ...}]
gaps = analyzer._detect_timeline_gaps(timeline_events)
```

#### _detect_legal_patterns() (v3.1)

```python
def _detect_legal_patterns(
    self,
    case_id: str,
    correlations: List[CorrelatedEntity],
    timeline_events: List[TimelineEvent],
    evidence_items: List[Dict[str, Any]]
) -> Optional[LegalPatternAnalysis]
```

**Purpose**: Use AI to detect contradictions, corroboration, and evidence gaps across evidence

**Process**:
1. Check if OpenAI client is available (skip if not)
2. Build context from correlation data (entities, timeline, evidence summaries)
3. Call OpenAI Responses API with CORRELATION_PATTERN_PROMPT
4. Parse response into LegalPatternAnalysis Pydantic model
5. Return AI-detected patterns or None if unavailable

**Returns**: LegalPatternAnalysis or None

**Example**:
```python
# Input: Correlation data + timeline + evidence
# Output: LegalPatternAnalysis(contradictions=[...], corroboration=[...], ...)
patterns = analyzer._detect_legal_patterns(case_id, correlations, timeline, evidence)
```

## Behavior

### Core Functionality

The Correlation Analyzer operates in a **three-phase analysis pipeline**:

#### Phase 1: Entity Extraction
1. Load all analyzed evidence for case from `derived/sha256=<hash>/analysis.v1.json`
2. Extract entities based on evidence type:
   - **Documents**: DocumentEntity objects (name, type, confidence, context, relationship, quoted_text)
   - **Emails**: EmailParticipant objects (email_address, display_name, role, authority_level)
   - **Images**: OCR text entities (capitalized words from detected_text)
3. Canonicalize each entity name into 3 variants (base, short, initials)
4. Index entities by ALL variants for robust matching
5. Result: Dictionary mapping canonical names → occurrences

#### Phase 2: Correlation
1. For each canonical name bucket:
   - Check if entity appears in 2+ evidence pieces (cross-evidence requirement)
   - Deduplicate variant-based occurrences (keep highest confidence per evidence)
   - Calculate average confidence across all occurrences
   - Determine most common entity type (majority vote across occurrences)
   - Select best display name (longest proper name for readability)
2. Sort correlations by (occurrence_count, confidence_average) descending
3. Result: List of CorrelatedEntity models (most important entities first)

#### Phase 3: Timeline + Pattern Detection
1. **Timeline Reconstruction**:
   - Extract temporal events from evidence metadata (file timestamps, email dates, EXIF)
   - Extract content-based dates (document date references parsed with dateutil)
   - Attach AI classification metadata (communication patterns, risk flags, legal significance)
   - Sort chronologically for coherent narrative

2. **Temporal Pattern Detection**:
   - Detect significant event sequences (retaliation, escalation, communication bursts)
   - Identify timeline gaps (potential spoliation, missing evidence)
   - Focus on high-value patterns (critical risk flags, hostile communications)

3. **AI Pattern Detection (v3.1)**:
   - Build context from correlation + timeline + evidence summaries
   - Call OpenAI Responses API with CORRELATION_PATTERN_PROMPT
   - Parse contradictions, corroboration, evidence gaps
   - Validate with LegalPatternAnalysis Pydantic model

4. Result: CorrelationAnalysis with complete cross-evidence insights

### Deterministic Entity Matching

The canonicalization algorithm ensures **deterministic, reproducible matching** without AI/ML:

**Why Deterministic?**
- Legal evidence requires reproducible results
- No black-box ML models (transparency for legal review)
- Same input → same output, every time
- No training data or model updates affecting results

**How It Works**:
```python
# Example: Three name variants for same person
"John Q. Smith"    → ("john q smith", "john smith", "j q s")
"Smith, John"      → ("john smith", "john smith", "j s")
"J. Smith"         → ("j smith", "j smith", "j s")

# All three get indexed in shared buckets:
# - "john smith" bucket: contains occurrences from all three variants
# - "j s" bucket: contains occurrences from variants 1 and 2
# Result: Correlation analyzer finds all three as same entity
```

**Edge Cases Handled**:
- Unicode normalization (accents, special characters)
- Multiple spaces, punctuation, case variations
- "Last, First" email header format
- Role abbreviations (CEO, CFO, VP, HR)
- Middle names and initials
- Compound last names (hyphenated)

## AI Integration

### v3.1 Legal Pattern Detection

The Correlation Analyzer uses the **OpenAI Responses API** (same pattern as DocumentAnalyzer, EmailAnalyzer) for cross-evidence pattern detection.

#### Model Used
```python
model = "gpt-4.1-mini"  # Cost-effective model for pattern detection
temperature = 0.0       # Deterministic for forensic quality (implied by Responses API)
```

#### Prompt Used
```python
from evidence_toolkit.domains.legal_config import CORRELATION_PATTERN_PROMPT
```

**Prompt Focus**:
1. Contradictions (factual, temporal, attribution)
2. Corroboration (weak, moderate, strong)
3. Evidence gaps (missing witnesses, documentation, unexplained absences)
4. Pattern summary (overall assessment + legal significance)

#### Response Format
```python
from evidence_toolkit.core.models import LegalPatternAnalysis

response = openai_client.responses.parse(
    model="gpt-4.1-mini",
    input=[
        {"role": "system", "content": CORRELATION_PATTERN_PROMPT},
        {"role": "user", "content": context}
    ],
    text_format=LegalPatternAnalysis  # Pydantic model for schema validation
)

# Handle response (same pattern as other analyzers)
if response.status == "completed" and response.output_parsed:
    return response.output_parsed  # LegalPatternAnalysis instance
elif response.status == "incomplete":
    print(f"Analysis incomplete: {response.incomplete_details}")
    return None
else:
    # Check for refusal
    if response.output[0].content[0].type == "refusal":
        print(f"Analysis refused: {response.output[0].content[0].refusal}")
    return None
```

#### Context Building
The analyzer provides AI with:
1. **Entity Correlations** (top 20 entities):
   ```
   - Paul Boucherat (person): appears in 5 evidence pieces, avg confidence 0.92
   - Rachel Hemmings (person): appears in 4 evidence pieces, avg confidence 0.89
   ```

2. **Timeline Events** (recent 30 events):
   ```
   - 2024-01-15T10:30:00: Email: Subject: Meeting Request (sha256: 2401112d...)
   - 2024-01-20T14:15:00: Email: Subject: Follow-up (sha256: 7b3c4a2f...)
   ```

3. **Evidence Summaries** (first 10 pieces):
   ```
   [2401112d] Document: This letter details a complaint filed against...
   [7b3c4a2f] Email: Thread discussing performance issues and...
   ```

#### Pattern Output
```python
# Example AI-detected patterns
LegalPatternAnalysis(
    contradictions=[
        Contradiction(
            statement_1="Meeting scheduled for January 15",
            statement_1_source="sha256=2401112d...",
            statement_2="No meeting occurred in January",
            statement_2_source="sha256=7b3c4a2f...",
            contradiction_type="factual",
            severity=0.8,
            explanation="Evidence conflicts on whether meeting took place"
        )
    ],
    corroboration=[
        CorroborationLink(
            claim="Performance issues discussed in December 2023",
            supporting_evidence=["sha256=2401112d...", "sha256=7b3c4a2f..."],
            corroboration_strength="strong",
            explanation="Multiple independent sources confirm performance discussions"
        )
    ],
    evidence_gaps=[
        "No evidence of HR involvement despite policy requirement",
        "Missing email correspondence between December 15 and January 10"
    ],
    pattern_summary="Evidence shows conflicting accounts of meeting occurrence with strong corroboration of performance issues. Notable gap in communications during key period.",
    confidence=0.85
)
```

## Validation & Compliance

### Forensic Integrity

The Correlation Analyzer maintains forensic-grade standards:

1. **Deterministic Processing**: Canonicalization algorithm is deterministic (same input → same output)
2. **No Data Modification**: Analyzer only reads from storage, never modifies evidence
3. **Pydantic Validation**: All outputs validated with Pydantic models for schema compliance
4. **Confidence Scoring**: All entity extractions include confidence scores
5. **Chain of Custody**: Analysis results timestamped and tracked

### Model Validation

All correlation outputs use Pydantic models from `core/models.py`:

```python
# Example: CorrelationAnalysis validation
class CorrelationAnalysis(BaseModel):
    case_id: str = Field(..., description="Case identifier")
    evidence_count: int = Field(..., ge=0, description="Evidence pieces analyzed")
    entity_correlations: List[CorrelatedEntity] = Field(default_factory=list)
    timeline_events: List[TimelineEvent] = Field(default_factory=list)
    temporal_sequences: List[Dict] = Field(default_factory=list)
    timeline_gaps: List[Dict] = Field(default_factory=list)
    legal_patterns: Optional[LegalPatternAnalysis] = Field(default=None)
    analysis_timestamp: datetime = Field(...)

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            float: lambda v: round(v, 4)  # Consistent precision
        }
```

**Validation Guarantees**:
- `evidence_count ≥ 0` (non-negative integer)
- `entity_correlations` contains only CorrelatedEntity instances (with `occurrence_count ≥ 2`)
- `timeline_events` sorted chronologically (enforced by caller)
- `legal_patterns` validated against LegalPatternAnalysis schema (if present)
- All datetime fields ISO-formatted for JSON serialization

### v3.0 Conversion: Dataclass → Pydantic

**Before (v2.0)**:
```python
@dataclass
class CorrelationResult:
    case_id: str
    entity_correlations: List[Dict]  # No validation
    timeline_events: List[Dict]      # No validation
```

**After (v3.0)**:
```python
class CorrelationAnalysis(BaseModel):  # Pydantic!
    case_id: str = Field(..., description="Case identifier")
    entity_correlations: List[CorrelatedEntity] = Field(default_factory=list)
    timeline_events: List[TimelineEvent] = Field(default_factory=list)
    # ... all fields validated at runtime
```

**Benefits**:
- Runtime validation catches errors early
- Schema documentation built-in
- JSON serialization handles datetime, float precision
- Type safety for legal compliance

## Error Handling

### Common Errors

#### 1. No Evidence for Case
```python
result = analyzer.analyze_case_correlations("NONEXISTENT-CASE")
# Returns: CorrelationAnalysis with evidence_count=0, empty lists
```

**Handling**: Analyzer returns empty but valid CorrelationAnalysis (no exception)

#### 2. Malformed Analysis Files
```python
# If analysis.v1.json is corrupted or missing
# Analyzer silently skips that evidence piece and continues
```

**Handling**: Try/except around JSON parsing with `continue` on error

#### 3. OpenAI API Failure (v3.1)
```python
# If OpenAI API call fails during pattern detection
# Analyzer returns None for legal_patterns field
result.legal_patterns  # None (pattern detection failed)
```

**Handling**: Graceful degradation - correlation still works without AI patterns

#### 4. Invalid Dates
```python
# If email date header is malformed or EXIF timestamp is corrupt
# Analyzer silently skips that temporal event and continues
```

**Handling**: Try/except around datetime parsing with `pass` on error

### Recovery Strategies

```python
def analyze_with_retry(analyzer, case_id, max_retries=3):
    """Analyze with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            result = analyzer.analyze_case_correlations(case_id)

            # Validate result quality
            if result.evidence_count == 0:
                raise ValueError(f"No evidence found for case: {case_id}")

            return result

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Performance Considerations

### Time Complexity

**analyze_case_correlations()**:
- Evidence loading: O(E) where E = number of evidence pieces
- Entity extraction: O(E × N) where N = avg entities per evidence
- Canonicalization: O(E × N × C) where C = avg length of entity name (small constant)
- Correlation finding: O(U × M) where U = unique canonical names, M = avg occurrences per name
- Timeline extraction: O(E × T) where T = avg timeline events per evidence
- Pattern detection: O(1) OpenAI API call (context size limited)

**Overall**: O(E × N × M) ≈ O(E²) in worst case (all entities correlated)

**Practical Performance**:
- 10 evidence pieces, 20 entities each → ~200 entity occurrences → <1 second
- 100 evidence pieces, 30 entities each → ~3,000 entity occurrences → ~5 seconds
- 1,000 evidence pieces → impractical (correlation analysis best suited for < 100 pieces)

### Space Complexity

**Memory Usage**:
- Entity index: O(U × M) where U = unique names, M = avg occurrences
- Timeline events: O(E × T) where E = evidence count, T = events per evidence
- Correlation results: O(C) where C = correlated entities (typically << total entities)

**Practical Memory**:
- 100 evidence pieces → ~10MB entity index
- 1,000 evidence pieces → ~100MB entity index
- Pattern detection context → ~50KB (limited to top 20 entities, 30 timeline events)

### Optimizations

1. **Variant-Based Indexing**: Entities indexed by all variants (base, short, initials) for fast matching
2. **Deduplication**: Per-evidence deduplication prevents double-counting variant matches
3. **Lazy AI Pattern Detection**: Only runs if OpenAI client provided (opt-in)
4. **Context Limiting**: AI pattern detection limited to top 20 entities, 30 timeline events (cost control)
5. **Early Filtering**: Timeline pattern detection excludes ingestion artifacts early

## Testing

### Unit Tests

```python
def test_canonicalize_entity_name():
    """Test entity name canonicalization variants."""
    assert canonicalize_entity_name("John Q. Smith") == ("john q smith", "john smith", "j q s")
    assert canonicalize_entity_name("Smith, John") == ("john smith", "john smith", "j s")
    assert canonicalize_entity_name("Chief Executive Officer") == ("ceo", "ceo", "c")

def test_empty_case():
    """Test analyzer behavior with no evidence."""
    storage = EvidenceStorage("data/storage")
    analyzer = CorrelationAnalyzer(storage)
    result = analyzer.analyze_case_correlations("NONEXISTENT")

    assert result.evidence_count == 0
    assert len(result.entity_correlations) == 0
    assert len(result.timeline_events) == 0
```

### Integration Tests

```python
def test_full_correlation_pipeline(tmpdir):
    """Test complete correlation analysis pipeline."""
    # Setup test case with multiple evidence pieces
    storage = EvidenceStorage(tmpdir / "storage")

    # Ingest and analyze evidence
    # ... (setup code)

    # Run correlation analysis
    analyzer = CorrelationAnalyzer(storage)
    result = analyzer.analyze_case_correlations("TEST-CASE")

    # Validate results
    assert result.evidence_count > 0
    assert len(result.entity_correlations) > 0
    assert len(result.timeline_events) > 0

    # Validate Pydantic model
    assert isinstance(result, CorrelationAnalysis)
    result_json = result.model_dump_json()  # Should not raise
```

### AI Pattern Detection Tests

```python
def test_ai_pattern_detection(openai_client):
    """Test AI-powered pattern detection."""
    storage = EvidenceStorage("data/storage")
    analyzer = CorrelationAnalyzer(storage, openai_client=openai_client)

    result = analyzer.analyze_case_correlations("TEST-CASE")

    # Should have legal patterns if OpenAI client provided
    assert result.legal_patterns is not None
    assert isinstance(result.legal_patterns, LegalPatternAnalysis)
    assert result.legal_patterns.confidence >= 0.0
    assert result.legal_patterns.confidence <= 1.0
```

## Dependencies

### Internal Dependencies

1. **EvidenceStorage** (`core/storage.py`):
   - Used for: Loading analyzed evidence from `derived/sha256=<hash>/`
   - Methods: `derived_dir` property for accessing analysis files

2. **Pydantic Models** (`core/models.py`):
   - `CorrelationAnalysis`: Output model
   - `CorrelatedEntity`: Entity correlation result
   - `TimelineEvent`: Timeline event representation
   - `LegalPatternAnalysis`: AI pattern detection result (v3.1)
   - `Contradiction`, `CorroborationLink`: Pattern components (v3.1)

3. **Legal Config** (`domains/legal_config.py`):
   - `CORRELATION_PATTERN_PROMPT`: AI pattern detection prompt
   - `CRITICAL_RISK_FLAGS`: Temporal pattern detection triggers

### External Dependencies

1. **OpenAI Python SDK** (optional, for v3.1 pattern detection):
   ```python
   from openai import OpenAI
   ```

2. **Python Standard Library**:
   - `json`: Loading analysis files
   - `datetime`: Timeline event handling
   - `email.utils.parsedate_to_datetime`: Email date parsing
   - `re`: Entity name parsing
   - `unicodedata`: Name normalization
   - `collections.defaultdict`: Entity indexing

3. **dateutil.parser** (optional, for document date parsing):
   ```python
   from dateutil import parser as date_parser
   ```

## Related Components

### Pipeline Stages

1. **Ingestion** (`pipeline/ingest.py`):
   - Stores evidence in content-addressed format
   - Provides SHA256 hashes for correlation

2. **Analysis** (`pipeline/analyze.py`):
   - Runs DocumentAnalyzer, EmailAnalyzer, ImageAnalyzer
   - Generates entity data consumed by correlation

3. **Correlation** (THIS MODULE):
   - Correlates entities across evidence
   - Builds timeline and detects patterns

4. **Packaging** (`pipeline/package.py`):
   - Generates client packages with correlation reports
   - Includes correlation_analysis.json

### Analyzers

1. **DocumentAnalyzer** (`analyzers/document.py`):
   - Extracts DocumentEntity objects (people, orgs, dates, legal terms)
   - Provides: entity name, type, confidence, context, relationship, quoted_text

2. **EmailAnalyzer** (`analyzers/email.py`):
   - Extracts EmailParticipant objects (email addresses, display names, roles)
   - Provides: email_address, display_name, authority_level, deference_score

3. **ImageAnalyzer** (`analyzers/image.py`):
   - Extracts OCR text entities from detected_text
   - Provides: capitalized words (likely proper nouns)

### Storage

**Evidence Files**:
```
data/storage/
├── derived/sha256=<hash>/
│   ├── analysis.v1.json      # Read by correlation analyzer
│   ├── metadata.json          # File metadata for timeline
│   ├── exif.json              # EXIF data for image timestamps
│   └── chain_of_custody.json # Forensic audit trail
└── cases/<case-id>/
    └── <sha256>.ext           # Case-linked evidence
```

**Correlation Output**:
```
data/packages/<case-id>_analysis_package_<timestamp>/
├── correlations/
│   └── correlation_analysis.json  # Full CorrelationAnalysis output
└── reports/
    └── executive_summary.txt      # Includes correlation insights
```

## Examples

### Example 1: Basic Correlation Analysis

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

# Initialize
storage = EvidenceStorage("data/storage")
analyzer = CorrelationAnalyzer(storage, verbose=True)

# Analyze case
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Print summary
print(f"\nCorrelation Analysis Summary")
print(f"{'=' * 50}")
print(f"Evidence pieces analyzed: {result.evidence_count}")
print(f"Entities in 2+ pieces: {len(result.entity_correlations)}")
print(f"Timeline events: {len(result.timeline_events)}")
print(f"Temporal sequences detected: {len(result.temporal_sequences)}")
print(f"Timeline gaps detected: {len(result.timeline_gaps)}")

# Top 5 correlated entities
print(f"\nTop Correlated Entities:")
for i, entity in enumerate(result.entity_correlations[:5], 1):
    print(f"{i}. {entity.entity_name} ({entity.entity_type})")
    print(f"   Appears in: {entity.occurrence_count} evidence pieces")
    print(f"   Confidence: {entity.confidence_average:.2f}")
    print(f"   Occurrences:")
    for occ in entity.evidence_occurrences[:3]:  # First 3 occurrences
        print(f"     - {occ['evidence_sha256'][:8]}: {occ['context'][:60]}...")
```

### Example 2: Timeline Reconstruction

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

# Initialize
storage = EvidenceStorage("data/storage")
analyzer = CorrelationAnalyzer(storage)

# Analyze case
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Print timeline
print(f"\nChronological Event Timeline")
print(f"{'=' * 80}")

for event in result.timeline_events:
    print(f"{event.timestamp.strftime('%Y-%m-%d %H:%M')} | {event.event_type:20s} | {event.description[:50]}")

    # Show AI classification if present
    if event.ai_classification:
        ai = event.ai_classification
        if ai.get('communication_pattern'):
            print(f"  → Pattern: {ai['communication_pattern']}")
        if ai.get('risk_flags'):
            print(f"  → Risks: {', '.join(ai['risk_flags'])}")
        if ai.get('legal_significance'):
            print(f"  → Legal significance: {ai['legal_significance']}")
```

### Example 3: Temporal Pattern Analysis

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

# Initialize
storage = EvidenceStorage("data/storage")
analyzer = CorrelationAnalyzer(storage)

# Analyze case
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Analyze temporal sequences (retaliation patterns, escalations)
print(f"\nTemporal Sequences Detected: {len(result.temporal_sequences)}")
print(f"{'=' * 80}")

for seq in result.temporal_sequences:
    print(f"\nSequence: {seq['pattern_type']}")
    print(f"Legal Significance: {seq['legal_significance']}")
    print(f"Time Span: {seq['time_span_days']:.1f} days ({seq['event_count']} events)")
    print(f"Risk Flags: {', '.join(seq['risk_flags'])}")

    print(f"\nAnchor Event:")
    anchor = seq['anchor_event']
    print(f"  {anchor['timestamp']} - {anchor['description'][:70]}")
    if anchor.get('ai_classification'):
        print(f"  Pattern: {anchor['ai_classification'].get('communication_pattern')}")

    print(f"\nRelated Events:")
    for event in seq['related_events'][:5]:  # First 5 related events
        print(f"  {event['timestamp']} - {event['description'][:70]}")

# Analyze timeline gaps (potential evidence spoliation)
print(f"\n\nTimeline Gaps Detected: {len(result.timeline_gaps)}")
print(f"{'=' * 80}")

for gap in result.timeline_gaps:
    print(f"\nGap: {gap['gap_duration_days']:.1f} days ({gap['significance']} significance)")
    print(f"Gap Period: {gap['gap_start']} → {gap['gap_end']}")
    print(f"Before: {gap['before_event']['description'][:60]}")
    print(f"After: {gap['after_event']['description'][:60]}")
```

### Example 4: v3.1 Legal Pattern Detection

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer
from openai import OpenAI
import os

# Initialize with OpenAI client for AI pattern detection
storage = EvidenceStorage("data/storage")
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=True)

# Analyze case (includes AI pattern detection)
result = analyzer.analyze_case_correlations("CASE-2024-001")

# Check if AI patterns were detected
if result.legal_patterns:
    patterns = result.legal_patterns

    print(f"\n{'=' * 80}")
    print(f"AI-Detected Legal Patterns (Confidence: {patterns.confidence:.2f})")
    print(f"{'=' * 80}")

    # Contradictions
    if patterns.contradictions:
        print(f"\nContradictions Detected: {len(patterns.contradictions)}")
        for i, contradiction in enumerate(patterns.contradictions, 1):
            print(f"\n{i}. {contradiction.contradiction_type.upper()} Contradiction (Severity: {contradiction.severity:.2f})")
            print(f"   Statement 1: {contradiction.statement_1}")
            print(f"   Source: {contradiction.statement_1_source[:8]}")
            print(f"   Statement 2: {contradiction.statement_2}")
            print(f"   Source: {contradiction.statement_2_source[:8]}")
            print(f"   Explanation: {contradiction.explanation}")

    # Corroboration
    if patterns.corroboration:
        print(f"\n\nCorroboration Links: {len(patterns.corroboration)}")
        for i, corr in enumerate(patterns.corroboration, 1):
            print(f"\n{i}. {corr.corroboration_strength.upper()} Corroboration")
            print(f"   Claim: {corr.claim}")
            print(f"   Supporting Evidence: {len(corr.supporting_evidence)} pieces")
            for sha in corr.supporting_evidence:
                print(f"     - {sha[:8]}")
            print(f"   Explanation: {corr.explanation}")

    # Evidence gaps
    if patterns.evidence_gaps:
        print(f"\n\nEvidence Gaps Identified: {len(patterns.evidence_gaps)}")
        for i, gap in enumerate(patterns.evidence_gaps, 1):
            print(f"{i}. {gap}")

    # Pattern summary
    print(f"\n\nPattern Summary:")
    print(f"{patterns.pattern_summary}")
else:
    print("⚠️  AI pattern detection not available (OpenAI client not provided)")
```

### Example 5: Entity Canonicalization Testing

```python
from evidence_toolkit.analyzers.correlation import canonicalize_entity_name

# Test various name formats
test_names = [
    "Paul Boucherat",
    "Boucherat, Paul",
    "Paul J. Boucherat",
    "P. Boucherat",
    "PAUL BOUCHERAT",
    "paul boucherat",
    "Rachel Hemmings",
    "Hemmings, Rachel",
    "R. Hemmings",
    "Chief Executive Officer",
    "CEO",
    "Human Resources Manager",
    "HR Manager",
]

print("Entity Name Canonicalization Test")
print(f"{'=' * 100}")
print(f"{'Original Name':<30s} | {'Base Form':<25s} | {'Short Form':<20s} | {'Initials':<10s}")
print(f"{'-' * 100}")

for name in test_names:
    base, short, initials = canonicalize_entity_name(name)
    print(f"{name:<30s} | {base:<25s} | {short:<20s} | {initials:<10s}")

# Demonstrate matching logic
print(f"\n{'=' * 100}")
print("Matching Demonstration:")
print("These variants will be matched as the same entity:")

variants = [
    "Paul Boucherat",
    "Boucherat, Paul",
    "Paul J. Boucherat"
]

canonical_forms = {}
for variant in variants:
    base, short, initials = canonicalize_entity_name(variant)
    canonical_forms[variant] = {'base': base, 'short': short, 'initials': initials}

print(f"\n{'Variant':<30s} | Canonical Forms")
print(f"{'-' * 100}")
for variant, forms in canonical_forms.items():
    print(f"{variant:<30s} | base={forms['base']}, short={forms['short']}, initials={forms['initials']}")

# Show shared bucket
print(f"\nShared 'short' bucket: All three variants map to '{canonical_forms[variants[0]]['short']}'")
print(f"→ Correlation analyzer will find all three as the same person")
```

---

This documentation provides comprehensive coverage of the Correlation Analyzer module, from basic usage to advanced AI pattern detection. It follows the Evidence Toolkit standards for clarity, completeness, and maintainability, with a strong focus on forensic-quality legal evidence analysis and the deterministic entity matching algorithm that enables robust cross-evidence correlation.
