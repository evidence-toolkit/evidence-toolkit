"""Core infrastructure for Evidence Toolkit.

This package contains the fundamental building blocks:
- models: All Pydantic models (unified)
- storage: Content-addressed evidence storage
- utils: File utilities and helpers
"""

from .models import (
    # Base Types
    EvidenceType,
    FileMetadata,
    ChainOfCustodyEvent,

    # AI Analysis
    DocumentAnalysis,
    ImageAnalysisStructured,
    EmailThreadAnalysis,

    # Unified Analysis
    UnifiedAnalysis,

    # Forensic Bundles
    EvidenceBundle,

    # Cross-Evidence (NOW PYDANTIC!)
    CorrelationAnalysis,

    # Operation Results
    IngestionResult,
    ExportResult,
)

from .utils import (
    calculate_sha256,
    get_file_metadata,
    extract_exif_data,
    detect_file_type,
    ensure_directory,
)

from .storage import EvidenceStorage

__all__ = [
    # Models
    "EvidenceType",
    "FileMetadata",
    "ChainOfCustodyEvent",
    "DocumentAnalysis",
    "ImageAnalysisStructured",
    "EmailThreadAnalysis",
    "UnifiedAnalysis",
    "EvidenceBundle",
    "CorrelationAnalysis",
    "IngestionResult",
    "ExportResult",

    # Utils
    "calculate_sha256",
    "get_file_metadata",
    "extract_exif_data",
    "detect_file_type",
    "ensure_directory",

    # Storage
    "EvidenceStorage",
]
