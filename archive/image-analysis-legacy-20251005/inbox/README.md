# Image Inbox

This is the default input directory for the Image Analysis component.

## Usage

Drop your images here and run analysis commands:

```bash
# Copy your images to inbox
cp /path/to/your/images/*.jpg inbox/
cp /path/to/your/images/*.png inbox/
cp /path/to/your/images/*.jpeg inbox/

# Ingest images into content-addressed storage
uv run python -m image_analysis.cli ingest ./inbox --case-id YOUR_CASE

# Analyze all ingested images
uv run python -m image_analysis.cli analyze-batch --skip-existing
```

## Sample Data

For sample images to test the system, see the main examples directory:
- [Sample Images](../../examples/sample-images/) - Test images for development

## Supported Formats

- JPEG/JPG
- PNG
- GIF
- BMP
- TIFF

## Getting Started

Try the system with sample data:

```bash
# Copy samples to inbox (if available)
cp ../../examples/sample-images/* ./

# Ingest and analyze
uv run python -m image_analysis.cli ingest ./ --case-id DEMO_CASE
uv run python -m image_analysis.cli analyze-batch --limit 5
```

## Important Notes

- **Real images in this directory are NOT tracked by git** (protected by .gitignore)
- All analysis results are stored in content-addressed format under `evidence/`
- Original images are preserved immutably with SHA256 verification
- Complete chain of custody is maintained for legal compliance

Results include scene descriptions, object detection, OCR text extraction, and risk assessment.