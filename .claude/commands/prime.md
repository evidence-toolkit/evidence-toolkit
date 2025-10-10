---
description: Understand the Evidence Toolkit codebase through dynamic discovery. Use PROACTIVELY when starting a new session or after major changes.
allowed-tools: Read, Bash(find:*), Bash(ls:*), Bash(grep:*), Bash(uv run python:*), Bash(which:*), SlashCommand:/update-docs:*
---

# Prime

Understand the Evidence Toolkit codebase by dynamically discovering and reading key files, then reporting comprehensive understanding.

**Use this command when:**
- Starting a new session with Claude
- Onboarding after time away from the project
- Understanding the current state after major refactoring
- Discovering what version features are present (v3.0 vs v3.1+)

## Context

**Project Version:**
!`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null || echo "Not installed"`

**Core Documentation (auto-discovered):**
!`find . -maxdepth 1 -name "*.md" -type f | grep -E "(README|ARCHITECTURE|V3|CLAUDE|CONTRIBUTING)" | sort`

**Core Python Modules:**
!`find src/evidence_toolkit/core -name "*.py" -type f | sort`

**Analyzers:**
!`find src/evidence_toolkit/analyzers -name "*.py" -type f | sort`

**Pipeline Components:**
!`find src/evidence_toolkit/pipeline -name "*.py" -type f | sort`

**Domain Configurations:**
!`find src/evidence_toolkit/domains -name "*.py" -type f 2>/dev/null | sort`

**Configuration Files:**
!`ls -1 pyproject.toml .gitignore quick-start.sh 2>/dev/null`

**CLI Entry Point:**
!`ls -1 src/evidence_toolkit/cli.py 2>/dev/null`

**Module Statistics:**
- Core modules: !`find src/evidence_toolkit/core -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' '` files
- Analyzers: !`find src/evidence_toolkit/analyzers -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' '` files
- Pipeline stages: !`find src/evidence_toolkit/pipeline -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' '` files
- Domain configs: !`find src/evidence_toolkit/domains -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' '` files

**Data Storage:**
!`if [ -d data/storage ]; then echo "✅ Storage exists"; else echo "❌ No storage yet"; fi`

**CLI Installation:**
!`if which evidence-toolkit >/dev/null 2>&1; then echo "✅ Installed"; else echo "❌ Not installed"; fi`

---

## Your Task

### Step 1: Read Discovered Files

Read the files discovered in the **Context** section above, in this order:

1. **Documentation first** (from "Core Documentation" list)
   - Start with README.md for overview
   - Then CLAUDE.md for project conventions
   - Then V3_ARCHITECTURE.md or similar for design
   - Finally V3_COMPLETE.md or changelog for recent changes

2. **Core modules** (from "Core Python Modules" list)
   - models.py - ALL Pydantic model definitions
   - storage.py - Content-addressed storage system
   - Any other core/*.py files discovered

3. **Analyzers** (from "Analyzers" list)
   - All analyzer modules found

4. **Pipeline** (from "Pipeline Components" list)
   - All pipeline stage modules found

5. **Domain configs** (from "Domain Configurations" list, if any)
   - Legal domain configuration with AI prompts

6. **CLI and config** (from "CLI Entry Point" and "Configuration Files")
   - cli.py - Command-line interface
   - pyproject.toml - Package metadata
   - .gitignore - What's hidden from git
   - quick-start.sh - Quick workflow script

### Step 2: Report Understanding

Report your understanding in this format:

```
🧠 EVIDENCE TOOLKIT COMPREHENSION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTATION OVERVIEW
─────────────────────────
For each documentation file discovered, report:
  • <File Name> - <Purpose> - <1-2 Key Points>

🐍 PYTHON COMPONENTS
────────────────────
**Core Modules** (src/evidence_toolkit/core/):
  • models.py - <Model count> Pydantic models - <Key model categories>
  • storage.py - <Core functionality> - <Key classes>
  • [Other core modules discovered]

**Analyzers** (src/evidence_toolkit/analyzers/):
  • [Each analyzer] - <What it analyzes> - <AI integration if any>

**Pipeline** (src/evidence_toolkit/pipeline/):
  • [Each stage] - <Pipeline role> - <Key functionality>

**Domain Configs** (src/evidence_toolkit/domains/):
  • [If present] - <Configuration purpose> - <AI prompts/models>

**CLI** (src/evidence_toolkit/cli.py):
  • <Commands available> - <Entry points> - <User interaction>

📋 OVERALL UNDERSTANDING
─────────────────────────
1. **Project Purpose**
   What the Evidence Toolkit does for legal professionals

2. **Architecture Pattern**
   Version: v<X.Y.Z>
   Pattern: Clean architecture, single unified package
   Key: src/evidence_toolkit/ structure

3. **Model Consolidation**
   Total Pydantic models: <count>
   Location: core/models.py
   Validation: All outputs use Pydantic (100% type safety)

4. **Content-Addressed Storage**
   System: SHA256-based deduplication
   Location: data/storage/raw/ and data/storage/derived/
   Chain of custody: Immutable evidence tracking

5. **AI Integration**
   Models used: <OpenAI models discovered>
   Analyzers: <List AI-powered analyzers>
   Deterministic: temperature=0 for forensic integrity
   [If v3.1+] Legal patterns, power dynamics, entity resolution

6. **Working Flow**
   Input: data/cases/<case-id>/
   Pipeline stages: ingest → analyze → correlate → package
   Output: data/packages/<case-id>.zip
   CLI: evidence-toolkit process-case <case-id>

7. **Entry Points**
   CLI commands: <list from cli.py>
   Quick start: ./quick-start.sh
   Direct Python: from evidence_toolkit import ...

8. **Version-Specific Features**
   [If v3.0] Baseline with unified models
   [If v3.1+] AI enhancements:
     • Legal pattern detection (LegalPatternAnalysis)
     • Power dynamics scoring (deference_score)
     • Enhanced relationship analysis
   [If v3.2+] Advanced features:
     • AI entity resolution (EntityMatchResult, --ai-resolve)
     • Case type support (workplace/employment/contract via --case-type)
     • Chunked summaries (map-reduce for 50+ evidence pieces)
     • Video/audio ingestion (basic support)

9. **Current State**
   ✅ Working: <What's functional>
   ⚠️  Needs attention: <Any issues or gaps discovered>
   📊 Data present: <Evidence files, cases, packages counts>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ I understand the Evidence Toolkit v<X.Y.Z> structure and am ready to work on it.

Key capabilities I can now help with:
  • Processing evidence through the pipeline
  • Modifying/adding analyzers
  • Working with Pydantic models
  • Debugging chain of custody issues
  • Enhancing AI analysis prompts
  • [Version-specific capabilities]
```

### Step 3: Offer Documentation Update (Optional)

After completing the comprehension report, if the discovery identified:
- Recent changes to Python files (in the last 5 commits)
- Missing documentation for key modules
- Outdated documentation (older than source files)

Then offer:

```
📝 Documentation Update Available

I noticed [X] modules have changed recently but documentation may be outdated:
  • [List modules that changed]

Would you like me to run /update-docs recent to refresh the documentation?
```

If the user confirms, invoke: `/update-docs recent`

---

## Notes

**Performance**: This command reads ~10-20 files (varies by codebase state)
**Token Usage**: Moderate (~15-25k tokens depending on file sizes)
**Side Effects**: Read-only discovery (unless /update-docs is invoked)
**Dependencies**: Requires uv and Python environment

**Workflow Integration**:
- Start of session: `/prime` → understand codebase → optionally update docs
- After major refactor: `/prime` → see what changed → `/update-docs recent`

**Related Commands**:
- `/status` - Quick project health check (lighter weight, no file reading)
- `/create-docs` - Document specific modules (invoked by /update-docs)
- `/update-docs recent` - Document recent changes only (can be auto-suggested by /prime)
