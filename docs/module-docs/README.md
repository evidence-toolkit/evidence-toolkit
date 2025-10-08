# Evidence Toolkit v3.0 - Module Documentation

This directory contains comprehensive documentation for individual Evidence Toolkit modules.

## Available Documentation

### Core Components

#### [CLI.md](CLI.md) - Command Line Interface
**File**: `src/evidence_toolkit/cli.py`
**Lines**: 1,150
**Size**: 33 KB

Complete documentation for the Evidence Toolkit CLI including:
- All commands (process-case, ingest, analyze, correlate, package)
- Storage management (stats, cleanup, prune)
- Case management (list, show, evidence)
- Re-analysis operations
- Usage examples and workflows
- Error handling and troubleshooting
- API reference for all commands

**Target Audience**: Users, DevOps, System Administrators

#### [LEGAL_DOMAIN_CONFIG.md](LEGAL_DOMAIN_CONFIG.md) - Legal Domain Configuration
**File**: `src/evidence_toolkit/domains/legal_config.py`
**Lines**: 949
**Size**: 31 KB

Complete documentation for legal domain configuration including:
- All AI prompts (document, email, image, correlation, executive summary)
- Prompt engineering best practices
- Risk flag definitions and usage
- Forensic quality requirements
- Prompt customization examples
- Multi-domain extension patterns

**Target Audience**: Developers, AI Engineers, Legal Tech Specialists

## Documentation Structure

Each module documentation follows the Evidence Toolkit standard template:

1. **Overview** - What the module does and why it exists
2. **Purpose & Scope** - Clear boundaries of responsibility
3. **Usage** - Basic and advanced usage examples
4. **Architecture** - How it fits into the system
5. **API Reference** - Complete parameter and return value documentation
6. **Behavior** - Detailed explanation of how it works
7. **AI Integration** - OpenAI usage (if applicable)
8. **Validation & Compliance** - Forensic quality assurance
9. **Error Handling** - Common errors and recovery strategies
10. **Performance Considerations** - Time/space complexity
11. **Storage & Persistence** - File locations and formats (if applicable)
12. **Testing** - How to test the module
13. **Dependencies** - Internal and external dependencies
14. **Related Components** - Integration points
15. **Migration Notes** - v2.0 → v3.0 changes
16. **Future Considerations** - Planned enhancements and known limitations
17. **Examples** - Real-world usage scenarios

## Documentation Coverage

This is part of a parallel documentation effort. Current coverage:

### Completed
- ✅ CLI (`cli.py`) - Full user and developer documentation
- ✅ Legal Domain Configuration (`domains/legal_config.py`) - Prompt engineering and customization

### In Progress (Parallel Efforts)
- Core Models (`core/models.py`)
- Storage Layer (`core/storage.py`)
- Analyzers (`analyzers/document.py`, `analyzers/email.py`, `analyzers/image.py`, `analyzers/correlation.py`)
- Pipeline Components (`pipeline/ingest.py`, `pipeline/analyze.py`, `pipeline/package.py`)

## Quick Navigation

### By User Type

**End Users** (Using the CLI):
- Start with: [CLI.md](CLI.md)
- Focus on: Usage section, Examples section

**Developers** (Extending the toolkit):
- Start with: [CLI.md](CLI.md) Architecture section
- Then: [LEGAL_DOMAIN_CONFIG.md](LEGAL_DOMAIN_CONFIG.md) for prompt customization
- Next: Check other module docs (when available)

**AI Engineers** (Improving analysis quality):
- Start with: [LEGAL_DOMAIN_CONFIG.md](LEGAL_DOMAIN_CONFIG.md)
- Focus on: Prompt Engineering Best Practices, Configuration Reference

**Legal Tech Specialists** (Understanding forensic capabilities):
- Start with: [LEGAL_DOMAIN_CONFIG.md](LEGAL_DOMAIN_CONFIG.md)
- Focus on: Configuration Elements, Validation & Compliance

## Documentation Standards

All module documentation in this directory follows these standards:

1. **Forensic Focus**: Documentation emphasizes chain of custody, validation, and compliance
2. **Example-Driven**: Real-world usage examples for all features
3. **Migration-Aware**: Clear v2.0 → v3.0 migration guidance
4. **Future-Oriented**: Planned enhancements and extensibility patterns
5. **Testing-Inclusive**: How to test each component
6. **Error-Focused**: Common errors and recovery strategies

## Related Documentation

- [V3_ARCHITECTURE.md](../V3_ARCHITECTURE.md) - Overall system architecture
- [CLAUDE.md](../../CLAUDE.md) - Developer guidance for AI assistants
- [README.md](../../README.md) - Project overview and quick start
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines

## Documentation Maintenance

### When to Update

Update module documentation when:
1. **API Changes**: Function signatures or return values change
2. **New Features**: New commands, options, or capabilities added
3. **Behavior Changes**: How the module works changes
4. **Prompt Updates**: AI prompts are modified (for domain configs)
5. **Migration Paths**: New version released (v3.1, v4.0, etc.)

### How to Update

1. Edit the relevant markdown file in `docs/module-docs/`
2. Follow the existing template structure
3. Update examples if API changed
4. Update migration notes if breaking changes
5. Add to Future Considerations if relevant
6. Run documentation tests (if available): `uv run pytest tests/test_docs.py`

### Documentation Review Checklist

- [ ] Overview clearly explains purpose
- [ ] Usage section has working examples
- [ ] API Reference is complete and accurate
- [ ] Error Handling section covers common issues
- [ ] Examples are up-to-date and tested
- [ ] Migration notes reflect actual changes
- [ ] Links to related components are correct
- [ ] Code blocks use correct syntax highlighting

## Feedback and Contributions

Found an issue with the documentation?
1. Check if issue already exists: `grep -r "TODO" docs/module-docs/`
2. Open an issue with tag `documentation`
3. Submit a PR with improvements

## Statistics

- **Total Documentation**: 2,099 lines
- **Total Size**: 64 KB
- **Modules Documented**: 2
- **Coverage**: CLI + Domain Configuration (25% of core modules)
- **Last Updated**: 2025-10-05

---

This documentation is part of the Evidence Toolkit v3.0 - Clean Architecture initiative.
