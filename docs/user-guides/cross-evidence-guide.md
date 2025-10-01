# Cross-Evidence Analysis User Guide

Correlate entities, timelines, and patterns across multiple evidence types for comprehensive legal analysis.

## Overview

Cross-evidence analysis enables you to:
- **Entity Correlation**: Find people, organizations, and concepts across documents, emails, and images
- **Timeline Reconstruction**: Build chronological narratives from mixed evidence types
- **Pattern Detection**: Identify relationships and communication flows
- **Professional Reporting**: Generate client-ready analysis packages

## Supported Evidence Types

- **Documents**: Text files, PDFs, legal filings
- **Emails**: .eml, .msg, .mbox files with thread analysis
- **Images**: Photographs, screenshots, scanned documents
- **Mixed Cases**: Any combination of the above

## Getting Started

### 1. Ingest Evidence

```bash
# Ingest mixed evidence types
document-analyzer ingest ./case-files --case-id CASE123
```

This processes all evidence types automatically and stores them in content-addressed format.

### 2. Analyze Correlations

```bash
# Find entity correlations across all evidence
document-analyzer correlate --case-id CASE123
```

### 3. Generate Timeline

Timeline reconstruction happens automatically during correlation analysis, showing:
- Evidence creation timestamps
- Analysis completion times
- Event sequences across evidence types

### 4. Create Professional Package

```bash
# Generate client deliverable
document-analyzer package --case-id CASE123 --output-dir ./client-packages --format zip
```

## Real Example: CORRELATION_TEST Case

Here's an actual working example from the Evidence Toolkit:

### Evidence Processed
```
Document Evidence:
- File: test_document.txt
- SHA256: 692df64a...
- Analysis: 52 words, themes: safety, john, manager, january, workplace

Email Evidence:
- File: test_email2.eml
- SHA256: 7352e3cd...
- Analysis: 3 participants, professional communication
```

### Correlation Results
```json
{
  "entity_correlations": [
    {
      "entity_name": "John",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "confidence_average": 0.60,
      "evidence_pieces": ["692df64a", "7352e3cd"]
    },
    {
      "entity_name": "Sarah",
      "entity_type": "person_name",
      "occurrence_count": 2,
      "confidence_average": 0.60,
      "evidence_pieces": ["692df64a", "7352e3cd"]
    }
  ]
}
```

### Timeline Reconstruction
```
2025-09-28 14:31:47 - Document created (test_document.txt)
2025-09-28 14:31:55 - Email created (test_email2.eml)
2025-09-28 14:32:43 - Document AI analysis completed
2025-09-28 14:32:58 - Email AI analysis completed
2025-09-28 14:59:23 - Cross-evidence correlation performed
```

## Analysis Features

### Entity Correlation
- **Person Names**: John, Sarah, management personnel
- **Organizations**: Companies, departments, external entities
- **Concepts**: Projects, incidents, locations
- **Confidence Scoring**: Average confidence across evidence types

### Timeline Analysis
- **File Creation**: When evidence was originally created
- **Analysis Timestamps**: When AI processing occurred
- **Event Sequencing**: Logical flow of evidence creation
- **Gap Detection**: Missing time periods in evidence

### Professional Reporting
Generated packages include:
- **Executive Summary**: AI-powered legal significance assessment
- **Individual Evidence Analysis**: Detailed analysis per evidence piece
- **Cross-Evidence Correlation**: Entity relationships and timelines
- **Evidence Catalog**: Complete forensic metadata
- **Professional Documentation**: Methodology and legal compliance

## Python API

```python
from document_analyzer.correlation_analyzer import CorrelationAnalyzer
from document_analyzer.evidence_manager import EvidenceManager

# Initialize
manager = EvidenceManager()
analyzer = CorrelationAnalyzer(manager)

# Analyze case correlations
results = analyzer.analyze_case_correlations("CASE123")

# Access correlation data
for correlation in results.entity_correlations:
    print(f"{correlation.entity_name}: {correlation.occurrence_count} occurrences")

# Access timeline
for event in results.timeline_events:
    print(f"{event.timestamp}: {event.description}")
```

## Schema Architecture

Cross-evidence analysis uses a 3-tier schema system:

### Tier 1: Individual Evidence
- `document.v1.json` - Document analysis schema
- `images.v1.json` - Image analysis schema
- Email analysis (UnifiedAnalysis format)

### Tier 2: Cross-Evidence
- `cross-analysis.v1.json` - Multi-evidence correlation schema
- Entity correlation results
- Timeline reconstruction
- Pattern analysis

### Tier 3: Case-Level
- Complete case aggregation
- Professional client deliverables
- Executive summaries

## Legal Compliance

### Forensic Integrity
- **Content-addressed storage** with SHA256 verification
- **Chain of custody tracking** for all correlation operations
- **Schema validation** for legal admissibility
- **Deterministic analysis** for reproducible expert testimony

### Professional Standards
- Federal Rules of Evidence compliance
- Expert testimony support documentation
- Complete audit trail for legal proceedings
- Cryptographic validation of evidence integrity

## Advanced Features

### Entity Resolution
- Fuzzy matching for name variants
- Context-based disambiguation
- Relationship mapping between entities
- Confidence scoring across evidence types

### Pattern Detection
- Communication flows across email threads
- Document reference chains
- Temporal clustering of related events
- Workflow reconstruction from mixed evidence

### Custom Analysis
The correlation engine supports custom entity extraction and analysis algorithms for specialized legal contexts.

For detailed schema reference and development information, see `docs/api/schema-reference.md`.