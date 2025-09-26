"""
Evidence Toolkit - Comprehensive legal evidence analysis suite.

This package provides unified access to both document and image analysis capabilities
for legal evidence processing with AI-powered content-addressed evidence storage.
"""

__version__ = "0.1.0"

# Re-export main components for convenience
try:
    from document_analyzer import DocumentAnalyzer, analyze_documents
    from document_analyzer.retaliation_analyzer import RetaliationAnalyzer
except ImportError:
    DocumentAnalyzer = None
    analyze_documents = None
    RetaliationAnalyzer = None

try:
    from image_analysis.models import EvidenceBundle, AnalysisRecord
    from image_analysis.paths import Layout
except ImportError:
    EvidenceBundle = None
    AnalysisRecord = None
    Layout = None

__all__ = [
    "DocumentAnalyzer",
    "analyze_documents",
    "RetaliationAnalyzer",
    "EvidenceBundle",
    "AnalysisRecord",
    "Layout",
]