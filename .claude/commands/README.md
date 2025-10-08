# Evidence Toolkit Slash Commands

Custom slash commands for Claude Code to help navigate and understand the Evidence Toolkit.

## Available Commands

### `/prime`
**Purpose:** Understand the Evidence Toolkit codebase from scratch

**What it does:**
- Reads all core documentation files
- Examines key Python components
- Shows actual directory structure (including gitignored)
- Reports comprehensive understanding

**Use when:**
- Starting a new session with Claude
- Onboarding a new AI assistant
- Getting back into the project after time away

**Example:**
```
/prime
```

---

### `/status`
**Purpose:** Quick project status check

**What it does:**
- Shows evidence storage statistics
- Lists current cases
- Shows generated client packages
- Checks CLI installation
- Shows recent file activity

**Use when:**
- Checking what's currently in the project
- Verifying a pipeline run completed
- Quick health check

**Example:**
```
/status
```

---

## How Slash Commands Work

1. Type `/` in Claude Code to see available commands
2. Select a command (or type `/prime`, `/status`, etc.)
3. Claude reads the markdown file and follows the instructions
4. The `Execute` section runs bash commands
5. The `Report` section guides the AI's response format

## Creating New Commands

To add a new command:

1. Create a markdown file in `.claude/commands/`
2. Use this structure:
   ```markdown
   # Command Name

   Brief description

   ## Read
   - file1.md
   - file2.py

   ## Execute
   ```bash
   command to run
   ```

   ## Report
   How to format the response
   ```

3. The filename (without .md) becomes the command name

## Tips

- Keep commands focused on a single purpose
- Use bash commands that are fast and informative
- Guide the AI's response format in the `Report` section
- Commands are great for repetitive analysis tasks

## Evidence Toolkit Specific Notes

**Remember:** This project has gitignored directories (`evidence/`, `cases/`, `client_packages/`). Slash commands that show `ls -la` help reveal the full structure that git hides.

**The `/prime` command is essential** when starting work on this project because it explains the gitignore visibility issue upfront.
