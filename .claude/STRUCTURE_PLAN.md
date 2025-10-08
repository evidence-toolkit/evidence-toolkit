# .claude/ Directory Structure Plan

**Created**: 2025-10-07
**Purpose**: Comprehensive organization for Claude Code project configuration

---

## 📁 Proposed Structure

```
.claude/
├── README.md                      # Overview of all Claude Code integration
├── STRUCTURE_PLAN.md             # This file - design document
│
├── commands/                      # Slash commands (organized by category)
│   ├── README.md                 # Command catalog
│   ├── _templates/               # Command templates for creating new ones
│   │   ├── basic-command.md
│   │   ├── bash-command.md
│   │   └── agent-delegating-command.md
│   │
│   ├── discovery/                # Codebase understanding
│   │   ├── prime.md              # [✓] Main onboarding command
│   │   ├── status.md             # [✓] Quick health check
│   │   └── explore.md            # [NEW] Interactive exploration
│   │
│   ├── development/              # Daily dev workflow
│   │   ├── commit.md             # [✓] Smart git commits
│   │   ├── test-fix.md           # [✓] Automated testing
│   │   ├── lint.md               # [NEW] Run linters/formatters
│   │   └── review.md             # [NEW] Self-review code
│   │
│   ├── documentation/            # Docs generation
│   │   ├── create-docs.md        # [✓] Create new documentation
│   │   ├── update-docs.md        # [✓] Batch doc updates
│   │   └── docstring.md          # [NEW] Add/update docstrings
│   │
│   ├── analysis/                 # Debugging and investigation
│   │   ├── rca.md                # [✓] Root cause analysis
│   │   ├── trace.md              # [NEW] Execution tracing
│   │   └── profile.md            # [NEW] Performance profiling
│   │
│   ├── release/                  # Release management
│   │   ├── package-release.md    # [✓] Version bump + changelog
│   │   ├── pr.md                 # [NEW] Create pull request
│   │   └── changelog.md          # [NEW] Generate changelog only
│   │
│   └── evidence/                 # Evidence Toolkit specific
│       ├── ingest-case.md        # [NEW] Ingest new case
│       ├── analyze-evidence.md   # [NEW] Analyze specific evidence
│       ├── correlate.md          # [NEW] Run correlation analysis
│       └── package-case.md       # [NEW] Package for client delivery
│
├── agents/                       # Custom AI agents
│   ├── README.md                 # Agent catalog and usage guide
│   ├── rca-debugger.md          # [✓] Root cause analysis specialist
│   ├── evidence-forensics-expert.md  # [✓] Chain of custody expert
│   ├── test-engineer.md         # [NEW] Test generation specialist
│   ├── doc-writer.md            # [NEW] Documentation specialist
│   └── security-auditor.md      # [NEW] Security review specialist
│
├── prompts/                      # Reusable prompt snippets
│   ├── README.md                 # Prompt library index
│   ├── code-review.md           # Code review checklist
│   ├── pydantic-validation.md   # Pydantic best practices
│   ├── forensic-integrity.md    # Legal evidence standards
│   └── ai-prompt-engineering.md # OpenAI prompt guidelines
│
├── templates/                    # File templates
│   ├── README.md                 # Template catalog
│   ├── analyzer.py.template     # New analyzer boilerplate
│   ├── test.py.template         # Test file template
│   ├── model.py.template        # Pydantic model template
│   └── module-doc.md.template   # Documentation template
│
├── workflows/                    # Multi-step workflows
│   ├── README.md                 # Workflow documentation
│   ├── new-analyzer.md          # Workflow: Creating new analyzer
│   ├── new-case-type.md         # Workflow: Adding case type
│   ├── add-ai-feature.md        # Workflow: Adding AI analysis
│   └── release-process.md       # Complete release workflow
│
├── hooks/                        # Project-specific hooks (optional)
│   ├── README.md                 # Hook documentation
│   └── pre-commit-check.sh      # Example pre-commit hook
│
└── config/                       # Configuration files
    ├── permissions.json          # IAM permissions config
    ├── agent-config.json         # Agent settings
    └── command-defaults.json     # Default command settings
```

---

## 🎯 Design Principles

### 1. **Namespaced Organization**
- Commands organized by purpose (discovery, development, analysis, etc.)
- Subdirectory names appear in command descriptions: `/prime (project:discovery)`
- Command names remain flat: `/prime` not `/discovery/prime`

### 2. **Progressive Disclosure**
- **Tier 1**: Core daily commands (commit, test-fix, prime)
- **Tier 2**: Specialized workflows (rca, package-release)
- **Tier 3**: Advanced/domain-specific (evidence toolkit operations)

### 3. **DRY Principle**
- Prompts extracted to `prompts/` for reuse
- Templates in `templates/` for consistency
- Agents in `agents/` for specialized tasks
- Commands delegate to agents when appropriate

### 4. **Discoverability**
- Each directory has README.md explaining contents
- Top-level README.md serves as main index
- AUTOMATION_GUIDE.md for user-facing documentation
- STRUCTURE_PLAN.md (this file) for maintainer reference

### 5. **Evidence Toolkit Specific**
- Domain-specific commands in `commands/evidence/`
- Forensic-focused prompts in `prompts/`
- Legal compliance workflows in `workflows/`

---

## 📋 Migration Plan

### Phase 1: Reorganize Existing Commands ✅

**Move commands into namespaced directories:**

```bash
# Discovery commands
.claude/commands/prime.md          → .claude/commands/discovery/prime.md
.claude/commands/status.md         → .claude/commands/discovery/status.md

# Development commands
.claude/commands/commit.md         → .claude/commands/development/commit.md
.claude/commands/test-fix.md       → .claude/commands/development/test-fix.md

# Documentation commands
.claude/commands/create-docs.md    → .claude/commands/documentation/create-docs.md
.claude/commands/update-docs.md    → .claude/commands/documentation/update-docs.md

# Analysis commands
.claude/commands/rca.md            → .claude/commands/analysis/rca.md

# Release commands
.claude/commands/package-release.md → .claude/commands/release/package-release.md
```

**Update top-level files:**
- Update README.md with new structure
- Keep AUTOMATION_GUIDE.md as user-facing docs
- Add this STRUCTURE_PLAN.md for maintainers

### Phase 2: Extract Reusable Prompts

**Create prompts library:**

```
prompts/
├── code-review.md           # Extract from /commit, /review
├── pydantic-validation.md   # Extract from /create-docs
├── forensic-integrity.md    # Evidence Toolkit standards
└── ai-prompt-engineering.md # OpenAI best practices
```

**Commands reference prompts:**
```markdown
## Review Standards
See: @prompts/code-review.md

## Validation Requirements
See: @prompts/pydantic-validation.md
```

### Phase 3: Add New Commands

**High-priority new commands:**

1. **`/ingest-case`** - Automated case ingestion
   ```bash
   /ingest-case /path/to/evidence --case-id CASE-001
   ```

2. **`/analyze-evidence`** - Analyze specific evidence
   ```bash
   /analyze-evidence sha256=abc123 --reanalyze
   ```

3. **`/correlate`** - Run correlation analysis
   ```bash
   /correlate --case-id CASE-001 --ai-resolve
   ```

4. **`/lint`** - Run code quality tools
   ```bash
   /lint
   /lint --fix
   ```

5. **`/review`** - Self-review before commit
   ```bash
   /review
   /review --full  # Include security audit
   ```

### Phase 4: Create Templates

**Command templates** (`.claude/commands/_templates/`):
- Basic read-only command
- Bash execution command
- Agent delegation command
- Workflow orchestration command

**Code templates** (`.claude/templates/`):
- New analyzer boilerplate
- New Pydantic model
- Test file structure
- Module documentation

### Phase 5: Document Workflows

**Multi-step workflows** (`.claude/workflows/`):

1. **new-analyzer.md** - Adding AI analyzer
   - Create model in `core/models.py`
   - Create analyzer in `analyzers/`
   - Add prompts to `domains/legal_config.py`
   - Write tests
   - Generate docs
   - Test end-to-end

2. **new-case-type.md** - Adding case type
   - Update `CASE_TYPES` enum
   - Add executive summary prompt
   - Update documentation
   - Test with sample case

3. **release-process.md** - Complete release
   - Run full test suite
   - Update all documentation
   - Version bump + changelog
   - Create tag and release
   - (Optional) Publish to PyPI

---

## 🔧 Implementation Notes

### Command Descriptions Will Change

**Before:**
```
/prime (project)
/commit (project)
```

**After:**
```
/prime (project:discovery)
/commit (project:development)
/ingest-case (project:evidence)
```

### Frontmatter Best Practices

All commands should have:
```markdown
---
description: Brief description (shows in /help)
argument-hint: [expected arguments]
allowed-tools: Tool1, Tool2, ...
model: claude-sonnet-4-5-20250929  # Optional, for specific needs
disable-model-invocation: false     # Set true to prevent auto-trigger
---
```

### Template Variables

**In prompts and templates:**
- `$ARGUMENTS` - All arguments as string
- `$1, $2, $3` - Positional arguments
- `@file/path` - File references
- `!`command`` - Bash command execution (requires allowed-tools)

### Agent Delegation Pattern

**When to delegate to agents:**
- Complex multi-step analysis
- Specialized domain expertise
- Want isolated context (save tokens)

**Pattern:**
```markdown
---
description: Analyze root cause
---

# Root Cause Analysis: $ARGUMENTS

Your task: Use the **rca-debugger** agent to analyze: $ARGUMENTS

The agent will provide systematic analysis following forensic standards.
```

---

## 🎨 Visual Organization

### Command Discovery Flow

```
User types /
  ↓
Sees categorized commands:
  • prime (project:discovery)
  • status (project:discovery)
  • commit (project:development)
  • test-fix (project:development)
  • rca (project:analysis)
  • ingest-case (project:evidence)
  ↓
Selects command
  ↓
Auto-complete shows argument-hint
  ↓
Command executes
```

### File Reference Flow

```
Command references prompt:
@prompts/code-review.md
  ↓
Claude reads prompt file
  ↓
Applies standards to current task
  ↓
Consistent behavior across commands
```

---

## 📊 Benefits

### For Users
- ✅ Clear categorization (discovery vs development vs evidence)
- ✅ Better autocomplete (argument hints)
- ✅ Fewer decisions (templates guide creation)
- ✅ Consistent workflows (documented in workflows/)

### For Maintainers
- ✅ DRY prompts (reusable snippets)
- ✅ Clear organization (namespaced directories)
- ✅ Easy to extend (templates for new commands)
- ✅ Self-documenting (README in each directory)

### For Evidence Toolkit
- ✅ Domain-specific commands (evidence/ directory)
- ✅ Forensic standards (prompts/forensic-integrity.md)
- ✅ Legal workflows (workflows/new-case-type.md)
- ✅ Compliance-focused (agents/evidence-forensics-expert.md)

---

## 🚀 Quick Start (After Migration)

### Daily Development
```bash
/prime                    # Start session
# ... make changes ...
/test-fix                 # Test
/lint --fix              # Format
/commit                  # Commit
```

### Adding New Analyzer
```bash
/workflows/new-analyzer  # Shows step-by-step guide
# Follow the workflow...
/test-fix                # Verify tests pass
/update-docs recent      # Document changes
```

### Processing Evidence
```bash
/ingest-case data/cases/NEW-CASE --case-id NEW-CASE
/analyze-evidence sha256=abc123
/correlate --case-id NEW-CASE --ai-resolve
/package-case --case-id NEW-CASE --case-type workplace
```

---

## 🔄 Rollback Plan

If this structure doesn't work out:

1. Extract backup: `tar -xzf .claude-backup-TIMESTAMP.tar.gz`
2. Review what worked vs. what didn't
3. Keep the good parts, revert the bad
4. Document lessons learned

**Backup created**: `.claude-backup-20251007-204041.tar.gz`

---

## 📝 Next Steps

1. ✅ Create this plan document
2. ⏳ Review and approve structure
3. ⏳ Implement Phase 1 (reorganize existing)
4. ⏳ Implement Phase 2 (extract prompts)
5. ⏳ Implement Phase 3 (new commands)
6. ⏳ Implement Phase 4 (templates)
7. ⏳ Implement Phase 5 (workflows)
8. ⏳ Update CLAUDE.md with new structure
9. ⏳ Test all commands work correctly
10. ⏳ Create migration guide for other projects

---

**Status**: PLANNING - Ready for review and approval
**Backup**: `.claude-backup-20251007-204041.tar.gz` (26KB)
**Estimated Time**: 2-3 hours to complete full migration
**Risk Level**: Low (full backup exists, easy rollback)
