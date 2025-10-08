# Evidence Ingestion Pipeline

## Overview

The ingestion pipeline is the entry point for all evidence processing in the Evidence Toolkit. It handles the transformation of raw evidence files into content-addressed, forensically tracked evidence stored in a deduplicating storage system. The ingestion process extracts metadata, computes SHA256 hashes for content addressing, initializes chain of custody tracking, and creates case-specific hard links for multi-case evidence reuse.

This module implements a clean, functional API extracted from the v2.0 monolithic CLI for v3.0's modular architecture.

## Purpose & Scope

### What Ingestion Does
- Computes SHA256 hash for content-addressed storage
- Extracts file metadata (size, timestamps, MIME type)
- Detects evidence type (document, image, email)
- Creates immutable evidence storage with chain of custody
- Handles both single files and entire directories
- Supports multi-case evidence association via hard links

### What Ingestion Does NOT Do
- Evidence analysis (delegated to analysis pipeline)
- File format conversion or modification
- Evidence validation (files are stored as-is)
- Network-based evidence acquisition

### Design Principles
1. **Immutability**: Original files are never modified
2. **Deduplication**: SHA256 prevents duplicate storage
3. **Traceability**: Chain of custody from first ingestion
4. **Multi-case**: Same evidence can belong to multiple cases

## Module Structure

```
evidence_toolkit/pipeline/ingest.py
│
├── ingest_evidence()        # Single file ingestion
├── ingest_directory()       # Batch directory ingestion
├── ingest_path()            # Smart router (file or directory)
└── print_ingestion_summary() # Human-readable results
```

### Integration Points
```
src/evidence_toolkit/
├── pipeline/
│   └── ingest.py            # This module
│
├── core/
│   ├── storage.py           # EvidenceStorage.ingest_file()
│   ├── models.py            # IngestionResult, FileMetadata
│   └── utils.py             # detect_file_type()
│
└── cli.py                   # CLI commands → ingest_path()
```

## API Reference

### `ingest_evidence()`

Ingest a single file into evidence storage.

**Signature:**
```python
def ingest_evidence(
    file_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system"
) -> IngestionResult
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file_path` | `Path` | Yes | - | Path to file to ingest |
| `storage` | `EvidenceStorage` | Yes | - | EvidenceStorage instance for storage operations |
| `case_id` | `Optional[str]` | No | `None` | Case ID to associate with this evidence |
| `actor` | `str` | No | `"system"` | Actor performing the ingestion (for chain of custody) |

**Returns:**

| Type | Description |
|------|-------------|
| `IngestionResult` | Pydantic model with SHA256, file path, evidence type, success status, and message |

**Exceptions:**

| Exception | When Raised |
|-----------|-------------|
| `FileNotFoundError` | If file_path does not exist |
| `PermissionError` | If file cannot be read due to permissions |

**Example:**
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_evidence

storage = EvidenceStorage()
result = ingest_evidence(
    file_path=Path("data/cases/CASE-001/document.pdf"),
    storage=storage,
    case_id="CASE-001",
    actor="investigator@example.com"
)

print(f"SHA256: {result.sha256}")
print(f"Type: {result.evidence_type}")
print(f"Success: {result.success}")
```

---

### `ingest_directory()`

Ingest all files from a directory into evidence storage (recursive).

**Signature:**
```python
def ingest_directory(
    directory_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system",
    quiet: bool = False
) -> List[IngestionResult]
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `directory_path` | `Path` | Yes | - | Path to directory containing files |
| `storage` | `EvidenceStorage` | Yes | - | EvidenceStorage instance for storage operations |
| `case_id` | `Optional[str]` | No | `None` | Case ID to associate with all evidence |
| `actor` | `str` | No | `"system"` | Actor performing the ingestion |
| `quiet` | `bool` | No | `False` | Suppress verbose output |

**Returns:**

| Type | Description |
|------|-------------|
| `List[IngestionResult]` | List of IngestionResult objects, one per file ingested |

**Behavior:**
- Recursively walks directory using `Path.rglob('*')`
- Skips hidden files (starting with `.`)
- Processes only regular files (skips directories, symlinks)
- Collects results for all files

**Example:**
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_directory

storage = EvidenceStorage()
results = ingest_directory(
    directory_path=Path("data/cases/CASE-001"),
    storage=storage,
    case_id="CASE-001",
    quiet=False
)

successful = [r for r in results if r.success]
print(f"Ingested {len(successful)}/{len(results)} files")
```

---

### `ingest_path()`

Convenience router that ingests from either a file or directory path.

**Signature:**
```python
def ingest_path(
    input_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system",
    quiet: bool = False
) -> List[IngestionResult]
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `input_path` | `Path` | Yes | - | Path to file or directory |
| `storage` | `EvidenceStorage` | Yes | - | EvidenceStorage instance |
| `case_id` | `Optional[str]` | No | `None` | Case ID to associate with evidence |
| `actor` | `str` | No | `"system"` | Actor performing ingestion |
| `quiet` | `bool` | No | `False` | Suppress verbose output |

**Returns:**

| Type | Description |
|------|-------------|
| `List[IngestionResult]` | List of IngestionResult objects (single item for file, multiple for directory) |

**Exceptions:**

| Exception | When Raised |
|-----------|-------------|
| `FileNotFoundError` | If input_path doesn't exist |
| `ValueError` | If input_path is neither file nor directory (e.g., symlink) |

**Routing Logic:**
```python
if input_path.is_file():
    # Route to ingest_evidence() → returns [single result]
elif input_path.is_dir():
    # Route to ingest_directory() → returns [multiple results]
else:
    raise ValueError(...)
```

**Example:**
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_path

storage = EvidenceStorage()

# Works with file
results = ingest_path(Path("document.pdf"), storage, case_id="CASE-001")

# Works with directory
results = ingest_path(Path("data/cases/CASE-001"), storage, case_id="CASE-001")
```

---

### `print_ingestion_summary()`

Print human-readable summary of ingestion results.

**Signature:**
```python
def print_ingestion_summary(
    results: List[IngestionResult],
    quiet: bool = False
) -> None
```

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `results` | `List[IngestionResult]` | Yes | - | List of IngestionResult objects |
| `quiet` | `bool` | No | `False` | Suppress output |

**Output Format:**
```
📥 Ingestion Summary:
   Files processed: 10
   Successfully ingested: 9
   Failed: 1

✅ Successfully ingested:
   2401112d2c3b... (document) - /path/to/file1.pdf
   7f3a8b9e1c4d... (image) - /path/to/image1.jpg
   ... and 7 more

❌ Failed to ingest:
   /path/to/corrupt.file: Invalid file format
```

**Example:**
```python
from evidence_toolkit.pipeline import ingest_directory, print_ingestion_summary

results = ingest_directory(Path("data/cases/CASE-001"), storage, case_id="CASE-001")
print_ingestion_summary(results)
```

## Data Models

### `IngestionResult` (from `core/models.py`)

```python
class IngestionResult(BaseModel):
    """Result of evidence ingestion."""
    sha256: str
    file_path: str
    evidence_type: EvidenceType
    metadata: Optional[FileMetadata] = None
    success: bool = True
    message: str = "Success"
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `sha256` | `str` | SHA256 hash of the ingested file (content addressing key) |
| `file_path` | `str` | Original file path (absolute) |
| `evidence_type` | `EvidenceType` | Detected type (DOCUMENT, IMAGE, EMAIL, UNKNOWN) |
| `metadata` | `Optional[FileMetadata]` | Extracted file metadata (size, timestamps, MIME type) |
| `success` | `bool` | Whether ingestion succeeded |
| `message` | `str` | Human-readable status message |

### `FileMetadata` (from `core/models.py`)

```python
class FileMetadata(BaseModel):
    """File metadata extracted during ingestion."""
    filename: str
    file_size: int
    mime_type: str
    file_extension: str
    created_timestamp: Optional[datetime]
    modified_timestamp: Optional[datetime]
    sha256: str
```

## Behavior

### Ingestion Flow

```
User provides file/directory path
  ↓
ingest_path() routes to appropriate function
  ↓
For each file:
  ├─→ Compute SHA256 hash
  ├─→ Check if already ingested (by SHA256)
  │   ├─→ If exists: Skip or add to new case
  │   └─→ If new: Continue ingestion
  ├─→ Detect evidence type (document/image/email)
  ├─→ Extract metadata (size, timestamps, MIME)
  ├─→ Store original file: raw/sha256=<hash>/original.{ext}
  ├─→ Save metadata: derived/sha256=<hash>/metadata.json
  ├─→ Initialize chain of custody
  ├─→ Create case hard link (if case_id provided)
  └─→ Return IngestionResult
  ↓
Collect all results → print_ingestion_summary()
```

### Deduplication Logic

The ingestion pipeline automatically deduplicates evidence using SHA256 hashing:

```python
# EvidenceStorage.ingest_file() checks for existing evidence
existing_sha256 = storage.get_sha256_by_content(file_path)

if existing_sha256:
    # Evidence already exists
    if case_id and case_id not in storage.get_case_ids(existing_sha256):
        # Add to new case (creates hard link only)
        storage.add_evidence_to_case(existing_sha256, case_id)
    return IngestionResult(
        sha256=existing_sha256,
        success=True,
        message="Evidence already ingested (added to case if new)"
    )
else:
    # New evidence - full ingestion
    # ... (copy file, extract metadata, etc.)
```

**Benefits:**
- Saves disk space (no duplicate files)
- Consistent analysis (same evidence, same SHA256)
- Multi-case reuse (hard links, not copies)

### Chain of Custody Initialization

Every ingestion creates an initial chain of custody event:

```json
{
  "timestamp": "2025-10-05T14:30:00.123456Z",
  "action": "ingest",
  "actor": "investigator@example.com",
  "details": "Evidence ingested into content-addressed storage",
  "metadata": {
    "original_path": "/path/to/document.pdf",
    "case_id": "CASE-001",
    "evidence_type": "document"
  }
}
```

Stored at:
```
data/storage/derived/sha256=<hash>/chain_of_custody.json
```

## Storage Layout

### Before Ingestion
```
data/cases/CASE-001/
├── document.pdf
├── image.jpg
└── email.eml
```

### After Ingestion
```
data/storage/
├── raw/
│   ├── sha256=2401112d.../
│   │   └── original.pdf       # document.pdf
│   ├── sha256=7f3a8b9e.../
│   │   └── original.jpg       # image.jpg
│   └── sha256=9c8d6e5f.../
│       └── original.eml       # email.eml
│
├── derived/
│   ├── sha256=2401112d.../
│   │   ├── metadata.json
│   │   └── chain_of_custody.json
│   ├── sha256=7f3a8b9e.../
│   │   ├── metadata.json
│   │   └── chain_of_custody.json
│   └── sha256=9c8d6e5f.../
│       ├── metadata.json
│       └── chain_of_custody.json
│
└── cases/
    └── CASE-001/
        ├── 2401112d....pdf    # Hard link to raw/sha256=.../original.pdf
        ├── 7f3a8b9e....jpg    # Hard link to raw/sha256=.../original.jpg
        └── 9c8d6e5f....eml    # Hard link to raw/sha256=.../original.eml
```

**Key Points:**
- Original files stored ONCE in `raw/`
- Case links are hard links (no disk duplication)
- Metadata and chain of custody in `derived/`
- SHA256 prefix used for directory names (collision-resistant)

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `FileNotFoundError` | Input path doesn't exist | Verify path, check permissions |
| `PermissionError` | Cannot read file | Check file permissions, run as appropriate user |
| `OSError` (disk full) | Insufficient disk space | Free disk space, clean old evidence |
| `ValueError` (type detection fails) | Unsupported file format | Add type detection rules or use UNKNOWN type |

### Error Handling Pattern

```python
try:
    result = ingest_evidence(file_path, storage, case_id)
    if result.success:
        print(f"✅ Ingested: {result.sha256[:12]}...")
    else:
        print(f"⚠️  Partial success: {result.message}")
except FileNotFoundError as e:
    print(f"❌ File not found: {e}")
except PermissionError as e:
    print(f"❌ Permission denied: {e}")
```

### Logging

Ingestion operations use emoji-prefixed output:
- `📥` - Ingestion operations
- `✅` - Success
- `⚠️` - Warning (already exists, added to case)
- `❌` - Error (failed to ingest)

## Performance Considerations

### Time Complexity
- **Single file**: O(n) where n = file size (SHA256 hashing)
- **Directory**: O(m × n) where m = number of files, n = average file size
- **Dominant operation**: SHA256 computation (~200 MB/s on modern hardware)

### Space Complexity
- **Disk usage**: 2× file size for new evidence (original + hard link)
- **Memory**: Minimal (streaming file read for SHA256)
- **Deduplication savings**: Shared evidence requires only 1 copy

### Optimization Notes
- SHA256 uses streaming (doesn't load entire file into memory)
- Hard links eliminate duplicate storage
- Metadata extraction is lazy (only when needed)
- Directory scanning uses `rglob()` (efficient recursive walk)

### Performance Example

```python
# Ingest 100 documents (average 1 MB each)
# Expected time: ~5 seconds (SHA256 dominant)
# Disk usage: ~200 MB (100 originals + 100 hard links)

# If 50 documents are duplicates:
# Actual disk usage: ~100 MB (50 unique files, 100 hard links)
# Deduplication savings: 50%
```

## Testing

### Unit Tests

```python
import tempfile
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_evidence

def test_ingest_single_file():
    """Test single file ingestion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage(base_dir=Path(tmpdir))

        # Create test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("Test evidence content")

        # Ingest
        result = ingest_evidence(test_file, storage, case_id="TEST-001")

        # Verify
        assert result.success
        assert result.evidence_type == EvidenceType.DOCUMENT
        assert len(result.sha256) == 64  # SHA256 is 64 hex chars

        # Verify storage
        assert storage.get_original_file_path(result.sha256).exists()
        assert storage.get_metadata(result.sha256) is not None

def test_ingest_deduplication():
    """Test deduplication of identical files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = EvidenceStorage(base_dir=Path(tmpdir))

        # Create two identical files
        file1 = Path(tmpdir) / "file1.txt"
        file2 = Path(tmpdir) / "file2.txt"
        file1.write_text("Same content")
        file2.write_text("Same content")

        # Ingest both
        result1 = ingest_evidence(file1, storage, case_id="CASE-A")
        result2 = ingest_evidence(file2, storage, case_id="CASE-B")

        # Same SHA256 (deduplication)
        assert result1.sha256 == result2.sha256

        # Both cases have access
        case_a_evidence = storage.get_case_evidence("CASE-A")
        case_b_evidence = storage.get_case_evidence("CASE-B")
        assert result1.sha256 in case_a_evidence
        assert result1.sha256 in case_b_evidence
```

### Integration Tests

```bash
# Test full ingestion pipeline
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify results
uv run evidence-toolkit list --case-id TEST-CASE
```

### Test Coverage
- Single file ingestion: ✅ Covered
- Directory ingestion: ✅ Covered
- Deduplication: ✅ Covered
- Multi-case association: ✅ Covered
- Error handling: ⚠️ Partial (needs more edge cases)

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.storage.EvidenceStorage` - Storage operations
- `evidence_toolkit.core.models.IngestionResult` - Return type
- `evidence_toolkit.core.models.FileMetadata` - Metadata model
- `evidence_toolkit.core.utils.detect_file_type` - Type detection

### External Dependencies
- `pathlib.Path` - Path operations
- `hashlib.sha256` - Content hashing (via storage)

## CLI Integration

The ingestion pipeline is exposed via CLI commands:

```bash
# Ingest single file
uv run evidence-toolkit ingest data/cases/CASE-001/doc.pdf --case-id CASE-001

# Ingest directory
uv run evidence-toolkit ingest data/cases/CASE-001 --case-id CASE-001

# Ingest without case association
uv run evidence-toolkit ingest evidence.pdf
```

**CLI Implementation** (`cli.py`):
```python
@app.command()
def ingest(
    path: Path,
    case_id: Optional[str] = None,
    quiet: bool = False
):
    """Ingest evidence into storage."""
    storage = EvidenceStorage()
    results = ingest_path(path, storage, case_id=case_id, quiet=quiet)
    print_ingestion_summary(results, quiet=quiet)
```

## Migration Notes

### v2.0 → v3.0 Changes

**Old (v2.0):**
```python
# Monolithic CLI function
from document_analyzer.cli import ingest_command
ingest_command(path="...", case_id="...")
```

**New (v3.0):**
```python
# Modular pipeline function
from evidence_toolkit.pipeline import ingest_path
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
results = ingest_path(Path("..."), storage, case_id="...")
```

**Breaking Changes:**
- Function signature changed (now requires `storage` parameter)
- Return type changed (now returns `List[IngestionResult]`)
- Import path changed (`document_analyzer.cli` → `evidence_toolkit.pipeline`)

**Migration Helper:**
```python
# v2.0 code
from document_analyzer.cli import ingest_command
ingest_command(path="data/cases/MY-CASE", case_id="MY-CASE")

# v3.0 equivalent
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_path, print_ingestion_summary

storage = EvidenceStorage()
results = ingest_path(Path("data/cases/MY-CASE"), storage, case_id="MY-CASE")
print_ingestion_summary(results)
```

## Future Considerations

### Planned Enhancements
- **Parallel ingestion**: Process multiple files concurrently
- **Progress bars**: Visual feedback for large directories
- **Ingestion profiles**: Pre-configured settings for common scenarios
- **Cloud storage**: Support for S3/Azure Blob ingestion
- **Incremental updates**: Re-ingest only modified files

### Known Limitations
- No support for remote files (must be local)
- No streaming ingestion (entire file read for SHA256)
- No partial file support (ingests complete files only)
- Hard links require same filesystem (no cross-volume)

### Technical Debt
- Type detection could be more robust (currently basic MIME + extension)
- Error messages could be more descriptive
- No ingestion hooks/plugins system

## Examples

### Example 1: Basic Ingestion
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_path

storage = EvidenceStorage()
results = ingest_path(
    input_path=Path("data/cases/CASE-001/document.pdf"),
    storage=storage,
    case_id="CASE-001",
    actor="investigator@example.com"
)

for result in results:
    print(f"SHA256: {result.sha256}")
    print(f"Type: {result.evidence_type}")
```

### Example 2: Batch Ingestion with Summary
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_directory, print_ingestion_summary

storage = EvidenceStorage()
results = ingest_directory(
    directory_path=Path("data/cases/CASE-001"),
    storage=storage,
    case_id="CASE-001",
    quiet=False
)

print_ingestion_summary(results)
```

### Example 3: Multi-Case Evidence Reuse
```python
from pathlib import Path
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline import ingest_evidence

storage = EvidenceStorage()

# Ingest for Case A
doc = Path("shared_evidence/contract.pdf")
result = ingest_evidence(doc, storage, case_id="CASE-A")
sha256 = result.sha256

# Add same evidence to Case B (by SHA256)
storage.add_evidence_to_case(sha256, "CASE-B")

# Both cases reference the same file (no duplication)
print(f"Evidence {sha256[:12]}... belongs to:")
print(f"  - Case A: {storage.case_has_evidence('CASE-A', sha256)}")
print(f"  - Case B: {storage.case_has_evidence('CASE-B', sha256)}")
```

---

**This documentation provides complete reference for the ingestion pipeline, covering all functions, models, behaviors, and usage patterns in Evidence Toolkit v3.0.**
