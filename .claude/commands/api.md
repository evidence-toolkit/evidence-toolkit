---
description: API interface for Evidence Toolkit operations - process requests and return structured responses
argument-hint: <endpoint> [json-payload or args]
allowed-tools: Task
---

# Evidence Toolkit API Interface

Machine-readable API for Evidence Toolkit operations. Returns structured JSON responses.

## Usage

```bash
/api <endpoint> <arguments>
```

## Available Endpoints

### Evidence Analysis
- `analyze <file-path>` - Analyze single evidence file
- `batch-analyze <case-id>` - Analyze all evidence in case
- `reanalyze <sha256>` - Re-run analysis with latest models

### Case Operations
- `correlate <case-id> [--ai-resolve]` - Run correlation analysis
- `summary <case-id> [--case-type <type>]` - Generate executive summary
- `package <case-id>` - Create client deliverable package
- `status <case-id>` - Get case processing status

### Evidence Management
- `ingest <file-path> --case-id <id>` - Ingest evidence file
- `list-evidence <case-id>` - List all evidence in case
- `get-metadata <sha256>` - Retrieve evidence metadata

### Utility
- `version` - Get toolkit version and features
- `health` - Check system health and dependencies
- `capabilities` - List available features (v3.1, v3.2, etc.)

## Context

**Project Version:**
!`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null || echo "0.0.0"`

**Available Features:**
!`if grep -q "EntityMatchResult" src/evidence_toolkit/core/models.py 2>/dev/null; then echo "v3.2+"; elif grep -q "LegalPatternAnalysis" src/evidence_toolkit/core/models.py 2>/dev/null; then echo "v3.1+"; else echo "v3.0"; fi`

**CLI Status:**
!`if which evidence-toolkit >/dev/null 2>&1; then echo "installed"; else echo "not_installed"; fi`

---

## Your Task

Using the **api-handler** subagent, process the API request: `$ARGUMENTS`

The subagent will:
1. Parse the endpoint and arguments
2. Validate the request
3. Execute the operation
4. Return structured JSON response

**Expected Response Format:**
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
  "errors": [ ... ] // if status is "error"
}
```

---

## Examples

```bash
# Analyze evidence
/api analyze data/cases/TEST-CASE/email_001.eml

# Run full case processing
/api process-case TEST-CASE --case-type workplace --ai-resolve

# Get case status
/api status TEST-CASE

# Check capabilities
/api capabilities
```

---

## Notes

**Purpose**: Programmatic interface for Evidence Toolkit
**Output**: Always returns JSON (even for errors)
**Side Effects**: Can modify evidence storage, create packages
**Authentication**: None (local use only)

**Integration**:
- CI/CD pipelines
- External tools
- Batch processing scripts
- Web interfaces

**Related**:
- Individual slash commands (e.g., `/create-test-case`) for interactive use
- CLI (`uv run evidence-toolkit`) for direct command-line access
