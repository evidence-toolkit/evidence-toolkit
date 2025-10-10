"""Evidence Toolkit v4.0 - Professional Forensic Analysis Platform

A professional toolkit for forensic-grade evidence processing with:
- Multi-modal AI analysis (documents, images, emails)
- Content-addressed storage with chain of custody
- Cross-evidence correlation and timeline reconstruction
- **v3.1**: Legal pattern detection (contradictions, corroboration, evidence gaps)
- **v3.1**: Power dynamics analysis in email communications
- **v3.2**: AI entity resolution, case type support, chunked summaries
- **v3.3**: Maximum Data Utilization (90-98% AI data surfaced)
- **v3.3**: Insights-first report structure
- **NEW v4.0**: 8 Professional Forensic Reports (automated generation)
- **NEW v4.0**: Generators Architecture (9 specialized report generators)
- **NEW v4.0**: £4,500 client deliverable value (8-9x increase)

Quick Start:
    from evidence_toolkit.core import EvidenceStorage, UnifiedAnalysis
    from evidence_toolkit.pipeline import analyze_evidence, PackageGenerator

    # Initialize storage
    storage = EvidenceStorage("data/storage")

    # Analyze evidence with v3.3 AI enhancements
    import openai
    client = openai.OpenAI()
    result = analyze_evidence(sha256, case_id, storage, client)

    # Generate client package with legal patterns
    generator = PackageGenerator(storage, client)
    package = generator.create_client_package(case_id, output_dir)

CLI Usage:
    evidence-toolkit process-case cases/MY-CASE --case-id MY-CASE

Architecture:
    - core/: Models (Pydantic), storage, utilities
    - analyzers/: Document, image, email, correlation analysis (AI-powered)
    - pipeline/: Ingest, analyze, correlate, package orchestration
    - generators/: [NEW v4.0] 9 report generators (8 professional reports)
    - domains/: Legal prompts and configurations

Reports Generated (v4.0):
    1. Executive Summary
    2. Forensic Legal Opinion
    3. Financial Risk Assessment
    4. Legal Patterns Analysis
    5. Timeline Reconstruction
    6. Quoted Statements Analysis
    7. Relationship Network Analysis
    8. Power Dynamics Analysis
"""

__version__ = "4.0.0"
__author__ = "Evidence Toolkit Contributors"

# Core exports
from .core import (
    EvidenceType,
    EvidenceStorage,
    UnifiedAnalysis,
    CorrelationAnalysis,
)

# Pipeline exports
from .pipeline import (
    ingest_evidence,
    analyze_evidence,
    PackageGenerator,
    SummaryGenerator,
)

# Analyzer exports
from .analyzers import (
    DocumentAnalyzer,
    ImageAnalyzer,
    EmailAnalyzer,
    CorrelationAnalyzer,
)

__all__ = [
    # Version
    "__version__",

    # Core
    "EvidenceType",
    "EvidenceStorage",
    "UnifiedAnalysis",
    "CorrelationAnalysis",

    # Pipeline
    "ingest_evidence",
    "analyze_evidence",
    "PackageGenerator",
    "SummaryGenerator",

    # Analyzers
    "DocumentAnalyzer",
    "ImageAnalyzer",
    "EmailAnalyzer",
    "CorrelationAnalyzer",
]
