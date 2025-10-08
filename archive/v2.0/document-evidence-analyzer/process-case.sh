#!/bin/bash
#
# Evidence Toolkit - Simplified Case Processing
#
# Usage: ./process-case.sh <case-directory> <case-id> [evidence-root]
#
# This script automates the entire evidence processing pipeline:
#   1. Ingest all evidence (PDFs, images, emails)
#   2. Analyze all evidence with AI
#   3. Run cross-evidence correlation
#   4. Generate client package
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arguments
CASE_DIR="${1}"
CASE_ID="${2}"
EVIDENCE_ROOT="${3:-../evidence}"

# Validate arguments
if [ -z "$CASE_DIR" ] || [ -z "$CASE_ID" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: $0 <case-directory> <case-id> [evidence-root]"
    echo ""
    echo "Example:"
    echo "  $0 ./cases/workplace-2024-001 WORKPLACE-2024-001"
    echo ""
    exit 1
fi

if [ ! -d "$CASE_DIR" ]; then
    echo -e "${RED}Error: Case directory not found: $CASE_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Evidence Toolkit - Case Processing Pipeline${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Case Directory:  ${GREEN}$CASE_DIR${NC}"
echo -e "  Case ID:         ${GREEN}$CASE_ID${NC}"
echo -e "  Evidence Root:   ${GREEN}$EVIDENCE_ROOT${NC}"
echo ""

# Step 1: Ingest Evidence
echo -e "${YELLOW}[1/4]${NC} Ingesting evidence files..."
../.venv/bin/document-analyzer ingest "$CASE_DIR" \
    --case-id "$CASE_ID" \
    --evidence-root "$EVIDENCE_ROOT" \
    --actor "process-case-script"

echo -e "${GREEN}✓${NC} Evidence ingestion complete"
echo ""

# Step 2: Analyze Evidence
echo -e "${YELLOW}[2/4]${NC} Analyzing evidence with AI..."

# Count evidence items
EVIDENCE_COUNT=$(find "$EVIDENCE_ROOT/derived" -maxdepth 1 -type d -name "sha256=*" | wc -l)
echo "  Found $EVIDENCE_COUNT evidence items to analyze"

# Analyze each piece of evidence
ANALYZED=0
SKIPPED=0
for sha256_dir in "$EVIDENCE_ROOT/derived"/sha256=*; do
    if [ -d "$sha256_dir" ]; then
        SHA256=$(basename "$sha256_dir" | cut -d'=' -f2)

        # Skip if already analyzed
        if [ -f "$sha256_dir/analysis.v1.json" ]; then
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        # Analyze
        ../.venv/bin/document-analyzer analyze "$SHA256" \
            --evidence-root "$EVIDENCE_ROOT" \
            --case-id "$CASE_ID" \
            --quiet

        ANALYZED=$((ANALYZED + 1))
    fi
done

echo -e "${GREEN}✓${NC} Analyzed $ANALYZED new items (skipped $SKIPPED already analyzed)"
echo ""

# Step 3: Cross-Evidence Correlation
echo -e "${YELLOW}[3/4]${NC} Running cross-evidence correlation analysis..."
../.venv/bin/document-analyzer correlate \
    --case-id "$CASE_ID" \
    --evidence-root "$EVIDENCE_ROOT" \
    --json-output "$EVIDENCE_ROOT/${CASE_ID}-correlation.json" \
    --quiet

echo -e "${GREEN}✓${NC} Correlation analysis complete"
echo ""

# Step 4: Generate Client Package
echo -e "${YELLOW}[4/4]${NC} Generating professional client package..."
../.venv/bin/document-analyzer package \
    --case-id "$CASE_ID" \
    --evidence-root "$EVIDENCE_ROOT" \
    --output-dir ../client_packages \
    --include-raw-evidence \
    --format zip

echo -e "${GREEN}✓${NC} Client package generated"
echo ""

# Find the generated package
PACKAGE_FILE=$(ls -t ../client_packages/${CASE_ID}_analysis_package_*.zip 2>/dev/null | head -1)

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Case Processing Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""
if [ -n "$PACKAGE_FILE" ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)
    echo -e "  📦 Client Package: ${GREEN}$PACKAGE_FILE${NC}"
    echo -e "  📊 Package Size:   ${GREEN}$PACKAGE_SIZE${NC}"
    echo ""
    echo -e "  The package includes:"
    echo -e "    • Executive summary and AI analysis"
    echo -e "    • Individual evidence analysis files"
    echo -e "    • Cross-evidence correlations"
    echo -e "    • Evidence catalog and metadata"
    echo -e "    • Original evidence files"
    echo -e "    • Documentation and methodology"
fi
echo ""
