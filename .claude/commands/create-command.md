---
description: Create a new slash command following Claude Code best practices
argument-hint: <command-name> <description>
allowed-tools: Task
---

# Create Slash Command

Generate a new slash command for Claude Code following official best practices and Evidence Toolkit conventions.

## Usage

```bash
/create-command <command-name> <description>
```

## Arguments

- `$1` - Command name (will become `/[name]`)
- `$ARGUMENTS` - Full request including description

## Examples

```bash
# Create a deployment command
/create-command deploy "Deploy to staging with health checks and rollback"

# Create a database migration command
/create-command migrate "Run database migrations safely with backup"

# Create a code review helper
/create-command review-pr "Review pull request with security and performance focus"
```

---

## Context

**Existing Slash Commands (for pattern consistency):**
!`ls -1 .claude/commands/*.md | wc -l` commands currently defined

**Sample existing patterns:**
!`ls -1 .claude/commands/ | head -8`

**Project conventions:**
- Evidence Toolkit uses `uv run` for all commands
- AI operations use OpenAI API
- Storage is content-addressed (SHA256)
- CLI tool: `evidence-toolkit`

---

## Your Task

Delegate to the **command-builder** subagent to create this slash command.

**Provide the subagent with:**
1. **Command name**: `$1` (extracted from arguments)
2. **User description**: `$ARGUMENTS`
3. **Context about existing commands**: List of current commands in `.claude/commands/`
4. **Project patterns**: Evidence Toolkit conventions (uv, content-addressed storage, etc.)
5. **Target location**: `.claude/commands/$1.md`

**The command-builder will:**
- Ask clarifying questions about:
  - Arguments needed (`$ARGUMENTS`, `$1 $2`, or none)
  - Tools required (`Task`, `Bash`, `Read`, `Write`, etc.)
  - Whether it delegates to a subagent
  - Pre-execution checks (bash commands with `!` prefix)
  - Model preference (inherit, sonnet, haiku)
- Read Claude Code documentation for best practices
- Analyze existing Evidence Toolkit command patterns
- Generate the `.md` file with validated frontmatter
- Provide usage examples and testing instructions

**Expected output:**
- New file: `.claude/commands/$1.md`
- Usage guidance: How to invoke and test the command
- Related commands: Suggestions for complementary workflows

---

## Notes

**After creation:**
- Test the command: `/$1 [args]`
- Verify it appears in `/help`
- Edit `.claude/commands/$1.md` to refine behavior
- Consider creating a related subagent for complex workflows

**Best practices:**
- Keep commands focused on single workflows
- Delegate complex logic to subagents (use `allowed-tools: Task`)
- Use `!` prefix for pre-execution bash commands
- Add `argument-hint` for auto-completion
- Include clear descriptions for `/help` visibility

**Related:**
- `/create-agent` - Create a subagent for complex logic
- `/command-docs` - View slash command syntax reference
- `/agents` - Manage existing subagents
