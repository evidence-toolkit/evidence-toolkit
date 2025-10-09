# Getting Started with Code Duplication Detection

Quick start guide for using the `/detect-duplicates` slash command.

---

## TL;DR

```bash
# Run the command
/detect-duplicates

# View the report
cat docs/technical-debt/code-duplication-report-*.md
```

That's it! The command will analyze your codebase and generate a comprehensive report.

---

## What You Just Got

I've created a complete code duplication detection system for you:

### 📁 Files Created

1. **[.claude/commands/detect-duplicates.md](.claude/commands/detect-duplicates.md)**
   - The working slash command you can use immediately
   - Analyzes code, detects duplicates, writes reports
   - Read-only (never modifies your code)

2. **[code-duplication-agent-guide.md](./code-duplication-agent-guide.md)**
   - Comprehensive guide (4,000+ words)
   - Best practices for building Claude Code agents
   - Decision framework: slash command vs agent
   - Example implementations (simple and advanced)
   - Testing and validation guidelines

3. **[docs/technical-debt/README.md](./README.md)**
   - Documentation for this directory
   - Workflow guidance
   - Metrics tracking
   - Report retention policy

4. **[.claude/commands/README.md](.claude/commands/README.md)**
   - Updated with `/detect-duplicates` documentation

---

## Quick Start

### 1. Run Analysis

```bash
# Analyze default directory (src/evidence_toolkit)
/detect-duplicates

# Analyze specific directory
/detect-duplicates src/evidence_toolkit/analyzers

# Custom threshold (10 lines minimum)
/detect-duplicates src/evidence_toolkit 10

# Custom file pattern (TypeScript files)
/detect-duplicates frontend/src 5 "*.ts"
```

### 2. View Report

```bash
# View latest report
ls -lt docs/technical-debt/code-duplication-report-*.md | head -1

# Read the report
cat docs/technical-debt/code-duplication-report-20251009_143022.md

# View summary
cat docs/technical-debt/duplication-summary.md
```

### 3. Take Action

1. Review **HIGH priority** duplications first
2. Create tickets for approved refactorings
3. Implement changes gradually
4. Re-run analysis to measure improvement

---

## What the Command Does

### Analysis Workflow

1. **Discovery** - Finds all matching files
2. **Pattern Analysis** - Searches for common duplication patterns
3. **Deep Analysis** - Reads files and compares code
4. **Report Generation** - Creates comprehensive markdown report
5. **Summary Update** - Updates the summary file

### Report Contents

- **Executive Summary** - Metrics and overview
- **High Priority Duplications** - Most critical items first
- **Detailed Findings** - Specific file:line references
- **Refactoring Roadmap** - Phased implementation plan
- **Metrics & Impact** - Quantified technical debt

### Example Report Output

```markdown
## 🔴 High Priority Duplications

### 1. calculate_total Function

**Severity**: HIGH
**Instances**: 3
**Duplicate Lines**: ~51 lines total

**Locations**:
- `analyzer1.py:42-58` (17 lines)
- `analyzer2.py:103-119` (17 lines)
- `processor.py:205-221` (17 lines)

**Refactoring Recommendation**:
- Extract to `src/utils/calculations.py`
- Function: `calculate_total(items) -> float`
- Effort: 30 minutes
- Impact: Removes 51 lines of duplicate code
```

---

## Best Practices

### When to Run

- **Monthly** - Regular scheduled analysis
- **Before releases** - Pre-release health check
- **After features** - Check for new duplication
- **During refactoring** - Measure improvements

### How to Use Reports

1. **Triage** - Review executive summary
2. **Prioritize** - Focus on HIGH items
3. **Estimate** - Use effort estimates for planning
4. **Track** - Monitor trends over time
5. **Celebrate** - Measure improvements

### Report Retention

- Keep latest report
- Keep one per month for trends
- Archive reports >6 months old

---

## Advanced Usage

### Custom Thresholds

```bash
# Higher threshold (10+ lines)
/detect-duplicates src/ 10

# Lower threshold (3+ lines, more sensitive)
/detect-duplicates src/ 3
```

### Specific File Types

```bash
# Python files
/detect-duplicates src/ 5 "*.py"

# TypeScript/JavaScript
/detect-duplicates frontend/ 5 "*.{ts,tsx,js,jsx}"

# All text files
/detect-duplicates docs/ 3 "*.md"
```

### Multiple Directories

Run analysis on multiple directories:

```bash
/detect-duplicates src/evidence_toolkit/core
/detect-duplicates src/evidence_toolkit/analyzers
/detect-duplicates src/evidence_toolkit/pipeline
```

Compare reports to see where duplication is concentrated.

---

## Understanding the Reports

### Severity Levels

- **HIGH** - Critical duplication, refactor immediately
  - 3+ instances of same code
  - 30+ lines of duplicated code
  - Core business logic

- **MEDIUM** - Important duplication, plan refactoring
  - 2 instances of same code
  - 10-30 lines of duplicated code
  - Utility functions

- **LOW** - Minor duplication, nice-to-have
  - Small code blocks
  - Boilerplate code
  - Test fixtures

### Metrics Explained

| Metric | Meaning |
|--------|---------|
| **Duplicate Code Blocks** | Number of distinct duplication patterns |
| **Total Duplicate Lines** | Estimated lines of duplicated code |
| **Files Affected** | Files containing duplications |
| **Refactoring Effort** | Estimated hours to resolve |
| **Impact** | Lines of code that will be removed |

---

## Next Steps

### 1. Read the Guide

For deep understanding of how to build agents:
- [Code Duplication Agent Guide](./code-duplication-agent-guide.md)

### 2. Run Your First Analysis

```bash
/detect-duplicates
```

### 3. Review the Report

Focus on HIGH priority items first.

### 4. Plan Refactoring

Create tickets for approved refactorings.

### 5. Measure Improvement

Re-run analysis after refactoring to track progress.

---

## Troubleshooting

### No Files Found

**Problem**: Command reports 0 files found

**Solution**:
- Check directory path exists
- Verify file pattern matches files
- Try absolute path: `/full/path/to/directory`

### Report Not Generated

**Problem**: Command runs but no report appears

**Solution**:
- Check `docs/technical-debt/` exists
- Create directory: `mkdir -p docs/technical-debt`
- Check file permissions

### Too Many False Positives

**Problem**: Report shows intentional duplication

**Solution**:
- Increase min-lines threshold
- Focus on specific directories
- Manual review and filtering

---

## Examples for Evidence Toolkit

### Analyze Core Modules

```bash
/detect-duplicates src/evidence_toolkit/core 5 "*.py"
```

### Analyze Analyzers

```bash
/detect-duplicates src/evidence_toolkit/analyzers 5 "*.py"
```

### Full Codebase Analysis

```bash
/detect-duplicates src/evidence_toolkit 5 "*.py"
```

### High-Threshold Analysis

```bash
/detect-duplicates src/evidence_toolkit 10 "*.py"
```

---

## Key Takeaways

✅ **Start simple** - Use the slash command, not an agent
✅ **Read-only** - Never modifies your code
✅ **Comprehensive** - Detailed reports with specific recommendations
✅ **Actionable** - Includes effort estimates and refactoring guidance
✅ **Trackable** - Timestamped reports for trend analysis
✅ **Safe** - No false refactorings, manual review recommended

---

## References

- [Code Duplication Agent Guide](./code-duplication-agent-guide.md) - Complete guide
- [Technical Debt README](./README.md) - Directory documentation
- [Slash Commands README](../../.claude/commands/README.md) - All commands
- [Building Effective Agents](https://anthropic.com/research/building-effective-agents) - Anthropic guide

---

**Ready to start?** Run your first analysis:

```bash
/detect-duplicates
```

**Questions?** Check the [guide](./code-duplication-agent-guide.md) or [README](./README.md).
