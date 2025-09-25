#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA_PATH="$ROOT_DIR/schemas/evidence.v1.json"
TARGET_DIR="$ROOT_DIR/evidence/derived"

if [[ ! -f "$SCHEMA_PATH" ]]; then
  echo "error: schema not found at $SCHEMA_PATH" >&2
  exit 1
fi

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "note: no derived evidence directory at $TARGET_DIR"
  exit 0
fi

mapfile -t ANALYSIS_FILES < <(find "$TARGET_DIR" -type f -name 'analysis.v1.json' | sort)

if (( ${#ANALYSIS_FILES[@]} == 0 )); then
  echo "note: no analysis.v1.json files found under $TARGET_DIR"
  exit 0
fi

status=0
for file in "${ANALYSIS_FILES[@]}"; do
  echo "Validating $file"
  if ! uv run python "$ROOT_DIR/validate_schema.py" "$file" --schema "$SCHEMA_PATH"; then
    status=1
  fi
  echo
fi

exit $status
