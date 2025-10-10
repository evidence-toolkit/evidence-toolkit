# Evidence Toolkit API - Quick Reference

**Version:** 3.3.0 | **Format:** JSON | **Interface:** Claude Code Slash Commands

---

## Quick Start

```bash
# Analyze single file
/api analyze data/cases/MY-CASE/email.eml

# Process entire case
/api-process-case MY-CASE --case-type workplace --ai-resolve

# Check status
/api-status MY-CASE

# Get capabilities
/api capabilities
```

---

## All Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| **Evidence Analysis** |
| `analyze <file>` | Analyze single evidence file | `/api analyze data/cases/TEST/email.eml` |
| `batch-analyze <case-id>` | Analyze all evidence in case | `/api batch-analyze TEST-CASE` |
| `reanalyze <sha256>` | Re-run analysis with latest models | `/api reanalyze abc123...` |
| **Case Operations** |
| `correlate <case-id>` | Run correlation analysis | `/api correlate TEST-CASE --ai-resolve` |
| `summary <case-id>` | Generate executive summary | `/api summary TEST-CASE --case-type workplace` |
| `package <case-id>` | Create client deliverable | `/api package TEST-CASE` |
| `status <case-id>` | Get case processing status | `/api status TEST-CASE` |
| **Evidence Management** |
| `ingest <file> --case-id <id>` | Ingest evidence file | `/api ingest email.eml --case-id TEST` |
| `list-evidence <case-id>` | List all evidence in case | `/api list-evidence TEST-CASE` |
| `get-metadata <sha256>` | Get evidence metadata | `/api get-metadata abc123...` |
| **Utility** |
| `version` | Get toolkit version | `/api version` |
| `health` | Check system health | `/api health` |
| `capabilities` | List available features | `/api capabilities` |

---

## Convenience Commands

| Command | Equivalent To | Use Case |
|---------|---------------|----------|
| `/api-process-case <id>` | Full pipeline (ingest→analyze→correlate→package) | Process entire case |
| `/api-status` | System-wide status | Check overall health |
| `/api-status <case-id>` | Case-specific status | Check case progress |

---

## Response Format

### Success
```json
{
  "status": "success",
  "endpoint": "analyze",
  "data": { /* endpoint-specific data */ },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 1234
  }
}
```

### Error
```json
{
  "status": "error",
  "endpoint": "analyze",
  "errors": [
    {
      "code": "FILE_NOT_FOUND",
      "message": "Evidence file not found",
      "field": "file_path"
    }
  ],
  "metadata": { /* ... */ }
}
```

---

## Common Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| `INVALID_ENDPOINT` | Endpoint doesn't exist | Check spelling, see endpoint list |
| `MISSING_ARGUMENT` | Required param missing | Add required argument |
| `FILE_NOT_FOUND` | File doesn't exist | Verify file path |
| `CASE_NOT_FOUND` | Case directory missing | Create case directory first |
| `CLI_NOT_INSTALLED` | Evidence Toolkit not installed | Run `uv pip install -e .` |

---

## Integration Patterns

### Python
```python
import subprocess, json

def call_api(endpoint, *args):
    result = subprocess.run(
        ["claude", "--headless", f"/api {endpoint} {' '.join(args)}"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

response = call_api("analyze", "data/cases/TEST/file.eml")
```

### Bash
```bash
claude --headless "/api-process-case MY-CASE" > result.json
status=$(jq -r '.status' result.json)
```

### CI/CD
```yaml
- run: |
    claude --headless "/api-process-case $CASE_ID" > result.json
    test "$(jq -r '.status' result.json)" = "success"
```

---

## Feature Detection

Check available features before using them:

```bash
/api capabilities
```

Returns:
```json
{
  "features": {
    "legal_patterns": true,        // v3.1+
    "entity_resolution": true,     // v3.2+
    "case_types": true,            // v3.2+
    "chunked_summaries": true      // v3.2+
  }
}
```

---

## Performance Tips

1. **Cache capabilities**: Query once per session
2. **Use batch operations**: `batch-analyze` instead of multiple `analyze` calls
3. **Monitor execution time**: Log if `execution_time_ms > 30000`
4. **Check health first**: Run `/api health` before heavy operations

---

## Files Created

```
.claude/
├── commands/
│   ├── api.md                    # Main API entry point
│   ├── api-process-case.md       # Convenience: full pipeline
│   └── api-status.md             # Convenience: status check
└── agents/
    └── api-handler.md            # Subagent: request processor

docs/
├── API.md                        # Full API documentation
└── API_QUICK_REFERENCE.md        # This file
```

---

## See Also

- [Full API Documentation](API.md)
- [Architecture Overview](../V3_ARCHITECTURE.md)
- [Project Guide](../CLAUDE.md)

---

**Quick Test:**
```bash
# Verify API works
/api capabilities

# Test with sample
/create-test-case
/api-process-case TEST-CASE
/api-status TEST-CASE
```
