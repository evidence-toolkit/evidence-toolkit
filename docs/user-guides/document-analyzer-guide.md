# Document Evidence Analyzer User Guide

A powerful Python tool for analyzing text documents and generating visualizations for legal evidence processing.

## Features

- **Text Analysis**: Advanced natural language processing for legal documents
- **Email Thread Analysis**: AI-powered analysis of email communications with escalation detection
- **Word Cloud Generation**: Create compelling visual representations of document themes
- **Frequency Analysis**: Statistical analysis of word patterns and frequency distributions
- **Legal Document Processing**: Specialized filters for business and legal correspondence
- **Batch Processing**: Analyze entire directories of documents efficiently
- **Evidence Storage**: Content-addressed storage with SHA256 hashing for forensic integrity
- **Cross-Evidence Correlation**: Link entities and timelines across multiple documents

## Installation

### Requirements
- Python 3.8 or higher
- pip or uv for package management

### Install from Source
```bash
cd document-evidence-analyzer
uv venv
uv pip install -e .
```

## Quick Start

### Command Line Usage

#### Basic Document Analysis
```bash
# Analyze documents in a directory
document-analyzer analyze ./documents

# Save results to specific output directory
document-analyzer analyze ./documents -o ./analysis-results

# Analyze with custom stop words
document-analyzer analyze ./documents --stop-words "company,internal"
```

#### Email Analysis
```bash
# Analyze email threads for legal patterns
document-analyzer email ./emails --case-id CASE123

# Email analysis with escalation detection
document-analyzer email ./emails --case-id CASE123 --output-dir ./email-analysis
```

#### Evidence Storage and Correlation
```bash
# Ingest evidence into content-addressed storage
document-analyzer ingest ./evidence-files --case-id CASE123

# Analyze correlations across evidence types
document-analyzer correlate --case-id CASE123

# Generate comprehensive case summary
document-analyzer summary --case-id CASE123 --ai-summary
```

#### Client Deliverables
```bash
# Create professional client package
document-analyzer package --case-id CASE123 --output-dir ./client-packages --format zip
```

## Evidence Storage

The document analyzer uses content-addressed storage for forensic integrity:

```
evidence/derived/sha256=<hash>/
├── analysis.v1.json        # Internal working format
├── evidence_bundle.v1.json # Schema-compliant forensic bundle
├── metadata.json           # File metadata
└── chain_of_custody.json   # Complete audit trail
```

## Python API

```python
from document_analyzer import DocumentAnalyzer, analyze_documents

# Basic analysis
analyzer = DocumentAnalyzer()
results = analyzer.analyze_directory("./documents")

# With evidence storage
from document_analyzer.evidence_manager import EvidenceManager

manager = EvidenceManager()
result = manager.ingest_file("document.txt", case_id="CASE123")
analysis = manager.analyze_evidence(result.sha256)
```

## Analysis Types

### Word Frequency Analysis
- Statistical analysis of word patterns
- Legal document filtering
- Custom stop word lists
- Frequency distribution charts

### Email Thread Analysis
- Participant identification
- Communication patterns
- Escalation detection
- Timeline reconstruction

### Cross-Evidence Correlation
- Entity matching across documents
- Timeline analysis
- Professional relationship mapping
- Case narrative construction

## Output Formats

### Visual Outputs
- Word clouds (PNG/SVG)
- Frequency charts
- Timeline visualizations

### Data Outputs
- JSON analysis results
- CSV frequency data
- Schema-compliant evidence bundles
- Professional client packages

## Legal Compliance

The document analyzer maintains forensic-grade standards:
- **Content-addressed storage** with SHA256 verification
- **Chain of custody tracking** for all operations
- **Schema validation** for legal admissibility
- **Deterministic AI analysis** for reproducible results

For advanced usage and API documentation, see the source code documentation.