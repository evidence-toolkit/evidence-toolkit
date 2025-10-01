# Evidence Toolkit - Getting Started Guide

The Evidence Toolkit provides forensic-grade analysis for legal evidence processing, supporting both document and image analysis with content-addressed storage and chain of custody tracking.

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for image analysis and advanced document features)

### Installation

**Prerequisites:**
- Python 3.8+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- OpenAI API key for image analysis

**Method 1: Using uv (Recommended)**
```bash
# Document Analysis
cd document-evidence-analyzer
uv sync && uv pip install -e .

# Image Analysis
cd ../image-analysis
uv sync && uv pip install -e .
export OPENAI_API_KEY="your-api-key-here"
```

**Method 2: Using pip/venv**
```bash
# Document Analysis
cd document-evidence-analyzer
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Image Analysis
cd ../image-analysis
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
export OPENAI_API_KEY="your-api-key-here"
```

## Document Analysis

### Basic Document Analysis
The simplest way to analyze documents:

```bash
cd document-evidence-analyzer/

# Basic analysis (uses inbox/ by default)
document-analyzer analyze

# With custom output directory
document-analyzer analyze --output-dir ./results

# Or analyze custom directory
document-analyzer analyze /path/to/documents --output-dir ./results
```

**Output:**
- Word cloud visualization (`word_cloud.png`)
- Frequency chart (`word_frequency.png`)
- Structured metadata and chain of custody (JSON files)

### Retaliation Pattern Analysis
Detect workplace retaliation patterns in dated documents:

```bash
cd document-evidence-analyzer/

# Analyze retaliation patterns (uses inbox/ by default)
document-analyzer retaliation

# With custom output directory
document-analyzer retaliation --output-dir ./timeline-analysis
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
cd image-analysis/

# 1. Ingest images (uses inbox/ by default)
uv run image-analyzer ingest --case-id "CASE-2025-001"

# 2. Analyze specific image by SHA256 hash
uv run image-analyzer analyze <sha256-hash>

# 3. Batch analysis of all ingested images
uv run image-analyzer analyze-batch --limit 10 --skip-existing

# 4. Export analysis results
uv run image-analyzer export-json <sha256-hash> report.json
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
   cd document-evidence-analyzer/
   # Copy case documents to inbox/
   document-analyzer analyze --case-id "CASE-2025-001"
   ```

2. **Process Images:**
   ```bash
   cd ../image-analysis/
   # Copy case images to inbox/
   uv run python -m image_analysis.cli ingest --case-id "CASE-2025-001"
   uv run python -m image_analysis.cli analyze-batch --skip-existing
   ```

3. **Both tools use the same case ID and compatible evidence storage**

### Legal Team Workflow

**Simplified Inbox Workflow:**
```bash
# 1. Drop evidence files into inboxes
cp case-documents/* document-evidence-analyzer/inbox/
cp case-photos/* image-analysis/inbox/

# 2. Run analysis (no paths needed!)
cd document-evidence-analyzer/
document-analyzer analyze --case-id "CASE-2025-001"
document-analyzer retaliation --case-id "CASE-2025-001"

cd ../image-analysis/
uv run python -m image_analysis.cli ingest --case-id "CASE-2025-001"
uv run python -m image_analysis.cli analyze-batch
```

**Traditional Workflow:**
1. **Bulk Document Processing:**
   - Place documents in organized folders
   - Run `document-analyzer analyze /path/to/docs` for overview
   - Run `document-analyzer retaliation /path/to/docs` for timeline analysis

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

## Troubleshooting

### Installation Issues

**"externally-managed-environment" Error:**
```bash
# Use virtual environment instead of system Python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**"python3-venv not available" Error:**
```bash
# Ubuntu/Debian systems
sudo apt install python3.12-venv python3-pip

# Then retry installation
```

**"uv not found" Error:**
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal, then retry
```

### Runtime Issues

**No sample files in inbox:**
```bash
# Copy examples to inbox directories
cp examples/sample-documents/* document-evidence-analyzer/inbox/
cp examples/sample-images/* image-analysis/inbox/
```

**OpenAI API errors:**
- Verify your API key is set: `echo $OPENAI_API_KEY`
- Check API key permissions at https://platform.openai.com/api-keys

**Image analysis "UNIQUE constraint failed" errors:**
```bash
# Reset the database to clear old analysis data
cd image-analysis
./scripts/reset_database.sh
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the USER_GUIDE.md in each component directory
- Validate your environment setup and API keys