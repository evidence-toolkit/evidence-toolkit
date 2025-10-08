#!/bin/bash
#
# Evidence Toolkit - Quick Start
# Simple one-command case processing
#
# Usage: ./quick-start.sh <case-directory> <case-id>
#
# Example:
#   ./quick-start.sh cases/workplace-2024-001 WORKPLACE-2024-001
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔬 Evidence Toolkit - Quick Start${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: Run this script from the evidence-toolkit root directory${NC}"
    exit 1
fi

# Check installation
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Not installed${NC}"
    echo ""
    echo "Install with:"
    echo -e "  ${GREEN}pip install -e .${NC}"
    echo ""
    exit 1
fi

# Check dependencies
.venv/bin/python -c "import pdfplumber, pdf2image, openai, nltk, wordcloud" 2>/dev/null || {
    echo -e "${RED}❌ Missing dependencies${NC}"
    echo ""
    echo "Install with:"
    echo -e "  ${GREEN}pip install -e .${NC}"
    echo ""
    exit 1
}

# Validate arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}❌ Missing arguments${NC}"
    echo ""
    echo "Usage: $0 <case-directory> <case-id>"
    echo ""
    echo "Example:"
    echo -e "  ${GREEN}$0 cases/workplace-2024-001 WORKPLACE-2024-001${NC}"
    echo ""
    exit 1
fi

CASE_DIR="$1"
CASE_ID="$2"

# Validate case directory exists
if [ ! -d "$CASE_DIR" ]; then
    echo -e "${RED}❌ Case directory not found: $CASE_DIR${NC}"
    exit 1
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Warning: OPENAI_API_KEY not set${NC}"
    echo "   AI analysis will fail without it"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Display configuration
echo -e "${BLUE}Configuration:${NC}"
echo -e "  📁 Case Directory: ${GREEN}$CASE_DIR${NC}"
echo -e "  🆔 Case ID:        ${GREEN}$CASE_ID${NC}"
echo -e "  💾 Evidence Root:  ${GREEN}data/storage${NC}"
echo -e "  📦 Output Dir:     ${GREEN}data/packages${NC}"
echo ""

# Count files in case directory
FILE_COUNT=$(find "$CASE_DIR" -type f \( -iname "*.pdf" -o -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.txt" -o -iname "*.eml" \) | wc -l)
echo -e "${BLUE}Found ${FILE_COUNT} evidence files${NC}"
echo ""

# Confirm before processing
read -p "Process this case? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Run the complete processing pipeline
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Starting Evidence Processing Pipeline${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

START_TIME=$(date +%s)

.venv/bin/evidence-toolkit process-case "$CASE_DIR" --case-id "$CASE_ID" --actor "quick-start-script"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Processing Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ⏱️  Duration: ${DURATION} seconds"
echo ""

# Find the generated package
PACKAGE_FILE=$(ls -t data/packages/${CASE_ID}_analysis_package_*.zip 2>/dev/null | head -1)

if [ -n "$PACKAGE_FILE" ]; then
    PACKAGE_SIZE=$(du -h "$PACKAGE_FILE" | cut -f1)
    echo -e "  📦 ${GREEN}Client Package Created${NC}"
    echo -e "     Location: ${PACKAGE_FILE}"
    echo -e "     Size:     ${PACKAGE_SIZE}"
    echo ""
    echo -e "  ${BLUE}Package includes:${NC}"
    echo -e "     • Executive summary and AI analysis"
    echo -e "     • Individual evidence analysis files"
    echo -e "     • Cross-evidence correlations"
    echo -e "     • Evidence catalog and metadata"
    echo -e "     • Original evidence files"
    echo -e "     • Documentation and methodology"
else
    echo -e "  ${YELLOW}⚠️  Warning: Could not find generated package${NC}"
    echo -e "     Check data/packages/ directory"
fi

echo ""
echo -e "${GREEN}✅ Done!${NC}"
echo ""
