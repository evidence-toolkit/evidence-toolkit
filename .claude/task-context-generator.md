# Task Context Generator

## Generate Current Development Context

**Usage**: `/generate-context [focus-area]`

**Purpose**: Create focused development context for current task, not general project documentation.

### Context Generation Commands

```bash
# Core architecture patterns we follow
echo "## Proven Patterns"
grep -A 15 -B 2 "responses\.parse" document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py

echo "## Pydantic Model Structure"
head -50 document-evidence-analyzer/src/document_analyzer/ai_models.py

echo "## Current Evidence Types"
ls -1 document-evidence-analyzer/src/document_analyzer/*.py | grep -E "(analyzer|models)"
ls -1 image-analysis/image_analysis/*.py | grep -E "(models|cli)"

echo "## Implementation Status"
find . -name "*email*" -type f 2>/dev/null | head -5
grep -l "EmailAnalysis\|email_analyzer" . -R --include="*.py" 2>/dev/null | head -3

echo "## Next Development Steps"
cat EMAIL_FORENSIC_ARCHITECTURE.md | grep -A 10 "Week 1\|Week 2\|Week 3"
```

### Context Injection Command

```bash
# Quick context reset command
echo "Current Task: $(cat CURRENT_TASK_CONTEXT.md | head -1)"
echo "Architecture: Following proven document/image analyzer patterns"
echo "Implementation: $(grep -c 'def.*analyze' document-evidence-analyzer/src/document_analyzer/word_cloud_analyzer.py) analysis methods in DocumentAnalyzer"
echo "Models: $(grep -c 'class.*Model' document-evidence-analyzer/src/document_analyzer/ai_models.py) Pydantic models defined"
echo "Status: Ready to implement EmailAnalyzer following same patterns"
```

### Session Startup Context

```bash
# AUDHD-friendly session restart
echo "=== DEVELOPMENT CONTEXT RESET ==="
echo "Task: Adding Email Analysis to Evidence Toolkit"
echo "Pattern: Copy proven DocumentAnalyzer architecture"
echo "Files: document-evidence-analyzer/src/document_analyzer/"
echo "Next: Create email_models.py + email_analyzer.py"
echo "Quality: Must match 4.6/5 forensic standard"
echo "==================================="
```