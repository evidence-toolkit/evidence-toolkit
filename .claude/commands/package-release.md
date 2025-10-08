---
allowed-tools: Read, Edit, Write, Bash(git tag:*), Bash(git log:*), Bash(git describe:*), Bash(uv build:*), Bash(uv run python:*)
argument-hint: [patch|minor|major]
description: Prepare package release with version bump and changelog
---

## Context

**Current Version:**
!`grep '^version = ' pyproject.toml | cut -d'"' -f2`

**Current Git Tags:**
!`git tag -l --sort=-version:refname | head -5`

**Commits Since Last Release:**
!`git log $(git describe --tags --abbrev=0 2>/dev/null || echo '--all')..HEAD --oneline`

**Package Status:**
!`git status --short`

---

## Your Task

Prepare a release of the Evidence Toolkit package.

### Release Process

#### 1. Determine Version Bump

**Semantic Versioning (MAJOR.MINOR.PATCH):**
- **PATCH** (3.0.0 → 3.0.1): Bug fixes, small improvements, docs
- **MINOR** (3.0.0 → 3.1.0): New features, non-breaking changes
- **MAJOR** (3.0.0 → 4.0.0): Breaking changes, major refactors

**Logic:**
- If $ARGUMENTS contains "major", "minor", or "patch", use that
- Otherwise, analyze commits since last tag:
  - "feat:", "refactor:" → MINOR bump
  - "fix:", "docs:", "chore:" → PATCH bump
  - "BREAKING" in commit → MAJOR bump (ask for confirmation!)
- Ask for confirmation before proceeding

#### 2. Update Version in pyproject.toml

Edit the version line:
```toml
[project]
version = "X.Y.Z"  # ← Update this
```

#### 3. Generate/Update CHANGELOG.md

**If CHANGELOG.md doesn't exist, create it:**

```markdown
# Changelog

All notable changes to Evidence Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [X.Y.Z] - YYYY-MM-DD

### Added
- New features from commits with "feat:"

### Fixed
- Bug fixes from commits with "fix:"

### Changed
- Changes from commits with "refactor:", "chore:"

### Documentation
- Docs changes from commits with "docs:"

## [Previous Versions]
...
```

**If CHANGELOG.md exists, prepend new section:**
- Add new version section at the top
- Group commits by type (Added/Fixed/Changed/Documentation)
- Extract meaningful info from commit messages
- Keep existing changelog content below

#### 4. Create Git Tag

```bash
git tag -a "vX.Y.Z" -m "Release vX.Y.Z

[Brief summary of key changes]

🤖 Generated with Claude Code"
```

#### 5. Validate Package Build

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
uv build

# Show what was built
ls -lh dist/
```

#### 6. Final Checklist

Present this checklist to the user:

```
✅ Release vX.Y.Z Prepared
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Version: X.Y.Z
📅 Date: YYYY-MM-DD

✅ Completed:
 ✓ Version bumped in pyproject.toml
 ✓ CHANGELOG.md updated
 ✓ Git tag created (vX.Y.Z)
 ✓ Package builds successfully

📋 Next Steps (Manual):
 1. Review CHANGELOG.md and make any edits
 2. Commit changes:
    git add pyproject.toml CHANGELOG.md
    git commit -m "chore: Release vX.Y.Z"
 3. Push commits and tags:
    git push origin main
    git push origin vX.Y.Z
 4. Create GitHub Release:
    gh release create vX.Y.Z ./dist/* --title "Release vX.Y.Z" --notes-file CHANGELOG.md
 5. (Optional) Publish to PyPI:
    uv publish

🎉 Release prepared! Review and follow the steps above when ready.
```

### Edge Cases

**Uncommitted Changes:**
- If `git status` shows uncommitted changes, warn:
  > ⚠️  You have uncommitted changes. Commit or stash before releasing.
- Offer to create commit first

**No Commits Since Last Tag:**
- If no new commits, ask:
  > ℹ️  No new commits since last release. Are you sure you want to bump version?

**Tag Already Exists:**
- If tag vX.Y.Z already exists:
  > ❌ Tag vX.Y.Z already exists. Did you mean to use a different version?

**Build Failures:**
- If `uv build` fails, show error and abort release prep
- Common issue: Missing dependencies in pyproject.toml

### Safety Checks

**Before making changes:**
1. Ensure we're on main/master branch (or ask to confirm if not)
2. Ensure repo is clean (or ask to commit first)
3. Confirm version bump is correct

**Do NOT:**
- Push tags automatically (user might want to review first)
- Publish to PyPI automatically (requires credentials)
- Delete or modify existing tags

### Output Format

```
🚀 Preparing Release: Evidence Toolkit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Current version: 3.0.0
📈 Detected changes:
   - 5 commits with feat:
   - 3 commits with fix:
   - 2 commits with docs:

💡 Recommended: MINOR bump → 3.1.0
   Proceed with 3.1.0? [Or specify major/minor/patch]

[User confirms]

✏️  Updating pyproject.toml...
   3.0.0 → 3.1.0 ✓

📝 Generating CHANGELOG.md...
   Added section for 3.1.0 ✓
   Categorized 10 commits ✓

🏷️  Creating git tag v3.1.0...
   Tag created ✓

📦 Validating package build...
   Building... ✓
   Created: dist/evidence_toolkit-3.1.0.tar.gz (123 KB)
   Created: dist/evidence_toolkit-3.1.0-py3-none-any.whl (98 KB)

✅ [Show final checklist above]
```

---

**Expected Outcome:**
A release-ready package with version bump, changelog, git tag, and validated build - but NOT yet pushed (giving you control over the final release timing).
