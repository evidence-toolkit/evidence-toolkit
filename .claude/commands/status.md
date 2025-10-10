---
description: Quick project status - evidence, cases, packages, v3.1/v3.2/vx.x features
allowed-tools: Read, Grep, Bash(git log:*)
---

# Status

Quick project status check - see what evidence, cases, and packages currently exist, plus detection of v3.1/v3.2 AI features.

## Context

**Package Version:**
!`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null || echo "Not installed"`

**Package Structure:**
!`find src/evidence_toolkit -type d -maxdepth 1 2>/dev/null | sort`

**Evidence Storage:**
!`if [ -d data/storage/raw ]; then echo "✅ Storage exists"; else echo "❌ No storage"; fi`
- Raw files: !`find data/storage/raw -type f 2>/dev/null | wc -l | tr -d ' '`
- Derived analyses: !`find data/storage/derived -type d -name "sha256=*" 2>/dev/null | wc -l | tr -d ' '`

**Cases:**
!`if [ -d data/cases ]; then ls -1 data/cases/ 2>/dev/null | head -10; else echo "No cases"; fi`
- Case count: !`ls -1 data/cases/ 2>/dev/null | wc -l | tr -d ' '`

**Client Packages:**
!`if [ -d data/packages ]; then ls -1 data/packages/*.zip 2>/dev/null | head -10 | xargs -n1 basename 2>/dev/null || echo "No packages"; else echo "No packages directory"; fi`
- Package count: !`ls -1 data/packages/*.zip 2>/dev/null | wc -l | tr -d ' '`

**CLI Installation:**
!`if which evidence-toolkit >/dev/null 2>&1; then echo "✅ Installed at $(which evidence-toolkit)"; else echo "❌ Not installed"; fi`

**v3.1+ Features Detection:**
- LegalPatternAnalysis: !`grep -c 'LegalPatternAnalysis' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0` references
- Deference scoring: !`grep -c 'deference_score' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0` references
- Enhanced relationships: !`grep -c 'relationship.*Optional' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0` references

**v3.2+ Features Detection:**
- EntityMatchResult: !`grep -c 'EntityMatchResult' src/evidence_toolkit/core/models.py 2>/dev/null || echo 0` references
- Case type prompts: !`grep -c 'EXECUTIVE_SUMMARY_PROMPTS' src/evidence_toolkit/domains/legal_config.py 2>/dev/null || echo 0` references
- Chunked summaries: !`grep -c 'ChunkSummaryResponse' src/evidence_toolkit/pipeline/summary.py 2>/dev/null || echo 0` references

**Recent Activity:**
!`find . -type f \( -name "*.py" -o -name "*.md" \) -not -path "./.venv/*" -not -path "./.git/*" 2>/dev/null | xargs ls -lt 2>/dev/null | head -5 | awk '{print $9 " (" $6 " " $7 " " $8 ")"}'`

**Recent Git Activity:**
!`git log --oneline --decorate -5 2>/dev/null || echo "Not a git repository"`

---

## Your Task

Analyze the context above and provide a comprehensive status report:

### 1. Version & Features Summary
Report:
- Current version (from Package Version)
- Which feature tiers are present (v3.0 baseline, v3.1 AI, v3.2 advanced)
- Specific feature counts from detection

### 2. Data Status
Report:
- Evidence storage state (exists? how many files?)
- Active cases (list them if <5, otherwise show count)
- Generated packages (list them if <5, otherwise show count)

### 3. Installation Status
Report:
- Is CLI installed? If yes, where?
- If not installed, remind: `uv pip install -e .`

### 4. Feature Analysis
Based on the reference counts, report:
- **v3.1 AI Enhancements**: Present if LegalPatternAnalysis > 0
  - Legal pattern detection
  - Power dynamics analysis (deference scoring)
  - Enhanced relationship extraction
- **v3.2 Advanced Features**: Present if EntityMatchResult > 0
  - AI entity resolution (--ai-resolve flag)
  - Case type support (--case-type flag)
  - Chunked summaries for large cases

### 5. Recent Activity Analysis
Based on Recent Activity and Recent Git Activity:
- What files changed recently?
- What were the last few commits about?
- Any patterns suggesting active development areas?

### 6. Recommendations
Suggest any immediate actions:
- Missing installation? → Run `uv pip install -e .`
- No test data? → Run `/create-test-case`
- Recent code changes without git commits? → Consider committing
- Old documentation? → Consider `/update-docs recent`

### Report Format

```
📊 EVIDENCE TOOLKIT STATUS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 VERSION & FEATURES
─────────────────────
Version: v{X.Y.Z}
Feature Tier: [v3.0 Baseline / v3.1 AI-Enhanced / v3.2 Advanced]

v3.1 AI Enhancements: [PRESENT / NOT FOUND]
  • Legal pattern detection: {count} model references
  • Power dynamics scoring: {count} field references
  • Enhanced relationships: {count} field references

v3.2 Advanced Features: [PRESENT / NOT FOUND]
  • AI entity resolution: {count} model references
  • Case type support: {count} config references
  • Chunked summaries: {count} response references

💾 DATA STATUS
──────────────
Evidence Storage: [{✅ / ❌}]
  • Raw evidence files: {count}
  • Derived analyses: {count}

Active Cases: {count}
  {list cases or say "See context above for full list"}

Client Packages: {count}
  {list packages or say "See context above for full list"}

🔧 INSTALLATION
───────────────
CLI Status: [{✅ Installed / ❌ Not installed}]
  {if installed: show path, if not: show install command}

📝 RECENT ACTIVITY
──────────────────
Modified Files (last 5):
  {list from context}

Recent Commits:
  {show from git log}

Active Development: {infer what's being worked on}

💡 RECOMMENDATIONS
──────────────────
{bullet list of suggested actions based on analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Notes

**Purpose**: Quick health check of the Evidence Toolkit project
**Performance**: Lightweight - all data pre-executed via `!` prefix
**Side Effects**: Read-only (no modifications)

**When to use:**
- Start of session (lighter alternative to `/prime`)
- Quick check before running pipeline
- Verify installation and features
- Check what evidence/cases exist

**Related Commands**:
- `/prime` - Comprehensive codebase discovery (heavier, reads all files)
- `/create-test-case` - Generate test data if none exists
- `/update-docs recent` - If recent code changes detected
