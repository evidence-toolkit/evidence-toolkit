"""Evidence Toolkit Analyzers (v3.1)

Unified analyzer modules for document, image, and email evidence processing with AI enhancements.

This module provides the core analysis engines that power the Evidence Toolkit:

- DocumentAnalyzer: Text analysis, word frequency, AI-powered entity extraction with relationships
- ImageAnalyzer: Vision AI analysis with OCR and scene understanding
- EmailAnalyzer: Forensic email thread analysis with power dynamics and escalation detection
- EmailParser: Multi-format email parsing (.eml, .msg, .mbox)
- CorrelationAnalyzer: Cross-evidence correlation with AI legal pattern detection

**v3.1 Enhancements:**
- Legal pattern detection: Contradictions, corroboration, evidence gaps
- Power dynamics analysis: Deference scoring, dominant topics in email threads
- Enhanced relationships: Entity relationships, quoted text, temporal event linking

All analyzers use the OpenAI Responses API for deterministic, legally-admissible
AI analysis suitable for legal evidence processing.
"""

from evidence_toolkit.analyzers.document import (
    DocumentAnalyzer,
    analyze_documents,
    analyze_text_content,
    create_schema_compliant_document_analysis,
    ensure_nltk_data,
)

from evidence_toolkit.analyzers.image import ImageAnalyzer

from evidence_toolkit.analyzers.email import EmailAnalyzer

from evidence_toolkit.analyzers.email_parser import EmailParser

from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer


__all__ = [
    # Document Analysis
    "DocumentAnalyzer",
    "analyze_documents",
    "analyze_text_content",
    "create_schema_compliant_document_analysis",
    "ensure_nltk_data",

    # Image Analysis
    "ImageAnalyzer",

    # Email Analysis
    "EmailAnalyzer",
    "EmailParser",

    # Correlation Analysis
    "CorrelationAnalyzer",
]


# Version info
__version__ = "3.1.0"
__author__ = "Evidence Toolkit Team"
__description__ = "AI-enhanced analyzer modules for legal evidence processing with pattern detection"
