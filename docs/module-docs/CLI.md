# Documentation: CLI (Command Line Interface)

## Overview

The Evidence Toolkit CLI (`src/evidence_toolkit/cli.py`) is the primary user interface for the Evidence Toolkit v3.0. It provides a clean, intuitive command-line interface that delegates all business logic to pipeline components. The CLI is built with Click and provides comprehensive commands for evidence ingestion, AI analysis, cross-evidence correlation, client package generation, and storage management.

The CLI follows v3.0's clean architecture principles: thin wrapper for argument parsing and user feedback, with all processing logic delegated to specialized pipeline modules.

## Purpose & Scope

### What It Does
- Provides user-friendly command-line interface for all Evidence Toolkit operations
- Validates user inputs and command-line arguments
- Orchestrates pipeline components (ingest, analyze, correlate, package)
- Displays progress, status, and results to users with rich formatting
- Manages storage operations (stats, cleanup, pruning)
- Handles case and evidence listing and inspection

### What It Does NOT Do
- Does NOT contain business logic (all in pipeline modules)
- Does NOT directly manipulate evidence files (delegates to EvidenceStorage)
- Does NOT perform AI analysis (delegates to analyzers)
- Does NOT make storage decisions (delegates to storage layer)

## Usage

### CLI Installation

```bash
# Install evidence-toolkit package
uv pip install -e .

# Verify installation
uv run evidence-toolkit --help
evidence-toolkit version
```

### Core Commands

#### 1. Process Complete Case (Full Pipeline)

```bash
# Complete pipeline: ingest → analyze → correlate → package
uv run evidence-toolkit process-case data/cases/ACME-001 --case-id ACME-001

# With custom output directory
uv run evidence-toolkit process-case data/cases/ACME-001 \
  --case-id ACME-001 \
  --output-dir ./deliverables

# Skip packaging (only analyze)
uv run evidence-toolkit process-case data/cases/ACME-001 \
  --case-id ACME-001 \
  --skip-package

# Quiet mode (minimal output)
uv run evidence-toolkit process-case data/cases/ACME-001 \
  --case-id ACME-001 \
  --quiet
```

#### 2. Ingest Evidence

```bash
# Ingest single file
uv run evidence-toolkit ingest document.pdf --case-id ACME-001

# Ingest entire directory
uv run evidence-toolkit ingest data/cases/ACME-001 --case-id ACME-001

# Ingest without case association
uv run evidence-toolkit ingest evidence/photo.jpg
```

#### 3. Analyze Evidence

```bash
# Analyze by SHA256 hash (auto-detect type)
uv run evidence-toolkit analyze a1b2c3d4... --case-id ACME-001

# Specify evidence type explicitly
uv run evidence-toolkit analyze a1b2c3d4... \
  --case-id ACME-001 \
  --type document

# Force re-analysis
uv run evidence-toolkit analyze a1b2c3d4... \
  --case-id ACME-001 \
  --force
```

#### 4. Correlate Evidence

```bash
# Run cross-evidence correlation
uv run evidence-toolkit correlate --case-id ACME-001

# Save correlation results to JSON
uv run evidence-toolkit correlate \
  --case-id ACME-001 \
  --json-output correlations.json

# Quiet mode
uv run evidence-toolkit correlate --case-id ACME-001 --quiet
```

#### 5. Generate Client Package

```bash
# Create ZIP package with analysis
uv run evidence-toolkit package --case-id ACME-001

# Include raw evidence files
uv run evidence-toolkit package \
  --case-id ACME-001 \
  --include-raw

# Create directory instead of ZIP
uv run evidence-toolkit package \
  --case-id ACME-001 \
  --format directory

# Custom output location
uv run evidence-toolkit package \
  --case-id ACME-001 \
  --output-dir ./deliverables
```

### Storage Management Commands

#### Storage Stats

```bash
# View storage statistics
uv run evidence-toolkit storage stats

# Custom storage directory
uv run evidence-toolkit storage stats --storage-dir /custom/path
```

#### Storage Cleanup

```bash
# Dry run (preview changes)
uv run evidence-toolkit storage cleanup

# Actually perform cleanup
uv run evidence-toolkit storage cleanup --force
```

#### Prune Case Evidence

```bash
# Preview what would be removed
uv run evidence-toolkit storage prune --case-id ACME-001

# Actually remove evidence unique to case
uv run evidence-toolkit storage prune --case-id ACME-001 --force
```

### Case Management Commands

#### List Cases

```bash
# List all cases
uv run evidence-toolkit case list

# Detailed view with evidence types
uv run evidence-toolkit case list --detailed
```

#### Show Case Details

```bash
# Show case information
uv run evidence-toolkit case show ACME-001

# Show full SHA256 hashes
uv run evidence-toolkit case show ACME-001 --full-hash
```

#### List Case Evidence

```bash
# List evidence in case
uv run evidence-toolkit case evidence ACME-001

# With full hashes
uv run evidence-toolkit case evidence ACME-001 --full-hash
```

### Re-Analysis Commands

```bash
# Re-analyze all evidence in case
uv run evidence-toolkit reanalyze --case-id ACME-001

# Re-analyze only documents
uv run evidence-toolkit reanalyze \
  --case-id ACME-001 \
  --evidence-type document

# Preview what would be re-analyzed
uv run evidence-toolkit reanalyze \
  --case-id ACME-001 \
  --dry-run
```

## Architecture

### Module Structure

```
src/evidence_toolkit/
├── cli.py                  # THIS MODULE - CLI entry point
├── pipeline/
│   ├── ingest.py          # Called by: ingest, process-case
│   ├── analyze.py         # Called by: analyze, process-case, reanalyze
│   └── package.py         # Called by: package, process-case
├── analyzers/
│   └── correlation.py     # Called by: correlate, process-case
└── core/
    ├── storage.py         # Used by: all commands
    └── models.py          # Type definitions
```

### Command Groups

The CLI is organized into three command groups:

1. **Main Commands** (`cli` group):
   - `process-case` - Full pipeline
   - `ingest` - File ingestion
   - `analyze` - Evidence analysis
   - `correlate` - Cross-evidence correlation
   - `package` - Client package generation
   - `reanalyze` - Batch re-analysis
   - `version` - Version information

2. **Storage Group** (`storage` subcommand):
   - `storage stats` - Storage statistics
   - `storage cleanup` - Cleanup operations
   - `storage prune` - Remove case evidence

3. **Case Group** (`case` subcommand):
   - `case list` - List all cases
   - `case show` - Show case details
   - `case evidence` - List case evidence

### Data Flow

```
User Input → CLI Parser (Click) → Pipeline Modules → EvidenceStorage → File System
                                         ↓
                                   AI Analyzers (OpenAI)
                                         ↓
                                  User Output (Click)
```

## API Reference

### Main Commands

#### `process-case`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| case_directory | Path | Yes | - | Directory containing evidence files |
| --case-id | str | Yes | - | Case identifier |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --output-dir | str | No | ./data/packages | Output directory for package |
| --skip-package | flag | No | False | Skip package generation step |
| --actor | str | No | system | Actor performing processing |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
1. Ingests all files from `case_directory`
2. Analyzes evidence with OpenAI (documents, images, emails)
3. Runs cross-evidence correlation
4. Generates client package (unless --skip-package)
5. Displays summary with timing and counts

**Return:** Exit code 0 on success, 1 on failure

**Example:**
```bash
uv run evidence-toolkit process-case data/cases/ACME-001 --case-id ACME-001
```

#### `ingest`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_path | Path | Yes | - | File or directory to ingest |
| --case-id | str | No | None | Case ID to associate with evidence |
| --actor | str | No | system | Actor performing ingestion |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
1. Computes SHA256 hash of each file
2. Stores in content-addressed storage (deduplication automatic)
3. Creates hard links in cases/ directory if --case-id provided
4. Records chain of custody events

**Return:** Exit code 0 on success, 1 on failure

**Example:**
```bash
uv run evidence-toolkit ingest email.eml --case-id ACME-001
```

#### `analyze`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| sha256 | str | Yes | - | SHA256 hash of evidence to analyze |
| --case-id | str | No | None | Case ID to associate with analysis |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --type | str | No | auto | Evidence type (auto/document/image/email) |
| --force | flag | No | False | Force re-analysis even if exists |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
1. Loads evidence file from storage
2. Auto-detects evidence type (unless --type specified)
3. Calls appropriate analyzer (DocumentAnalyzer, ImageAnalyzer, EmailAnalyzer)
4. Saves analysis results to derived/ directory
5. Records chain of custody event

**Return:** Exit code 0 on success, 1 on failure

**Example:**
```bash
uv run evidence-toolkit analyze a1b2c3d4e5f6... --case-id ACME-001
```

#### `correlate`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --case-id | str | Yes | - | Case ID to analyze for correlations |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --json-output | Path | No | None | Save correlation results as JSON |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
1. Loads all evidence for specified case
2. Extracts entities from all analysis results
3. Correlates entities across evidence types
4. Reconstructs timeline from all temporal events
5. Detects patterns with AI (if OpenAI available)
6. Displays top correlations and timeline summary

**Return:** Exit code 0 on success, 1 on failure

**Example:**
```bash
uv run evidence-toolkit correlate --case-id ACME-001 --json-output results.json
```

#### `package`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --case-id | str | Yes | - | Case ID to package |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --output-dir | str | No | ./data/packages | Output directory |
| --include-raw | flag | No | False | Include original evidence files |
| --format | str | No | zip | Package format (zip/directory) |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
1. Loads all evidence and analysis for case
2. Generates executive summary with OpenAI
3. Creates package structure with analysis JSON
4. Optionally includes raw evidence files
5. Creates ZIP archive or directory

**Return:** Exit code 0 on success, 1 on failure

**Example:**
```bash
uv run evidence-toolkit package --case-id ACME-001 --include-raw
```

### Storage Commands

#### `storage stats`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --storage-dir | str | No | data/storage | Evidence storage directory |

**Output:**
- Total evidence count and size
- Evidence counts by type (document/image/email)
- Storage breakdown (raw vs derived)
- Case count
- Label count
- Orphaned file count

**Example:**
```bash
uv run evidence-toolkit storage stats
```

#### `storage cleanup`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --dry-run | flag | No | True | Preview changes without applying |
| --force | flag | No | False | Actually perform cleanup |

**Behavior:**
- Removes broken hard links in labels/
- Removes empty label directories
- Reports orphaned evidence files (not linked to any case)
- Default mode is dry-run for safety

**Example:**
```bash
# Preview
uv run evidence-toolkit storage cleanup

# Execute
uv run evidence-toolkit storage cleanup --force
```

#### `storage prune`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --case-id | str | Yes | - | Case ID to prune evidence for |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --dry-run | flag | No | True | Preview changes without applying |
| --force | flag | No | False | Actually remove evidence |

**Behavior:**
- Only removes evidence UNIQUE to specified case
- Preserves evidence shared with other cases
- Removes raw files, derived analysis, and case links
- Default mode is dry-run for safety

**Warning:** Destructive operation - use --dry-run first!

**Example:**
```bash
# Preview
uv run evidence-toolkit storage prune --case-id OLD-CASE

# Execute
uv run evidence-toolkit storage prune --case-id OLD-CASE --force
```

### Case Commands

#### `case list`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --detailed | flag | No | False | Show detailed information |

**Output:**
- Table format: Case ID, Evidence count, Last modified
- Detailed mode: Evidence types, file sizes

**Example:**
```bash
uv run evidence-toolkit case list --detailed
```

#### `case show`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| case_id | str | Yes | - | Case ID to display |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --full-hash | flag | No | False | Show full SHA256 hashes |

**Output:**
- Evidence inventory with filenames
- Evidence types and file sizes
- SHA256 hashes (truncated or full)
- Legal significance ratings

**Example:**
```bash
uv run evidence-toolkit case show ACME-001 --full-hash
```

#### `case evidence`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| case_id | str | Yes | - | Case ID to display |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --full-hash | flag | No | False | Show full SHA256 hashes |

**Output:**
- Simple table: SHA256, Type, Filename
- Lighter weight than `case show`

**Example:**
```bash
uv run evidence-toolkit case evidence ACME-001
```

### Re-Analysis Command

#### `reanalyze`

**Arguments:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| --case-id | str | Yes | - | Case ID to re-analyze |
| --storage-dir | str | No | data/storage | Evidence storage directory |
| --evidence-type | str | No | all | Filter by type (all/document/image/email) |
| --dry-run | flag | No | False | Preview what would be re-analyzed |
| --quiet | flag | No | False | Suppress verbose output |

**Behavior:**
- Re-runs AI analysis on all evidence in case
- Previous analysis results are backed up before overwriting
- Can filter by evidence type
- Useful after prompt improvements or model updates

**Example:**
```bash
# Preview
uv run evidence-toolkit reanalyze --case-id ACME-001 --dry-run

# Re-analyze all documents
uv run evidence-toolkit reanalyze --case-id ACME-001 --evidence-type document
```

## Behavior

### Core Functionality

#### 1. Argument Parsing with Click

The CLI uses Click decorators for:
- Command registration (`@cli.command()`, `@cli.group()`)
- Argument validation (`type=click.Path(exists=True)`)
- Option parsing (`@click.option()`)
- Help text generation (automatic from docstrings)

#### 2. Pipeline Delegation

All business logic is delegated to pipeline modules:

```python
# CLI only orchestrates - does not implement logic
from evidence_toolkit.pipeline import ingest_path, analyze_evidence, PackageGenerator
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer

# Example: analyze command delegates to pipeline
def analyze_cmd(sha256, ...):
    analyze_evidence(sha256=sha256, storage=storage, ...)
```

#### 3. User Feedback

Rich console output with:
- Progress indicators (e.g., "Analyzing 12/45...")
- Status emojis (✅ ❌ ⚠️ 🔍 📦)
- Formatted tables (case lists, evidence lists)
- Summary statistics (timing, counts, sizes)
- Error messages with troubleshooting hints

#### 4. OpenAI Client Initialization

```python
# Graceful handling of missing OPENAI_API_KEY
openai_client = None
try:
    import openai
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
except ImportError:
    # Continues without AI analysis
    pass
```

### Data Flow

#### Full Pipeline (`process-case`)

```
User Command
    ↓
CLI Parser (Click)
    ↓
[1/4] Ingest Evidence
    → ingest_path() → EvidenceStorage.ingest_file()
    → Compute SHA256, store in raw/, link to cases/
    ↓
[2/4] Analyze Evidence
    → analyze_evidence() → DocumentAnalyzer/ImageAnalyzer/EmailAnalyzer
    → OpenAI API calls → Save to derived/
    ↓
[3/4] Cross-Evidence Correlation
    → CorrelationAnalyzer.analyze_case_correlations()
    → Entity extraction, timeline reconstruction, AI pattern detection
    ↓
[4/4] Generate Client Package
    → PackageGenerator.create_client_package()
    → Executive summary (OpenAI), package structure, ZIP creation
    ↓
Summary Output
```

### State Management

The CLI is **stateless** - it does not maintain any state between commands. All state is managed by:
- **EvidenceStorage**: File system storage (data/storage/)
- **Pipeline modules**: Temporary state during processing
- **Analysis files**: Persistent JSON in derived/ directories

### Error Handling

The CLI handles errors at multiple levels:

1. **Argument Validation**: Click validates types and paths before execution
2. **Try/Except Blocks**: Each command wraps operations in try/except
3. **Exit Codes**: Returns 0 on success, 1 on failure
4. **User-Friendly Messages**: Clear error messages with troubleshooting hints

Example:
```python
try:
    results = ingest_path(case_directory, storage, ...)
except Exception as e:
    click.echo(f"❌ Ingestion failed: {e}", err=True)
    sys.exit(1)
```

## AI Integration

### OpenAI Client Initialization

The CLI initializes the OpenAI client for commands that need AI analysis:

```python
import openai
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    openai_client = openai.OpenAI(api_key=api_key)
else:
    openai_client = None  # Graceful degradation
```

**Commands Using OpenAI:**
- `process-case` - Analysis and executive summary
- `analyze` - Evidence analysis
- `correlate` - Pattern detection (v3.1 feature)
- `package` - Executive summary generation
- `reanalyze` - Batch re-analysis

### Graceful Degradation

If OpenAI is not available:
- Commands continue but skip AI analysis
- Users see warning: "⚠️ OPENAI_API_KEY not set - AI analysis disabled"
- Metadata and file operations still work
- No crashes or failures

## Validation & Compliance

### Input Validation

Click provides automatic validation:

```python
@click.argument('case_directory', type=click.Path(exists=True, path_type=Path))
```

- Path existence checking
- Type conversion (str → Path)
- Choice constraints (e.g., `type=click.Choice(['zip', 'directory'])`)

### Chain of Custody

The CLI records chain of custody events for all operations:

```python
# Ingestion records custody event
custody_event = ChainOfCustodyEvent(
    timestamp=datetime.now(),
    event_type='ingestion',
    actor=actor,
    description=f"Ingested as case {case_id}"
)
```

**Custody Events:**
- Ingestion: File added to storage
- Analysis: AI analysis performed
- Case association: Evidence linked to case
- Re-analysis: Previous analysis overwritten (with backup)

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `Case not found: {case_id}` | No evidence for specified case | Verify case ID with `case list` |
| `OPENAI_API_KEY not set` | Missing environment variable | Set `export OPENAI_API_KEY=sk-...` |
| `Ingestion failed: Permission denied` | Insufficient file permissions | Check file permissions, run as appropriate user |
| `Analysis failed: {sha256}` | Evidence file missing or corrupted | Re-ingest evidence file |
| `Package generation failed` | Missing analysis data | Run `analyze` command first |

### Logging

The CLI uses Click's `click.echo()` for output:

- **Standard output**: Progress, results, summaries
- **Error output**: `click.echo(..., err=True)` for errors and warnings
- **Quiet mode**: `--quiet` flag suppresses all non-essential output

No file-based logging - all output is to stdout/stderr for easy redirection:

```bash
# Redirect output to log file
uv run evidence-toolkit process-case data/cases/ACME-001 --case-id ACME-001 > process.log 2>&1

# Capture only errors
uv run evidence-toolkit process-case data/cases/ACME-001 --case-id ACME-001 2> errors.log
```

## Performance Considerations

### Time Complexity

- **Ingestion**: O(n) where n = number of files (hash computation is linear)
- **Analysis**: O(n * A) where A = AI analysis time (typically 2-10 seconds per item)
- **Correlation**: O(n * m) where m = average entities per evidence item
- **Package**: O(n) for file copying, O(1) for executive summary

### Space Complexity

- **Ingestion**: O(1) - uses hard links, no duplication
- **Analysis**: O(n) - stores JSON analysis for each evidence item
- **Package**: O(n) if --include-raw, O(1) otherwise (just analysis JSON)

### Optimization Notes

1. **Parallel Processing**: Not currently implemented
   - Future: Could parallelize analysis with ThreadPoolExecutor
   - AI API calls are network-bound, good candidate for concurrency

2. **Incremental Analysis**: Already implemented
   - Skips already-analyzed evidence (checks for analysis.v1.json)
   - Only re-analyzes if --force flag used

3. **Deduplication**: Automatic via content-addressing
   - Same file ingested multiple times creates only one raw copy
   - Storage savings can be significant for duplicate evidence

## Storage & Persistence

### File Locations

```
data/storage/
├── raw/sha256=<hash>/
│   └── original.{ext}          # Original evidence file
├── derived/sha256=<hash>/
│   ├── metadata.json           # File metadata
│   ├── analysis.v1.json        # AI analysis results
│   ├── evidence_bundle.v1.json # Forensic bundle
│   └── chain_of_custody.json   # Custody events
└── cases/<case-id>/
    └── <sha256>.{ext}          # Hard link to raw file
```

### Data Format

All analysis data is stored as JSON with Pydantic validation:

- **metadata.json**: FileMetadata model
- **analysis.v1.json**: UnifiedAnalysis model (DocumentAnalysis/ImageAnalysis/EmailAnalysis)
- **evidence_bundle.v1.json**: EvidenceBundle model
- **chain_of_custody.json**: List of ChainOfCustodyEvent models

## Testing

### Unit Tests

CLI commands are tested via Click's testing utilities:

```python
from click.testing import CliRunner
from evidence_toolkit.cli import cli

def test_version_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    assert "Evidence Toolkit v3.0.0" in result.output
```

### Integration Tests

Full pipeline testing:

```python
def test_full_pipeline():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create test case directory
        os.makedirs('cases/TEST-001')
        shutil.copy('test_doc.pdf', 'cases/TEST-001/')

        # Run full pipeline
        result = runner.invoke(cli, [
            'process-case', 'cases/TEST-001',
            '--case-id', 'TEST-001'
        ])

        assert result.exit_code == 0
        assert "Case Processing Complete" in result.output
```

### Test Coverage

Current coverage focuses on:
- Command parsing and validation
- Pipeline delegation
- Error handling and exit codes
- Output formatting

## Dependencies

### Internal Dependencies

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import EvidenceType, ChainOfCustodyEvent
from evidence_toolkit.pipeline import (
    ingest_path,
    print_ingestion_summary,
    analyze_evidence,
    SummaryGenerator,
    PackageGenerator,
)
from evidence_toolkit.analyzers.correlation import CorrelationAnalyzer
```

### External Dependencies

- **click**: CLI framework (commands, options, arguments)
- **openai**: Optional - AI analysis (graceful degradation if missing)
- **pathlib.Path**: File path handling
- **datetime**: Timestamps for custody events
- **sys**: Exit codes
- **os**: Environment variables (OPENAI_API_KEY)
- **time**: Pipeline timing

## Related Components

### Upstream Components

The CLI is the entry point - no upstream components. User commands flow into CLI.

### Downstream Components

The CLI delegates to:

1. **Pipeline Modules** (`evidence_toolkit.pipeline`)
   - `ingest.py`: File ingestion logic
   - `analyze.py`: Analysis orchestration
   - `package.py`: Client package generation

2. **Analyzers** (`evidence_toolkit.analyzers`)
   - `correlation.py`: Cross-evidence correlation

3. **Storage** (`evidence_toolkit.core.storage`)
   - `EvidenceStorage`: All file system operations

4. **Models** (`evidence_toolkit.core.models`)
   - Type definitions and validation

### Configuration

- **Environment Variables**: `OPENAI_API_KEY`
- **Default Paths**: `DEFAULT_STORAGE_PATH = Path("data/storage")`
- **Domain Config**: Prompts defined in `domains/legal_config.py`

## Migration Notes

### v2.0 → v3.0 Changes

**CLI Structure:**
- v2.0: CLI contained business logic (1200+ lines)
- v3.0: CLI is thin wrapper (865 lines), delegates to pipeline

**Package Name:**
- v2.0: `document-analyzer` command
- v3.0: `evidence-toolkit` command

**Storage Location:**
- v2.0: Multiple locations (`evidence/`, `document-evidence-analyzer/evidence/`)
- v3.0: Single location (`data/storage`)

**Removed Commands:**
- `retaliation` - Standalone analyzer archived (not in AI pipeline)

**New Commands:**
- `storage` group - Stats, cleanup, prune
- `case` group - List, show, evidence
- `reanalyze` - Batch re-analysis

**Breaking Changes:**
- Command name changed: `document-analyzer` → `evidence-toolkit`
- Storage directory default changed: `evidence/` → `data/storage`
- Import paths changed: `document_analyzer.cli` → `evidence_toolkit.cli`

## Future Considerations

### Planned Enhancements

1. **Parallel Processing**
   - Use ThreadPoolExecutor for concurrent AI analysis
   - Could reduce `process-case` time by 50-75%

2. **Progress Bars**
   - Replace simple counters with rich progress bars
   - Use Click's `progressbar()` or rich library

3. **Export Formats**
   - Add CSV export for correlation results
   - Add HTML reports for client packages

4. **Batch Operations**
   - `batch-ingest` for multiple case directories
   - `batch-package` for generating packages for all cases

5. **Search Commands**
   - `search entities` - Find evidence containing specific entities
   - `search timeline` - Find events in date range
   - `search risk` - Find high-risk evidence

### Known Limitations

1. **No Undo**: Destructive operations (prune, cleanup) cannot be undone
   - Mitigation: Dry-run mode enabled by default
   - Future: Add backup/restore commands

2. **Single Storage Location**: Cannot work with multiple storage directories simultaneously
   - Mitigation: Use --storage-dir option
   - Future: Add storage location management

3. **No Versioning**: Re-analysis overwrites previous results
   - Mitigation: Backups created before overwriting
   - Future: Full version history in derived/ directories

### Technical Debt

1. **Error Messages**: Could be more specific with troubleshooting steps
2. **Help Text**: Could include more examples
3. **Config File**: No support for config files (all CLI options)
4. **Plugins**: No plugin system for custom analyzers

## Examples

### Example 1: Complete Case Processing

```bash
# Scenario: Process a new workplace investigation case
# - Ingest all evidence from case directory
# - Analyze with AI
# - Generate correlation analysis
# - Create client deliverable package

# Set OpenAI API key
export OPENAI_API_KEY=sk-...

# Run full pipeline
uv run evidence-toolkit process-case \
  data/cases/WORKPLACE-2025-001 \
  --case-id WORKPLACE-2025-001 \
  --output-dir ./deliverables/WORKPLACE-2025-001

# Output:
# 🔬 Evidence Toolkit v3.0 - Automated Case Processing Pipeline
# ============================================================
# 📁 Case Directory: data/cases/WORKPLACE-2025-001
# 🆔 Case ID: WORKPLACE-2025-001
# 💾 Storage: data/storage
# ============================================================
#
# 📥 [1/4] Ingesting evidence files...
#    ✅ Ingested 15 files (3 new, 0 duplicates, 12 existing)
#
# 🔍 [2/4] Analyzing evidence with AI...
#    🤖 AI analysis enabled (OpenAI)
#    ✅ Analyzed 3 new items (skipped 12 existing)
#
# 🔗 [3/4] Running cross-evidence correlation...
#    ✅ Found 8 correlated entities
#    ✅ Extracted 23 timeline events
#
# 📦 [4/4] Generating client package...
#    ✅ Package created: ./deliverables/WORKPLACE-2025-001/WORKPLACE-2025-001.zip
#    📊 Size: 12.3 MB
#
# ============================================================
# ✅ Case Processing Complete!
# ============================================================
# ⏱️  Total time: 45.2 seconds
# 📊 Evidence processed: 15 items
```

### Example 2: Incremental Evidence Addition

```bash
# Scenario: Add new evidence to existing case

# Ingest new document
uv run evidence-toolkit ingest \
  new-email.eml \
  --case-id WORKPLACE-2025-001

# Analyze the new evidence only
# (Get SHA256 from ingestion output)
uv run evidence-toolkit analyze \
  a1b2c3d4e5f6... \
  --case-id WORKPLACE-2025-001

# Re-run correlation with new evidence
uv run evidence-toolkit correlate \
  --case-id WORKPLACE-2025-001

# Update client package
uv run evidence-toolkit package \
  --case-id WORKPLACE-2025-001 \
  --include-raw \
  --output-dir ./deliverables/WORKPLACE-2025-001
```

### Example 3: Storage Management

```bash
# Check storage statistics
uv run evidence-toolkit storage stats

# Output:
# 📊 Storage Statistics
# ============================================================
# Evidence: 127 items (1,234.56 MB total)
#   - document: 45 items
#   - email: 67 items
#   - image: 15 items
#
# Storage breakdown:
#   - Raw files: 1,100.00 MB
#   - Derived/analysis: 134.56 MB
#
# Cases: 8
# Labels: 3 categories
#
# ✅ No orphaned files detected

# Preview cleanup
uv run evidence-toolkit storage cleanup

# Actually perform cleanup
uv run evidence-toolkit storage cleanup --force

# Remove old case (dry run first!)
uv run evidence-toolkit storage prune --case-id OLD-CASE-2023
uv run evidence-toolkit storage prune --case-id OLD-CASE-2023 --force
```

### Example 4: Batch Re-Analysis After Prompt Improvement

```bash
# Scenario: Legal prompts improved, need to re-analyze all evidence

# Preview what would be re-analyzed
uv run evidence-toolkit reanalyze \
  --case-id WORKPLACE-2025-001 \
  --dry-run

# Re-analyze only documents (emails unchanged)
uv run evidence-toolkit reanalyze \
  --case-id WORKPLACE-2025-001 \
  --evidence-type document

# Output:
# Re-analyzing case: WORKPLACE-2025-001
# Evidence items: 45
# Filter: document only
# 🤖 OpenAI client initialized
# [1/45] Analyzing a1b2c3d4e5f6...
#   ✅ Complete
# [2/45] Analyzing b2c3d4e5f6a7...
#   ✅ Complete
# ...
# [45/45] Analyzing f6a7b8c9d0e1...
#   ✅ Complete
#
# ✅ Re-analysis complete: 45 successful, 0 failed
```

### Example 5: Case Investigation Workflow

```bash
# List all cases to find the one you need
uv run evidence-toolkit case list

# Show detailed information about a case
uv run evidence-toolkit case show ACME-2024-005

# List evidence in the case
uv run evidence-toolkit case evidence ACME-2024-005 --full-hash

# Analyze correlations and save results
uv run evidence-toolkit correlate \
  --case-id ACME-2024-005 \
  --json-output acme-correlations.json

# Generate final deliverable package
uv run evidence-toolkit package \
  --case-id ACME-2024-005 \
  --include-raw \
  --output-dir ./client-deliverables
```

---

This documentation provides comprehensive coverage of the Evidence Toolkit CLI, from basic usage to advanced workflows. It follows the Evidence Toolkit standards for clarity, completeness, and maintainability.
