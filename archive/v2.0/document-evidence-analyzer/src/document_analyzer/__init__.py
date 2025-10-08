"""
Document Evidence Analyzer

A Python library for analyzing text documents and generating visualizations
for legal evidence processing.
"""

from .document_analyzer_core import (
    DocumentAnalyzer,
    analyze_documents,
    analyze_text_content,
    ensure_nltk_data
)

from .retaliation_analyzer import (
    RetaliationAnalyzer,
    RetaliationSummary,
    analyze_retaliation_case
)

from .evidence_manager import EvidenceManager
from .image_analyzer import ImageAnalyzer
from .unified_models import (
    UnifiedAnalysis,
    DocumentAnalysisResult,
    ImageAnalysisResult,
    EvidenceType,
    IngestionResult,
    ExportResult
)
from .evidence_models import (
    DocumentEvidenceBundle,
    EvidenceCore,
    ChainOfCustodyEntry,
    DocumentAnalysisRecord,
    AnalysisModelInfo,
    AnalysisParameters
)
from .utils import (
    calculate_sha256,
    get_file_metadata,
    detect_file_type,
    is_image_file,
    is_text_file
)

__version__ = "0.1.0"
__author__ = "Evidence Toolkit Contributors"

__all__ = [
    # Document analysis
    "DocumentAnalyzer",
    "analyze_documents",
    "analyze_text_content",
    "ensure_nltk_data",

    # Retaliation analysis
    "RetaliationAnalyzer",
    "RetaliationSummary",
    "analyze_retaliation_case",

    # Unified evidence toolkit
    "EvidenceManager",
    "ImageAnalyzer",

    # Models
    "UnifiedAnalysis",
    "DocumentAnalysisResult",
    "ImageAnalysisResult",
    "EvidenceType",
    "IngestionResult",
    "ExportResult",

    # Evidence Bundle Models
    "DocumentEvidenceBundle",
    "EvidenceCore",
    "ChainOfCustodyEntry",
    "DocumentAnalysisRecord",
    "AnalysisModelInfo",
    "AnalysisParameters",

    # Utils
    "calculate_sha256",
    "get_file_metadata",
    "detect_file_type",
    "is_image_file",
    "is_text_file"
]