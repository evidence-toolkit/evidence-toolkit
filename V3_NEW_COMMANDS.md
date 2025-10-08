# Evidence Toolkit v3.0 - New CLI Commands

**Version**: 3.0.0
**Date**: 2025-10-05
**Status**: Production Ready

---

## Overview

Evidence Toolkit v3.0 introduces **storage management** and **case management** command groups, plus enhanced re-analysis capabilities. These additions provide comprehensive control over the evidence storage system and multi-case workflows.

---

## New Command Groups

### 1. Storage Management (`storage`)

Manage content-addressed evidence storage, monitor health, and perform maintenance.

#### `evidence-toolkit storage stats`

Display comprehensive storage statistics.

```bash
evidence-toolkit storage stats [--storage-dir PATH]
```

**Output Includes**:
- Total evidence count and size
- Evidence breakdown by type (document, email, image)
- Storage size (raw vs derived)
- Case count
- Label categories
- Orphaned file detection

**Example**:
```bash
$ evidence-toolkit storage stats

📊 Storage Statistics
============================================================
Evidence: 20 items (45.32 MB total)
  - document: 12 items
  - email: 5 items
  - image: 3 items

Storage breakdown:
  - Raw files: 38.45 MB
  - Derived/analysis: 6.87 MB

Cases: 3
Labels: 8 categories

✅ No orphaned files detected
```

---

#### `evidence-toolkit storage cleanup`

Clean up broken links and empty directories.

```bash
evidence-toolkit storage cleanup [--storage-dir PATH] [--dry-run] [--force]
```

**Options**:
- `--dry-run`: Preview changes without applying (default)
- `--force`: Actually perform cleanup (overrides `--dry-run`)

**What It Does**:
- Removes broken hard links in `labels/` directory
- Removes empty label directories
- Reports orphaned evidence files (not linked to any case)

**Example**:
```bash
$ evidence-toolkit storage cleanup --dry-run

🔍 Dry run mode (use --force to apply changes)
============================================================
Would remove 2 broken link(s)
Would remove 1 empty director(ies)

⚠️  Found 3 orphaned file(s)
    (Evidence not linked to any case)
    Use 'evidence-toolkit storage prune' to remove if needed

Run with --force to apply these changes
```

**Safety**: Always defaults to dry-run mode. Requires explicit `--force` flag to make changes.

---

#### `evidence-toolkit storage prune`

Remove evidence unique to a specific case.

```bash
evidence-toolkit storage prune --case-id CASE-ID [--storage-dir PATH] [--dry-run] [--force]
```

**Options**:
- `--case-id`: Case ID to prune evidence for (required)
- `--dry-run`: Preview what would be removed (default)
- `--force`: Actually remove evidence (overrides `--dry-run`)

**Safety Features**:
- Only removes evidence that belongs EXCLUSIVELY to the specified case
- Evidence shared with other cases is automatically preserved
- Multi-case evidence reuse is protected

**Example**:
```bash
$ evidence-toolkit storage prune --case-id TEST-2024-001 --dry-run

🔍 Dry run for case: TEST-2024-001
============================================================
Would remove 5 evidence item(s)

Evidence to be removed (unique to this case):
  - 1102b318a5fe2fc6...
  - 2401112d2c3bcc88...
  - 6d0f3bd3b8c1edcd...
  ... and 2 more

Run with --force to actually remove this evidence
```

**Warning**: This is a destructive operation. Always use `--dry-run` first!

---

### 2. Case Management (`case`)

Manage cases, view evidence inventory, and explore case metadata.

#### `evidence-toolkit case list`

List all cases in storage.

```bash
evidence-toolkit case list [--storage-dir PATH] [--detailed]
```

**Options**:
- `--detailed`: Show expanded information including evidence types

**Example (Standard)**:
```bash
$ evidence-toolkit case list

📁 Cases in Storage
================================================================================
CASE ID                        Evidence     Last Modified
--------------------------------------------------------------------------------
WORKPLACE-2024-003             8            2025-10-05 17:34
WORKPLACE-2024-002             12           2025-10-05 15:36
TEST-2024-001                  5            2025-10-05 14:29

Total: 3 case(s)
```

**Example (Detailed)**:
```bash
$ evidence-toolkit case list --detailed

📁 Cases in Storage
================================================================================

WORKPLACE-2024-003
  Evidence: 8 items (12.45 MB)
  Types: document, email, image
  Modified: 2025-10-05 17:34:22

WORKPLACE-2024-002
  Evidence: 12 items (24.67 MB)
  Types: document, email
  Modified: 2025-10-05 15:36:18
```

---

#### `evidence-toolkit case show`

Show detailed case information with evidence inventory.

```bash
evidence-toolkit case show CASE-ID [--storage-dir PATH] [--full-hash]
```

**Options**:
- `--full-hash`: Show full SHA256 hashes (default shows first 16 chars)

**Example**:
```bash
$ evidence-toolkit case show WORKPLACE-2024-003

📁 Case: WORKPLACE-2024-003
================================================================================
Evidence count: 8 items

1. complaint_email.eml
   Type: email
   SHA256: 1102b318a5fe2fc6...
   Size: 4.2 KB

2. investigation_notes.pdf
   Type: document
   SHA256: 2401112d2c3bcc88...
   Size: 156.8 KB
   Significance: high

3. evidence_photo.jpg
   Type: image
   SHA256: 6d0f3bd3b8c1edcd...
   Size: 2.1 MB
```

---

#### `evidence-toolkit case evidence`

Simple listing of evidence files in a case.

```bash
evidence-toolkit case evidence CASE-ID [--storage-dir PATH] [--full-hash]
```

**Example**:
```bash
$ evidence-toolkit case evidence WORKPLACE-2024-003

Evidence in case: WORKPLACE-2024-003
================================================================================
SHA256             Type         Filename
--------------------------------------------------------------------------------
1102b318a5fe2fc6...  email        complaint_email.eml
2401112d2c3bcc88...  document     investigation_notes.pdf
6d0f3bd3b8c1edcd...  image        evidence_photo.jpg
e81bd4176e3ec009...  document     witness_statement.txt
e95f4d83f8ccf8fc...  email        followup_thread.eml

Total: 5 item(s)
```

---

### 3. Batch Re-Analysis (`reanalyze`)

Re-run AI analysis on all evidence in a case (useful after OpenAI model updates or prompt improvements).

#### `evidence-toolkit reanalyze`

```bash
evidence-toolkit reanalyze --case-id CASE-ID [--storage-dir PATH] [--evidence-type TYPE] [--dry-run] [--quiet]
```

**Options**:
- `--case-id`: Case ID to re-analyze (required)
- `--evidence-type`: Filter by type (`all`, `document`, `image`, `email`) - default: `all`
- `--dry-run`: Preview what would be re-analyzed
- `--quiet`: Suppress verbose output

**What It Does**:
- Re-runs AI analysis on all evidence items in the case
- Backs up previous analysis results before overwriting
- Preserves chain of custody (adds re-analysis event)
- Requires `OPENAI_API_KEY` for AI analysis

**Example**:
```bash
$ evidence-toolkit reanalyze --case-id WORKPLACE-2024-003 --dry-run

Re-analyzing case: WORKPLACE-2024-003
Evidence items: 8
🔍 Dry run mode - no changes will be made

Would re-analyze:
  - 1102b318a5fe2fc6... (email): complaint_email.eml
  - 2401112d2c3bcc88... (document): investigation_notes.pdf
  - 6d0f3bd3b8c1edcd... (image): evidence_photo.jpg
  ... (5 more items)
```

**Use Cases**:
- After OpenAI model updates (e.g., `gpt-4.1-mini` improvements)
- After domain prompt refinements in `legal_config.py`
- When analysis confidence was low and you want to retry
- After fixing bugs in analysis code

---

## Updated Core Commands

The following existing commands have been **enhanced** in v3.0:

### `evidence-toolkit process-case`

**New Options**:
- `--skip-package`: Skip package generation (only ingest, analyze, correlate)
- `--actor`: Specify actor for chain of custody (default: `system`)

**Example**:
```bash
evidence-toolkit process-case data/cases/CASE-2024-001 \
  --case-id CASE-2024-001 \
  --actor "investigator@firm.com" \
  --skip-package
```

---

### `evidence-toolkit analyze`

**New Options**:
- `--force`: Force re-analysis even if analysis exists (backs up previous analysis)

**Example**:
```bash
evidence-toolkit analyze 1102b318a5fe2fc60aeaaaf71a4af94259c75be70874a44896180d71edf91087 \
  --case-id WORKPLACE-2024-003 \
  --force
```

---

## Command Comparison: v2.0 vs v3.0

| Feature | v2.0 | v3.0 |
|---------|------|------|
| **Storage Stats** | ❌ Not available | ✅ `storage stats` |
| **Storage Cleanup** | ❌ Manual only | ✅ `storage cleanup --dry-run` |
| **Case Pruning** | ❌ Manual deletion | ✅ `storage prune --case-id CASE` |
| **Case Listing** | ❌ Not available | ✅ `case list --detailed` |
| **Case Details** | ❌ Not available | ✅ `case show CASE-ID` |
| **Evidence Inventory** | ❌ Not available | ✅ `case evidence CASE-ID` |
| **Batch Re-analysis** | ❌ Manual scripting | ✅ `reanalyze --case-id CASE` |
| **Default Storage** | `evidence/` (hidden) | `data/storage/` (visible) |
| **CLI Size** | 1,229 lines | 438 lines (64% smaller) |

---

## Common Workflows

### Workflow 1: Case Health Check

```bash
# Check overall storage health
evidence-toolkit storage stats

# List all cases
evidence-toolkit case list --detailed

# Inspect specific case
evidence-toolkit case show WORKPLACE-2024-003

# Clean up broken links
evidence-toolkit storage cleanup --dry-run
evidence-toolkit storage cleanup --force  # If cleanup looks good
```

---

### Workflow 2: Case Cleanup After Settlement

```bash
# Review what would be removed (dry run)
evidence-toolkit storage prune --case-id SETTLED-2023-045 --dry-run

# Actually remove evidence (if case is closed and evidence is unique)
evidence-toolkit storage prune --case-id SETTLED-2023-045 --force

# Verify cleanup
evidence-toolkit storage stats
```

---

### Workflow 3: Re-analyze After Prompt Improvements

```bash
# Updated legal_config.py with better prompts
# Re-analyze all documents in a case

evidence-toolkit reanalyze \
  --case-id WORKPLACE-2024-003 \
  --evidence-type document \
  --dry-run

# Looks good - proceed
evidence-toolkit reanalyze \
  --case-id WORKPLACE-2024-003 \
  --evidence-type document
```

---

## Safety Features

All destructive operations include safety mechanisms:

1. **Dry-run by Default**: `cleanup` and `prune` default to `--dry-run`
2. **Explicit Force Required**: Must use `--force` flag to make changes
3. **Multi-case Protection**: `prune` preserves evidence shared across cases
4. **Backup Before Re-analysis**: Previous analysis backed up before overwrite
5. **Chain of Custody**: All operations logged in custody trail

---

## Migration Notes

### From v2.0 to v3.0

**Storage Location Changed**:
- Old: `evidence/` (gitignored, hidden)
- New: `data/storage/` (visible with `.gitkeep`)

**Command Name Changed**:
- Old: `document-analyzer`
- New: `evidence-toolkit`

**New Capabilities**:
- Storage management commands
- Case management commands
- Batch re-analysis
- Health monitoring
- Orphaned file detection

**Backward Compatibility**:
- Evidence format unchanged (SHA256 content-addressed)
- Analysis schema unchanged (`analysis.v1.json`)
- Chain of custody preserved
- Multi-case support maintained

---

## Performance Notes

- `storage stats`: Fast (reads metadata only, ~1-2 seconds for 100 evidence items)
- `case list`: Fast (filesystem scan, ~0.5 seconds)
- `reanalyze`: Slow (AI analysis, ~10-30 seconds per evidence item)
- `storage cleanup`: Fast (dry-run ~0.1 seconds, force ~0.5 seconds)

---

## Future Enhancements

Planned for v3.1:

- `evidence-toolkit export` - Export evidence to external formats
- `evidence-toolkit import` - Import from other forensic tools
- `evidence-toolkit verify` - Verify SHA256 integrity
- `evidence-toolkit backup` - Create storage backups
- `evidence-toolkit search` - Full-text search across evidence

---

**Documentation Generated**: 2025-10-05
**Evidence Toolkit Version**: 3.0.0
**License**: MIT
