# Evidence Toolkit Documentation

**Version**: 4.0.0 | **Last Updated**: 2025-10-10

Welcome to the Evidence Toolkit documentation! This is your central navigation hub for all project documentation.

---

## 🚀 Quick Start

**New to Evidence Toolkit?** Start here:

1. **[Project README](../README.md)** - Overview, installation, quick start
2. **[Architecture Overview](#architecture)** - System design and principles
3. **[Pipeline Guide](pipeline/PIPELINE_OVERVIEW.md)** - How evidence processing works
4. **[CLI Reference](module-docs/CLI.md)** - Complete command-line guide

**Quick Command**:
```bash
uv run evidence-toolkit process-case data/cases/MY-CASE --case-id MY-CASE
```

---

## 📚 Documentation Sections

### Core Documentation

#### Architecture & Design
| Document | Description | Status |
|----------|-------------|--------|
| [V4_ARCHITECTURE.md](V4_ARCHITECTURE.md) | Complete system architecture (v3.0-v4.0) | ✅ Current |
| [V3_3_COMPLETE.md](V3_3_COMPLETE.md) | v3.3 release notes (98% data utilization) | 📋 Reference |
| [V3_DEDUPLICATION_REPORT.md](V3_DEDUPLICATION_REPORT.md) | Code quality analysis | 📋 Reference |

#### Version History
| Document | Description | Status |
|----------|-------------|--------|
| [CHANGELOG.md](../CHANGELOG.md) | Complete version history (v3.0-v4.0) | ✅ Current |
| [V4_RELEASE_NOTES.md](V4_RELEASE_NOTES.md) | v4.0 release documentation | ✅ Current |
| [V3.1_DATA_FLOW.md](V3.1_DATA_FLOW.md) | v3.1 AI enhancements data flow | 📋 Reference |

### Module Documentation

Complete documentation for each Evidence Toolkit module:

| Module | Document | Lines | Updated |
|--------|----------|-------|---------|
| **CLI** | [module-docs/CLI.md](module-docs/CLI.md) | 1,150 | Oct 6 |
| **Generators** | [module-docs/GENERATORS.md](module-docs/GENERATORS.md) | 502 | Oct 10 |
| **Legal Config** | [module-docs/LEGAL_DOMAIN_CONFIG.md](module-docs/LEGAL_DOMAIN_CONFIG.md) | 1,014 | Oct 7 |
| **Correlation** | [module-docs/CORRELATION_ANALYZER.md](module-docs/CORRELATION_ANALYZER.md) | 1,438 | Oct 10 |
| **Index** | [module-docs/README.md](module-docs/README.md) | - | Oct 5 |

### Pipeline Documentation

Deep dives into each pipeline stage:

| Stage | Document | Description |
|-------|----------|-------------|
| **Overview** | [pipeline/PIPELINE_OVERVIEW.md](pipeline/PIPELINE_OVERVIEW.md) | Complete 4-stage pipeline architecture |
| **Stage 1** | [pipeline/ingest.md](pipeline/ingest.md) | Evidence ingestion & content-addressing |
| **Stage 2** | [pipeline/analyze.md](pipeline/analyze.md) | AI-powered evidence analysis |
| **Stage 3** | [pipeline/summary.md](pipeline/summary.md) | Cross-evidence correlation & summarization |
| **Stage 4** | [pipeline/package.md](pipeline/package.md) | Client deliverable package generation |

### API Documentation

| Document | Description |
|----------|-------------|
| [api/README.md](api/README.md) | API overview |
| [api/models.md](api/models.md) | Complete Pydantic models reference (1,734 lines) |
| [api/models-quick-reference.md](api/models-quick-reference.md) | Quick model lookup |

### Feature Guides

| Guide | Description | Status |
|-------|-------------|--------|
| [CASE_TYPES.md](CASE_TYPES.md) | Domain-specific prompts (workplace, contract, generic) | ✅ Current |
| [ANALYZERS.md](ANALYZERS.md) | Analyzer architecture | 🟡 Has TODOs |
| [GENERATORS_IMPLEMENTATION_PLAN.md](GENERATORS_IMPLEMENTATION_PLAN.md) | v3.4 generators design | 📋 Reference |
| [WASTED_DATA_INVENTORY.md](WASTED_DATA_INVENTORY.md) | Data utilization analysis | 📋 Reference |

### Development

| Topic | Document | Description |
|-------|----------|-------------|
| **API** | [API.md](API.md) | API interface documentation |
| **Quick Ref** | [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) | Quick API lookup |
| **Testing** | [AB_TESTING_FRAMEWORK.md](AB_TESTING_FRAMEWORK.md) | A/B testing for prompts |
| **Prompts** | [PIPELINE_PROMPT_VALIDATION.md](PIPELINE_PROMPT_VALIDATION.md) | Prompt validation guide |
| **Storage** | [storage-module.md](storage-module.md) | Content-addressed storage details |
| **Commands** | [SLASH_COMMAND_TEMPLATE.md](SLASH_COMMAND_TEMPLATE.md) | Creating slash commands |

---

## 📦 v4.0 Key Features

Evidence Toolkit v4.0 delivers **8 professional forensic reports** automatically:

1. **Executive Summary** - AI-generated case overview with key findings
2. **Forensic Legal Opinion** - Statutory risk analysis and legal implications
3. **Financial Risk Assessment** - Tribunal probability and settlement ranges
4. **Legal Patterns Analysis** - Contradictions, corroboration, evidence gaps
5. **Timeline Reconstruction** - Chronological event mapping with gap analysis
6. **Quoted Statements** - Person-by-person statement breakdown with sentiment
7. **Relationship Network** - Entity connection mapping and key player identification
8. **Power Dynamics** - Email authority hierarchy and deference scoring

**Data Utilization**: 90% (up from 65% in v3.2)
**Client Value**: £4,500 deliverable (up from £500)
**AI Cost**: $0 additional (reuses v3.3 analysis)

---

## 🗺️ Documentation by Use Case

### I want to...

**...understand the system architecture**
→ [V4_ARCHITECTURE.md](V4_ARCHITECTURE.md) - Complete design and principles

**...process my first case**
→ [Project README](../README.md) Quick Start → [Pipeline Overview](pipeline/PIPELINE_OVERVIEW.md)

**...use the CLI**
→ [CLI Reference](module-docs/CLI.md) - All commands with examples

**...customize AI prompts**
→ [Legal Domain Config](module-docs/LEGAL_DOMAIN_CONFIG.md) - Prompt engineering guide

**...understand report generators**
→ [Generators Module](module-docs/GENERATORS.md) - Generator architecture

**...work with the API**
→ [API Documentation](API.md) → [Models Reference](api/models.md)

**...contribute code**
→ [Contributing Guide](../CONTRIBUTING.md) → [Technical Debt](technical-debt/README.md)

**...understand data flow**
→ [V3.1 Data Flow](V3.1_DATA_FLOW.md) → [Pipeline Overview](pipeline/PIPELINE_OVERVIEW.md)

---

## 🔮 Future Planning (v4.1+)

Future architecture and enhancement planning:

| Document | Description | Status |
|----------|-------------|--------|
| [v4.0/README.md](v4.0/README.md) | Future v4.x roadmap | 🔵 Planning |
| [v4.0/ARCHITECTURE.md](v4.0/ARCHITECTURE.md) | Hexagonal architecture design | 🔵 Planning |
| [v4.0/AGENTIC_DESIGN.md](v4.0/AGENTIC_DESIGN.md) | Agent-based workflow | 🔵 Planning |
| [v4.0/MIGRATION_GUIDE.md](v4.0/MIGRATION_GUIDE.md) | Migration planning | 🔵 Planning |

---

## 🗄️ Historical Documentation

Archived documentation for reference:

- **[archive/v3.0/](archive/v3.0/)** - v3.0 refactor completion docs (Oct 5, 2025)
- **[archive/v3.3/](archive/v3.3/)** - v3.3 planning and session notes (Oct 8, 2025)
- **[archive/v3.4/](archive/v3.4/)** - v3.4 Phase 2 planning (Oct 9, 2025)
- **[archive/sessions/](archive/sessions/)** - Development session continuation prompts

---

## 📊 Technical Debt

Code quality and improvement tracking:

| Document | Description |
|----------|-------------|
| [technical-debt/README.md](technical-debt/README.md) | Overview |
| [technical-debt/GETTING_STARTED.md](technical-debt/GETTING_STARTED.md) | How to address tech debt |
| [technical-debt/v3.3_data_utilization_audit.md](technical-debt/v3.3_data_utilization_audit.md) | v3.3 data audit |
| [technical-debt/v3.4_priority_3_improvements.md](technical-debt/v3.4_priority_3_improvements.md) | v3.4 improvements |
| [technical-debt/duplication-summary.md](technical-debt/duplication-summary.md) | Code duplication analysis |

---

## 📖 External Reference Documentation

Copied documentation from external platforms (for offline reference):

### OpenAI API Reference
- [ai-docs/openai/openai-quickstart.md](ai-docs/openai/openai-quickstart.md)
- [ai-docs/openai/text.md](ai-docs/openai/text.md)
- [ai-docs/openai/structured-out.md](ai-docs/openai/structured-out.md)
- [ai-docs/openai/images.md](ai-docs/openai/images.md)
- [ai-docs/openai/function-tools.md](ai-docs/openai/function-tools.md)
- [ai-docs/openai/prompting.md](ai-docs/openai/prompting.md)
- [ai-docs/openai/models.md](ai-docs/openai/models.md)

### Claude Code Best Practices
- [ai-docs/claude/build_effective_agents.md](ai-docs/claude/build_effective_agents.md)
- [ai-docs/claude/claude_code_best_practices.md](ai-docs/claude/claude_code_best_practices.md)
- [ai-docs/claude/claude_code_tech.md](ai-docs/claude/claude_code_tech.md)
- [ai-docs/claude/claude-code-tutorials.md](ai-docs/claude/claude-code-tutorials.md)

---

## 📈 Documentation Statistics

- **Total Documentation**: ~30,000 lines (after archiving)
- **Active Core Docs**: 52 files
- **Archived Docs**: 12 files
- **Module Documentation**: 12 files (~12,000 lines)
- **API Reference**: 6 files (~3,000 lines)
- **Coverage**: Core modules, pipeline, API, generators

---

## 🔄 Documentation Updates

### When to Update Documentation

Update relevant docs when:
1. **API Changes**: Function signatures or return values change
2. **New Features**: New commands, generators, or capabilities added
3. **Behavior Changes**: How modules work changes
4. **Prompt Updates**: AI prompts are modified
5. **Migration Paths**: New version released

### How to Update

1. Edit the relevant markdown file in `docs/`
2. Follow existing template structure
3. Update examples if API changed
4. Update version history in CHANGELOG.md
5. Update this README if new docs added

---

## 💬 Getting Help

- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Ask questions on GitHub Discussions
- **Documentation Feedback**: Open issues tagged `documentation`

---

**Status Legend**:
- ✅ **Current** - Up-to-date, actively maintained
- 📋 **Reference** - Historical reference, still accurate
- 🔵 **Future** - Planning documents for future work
- 🟡 **Review Needed** - May have incomplete sections or TODOs

---

*Last updated: 2025-10-10 | Evidence Toolkit v4.0*
