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
- **Current working directory**: Focus analysis on this project
- **Recent changes**: Consider git history for potential causes
- **Test failures**: If analyzing test failures, include test output and logs
- **Error traces**: If analyzing errors, capture full stack traces

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