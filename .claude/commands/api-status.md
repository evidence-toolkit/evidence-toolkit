---
description: API endpoint - Get detailed status of a case or the entire system
argument-hint: [case-id]
---

# API: Status Check

Get detailed status information for a case or system-wide status.

## Usage
```bash
/api-status                    # System status
/api-status <case-id>          # Case status
```

## Context

**System Info:**
- Version: !`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null || echo "unknown"`
- CLI: !`if which evidence-toolkit >/dev/null 2>&1; then echo "installed"; else echo "not_installed"; fi`
- Cases: !`ls -1 data/cases/ 2>/dev/null | wc -l | tr -d ' '`
- Packages: !`ls -1 data/packages/*.zip 2>/dev/null | wc -l | tr -d ' '`

**Case Info (if $1 provided):**
- Evidence: !`find data/cases/$1 -type f 2>/dev/null | wc -l | tr -d ' '`
- Analyzed: !`find data/storage/cases/$1 -type f 2>/dev/null | wc -l | tr -d ' '`
- Correlation: !`if [ -f data/storage/cases/$1/correlation_analysis.json ]; then echo "exists"; else echo "missing"; fi`
- Package: !`if [ -f data/packages/$1.zip ]; then echo "exists"; else echo "missing"; fi`

---

## Your Task

Using the **api-handler** subagent, return status in JSON format:

### System Status (no case-id)
```json
{
  "status": "success",
  "endpoint": "status",
  "data": {
    "system": {
      "version": "3.3.0",
      "cli_installed": true,
      "features": ["v3.1", "v3.2", "v3.3"]
    },
    "storage": {
      "total_cases": 5,
      "total_evidence": 127,
      "total_packages": 3
    },
    "health": {
      "python_version": "3.11.5",
      "dependencies_ok": true
    }
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 89
  }
}
```

### Case Status (with case-id)
```json
{
  "status": "success",
  "endpoint": "status",
  "data": {
    "case_id": "$1",
    "evidence_count": 13,
    "analyzed_count": 13,
    "processing_complete": true,
    "stages": {
      "ingest": {"complete": true, "count": 13},
      "analyze": {"complete": true, "count": 13},
      "correlate": {"complete": true, "exists": true},
      "package": {"complete": true, "exists": true, "path": "data/packages/$1.zip"}
    }
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 45
  }
}
```
