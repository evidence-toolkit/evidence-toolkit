# Evidence Analysis Pipeline

## Overview

The analysis pipeline orchestrates AI-powered forensic analysis of evidence based on type-specific analyzers. It detects evidence types, routes to appropriate analyzers (documents, images, emails), generates categorization labels, and produces unified analysis results with complete chain of custody tracking. The pipeline uses OpenAI's deterministic models (temperature=0) for reproducible, forensic-grade analysis suitable for legal proceedings.

This module serves as the central analysis orchestrator, delegating type-specific analysis to specialized analyzers while maintaining consistent result formats.

## Purpose & Scope

### What Analysis Does
- Detects evidence type (document, image, email) automatically or by user override
- Routes evidence to type-specific AI analyzers
- Generates categorical labels for evidence organization
- Produces unified analysis results (`UnifiedAnalysis`)
- Persists analysis with chain of custody tracking
- Supports force re-analysis with automatic backup

### What Analysis Does NOT Do
- Evidence ingestion (handled by ingestion pipeline)
- Cross-evidence correlation (handled by summary pipeline)
- Client package generation (handled by packaging pipeline)
- Evidence modification (read-only analysis)

### Design Principles
1. **Type Polymorphism**: Single interface for all evidence types
2. **AI-Powered**: Leverages OpenAI for deep analysis
3. **Deterministic**: Temperature=0 for reproducible results
4. **Forensic Grade**: Complete audit trails and versioning
5. **Graceful Degradation**: Works without OpenAI (limited analysis)

## Module Structure

```
evidence_toolkit/pipeline/analyze.py
│
├── analyze_evidence()       # Main orchestration function
│   ├─→ Type detection
│   ├─→ Analysis routing
│   └─→ Result persistence
│
├── _analyze_document()      # Document analysis
├── _analyze_image()         # Image/PDF vision analysis
├── _analyze_email()         # Email thread analysis
└── _generate_labels()       # Label generation for categorization
```

### Integration Points
```
src/evidence_toolkit/
├── pipeline/
│   └── analyze.py           # This module
│
├── analyzers/
│   ├── document.py          # DocumentAnalyzer
│   ├── image.py             # ImageAnalyzer
│   ├── email.py             # EmailAnalyzer
│   └── email_parser.py      # EmailParser
│
├── core/
│   ├── models.py            # UnifiedAnalysis, DocumentAnalysisResult, etc.
│   ├── storage.py           # EvidenceStorage
│   └── utils.py             # detect_file_type(), extract_exif_data()
│
└── domains/
    └── legal_config.py      # AI prompts
```

## API Reference

### `analyze_evidence()`

Main analysis orchestration function. Detects evidence type, routes to appropriate analyzer, constructs unified analysis, and saves results.

**Signature:**
```python
def analyze_evidence(
    sha256: str,
    storage: EvidenceStorage,
    openai_client: Optional[Any] = None,
    case_id: Optional[str] = None,
    evidence_type: Optional[str] = None,
    force: bool = False,
    quiet: bool = False
) -> UnifiedAnalysis
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `sha256` | `str` | Yes | - | SHA256 hash of evidence to analyze |
| `storage` | `EvidenceStorage` | Yes | - | EvidenceStorage instance |
| `openai_client` | `Optional[Any]` | No | `None` | OpenAI client for AI analysis (if None, limited analysis) |
| `case_id` | `Optional[str]` | No | `None` | Case ID to associate with analysis |
| `evidence_type` | `Optional[str]` | No | `None` | Force evidence type ('document', 'image', 'email', 'auto') |
| `force` | `bool` | No | `False` | Re-analyze even if analysis exists (backs up old analysis) |
| `quiet` | `bool` | No | `False` | Suppress verbose output |

**Returns:**

| Type | Description |
|------|-------------|
| `UnifiedAnalysis` | Pydantic model with complete analysis results for the evidence type |

**Exceptions:**

| Exception | When Raised |
|-----------|-------------|
| `FileNotFoundError` | If evidence not found for SHA256 |
| `ValueError` | If evidence type cannot be determined or is unsupported |
| `RuntimeError` | If analysis fails to save |

**Example:**
```python
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

analysis = analyze_evidence(
    sha256="2401112d2c3bcc883a713fc238830307c1d596f74b28110d3137675529191c8c",
    storage=storage,
    openai_client=openai_client,
    case_id="CASE-001",
    force=False,
    quiet=False
)

print(f"Evidence type: {analysis.evidence_type}")
print(f"Legal significance: {analysis.document_analysis.legal_significance}")
print(f"Labels: {analysis.labels}")
```

---

### `_analyze_document()`

Analyze document using DocumentAnalyzer (word frequency + AI analysis).

**Signature:**
```python
def _analyze_document(
    file_path: Path,
    quiet: bool = False
) -> DocumentAnalysisResult
```

**Internal function** - Called by `analyze_evidence()` when type is DOCUMENT.

**Process:**
1. Initialize `DocumentAnalyzer` with settings
2. Run `analyze_directory()` on file
3. Extract word frequency statistics
4. Extract AI analysis fields (if available)
5. Return `DocumentAnalysisResult`

**AI Fields (if OpenAI available):**
- `ai_summary` - Document summary
- `entities` - Extracted persons, organizations, locations
- `document_type` - Classification (contract, letter, email, filing)
- `sentiment` - Overall sentiment
- `legal_significance` - Critical/high/medium/low
- `risk_flags` - Risk indicators

---

### `_analyze_image()`

Analyze image or scanned PDF using ImageAnalyzer with OpenAI Vision API.

**Signature:**
```python
def _analyze_image(
    file_path: Path,
    openai_client: Optional[Any],
    quiet: bool = False
) -> ImageAnalysisResult
```

**Internal function** - Called by `analyze_evidence()` when type is IMAGE.

**Process:**
1. Check if file is PDF (scanned PDF) or regular image
2. Route to appropriate analyzer method:
   - PDF → `ImageAnalyzer.analyze_pdf()`
   - Image → `ImageAnalyzer.analyze_image()`
3. Return `ImageAnalysisResult`

**Analysis Fields:**
- `scene_description` - What the image shows
- `detected_text` - OCR results
- `detected_objects` - Object detection
- `analysis_confidence` - Confidence score

---

### `_analyze_email()`

Analyze email using EmailAnalyzer and extract metadata.

**Signature:**
```python
def _analyze_email(
    file_path: Path,
    openai_client: Optional[Any],
    case_id: Optional[str],
    quiet: bool = False
) -> Tuple[EmailThreadAnalysis, Optional[dict]]
```

**Internal function** - Called by `analyze_evidence()` when type is EMAIL.

**Process:**
1. Parse email file with `EmailParser` to extract headers
2. Initialize `EmailAnalyzer` with OpenAI client
3. Analyze email with `EmailAnalyzer.analyze_email_files()`
4. Return `(EmailThreadAnalysis, email_metadata)`

**Returns:**
- `EmailThreadAnalysis` - Full email analysis with participants (v3.1)
- `email_metadata` - Extracted headers (from, to, subject, date, message_id)

**Analysis Fields (v3.1):**
- `participants` - Email participants with roles, email addresses, and metadata
  - Each participant includes: `name`, `email`, `role` (sender/recipient/cc/bcc), `interaction_count`, `first_interaction`, `last_interaction`
- `thread_summary` - Thread summary
- `communication_pattern` - Pattern classification (escalation, negotiation, routine, etc.)
- `escalation_detected` - Whether escalation is present
- `legal_significance` - Critical/high/medium/low
- `risk_flags` - Risk indicators (harassment, retaliation, time_sensitive, etc.)
- `confidence_overall` - Overall analysis confidence (0.0-1.0)

**v3.1 Enhancement:**
The full `EmailThreadAnalysis` model is now preserved throughout the pipeline, including detailed participant metadata. This enables correlation analysis to match participants across evidence and track communication patterns over time.

---

### `_generate_labels()`

Generate categorical labels for evidence based on analysis results.

**Signature:**
```python
def _generate_labels(
    evidence_type: EvidenceType,
    analysis_result: Union[DocumentAnalysisResult, ImageAnalysisResult, EmailThreadAnalysis],
    email_metadata: Optional[dict] = None
) -> List[str]
```

**Internal function** - Called by `analyze_evidence()` to generate labels for hierarchical evidence organization.

**Purpose:**
Labels enable browsable, categorical organization of evidence by:
- Evidence type (document, image, email)
- Legal significance (critical, high, medium, low)
- Risk flags (retaliation, harassment, time_sensitive, etc.)
- Document/communication classification

**Label Categories:**

**For Documents:**
- Evidence type: `"document"`
- Legal significance: `"{significance}-significance"` (e.g., `"high-significance"`)
- Risk flags: `["retaliation", "harassment", ...]`
- Document type: `"doctype-{type}"` (e.g., `"doctype-contract"`)

**For Emails (v3.1):**
- Evidence type: `"email"`
- Legal significance: `"{significance}-significance"`
- Risk flags: `["time_sensitive", "escalation", "harassment", ...]`
- Communication pattern: `"pattern-{pattern}"` (e.g., `"pattern-escalation"`, `"pattern-negotiation"`)

**For Images:**
- Evidence type: `"image"`
- Visual evidence marker: `"visual-evidence"`

**Example Output:**
```python
# Document labels
["document", "high-significance", "retaliation", "harassment", "doctype-email"]

# Email labels (v3.1 with communication patterns)
["email", "critical-significance", "escalation", "time_sensitive", "pattern-escalation"]

# Image labels
["image", "visual-evidence"]
```

**v3.1 Integration:**
Labels are generated from the full `EmailThreadAnalysis` model, which includes AI-powered classification of communication patterns and risk factors. These labels enable filtering and organization in the package generation stage.

## Data Models

### `UnifiedAnalysis` (from `core/models.py`)

Unified analysis result for any evidence type.

```python
class UnifiedAnalysis(BaseModel):
    evidence_type: EvidenceType
    analysis_timestamp: datetime
    file_metadata: FileMetadata
    case_id: Optional[str] = None

    # Type-specific analysis (only one populated)
    document_analysis: Optional[DocumentAnalysisResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None
    email_analysis: Optional[EmailThreadAnalysis] = None

    # Optional metadata
    exif_data: Optional[Dict[str, Any]] = None
    email_metadata: Optional[Dict[str, Any]] = None

    # Categorization
    labels: List[str] = Field(default_factory=list)

    # Multi-case support (v3.1)
    case_ids: List[str] = Field(default_factory=list)
```

### Type-Specific Analysis Models

| Model | Used For | Key Fields (v3.1) |
|-------|----------|-------------------|
| `DocumentAnalysisResult` | Documents (.txt, .pdf) | total_words, ai_summary, entities, legal_significance, risk_flags |
| `ImageAnalysisResult` | Images (.jpg, .png, scanned PDFs) | scene_description, detected_text, detected_objects, analysis_confidence |
| `EmailThreadAnalysis` | Emails (.eml, .msg) | **participants** (with full metadata), thread_summary, communication_pattern, escalation_detected, legal_significance, risk_flags |

## Behavior

### Analysis Flow

```
analyze_evidence(sha256, ...)
  ↓
1. Check if evidence exists
   ├─→ Not found: FileNotFoundError
   └─→ Found: Continue
  ↓
2. Check if already analyzed
   ├─→ Exists & force=False: Return existing
   ├─→ Exists & force=True: Backup old, continue
   └─→ Not exists: Continue
  ↓
3. Detect or use provided evidence type
   ├─→ Auto-detect: detect_file_type(file)
   └─→ Provided: Use evidence_type param
  ↓
4. Load file metadata
  ↓
5. Route to type-specific analyzer
   ├─→ DOCUMENT: _analyze_document()
   ├─→ IMAGE: _analyze_image()
   ├─→ EMAIL: _analyze_email()
   └─→ Unknown: ValueError
  ↓
6. Generate labels
   └─→ _generate_labels()
  ↓
7. Construct UnifiedAnalysis
   ├─→ Set evidence_type
   ├─→ Set type-specific analysis
   ├─→ Set labels
   └─→ Set metadata
  ↓
8. Save analysis
   └─→ storage.save_analysis()
  ↓
9. Update chain of custody
  ↓
Return UnifiedAnalysis
```

### Type Detection Logic

```python
# Auto-detect evidence type
if evidence_type == 'auto' or evidence_type is None:
    detected_type = detect_file_type(original_file)
    # detect_file_type() checks:
    # 1. File extension (.txt, .pdf, .jpg, .eml, etc.)
    # 2. MIME type
    # 3. File content (for PDFs: text-based vs. scanned)
    evidence_type_enum = EvidenceType(detected_type)
else:
    # Use provided type
    evidence_type_enum = EvidenceType(evidence_type)
```

**Routing Table:**

| File Type | Extension | Detection Method | Analyzer |
|-----------|-----------|------------------|----------|
| Text document | `.txt` | Extension | DocumentAnalyzer |
| PDF (text-based) | `.pdf` | Content analysis | DocumentAnalyzer |
| PDF (scanned) | `.pdf` | Content analysis (no text) | ImageAnalyzer |
| Image | `.jpg`, `.png`, `.jpeg`, `.gif` | Extension | ImageAnalyzer |
| Email | `.eml`, `.msg` | Extension | EmailAnalyzer |

### Force Re-analysis

When `force=True`, the pipeline:
1. Checks for existing analysis
2. Creates timestamped backup: `analysis.v1.json.backup.<timestamp>`
3. Proceeds with new analysis
4. Overwrites `analysis.v1.json`

**Example:**
```bash
# First analysis
uv run evidence-toolkit analyze <sha256> --case-id CASE-001
# Creates: derived/sha256=.../analysis.v1.json

# Re-analysis with force
uv run evidence-toolkit analyze <sha256> --case-id CASE-001 --force
# Creates: derived/sha256=.../analysis.v1.json.backup.1728149400
# Updates: derived/sha256=.../analysis.v1.json
```

### Chain of Custody Events

Every analysis adds a chain of custody event:

```json
{
  "timestamp": "2025-10-05T14:45:00.123456Z",
  "action": "analysis",
  "actor": "system",
  "details": "AI-powered document analysis completed",
  "metadata": {
    "evidence_type": "document",
    "case_id": "CASE-001",
    "openai_model": "gpt-4.1-mini",
    "analysis_confidence": 0.92
  }
}
```

## AI Integration

### Models Used

| Evidence Type | Model | API | Purpose |
|---------------|-------|-----|---------|
| Document | `gpt-4.1-mini` | Responses | Extract entities, sentiment, legal significance |
| Image | `gpt-4o` | Vision | Scene description, OCR, object detection |
| Email | `gpt-4.1-mini` | Responses | Thread analysis, escalation detection |

### Prompts

All prompts are in `evidence_toolkit/domains/legal_config.py`:

```python
# Document analysis prompt
DOCUMENT_ANALYSIS_PROMPT = """You are a forensic document analyzer..."""

# Image analysis prompt
IMAGE_ANALYSIS_PROMPT = """Analyze this image for forensic evidence..."""

# Email analysis prompt
EMAIL_ANALYSIS_PROMPT = """Analyze this email thread for legal significance..."""
```

### Deterministic Analysis

**All AI analysis uses temperature=0** for reproducible results:

```python
# OpenAI Responses API call (SAME PATTERN across all analyzers)
response = openai_client.responses.parse(
    model="gpt-4.1-mini",
    input=[
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": evidence_content}
    ],
    text_format=DocumentAnalysisResult,  # Pydantic schema
    # temperature=0 (default for Responses API)
)
```

### Response Handling

```python
# Standard response handling pattern
if response.status == "completed" and response.output_parsed:
    return response.output_parsed  # Pydantic-validated result
elif response.status == "incomplete":
    raise Exception(f"Analysis incomplete: {response.incomplete_details}")
else:
    # Check for refusal
    if (response.output and len(response.output) > 0 and
        len(response.output[0].content) > 0 and
        response.output[0].content[0].type == "refusal"):
        raise Exception(f"Analysis refused: {response.output[0].content[0].refusal}")
    raise Exception("Analysis failed with unknown error")
```

## Validation & Compliance

### Input Validation
- SHA256 format validation (64 hex characters)
- Evidence existence check (file must be ingested)
- Type validation (document/image/email/auto)
- Case ID validation (if provided)

### Output Validation
All analysis results are Pydantic-validated:

```python
# UnifiedAnalysis validates all fields
unified_analysis = UnifiedAnalysis(
    evidence_type=evidence_type_enum,  # Enum validation
    analysis_timestamp=datetime.now(),  # Datetime validation
    file_metadata=file_metadata,        # Nested Pydantic validation
    document_analysis=analysis_result,  # Type-specific validation
    labels=labels                        # List[str] validation
)
```

### Chain of Custody
Analysis operations are tracked in chain of custody:

```
data/storage/derived/sha256=<hash>/chain_of_custody.json
```

Each analysis adds an event with metadata for complete audit trail.

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `FileNotFoundError` | Evidence not ingested | Run ingestion first |
| `ValueError` | Invalid evidence type | Check type detection, use --evidence-type |
| `RuntimeError` | Analysis save failed | Check permissions, disk space |
| `OpenAI APIError` | AI analysis failed | Check API key, rate limits, retry |
| `JSONDecodeError` | Corrupted metadata | Re-ingest evidence |

### Error Handling Pattern

```python
try:
    analysis = analyze_evidence(sha256, storage, openai_client)
    print(f"✅ Analysis completed: {analysis.evidence_type}")
except FileNotFoundError:
    print(f"❌ Evidence not found. Ingest first: uv run evidence-toolkit ingest ...")
except ValueError as e:
    print(f"❌ Type detection failed: {e}. Try --evidence-type document|image|email")
except RuntimeError as e:
    print(f"❌ Analysis failed: {e}")
```

### Logging

Analysis operations use emoji-prefixed output:
- `🔍` - Analysis operations
- `✅` - Success
- `⚠️` - Warning (already analyzed, using existing)
- `🔄` - Re-analysis with force flag
- `❌` - Error

## Performance Considerations

### Time Complexity
- **Type detection**: O(1) for extension-based, O(n) for content-based (PDF)
- **Document analysis**: O(n) where n = document length (word frequency) + O(1) API call
- **Image analysis**: O(1) API call (model processes image)
- **Email analysis**: O(m) where m = number of messages + O(1) API call

### Space Complexity
- **Analysis results**: ~10-50 KB JSON per evidence
- **Backup files**: ~10-50 KB per re-analysis
- **Memory**: Minimal (streaming file read, API handles processing)

### API Cost Impact

| Evidence Type | Model | Tokens (avg) | Cost (per 1M tokens) | Avg Cost |
|---------------|-------|--------------|----------------------|----------|
| Document | gpt-4.1-mini | ~2,000 input + 500 output | $0.15 / $0.60 | ~$0.0006 |
| Image | gpt-4o (Vision) | ~1,000 input + 300 output | $2.50 / $10.00 | ~$0.006 |
| Email | gpt-4.1-mini | ~1,500 input + 400 output | $0.15 / $0.60 | ~$0.0005 |

**Example:** Analyzing 100 mixed evidence pieces costs approximately $0.05-0.10.

### Optimization Notes
- Analysis results are cached (re-analysis only with `--force`)
- Type detection uses fast extension check before content analysis
- API calls use structured output (reduces token usage)
- Backup creation is lazy (only when `force=True`)

## Storage & Persistence

### File Locations

```
data/storage/derived/sha256=<hash>/
├── metadata.json              # File metadata (from ingestion)
├── analysis.v1.json           # Current analysis (UnifiedAnalysis)
├── analysis.v1.json.backup.*  # Backups (from force re-analysis)
├── chain_of_custody.json      # Chain of custody events
└── [visualizations/]          # Optional (word clouds, etc.)
```

### Analysis File Format

**`analysis.v1.json`** (UnifiedAnalysis):
```json
{
  "evidence_type": "document",
  "analysis_timestamp": "2025-10-05T14:45:00.123456Z",
  "case_id": "CASE-001",
  "case_ids": ["CASE-001"],
  "file_metadata": { ... },
  "document_analysis": {
    "total_words": 1500,
    "unique_words": 450,
    "ai_summary": "Employment termination letter...",
    "entities": [
      {"name": "John Doe", "type": "person", "confidence": 0.95},
      {"name": "Acme Corp", "type": "organization", "confidence": 0.98}
    ],
    "document_type": "letter",
    "sentiment": "negative",
    "legal_significance": "high",
    "risk_flags": ["retaliation", "termination"],
    "analysis_confidence": 0.92
  },
  "labels": [
    "document",
    "high-significance",
    "retaliation",
    "termination",
    "doctype-letter"
  ]
}
```

## Testing

### Unit Tests

```python
import tempfile
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.models import EvidenceType

def test_analyze_document():
    """Test document analysis."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage(base_dir=Path(tmpdir))

        # Create and ingest test document
        doc = Path(tmpdir) / "test.txt"
        doc.write_text("This is a test document for analysis.")
        result = storage.ingest_file(doc, case_id="TEST")

        # Analyze (without OpenAI for testing)
        analysis = analyze_evidence(
            sha256=result.sha256,
            storage=storage,
            openai_client=None,  # No AI
            case_id="TEST"
        )

        # Verify
        assert analysis.evidence_type == EvidenceType.DOCUMENT
        assert analysis.document_analysis is not None
        assert analysis.document_analysis.total_words > 0
        assert "document" in analysis.labels

def test_force_reanalysis():
    """Test force re-analysis with backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage(base_dir=Path(tmpdir))

        # Ingest
        doc = Path(tmpdir) / "test.txt"
        doc.write_text("Test content")
        result = storage.ingest_file(doc)

        # First analysis
        analysis1 = analyze_evidence(result.sha256, storage)

        # Force re-analysis
        analysis2 = analyze_evidence(result.sha256, storage, force=True)

        # Verify backup was created
        derived_dir = storage.derived_dir / f"sha256={result.sha256}"
        backups = list(derived_dir.glob("analysis.v1.json.backup.*"))
        assert len(backups) == 1
```

### Integration Tests

```bash
# Full pipeline test
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify analysis
uv run evidence-toolkit list --case-id TEST-CASE --detailed
```

### Test Coverage
- Type detection: ✅ Covered
- Document analysis: ✅ Covered
- Image analysis: ✅ Covered
- Email analysis: ✅ Covered
- Label generation: ✅ Covered
- Force re-analysis: ✅ Covered
- AI error handling: ⚠️ Partial (needs mocking)

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.storage.EvidenceStorage` - Storage operations
- `evidence_toolkit.core.models.*` - All analysis models
- `evidence_toolkit.core.utils.detect_file_type` - Type detection
- `evidence_toolkit.core.utils.extract_exif_data` - EXIF extraction
- `evidence_toolkit.analyzers.document.DocumentAnalyzer` - Document analysis
- `evidence_toolkit.analyzers.image.ImageAnalyzer` - Image analysis
- `evidence_toolkit.analyzers.email.EmailAnalyzer` - Email analysis
- `evidence_toolkit.analyzers.email_parser.EmailParser` - Email parsing

### External Dependencies
- `openai` - AI analysis (optional, gracefully degrades)
- `pydantic` - Model validation
- `pathlib` - Path operations

## CLI Integration

```bash
# Analyze by SHA256
uv run evidence-toolkit analyze <sha256> --case-id CASE-001

# Force re-analysis
uv run evidence-toolkit analyze <sha256> --case-id CASE-001 --force

# Override type detection
uv run evidence-toolkit analyze <sha256> --evidence-type document

# Quiet mode
uv run evidence-toolkit analyze <sha256> --quiet
```

**CLI Implementation** (`cli.py`):
```python
@app.command()
def analyze(
    sha256: str,
    case_id: Optional[str] = None,
    evidence_type: Optional[str] = None,
    force: bool = False,
    quiet: bool = False
):
    """Analyze evidence by SHA256."""
    storage = EvidenceStorage()
    openai_client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

    analysis = analyze_evidence(
        sha256=sha256,
        storage=storage,
        openai_client=openai_client,
        case_id=case_id,
        evidence_type=evidence_type,
        force=force,
        quiet=quiet
    )

    if not quiet:
        print(f"✅ Analysis completed: {analysis.evidence_type}")
```

## Migration Notes

### v2.0 → v3.0/v3.1 Changes

**Old (v2.0):**
```python
# Monolithic CLI
from document_analyzer.cli import analyze_command
analyze_command(sha256="...", case_id="...")
```

**New (v3.0/v3.1):**
```python
# Modular pipeline
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
analysis = analyze_evidence(sha256="...", storage=storage, case_id="...")
```

**Breaking Changes:**
- Function signature changed (requires `storage` parameter)
- Return type changed (`UnifiedAnalysis` instead of dict)
- Import path changed (`document_analyzer.cli` → `evidence_toolkit.pipeline`)
- Email analysis now returns full `EmailThreadAnalysis` with participants (v3.1)

**v3.1 Email Enhancements:**
- Email analysis preserves full participant data (name, email, role, interaction timestamps)
- Label generation includes communication patterns from AI analysis
- `EmailThreadAnalysis` model used throughout pipeline (not simplified `EmailAnalysisResult`)

## Future Considerations

### Planned Enhancements
- **Parallel analysis**: Async analysis for multiple evidence pieces
- **Progressive results**: Stream analysis updates in real-time
- **Custom analyzers**: Plugin system for domain-specific analyzers
- **Confidence tuning**: Configurable confidence thresholds
- **Analysis versioning**: Support for multiple analysis versions

### Known Limitations
- Sequential analysis only (no concurrency)
- OpenAI API rate limits apply
- No partial analysis (all-or-nothing)
- Limited error recovery for AI failures

### Technical Debt
- Some duplicate logic in type-specific analyzers
- Hard-coded model names (should be configurable)
- Label generation could be more sophisticated

## Examples

### Example 1: Basic Analysis
```python
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
analysis = analyze_evidence(
    sha256="2401112d2c3bcc883a713fc238830307c1d596f74b28110d3137675529191c8c",
    storage=storage,
    openai_client=OpenAI(),
    case_id="CASE-001"
)

print(f"Type: {analysis.evidence_type}")
print(f"Summary: {analysis.document_analysis.ai_summary}")
print(f"Entities: {len(analysis.document_analysis.entities)}")
```

### Example 2: Batch Analysis
```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import analyze_evidence
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()
case_id = "CASE-001"

# Get all evidence for case
evidence_list = storage.get_case_evidence(case_id)

# Analyze each piece
for sha256 in evidence_list:
    analysis = analyze_evidence(sha256, storage, openai_client, case_id)
    print(f"Analyzed: {sha256[:12]}... ({analysis.evidence_type})")
```

### Example 3: Analysis with Type Override
```python
from evidence_toolkit.pipeline import analyze_evidence
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()

# Force image analysis (even if detected as document)
analysis = analyze_evidence(
    sha256="abc123...",
    storage=storage,
    evidence_type="image",  # Override detection
    case_id="CASE-001"
)

print(f"Scene: {analysis.image_analysis.scene_description}")
```

---

**This documentation provides complete reference for the analysis pipeline, covering all orchestration logic, type-specific analysis, AI integration, and usage patterns in Evidence Toolkit v3.0.**
