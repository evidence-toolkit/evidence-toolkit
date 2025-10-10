---
description: Create a new subagent following Claude Code best practices
argument-hint: <agent-name> <description>
allowed-tools: Task
---

# Create Subagent

Generate a new subagent for Claude Code following official best practices and Evidence Toolkit conventions.

## Usage

```bash
/create-agent <agent-name> <description>
```

## Arguments

- `$1` - Agent name (lowercase-with-hyphens)
- `$ARGUMENTS` - Full request including description and behavior

## Examples

```bash
# Create a test automation agent
/create-agent test-runner "Proactively run tests and fix failures without asking"

# Create a documentation generator
/create-agent doc-writer "Generate comprehensive module documentation from source code"

# Create a deployment specialist
/create-agent deployment-expert "Handle staging/production deployments with health checks and rollback"

# Create a security scanner
/create-agent security-auditor "Scan code for vulnerabilities, secrets, and security issues"
```

---

## Context

**Existing Subagents (for pattern consistency):**
!`ls -1 .claude/agents/*.md 2>/dev/null | wc -l` agents currently defined

**Current agents:**
!`ls -1 .claude/agents/ 2>/dev/null`

**Project conventions:**
- Evidence Toolkit uses `uv run` for CLI operations
- AI operations use OpenAI API (GPT-4o-mini, GPT-4o)
- Content-addressed storage with SHA256 hashing
- Pydantic models for all data validation
- Forensic focus: deterministic, temperature=0, chain of custody

---

## Your Task

Delegate to the **command-builder** subagent to create this specialized AI agent.

**Provide the subagent with:**
1. **Agent name**: `$1` (extracted from arguments)
2. **User description**: `$ARGUMENTS`
3. **Context about existing agents**: List of current agents in `.claude/agents/`
4. **Project patterns**: Evidence Toolkit conventions (forensic focus, Pydantic, etc.)
5. **Target location**: `.claude/agents/$1.md`

**The command-builder will:**
- Ask clarifying questions about:
  - **When to invoke**: Proactive triggers or explicit requests
  - **Tools needed**: Read, Write, Edit, Bash, Grep, Glob, Task, WebFetch, MCP tools
  - **Model preference**: sonnet (default), opus, haiku, inherit
  - **Proactivity**: Should Claude use this automatically? (Add "Use PROACTIVELY")
  - **Behavior constraints**: Guardrails (never modify X, always validate Y)
  - **Success criteria**: How to know when task is complete
- Read Claude Code documentation for best practices
- Analyze existing Evidence Toolkit agent patterns (v4-architect, api-handler, etc.)
- Generate the `.md` file with validated frontmatter
- Provide usage examples and testing instructions

**Expected output:**
- New file: `.claude/agents/$1.md`
- Usage guidance: How to invoke and test the agent
- Related agents: Suggestions for complementary agents

---

## Notes

**After creation:**
- Test the agent: "Use the `$1` agent to [task]"
- Verify it appears in `/agents` interface
- Edit `.claude/agents/$1.md` to refine behavior
- Consider creating a slash command wrapper for common workflows

**Best practices:**
- **Single responsibility**: One agent, one expertise area
- **Proactive descriptions**: Include "Use PROACTIVELY when [trigger]" for automatic invocation
- **Tool minimalism**: Only grant tools needed for the task (or omit `tools` to inherit all)
- **Clear success criteria**: Define what "done" looks like
- **Detailed prompts**: Include examples, constraints, working patterns

**Proactivity triggers:**
- "Use PROACTIVELY after code changes" → Auto-runs when code is modified
- "Use PROACTIVELY when encountering errors" → Auto-invoked on failures
- "MUST BE USED for [task type]" → Strong signal for automatic invocation

**Model selection:**
- `sonnet` - Default, balanced performance (Claude 3.5 Sonnet)
- `opus` - Maximum capability for complex reasoning
- `haiku` - Fast, lightweight for simple tasks
- `inherit` - Use same model as main conversation

**Tool inheritance:**
- **Omit `tools` field** → Inherits ALL tools from main thread (including MCP)
- **Specify tools** → Restricts to listed tools only (security/focus)

**Related:**
- `/create-command` - Create a slash command that invokes this agent
- `/agents` - Manage existing agents interactively
- `/command-docs` - View subagent syntax reference

---

## Common Agent Patterns

### Debugger/Fixer Agents
```yaml
description: Use PROACTIVELY when encountering errors, test failures, or bugs
tools: Read, Edit, Bash, Grep, Glob
model: sonnet
```

### Documentation Agents
```yaml
description: Use PROACTIVELY after code changes to update documentation
tools: Read, Write, Grep, Glob, Bash
model: haiku  # Fast for documentation tasks
```

### Architecture Agents
```yaml
description: Expert in [framework/pattern]. Use for infrastructure design and refactoring
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus  # Complex reasoning for architecture decisions
```

### Automation Agents
```yaml
description: Use PROACTIVELY to handle [workflow]. Executes without confirmation
tools: Bash, Read, Write
model: inherit  # Match main conversation model
```

---

## Examples of Subagent Invocation

**Explicit:**
```
> Use the test-runner agent to fix failing tests
> Have the security-auditor agent scan for vulnerabilities
> Ask the doc-writer agent to document the new module
```

**Automatic (when description includes "Use PROACTIVELY"):**
```
User: "I just modified the analyzer code"
Claude: [Automatically invokes test-runner agent to run tests]

User: "The build is failing with errors"
Claude: [Automatically invokes debugger agent for root cause analysis]
```

---

**Create specialized agents to automate your workflows. The more specific the agent, the better it performs.**
