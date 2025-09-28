# Evidence Toolkit Examples

This directory contains comprehensive sample data for testing and demonstrating the Evidence Toolkit components.

## 📁 Sample Data Organization

### 📄 Sample Documents (`sample-documents/`)

Professional legal document examples demonstrating a typical workplace harassment case progression:

- `2025-01-15-EMAIL-ComplaintInitial-JSmith-HR.txt` - Initial harassment complaint
- `2025-01-20-LETTER-PolicyViolation-HR-JSmith.txt` - HR response with policy citations
- `2025-02-01-MEMO-InvestigationUpdate-Legal-Management.txt` - Internal legal memo
- `2025-02-15-EMAIL-EscalationResponse-CEO-Legal.txt` - Executive decision communication
- `2025-03-01-LETTER-Resolution-Legal-JSmith.txt` - Settlement agreement letter

**Features demonstrated:**
- Proper naming conventions for timeline analysis
- Realistic legal language and escalation patterns
- Retaliation detection capabilities
- Cross-document entity correlation

### 📧 Sample Emails (`sample-emails/`)

Email communication examples showing workplace safety investigation:

- `test.eml` - Basic email structure for testing
- `2025-01-16-EMAIL-ComplaintResponse-HR-JSmith.eml` - HR response to safety complaint
- `2025-01-22-EMAIL-FollowUp-SJohnson-JSmith.eml` - Safety compliance follow-up

**Features demonstrated:**
- Email thread analysis and participant identification
- Cross-evidence entity correlation (John, Sarah appear in both emails and documents)
- Professional communication pattern detection
- Timeline reconstruction capabilities

### 📄 Sample PDFs (`sample-pdfs/`)

- `legal_document.pdf` - Simple PDF for testing document processing

**Features demonstrated:**
- PDF text extraction and analysis
- Document classification and processing

### 🖼️ Sample Images (`sample-images/`)

Coming soon - safe sample images for testing visual analysis capabilities.

### 🔗 Cross-Analysis Example (`cross-analysis-example.json`)

Complete example of cross-evidence analysis output showing:
- Entity correlations across multiple evidence types
- Timeline reconstruction
- Narrative consistency analysis
- Risk assessment results

## 🚀 Usage Examples

### Basic Document Analysis
```bash
# Analyze sample documents
document-analyzer analyze examples/sample-documents --output-dir ./results

# Timeline analysis for retaliation patterns
document-analyzer retaliation examples/sample-documents --output-dir ./timeline-analysis
```

### Email Analysis
```bash
# Analyze email communications
document-analyzer email examples/sample-emails --case-id DEMO_CASE --output-dir ./email-analysis
```

### Cross-Evidence Correlation
```bash
# Ingest all sample evidence
document-analyzer ingest examples/sample-documents --case-id DEMO_CASE
document-analyzer ingest examples/sample-emails --case-id DEMO_CASE

# Find correlations across evidence types
document-analyzer correlate --case-id DEMO_CASE

# Generate comprehensive case summary
document-analyzer summary --case-id DEMO_CASE --ai-summary

# Create professional client package
document-analyzer package --case-id DEMO_CASE --output-dir ./client-packages --format zip
```

### Image Analysis
```bash
# Ingest sample images (when available)
cd image-analysis
uv run python -m image_analysis.cli ingest ../examples/sample-images --case-id DEMO_CASE

# Analyze images
uv run python -m image_analysis.cli analyze-batch --skip-existing --limit 5
```

## 📊 Expected Results

### Document Analysis Output
- **Word clouds** highlighting key terms (complaint, investigation, harassment, safety)
- **Frequency analysis** showing legal terminology patterns
- **Timeline visualization** showing escalation from initial complaint to resolution
- **Entity extraction** identifying people, organizations, and key concepts

### Email Analysis Output
- **Thread reconstruction** showing communication flow
- **Participant identification** and relationship mapping
- **Escalation detection** in communication patterns
- **Professional vs informal communication classification**

### Cross-Evidence Correlation
- **Entity correlation** finding "John" and "Sarah" across documents and emails
- **Timeline reconstruction** showing evidence creation and analysis chronology
- **Professional summary** with AI-powered legal significance assessment
- **Client deliverable** package with reports, analysis, and documentation

### Sample Correlation Results
```json
{
  "entity_correlations": [
    {
      "entity_name": "John",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "evidence_pieces": ["documents", "emails"]
    },
    {
      "entity_name": "Sarah",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "evidence_pieces": ["documents", "emails"]
    }
  ]
}
```

## 🎯 Learning Objectives

These samples demonstrate:

1. **Forensic Evidence Processing**: Content-addressed storage with SHA256 verification
2. **AI-Powered Analysis**: Deterministic analysis using OpenAI Responses API
3. **Cross-Evidence Intelligence**: Entity correlation across multiple evidence types
4. **Professional Deliverables**: Client-ready analysis packages for legal use
5. **Legal Compliance**: Chain of custody tracking and schema validation
6. **Timeline Reconstruction**: Chronological analysis of evidence and events

## 🔧 File Naming Conventions

For best results with your own evidence, follow these patterns:

**Documents & Emails:**
- `YYYY-MM-DD-TYPE-Description-Parties.ext`
- Example: `2025-03-15-EMAIL-ComplaintFollowUp-JSmith-HR.eml`

**Images:**
- Descriptive names help with analysis
- Include dates when possible
- Example: `2025-01-15-screenshot-complaint-submission.png`

## 🛡️ Data Safety

All sample data contains:
- **Fictional characters and scenarios**
- **Generic legal language and patterns**
- **No real personal or confidential information**
- **Safe for demonstration and testing purposes**

For real evidence processing, the toolkit maintains:
- **Complete chain of custody tracking**
- **Immutable content-addressed storage**
- **Schema validation for legal admissibility**
- **Professional audit trails**

These samples provide a complete foundation for understanding and testing the Evidence Toolkit's capabilities while maintaining the highest standards of forensic integrity.