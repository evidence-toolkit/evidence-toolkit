# Evidence Toolkit

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991.svg)](https://openai.com/)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-Compliant-green.svg)](#legal-compliance)

**Forensic-grade evidence analysis platform for legal professionals**

The Evidence Toolkit is a comprehensive suite for legal evidence processing, providing AI-powered analysis across documents, emails, and images with content-addressed storage, cross-evidence correlation, and professional client deliverables.

## 🎯 Core Features

- **Document Analysis**: Text processing, entity extraction, sentiment analysis
- **Email Thread Analysis**: Communication pattern detection, escalation analysis
- **Image Analysis**: Forensic image processing with OCR and visual AI
- **Cross-Evidence Correlation**: Entity matching and timeline reconstruction across evidence types
- **Professional Deliverables**: AI-powered executive summaries and client packages
- **Forensic Integrity**: Content-addressed storage with SHA256 verification
- **Legal Compliance**: Chain of custody tracking and schema validation

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit/document-evidence-analyzer
uv venv && uv pip install -e .
export OPENAI_API_KEY="your-api-key"
```

### Basic Usage

```bash
# Analyze documents
document-analyzer analyze ./documents --case-id CASE123

# Process emails
document-analyzer email ./emails --case-id CASE123

# Cross-evidence correlation
document-analyzer correlate --case-id CASE123

# Generate client package
document-analyzer package --case-id CASE123 --format zip
```

## 📊 Real Example: Multi-Evidence Case

Here's what the toolkit found in an actual test case:

```bash
# Evidence processed:
# - Document: test_document.txt (workplace safety memo)
# - Email: test_email2.eml (safety review discussion)

# Correlations found:
# - "John" appears in both document and email
# - "Sarah" appears in both document and email
# - Timeline reconstructed from file creation to analysis
```

**Output**: Professional ZIP package with executive summary, correlation analysis, timeline reconstruction, and forensic documentation.

## 📁 Architecture

### Evidence Storage
```
evidence/derived/sha256=<hash>/
├── analysis.v1.json        # Internal working format
├── evidence_bundle.v1.json # Schema-compliant forensic bundle
├── metadata.json           # File metadata
└── chain_of_custody.json   # Complete audit trail
```

### Schema System
- **Individual Evidence**: `document.v1.json`, `images.v1.json`
- **Cross-Evidence**: `cross-analysis.v1.json` for correlation
- **Case-Level**: Professional client deliverable schemas

## 📚 Documentation

### User Guides
- [Document Analyzer Guide](docs/user-guides/document-analyzer-guide.md)
- [Image Analysis Guide](docs/user-guides/image-analysis-guide.md)
- [Cross-Evidence Analysis Guide](docs/user-guides/cross-evidence-guide.md)

### API Reference
- [Schema Reference](docs/api/schema-reference.md)

### Development
- [Getting Started](docs/development/GETTING_STARTED.md)
- [AUDHD Developer Guide](docs/development/AUDHD_DEV_GUIDE.md)

## 🔧 Components

### Document Evidence Analyzer
Advanced text analysis with legal document processing:
- Word frequency analysis with legal filters
- AI-powered entity extraction and sentiment analysis
- Email thread reconstruction and escalation detection
- Content-addressed evidence storage

### Image Analysis
Forensic-grade image processing:
- Content-addressed storage with SHA256 verification
- AI visual analysis with OpenAI Responses API
- OCR text extraction and scene description
- Perceptual hashing for duplicate detection

### Cross-Evidence Correlation
Multi-evidence analysis capabilities:
- Entity correlation across document, email, and image evidence
- Timeline reconstruction from mixed evidence types
- Professional case summary generation
- Client-ready deliverable packages

## ⚖️ Legal Compliance

### Forensic Standards
- **Content-addressed storage** prevents evidence tampering
- **Chain of custody tracking** for all operations
- **Deterministic AI analysis** for reproducible results
- **Schema validation** ensures legal admissibility

### Professional Use
- Federal Rules of Evidence compliance
- Expert testimony support documentation
- Complete audit trail for legal proceedings
- GDPR-compliant data processing

## 🛠️ Development

### Prerequisites
- Python 3.8+ (3.12+ recommended for image analysis)
- OpenAI API key for AI analysis
- [uv](https://github.com/astral-sh/uv) for dependency management

### Component Development
```bash
# Document analyzer
cd document-evidence-analyzer
uv venv && uv pip install -e .

# Image analysis
cd image-analysis
uv sync
```

### Testing
```bash
# Validate schema compliance
python validate_cross_analysis.py --comprehensive

# Component-specific validation
cd document-evidence-analyzer && python -m pytest tests/
cd image-analysis && scripts/validate_analyses.sh
```

## 📈 Professional Services

The Evidence Toolkit enables professional legal consulting services:
- **Case Analysis**: $50-500 per case depending on complexity
- **Expert Testimony**: Reproducible, court-ready analysis
- **Training Services**: Legal team onboarding and best practices
- **Custom Development**: Specialized analysis for unique legal contexts

## 🤝 Contributing

Contributions welcome! Please see our development guides:
- [Getting Started](docs/development/GETTING_STARTED.md)
- [AUDHD Developer Guide](docs/development/AUDHD_DEV_GUIDE.md)

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- [Documentation](docs/)
- [Issue Tracker](https://github.com/evidence-toolkit/evidence-toolkit/issues)
- [OpenAI Responses API](https://platform.openai.com/docs/guides/function-calling)

---

*Built with forensic integrity and legal compliance in mind. Designed for professional legal evidence analysis.*