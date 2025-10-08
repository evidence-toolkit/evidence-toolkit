---
allowed-tools: Read, Write, Grep, Glob, Bash(git diff:*), Bash(git log:*), SlashCommand:/create-docs:*
argument-hint: [module-path or 'recent' or 'all']
description: Generate/update documentation for modules. Use after refactoring or when docs are outdated.
---

## Context

**Documentation Structure:**
```
docs/
├── api/                    # API reference docs
│   ├── models.md
│   ├── models-quick-reference.md
│   └── README.md
├── module-docs/            # Module documentation
│   ├── CLI.md
│   ├── LEGAL_DOMAIN_CONFIG.md
│   └── README.md
├── pipeline/               # Pipeline stage docs
│   ├── ingest.md
│   ├── analyze.md
│   ├── summary.md
│   ├── package.md
│   └── README.md
├── storage-module.md       # Storage system docs
└── ANALYZERS.md            # Analyzer documentation
```

**Recent Changes (for 'recent' mode):**
!`git diff --name-only HEAD~5..HEAD -- 'src/evidence_toolkit/**/*.py'`

**Project Source:**
```
src/evidence_toolkit/
├── core/               # Models, storage, utilities
├── analyzers/          # AI analysis modules
├── pipeline/           # Processing pipeline
├── domains/            # Domain configurations
└── cli.py              # CLI entry point
```

---

## Your Task

Generate or update documentation based on the argument provided.

### Modes

**1. Specific Module** (`$ARGUMENTS` = file path or module name)
```bash
/update-docs src/evidence_toolkit/core/storage.py
/update-docs analyzers
/update-docs cli
```
- Generate docs for that specific module/file
- Save to appropriate docs/ subdirectory

**2. Recent Changes** (`$ARGUMENTS` contains 'recent')
```bash
/update-docs recent
```
- Document modules that changed in last 5 commits
- Useful after a refactoring session

**3. Batch Update** (`$ARGUMENTS` contains 'all')
```bash
/update-docs all
```
- Update ALL module documentation
- WARNING: This is expensive (uses lots of tokens)
- Ask for confirmation before proceeding

### Documentation Template

Use the existing `/create-docs` template structure:

```markdown
# Documentation: {Module Name}

## Overview
[Brief 1-2 paragraph overview]

## Purpose & Scope
[What problem does this solve? Responsibilities?]

## Usage
### Basic Usage
[Code examples]

### CLI Usage (if applicable)
[Command examples]

## Architecture
### Module Structure
[How this fits in evidence-toolkit]

### Data Models
[Pydantic models used]

## API Reference
### Parameters
[Table of parameters]

### Return Values
[What is returned]

### Exceptions
[What errors can occur]

## Behavior
### Core Functionality
[Step-by-step explanation]

### Data Flow
[How data moves through]

## AI Integration (if applicable)
[OpenAI models, prompts, response formats]

## Validation & Compliance
[How forensic integrity is maintained]

## Error Handling
[Common errors and recovery]

## Performance Considerations
[Time/space complexity, optimizations]

## Storage & Persistence (if applicable)
[File locations, data formats]

## Testing
[How to test this module]

## Dependencies
[Internal and external dependencies]

## Related Components
[Upstream/downstream components]

## Examples
[Real-world usage examples]
```

### Workflow

1. **Identify Target(s)**
   - Parse $ARGUMENTS to determine what to document
   - If 'recent', use git diff to find changed files
   - If 'all', use Glob to find all source files (⚠️ expensive - ask for confirmation)
   - If specific module path, validate it exists

2. **Pre-Processing Check**
   - Count total modules to document
   - Estimate token cost (warn if >10 modules)
   - Ask for confirmation if batch operation

3. **For Each Target Module:**

   **Option A: Use /create-docs (Recommended - DRY principle)**
   ```
   For each module in target list:
     Invoke: /create-docs {module_path}
   ```

   This delegates to the specialized /create-docs command which:
   - Checks if docs already exist
   - Reads source code and tests
   - Generates comprehensive documentation
   - Saves to appropriate docs/ subdirectory

   **Option B: Direct documentation (fallback)**

   If /create-docs is not available or fails:
   - Read the source code thoroughly
   - Understand its purpose, inputs, outputs, and dependencies
   - Use Grep to find related tests
   - Check existing docs to see if updating or creating new
   - Generate documentation following the template structure
   - Include code references with line numbers (e.g., `storage.py:142`)

4. **Save Documentation:**
   - **Core modules** → `docs/module-docs/{module}.md`
   - **Analyzers** → Update `docs/ANALYZERS.md` or create section
   - **Pipeline** → `docs/pipeline/{stage}.md`
   - **Models** → Update `docs/api/models.md`
   - **CLI** → Update `docs/module-docs/CLI.md`

5. **Report Results:**
   - List what was generated/updated
   - Show file paths of new documentation
   - Token cost summary (if batch operation)
   - Suggest related docs that might need updates

### Special Considerations

**Forensic Focus:**
This is a legal evidence toolkit. Emphasize:
- Chain of custody preservation
- Deterministic analysis (temperature=0)
- Validation and compliance
- Data integrity

**Pydantic Models:**
All models are in `src/evidence_toolkit/core/models.py`. Document:
- Field descriptions
- Validation constraints
- Example JSON output

**AI Integration:**
Document OpenAI usage:
- Which model (e.g., gpt-4o-mini, gpt-4o)
- What prompts (from domains/legal_config.py)
- Response format (Pydantic model)
- Cost implications

### Output Format

**Single Module:**
```
📝 Documentation Update: {target}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 Strategy: Using /create-docs for detailed documentation generation

🔍 Invoking: /create-docs src/evidence_toolkit/core/storage.py

[/create-docs output appears here]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Documentation complete!
```

**Batch Mode (recent/all):**
```
📝 Batch Documentation Update: {mode}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Discovered {N} modules to document:
   1. src/evidence_toolkit/core/storage.py
   2. src/evidence_toolkit/analyzers/correlation.py
   3. [...]

⚠️  This will use ~{estimated} tokens. Continue? [y/N]

[If confirmed:]

📖 Processing module 1/{N}: storage.py
   Invoking: /create-docs src/evidence_toolkit/core/storage.py
   ✅ Done

📖 Processing module 2/{N}: correlation.py
   Invoking: /create-docs src/evidence_toolkit/analyzers/correlation.py
   ✅ Done

[...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Batch documentation complete!

📊 Summary:
   • Modules documented: {N}
   • New docs created: {X}
   • Existing docs updated: {Y}
   • Failed: {Z} (if any)

📂 Generated:
   - docs/module-docs/storage.md
   - docs/analyzers/correlation.md
   [...]

💡 Suggested updates:
   - docs/pipeline/README.md (add links to new docs)
   - docs/api/models.md (cross-reference new models)
```

---

## Notes

**Expected Outcome:**
High-quality, comprehensive documentation that helps developers understand and use the Evidence Toolkit effectively.

**Workflow Integration**:
- After refactoring: `/update-docs recent` to refresh changed module docs
- After major changes: `/prime` may suggest running `/update-docs recent`
- Manual batch update: `/update-docs all` (expensive, requires confirmation)
- Specific module: `/update-docs src/evidence_toolkit/core/storage.py`

**Performance**:
- Single module: Delegates to /create-docs (~5-10k tokens)
- Recent (5 commits): Typically 2-5 modules (~20-50k tokens)
- All modules: 10+ modules (~100k+ tokens) - requires confirmation

**Related Commands**:
- `/create-docs` - Called internally for each module (DRY principle)
- `/prime` - May auto-suggest running /update-docs after discovery
- `/status` - Quick check without documentation generation
