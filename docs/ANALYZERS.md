# Documentation: Evidence Toolkit Analyzers

## Overview

The Evidence Toolkit Analyzers module provides AI-powered forensic analysis capabilities for legal evidence processing. This module contains five specialized analyzers that work together to extract legally significant insights from documents, emails, and images using OpenAI's Responses API for deterministic, legally-admissible analysis results.

The analyzers follow a unified architecture pattern established in v3.0, using Pydantic models for validation, OpenAI Responses API (NOT chat completions) for structured outputs, and content-addressed storage for evidence integrity. All analyzers are designed for forensic-grade analysis suitable for legal proceedings, with full chain of custody tracking and schema-compliant outputs.

## Purpose & Scope

**What this module solves:**
- Automated extraction of entities, dates, and legal terms from evidence
- Cross-evidence correlation to identify key participants and timeline patterns
- Forensic-grade email thread analysis with escalation detection
- OCR and scene understanding for image evidence
- Deterministic AI analysis with confidence scoring for legal admissibility

**Responsibilities:**
- AI-powered entity extraction with relationship mapping
- Document classification and sentiment analysis
- Email thread reconstruction and participant analysis
- Image analysis with Vision API (OCR, scene description, object detection)
- Cross-evidence entity correlation and timeline reconstruction
- AI pattern detection (contradictions, corroboration, evidence gaps)

**NOT Responsible For:**
- Evidence ingestion (handled by `pipeline.ingest`)
- Storage management (handled by `core.storage`)
- Client package generation (handled by `pipeline.package`)
- Authentication or access control

## Architecture

### Module Structure

```
src/evidence_toolkit/
├── core/
│   ├── models.py              # Pydantic models (DocumentAnalysis, EmailThreadAnalysis, etc.)
│   ├── storage.py             # EvidenceStorage for content-addressed access
│   └── utils.py               # Shared utilities
├── analyzers/                 # THIS MODULE
│   ├── __init__.py            # Public API exports
│   ├── document.py            # DocumentAnalyzer - text analysis + AI entity extraction
│   ├── email.py               # EmailAnalyzer - forensic email thread analysis
│   ├── email_parser.py        # EmailParser - multi-format email parsing (.eml, .msg, .mbox)
│   ├── image.py               # ImageAnalyzer - Vision API for images + PDFs
│   └── correlation.py         # CorrelationAnalyzer - cross-evidence correlation
├── domains/
│   └── legal_config.py        # AI prompts and legal domain configuration
└── pipeline/
    └── analyze.py             # Analysis orchestration (uses analyzers)
```

### Data Flow

```
Evidence Ingestion (pipeline.ingest)
         ↓
    Storage (content-addressed by SHA256)
         ↓
    Analysis (THIS MODULE)
    ├── DocumentAnalyzer → DocumentAnalysis (Pydantic)
    ├── EmailAnalyzer → EmailThreadAnalysis (Pydantic)
    ├── ImageAnalyzer → ImageAnalysisResult (Pydantic)
    └── CorrelationAnalyzer → CorrelationAnalysis (Pydantic)
         ↓
    Validated Results → data/storage/derived/sha256=<hash>/analysis.v1.json
         ↓
    Client Package Generation (pipeline.package)
```

## Analyzers Overview

| Analyzer | Purpose | Input | Output | AI Model |
|----------|---------|-------|--------|----------|
| **DocumentAnalyzer** | Text analysis, word frequency, AI entity extraction | Text/PDF documents | DocumentAnalysis | gpt-4.1-mini |
| **EmailAnalyzer** | Email thread analysis, escalation detection | Parsed email dictionaries | EmailThreadAnalysis | gpt-4.1-mini |
| **EmailParser** | Multi-format email parsing | .eml, .msg, .mbox files | Standardized email dict | N/A (parsing only) |
| **ImageAnalyzer** | OCR, scene description, object detection | Images, scanned PDFs | ImageAnalysisResult | gpt-4.1-mini (vision) |
| **CorrelationAnalyzer** | Cross-evidence entity correlation | Multiple evidence items | CorrelationAnalysis | gpt-4.1-mini (optional) |

---

# DocumentAnalyzer

## Purpose

Analyzes text documents for legal evidence processing, providing:
- Word frequency analysis and visualizations
- AI-powered entity extraction (people, organizations, dates, legal terms)
- Document classification and sentiment analysis
- Legal significance assessment with risk flagging

## Usage

### Basic Usage

```python
from evidence_toolkit.analyzers import DocumentAnalyzer

# Initialize analyzer
analyzer = DocumentAnalyzer(
    custom_stop_words={'confidential', 'privileged'},
    min_word_length=3,
    verbose=True
)

# Analyze text content
text = "Complaint filed against Paul Rodriguez on January 15, 2024..."
result = analyzer.analyze_text(text, output_dir="analysis_output")

# Access AI analysis
if result.get('ai_analysis'):
    ai = result['ai_analysis']
    print(f"Summary: {ai['summary']}")
    print(f"Document Type: {ai['document_type']}")
    print(f"Legal Significance: {ai['legal_significance']}")

    for entity in ai['entities']:
        print(f"- {entity['name']} ({entity['type']}): {entity['context'][:100]}")
```

### Schema-Compliant Analysis

```python
from evidence_toolkit.analyzers import create_schema_compliant_document_analysis

# Create forensic-grade analysis document
schema_doc = create_schema_compliant_document_analysis(
    text=document_text,
    case_id="CASE-2024-001",
    source_path="/path/to/document.pdf",
    actor="analyst@lawfirm.com",
    output_file="data/storage/derived/sha256=<hash>/analysis.v1.json",
    verbose=True
)

# Output is schema-compliant with chain of custody
print(f"Evidence ID: {schema_doc['evidence']['evidence_id']}")
print(f"SHA256: {schema_doc['evidence']['sha256']}")
print(f"Analysis Confidence: {schema_doc['analyses'][0]['confidence_overall']}")
```

### Directory Analysis

```python
from evidence_toolkit.analyzers import analyze_documents

# Analyze all documents in a directory
result = analyze_documents(
    data_dir="data/cases/MY-CASE",
    output_dir="analysis_output",
    custom_stop_words={'redacted'},
    verbose=True
)

# Generates word clouds, frequency charts, and AI analysis
print(f"Processed {result['files_processed']} files")
print(f"Total words: {result['total_words']}")
print(f"Word cloud: {result['wordcloud_file']}")
```

## AI Integration

### OpenAI Model

- **Model**: `gpt-4.1-mini` (cost-effective, excellent quality)
- **API**: OpenAI Responses API (NOT chat completions)
- **Cost**: ~16x cheaper than gpt-4o
- **Determinism**: temperature=0.0 for reproducible results

### Prompt Configuration

Location: `src/evidence_toolkit/domains/legal_config.py`

```python
DOCUMENT_ANALYSIS_PROMPT = """You are a forensic document analyzer for legal evidence processing.

Analyze the provided document text with the following requirements:

1. **Summary**: Concise summary focusing on legal significance
2. **Entity Extraction**: People, organizations, dates, legal terms with:
   - High confidence scores (0.0-1.0)
   - Context: surrounding text
   - Relationship: connections to other entities
   - Quoted Text: verbatim legally significant statements
   - Associated Event: for dates, what happened
3. **Document Classification**: email, letter, contract, filing
4. **Sentiment Analysis**: hostile, neutral, professional
5. **Legal Significance**: critical, high, medium, low
6. **Risk Flags**: threatening, deadlines, PII, confidential, retaliation, harassment
...
"""
```

### Response Format (Pydantic Model)

```python
class DocumentAnalysis(BaseModel):
    summary: str
    entities: List[DocumentEntity]
    document_type: str  # email, letter, contract, filing, unknown
    sentiment: str      # hostile, neutral, professional
    legal_significance: str  # critical, high, medium, low
    risk_flags: List[str]    # retaliation, harassment, threatening, etc.
    confidence_overall: float  # 0.0-1.0

class DocumentEntity(BaseModel):
    name: str
    type: str           # person, organization, date, legal_term
    confidence: float
    context: str
    relationship: Optional[str] = None    # "sent email to Rachel", "reported to HR"
    quoted_text: Optional[str] = None     # Verbatim legally significant quote
    associated_event: Optional[str] = None  # For dates: "meeting with HR"
```

## API Reference

### DocumentAnalyzer.__init__

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| custom_stop_words | Optional[set] | No | None | Additional words to filter (merged with defaults) |
| min_word_length | int | No | 3 | Minimum word length for analysis |
| verbose | bool | No | True | Print progress messages |

### DocumentAnalyzer.analyze_with_ai

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | str | Yes | - | Document text to analyze |

**Returns**: `Optional[DocumentAnalysis]` - Pydantic model with structured insights or None if AI disabled

**Exceptions**:
- Returns None if `OPENAI_API_KEY` not set
- Returns None if text is empty
- Returns None on API failures (logs error if verbose=True)

### DocumentAnalyzer.analyze_text

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| text | str | Yes | - | Raw text to analyze |
| output_dir | Optional[Union[str, Path]] | No | None | Directory for visualizations |

**Returns**: Dict with:
- `status`: "success" or "error"
- `total_words`: Word count
- `unique_words`: Unique word count
- `word_frequency`: Dict[str, int]
- `wordcloud_file`: Path (if output_dir provided)
- `frequency_chart_file`: Path (if output_dir provided)
- `ai_analysis`: Dict with AI results (if OPENAI_API_KEY set)

## Behavior

### Core Functionality

1. **Text Preprocessing**: Clean text (remove emails, dates, phone numbers, special chars)
2. **Word Extraction**: Tokenize with NLTK, filter stop words, extract meaningful terms
3. **Frequency Analysis**: Count word occurrences, generate top-N lists
4. **Visualization**: Create word clouds and frequency bar charts
5. **AI Analysis**: Call OpenAI Responses API for structured entity extraction
6. **Validation**: Return Pydantic-validated results

### NLTK Data Management

Automatically downloads required NLTK data on first run:
- `punkt` - Tokenizer models
- `stopwords` - English stop words

### PDF Support

Uses `pdfplumber` for text extraction from PDFs:
- Extracts text from all pages
- Routes to ImageAnalyzer if no text extracted (scanned PDFs)

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| OPENAI_API_KEY not set | Missing environment variable | Falls back to word frequency only (no AI) |
| PDF text extraction failed | Scanned/image PDF | Routes to ImageAnalyzer for OCR |
| API rate limit | Too many requests | Returns None, logs error (retry externally) |
| Empty text | No content to analyze | Returns error status with message |

### Logging

When `verbose=True`:
- `✅` - Success messages (AI analysis complete, files saved)
- `⚠️` - Warnings (AI disabled, no text extracted)
- `❌` - Errors (API failures, parsing errors)

## Performance Considerations

### Time Complexity
- Word frequency: O(n) where n = word count
- AI analysis: ~2-5 seconds per document (API latency)
- Visualization: O(n) where n = unique words

### Space Complexity
- Word frequency dict: O(u) where u = unique words
- Visualizations: ~1-5 MB PNG files
- AI analysis: ~2-10 KB JSON

### Optimization Notes
- Uses non-interactive matplotlib backend (`Agg`) for production
- Caches NLTK data downloads
- AI analysis skipped if `OPENAI_API_KEY` not set (graceful degradation)

---

# EmailAnalyzer

## Purpose

Provides forensic-grade email thread analysis for legal evidence processing:
- Thread reconstruction and chronological ordering
- Participant role and authority analysis
- Escalation detection (tone changes, authority escalation, new recipients)
- Communication pattern assessment (professional, hostile, retaliatory)
- Legal risk flagging (harassment, discrimination, retaliation)

## Usage

### Basic Usage

```python
from pathlib import Path
from openai import OpenAI
from evidence_toolkit.analyzers import EmailAnalyzer

# Initialize with OpenAI client
client = OpenAI(api_key="sk-...")
analyzer = EmailAnalyzer(openai_client=client, verbose=True)

# Analyze email files as thread
email_files = [
    Path("email1.eml"),
    Path("email2.eml"),
    Path("email3.eml")
]

analysis = analyzer.analyze_email_files(email_files, case_id="CASE-2024-001")

if analysis:
    print(f"Thread Summary: {analysis.thread_summary}")
    print(f"Legal Significance: {analysis.legal_significance}")
    print(f"Communication Pattern: {analysis.communication_pattern}")

    # Check for escalation events
    for event in analysis.escalation_events:
        print(f"Escalation at email {event.email_position + 1}: {event.escalation_type}")
        print(f"  Confidence: {event.confidence:.2f}")
```

### Working with Parsed Emails

```python
from evidence_toolkit.analyzers import EmailParser, EmailAnalyzer

# Parse emails first
parser = EmailParser(verbose=True)
emails = [parser.parse_file(f) for f in email_files]

# Build thread
threaded_emails = parser.build_thread_from_emails(emails)

# Analyze thread
analyzer = EmailAnalyzer(openai_client=client)
analysis = analyzer.analyze_email_thread(threaded_emails)
```

### Export and Reporting

```python
# Export analysis to JSON
analyzer.export_analysis_to_json(
    analysis,
    output_path=Path("data/storage/derived/sha256=<hash>/email_analysis.json")
)

# Generate human-readable summary
summary = analyzer.get_analysis_summary(analysis)
print(summary)
```

## AI Integration

### OpenAI Model

- **Model**: `gpt-4.1-mini` (16x cheaper than gpt-4o)
- **API**: OpenAI Responses API
- **Cost**: ~$0.02 per email thread analysis (typical 5-10 emails)

### Prompt Configuration

Location: `src/evidence_toolkit/domains/legal_config.py`

```python
EMAIL_ANALYSIS_PROMPT = """You are a forensic email analyzer for legal evidence processing.

Analyze the provided email thread with these requirements:

1. **Thread Summary**: Concise summary focusing on legal significance
2. **Participant Analysis** (v3.1 Enhanced): For each participant:
   - Organizational authority level (executive/management/employee/external)
   - Message count: How many messages this participant sent
   - Deference score: Communication style analysis
     * 0.0 = Highly dominant/controlling (gives orders, demands, uses imperatives)
     * 0.5 = Neutral/balanced (collaborative, professional)
     * 1.0 = Highly deferential (seeks approval, apologetic, passive)
   - Dominant topics: Subjects this participant drove or controlled in the conversation
3. **Communication Pattern**: professional, escalating, hostile, retaliatory
4. **Sentiment Progression**: Track sentiment changes (0.0=hostile, 1.0=professional)
5. **Escalation Detection**: tone changes, authority escalation, threats, deadlines
6. **Legal Significance**: critical/high/medium/low
7. **Risk Assessment**: harassment, discrimination, retaliation, threatening
8. **Timeline Reconstruction**: Chronological summary of key events

Focus on workplace investigation patterns: retaliation, escalation, policy violations, power imbalances.
Use power dynamics analysis to identify controlling behavior, intimidation, or abuse of authority.
"""
```

### Response Format (Pydantic Model)

```python
class EmailThreadAnalysis(BaseModel):
    thread_summary: str
    participants: List[EmailParticipant]
    communication_pattern: str  # professional, escalating, hostile, retaliatory
    sentiment_progression: List[float]  # Per-email sentiment scores
    escalation_events: List[EscalationEvent]
    legal_significance: str  # critical, high, medium, low
    risk_flags: List[str]
    timeline_reconstruction: List[str]  # Chronological narrative
    confidence_overall: float

class EmailParticipant(BaseModel):
    email_address: str
    display_name: Optional[str] = None
    role: str  # sender, recipient, cc, bcc
    authority_level: str  # executive, management, employee, external
    confidence: float

    # v3.1 Layer 1 Enhancements - Power Dynamics Analysis
    message_count: int = 0  # Number of messages sent by this participant
    deference_score: float = 0.5  # 0.0=highly dominant, 0.5=neutral, 1.0=highly deferential
    dominant_topics: List[str] = []  # Topics this participant drove/controlled

class EscalationEvent(BaseModel):
    email_position: int  # 0-indexed position in thread
    escalation_type: str  # tone_change, authority_escalation, new_recipients, etc.
    description: str
    confidence: float
```

## API Reference

### EmailAnalyzer.__init__

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| openai_client | OpenAI | Yes | - | OpenAI client instance (from `openai` package) |
| verbose | bool | No | True | Print progress messages |

### EmailAnalyzer.analyze_email_thread

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| emails | List[Dict[str, Any]] | Yes | - | Parsed email dictionaries from EmailParser |

**Returns**: `Optional[EmailThreadAnalysis]` - Pydantic model or None on failure

### EmailAnalyzer.analyze_email_files

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file_paths | List[Path] | Yes | - | Email file paths to analyze |
| case_id | Optional[str] | No | None | Case identifier for tracking |

**Returns**: `Optional[EmailThreadAnalysis]` - Pydantic model or None on failure

## Behavior

### Email Thread Formatting

The analyzer converts parsed emails into a structured format for AI analysis:

```
EMAIL 1/3:
From: john.doe@company.com
To: rachel.hemmings@company.com
CC: hr@company.com
Subject: Complaint Regarding Workplace Conduct
Date: Mon, 15 Jan 2024 09:30:00 -0500

[Email body content...]

---

EMAIL 2/3:
...
```

### Escalation Detection

The AI identifies:
- **Tone changes**: Shift from professional to hostile language
- **Authority escalation**: Adding executives/management to CC
- **New recipients**: Expansion of recipient list (visibility expansion)
- **Threats/deadlines**: Introduction of ultimatums or time constraints

## Error Handling

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| AI analysis disabled | openai_client=None | Returns None, logs warning |
| Empty email list | No emails provided | Returns None, logs warning |
| API incomplete status | OpenAI API issue | Returns None, logs incomplete details |
| API refusal | Content policy violation | Returns None, logs refusal reason |

---

# EmailParser

## Purpose

Multi-format email parsing for forensic analysis, supporting:
- `.eml` files (RFC 822 standard email format)
- `.msg` files (Outlook format, requires `extract-msg`)
- `.mbox` files (Unix mailbox format)

Provides standardized email data extraction and thread reconstruction.

## Usage

### Basic Parsing

```python
from pathlib import Path
from evidence_toolkit.analyzers import EmailParser

parser = EmailParser(verbose=True)

# Parse single email file
email_data = parser.parse_file(Path("evidence.eml"))

print(f"From: {email_data['headers']['from']}")
print(f"To: {', '.join(email_data['headers']['to'])}")
print(f"Subject: {email_data['headers']['subject']}")
print(f"Body: {email_data['body'][:200]}...")
```

### Thread Reconstruction

```python
# Parse multiple emails
email_files = [Path(f"email{i}.eml") for i in range(1, 6)]
emails = [parser.parse_file(f) for f in email_files]

# Build thread (sorts by date, groups by subject)
threaded = parser.build_thread_from_emails(emails)

# Extract thread metadata
metadata = parser.extract_thread_metadata(threaded)

print(f"Thread Subject: {metadata['subject']}")
print(f"Participants: {metadata['participant_count']}")
print(f"Duration: {metadata['duration_days']} days")
print(f"Email Count: {metadata['email_count']}")
```

### Format-Specific Parsing

```python
# Parse .eml file
eml_data = parser.parse_eml_file(Path("email.eml"))

# Parse Outlook .msg file (requires extract-msg library)
msg_data = parser.parse_msg_file(Path("email.msg"))

# Parse .mbox file (returns list of emails)
mbox_emails = parser.parse_mbox_file(Path("mailbox.mbox"))
```

## API Reference

### EmailParser.parse_file

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| file_path | Path | Yes | - | Path to email file (.eml, .msg, .mbox) |

**Returns**: `Optional[Dict[str, Any]]` - Standardized email data or None on failure

**Email Data Structure**:
```python
{
    'headers': {
        'from': str,
        'to': List[str],
        'cc': List[str],
        'bcc': List[str],
        'subject': str,
        'date': str,
        'parsed_date': str (ISO format),
        'message_id': Optional[str],
        'in_reply_to': Optional[str],
        'references': Optional[str]
    },
    'body': str,               # Plain text body
    'html_body': Optional[str], # HTML body if present
    'attachments': List[str],   # Attachment filenames
    'source_file': str,         # Original file path
    'file_format': str          # 'eml', 'msg', or 'mbox'
}
```

### EmailParser.build_thread_from_emails

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| emails | List[Dict[str, Any]] | Yes | - | Parsed email dictionaries |

**Returns**: `List[Dict[str, Any]]` - Emails sorted in thread order with added metadata:
- `thread_position`: 0-indexed position in thread
- `thread_size`: Total emails in thread
- `normalized_subject`: Subject without Re:/Fwd: prefixes

### EmailParser.extract_thread_metadata

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| emails | List[Dict[str, Any]] | Yes | - | Threaded emails |

**Returns**: `Dict[str, Any]` - Thread metadata including participants, dates, duration

## Behavior

### Subject Normalization

Removes common reply/forward prefixes for thread grouping:
- `Re:` → removed
- `Fwd:`, `Fw:` → removed
- Case-insensitive matching
- Multiple prefixes handled (`Re: Re: Fwd:` → base subject)

### Date Parsing

Multi-strategy date parsing:
1. `email.utils.parsedate_to_datetime()` for RFC 822 dates
2. Regex fallback for malformed dates
3. Returns None for unparseable dates (graceful degradation)

### Attachment Handling

- Extracts attachment filenames only (not content)
- Supports multipart MIME messages
- `.msg` files: uses `extract-msg` library

## Dependencies

### Required
- `email` (Python stdlib)
- `mailbox` (Python stdlib)

### Optional
- `extract-msg` - Required for .msg file support
  ```bash
  uv pip install extract-msg
  ```

## Error Handling

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| File not found | Invalid file path | Returns None, logs error |
| Unsupported format | Unknown file extension | Returns None, logs warning |
| Malformed date | Invalid date string | Sets parsed_date=None, continues |
| Missing extract-msg | .msg file without library | Raises ImportError with install instructions |

---

# ImageAnalyzer

## Purpose

Analyzes images and scanned PDFs using OpenAI Vision API for:
- OCR (Optical Character Recognition) - text extraction
- Scene description and object detection
- Forensic image analysis for legal evidence
- Multi-page PDF processing (converts to images, analyzes each page)

## Usage

### Basic Image Analysis

```python
from pathlib import Path
from evidence_toolkit.analyzers import ImageAnalyzer

# Initialize analyzer
analyzer = ImageAnalyzer(
    api_key="sk-...",  # Or uses OPENAI_API_KEY env var
    model="gpt-4.1-mini",  # Vision-capable model
    verbose=True
)

# Analyze image
result = analyzer.analyze_image(
    image_path=Path("evidence_photo.jpg"),
    prompt="Focus on any visible text or identifying markers"
)

print(f"Scene: {result.scene_description}")
print(f"Detected Text: {result.detected_text}")
print(f"Objects: {', '.join(result.detected_objects or [])}")
print(f"Confidence: {result.analysis_confidence:.2f}")
```

### Scanned PDF Analysis

```python
# Analyze scanned PDF (converts pages to images)
result = analyzer.analyze_pdf(
    pdf_path=Path("scanned_contract.pdf"),
    prompt="Extract all text and identify document type",
    max_pages=10  # Limit to first 10 pages
)

# Result contains combined OCR from all pages
print(f"Extracted Text: {result.detected_text}")
print(f"Pages Analyzed: {result.openai_response['pages_analyzed']}")
```

### Custom Analysis Prompt

```python
# Provide specific instructions for Vision API
result = analyzer.analyze_image(
    image_path=Path("workplace_photo.jpg"),
    prompt="Identify any people, timestamps, or company logos visible in the image"
)
```

## AI Integration

### OpenAI Model

- **Model**: `gpt-4.1-mini` (default) - Vision-capable, 1M+ token context
- **API**: OpenAI Responses API (structured vision analysis)
- **Cost**: ~$0.01-0.05 per image (depends on resolution)
- **Alternatives**: `gpt-4o-2024-08-06` (higher quality, higher cost)

### Prompt Configuration

Location: `src/evidence_toolkit/domains/legal_config.py`

```python
IMAGE_ANALYSIS_PROMPT = """You are assisting a legal evidence analyst.
Examine the IMAGE and provide factual, non-speculative observations about:
- Visual scene and objects
- Any visible text (OCR)
- People, if present
- Timestamps or identifying markers
- Potential evidential value

Be precise, objective, and note any quality issues or uncertainties."""
```

### Response Format (Pydantic Model)

```python
class ImageAnalysisStructured(BaseModel):
    scene_description: str
    detected_text: Optional[str] = None
    detected_objects: Optional[List[str]] = None
    confidence_overall: float

class ImageAnalysisResult(BaseModel):
    openai_model: str
    openai_response: Dict[str, Any]
    detected_objects: Optional[List[str]]
    detected_text: Optional[str]
    scene_description: str
    analysis_confidence: float
```

## API Reference

### ImageAnalyzer.__init__

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| api_key | Optional[str] | No | None | OpenAI API key (falls back to OPENAI_API_KEY env var) |
| model | str | No | "gpt-4.1-mini" | Vision-capable model |
| max_tokens | int | No | 1000 | Max tokens (unused with Responses API) |
| verbose | bool | No | True | Print progress messages |

### ImageAnalyzer.analyze_image

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| image_path | Path | Yes | - | Path to image file |
| prompt | Optional[str] | No | None | Custom analysis prompt (overrides default) |

**Returns**: `ImageAnalysisResult` - Pydantic model with OCR, scene description, objects

**Exceptions**:
- `ValueError` if file is not a supported image format
- `ValueError` if file does not exist
- Returns error result (confidence=0.0) on API failures

### ImageAnalyzer.analyze_pdf

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| pdf_path | Path | Yes | - | Path to PDF file |
| prompt | Optional[str] | No | None | Custom analysis prompt |
| max_pages | Optional[int] | No | None | Limit to first N pages |

**Returns**: `ImageAnalysisResult` - Combined analysis from all pages

**Requires**: `pdf2image` library (`uv pip install pdf2image`)

## Behavior

### Image Encoding

Images are base64-encoded before sending to OpenAI Vision API:
```python
def _encode_image(self, image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
```

### PDF Processing

1. Convert PDF pages to images (200 DPI) using `pdf2image`
2. Analyze each page individually with Vision API
3. Combine results:
   - Detected text: Concatenated with `[Page N]` prefixes
   - Objects: Deduplicated list
   - Scene descriptions: Per-page summaries
4. Return single `ImageAnalysisResult` with combined data

### Supported Formats

- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`
- **PDFs**: `.pdf` (converted to images)

Validation performed by `core.utils.is_image_file()`

## Performance Considerations

### Time Complexity
- Single image: ~2-5 seconds (API latency)
- PDF processing: ~2-5 seconds per page
- 10-page PDF: ~20-50 seconds total

### Space Complexity
- Base64 encoding: ~1.33x image file size (in memory)
- PDF temp files: ~1-5 MB per page (deleted after analysis)

### Optimization Notes
- PDF pages analyzed sequentially (could parallelize for speed)
- Temp files cleaned up immediately after each page
- Max pages limit prevents runaway costs on large PDFs

## Error Handling

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| pdf2image not installed | Missing dependency | Returns error result with install instructions |
| Invalid image format | Unsupported file type | Raises ValueError |
| API refusal | Content policy violation | Returns error result with refusal reason |
| API incomplete | Timeout or API issue | Returns error result with incomplete details |

---

# CorrelationAnalyzer

## Purpose

Cross-evidence correlation analyzer that identifies:
- **Entity Correlations**: People, organizations, emails appearing across multiple evidence pieces
- **Timeline Reconstruction**: Chronological ordering of events from all evidence
- **Temporal Patterns**: Sequences of events in short time windows (escalation clusters)
- **Timeline Gaps**: Suspicious absences in evidence timeline
- **Legal Patterns** (v3.1): AI-detected contradictions, corroboration, evidence gaps

## Usage

### Basic Correlation Analysis

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers import CorrelationAnalyzer

# Initialize with storage
storage = EvidenceStorage("data/storage")
analyzer = CorrelationAnalyzer(storage, verbose=True)

# Analyze all evidence for a case
result = analyzer.analyze_case_correlations("CASE-2024-001")

print(f"Evidence Count: {result.evidence_count}")
print(f"Entity Correlations: {len(result.entity_correlations)}")
print(f"Timeline Events: {len(result.timeline_events)}")

# Top correlated entities (appearing in most evidence)
for entity in result.entity_correlations[:5]:
    print(f"- {entity.entity_name} ({entity.entity_type})")
    print(f"  Appears in {entity.occurrence_count} evidence pieces")
    print(f"  Average confidence: {entity.confidence_average:.2f}")
```

### Timeline Analysis

```python
# Get timeline events sorted chronologically
timeline = result.timeline_events

for event in timeline[:10]:
    print(f"{event.timestamp.isoformat()}: {event.description}")
    print(f"  Source: {event.evidence_sha256[:8]}... ({event.evidence_type})")
    if event.ai_classification:
        print(f"  Legal significance: {event.ai_classification.get('legal_significance')}")
```

### Temporal Pattern Detection

```python
# Detect temporal sequences (escalation clusters)
sequences = result.temporal_sequences

for seq in sequences:
    print(f"Temporal Cluster: {seq['event_count']} events in {seq['time_span_hours']:.1f} hours")
    print(f"  Anchor: {seq['anchor_event']['description']}")
    print(f"  Legal Significance: {seq['legal_significance']}")
    print(f"  Risk Flags: {', '.join(seq['risk_flags'])}")

# Detect timeline gaps (evidence spoliation indicators)
gaps = result.timeline_gaps

for gap in gaps:
    print(f"Gap: {gap['gap_duration_days']:.1f} days ({gap['significance']})")
    print(f"  Before: {gap['before_event']['description']}")
    print(f"  After: {gap['after_event']['description']}")
```

### AI Legal Pattern Detection (v3.1)

```python
from openai import OpenAI

# Initialize with OpenAI client for pattern detection
client = OpenAI(api_key="sk-...")
analyzer = CorrelationAnalyzer(storage, openai_client=client, verbose=True)

result = analyzer.analyze_case_correlations("CASE-2024-001")

if result.legal_patterns:
    patterns = result.legal_patterns

    print(f"Pattern Summary: {patterns.pattern_summary}")
    print(f"Confidence: {patterns.confidence:.2f}")

    # Contradictions
    for contradiction in patterns.contradictions:
        print(f"Contradiction ({contradiction.contradiction_type}):")
        print(f"  Severity: {contradiction.severity:.2f}")
        print(f"  Statement 1: {contradiction.statement_1}")
        print(f"  Statement 2: {contradiction.statement_2}")

    # Corroboration
    for corr in patterns.corroboration:
        print(f"Corroborated Claim ({corr.strength}):")
        print(f"  Claim: {corr.claim}")
        print(f"  Supporting Evidence: {len(corr.supporting_evidence)} pieces")

    # Evidence Gaps
    for gap in patterns.evidence_gaps:
        print(f"Evidence Gap ({gap.gap_type}):")
        print(f"  Description: {gap.description}")
        print(f"  Legal Significance: {gap.legal_significance}")
```

## AI Integration (v3.1 Enhancement)

### OpenAI Model

- **Model**: `gpt-4.1-mini`
- **API**: OpenAI Responses API
- **Purpose**: Cross-evidence pattern detection
- **Optional**: Analyzer works without AI (entity/timeline only)

### Prompt Configuration

Location: `src/evidence_toolkit/domains/legal_config.py`

```python
CORRELATION_PATTERN_PROMPT = """You are analyzing cross-evidence correlation data
for legal pattern detection.

Given entity correlations and timeline events from multiple evidence pieces, identify:

1. **Contradictions**: Conflicting statements across evidence
   - Factual, Temporal, Attribution conflicts
   - Severity: 0.0-1.0

2. **Corroboration**: Evidence supporting the same claims
   - Strength: weak (1 source), moderate (2-3), strong (4+)

3. **Evidence Gaps**: Missing witnesses, documentation, unexplained absences

4. **Pattern Summary**: Overall assessment and legal significance

Focus on workplace investigation patterns: retaliation, credibility, evidence tampering.
"""
```

### Response Format (Pydantic Model)

```python
class LegalPatternAnalysis(BaseModel):
    contradictions: List[Contradiction]
    corroboration: List[CorroborationLink]
    evidence_gaps: List[EvidenceGap]
    pattern_summary: str
    confidence: float

class Contradiction(BaseModel):
    contradiction_type: str  # factual, temporal, attribution
    statement_1: str
    statement_2: str
    evidence_1_sha256: str
    evidence_2_sha256: str
    severity: float  # 0.0-1.0

class CorroborationLink(BaseModel):
    claim: str
    strength: str  # weak, moderate, strong
    supporting_evidence: List[str]  # List of SHA256 hashes
    explanation: str

class EvidenceGap(BaseModel):
    gap_type: str  # missing_witness, missing_documentation, unexplained_absence
    description: str
    legal_significance: str  # low, medium, high
```

## API Reference

### CorrelationAnalyzer.__init__

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| evidence_storage | EvidenceStorage | Yes | - | Storage instance for accessing evidence |
| openai_client | Optional[OpenAI] | No | None | OpenAI client for AI pattern detection (v3.1) |
| verbose | bool | No | True | Print progress messages |

### CorrelationAnalyzer.analyze_case_correlations

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| case_id | str | Yes | - | Case identifier to analyze |

**Returns**: `CorrelationAnalysis` - Pydantic model with:
- `case_id`: str
- `evidence_count`: int
- `entity_correlations`: List[CorrelatedEntity]
- `timeline_events`: List[TimelineEvent]
- `temporal_sequences`: List[Dict] - Escalation clusters
- `timeline_gaps`: List[Dict] - Suspicious gaps
- `legal_patterns`: Optional[LegalPatternAnalysis] - AI-detected patterns (v3.1)
- `analysis_timestamp`: datetime

## Behavior

### Entity Canonicalization

Robust name normalization for cross-evidence matching:

```python
def canonicalize_entity_name(name: str) -> Tuple[str, str, str]:
    """
    Returns: (base_form, short_form, initials)

    Examples:
        "John Q. Smith" → ("john q smith", "john smith", "j q s")
        "Smith, John" → ("john smith", "john smith", "j s")
        "Chief Executive Officer" → ("ceo", "ceo", "c")
    """
```

**Canonicalization steps**:
1. Unicode normalization (NFKC)
2. Casefold (Unicode-aware lowercase)
3. Role variant expansion ("Chief Executive Officer" → "ceo")
4. "Last, First" format conversion ("Smith, John" → "John Smith")
5. Extract base form (all words), short form (first + last), initials

### Entity Extraction by Evidence Type

| Evidence Type | Data Source | Entity Types | Confidence |
|---------------|-------------|--------------|------------|
| **Document** | AI entities (DocumentEntity) | person, organization, date, legal_term | AI-provided |
| **Document** | Fallback: top words | unknown | 0.6 (word freq based) |
| **Email** | AI participants (EmailParticipant) | person, email_address | 0.9-0.95 |
| **Email** | Fallback: regex email extraction | email_address | 0.7 |
| **Image** | OCR detected text | text_in_image | 0.7 |

### Timeline Event Sources

| Event Type | Source | Confidence | Notes |
|------------|--------|------------|-------|
| `file_created` | File metadata | 1.0 | File system timestamp |
| `analysis_performed` | Analysis metadata | 1.0 | AI analysis completion |
| `communication` | Email Date header | 1.0 | RFC 822 parsed date |
| `photo_taken` | EXIF DateTimeOriginal | 0.9 | Can be manipulated |
| `document_date_reference` | AI-extracted dates | AI-provided | From document content |

### Temporal Sequence Detection

Identifies legally significant event clusters:

**Trigger Conditions** (anchor events):
- Legal significance: `high` or `critical`
- Communication pattern: `hostile`, `retaliatory`, `escalating`
- Risk flags: `retaliation`, `harassment`, `discrimination`, `threatening`

**Detection Parameters**:
- `temporal_window_hours`: 72 (3 days) - default window for related events
- Finds nearby events within window
- Calculates legal significance based on risk flags

**Output**: List of sequences with:
- Anchor event (triggering event)
- Related events (within time window)
- Time span (hours/days)
- Legal significance (low/medium/high)
- Aggregated risk flags

### Timeline Gap Detection

Identifies suspicious absences in evidence:

**Detection Threshold**: 168 hours (7 days)

**Significance Assessment**:
- High: > 720 hours (30 days)
- Medium: > 336 hours (14 days)
- Low: > 168 hours (7 days)

**Filters Out**: Ingestion artifacts (`analysis_performed`, `file_created`)

**Output**: List of gaps with:
- Gap start/end timestamps
- Duration (hours/days)
- Significance level
- Events before/after gap (with AI classification)

## Performance Considerations

### Time Complexity
- Entity extraction: O(n × e) where n=evidence count, e=entities per evidence
- Correlation: O(u²) where u=unique entities (worst case, rare)
- Timeline: O(t log t) where t=timeline events (sorting)
- Actual: ~1-5 seconds for typical case (10-50 evidence items)

### Space Complexity
- Entity index: O(u × n) where u=unique entities, n=occurrences
- Timeline: O(t) where t=total events
- Typical: ~100KB - 1MB for medium-sized case

### Optimization Notes
- Variant-based indexing reduces entity duplicates
- Deduplication by SHA256 prevents double-counting
- AI pattern detection is optional (skip if no OpenAI client)

## Error Handling

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| No evidence for case | Invalid case_id or no ingested evidence | Returns empty CorrelationAnalysis |
| Invalid JSON in analysis files | Corrupted data | Skips invalid evidence, continues |
| AI pattern detection failed | API error or no client | Sets legal_patterns=None, continues |
| Date parsing failed | Malformed dates | Skips event, continues with other events |

## Testing

### Unit Tests

```python
def test_canonicalize_entity_name():
    """Test entity name normalization"""
    base, short, initials = canonicalize_entity_name("John Q. Smith")
    assert base == "john q smith"
    assert short == "john smith"
    assert initials == "j q s"

def test_correlation_analysis():
    """Test cross-evidence correlation"""
    storage = EvidenceStorage("test_data/storage")
    analyzer = CorrelationAnalyzer(storage, verbose=False)
    result = analyzer.analyze_case_correlations("TEST-CASE")
    assert isinstance(result, CorrelationAnalysis)
    assert result.case_id == "TEST-CASE"
```

---

# Dependencies

## Internal Dependencies

```python
from evidence_toolkit.core.models import (
    DocumentAnalysis, DocumentEntity,
    EmailThreadAnalysis, EmailParticipant, EscalationEvent,
    ImageAnalysisResult, ImageAnalysisStructured,
    CorrelationAnalysis, CorrelatedEntity, TimelineEvent,
    LegalPatternAnalysis, Contradiction, CorroborationLink
)
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.utils import is_image_file
from evidence_toolkit.domains import legal_config
```

## External Dependencies

### Required
- `openai` - OpenAI Responses API client
- `pydantic` - Data validation and models
- `nltk` - Natural language processing (DocumentAnalyzer)
- `matplotlib` - Visualization (DocumentAnalyzer)
- `wordcloud` - Word cloud generation (DocumentAnalyzer)

### Optional
- `pdfplumber` - PDF text extraction (DocumentAnalyzer)
- `pdf2image` - PDF to image conversion (ImageAnalyzer)
- `extract-msg` - Outlook .msg file parsing (EmailParser)
- `dateutil` - Flexible date parsing (CorrelationAnalyzer)

### Installation

```bash
# Required
uv pip install openai pydantic nltk matplotlib wordcloud

# Optional - PDF support
uv pip install pdfplumber pdf2image

# Optional - Email support
uv pip install extract-msg python-dateutil
```

---

# Migration Notes (v2.0 → v3.0)

## Breaking Changes

1. **All Pydantic Models**: `CorrelationAnalysis` (was `CorrelationResult` dataclass) now uses Pydantic
2. **EvidenceStorage**: `EvidenceManager` renamed to `EvidenceStorage`
3. **Import Paths**: All analyzers now in `evidence_toolkit.analyzers` (was `document_analyzer`)
4. **Unified Models**: All models consolidated in `core.models` (was split across 5 files)

## Upgrade Guide

### Old (v2.0)
```python
from document_analyzer.document_analyzer_core import DocumentAnalyzer
from document_analyzer.email_analyzer import EmailAnalyzer
from document_analyzer.correlation_analyzer import CorrelationAnalyzer
from document_analyzer.evidence_manager import EvidenceManager
from models.cross_analysis_models import CrossAnalysisBundle
```

### New (v3.0)
```python
from evidence_toolkit.analyzers import (
    DocumentAnalyzer,
    EmailAnalyzer,
    CorrelationAnalyzer
)
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import CorrelationAnalysis
```

## New Features (v3.0)

- **Pydantic Validation**: All outputs validated at runtime
- **Responses API**: Structured outputs with schema compliance
- **Legal Patterns** (v3.1): AI contradiction/corroboration detection
- **Temporal Patterns**: Escalation cluster detection
- **Timeline Gaps**: Evidence spoliation indicators
- **Enhanced Entities**: Relationships, quoted text, associated events

---

# Future Considerations

## Planned Enhancements

1. **Parallel PDF Processing**: Speed up multi-page PDFs
2. **Entity Relationship Graphs**: Visualize entity connections
3. **Advanced Timeline Viz**: Interactive timeline with Plotly
4. **Batch Analysis**: Process multiple cases in parallel
5. **Caching**: Cache AI results to reduce API costs on re-analysis
6. **Custom Models**: Support local LLMs for sensitive cases

## Known Limitations

1. **AI Cost**: Large cases (100+ documents) can incur $10-50 in OpenAI costs
2. **Sequential Processing**: PDFs analyzed page-by-page (could parallelize)
3. **OCR Accuracy**: Vision API OCR ~90-95% accurate (not perfect)
4. **Entity Deduplication**: Requires exact canonical form matches (could use fuzzy matching)
5. **Timeline Timezone**: Naïve datetimes (no timezone support yet)

## Technical Debt

- TODO: Implement `DocumentValidator` for schema validation
- TODO: Add retry logic for OpenAI API rate limits
- TODO: Support additional image formats (HEIC, RAW)
- TODO: Add progress bars for long-running analyses

---

# Examples

## Example 1: Full Case Analysis Pipeline

```python
"""Complete workflow: Ingest → Analyze → Correlate → Package"""
from pathlib import Path
from openai import OpenAI
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.analyzers import (
    DocumentAnalyzer,
    EmailAnalyzer,
    ImageAnalyzer,
    CorrelationAnalyzer
)
from evidence_toolkit.pipeline import PackageGenerator

# Initialize
storage = EvidenceStorage("data/storage")
openai_client = OpenAI(api_key="sk-...")
case_id = "CASE-2024-001"

# Step 1: Analyze documents
doc_analyzer = DocumentAnalyzer(verbose=True)
for doc_file in Path("data/cases/CASE-2024-001").glob("*.txt"):
    text = doc_file.read_text()
    analysis = doc_analyzer.analyze_with_ai(text)
    # Save to storage...

# Step 2: Analyze emails
email_analyzer = EmailAnalyzer(openai_client, verbose=True)
email_files = list(Path("data/cases/CASE-2024-001").glob("*.eml"))
email_analysis = email_analyzer.analyze_email_files(email_files, case_id)

# Step 3: Analyze images
image_analyzer = ImageAnalyzer(verbose=True)
for img_file in Path("data/cases/CASE-2024-001").glob("*.jpg"):
    img_analysis = image_analyzer.analyze_image(img_file)
    # Save to storage...

# Step 4: Cross-evidence correlation
corr_analyzer = CorrelationAnalyzer(storage, openai_client, verbose=True)
correlation = corr_analyzer.analyze_case_correlations(case_id)

print(f"Top 5 correlated entities:")
for entity in correlation.entity_correlations[:5]:
    print(f"  - {entity.entity_name} ({entity.occurrence_count} occurrences)")

print(f"\nTemporal sequences: {len(correlation.temporal_sequences)}")
print(f"Timeline gaps: {len(correlation.timeline_gaps)}")

if correlation.legal_patterns:
    print(f"\nLegal patterns detected:")
    print(f"  Contradictions: {len(correlation.legal_patterns.contradictions)}")
    print(f"  Corroboration links: {len(correlation.legal_patterns.corroboration)}")
```

## Example 2: Handling Edge Cases

```python
"""Graceful degradation when AI unavailable"""
from evidence_toolkit.analyzers import DocumentAnalyzer

# Initialize without OpenAI API key
analyzer = DocumentAnalyzer(verbose=True)

text = "Legal document text..."
result = analyzer.analyze_text(text)

# Check if AI analysis succeeded
if result.get('ai_analysis'):
    print("AI analysis available")
    print(f"Entities: {result['ai_analysis']['entities']}")
else:
    print("AI analysis unavailable - using word frequency only")
    print(f"Top words: {list(result['word_frequency'].items())[:10]}")
```

## Example 3: Custom Stop Words

```python
"""Domain-specific stop word filtering"""
from evidence_toolkit.analyzers import DocumentAnalyzer

# Add legal/HR domain stop words
legal_stop_words = {
    'plaintiff', 'defendant', 'hereby', 'whereas', 'pursuant',
    'aforementioned', 'herein', 'thereof', 'thereto',
    'employee', 'employer', 'department', 'company'
}

analyzer = DocumentAnalyzer(
    custom_stop_words=legal_stop_words,
    min_word_length=4,  # Longer words only
    verbose=True
)

result = analyzer.analyze_directory(
    "data/cases/HR-CASE",
    output_dir="output/HR-CASE"
)
```

## Example 4: v3.1 Power Dynamics Analysis (Email)

```python
"""Workplace investigation: Analyzing power imbalances and controlling behavior"""
from pathlib import Path
from openai import OpenAI
from evidence_toolkit.analyzers import EmailAnalyzer

# Initialize analyzer
client = OpenAI(api_key="sk-...")
analyzer = EmailAnalyzer(openai_client=client, verbose=True)

# Analyze email thread
email_files = [
    Path("email1_initial_complaint.eml"),
    Path("email2_manager_response.eml"),
    Path("email3_hr_escalation.eml")
]

analysis = analyzer.analyze_email_files(email_files, case_id="WORKPLACE-2024")

# Examine power dynamics
print("=== POWER DYNAMICS ANALYSIS ===")
for participant in analysis.participants:
    print(f"\n{participant.display_name or participant.email_address}")
    print(f"  Authority: {participant.authority_level}")
    print(f"  Messages sent: {participant.message_count}")
    print(f"  Deference score: {participant.deference_score:.2f}")

    # Interpret deference score
    if participant.deference_score < 0.3:
        style = "DOMINANT/CONTROLLING"
    elif participant.deference_score > 0.7:
        style = "DEFERENTIAL/SUBMISSIVE"
    else:
        style = "BALANCED"
    print(f"  Communication style: {style}")

    if participant.dominant_topics:
        print(f"  Controlled topics: {', '.join(participant.dominant_topics)}")

# Example output interpretation:
# Manager A:
#   Authority: management
#   Messages sent: 5
#   Deference score: 0.15  ← HIGHLY DOMINANT (red flag for abuse of power)
#   Communication style: DOMINANT/CONTROLLING
#   Controlled topics: investigation process, documentation requirements, deadlines
#
# Employee B:
#   Authority: employee
#   Messages sent: 2
#   Deference score: 0.85  ← HIGHLY DEFERENTIAL (may indicate intimidation)
#   Communication style: DEFERENTIAL/SUBMISSIVE
#   Controlled topics: (none - reactive only)
#
# This pattern (dominant manager + deferential employee) may indicate:
# - Power imbalance being exploited
# - Intimidation or coercion
# - Hostile work environment
```

---

This documentation follows Evidence Toolkit standards for clarity, completeness, and maintainability. It provides both high-level understanding and implementation details for developers working with the analyzers module.
