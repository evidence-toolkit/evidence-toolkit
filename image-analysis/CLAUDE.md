# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Evidence Toolkit for image analysis that provides content-addressed evidence ingestion, deterministic AI analysis using OpenAI's Responses API, and JSON schema validation. The system is designed for legal evidence analysis with strict chain-of-custody tracking.

## Development Commands

### Environment Setup
```bash
uv sync  # installs dependencies into .venv using pyproject.toml
source .venv/bin/activate  # optional for persistent shells
```

### Core CLI Commands
The main application is at `image_analysis/cli.py` and all commands use the `uv run` pattern:

```bash
# Get help
uv run python -m image_analysis.cli --help

# Ingest images (creates content-addressed storage)
uv run python -m image_analysis.cli ingest /path/to/images --case-id CASE123

# Analyze single image by SHA256
uv run python -m image_analysis.cli analyze <sha256>

# Batch analysis with optional limits
uv run python -m image_analysis.cli analyze-batch --skip-existing --limit 10

# Export analysis results
uv run python -m image_analysis.cli export-json <sha256> output.json
```

### Schema Validation
```bash
# Validate single analysis file
uv run python validate_schema.py evidence/derived/sha256=<hash>/analysis.v1.json

# Validate all analysis files (CI/pipeline hook)
scripts/validate_analyses.sh
```

## Architecture

### Content-Addressed Storage
Evidence is stored by SHA256 hash in a structured layout:
- `evidence/raw/sha256=<hash>/original.<ext>` - Original files
- `evidence/derived/sha256=<hash>/` - Metadata, EXIF, analysis results
- `evidence/labels/<label>/` - Hard links organized by detected labels
- `db/evidence.sqlite` - SQLite catalog for queries

### Key Components

1. **CLI (`image_analysis/cli.py`)** - Main Typer application with ingest, analyze, and export commands
2. **Models (`image_analysis/models.py`)** - Pydantic models for evidence bundles, analysis records, and chain-of-custody
3. **Database (`image_analysis/db.py`)** - SQLAlchemy models for Evidence and Analysis tables
4. **Utils (`image_analysis/utils.py`)** - Helper functions for hashing, EXIF extraction, perceptual hashing
5. **Paths (`image_analysis/paths.py`)** - Layout class for organizing file system structure

### Analysis Pipeline
1. **Ingest**: Images are hashed, copied to content-addressed storage, metadata extracted
2. **Analysis**: OpenAI Responses API called with temperature=0, results validated against schema
3. **Chain of Custody**: Every operation logged with timestamps and actors
4. **Validation**: All outputs conform to `schemas/evidence.v1.json`

### Environment Variables
- `OPENAI_API_KEY` - Required for analysis operations
- `EVIDENCE_TOOLKIT_MODEL` - Default: "gpt-4.1-mini"
- `EVIDENCE_TOOLKIT_MODEL_REVISION` - Default: "2025-09-10"

### Schema Validation
The canonical schema is `schemas/evidence.v1.json`. All analysis outputs must validate against this schema before storage. The validation script provides detailed error reporting for debugging schema violations.