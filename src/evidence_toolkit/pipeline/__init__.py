"""Evidence Processing Pipeline - v3.0

Modular pipeline components for evidence analysis workflow.

This package provides the core pipeline operations extracted from the monolithic CLI:

- **ingest**: File ingestion into content-addressed storage
- **analyze**: Evidence analysis orchestration (documents, images, emails)
- **summary**: Case summary generation with AI insights
- **package**: Client deliverable package creation

All components work with the unified EvidenceStorage and support multi-case evidence reuse.
"""

from evidence_toolkit.pipeline.ingest import (
    ingest_evidence,
    ingest_directory,
    ingest_path,
    print_ingestion_summary,
)

from evidence_toolkit.pipeline.analyze import (
    analyze_evidence,
)

from evidence_toolkit.pipeline.summary import (
    ExecutiveSummaryResponse,
    EvidenceSummary,
    CaseSummary,
    SummaryGenerator,
)

from evidence_toolkit.pipeline.package import (
    PackageGenerator,
)


__all__ = [
    # Ingestion
    'ingest_evidence',
    'ingest_directory',
    'ingest_path',
    'print_ingestion_summary',

    # Analysis
    'analyze_evidence',

    # Summary
    'ExecutiveSummaryResponse',
    'EvidenceSummary',
    'CaseSummary',
    'SummaryGenerator',

    # Package
    'PackageGenerator',
]
