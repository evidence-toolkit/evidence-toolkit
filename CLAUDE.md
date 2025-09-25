# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Evidence Toolkit is a comprehensive suite for legal evidence analysis, containing two main components:

1. **Document Evidence Analyzer** - Text analysis and visualization for legal documents
2. **Image Analysis** - Content-addressed evidence ingestion and AI-powered forensic image analysis

Both tools are designed for professional legal evidence processing with strict chain-of-custody tracking and deterministic analysis workflows.

## Architecture

### Repository Structure

The repository is organized as a monorepo with two main applications:

- `document-evidence-analyzer/` - Standalone Python package for document analysis
- `image-analysis/` - Typer-based CLI for forensic image analysis with content-addressed storage
- Both components can work independently or as part of a unified evidence processing pipeline

### Document Evidence Analyzer

Located in `document-evidence-analyzer/`, this component provides:
- **Core Analysis Engine** (`src/document_analyzer/word_cloud_analyzer.py`) - Text processing and visualization
- **Retaliation Analyzer** (`src/document_analyzer/retaliation_analyzer.py`) - Timeline analysis for workplace retaliation patterns
- **Unified CLI** (`src/document_analyzer/cli.py`) - Command interface supporting both document and image analysis
- **Evidence Management** (`src/document_analyzer/evidence_manager.py`) - Content-addressed storage integration

### Image Analysis System

Located in `image-analysis/`, this is a forensic-grade system providing:
- **Content-Addressed Storage** - Evidence organized by SHA256 with immutable file layout
- **Chain of Custody** - Complete audit trail for all operations
- **AI Analysis** - OpenAI Responses API integration with temperature=0 for deterministic results
- **Schema Validation** - All outputs validated against `schemas/evidence.v1.json`

## Development Commands

### Environment Setup

Both components use modern Python packaging:

```bash
# Document Analyzer (uses pip/uv)
cd document-evidence-analyzer
uv venv
uv pip install -e .
# OR
pip install -e .

# Image Analysis (uses uv)
cd image-analysis
uv sync
source .venv/bin/activate  # optional
```

### Document Evidence Analyzer Commands

```bash
# CLI commands (run from document-evidence-analyzer/)
document-analyzer analyze ./documents --output-dir ./results
document-analyzer retaliation ./documents --output-dir ./analysis
document-analyzer ingest ./files --case-id CASE123
document-analyzer export <sha256> output.json

# Testing
pytest tests/
uv run pytest tests/
```

### Image Analysis Commands

```bash
# All commands use uv run from image-analysis/
uv run python -m image_analysis.cli --help

# Core workflow
uv run python -m image_analysis.cli ingest /path/to/images --case-id CASE123
uv run python -m image_analysis.cli analyze <sha256>
uv run python -m image_analysis.cli analyze-batch --limit 10 --skip-existing
uv run python -m image_analysis.cli export-json <sha256> output.json

# Schema validation
uv run python validate_schema.py evidence/derived/sha256=<hash>/analysis.v1.json
scripts/validate_analyses.sh  # CI validation hook
```

### Testing and Validation

```bash
# Document analyzer tests
cd document-evidence-analyzer && pytest tests/

# Image analysis schema validation (critical for CI)
cd image-analysis && scripts/validate_analyses.sh

# Run individual schema validation
cd image-analysis && uv run python validate_schema.py <analysis-file>
```

## Key Components and Integration

### Unified Analysis Models

The document analyzer includes unified models (`src/document_analyzer/unified_models.py`) that bridge document and image analysis:
- `UnifiedAnalysis` - Container for both analysis types
- `DocumentAnalysisResult` and `ImageAnalysisResult` - Type-specific results
- `EvidenceType` - Enum for document/image classification

### Content-Addressed Evidence Storage

Both components can use the evidence storage system:
- `evidence/raw/sha256=<hash>/original.<ext>` - Original files
- `evidence/derived/sha256=<hash>/` - Metadata, analysis results, chain of custody
- `evidence/labels/<label>/` - Hard links organized by detected content
- `db/evidence.sqlite` - SQLite catalog for queries

### Environment Variables

**Image Analysis:**
- `OPENAI_API_KEY` - Required for AI analysis
- `EVIDENCE_TOOLKIT_MODEL` - Default: "gpt-4.1-mini"
- `EVIDENCE_TOOLKIT_MODEL_REVISION` - Default: "2025-09-10"

## Development Workflow

### For Document Analysis Tasks
1. Use `document-analyzer` CLI or Python API from `document_analyzer` module
2. Results include word clouds, frequency charts, and JSON exports
3. Supports both legacy directory mode and content-addressed evidence mode

### For Image Analysis Tasks
1. **Ingest** images into content-addressed storage with metadata extraction
2. **Analyze** using OpenAI Responses API with deterministic settings (temp=0)
3. **Validate** all outputs against canonical schema before storage
4. **Export** validated bundles for downstream processing

### Schema Compliance
All image analysis outputs MUST validate against `schemas/evidence.v1.json`. The validation pipeline fails fast if any analysis drifts from the schema, ensuring forensic integrity.

### Chain of Custody
Every evidence operation is logged with timestamps and actors. This creates an immutable audit trail suitable for legal proceedings.

## Integration Notes

- Both components can work with the same evidence storage format
- The document analyzer CLI includes image analysis capabilities via `ImageAnalyzer` class
- Unified models allow seamless processing of mixed document/image evidence cases
- All analysis results include comprehensive metadata for legal admissibility