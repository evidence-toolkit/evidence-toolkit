# Evidence Toolkit - Getting Started Guide

The Evidence Toolkit provides forensic-grade analysis for legal evidence processing, supporting both document and image analysis with content-addressed storage and chain of custody tracking.

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for image analysis and advanced document features)

### Installation

**Document Analysis:**
```bash
cd document-evidence-analyzer
pip install -e .
# OR
uv venv && uv pip install -e .
```

**Image Analysis:**
```bash
cd image-analysis
uv sync
export OPENAI_API_KEY="your-api-key-here"
```

## Document Analysis

### Basic Document Analysis
Analyze a folder of legal documents:

```bash
# Basic analysis using provided samples
document-analyzer analyze examples/sample-documents --output-dir ./results

# Analyze with custom case ID
document-analyzer analyze examples/sample-documents --case-id "CASE-2025-001" --output-dir ./results
```

**Output:**
- Word cloud visualization (`word_cloud.png`)
- Frequency chart (`word_frequency.png`)
- Structured metadata and chain of custody (JSON files)

### Retaliation Pattern Analysis
Detect workplace retaliation patterns in dated documents:

```bash
# Analyze retaliation patterns (requires dated filenames)
document-analyzer retaliation examples/sample-documents --output-dir ./retaliation-results
```

**Naming Convention for Best Results:**
- `YYYY-MM-DD-TYPE-Description-Parties.txt`
- Example: `2025-03-15-EMAIL-ComplaintFollowUp-JSmith-HR.txt`

**Output:**
- Timeline analysis with escalation patterns
- Communication frequency charts
- Retaliation risk scores and statistics

### Evidence Storage Mode
Process documents with forensic-grade evidence tracking:

```bash
# Ingest documents into content-addressed storage
document-analyzer ingest ./documents --case-id "CASE-2025-001"

# Export analysis results
document-analyzer export <sha256-hash> analysis-report.json
```

## Image Analysis

### Forensic Image Processing
Process images with AI-powered analysis and content-addressed storage:

```bash
# 1. Ingest images into evidence storage
uv run python -m image_analysis.cli ingest examples/sample-images --case-id "CASE-2025-001"

# 2. Analyze specific image by SHA256 hash
uv run python -m image_analysis.cli analyze <sha256-hash>

# 3. Batch analysis of all ingested images
uv run python -m image_analysis.cli analyze-batch --limit 10 --skip-existing

# 4. Export analysis results
uv run python -m image_analysis.cli export-json <sha256-hash> report.json
```

**AI Analysis Features:**
- Object and text detection with bounding boxes
- Scene description and context analysis
- Risk assessment and confidence scoring
- Deterministic results (temperature=0)

## Common Workflows

### Mixed Evidence Cases
For cases with both documents and images:

1. **Process Documents:**
   ```bash
   document-analyzer analyze examples/sample-documents --case-id "CASE-2025-001"
   ```

2. **Process Images:**
   ```bash
   uv run python -m image_analysis.cli ingest examples/sample-images --case-id "CASE-2025-001"
   uv run python -m image_analysis.cli analyze-batch --skip-existing
   ```

3. **Both tools use the same case ID and compatible evidence storage**

### Legal Team Workflow
1. **Bulk Document Processing:**
   - Place documents in organized folders
   - Run `document-analyzer analyze` for overview
   - Run `document-analyzer retaliation` for timeline analysis

2. **Evidence Preservation:**
   - Use `ingest` commands for forensic-grade storage
   - Chain of custody automatically tracked
   - All operations logged with timestamps

3. **Export for Legal Review:**
   - Export analysis results as JSON
   - Include chain of custody for admissibility
   - Generated visualizations ready for presentations

## Output Formats

### Document Analysis Results
```json
{
  "schema_version": "1.0.0",
  "case_id": "CASE-2025-001",
  "evidence": {
    "evidence_id": "doc_sha256_hash",
    "mime_type": "text/plain",
    "bytes": 2048,
    "ingested_at": "2025-09-25T14:30:00Z"
  },
  "analyses": [{
    "summary": "Employment termination email with hostile tone",
    "entities": [
      {"name": "John Doe", "type": "person", "confidence": 0.95}
    ],
    "document_type": "email",
    "sentiment": "hostile",
    "risk_flags": ["threatening", "deadline"]
  }],
  "chain_of_custody": [
    {"ts": "2025-09-25T14:30:00Z", "actor": "analyst@firm.com", "action": "ingest"}
  ]
}
```

### Image Analysis Results
```json
{
  "schema_version": "1.0.0",
  "case_id": "CASE-2025-001",
  "evidence": {
    "sha256": "image_sha256_hash",
    "mime_type": "image/jpeg",
    "width_px": 1920,
    "height_px": 1080
  },
  "analyses": [{
    "outputs": {
      "summary": "Office scene showing computer screen with confidential document",
      "objects": [
        {"label": "computer", "bbox": [100, 200, 300, 400], "confidence": 0.95}
      ],
      "risk_flags": ["sensitive_content"],
      "confidence_overall": 0.89
    }
  }]
}
```

## Environment Variables

**Required for Image Analysis:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional Configuration:**
- `EVIDENCE_TOOLKIT_MODEL` - Default: "gpt-4.1-mini"
- `EVIDENCE_TOOLKIT_MODEL_REVISION` - Default: "2025-09-10"

## Tips for Best Results

### Document Analysis
- Use consistent date formats in filenames (YYYY-MM-DD)
- Include document type indicators (EMAIL, LETTER, CONTRACT)
- Organize by case or matter for easier batch processing

### Image Analysis
- Supported formats: PNG, JPEG, GIF, BMP
- Higher resolution images provide better analysis
- Group related images in same directory for batch processing

### Evidence Management
- Use meaningful case IDs for organization
- Content-addressed storage prevents data corruption
- Chain of custody is automatically maintained for legal admissibility

## Support

For issues or questions:
- Check the README files in each component directory
- Review the CLAUDE.md files for technical details
- Validate your environment setup and API keys