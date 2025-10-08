---
description: Create comprehensive documentation for a module, model, analyzer, or feature. Use when adding new components.
argument-hint: [module-name or file-path]
allowed-tools: Read, Write, Grep, Glob, Bash(git log:*), Bash(ls:*)
---

# Create Documentation for $ARGUMENTS

Your task is to create comprehensive documentation for **$ARGUMENTS** following Evidence Toolkit documentation standards.

## Pre-Flight Check

First, check if documentation already exists for $ARGUMENTS:

```bash
# Search for existing docs
find docs/ -name "*.md" -type f -exec grep -l "$ARGUMENTS" {} \; 2>/dev/null
```

If documentation exists:
- **Option 1**: Update existing doc instead (suggest user runs `/update-docs $ARGUMENTS`)
- **Option 2**: If user insists, proceed but note we're replacing existing docs

If no documentation exists, proceed with creation.

## Analysis Phase

I'll analyze:
1. The code structure and purpose of $ARGUMENTS
2. Inputs, outputs, and data flow
3. Integration points with other modules
4. Edge cases and error handling
5. Schema/model definitions (if applicable)
6. Related tests (search tests/ directory)

Then I'll generate documentation with:

# Documentation: $ARGUMENTS

## Overview
[Brief 1-2 paragraph overview explaining what this module/feature does and why it exists]

## Purpose & Scope
[What problem does this solve? What is it responsible for? What is it NOT responsible for?]

## Usage

### Basic Usage
```python
# Minimal example showing core functionality
```

### Advanced Usage
```python
# More complex example demonstrating key features
```

### CLI Usage (if applicable)
```bash
# Command-line examples
uv run evidence-toolkit <command> [options]
```

## Architecture

### Module Structure
[How this fits into the Evidence Toolkit package structure]
```
src/evidence_toolkit/
├── core/              # Where this fits
│   └── [module].py
└── [related modules]
```

### Data Models
[Pydantic models used/defined - link to models.py]

| Model | Purpose | Key Fields |
|-------|---------|------------|
| ModelName | Description | field1, field2 |

## API Reference

### Parameters / Arguments
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| param1 | str | Yes | - | Purpose and constraints |
| param2 | Optional[int] | No | None | Purpose and constraints |

### Return Values
| Type | Description |
|------|-------------|
| ReturnType | What is returned and under what conditions |

### Exceptions
| Exception | When Raised |
|-----------|-------------|
| ValueError | Invalid input conditions |
| RuntimeError | Processing failures |

## Behavior

### Core Functionality
[Detailed explanation of how this works step-by-step]

### Data Flow
[How data moves through this component]
```
Input → [Processing Steps] → Output
```

### State Management
[How this module maintains/modifies state, if applicable]

## AI Integration (if applicable)

### OpenAI Models Used
| Model | Purpose | Cost Impact |
|-------|---------|-------------|
| gpt-4.1-mini | Document analysis | Low |

### Prompts
[Location of prompts in domains/legal_config.py]
[What the prompts instruct the AI to do]

### Response Format
[Pydantic model the AI returns]

## Validation & Compliance

### Input Validation
[How inputs are validated - Pydantic constraints, custom validators]

### Output Validation
[How outputs are validated for forensic integrity]

### Chain of Custody (if applicable)
[How this maintains evidence chain of custody]

## Error Handling

### Common Errors
| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| Error type | What causes it | How to fix/prevent |

### Logging
[What gets logged and at what level]

## Performance Considerations

### Time Complexity
[Expected runtime characteristics]

### Space Complexity
[Memory usage patterns]

### Optimization Notes
[Any performance optimizations implemented or available]

## Storage & Persistence (if applicable)

### File Locations
```
data/storage/
├── raw/sha256=<hash>/
├── derived/sha256=<hash>/
└── cases/<case-id>/
```

### Data Format
[JSON schema, file formats used]

## Testing

### Unit Tests
```python
# Example test showing how to test this module
```

### Integration Tests
[How this is tested as part of the pipeline]

### Test Coverage
[Current coverage level, what's tested]

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.models` - Model definitions
- `evidence_toolkit.core.storage` - Storage operations

### External Dependencies
- `openai` - AI analysis
- `pydantic` - Validation

## Related Components

### Upstream Components
[What feeds data into this]

### Downstream Components
[What consumes output from this]

### Configuration
[Related files: domains/legal_config.py, CLAUDE.md]

## Migration Notes (if applicable)
[v2.0 → v3.0 changes, breaking changes, deprecations]

## Future Considerations
[Known limitations, planned enhancements, technical debt]

## Examples

### Example 1: [Common Use Case]
```python
# Complete working example
```

### Example 2: [Edge Case]
```python
# How to handle special situations
```

---

## Post-Creation Actions

After creating documentation, report:

```
✅ Documentation Created: $ARGUMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 New file: docs/[path]/[module].md
📊 Sections: [count] sections, [word-count] words
🔗 References: [list of linked modules/models]

💡 Suggested Next Steps:
  • Review the generated documentation for accuracy
  • Add any project-specific examples
  • Consider documenting related modules: [list]
  • Update docs/README.md to include link to new doc
```

---

## Notes

This documentation follows the Evidence Toolkit standards for clarity, completeness, and maintainability. It provides both high-level understanding and implementation details for developers working with $ARGUMENTS.

**Workflow Integration**:
- Called directly: `/create-docs src/evidence_toolkit/core/storage.py`
- Called by /update-docs: Generates docs for each module in batch
- After new feature: Add new analyzer → `/create-docs analyzers/new_analyzer.py`

**Related Commands**:
- `/update-docs` - Batch update of existing documentation (calls /create-docs internally)
- `/prime` - May suggest running documentation updates after discovery
