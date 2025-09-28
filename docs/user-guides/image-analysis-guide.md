# Image Analysis User Guide

Forensic-grade image evidence ingestion, AI analysis, and validation for legal proceedings.

## Features

- **Content-Addressed Storage**: Images organized by SHA256 with immutable file layout
- **AI Analysis**: OpenAI Responses API integration with temperature=0 for deterministic results
- **Chain of Custody**: Complete audit trail for all operations
- **Schema Validation**: All outputs validated against `schemas/images.v1.json`
- **Perceptual Hashing**: Duplicate detection and visual similarity analysis
- **EXIF Extraction**: Comprehensive metadata extraction for forensic analysis

## Prerequisites

- [uv](https://github.com/astral-sh/uv) for dependency management
- Python 3.12+
- `OPENAI_API_KEY` exported in your shell for the Responses API

## Environment Setup

```bash
# Inside the image-analysis directory
uv sync  # installs dependencies into .venv using pyproject.toml

# Optional: activate environment for persistent shells
source .venv/bin/activate
```

All commands can be run ad-hoc via `uv run …` without activating the venv.

## CLI Commands

### Ingest Images

```bash
# Ingest images into content-addressed storage
uv run python -m image_analysis.cli ingest /path/to/images --case-id CASE123
```

This command:
- Copies each image to `evidence/raw/sha256=<hash>/original.<ext>`
- Extracts EXIF, perceptual hash, and metadata to `evidence/derived/sha256=<hash>/`
- Creates `chain_of_custody.json` with ingest event
- Updates SQLite catalog at `db/evidence.sqlite`

### Analyze Images

```bash
# Analyze single image by SHA256
uv run python -m image_analysis.cli analyze <sha256>

# Batch analysis with limits
uv run python -m image_analysis.cli analyze-batch --skip-existing --limit 10
```

Analysis includes:
- Scene description
- Object detection
- Text extraction (OCR)
- Risk flag identification
- Legal significance assessment

### Export Results

```bash
# Export analysis results to JSON
uv run python -m image_analysis.cli export-json <sha256> output.json
```

## Evidence Storage Structure

```
evidence/
├── raw/sha256=<hash>/
│   └── original.<ext>              # Original image file
├── derived/sha256=<hash>/
│   ├── analysis.v1.json           # AI analysis results
│   ├── metadata.json              # File metadata
│   ├── exif.json                  # EXIF data
│   ├── chain_of_custody.json      # Audit trail
│   └── openai.v1.json            # Raw OpenAI response
└── labels/<label>/                # Hard links by detected content
    └── sha256=<hash> -> ../../raw/sha256=<hash>/original.<ext>
```

## Schema Validation

All analysis outputs must validate against `schemas/images.v1.json`:

```bash
# Validate single analysis file
uv run python validate_schema.py evidence/derived/sha256=<hash>/analysis.v1.json

# Validate all analysis files (CI/pipeline hook)
scripts/validate_analyses.sh
```

## Python API

```python
from image_analysis.cli import ingest_images, analyze_image
from image_analysis.models import EvidenceBundle

# Ingest images
results = ingest_images("/path/to/images", case_id="CASE123")

# Analyze specific image
bundle = analyze_image("sha256_hash")

# Access analysis results
print(bundle.analyses[0].outputs.scene_description)
```

## Environment Variables

- `OPENAI_API_KEY` - Required for AI analysis
- `EVIDENCE_TOOLKIT_MODEL` - Default: "gpt-4o-mini"
- `EVIDENCE_TOOLKIT_MODEL_REVISION` - Default: "2024-07-18"

## Legal Compliance

The image analysis system maintains forensic standards:

### Chain of Custody
- Every operation logged with timestamps and actors
- Immutable audit trail suitable for legal proceedings
- Complete traceability from ingestion to analysis

### Data Integrity
- SHA256 verification for all evidence files
- Content-addressed storage prevents tampering
- Cryptographic validation of evidence integrity

### Deterministic Analysis
- Temperature=0 OpenAI API calls for reproducible results
- Schema validation ensures consistent output format
- Version tracking for analysis algorithms and models

## Advanced Features

### Perceptual Hashing
Images are processed with perceptual hashing for:
- Duplicate detection across cases
- Visual similarity analysis
- Content-based organization

### Label Organization
Detected content automatically creates hard links:
```
evidence/labels/
├── face/           # Images containing faces
├── document/       # Images of documents
├── screenshot/     # Screenshots
└── outdoors/       # Outdoor scenes
```

### Database Querying
SQLite catalog enables complex queries:
```sql
SELECT * FROM evidence WHERE case_id = 'CASE123' AND width_px > 1920;
```

For advanced usage and development, see the source code documentation.