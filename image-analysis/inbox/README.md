# Image Inbox

This is the default input directory for the Image Analysis system.

## Usage

Simply drop your images here and run analysis commands without specifying paths:

```bash
# Copy your images to inbox
cp /path/to/your/images/* inbox/

# Ingest images (defaults to ./inbox/)
uv run python -m image_analysis.cli ingest --case-id "CASE-001"

# Analyze images
uv run python -m image_analysis.cli analyze-batch
```

## Sample Images

This directory contains sample images for testing:

- `office-screenshot.png` - Computer screen capture showing development environment

## Supported Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- TIFF

## Getting Started

Try running analysis on the sample image:

```bash
# Ingest sample images
uv run python -m image_analysis.cli ingest --case-id "DEMO-2025"

# List ingested evidence to get SHA256 hashes
ls evidence/raw/

# Analyze specific image (replace <hash> with actual SHA256)
uv run python -m image_analysis.cli analyze <hash>

# Or analyze all ingested images
uv run python -m image_analysis.cli analyze-batch --skip-existing
```

Results will be stored in the content-addressed evidence directory with complete chain of custody tracking.