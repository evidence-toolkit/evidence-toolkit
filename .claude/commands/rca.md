---
description: Enhanced root-cause analysis with argument parsing for bugs, test failures, and error messages
argument-hint: [error-message|test-name|file-path] [additional-context]
---

# Enhanced Root Cause Analysis

## Input Analysis
- **Primary target**: $1 (error message, test name, or file path)
- **Additional context**: $2 (optional: related files, recent changes, etc.)
- **Full arguments**: $ARGUMENTS

## Analysis Context

**Recent Git Commits (last 10):**
!`git log --oneline --decorate -10 2>/dev/null || echo "Not a git repository"`

**Recent File Changes:**
!`git diff --name-only HEAD~5..HEAD 2>/dev/null | head -10 || echo "No recent changes"`

**Current Branch:**
!`git branch --show-current 2>/dev/null || echo "Unknown"`

**Project Version:**
!`uv run python -c "import evidence_toolkit; print(evidence_toolkit.__version__)" 2>/dev/null || echo "Not installed"`

**Analysis Guidelines:**
- Focus analysis on this Evidence Toolkit project (v3.3)
- Consider recent git commits (shown above) as potential causes
- For test failures: examine test output and related test files
- For errors: capture full stack traces with line numbers
- For performance issues: check for recent algorithm changes

## Your Task
Using the **rca-debugger** subagent, perform comprehensive root-cause analysis of: **$ARGUMENTS**

The analysis should:
1. **Problem Statement**: Clear definition of the issue
2. **Evidence Gathering**: Relevant logs, stack traces, recent changes
3. **Hypothesis Formation**: Ranked list of potential root causes
4. **Impact Assessment**: Severity and scope of the issue
5. **Reproduction Steps**: Minimal steps to reproduce the problem
6. **Fix Recommendations**: Specific, actionable solutions
7. **Prevention Strategy**: How to avoid similar issues

**IMPORTANT**: This is analysis-only. Do not implement any changes.