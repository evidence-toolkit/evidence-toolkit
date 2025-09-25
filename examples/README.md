# Evidence Toolkit Examples

This directory contains sample data for testing the Evidence Toolkit components.

## Sample Documents (`sample-documents/`)

Professional legal document examples demonstrating typical workplace harassment case progression:

- `2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt` - Initial harassment complaint
- `2025-01-20-LETTER-PolicyViolation-HR-JSmith.txt` - HR response with policy citations
- `2025-02-01-MEMO-InvestigationUpdate-Legal-Management.txt` - Internal legal memo
- `2025-02-15-EMAIL-EscalationResponse-CEO-Legal.txt` - Executive decision communication
- `2025-03-01-LETTER-Resolution-Legal-JSmith.txt` - Settlement agreement letter

These documents follow proper naming conventions for timeline analysis:
- `YYYY-MM-DD-TYPE-Description-Parties.txt`
- Include realistic legal language and escalation patterns
- Demonstrate retaliation detection capabilities

## Sample Images (`sample-images/`)

- `office-screenshot.png` - Computer screen capture showing development environment

## Usage Examples

### Document Analysis
```bash
# Basic analysis
document-analyzer analyze examples/sample-documents --output-dir ./results

# Retaliation timeline analysis
document-analyzer retaliation examples/sample-documents --output-dir ./timeline-analysis
```

### Image Analysis
```bash
# Ingest sample images
uv run python -m image_analysis.cli ingest examples/sample-images --case-id "DEMO-2025"

# Analyze (replace <hash> with actual SHA256)
uv run python -m image_analysis.cli analyze <hash>
```

## Expected Results

**Document Analysis:**
- Word clouds highlighting key terms (complaint, investigation, harassment, etc.)
- Frequency analysis showing legal terminology patterns
- Timeline visualization showing escalation from initial complaint to resolution

**Image Analysis:**
- Object detection for computer equipment, documents, text content
- OCR extraction of any visible text
- Scene analysis describing office/workplace environment
- Risk flags for sensitive content or confidential information

These samples demonstrate the toolkit's capability to process real-world legal evidence while maintaining professional standards for forensic analysis.