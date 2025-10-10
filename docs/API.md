# Evidence Toolkit API

**Version:** 3.3.0
**Type:** Claude Code Slash Command API
**Output:** Structured JSON

---

## Overview

The Evidence Toolkit API provides a programmatic interface for evidence analysis operations through Claude Code slash commands and specialized subagents. All operations return structured JSON responses suitable for automation and integration.

## Architecture

```
┌─────────────────────────────────────────────┐
│ /api <endpoint> <args>                      │
│ (Slash Command Entry Point)                 │
└──────────────┬──────────────────────────────┘
               │
               │ Delegates to
               ↓
┌─────────────────────────────────────────────┐
│ api-handler Subagent                        │
│ - Parse & validate request                  │
│ - Execute Evidence Toolkit operation        │
│ - Format JSON response                      │
└─────────────────────────────────────────────┘
```

## Quick Start

### Basic Usage

```bash
# Analyze a single evidence file
/api analyze data/cases/MY-CASE/email.eml

# Process entire case
/api-process-case MY-CASE --case-type workplace --ai-resolve

# Get case status
/api-status MY-CASE

# Check system capabilities
/api capabilities
```

### Response Format

All API responses follow this structure:

```json
{
  "status": "success" | "error",
  "endpoint": "<endpoint-name>",
  "data": { ... },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 1234
  },
  "errors": [ ... ]  // only if status is "error"
}
```

---

## API Endpoints

### Evidence Analysis

#### `analyze <file-path>`

Analyze a single evidence file (document, email, or image).

**Request:**
```bash
/api analyze data/cases/TEST-CASE/email_001.eml
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "analyze",
  "data": {
    "sha256": "a1b2c3d4e5f6...",
    "file_path": "data/cases/TEST-CASE/email_001.eml",
    "content_type": "email",
    "analysis": {
      "entities": [
        {
          "name": "John Smith",
          "email": "john@example.com",
          "role": "Sender",
          "organization": "Acme Corp"
        }
      ],
      "summary": "Email regarding project deadline...",
      "quoted_statements": [...],
      "sentiment": "professional"
    }
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 1847
  }
}
```

#### `batch-analyze <case-id>`

Analyze all evidence files in a case directory.

**Request:**
```bash
/api batch-analyze TEST-CASE
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "batch-analyze",
  "data": {
    "case_id": "TEST-CASE",
    "evidence_count": 13,
    "analyzed_count": 13,
    "failed_count": 0,
    "results": [
      {"sha256": "abc...", "status": "success"},
      {"sha256": "def...", "status": "success"}
    ]
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 12340
  }
}
```

---

### Case Operations

#### `correlate <case-id> [--ai-resolve]`

Run cross-evidence correlation analysis.

**Request:**
```bash
/api correlate TEST-CASE --ai-resolve
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "correlate",
  "data": {
    "case_id": "TEST-CASE",
    "correlation_analysis": {
      "entity_matches": 47,
      "temporal_connections": 12,
      "communication_patterns": [...],
      "legal_patterns": {
        "contradictions": 2,
        "corroborations": 5,
        "evidence_gaps": 3
      }
    },
    "ai_entity_resolution": true
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 3450
  }
}
```

#### `summary <case-id> [--case-type <type>]`

Generate executive summary for case.

**Request:**
```bash
/api summary TEST-CASE --case-type workplace
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "summary",
  "data": {
    "case_id": "TEST-CASE",
    "case_type": "workplace",
    "executive_summary": "...",
    "key_findings": [...],
    "legal_implications": [...],
    "recommended_actions": [...]
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 5670
  }
}
```

#### `package <case-id>`

Create client deliverable package.

**Request:**
```bash
/api package TEST-CASE
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "package",
  "data": {
    "case_id": "TEST-CASE",
    "package_path": "data/packages/TEST-CASE.zip",
    "package_size_bytes": 1234567,
    "contents": {
      "evidence_count": 13,
      "reports": ["executive_summary.md", "analysis_report.md"],
      "analyses": 13
    }
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 890
  }
}
```

---

### Evidence Management

#### `ingest <file-path> --case-id <case-id>`

Ingest evidence file into content-addressed storage.

**Request:**
```bash
/api ingest data/cases/TEST-CASE/new_email.eml --case-id TEST-CASE
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "ingest",
  "data": {
    "sha256": "a1b2c3d4e5f6...",
    "file_path": "data/cases/TEST-CASE/new_email.eml",
    "storage_path": "data/storage/raw/sha256=a1b2c3d4e5f6.../original.eml",
    "case_id": "TEST-CASE",
    "duplicate": false
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 123
  }
}
```

#### `list-evidence <case-id>`

List all evidence files in a case.

**Response:**
```json
{
  "status": "success",
  "endpoint": "list-evidence",
  "data": {
    "case_id": "TEST-CASE",
    "evidence_count": 13,
    "evidence": [
      {
        "sha256": "abc...",
        "filename": "email_001.eml",
        "content_type": "email",
        "analyzed": true
      },
      // ...
    ]
  }
}
```

#### `get-metadata <sha256>`

Retrieve metadata for specific evidence.

**Response:**
```json
{
  "status": "success",
  "endpoint": "get-metadata",
  "data": {
    "sha256": "a1b2c3d4e5f6...",
    "original_filename": "email_001.eml",
    "ingested_timestamp": "2025-10-10T10:00:00Z",
    "content_type": "email",
    "file_size_bytes": 4567,
    "chain_of_custody": [
      {
        "action": "ingested",
        "timestamp": "2025-10-10T10:00:00Z",
        "user": "analyst"
      }
    ]
  }
}
```

---

### Utility Endpoints

#### `version`

Get Evidence Toolkit version information.

**Response:**
```json
{
  "status": "success",
  "endpoint": "version",
  "data": {
    "version": "3.3.0",
    "python_version": "3.11.5",
    "cli_installed": true
  }
}
```

#### `health`

Check system health and dependencies.

**Response:**
```json
{
  "status": "success",
  "endpoint": "health",
  "data": {
    "overall": "healthy",
    "checks": {
      "cli_installed": true,
      "python_version": "3.11.5",
      "dependencies": "ok",
      "storage_accessible": true,
      "openai_configured": true
    }
  }
}
```

#### `capabilities`

List available features and versions.

**Response:**
```json
{
  "status": "success",
  "endpoint": "capabilities",
  "data": {
    "version": "3.3.0",
    "features": {
      "baseline": true,
      "legal_patterns": true,
      "power_dynamics": true,
      "entity_resolution": true,
      "case_types": true,
      "chunked_summaries": true,
      "video_audio_ingestion": true
    },
    "supported_content_types": ["email", "document", "image", "video", "audio"],
    "available_case_types": ["generic", "workplace", "employment", "contract"]
  }
}
```

---

## Convenience Commands

### `/api-process-case <case-id> [options]`

Full pipeline processing (ingest → analyze → correlate → package).

**Example:**
```bash
/api-process-case MY-CASE --case-type workplace --ai-resolve
```

**Response:**
```json
{
  "status": "success",
  "endpoint": "process-case",
  "data": {
    "case_id": "MY-CASE",
    "evidence_count": 13,
    "stages": {
      "ingest": {"status": "success", "time_ms": 450},
      "analyze": {"status": "success", "time_ms": 12340},
      "correlate": {"status": "success", "time_ms": 3450},
      "package": {"status": "success", "time_ms": 890}
    },
    "package_path": "data/packages/MY-CASE.zip"
  },
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 17130
  }
}
```

### `/api-status [case-id]`

Get system or case status.

**System Status:**
```bash
/api-status
```

**Case Status:**
```bash
/api-status MY-CASE
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "endpoint": "analyze",
  "errors": [
    {
      "code": "FILE_NOT_FOUND",
      "message": "Evidence file not found: data/cases/TEST-CASE/missing.eml",
      "field": "file_path"
    }
  ],
  "metadata": {
    "version": "3.3.0",
    "timestamp": "2025-10-10T12:34:56Z",
    "execution_time_ms": 45
  }
}
```

### Error Codes

| Code | Description | HTTP Equivalent |
|------|-------------|-----------------|
| `INVALID_ENDPOINT` | Endpoint not recognized | 404 |
| `MISSING_ARGUMENT` | Required argument missing | 400 |
| `FILE_NOT_FOUND` | Referenced file doesn't exist | 404 |
| `CASE_NOT_FOUND` | Case directory doesn't exist | 404 |
| `ANALYSIS_FAILED` | Evidence analysis error | 500 |
| `INVALID_CASE_ID` | Case ID format invalid | 400 |
| `CLI_NOT_INSTALLED` | Evidence Toolkit CLI not available | 503 |
| `EXECUTION_ERROR` | Command execution failed | 500 |

---

## Integration Examples

### Python Script

```python
import subprocess
import json

def api_call(endpoint, *args):
    """Call Evidence Toolkit API via Claude Code"""
    cmd = f"/api {endpoint} {' '.join(args)}"
    result = subprocess.run(
        ["claude", "--headless", cmd],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# Analyze evidence
response = api_call("analyze", "data/cases/MY-CASE/email.eml")
if response["status"] == "success":
    print(f"SHA256: {response['data']['sha256']}")
    print(f"Entities: {len(response['data']['analysis']['entities'])}")
```

### Bash Script

```bash
#!/bin/bash

# Process case via API
claude --headless "/api-process-case MY-CASE --case-type workplace" > result.json

# Extract package path
package_path=$(jq -r '.data.package_path' result.json)
echo "Package created: $package_path"
```

### CI/CD Pipeline

```yaml
# .github/workflows/evidence-analysis.yml
- name: Analyze Evidence
  run: |
    claude --headless "/api-process-case $CASE_ID" > result.json

    # Check status
    status=$(jq -r '.status' result.json)
    if [ "$status" != "success" ]; then
      echo "Analysis failed"
      jq '.errors' result.json
      exit 1
    fi

    # Upload package
    package=$(jq -r '.data.package_path' result.json)
    aws s3 cp "$package" s3://evidence-packages/
```

---

## Best Practices

### 1. Always Check Response Status

```python
response = api_call("analyze", file_path)
if response["status"] != "success":
    for error in response["errors"]:
        print(f"Error {error['code']}: {error['message']}")
    return
```

### 2. Use Execution Time for Monitoring

```python
exec_time = response["metadata"]["execution_time_ms"]
if exec_time > 30000:  # 30 seconds
    logging.warning(f"Slow API call: {exec_time}ms")
```

### 3. Validate Inputs Before Calling

```python
if not os.path.exists(file_path):
    print("File not found, skipping API call")
    return

if not re.match(r'^[A-Z0-9_-]+$', case_id):
    print("Invalid case ID format")
    return
```

### 4. Cache Capabilities

```python
# Fetch once, cache for session
capabilities = api_call("capabilities")
HAS_AI_RESOLVE = capabilities["data"]["features"]["entity_resolution"]
```

---

## Limitations

1. **Local Only**: API runs via Claude Code, requires local installation
2. **No Authentication**: Designed for trusted local environments
3. **Synchronous**: All operations block until complete
4. **Rate Limits**: Subject to OpenAI API rate limits for AI operations
5. **File Size**: Large evidence files may timeout (>50MB)

---

## Future Enhancements

Planned features for future versions:

- [ ] Async operations with status polling
- [ ] Webhook callbacks for long-running tasks
- [ ] Batch operations endpoint
- [ ] Export formats (CSV, XML, DOCX)
- [ ] Query language for filtering results
- [ ] REST API wrapper (HTTP server mode)

---

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project conventions and architecture
- [V3_ARCHITECTURE.md](../V3_ARCHITECTURE.md) - Technical architecture
- [CLI Reference](../README.md#commands) - Direct CLI usage
- [Slash Commands](../.claude/commands/) - Interactive commands

---

## Support

For issues or questions:
- Check error codes and messages in responses
- Review [troubleshooting guide](../README.md#troubleshooting)
- Examine execution logs: `~/.claude/logs/`
- Test with `/api capabilities` to verify features available

**Version:** 3.3.0
**Last Updated:** 2025-10-10
