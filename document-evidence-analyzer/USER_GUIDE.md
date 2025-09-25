# Document Evidence Analyzer - User Guide

A forensic-grade document analysis tool for legal evidence processing with AI-powered insights, retaliation pattern detection, and content-addressed evidence storage.

## Quick Start

### Installation
```bash
# Using pip
pip install -e .

# Using uv (recommended)
uv venv
uv pip install -e .
source .venv/bin/activate
```

### Basic Usage
```bash
# Simple analysis (uses ./inbox/ by default)
document-analyzer analyze

# Analyze custom directory
document-analyzer analyze ./legal-documents --output-dir ./results

# Detect retaliation patterns (uses ./inbox/ by default)
document-analyzer retaliation

# Version information
document-analyzer version
```

## Commands

### `analyze` - Document Analysis
Analyzes text documents to extract insights, create visualizations, and detect patterns.

```bash
document-analyzer analyze [DOCUMENTS_DIR] [OPTIONS]
```

**Options:**
- `--output-dir, -o DIR` - Output directory for results (default: analysis_output)
- `--case-id TEXT` - Case ID for evidence tracking
- `--quiet, -q` - Suppress verbose output
- `--stop-words TEXT` - Additional stop words (comma-separated)

**Examples:**
```bash
# Basic analysis (uses ./inbox/ by default)
document-analyzer analyze

# With case tracking and custom output
document-analyzer analyze --case-id "CASE-2025-001" -o ./results

# Custom directory with stop words
document-analyzer analyze ./custom-docs --quiet --stop-words "company,internal,email"
```

**Outputs:**
- `word_cloud.png` - Visual word cloud representation
- `word_frequency.png` - Bar chart of most frequent terms
- Structured JSON metadata with evidence tracking

### `retaliation` - Timeline Analysis
Specialized analysis for detecting retaliation patterns in workplace communications.

```bash
document-analyzer retaliation [DOCUMENTS_DIR] [OPTIONS]
```

**Best Results - File Naming Convention:**
Use dated filenames for timeline analysis:
- `YYYY-MM-DD-TYPE-Description-Parties.txt`
- Example: `2025-03-15-EMAIL-ComplaintResponse-JSmith-HR.txt`

**Document Types:**
- `EMAIL` - Email communications
- `LETTER` - Formal letters
- `MEMO` - Internal memos
- `MEETING` - Meeting notes
- `REPORT` - Incident reports

**Examples:**
```bash
# Analyze for retaliation patterns (uses ./inbox/ by default)
document-analyzer retaliation --case-id "RETALIATION-001"

# Custom directory with output location
document-analyzer retaliation ./dated-documents --output-dir ./timeline-analysis
```

**Outputs:**
- Timeline visualization showing escalation patterns
- Communication frequency analysis
- Retaliation risk scoring
- Statistical summary of key events

**Analysis Includes:**
- Days from initial complaint to adverse action
- Communication frequency changes
- Escalation pathway mapping
- Sentiment analysis over time
- Health impact documentation

### `ingest` - Evidence Storage
Ingests documents into content-addressed storage with forensic-grade tracking.

```bash
document-analyzer ingest [INPUT_PATH] [OPTIONS]
```

**Options:**
- `--case-id TEXT` - Case ID to associate with evidence
- `--actor TEXT` - Actor performing ingestion (default: system)
- `--evidence-root DIR` - Evidence storage directory (default: evidence)
- `--quiet, -q` - Suppress verbose output

**Examples:**
```bash
# Ingest single document
document-analyzer ingest ./important-contract.pdf --case-id "CONTRACT-2025"

# Ingest entire directory
document-analyzer ingest ./discovery-documents --case-id "LITIGATION-001"
```

**Features:**
- SHA256-based content addressing
- Automatic metadata extraction
- Chain of custody tracking
- Duplicate detection
- Evidence integrity verification

### `export` - Export Analysis
Exports validated analysis results for external use.

```bash
document-analyzer export [SHA256_HASH] [OUTPUT_FILE]
```

**Example:**
```bash
# Export analysis results
document-analyzer export a1b2c3d4e5f6... case-summary.json
```

**Output Format:**
```json
{
  "schema_version": "1.0.0",
  "case_id": "CASE-2025-001",
  "evidence": {
    "evidence_id": "doc_hash",
    "sha256": "a1b2c3d4...",
    "mime_type": "text/plain",
    "bytes": 2048,
    "ingested_at": "2025-09-25T14:30:00Z"
  },
  "analyses": [{
    "analysis_id": "analysis_id",
    "created_at": "2025-09-25T14:31:00Z",
    "model": {"name": "gpt-4o-2024-08-06"},
    "outputs": {
      "summary": "Contract termination notice with hostile language",
      "entities": [
        {"name": "ACME Corp", "type": "organization", "confidence": 0.98},
        {"name": "John Doe", "type": "person", "confidence": 0.95}
      ],
      "document_type": "letter",
      "sentiment": "hostile",
      "legal_significance": "high",
      "risk_flags": ["threatening", "deadline"],
      "confidence_overall": 0.89
    }
  }],
  "chain_of_custody": [
    {"ts": "2025-09-25T14:30:00Z", "actor": "analyst@firm.com", "action": "ingest"}
  ]
}
```

## Analysis Features

### AI-Powered Document Analysis
- **Entity Extraction**: Identifies people, organizations, dates, locations
- **Document Classification**: Email, letter, contract, filing, memo
- **Sentiment Analysis**: Hostile, neutral, professional tone detection
- **Legal Risk Flags**: PII, privileged content, threats, deadlines
- **Confidence Scoring**: Reliability metrics for all analyses

### Retaliation Pattern Detection
- **Timeline Analysis**: Visual representation of events over time
- **Escalation Tracking**: Maps complaint progression through organization
- **Communication Frequency**: Detects changes in interaction patterns
- **Health Impact Correlation**: Links stress/medical issues to workplace events
- **Statistical Metrics**: Quantitative measures of retaliation likelihood

### Evidence Management
- **Content-Addressed Storage**: Files organized by cryptographic hash
- **Chain of Custody**: Complete audit trail for legal admissibility
- **Metadata Preservation**: File system attributes and processing history
- **Schema Validation**: All outputs conform to legal evidence standards
- **Duplicate Detection**: Automatically identifies identical documents

## Inbox Workflow

### Quick Start with Inbox
The easiest way to use the Document Evidence Analyzer:

```bash
# 1. Copy your documents to the inbox
cp /path/to/case-files/*.txt inbox/

# 2. Run analysis (no paths needed!)
document-analyzer analyze --case-id "CASE-2025-001"
document-analyzer retaliation --case-id "CASE-2025-001"

# 3. Results appear in current directory
ls *.png  # word_cloud.png, word_frequency.png, timeline charts
```

The `inbox/` directory contains sample documents you can analyze immediately, or replace with your own case files.

## File Organization

### Input Documents
For best results, organize documents with descriptive names:

```
case-documents/
├── 2025-01-15-EMAIL-InitialComplaint-JSmith-HR.txt
├── 2025-01-20-EMAIL-ManagerResponse-BossMan-JSmith.txt
├── 2025-02-01-LETTER-FormalGrievance-JSmith-Legal.txt
├── 2025-02-15-MEMO-PolicyReminder-HR-AllStaff.txt
└── 2025-03-01-REPORT-IncidentReport-Security-HR.txt
```

### Output Structure
```
analysis_output/
├── word_cloud.png              # Visual word cloud
├── word_frequency.png          # Frequency bar chart
└── retaliation_analysis/       # Retaliation-specific outputs
    ├── timeline_chart.png      # Event timeline
    ├── frequency_analysis.png  # Communication patterns
    └── statistical_summary.txt # Quantitative results
```

### Evidence Storage
```
evidence/
├── raw/sha256=abc123.../       # Original documents
│   └── original.txt
├── derived/sha256=abc123.../   # Analysis results
│   ├── metadata.json
│   ├── analysis.v1.json
│   └── chain_of_custody.json
└── labels/                     # Organized by content type
    ├── email/
    ├── contracts/
    └── complaints/
```

## Best Practices

### Document Preparation
1. **Consistent Naming**: Use YYYY-MM-DD format for dates
2. **Type Indicators**: Include document type (EMAIL, LETTER, etc.)
3. **Party Identification**: Include sender/receiver in filename
4. **Text Format**: Convert PDFs to text when possible for better analysis
5. **Organization**: Group related documents in folders by case or time period

### Legal Compliance
1. **Privilege Review**: Review documents for attorney-client privilege
2. **PII Redaction**: Consider redacting sensitive personal information
3. **Chain of Custody**: Use `ingest` command for evidence requiring legal admissibility
4. **Version Control**: Maintain original document integrity
5. **Access Controls**: Restrict access to evidence directories

### Performance Optimization
1. **Batch Processing**: Analyze documents in groups rather than individually
2. **Stop Words**: Add case-specific common words to improve relevance
3. **File Size**: Large documents may need preprocessing for optimal results
4. **Rate Limiting**: AI analysis includes built-in API rate limiting

## Troubleshooting

### Common Issues
- **No dated documents**: Retaliation analysis requires files with dates in names
- **Empty results**: Check file encoding (UTF-8 recommended)
- **Permission errors**: Ensure write access to output directories
- **API failures**: Verify OpenAI API key for advanced analysis features

### Getting Help
- Check log files in output directory for detailed error messages
- Validate file formats and naming conventions
- Review CLAUDE.md for technical implementation details
- Ensure all dependencies are properly installed