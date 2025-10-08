#!/bin/bash
# Re-analyze files missing analysis.v1.json

for sha256_dir in evidence/derived/sha256=*/; do
    if [ ! -f "${sha256_dir}analysis.v1.json" ]; then
        SHA256=$(basename "$sha256_dir" | cut -d'=' -f2)
        echo "Analyzing $SHA256..."
        .venv/bin/document-analyzer analyze "$SHA256" --case-id WORKPLACE-2024-002 --quiet
    fi
done
