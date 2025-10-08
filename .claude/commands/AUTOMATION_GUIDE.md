# Evidence Toolkit Automation Commands

**Stop doing boring stuff manually!** These slash commands automate the tedious parts of development.

---

## 🎯 Quick Reference

| Command | What It Does | Example |
|---------|-------------|---------|
| `/commit` | Smart git commits | `/commit` or `/commit fix parser bug` |
| `/test-fix` | Run tests, auto-fix failures | `/test-fix` or `/test-fix --full` |
| `/update-docs` | Generate documentation | `/update-docs recent` |
| `/package-release` | Version bump + changelog | `/package-release minor` |

---

## 📘 Command Details

### `/commit` - Smart Git Commits

**What it does:**
- Reads your staged/unstaged changes
- Analyzes recent commit style
- Generates meaningful commit message following project conventions
- Creates commit with Claude Code attribution

**Usage:**
```bash
# Auto-generate commit message from changes
/commit

# Use custom message
/commit Fix validation bug in storage module
```

**Commit Format:**
```
<type>: <subject>

<optional body>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

**Safety:**
- Won't commit sensitive files (.env, credentials, etc.)
- Warns if suspicious files are staged
- Shows what will be committed before doing it

---

### `/test-fix` - Automated Testing

**What it does:**
- Runs pytest test suite
- Analyzes failures automatically
- Fixes bugs, validation errors, import issues
- Re-runs tests to verify fixes

**Usage:**
```bash
# Run critical tests (fast)
/test-fix

# Run full test suite
/test-fix --full
```

**What it fixes:**
- ✅ Logic errors in source code
- ✅ Pydantic validation issues
- ✅ Import/dependency problems
- ✅ Test expectations (when wrong)
- ❌ Missing API keys (will skip gracefully)

**Output:**
```
🧪 Running Tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Test results]
📊 Results: 45 passed, 2 failed

🔧 Fixing failures...
✅ All tests now passing!
```

---

### `/update-docs` - Documentation Generator

**What it does:**
- Analyzes Python source code
- Generates comprehensive documentation
- Follows Evidence Toolkit doc standards
- Saves to appropriate docs/ subdirectories

**Usage:**
```bash
# Document a specific module
/update-docs src/evidence_toolkit/core/storage.py
/update-docs analyzers

# Document recently changed files (last 5 commits)
/update-docs recent

# Regenerate ALL documentation (expensive!)
/update-docs all
```

**Generated Sections:**
- Overview & purpose
- Usage examples (basic + advanced)
- API reference (parameters, returns, exceptions)
- Architecture & data flow
- AI integration (prompts, models, costs)
- Testing & dependencies
- Real-world examples

**Where docs are saved:**
```
docs/
├── api/           # Model/API reference
├── module-docs/   # Core module docs
├── pipeline/      # Pipeline stage docs
└── *.md           # Top-level docs
```

---

### `/package-release` - Release Automation

**What it does:**
- Analyzes commits since last release
- Suggests version bump (major/minor/patch)
- Updates version in pyproject.toml
- Generates/updates CHANGELOG.md from git history
- Creates git tag
- Validates package builds

**Usage:**
```bash
# Auto-detect version bump from commits
/package-release

# Specify bump type
/package-release patch   # 3.0.0 → 3.0.1
/package-release minor   # 3.0.0 → 3.1.0
/package-release major   # 3.0.0 → 4.0.0
```

**Semantic Versioning:**
- **PATCH**: Bug fixes, docs, small changes
- **MINOR**: New features, non-breaking changes
- **MAJOR**: Breaking changes, major refactors

**What it does NOT do:**
- ❌ Push tags/commits (you control timing)
- ❌ Publish to PyPI (requires credentials)
- ❌ Create GitHub releases (shows you the command)

**Output:**
```
✅ Release v3.1.0 Prepared

📋 Next Steps (Manual):
 1. Review CHANGELOG.md
 2. Commit: git commit -m "chore: Release v3.1.0"
 3. Push: git push origin main && git push origin v3.1.0
 4. Create GitHub release
 5. (Optional) Publish to PyPI
```

---

## 💡 Workflow Examples

### Daily Development Flow
```bash
# Make changes...
# Run tests
/test-fix

# Commit when tests pass
/commit

# Update docs for what you changed
/update-docs recent
```

### Pre-Release Flow
```bash
# Ensure tests pass
/test-fix --full

# Update all documentation
/update-docs all

# Prepare release
/package-release minor

# Review CHANGELOG.md, then push
```

### Quick Fix Flow
```bash
# Fix a bug
# Test it
/test-fix

# Commit it
/commit fix: Handle null values in parser

# Done!
```

---

## 🧠 ADHD-Friendly Tips

**These commands are designed to eliminate decision paralysis:**

1. **Don't overthink commits** - Just run `/commit` and let it figure out the message
2. **Don't manually debug tests** - `/test-fix` handles the tedious iteration
3. **Don't procrastinate docs** - `/update-docs recent` makes it painless
4. **Don't dread releases** - `/package-release` automates the tedious parts

**The boring stuff is now ONE COMMAND.**

---

## 🔧 Troubleshooting

**Command not found?**
- Restart Claude Code to reload commands
- Check `.claude/commands/{command}.md` exists

**Command fails?**
- Check the error message
- Most commands show clear "what went wrong" output
- You can always run underlying commands manually

**Want to customize?**
- Edit `.claude/commands/{command}.md`
- Change prompts, add/remove tools, adjust behavior
- Commands are just markdown files!

---

## 📚 Related

- **[README.md](../../.claude/commands/README.md)** - All slash commands
- **[CLAUDE.md](../../CLAUDE.md)** - Project guide for Claude
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)** - Contribution guidelines

---

**Built with Claude Code** - Because nobody should have to manually write changelogs in 2025.
