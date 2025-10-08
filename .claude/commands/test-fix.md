---
allowed-tools: Bash(uv run pytest:*), Bash(uv run python:*), Edit, Read, Grep
argument-hint: [--full for full test suite]
description: Run tests and automatically fix failures
---

## Context

**Test Suite Structure:**
```
tests/
├── test_critical.py    # Core functionality tests (FAST)
├── test_models.py      # Pydantic model validation
├── test_pipeline.py    # End-to-end pipeline tests
└── conftest.py         # Pytest fixtures
```

**Project Info:**
- Using `uv` for package management
- Python 3.12+
- Pydantic v2 for all models

---

## Your Task

Run the test suite and fix any failures automatically.

### Test Execution Strategy

**Default (Fast):**
```bash
uv run pytest tests/test_critical.py -v
```

**Full Suite (if --full in $ARGUMENTS):**
```bash
uv run pytest tests/ -v
```

### Workflow

1. **Run Tests**
   - Execute appropriate test suite based on arguments
   - Capture full output including tracebacks
   - Show clear PASS/FAIL summary

2. **If Tests Pass**
   - ✅ Report success
   - Show coverage summary if available
   - Done!

3. **If Tests Fail**
   - 🔍 Analyze each failure:
     - Read the failing test file
     - Understand what the test expects
     - Identify the root cause (logic error, API change, validation issue, etc.)

   - 🔧 Fix the issues:
     - **Code bugs**: Edit the source files to fix logic errors
     - **Test bugs**: Edit test files if expectations are wrong
     - **API changes**: Update code to match new APIs
     - **Validation errors**: Fix Pydantic models or validation logic

   - 🔄 Re-run tests to verify fixes

   - 📊 Report results:
     - What was broken
     - What you fixed
     - Whether fixes resolved all failures

### Special Cases

**Import Errors:**
- Check if packages are installed: `uv pip list`
- Suggest installation if missing

**Pydantic Validation Errors:**
- Common in this project - check field types, Optional vs required
- Ensure all models use Pydantic v2 syntax

**File Not Found Errors:**
- Check if test fixtures/sample files exist
- May need to run from correct directory

**OpenAI API Errors:**
- These are OK to skip (test will be marked as skip/xfail)
- Don't try to "fix" missing API keys in tests

### Output Format

```
🧪 Running Tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Test output here]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Results: X passed, Y failed, Z skipped

[If failures:]
🔧 Fixing failures...

Failure 1: test_foo
  Issue: Expected str, got None
  Fix: Added null check in src/evidence_toolkit/core/models.py:123

[After fixes:]
🔄 Re-running tests...
✅ All tests now passing!
```

### Guidelines

- **Don't over-fix**: Only fix actual bugs, not test design
- **Preserve forensic integrity**: Don't change validation logic without understanding impact
- **Run incrementally**: Fix one issue at a time if failures are complex
- **Ask for help**: If fix is ambiguous, explain the issue and ask which approach to take

---

**Expected Outcome:**
Either all tests pass, or you've fixed what you can and reported remaining issues clearly.
