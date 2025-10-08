#!/bin/bash

# Reset Evidence Database Script
# Clears all analysis data and evidence entries for fresh start

set -e

echo "🗄️  Evidence Database Reset"
echo "================================"

DB_PATH="db/evidence.sqlite"

if [ ! -f "$DB_PATH" ]; then
    echo "❌ Database not found at $DB_PATH"
    echo "Run this script from the image-analysis/ directory"
    exit 1
fi

# Show current database status
echo "📊 Current database status:"
EVIDENCE_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM evidence;" 2>/dev/null || echo "0")
ANALYSIS_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM analysis;" 2>/dev/null || echo "0")

echo "   Evidence entries: $EVIDENCE_COUNT"
echo "   Analysis entries: $ANALYSIS_COUNT"
echo ""

if [ "$EVIDENCE_COUNT" -eq 0 ] && [ "$ANALYSIS_COUNT" -eq 0 ]; then
    echo "✅ Database is already empty. Nothing to reset."
    exit 0
fi

# Confirm before deletion
read -p "⚠️  This will DELETE ALL analysis data and evidence entries. Continue? (y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🚫 Reset cancelled."
    exit 0
fi

echo ""
echo "🔄 Resetting database..."

# Clear analysis table
sqlite3 "$DB_PATH" "DELETE FROM analysis;" 2>/dev/null || true
echo "   ✓ Cleared analysis table"

# Clear evidence table
sqlite3 "$DB_PATH" "DELETE FROM evidence;" 2>/dev/null || true
echo "   ✓ Cleared evidence table"

# Clean up evidence directories (optional)
read -p "🗂️  Also remove evidence directories? This will delete analyzed files. (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   🗑️  Removing evidence directories..."
    rm -rf evidence/raw/sha256=* 2>/dev/null || true
    rm -rf evidence/derived/sha256=* 2>/dev/null || true
    rm -rf evidence/labels/* 2>/dev/null || true
    echo "   ✓ Evidence directories cleared"
fi

echo ""
echo "✅ Database reset complete!"
echo ""
echo "Next steps:"
echo "1. Copy new images to inbox/ directory"
echo "2. Run: uv run image-analyzer ingest --case-id \"YOUR-CASE\""
echo "3. Run: uv run image-analyzer analyze-batch"