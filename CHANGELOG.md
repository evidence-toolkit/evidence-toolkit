# Changelog

All notable changes to Evidence Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.3.0] - 2025-10-09

### Added
- **v3.3 Phase B**: Image OCR aggregation for visual evidence analysis
  - Extracts and displays detected text from 75% of images
  - Groups by evidence value (high/medium/low)
  - Highlights images with people present and visible timestamps
- **v3.3 Phase B**: Semantic timeline events from AI-extracted dates
  - Adds narrative events to timeline ("meeting with HR", "grievance filed")
  - Parses multiple date formats (ISO, UK, US)
  - Enriches timeline beyond just document timestamps
- **v3.3 Phase B**: Relationship network extraction
  - Parses entity relationships for escalation chains
  - Maps email communication patterns (sender → recipient)
  - Identifies key players by connection count
- **v3.3 Phase B+**: Forensic-first report layout
  - Executive summary now leads with insights (35-45% of report)
  - Supporting documentation moved to appendix (55-65%)
  - Added quoted statements section with sentiment analysis
  - Added communication pattern classification section
  - Added relationship network section
  - Added image OCR analysis section

### Changed
- Achieved **98% data utilization** (up from 65% in v3.1)
  - All AI-generated insights now displayed to users
  - Zero additional API costs (uses existing analysis data)
- Refactored report structure to prioritize forensic insights over raw data
- Enhanced executive summary prompts for workplace and generic cases
- Updated AI prompts to use v3.3 data types (relationships, quotes, patterns, OCR)

### Fixed
- **Code Deduplication Phase 1**: OpenAI API response handling (-39 lines)
- **Code Deduplication Phase 2**: Path construction utilities (-924 lines)
- **Code Deduplication Phase 3**: Redundant correlation call (-4 lines)
- **Code Deduplication Phase 4**: Metadata loading and directory creation (-2 lines)
- **Total**: Eliminated ~969 lines of duplicated code across 4 phases

## [3.2.0] - 2025-10-06

### Added
- **AI Entity Resolution**: Context-aware name matching with `--ai-resolve` flag
  - Handles informal vs formal names ("Paul" vs "Paul Boucherat")
  - Resolves nicknames and abbreviations
  - Uses organization, role, email domain for disambiguation
  - Conservative bias for forensic accuracy
- **Case Type Support**: Domain-specific prompts via `--case-type` flag
  - `generic` - General legal matters (default)
  - `workplace`/`employment` - Employment law focus (ACAS compliance, tribunal risk)
  - `contract` - Commercial dispute focus
- **Chunked Summaries**: Map-reduce pattern for cases with 50+ evidence items
  - Automatically activates for large cases
  - Breaks evidence into 30-item chunks
  - Generates chunk summaries, then combines for final executive summary
  - Prevents OpenAI context overflow
- **Video/Audio Ingestion**: Basic support for multimedia files
  - Files can be ingested and tracked in chain of custody
  - Analysis implementation planned for future version

### Fixed
- Context length errors in executive summary generation for cases >1000 items
- Video/audio files (.mov, .mp4, .mp3, .wav) no longer classified as "other" type
- Smart threshold: Cases ≤50 items use direct approach, >50 use chunking

## [3.1.0] - 2025-10-05

### Added
- **Legal Pattern Detection**: AI-powered analysis of cross-evidence patterns
  - Contradictions (factual, temporal, attribution)
  - Corroboration (weak, moderate, strong)
  - Evidence gaps (missing witnesses, documentation, communications)
- **Power Dynamics Analysis**: Email thread hierarchy and influence scoring
  - Deference score (0.0=dominant, 0.5=neutral, 1.0=deferential)
  - Dominant topics per participant
  - Authority levels (executive/management/employee/external)
- **Enhanced Entity Extraction**: Richer relationship data
  - Relationship field (organizational, escalation, email communication)
  - Quoted text extraction with speaker attribution
  - Associated event field for date entities
- **Temporal Analysis**: Timeline sequences and gap detection
  - Escalation events tracked across evidence
  - Timeline reconstruction from metadata and content

### Changed
- Data utilization increased to **65%** (from ~40% in v3.0)
- AI prompts enhanced with legal domain expertise
- Correlation analysis now detects sophisticated patterns

## [3.0.0] - 2025-10-05

### Added
- **Complete v3.0 Architecture Refactor**
  - Single unified package structure (`src/evidence_toolkit/`)
  - Consolidated 48 Pydantic models into single file (`core/models.py`)
  - Content-addressed storage with SHA256 deduplication
  - Visible `data/` directory structure (cases, storage, packages)
  - Clean separation: core, analyzers, pipeline, domains
- **Simplified CLI**: Delegated architecture
  - Reduced CLI from 1,229 lines to 438 lines (64% reduction)
  - Pipeline components handle orchestration
  - Cleaner command structure
- **Unified Models**: All Pydantic, all validated
  - CorrelationAnalysis converted from dataclass to Pydantic
  - 100% runtime validation across all outputs
  - Single source of truth for all models
- **Content-Addressed Storage**: Efficient evidence management
  - SHA256-based file identification
  - Automatic deduplication across cases
  - Hard links for multi-case evidence reuse
  - Complete chain of custody tracking

### Changed
- **Package rename**: `document-analyzer` → `evidence-toolkit`
- **Import paths**: `document_analyzer.*` → `evidence_toolkit.*`
- **CLI command**: `document-analyzer` → `evidence-toolkit`
- **Directory structure**:
  - `evidence/` → `data/storage/`
  - `cases/` → `data/cases/`
  - `client_packages/` → `data/packages/`

### Removed
- Legacy v2.0 nested package structure
- Duplicate model definitions across 5 files (1,071 lines consolidated to 715)
- Confusing "dual directory" warnings

### Migration
- See [V3_COMPLETE.md](V3_COMPLETE.md) for complete migration guide
- Breaking changes documented in [V3_ARCHITECTURE.md](V3_ARCHITECTURE.md)

## [2.0.x] - 2025-10-04 and earlier

### Features
- Document analysis (PDF, TXT)
- Email analysis (EML)
- Image analysis (JPG, PNG)
- Basic cross-evidence correlation
- Client package generation
- Chain of custody tracking

### Architecture
- Multi-package structure (`document_analyzer/`, `models/`)
- Mixed validation (Pydantic + dataclasses)
- Hidden data directories (gitignored)

---

## Version Support Policy

| Version | Status | Support End |
|---------|--------|-------------|
| 3.3.x   | ✅ Active | Current |
| 3.2.x   | ✅ Active | 2025-12-31 |
| 3.1.x   | ⚠️ Security fixes only | 2025-10-31 |
| 3.0.x   | ⚠️ Security fixes only | 2025-10-31 |
| < 3.0   | ❌ End of life | 2025-10-05 |

---

## Upgrade Paths

### From v3.2.x to v3.3.0
No breaking changes - drop-in replacement. Re-run `package` command to get new report layout.

### From v3.1.x to v3.3.0
No breaking changes - drop-in replacement. Use `--ai-resolve` and `--case-type` flags for new features.

### From v3.0.x to v3.3.0
No breaking changes - drop-in replacement. All new features are additive.

### From v2.x to v3.3.0
**Breaking changes** - see [V3_COMPLETE.md](V3_COMPLETE.md) for migration guide:
- Update imports: `document_analyzer.*` → `evidence_toolkit.*`
- Update CLI commands: `document-analyzer` → `evidence-toolkit`
- Update data directories: `evidence/` → `data/storage/`

---

## Links

- [GitHub Repository](https://github.com/evidence-toolkit/evidence-toolkit)
- [Documentation](https://github.com/evidence-toolkit/evidence-toolkit#readme)
- [Issue Tracker](https://github.com/evidence-toolkit/evidence-toolkit/issues)
