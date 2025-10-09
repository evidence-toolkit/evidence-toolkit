# Troubleshooting: Code Duplication Detection

Common issues and solutions when using the `/detect-duplicates` command.

---

## Permission Issues with Bash Commands

### The Problem

If you see errors like:
```
(eval):1: permission denied:
```

This happens when slash commands use complex bash piping and command substitution:

```bash
# ❌ This causes permission errors in Claude Code
grep -r "^def " "$TARGET_DIR" --include="$PATTERN" 2>/dev/null | \
  sed 's/^[[:space:]]*//' | \
  sed 's/(.*$//' | \
  sort | uniq -c | sort -rn
```

**Root Cause**: Claude Code's bash execution environment has restrictions on:
- Complex shell piping (`|`)
- Command substitution (`$(...)`)
- Variable expansion in certain contexts
- Subshell operations

### The Solution

**Use Claude Code's dedicated tools instead of bash commands:**

| ❌ Don't Use | ✅ Use Instead |
|-------------|---------------|
| `bash grep` | **Grep tool** |
| `bash find` | **Glob tool** |
| `bash cat` | **Read tool** |
| `bash echo >` | **Write tool** |

**Example Fix:**

```markdown
# ❌ OLD (causes permission errors)
```bash
grep -r "^def " "$TARGET_DIR" --include="$PATTERN" | sed 's/(.*$//'
```

# ✅ NEW (works correctly)
Use the **Grep** tool:
- Pattern: `^def `
- Path: `src/evidence_toolkit`
- Type: `py`
- Output mode: `content`
- Line numbers: Yes (`-n`)
```

---

## Updated Command

The `/detect-duplicates` command has been **rewritten** (as of 2025-10-09) to use:

- ✅ **Glob tool** for file discovery (not `find`)
- ✅ **Grep tool** for pattern matching (not `bash grep`)
- ✅ **Read tool** for reading files (not `cat`)
- ✅ **Write tool** for generating reports (not `echo >`)

This eliminates all permission issues.

---

## General Best Practices for Slash Commands

### ✅ DO Use These Tools

1. **Glob** - Find files by pattern
   ```
   pattern: "src/**/*.py"
   ```

2. **Grep** - Search file contents
   ```
   pattern: "^def "
   path: "src/"
   type: "py"
   ```

3. **Read** - Read file contents
   ```
   file_path: "/absolute/path/to/file.py"
   ```

4. **Write** - Create/overwrite files
   ```
   file_path: "/absolute/path/to/output.md"
   content: "..."
   ```

5. **Bash** - ONLY for simple, non-piped commands
   ```bash
   # ✅ Simple commands are OK
   ls -la
   date +%Y%m%d
   wc -l file.txt
   ```

### ❌ DON'T Use Complex Bash

Avoid these patterns in slash commands:

```bash
# ❌ Piping
command1 | command2 | command3

# ❌ Command substitution
result=$(command)

# ❌ Complex variable expansion
${var:-default} | sed 's/pattern//'

# ❌ Subshells
(command1; command2)

# ❌ Process substitution
command <(other_command)
```

**Why?** Claude Code's bash environment has security restrictions that block these patterns.

---

## Other Common Issues

### Issue: No Files Found

**Symptoms**:
```
Files Analyzed: 0
```

**Causes**:
1. Directory path doesn't exist
2. File pattern doesn't match any files
3. Typo in arguments

**Solutions**:
```bash
# Verify directory exists
ls -la src/evidence_toolkit

# Check file pattern matches
ls src/evidence_toolkit/**/*.py

# Try absolute path
/detect-duplicates /full/path/to/directory
```

### Issue: Report Not Generated

**Symptoms**:
- Command completes but no report file

**Causes**:
1. Target directory doesn't exist
2. Permission issues writing files
3. Error during report generation

**Solutions**:
```bash
# Create directory if missing
mkdir -p docs/technical-debt

# Check permissions
ls -la docs/technical-debt

# Check for errors in command output
```

### Issue: Too Many False Positives

**Symptoms**:
- Report shows intentional duplication as problems

**Causes**:
- Threshold too low
- Boilerplate code flagged
- Framework patterns detected

**Solutions**:
```bash
# Increase min-lines threshold
/detect-duplicates src/evidence_toolkit 10

# Focus on specific directories
/detect-duplicates src/evidence_toolkit/core

# Manual review required
# Some duplication is intentional (e.g., Pydantic models)
```

---

## Getting Help

### Quick Checks

1. **Verify command syntax**:
   ```bash
   /detect-duplicates [directory] [min-lines] [pattern]
   ```

2. **Check tool is available**:
   - Type `/` and look for `detect-duplicates`

3. **View command definition**:
   ```bash
   cat .claude/commands/detect-duplicates.md
   ```

### If Still Having Issues

1. **Check the guide**: [code-duplication-agent-guide.md](./code-duplication-agent-guide.md)
2. **Review examples**: [GETTING_STARTED.md](./GETTING_STARTED.md)
3. **Examine existing agents**: `.claude/agents/rca-debugger.md`

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2025-10-09 | 2.0 | Rewritten to use Claude Code native tools (fixes permission issues) |
| 2025-10-09 | 1.0 | Initial version (had bash permission issues) |

---

## Technical Details

### Why Permission Errors Occur

Claude Code runs bash commands in a restricted environment for security:

1. **Sandboxed execution** - Limited shell features
2. **Process isolation** - Restricted piping and subshells
3. **Security model** - Prevents arbitrary code execution

### Tool Architecture

Claude Code provides dedicated tools that:
- Run with proper permissions
- Handle errors gracefully
- Provide structured output
- Integrate with the AI system

**Recommendation**: Always prefer dedicated tools over bash commands.

---

## Related Documentation

- [Slash Commands README](../../.claude/commands/README.md)
- [Code Duplication Guide](./code-duplication-agent-guide.md)
- [Getting Started](./GETTING_STARTED.md)

---

**Last Updated**: 2025-10-09
