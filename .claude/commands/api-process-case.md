---
description: API endpoint - Full case processing pipeline (ingest → analyze → correlate → package)
argument-hint: <case-id> [--case-type <type>] [--ai-resolve]
---

# API: Process Case

Full pipeline processing for a case directory.

## Usage
```bash
/api-process-case <case-id> [options]
```

## Arguments
- `$1` - Case ID (required)
- `$ARGUMENTS` - Full arguments including options

## Context

**Input Directory:**
!`ls -1 data/cases/$1/ 2>/dev/null | head -10 || echo "Case not found"`

**Evidence Count:**
!`find data/cases/$1 -type f 2>/dev/null | wc -l | tr -d ' '`

---

## Your Task

Using the **api-handler** subagent, execute full case processing pipeline:

```bash
uv run evidence-toolkit process-case data/cases/$1 --case-id $1 $ARGUMENTS
```

Return JSON response with:
- Evidence ingested count
- Analyses completed count
- Correlation status
- Package location
- Execution time per stage

**Example Response:**
```json
{
  "status": "success",
  "endpoint": "process-case",
  "data": {
    "case_id": "$1",
    "evidence_count": 13,
    "stages": {
      "ingest": {"status": "success", "time_ms": 450},
      "analyze": {"status": "success", "time_ms": 12340},
      "correlate": {"status": "success", "time_ms": 3450},
      "package": {"status": "success", "time_ms": 890}
    },
    "package_path": "data/packages/$1.zip"
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 17130
  }
}
```
