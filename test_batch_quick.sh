#!/bin/bash
# Quick test of batch processing with the test images

echo "🧪 Quick Batch Processing Test"
echo "================================"
echo ""
echo "Testing with 10 test images..."
echo ""

# Run with parallel processing (5 concurrent)
uv run evidence-toolkit process-case data/cases/PARALLEL-TEST \
    --case-id PARALLEL-TEST-QUICK \
    --max-concurrent 5

echo ""
echo "✅ Test complete!"
echo ""
echo "Check the output above for:"
echo "  - '⚡ Batch processing N images' message"
echo "  - '✅ Batch analyzed N images' message"
echo ""
echo "Package created at:"
ls -lh data/packages/PARALLEL-TEST-QUICK*.zip 2>/dev/null || echo "  (Package not found - check for errors above)"
