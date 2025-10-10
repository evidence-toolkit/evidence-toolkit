---
description: Show Claude Code slash command and subagent documentation reference
allowed-tools: Read
---

# Command Documentation Reference

Quick reference for creating slash commands and subagents in Claude Code.

---

## Slash Command Syntax

### File Structure
```markdown
---
description: Brief description shown in /help
argument-hint: <arg1> [optional-arg2]
allowed-tools: Tool1, Tool2, Tool3
model: sonnet|opus|haiku|inherit  # Optional
disable-model-invocation: true|false  # Optional
---

# Command Title

Your command prompt goes here.

## Usage
```bash
/command-name <args>
```

## Arguments
- `$ARGUMENTS` - All arguments as single string
- `$1` - First positional argument
- `$2` - Second positional argument

## Context
**Pre-execution:**
!`bash command to run before execution`
```

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `description` | Yes | Brief description for /help | `Create a git commit` |
| `argument-hint` | No | Auto-completion hint | `<case-id> [--options]` |
| `allowed-tools` | No | Tools this command can use | `Bash, Read, Write` |
| `model` | No | Model to use | `sonnet`, `haiku`, `inherit` |
| `disable-model-invocation` | No | Prevent SlashCommand tool from calling this | `true` |

### Argument Patterns

```markdown
# All arguments
$ARGUMENTS  → "arg1 arg2 arg3"

# Positional arguments
$1  → "arg1"
$2  → "arg2"
$3  → "arg3"

# Mixed usage
/fix-issue $1 with priority $2
→ /fix-issue 123 with priority high
```

### Bash Execution

Use `!` prefix to run commands before execution:

```markdown
## Context

**Current branch:**
!`git branch --show-current`

**Recent changes:**
!`git diff --stat`

**File count:**
!`find . -name "*.py" | wc -l`
```

### File References

Use `@` prefix to include file contents:

```markdown
Review the implementation in @src/utils/helpers.js

Compare @src/old-version.js with @src/new-version.js
```

### Delegating to Subagents

```markdown
---
allowed-tools: Task
---

## Your Task

Using the **[subagent-name]** subagent, perform [task].

[Provide context and instructions for the subagent]
```

---

## Subagent Syntax

### File Structure

```markdown
---
name: agent-name
description: When to invoke. Use PROACTIVELY when [trigger]
tools: Read, Write, Edit, Bash  # Optional - omit to inherit all
model: sonnet  # Optional - sonnet|opus|haiku|inherit
---

# Agent Name - Expert Title

You are the **[Agent Name]**, an expert in [domain].

## Your Responsibilities

[What this agent does]

## Workflow

When invoked:
1. [Step 1]
2. [Step 2]

## Success Criteria

You've succeeded when:
1. ✅ [Criterion 1]
2. ✅ [Criterion 2]
```

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `name` | Yes | Unique identifier (lowercase-with-hyphens) | `test-runner` |
| `description` | Yes | When to invoke this agent | `Use PROACTIVELY after code changes` |
| `tools` | No | Comma-separated tools (omit to inherit all) | `Read, Write, Edit, Bash` |
| `model` | No | Model alias or inherit | `sonnet`, `haiku`, `inherit` |

### Model Selection

- `sonnet` - Default, balanced (Claude 3.5 Sonnet)
- `opus` - Maximum capability
- `haiku` - Fast, lightweight
- `inherit` - Use main conversation's model

### Tool Inheritance

```yaml
# Inherit ALL tools (including MCP)
tools:  # Omit this field entirely

# Restrict to specific tools
tools: Read, Write, Edit, Bash

# For delegation workflows
tools: Task
```

### Proactivity Triggers

Add to `description` field:

```yaml
# Automatic invocation on code changes
description: Use PROACTIVELY after code changes to run tests

# Strong signal for automatic use
description: MUST BE USED for deployment workflows

# Explicit trigger
description: Use when encountering errors or test failures
```

---

## Available Tools

**File Operations:**
- `Read` - Read files
- `Write` - Create/overwrite files
- `Edit` - Modify existing files
- `Glob` - Find files by pattern
- `Grep` - Search file contents

**Execution:**
- `Bash` - Run shell commands
- `Task` - Invoke subagents

**Web:**
- `WebFetch` - Fetch and analyze URLs
- `WebSearch` - Search the web

**MCP Tools:**
- `mcp__context7__resolve-library-id` - Find library documentation
- `mcp__context7__get-library-docs` - Fetch library docs
- [Other MCP servers if configured]

**Special:**
- `SlashCommand` - Execute slash commands programmatically
- `TodoWrite` - Manage todo lists

---

## Evidence Toolkit Patterns

### Command Patterns

**Delegation Pattern** ([/api](.claude/commands/api.md)):
```yaml
allowed-tools: Task
```
Then invoke subagent via Task tool.

**Bash Execution Pattern** ([/prime](.claude/commands/prime.md)):
```markdown
!`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)"`
```

**Multi-argument Pattern** ([/api-process-case](.claude/commands/api-process-case.md)):
```yaml
argument-hint: <case-id> [--case-type <type>] [--ai-resolve]
```

### Agent Patterns

**Architecture Specialist** ([v4-architect](.claude/agents/v4-architect.md)):
- Comprehensive system prompt
- Detailed working pattern
- Success criteria
- What NOT to do section

**API Handler** ([api-handler](.claude/agents/api-handler.md)):
- Focused, single-purpose
- Structured JSON responses
- Error handling patterns
- Security considerations

**Forensics Expert** ([evidence-forensics-expert](.claude/agents/evidence-forensics-expert.md)):
- Domain-specific expertise
- Chain of custody focus
- Legal compliance constraints

---

## Quick Examples

### Simple Command
```markdown
---
description: Run pytest with coverage
allowed-tools: Bash
---

Run the test suite:
```bash
uv run pytest --cov --cov-report=term
```
```

### Command with Arguments
```markdown
---
description: Analyze evidence file
argument-hint: <file-path>
allowed-tools: Bash
---

Analyze evidence: `$1`

```bash
uv run evidence-toolkit analyze $1
```
```

### Delegating Command
```markdown
---
description: Create comprehensive documentation
argument-hint: <module-path>
allowed-tools: Task
---

Using the **doc-writer** subagent, create documentation for: `$1`
```

### Simple Agent
```markdown
---
name: test-fixer
description: Use PROACTIVELY when tests fail to analyze and fix issues
tools: Bash, Read, Edit, Grep
model: sonnet
---

You are a test fixing expert. When tests fail:
1. Run pytest to capture failures
2. Analyze error messages
3. Fix the underlying code
4. Re-run tests to verify
5. Report results
```

---

## File Locations

**Project Commands:** `.claude/commands/<name>.md`
**User Commands:** `~/.claude/commands/<name>.md`

**Project Agents:** `.claude/agents/<name>.md`
**User Agents:** `~/.claude/agents/<name>.md`

---

## Related Commands

- `/create-command` - Create a new slash command
- `/create-agent` - Create a new subagent
- `/agents` - Manage existing agents interactively
- `/help` - List all available commands

---

## Official Documentation

**Read these for full details:**
- `~/.claude-code-docs/docs/slash-commands.md` - Comprehensive slash command guide
- `~/.claude-code-docs/docs/sub-agents.md` - Comprehensive subagent guide
- `~/.claude-code-docs/docs/common-workflows.md` - Best practice patterns

---

**Use `/create-command` and `/create-agent` to automatically generate properly formatted files.**
