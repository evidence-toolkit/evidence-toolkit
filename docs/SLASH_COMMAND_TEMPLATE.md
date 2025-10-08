# Slash Command Template & Best Practices

> **Purpose**: Reusable template and guidelines for creating maintainable Claude Code slash commands for the Evidence Toolkit project.

**Version**: 1.0
**Last Updated**: 2025-10-06
**Related**: `.claude/commands/`, [Claude Code Slash Commands Docs](https://docs.anthropic.com/en/docs/claude-code/slash-commands)

---

## Table of Contents

1. [Quick Template](#quick-template)
2. [Best Practices](#best-practices)
3. [Command Patterns](#command-patterns)
4. [Anti-Patterns](#anti-patterns)
5. [Real Examples](#real-examples)
6. [Testing Commands](#testing-commands)

---

## Quick Template

Use this as a starting point for new slash commands:

```markdown
---
description: Brief action-oriented description (under 60 chars)
argument-hint: [arg1] [optional-arg2]
allowed-tools: Bash(command:*), Read, Edit, Write, Grep, Glob
---

# Command Name

Brief explanation of what this command does and when to use it.

## Context

**Dynamic Information Gathering:**
!`command to get current project state`
!`another command for relevant context`

**Static Context (if needed):**
- Important constants or configuration
- Expected directory structure
- Project-specific conventions

---

## Your Task

Clear, specific instructions for Claude Code to execute.

### Instructions

1. **First Step**: What to do first
   - Use `$ARGUMENTS` or `$1`, `$2` for parameters
   - Provide conditional logic: "If $ARGUMENTS contains 'flag'..."

2. **Second Step**: What to do next
   - Show example bash commands if needed
   - Explain expected outcomes

3. **Final Step**: How to complete and report
   - What to output to the user
   - What files to create/modify
   - Success criteria

### Arguments

**If provided `$ARGUMENTS`:**
- Explain how arguments affect behavior
- Provide examples: `/command foo bar`

**If no arguments:**
- Default behavior
- Prompt user if needed

### Error Handling

- What can go wrong
- How to detect errors
- Recovery strategies
- When to ask for user input

---

## Expected Output

Format guide for Claude's response:

```
🎯 Command Name: [Action]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Status updates as work proceeds]

✅ Results:
   • Item 1
   • Item 2

💡 Next Steps:
   - Recommendation 1
   - Recommendation 2
```

---

## Notes

- **Performance**: Estimated runtime or token usage
- **Dependencies**: Required tools, environment variables, or files
- **Side Effects**: What this command modifies
- **Related Commands**: Other commands that might be useful
```

---

## Best Practices

### 1. **Dynamic Discovery Over Hardcoding**

✅ **DO**: Use bash commands to discover current state
```markdown
## Context
**Current Test Files:**
!`find tests/ -name "test_*.py" -type f | sort`

**Recent Changes:**
!`git diff --name-only HEAD~5..HEAD -- 'src/**/*.py'`
```

❌ **DON'T**: Hardcode file lists that go stale
```markdown
## Read These Files:
- src/evidence_toolkit/core/models.py
- src/evidence_toolkit/core/storage.py
- src/evidence_toolkit/analyzers/document.py
# ↑ This becomes outdated as codebase evolves
```

### 2. **Explicit Tool Permissions**

✅ **DO**: Specify exact commands and patterns
```yaml
---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Read, Edit
---
```

❌ **DON'T**: Use broad permissions requiring approval
```yaml
---
allowed-tools: Bash, Read, Write  # Too broad - will prompt for approval
---
```

**Tool Permission Patterns:**
- `Bash(git add:*)` - Allows `git add` with any arguments
- `Bash(uv run pytest:*)` - Allows `uv run pytest ...`
- `Bash(ls:*)` - Allows `ls` commands
- `Read, Write, Edit` - File operations (no patterns needed)
- `Grep, Glob` - Search operations (no patterns needed)

### 3. **Argument Handling**

**Use `$ARGUMENTS` for all args:**
```markdown
/command foo bar baz
# $ARGUMENTS = "foo bar baz"

Process all arguments: $ARGUMENTS
```

**Use `$1`, `$2`, etc. for positional args:**
```markdown
/command patch v3.1.0
# $1 = "patch"
# $2 = "v3.1.0"

Version bump type: $1
Target version: $2
```

**Conditional logic:**
```markdown
If $ARGUMENTS contains "recent":
  - Process only recent changes
Otherwise if $ARGUMENTS contains "all":
  - Process entire codebase
  - ⚠️ Warn about token usage
Otherwise:
  - Treat $ARGUMENTS as specific file/module path
```

### 4. **Self-Documenting Descriptions**

✅ **DO**: Action-oriented, clear purpose
```yaml
description: Run tests and automatically fix failures
description: Create git commit following project conventions
description: Enhanced root-cause analysis for bugs and errors
```

❌ **DON'T**: Vague or overly technical
```yaml
description: Test helper
description: Commit stuff
description: Debug things
```

### 5. **Bash Context with `!` Prefix**

**Dynamic context gathering:**
```markdown
## Context

**Git Status:**
!`git status --short`

**Package Version:**
!`grep '^version = ' pyproject.toml | cut -d'"' -f2`

**Storage Stats:**
!`find data/storage/raw -type f 2>/dev/null | wc -l`
```

**Key Benefits:**
- Always fresh data
- No manual updates needed
- Shows real project state
- Works across different project states

### 6. **Error Prevention**

Include common failure modes and recovery:

```markdown
### Error Handling

**Uncommitted Changes:**
- Detect: `git status --short` has output
- Action: Warn user, offer to commit first

**Missing Dependencies:**
- Detect: Command not found errors
- Action: Show installation command: `uv pip install <package>`

**Permission Denied:**
- Detect: Permission error in output
- Action: Suggest `chmod +x` or check file ownership
```

---

## Command Patterns

### Pattern 1: Discovery Command
**Purpose**: Understand current project state
**Example**: `/status`, `/prime`

```markdown
---
description: Check current project status
allowed-tools: Bash(ls:*), Bash(find:*), Bash(uv run python:*)
---

# Status Check

## Execute

!`echo "=== PROJECT STATUS ==="`
!`ls -la`
!`find data/ -type f | wc -l`
!`uv run evidence-toolkit --version`

## Report

Summarize what you found:
- Project structure
- Data present
- Version installed
- Any issues detected
```

### Pattern 2: Action Command
**Purpose**: Perform operation with validation
**Example**: `/commit`, `/test-fix`

```markdown
---
description: Action with argument
argument-hint: [required-arg]
allowed-tools: Bash(specific:*), Read, Edit
---

# Perform Action

## Context
!`get current state`

## Your Task

1. Validate $ARGUMENTS
2. Perform operation
3. Verify success
4. Report results

### Validation
- Check prerequisites
- Confirm with user if destructive

### Execution
- Step by step with error handling
- Show progress

### Verification
- Confirm operation succeeded
- Show before/after state
```

### Pattern 3: Generator Command
**Purpose**: Create documentation or code
**Example**: `/create-docs`, `/update-docs`

```markdown
---
description: Generate content based on template
argument-hint: [target]
allowed-tools: Read, Write, Grep, Glob
---

# Generate Content

## Your Task

Create [type of content] for: $ARGUMENTS

### Discovery
1. Find target (file, module, etc.)
2. Analyze structure and purpose
3. Gather related information

### Generation
1. Follow template structure
2. Include examples and usage
3. Add cross-references

### Validation
1. Check completeness
2. Verify formatting
3. Save to appropriate location

### Report
- What was created
- Where it was saved
- Suggestions for next steps
```

### Pattern 4: Analysis Command
**Purpose**: Investigate and report (no changes)
**Example**: `/rca`

```markdown
---
description: Analyze issue without making changes
argument-hint: [error-message|file-path]
---

# Analysis Task

## Your Task

Analyze: $ARGUMENTS

**Important**: This is analysis-only. Do NOT implement changes.

### Analysis Steps
1. Gather evidence (logs, traces, files)
2. Form hypotheses (ranked by likelihood)
3. Assess impact and scope
4. Recommend solutions

### Report Format
- Problem statement
- Evidence gathered
- Root cause analysis
- Recommended fixes
- Prevention strategy
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Stale Hardcoded Lists

**Problem:**
```markdown
# Prime Command

Read these files:
- src/evidence_toolkit/core/models.py
- src/evidence_toolkit/core/storage.py
- src/evidence_toolkit/analyzers/document.py
# ↑ Breaks when you add new analyzers or rename files
```

**Solution:**
```markdown
# Prime Command

## Context

**Core Modules:**
!`find src/evidence_toolkit/core -name "*.py" -type f | sort`

**Analyzers:**
!`find src/evidence_toolkit/analyzers -name "*.py" -type f | sort`

**Documentation:**
!`find docs/ -name "*.md" | grep -E "(README|ARCHITECTURE|V3)" | sort`

## Your Task

Read the files discovered above and understand the project structure.
```

### ❌ Anti-Pattern 2: Overly Complex Logic

**Problem:**
```markdown
If $1 equals "major" and $2 is not empty and $3 contains "force":
  Do complex thing
Else if $1 equals "minor" or ($1 equals "m" and $ARGUMENTS doesn't contain "major"):
  Do other complex thing
# ↑ Too complicated, error-prone
```

**Solution:**
```markdown
**Version Bump Type**: $1 (major|minor|patch)

If $ARGUMENTS is empty:
  - Analyze commits to recommend bump type
  - Ask user to confirm

Otherwise:
  - Use $1 as bump type
  - Validate it's one of: major, minor, patch
```

### ❌ Anti-Pattern 3: Missing Error Handling

**Problem:**
```markdown
## Your Task

Run: `git commit -m "$ARGUMENTS"`
```

**Solution:**
```markdown
## Your Task

Create a git commit.

### Validation
1. Check for uncommitted changes: `git status --short`
   - If empty, warn: "No changes to commit"
2. Check for sensitive files (.env, *.key)
   - If found, warn user before committing

### Execution
1. Stage files: `git add <files>`
2. Create commit: `git commit -m "..."`

### Verification
1. Confirm commit created: `git log -1 --oneline`
2. Show what was committed: `git show --stat`
```

### ❌ Anti-Pattern 4: No User Feedback

**Problem:**
```markdown
Run pytest. Fix failures. Done.
```

**Solution:**
```markdown
## Your Task

Run tests and fix failures.

### Execution
1. **Run Tests**
   ```bash
   uv run pytest tests/test_critical.py -v
   ```
   Show: ✅ X passed, ❌ Y failed, ⏭️ Z skipped

2. **If Failures**
   For each failure:
   - 🔍 Analyze: Read test file, understand expectation
   - 🔧 Fix: Edit source to resolve issue
   - 📊 Report: "Fixed test_foo by adding null check in models.py:123"

3. **Re-run & Verify**
   ```bash
   uv run pytest tests/test_critical.py -v
   ```
   Show final results

### Output Format
```
🧪 Running Tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[test output]

📊 Results: 5 passed, 2 failed

🔧 Fixing Failures...
  ✓ test_foo: Added validation
  ✓ test_bar: Fixed type hint

🔄 Re-running...
✅ All tests passing!
```
```

---

## Real Examples

### Example 1: Excellent - `/status` Command

**Why it works:**
- ✅ Pure bash discovery (lines 8-105)
- ✅ Adapts to project version (v3.1 feature detection)
- ✅ Checks both current and legacy paths
- ✅ Clear reporting format
- ✅ No hardcoded assumptions

**Key techniques:**
```bash
# Conditional checks
if [ -d data/storage/raw ]; then
    raw_count=$(find data/storage/raw -type f 2>/dev/null | wc -l)
    echo "  Raw files: $raw_count"
elif [ -d evidence/raw ]; then
    echo "  Legacy evidence/: ..."
fi

# Feature detection
if grep -q "legal_patterns" "$corr_file" 2>/dev/null; then
    echo "    ✨ v3.1 legal patterns detected"
fi
```

### Example 2: Excellent - `/commit` Command

**Why it works:**
- ✅ Dynamic git context with `!` prefix
- ✅ Explicit tool permissions
- ✅ Clear conventions (commit types, format)
- ✅ Heredoc for proper formatting
- ✅ Safety checks (sensitive files)

**Key techniques:**
```markdown
## Context

**Current Status:**
!`git status`

**Staged & Unstaged Changes:**
!`git diff HEAD`

**Recent Commit Style (for reference):**
!`git log --oneline -10`
```

### Example 3: Good - `/rca` Command

**Why it works:**
- ✅ Uses Task tool for complex analysis
- ✅ Clear argument handling ($1, $2)
- ✅ Analysis-only (no code changes)
- ✅ Structured output format

**Key techniques:**
```markdown
## Input Analysis
- **Primary target**: $1 (error message, test name, or file path)
- **Additional context**: $2 (optional: related files, recent changes)

## Your Task
Using the **rca-debugger** subagent, perform analysis of: **$ARGUMENTS**

**IMPORTANT**: This is analysis-only. Do not implement changes.
```

### Example 4: Needs Improvement - Old `/prime` Command

**Why it needs work:**
- ❌ Hardcoded file list (lines 7-24)
- ❌ Breaks when files are added/renamed
- ❌ Requires manual maintenance
- ✅ But: Good reporting structure

**Refactoring approach:**
```markdown
# Before (hardcoded)
Read:
- V3_ARCHITECTURE.md
- src/evidence_toolkit/core/models.py
- src/evidence_toolkit/core/storage.py

# After (dynamic)
## Context

**Documentation Files:**
!`find . -maxdepth 1 -name "*.md" | grep -E "(README|ARCHITECTURE|V3|CLAUDE)" | sort`

**Core Python Modules:**
!`find src/evidence_toolkit/core -name "*.py" -type f | sort`

**Key Configuration:**
!`ls -1 pyproject.toml .gitignore quick-start.sh 2>/dev/null`

## Your Task
Read the files discovered above (documentation first, then code).
```

---

## Testing Commands

### Quick Test Checklist

Before committing a new slash command:

1. **Syntax Check**
   ```bash
   # Frontmatter must be valid YAML
   head -5 .claude/commands/mycommand.md
   ```

2. **Test with Arguments**
   ```
   /mycommand foo
   /mycommand foo bar baz
   /mycommand
   ```

3. **Test Edge Cases**
   - Empty arguments
   - Invalid arguments
   - Missing files/directories
   - Clean vs dirty git state

4. **Verify Tool Permissions**
   - Should NOT prompt for approval if `allowed-tools` is correct
   - Test each bash command pattern listed

5. **Check Reusability**
   - Will this work in 6 months when codebase has changed?
   - Does it discover state dynamically?
   - Are paths/files hardcoded?

### Testing in Development

```bash
# 1. Create command file
cat > .claude/commands/test.md << 'EOF'
---
description: Test command
---

# Test

!`echo "Testing: $ARGUMENTS"`

## Your Task
Process: $ARGUMENTS
EOF

# 2. Use in Claude Code
/test hello world

# 3. Check output
# Should show: "Testing: hello world"

# 4. Iterate until working as expected
```

---

## Evidence Toolkit Specific Notes

### Project Context

This is a **forensic evidence analysis toolkit** for legal professionals. Commands should:

- ✅ Respect chain of custody principles
- ✅ Preserve data integrity (SHA256 content addressing)
- ✅ Use deterministic AI analysis (temperature=0)
- ✅ Validate all Pydantic models
- ✅ Handle sensitive data carefully

### Common Paths

**Dynamic discovery** (preferred):
```bash
# Find core modules
find src/evidence_toolkit/core -name "*.py"

# Find analyzers
find src/evidence_toolkit/analyzers -name "*.py"

# Check data storage
find data/storage -type f 2>/dev/null | wc -l

# Get package version
uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)"
```

**Environment:**
```bash
# Always use UV for Python commands
uv run evidence-toolkit --help
uv run pytest tests/
uv pip install -e .

# Git conventions
git log --oneline -10              # Recent commits
git diff HEAD                      # All changes
git status --short                 # Concise status
```

### V3.1 Feature Detection

Commands should adapt to version changes:

```bash
# Check for v3.1 features
if grep -q "legal_patterns.*LegalPatternAnalysis" src/evidence_toolkit/core/models.py; then
    echo "✅ v3.1 AI enhancements: PRESENT"
fi

# Check data for v3.1 analysis
has_legal=$(find data/storage/derived -name "*.json" -exec grep -l "legal_patterns" {} \; 2>/dev/null | wc -l)
if [ $has_legal -gt 0 ]; then
    echo "✨ v3.1 legal patterns: $has_legal files"
fi
```

---

## Template Checklist

Use this when creating a new command:

```markdown
- [ ] Frontmatter complete (description, argument-hint, allowed-tools)
- [ ] Description is action-oriented and under 60 chars
- [ ] Tool permissions are specific (no broad "Bash" without patterns)
- [ ] Uses `!` prefix for dynamic context gathering
- [ ] No hardcoded file lists (use find/ls/grep instead)
- [ ] Arguments handled clearly ($ARGUMENTS or $1, $2, etc.)
- [ ] Error handling included (what can go wrong, how to recover)
- [ ] Expected output format provided
- [ ] Tested with: args, no args, edge cases
- [ ] Will work 6 months from now without updates
```

---

## Quick Reference

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `description` | Yes | Shows in `/help` | `Run tests and fix failures` |
| `argument-hint` | Recommended | Shows expected args | `[module-path]` or `[major\|minor\|patch]` |
| `allowed-tools` | Optional | Prevents approval prompts | `Bash(git add:*), Read, Edit` |
| `model` | Optional | Override model for this command | `claude-sonnet-4-5-20250929` |
| `disable-model-invocation` | Optional | Prevent SlashCommand tool use | `true` |

### Bash Context Syntax

```markdown
## Context

**Label:**
!`bash command here`
```

**Output appears in context for Claude to use.**

### Argument Variables

| Variable | Contains | Example |
|----------|----------|---------|
| `$ARGUMENTS` | All arguments as string | `/cmd foo bar` → `"foo bar"` |
| `$1` | First argument | `/cmd foo bar` → `"foo"` |
| `$2` | Second argument | `/cmd foo bar` → `"bar"` |
| `$3`, `$4`... | Additional positional args | Continue as needed |

### Common Tool Permissions

```yaml
# Git operations
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git add:*), Bash(git commit:*)

# Testing
allowed-tools: Bash(uv run pytest:*), Bash(uv run python:*), Read, Edit

# File operations (no restrictions needed)
allowed-tools: Read, Write, Edit, Grep, Glob

# System commands
allowed-tools: Bash(ls:*), Bash(find:*), Bash(tree:*)

# UV/Python commands
allowed-tools: Bash(uv run:*), Bash(uv pip:*), Bash(uv build:*)
```

---

## Resources

- **Claude Code Docs**: https://docs.anthropic.com/en/docs/claude-code/slash-commands
- **Project Commands**: `.claude/commands/`
- **Command Examples**:
  - [status.md](../.claude/commands/status.md) - Best practice example
  - [commit.md](../.claude/commands/commit.md) - Dynamic context usage
  - [rca.md](../.claude/commands/rca.md) - Task tool delegation
- **Evidence Toolkit Conventions**: See [CLAUDE.md](../CLAUDE.md)

---

## Changelog

**v1.0** (2025-10-06)
- Initial template created
- Best practices documented from `/status`, `/commit`, `/rca` analysis
- Anti-patterns identified from legacy `/prime` command
- Evidence Toolkit specific guidelines added

---

**Next**: Use this template to refactor `/prime`, `/test-fix`, and `/update-docs` for better maintainability.
