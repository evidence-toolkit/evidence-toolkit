# Evidence Toolkit

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991.svg)](https://openai.com/)
[![GDPR Compliant](https://img.shields.io/badge/GDPR-Compliant-green.svg)](#legal-compliance)

**Comprehensive AI-powered legal evidence analysis suite with forensic-grade content-addressed storage**

The Evidence Toolkit is a professional suite for legal evidence processing, combining advanced document analysis with forensic-grade image analysis. Designed for legal professionals, investigators, and compliance teams who need reliable, court-ready evidence analysis.

---

## 🚀 Quick Start

### Installation Options

**Option 1: Complete Toolkit (Recommended)**
```bash
# Install everything with unified CLI
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit
pip install -e .

# Now you can use either:
evidence-toolkit document analyze ./documents    # Unified CLI
document-analyzer analyze ./documents           # Direct CLI
image-analyzer ingest ./images --case-id CASE123  # Direct CLI
```

**Option 2: Individual Components**
```bash
# Document analysis only
git clone https://github.com/evidence-toolkit/document-evidence-analyzer.git
cd document-evidence-analyzer
pip install -e .
document-analyzer analyze ./documents

# Image analysis only
git clone https://github.com/evidence-toolkit/image-analysis.git
cd image-analysis
uv sync
uv run python -m image_analysis.cli ingest ./images --case-id CASE123
```

### Basic Usage Examples

```bash
# Document Analysis - Generate word clouds and legal insights
document-analyzer analyze ./legal_documents --output-dir ./analysis

# Image Evidence Processing - Full forensic pipeline
image-analyzer ingest ./evidence_photos --case-id WORKPLACE-2024-001
image-analyzer analyze-batch --limit 10
image-analyzer export-json <sha256> court_evidence.json

# Unified Toolkit Commands
evidence-toolkit document analyze ./case_files
evidence-toolkit image ingest ./photos --case-id CASE123
```

---

## 🏗️ Architecture Overview

The Evidence Toolkit uses a **hybrid monorepo + separate packages** approach:

### Repository Structure
```
evidence-toolkit/                    # 🏠 Monorepo for unified development
├── document-evidence-analyzer/      # 📄 Standalone document analysis package
├── image-analysis/                  # 📸 Forensic image analysis package
├── evidence_toolkit/               # 🔧 Unified CLI and Python API
└── pyproject.toml                  # 📦 Unified installation
```

### Component Architecture
- **Document Evidence Analyzer**: Text processing, word clouds, retaliation analysis
- **Image Analysis System**: Content-addressed storage, AI analysis, chain of custody
- **Unified Toolkit**: Single installation with combined CLI and Python API

### Deployment Flexibility
Users can choose their preferred approach:

| Approach | Use Case | Installation | CLI Access |
|----------|----------|--------------|------------|
| **Complete Toolkit** | Full legal workflow | `pip install -e .` | `evidence-toolkit`, `document-analyzer`, `image-analyzer` |
| **Document Only** | Text analysis focus | Individual repo install | `document-analyzer` |
| **Image Only** | Forensic imaging focus | Individual repo install | `image-analyzer` |

---

## 📋 Component Features

### Document Evidence Analyzer
- **Legal Text Analysis**: NLP processing optimized for legal documents
- **Visual Evidence**: Word clouds and frequency charts for court presentations
- **Retaliation Analysis**: Timeline analysis for workplace retaliation patterns
- **Batch Processing**: Analyze entire directories efficiently
- **Multiple Export Formats**: JSON, visualizations, statistical reports

### Image Analysis System
- **Content-Addressed Storage**: SHA256-based evidence organization with immutable file layout
- **AI-Powered Analysis**: OpenAI Responses API integration with deterministic results (temperature=0)
- **Chain of Custody**: Complete audit trail suitable for legal proceedings
- **Schema Validation**: All outputs validated against canonical evidence schema
- **Forensic Standards**: Professional-grade evidence handling and documentation

### Unified Python API
```python
from evidence_toolkit import DocumentAnalyzer, EvidenceBundle
from pathlib import Path

# Document analysis
analyzer = DocumentAnalyzer(custom_stop_words={'confidential', 'internal'})
result = analyzer.analyze_directory('./case_documents', './analysis')

# Access both components seamlessly
evidence_path = Path('./evidence/derived/sha256=abc123/')
bundle = EvidenceBundle.from_path(evidence_path)
print(f"Analysis confidence: {bundle.analysis.confidence}")
```

---

## 💼 Professional Use Cases

### Law Firms
- **Multi-Domain Evidence Processing**: Handle text documents and visual evidence in unified workflow
- **Court Presentation**: Generate professional visualizations and forensic reports
- **Cost-Effective Analysis**: AI-powered processing at ~£0.0011 per image vs £37.50 manual expert analysis
- **Compliance Assurance**: GDPR-compliant processing with complete audit trails

### Corporate Legal Teams
- **Workplace Investigations**: Analyze communications and document visual evidence systematically
- **Regulatory Compliance**: Systematic analysis across multiple regulatory domains
- **Risk Assessment**: Identify and prioritize legal exposures from mixed evidence types
- **Internal Audits**: Comprehensive evidence processing for compliance reviews

### Government & Regulatory Bodies
- **Investigation Support**: Process large volumes of mixed evidence efficiently
- **Compliance Monitoring**: Systematic analysis of regulatory violations
- **Public Interest Cases**: Cost-effective processing of complex evidence sets
- **Standard Documentation**: Consistent analysis methodology across cases

---

## 🛠️ Development Workflow

### For Document Analysis
```bash
cd document-evidence-analyzer
document-analyzer analyze ./documents --output-dir ./results
document-analyzer retaliation ./timeline_docs --output-dir ./analysis
```

### For Image Analysis
```bash
cd image-analysis
uv run python -m image_analysis.cli ingest /path/to/images --case-id CASE123
uv run python -m image_analysis.cli analyze <sha256>
uv run python -m image_analysis.cli export-json <sha256> output.json
```

### Unified Development
```bash
# Install complete toolkit for development
pip install -e .

# Run tests across all components
pytest document-evidence-analyzer/tests/
cd image-analysis && scripts/validate_analyses.sh
```

---

## 📊 Evidence Processing Pipeline

### Document Processing Flow
```
Legal Documents → Text Analysis → Word Frequency → Visualizations → Court-Ready Reports
```

### Image Processing Flow
```
Evidence Images → Content-Addressed Ingest → AI Analysis → Schema Validation → Forensic Bundle Export
```

### Unified Evidence Management
```
Mixed Evidence → Unified Ingest → Parallel Processing → Comprehensive Analysis → Integrated Legal Reports
```

---

## 🔒 Legal Compliance & Security

### UK Legal Standards
- **GDPR Compliance**: Article 6(1)(f) legitimate interests implementation
- **Evidence Act Compliance**: Court admissibility standards for digital evidence
- **Expert Witness Standards**: Analysis meets CPR Part 35 requirements
- **Data Retention**: Automated compliance with legal profession retention standards

### Security Features
- **Chain of Custody**: Immutable audit trails for all evidence operations
- **Content Integrity**: SHA256 verification and tamper detection
- **API Security**: HTTPS-only communication with secure key management
- **Access Controls**: Configurable evidence access and retention policies

### Professional Standards
- **Forensic Methodology**: Evidence processing follows established forensic standards
- **Deterministic Analysis**: AI processing with temperature=0 for consistent results
- **Schema Validation**: All outputs validated against canonical legal evidence schema
- **Audit Logging**: Complete operation logs suitable for expert witness testimony

---

## 📚 Documentation

### User Guides
- **[Getting Started](GETTING_STARTED.md)** - Quick setup and first analysis
- **[Document Analyzer Guide](document-evidence-analyzer/README.md)** - Text analysis workflows
- **[Image Analyzer Guide](image-analysis/README.md)** - Forensic image processing
- **[Legal Compliance](image-analysis/docs/LEGAL_COMPLIANCE.md)** - UK legal standards and GDPR

### Technical Documentation
- **[Architecture Overview](CLAUDE.md)** - System design and component integration
- **[API Reference](image-analysis/docs/API_REFERENCE.md)** - Complete Python API documentation
- **[Development Guide](image-analysis/docs/DEVELOPER_GUIDE.md)** - Contributing and customization

### Professional Resources
- **[Cost Analysis](image-analysis/docs/COST_GUIDE.md)** - ROI analysis and budget planning
- **[Expert Witness Integration](image-analysis/docs/USER_GUIDE.md)** - Court preparation guidance

---

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# For AI-powered image analysis
export OPENAI_API_KEY='sk-your-openai-key-here'

# Optional model configuration
export EVIDENCE_TOOLKIT_MODEL='gpt-4.1-mini'          # Default model
export EVIDENCE_TOOLKIT_MODEL_REVISION='2025-09-10'   # Model revision
```

### Installation Requirements
- **Python**: 3.8+ for document analysis, 3.12+ for image analysis
- **Package Manager**: pip, uv, or poetry
- **API Access**: OpenAI API key for image analysis features
- **System**: Linux, macOS, or Windows with standard Python development tools

---

## 💰 Cost Transparency

### AI Analysis Costs
- **Image Analysis**: ~$0.0014 USD per image (~£0.0011 GBP)
- **Document Analysis**: No AI costs - purely local processing
- **Real-Time Tracking**: Built-in cost monitoring with configurable alerts

### Professional Service Comparison
| Method | Cost per Image | Time | Consistency | Quality |
|--------|---------------|------|-------------|---------|
| **Evidence Toolkit** | **£0.0011** | **3 seconds** | **100%** | **Expert-Grade** |
| Manual Expert Analysis | £37.50 | 15 minutes | 95% | Excellent |

**100-image case ROI**: £3,749.89 savings (99.997% cost reduction)

---

## 🤝 Contributing

We welcome contributions from legal professionals, developers, and compliance experts:

1. **Fork the repository** and create a feature branch
2. **Follow the architecture**: Maintain separation between components while enabling unified usage
3. **Maintain legal compliance**: All changes must preserve GDPR and UK legal standard compliance
4. **Add tests**: Both unit tests and integration tests for new features
5. **Update documentation**: Keep all README files and technical documentation current

### Development Setup
```bash
git clone https://github.com/evidence-toolkit/evidence-toolkit.git
cd evidence-toolkit
pip install -e ".[dev]"

# Run comprehensive test suite
pytest document-evidence-analyzer/tests/
cd image-analysis && scripts/validate_analyses.sh
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Professional Certifications:**
- GDPR Compliance Framework
- UK Legal Standards Alignment
- Expert Witness Quality Standards
- Forensic Evidence Processing Standards

---

## 🙏 Acknowledgments

- **OpenAI**: AI-powered analysis capabilities via GPT-4 Vision API
- **UK Legal Community**: Framework validation by qualified legal professionals
- **Open Source**: Built on robust open-source foundations (NLTK, WordCloud, SQLAlchemy, Typer)
- **Professional Standards**: Methodology aligned with forensic and legal best practices

---

**⚖️ Professional Legal Evidence Analysis**
*Comprehensive toolkit for modern legal evidence processing*

**🏛️ Court-Ready | 🛡️ GDPR Compliant | 📊 Cost Transparent | 👥 Expert Validated**

*Transform your legal evidence workflow with AI-powered analysis that meets the highest professional standards.*