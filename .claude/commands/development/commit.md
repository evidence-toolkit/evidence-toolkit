---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(git log:*)
argument-hint: [optional custom message]
description: Create a smart git commit following project conventions
---

## Context

**Current Status:**
!`git status`

**Staged & Unstaged Changes:**
!`git diff HEAD`

**Recent Commit Style (for reference):**
!`git log --oneline -10`

**Current Branch:**
!`git branch --show-current`

---

## Your Task

Create a git commit following Evidence Toolkit conventions:

### Commit Message Format

Use this exact format:
```
<type>: <subject>

<optional body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring without behavior change
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Instructions

1. **Analyze ALL changes** (staged + unstaged) shown in the git diff above
2. **Determine the appropriate commit type** based on what changed
3. **Craft a concise subject line** (50 chars max) that describes WHY, not WHAT
4. **Stage any untracked/modified files** that should be committed (skip .env, credentials, etc.)
5. **Create the commit** using heredoc format for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
<type>: <subject>

<optional body if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

6. **Verify success** with `git status`

### Special Handling

- **DO NOT commit**: `.env`, `credentials.json`, `*.key`, temporary files
- **Warn me** if sensitive files are staged
- **Use meaningful subjects**: Focus on the PURPOSE of changes, not implementation details
- **Keep it atomic**: If changes are unrelated, ask if I want separate commits

### Custom Message Handling

If I provided arguments ($ARGUMENTS), use that as the commit subject instead of auto-generating one.

---

**Expected Output:**
- Show what files were staged
- Show the commit message you created
- Confirm commit was successful
