---
description: Detect code duplication and write findings to docs/technical-debt/
argument-hint: [directory] [min-lines] [pattern]
---

# Code Duplication Detection

Analyze the codebase for duplicate code patterns and generate a comprehensive report.

## Parameters

- **Directory**: $1 (default: `src/evidence_toolkit`)
- **Min Lines**: $2 (minimum lines to qualify as duplication, default: 5)
- **Pattern**: $3 (file pattern, default: `*.py`)
- **Full Arguments**: $ARGUMENTS

## Analysis Workflow

### Step 1: Discovery Phase

**Your Task**: Use the **Glob** tool to find all files matching the pattern.

```
Target Directory: ${1:-src/evidence_toolkit}
File Pattern: ${3:-*.py}
Min Duplicate Lines: ${2:-5}
Timestamp: $(date +%Y%m%d_%H%M%S)
```

**Example Glob patterns**:
- Python files: `src/evidence_toolkit/**/*.py`
- TypeScript: `frontend/src/**/*.ts`
- All code: `src/**/*.{py,ts,js}`

**Output**: List all discovered files with their paths.

---

### Step 2: Pattern Analysis

Use the **Grep** tool to search for common duplication patterns:

#### 2a. Function Definitions

Search for function signatures across all files:

**Grep Parameters**:
- Pattern: `^def |^    def |^        def `
- Path: Target directory from Step 1
- Type: `py` (or file type from arguments)
- Output mode: `content`
- Line numbers: Yes (`-n`)

**Analysis**: Look for function names that appear multiple times. Functions with the same name in different files may indicate duplication.

#### 2b. Class Definitions

Search for class definitions:

**Grep Parameters**:
- Pattern: `^class `
- Path: Target directory
- Type: `py`
- Output mode: `content`
- Line numbers: Yes

**Analysis**: Similar class names or structures may indicate duplication.

#### 2c. Import Patterns

Search for import statements:

**Grep Parameters**:
- Pattern: `^import |^from `
- Path: Target directory
- Type: `py`
- Output mode: `content`

**Analysis**: Repeated import patterns across files may indicate opportunity for shared modules.

---

### Step 3: Deep File Analysis

For each file discovered in Step 1:

1. **Read the file completely** using the **Read** tool
2. **Analyze for duplication patterns**:
   - Similar function implementations
   - Repeated code blocks (>= min-lines threshold)
   - Copy-pasted logic
   - Redundant utility functions
   - Repeated validation/error-handling patterns
   - String/constant duplication

3. **Compare across files**:
   - Identify functions with identical/near-identical implementations
   - Find classes with similar structures
   - Check for duplicated business logic
   - Look for repeated patterns

4. **Document findings** with:
   - Exact file paths
   - Line numbers for each instance
   - Similarity assessment (percentage)
   - Number of duplicate lines
   - Severity classification (HIGH/MEDIUM/LOW)

---

### Step 4: Duplication Detection Strategy

Use these criteria to identify duplications:

#### High Priority (Severity: HIGH)
- **3+ instances** of identical/near-identical code
- **30+ lines** of duplicated code total
- **Core business logic** that's copy-pasted
- **Functions with 90%+ similarity**

Example patterns:
- Same function in multiple analyzers
- Identical error handling blocks
- Copy-pasted validation logic
- Repeated API call patterns

#### Medium Priority (Severity: MEDIUM)
- **2 instances** of similar code
- **10-30 lines** of duplicated code
- **Utility functions** that could be shared
- **Functions with 70-90% similarity**

Example patterns:
- Similar helper functions
- Common data transformations
- Repeated file operations
- Shared string processing

#### Low Priority (Severity: LOW)
- **Small code blocks** (5-10 lines)
- **Boilerplate code** (may be intentional)
- **Test fixtures** and mocks
- **Functions with 50-70% similarity**

Example patterns:
- Common imports
- Standard error messages
- Simple getters/setters
- Configuration patterns

---

### Step 5: Generate Comprehensive Report

**Use the Write tool** to create a report at:
`docs/technical-debt/code-duplication-report-<timestamp>.md`

**Report Structure** (copy this template):

```markdown
# Code Duplication Analysis Report

**Generated**: <ISO timestamp>
**Target Directory**: <directory from arguments>
**File Pattern**: <pattern from arguments>
**Files Analyzed**: <count from Step 1>
**Min Duplicate Lines**: <threshold from arguments>
**Analysis Duration**: <time taken>

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| **Duplicate Code Blocks Found** | <count> |
| **Total Duplicate Lines** | ~<count> lines |
| **Files with Duplication** | <count> of <total> files (<percentage>%) |
| **High Priority Items** | <count> |
| **Medium Priority Items** | <count> |
| **Low Priority Items** | <count> |
| **Most Duplicated Pattern** | <pattern-name> (<count> instances) |
| **Estimated Refactoring Effort** | ~<hours> hours |
| **Overall Priority Level** | HIGH / MEDIUM / LOW |

**Key Findings**:
- <3-5 bullet points of most important discoveries>

---

## 🔴 High Priority Duplications

### 1. [Pattern/Function Name]

**Severity**: HIGH
**Instances**: <count> locations
**Duplicate Lines**: ~<count> lines per instance
**Total Waste**: ~<count> lines
**Similarity**: <percentage>% identical code

**Locations**:
- [`file1.py:42-58`](../../src/path/to/file1.py#L42) (17 lines)
- [`file2.py:103-119`](../../src/path/to/file2.py#L103) (17 lines)
- [`file3.py:205-221`](../../src/path/to/file3.py#L205) (17 lines)

**Example Code**:
```python
# Representative sample of the duplicated code
def example_function(param):
    # Show the actual duplicated code here
    result = process(param)
    return result
```

**Root Cause**: [Why this duplication exists - e.g., "Copy-pasted from original implementation", "Common pattern not abstracted", etc.]

**Refactoring Recommendation**:
- **Action**: Extract to shared utility module
- **Target Location**: `src/evidence_toolkit/utils/common.py`
- **New Function Signature**: `descriptive_name(params: Type) -> ReturnType`
- **Migration Steps**:
  1. Create shared function in utils module
  2. Add unit tests for extracted function
  3. Replace instance in file1.py with import
  4. Replace instance in file2.py with import
  5. Replace instance in file3.py with import
  6. Remove old implementations
- **Estimated Effort**: <minutes> minutes
- **Impact**: Removes <count> lines of duplicate code
- **Risk Level**: LOW / MEDIUM / HIGH
- **Testing Required**: Unit tests, integration tests

**Example Refactoring**:
```python
# Before (in each file)
def local_function(param):
    # duplicated implementation
    pass

# After (in utils/common.py)
def shared_function(param: ParamType) -> ReturnType:
    """Extracted common functionality."""
    # implementation
    pass

# After (in each original file)
from evidence_toolkit.utils.common import shared_function

result = shared_function(param)
```

**Benefits**:
- Single source of truth for this logic
- Bug fixes apply to all <count> call sites
- Easier to test and maintain
- Reduces codebase by <count> lines

---

[Repeat structure for each HIGH priority duplication...]

---

## 🟡 Medium Priority Duplications

[Use same structure as HIGH priority, but for medium severity items...]

---

## 🟢 Low Priority Duplications

[Use same structure, but for low severity items - can be more concise...]

---

## 📋 Detailed Findings by Category

### Category 1: Function Duplication

**Total Instances**: <count>
**Files Affected**: <count>
**Total Duplicate Lines**: ~<count>

| Function Pattern | Instances | Lines Each | Total Lines | Similarity | Priority |
|-----------------|-----------|------------|-------------|------------|----------|
| pattern_name    | 3         | 15         | 45          | 95%        | HIGH     |
| other_pattern   | 2         | 10         | 20          | 80%        | MEDIUM   |
| minor_pattern   | 2         | 5          | 10          | 60%        | LOW      |

**Summary**: <Brief analysis of function duplication findings>

### Category 2: Class Duplication

**Total Instances**: <count>
**Files Affected**: <count>

[Similar table structure...]

### Category 3: Code Block Duplication

**Total Instances**: <count>
**Files Affected**: <count>

[Details of repeated code blocks that aren't full functions...]

### Category 4: String/Constant Duplication

**Total Instances**: <count>
**Files Affected**: <count>

**Common Repeated Strings**:
- `"error_message_text"` - Used in <count> files
- `"api_endpoint_url"` - Used in <count> files
- Magic number `42` - Used in <count> locations

**Recommendation**: Extract to shared constants module

---

## 🎯 Refactoring Roadmap

### Phase 1: Quick Wins (1-2 hours total)

#### 1.1 Extract `function_name` to shared utility
- **Files**: file1.py, file2.py, file3.py
- **Effort**: 30 minutes
- **Impact**: Removes 51 lines
- **Risk**: LOW
- **Owner**: [TBD]
- **Priority**: P0 (Immediate)

#### 1.2 Consolidate error handling pattern
- **Files**: analyzer1.py, analyzer2.py, processor.py
- **Effort**: 45 minutes
- **Impact**: Removes 80 lines
- **Risk**: LOW
- **Owner**: [TBD]
- **Priority**: P0 (Immediate)

[Continue with Phase 1 items...]

### Phase 2: Medium Effort (3-5 hours total)

[List medium effort refactorings...]

### Phase 3: Major Refactoring (1-2 days total)

[List major refactorings that require careful planning...]

---

## 📈 Metrics & Impact Analysis

### Code Volume Metrics

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| **Total Lines of Code** | <current> | <projected> | <count> lines (<percentage>%) |
| **Duplicate Lines** | <current> | 0 | <count> lines (100%) |
| **Files with Duplication** | <count> | 0 | <count> files |
| **Average File Size** | <lines> | <lines> | <lines> (<percentage>%) |

### Maintainability Metrics

- **Cyclomatic Complexity**: Expected reduction of <percentage>%
- **Code Churn**: <count> files will be modified
- **Test Coverage**: <percentage>% of duplications are currently tested
- **Bug Surface Area**: Centralized fixes will affect <count> call sites
- **Code Review Effort**: Reduced by <percentage>% (fewer lines to review)

### Technical Debt Metrics

- **Current Debt**: ~<hours> hours (time to understand duplicated code)
- **Refactoring Investment**: ~<hours> hours (time to fix)
- **Future Savings**: ~<hours> hours per year (reduced maintenance)
- **Net Debt Reduction**: ~<hours> hours
- **Return on Investment**: <percentage>% over 12 months

### Quality Metrics

- **Potential Bugs**: <count> locations where bugs could diverge
- **Single Source of Truth**: <count> patterns will be centralized
- **Consistency**: <count> inconsistent implementations unified
- **Documentation**: <count> functions will need single docstring

---

## ⚠️ Risk Assessment

### Low Risk Refactorings (Safe to implement immediately)

- ✅ Pure function extractions (no side effects)
- ✅ Utility consolidations (stateless operations)
- ✅ Constant definitions (simple values)
- ✅ Import statement reorganization

**Examples from this analysis**:
- [List specific low-risk items from findings]

### Medium Risk Refactorings (Require testing)

- ⚠️ Business logic consolidation (affects behavior)
- ⚠️ State management changes (affects data flow)
- ⚠️ Error handling changes (affects exception flow)
- ⚠️ API surface modifications (affects callers)

**Examples from this analysis**:
- [List specific medium-risk items]

### High Risk Refactorings (Require careful planning)

- 🚨 Core algorithm changes (fundamental behavior)
- 🚨 Cross-module dependencies (architectural impact)
- 🚨 Breaking changes (affects external code)
- 🚨 Performance-critical code (affects system performance)

**Examples from this analysis**:
- [List specific high-risk items]

---

## ✅ Next Steps & Action Items

### Immediate Actions (This Week)

1. **Review & Validate Findings**
   - [ ] Review this report with the team
   - [ ] Validate high-priority duplications
   - [ ] Confirm refactoring recommendations
   - [ ] Identify any false positives

2. **Create Tracking Issues**
   - [ ] Create GitHub issues for each Phase 1 refactoring
   - [ ] Link issues to this report for context
   - [ ] Assign effort estimates and owners
   - [ ] Add to sprint backlog

3. **Establish Baseline**
   - [ ] Document current metrics
   - [ ] Set up code quality dashboard
   - [ ] Define success criteria

### Short-Term Actions (Next 2 Weeks)

4. **Implement Phase 1 Refactorings**
   - [ ] Complete all "Quick Wins" items
   - [ ] Write tests for extracted functions
   - [ ] Run full test suite after each change
   - [ ] Code review all changes

5. **Measure Impact**
   - [ ] Re-run `/detect-duplicates` after Phase 1
   - [ ] Compare before/after metrics
   - [ ] Document lessons learned

### Medium-Term Actions (Next Month)

6. **Plan Phase 2 & 3**
   - [ ] Review Phase 2 items with architecture team
   - [ ] Create detailed implementation plans
   - [ ] Schedule refactoring sprints
   - [ ] Allocate resources

7. **Establish Prevention**
   - [ ] Add code review checklist item for duplication
   - [ ] Set up automated duplication detection
   - [ ] Create coding guidelines for common patterns
   - [ ] Schedule monthly duplication analysis

---

## 📚 Appendix

### A. Analysis Methodology

**Tools Used**:
- Claude Code Glob tool for file discovery
- Claude Code Grep tool for pattern matching
- Claude Code Read tool for file analysis
- Manual code review and comparison

**Detection Criteria**:
- Minimum <threshold> lines for duplication
- 50%+ code similarity for flagging
- Manual review for false positive filtering

**Limitations**:
- Focuses on exact/near-exact textual matches
- Semantic duplication may not be detected
- Intentional duplication (boilerplate) may be flagged
- Manual review recommended for all findings

### B. False Positives & Exclusions

**Intentional Duplication** (excluded from recommendations):
- Framework-required boilerplate
- Test fixtures and mocks (when justified)
- Generated code
- Third-party library patterns

**False Positives Found**:
- [List any patterns that look like duplication but are intentional]

### C. Project-Specific Context

**Evidence Toolkit Patterns**:
- Pydantic model definitions (intentional similarity)
- Chain of custody logging (standardized pattern)
- SHA256 hash operations (security requirement)
- Forensic timestamp patterns (legal compliance)

**Acceptable Duplication**:
- [List patterns that are acceptable in this codebase]

### D. Related Documentation

- [Code Quality Guidelines](../../CONTRIBUTING.md)
- [Architecture Documentation](../../V3_ARCHITECTURE.md)
- [Previous Duplication Report](./code-duplication-report-YYYYMMDD.md)
- [Refactoring Best Practices](../../docs/refactoring-guide.md)

### E. References

- Martin Fowler's Refactoring Catalog
- Clean Code principles (Robert C. Martin)
- DRY principle (Don't Repeat Yourself)
- Evidence Toolkit coding standards

---

## 🔍 Glossary

- **Duplication**: Code that appears in multiple locations with high similarity
- **Similarity**: Percentage of identical/near-identical code between instances
- **Refactoring**: Restructuring code without changing external behavior
- **Technical Debt**: Cost of maintaining duplicated/suboptimal code over time
- **Code Smell**: Indicator of potential code quality issues

---

**Report Generated By**: Claude Code `/detect-duplicates` command
**Analysis Date**: <timestamp>
**Analyst**: Claude Code Assistant
**Next Scheduled Review**: <30 days from analysis date>
**Report Version**: 1.0
**Contact**: [Your team contact information]

---

_This analysis is provided for code quality improvement purposes. All refactoring recommendations should be reviewed by the development team before implementation._
```

---

### Step 6: Update Summary File

**Use the Write tool** to update (or create if new):
`docs/technical-debt/duplication-summary.md`

```markdown
# Code Duplication Summary

**Last Updated**: <timestamp>
**Last Full Analysis**: <date>
**Analyzer**: Claude Code `/detect-duplicates`

---

## 🎯 Current Status Snapshot

| Metric | Value | Trend |
|--------|-------|-------|
| **Duplicate Code Blocks** | <count> | 🔴 / 🟢 / ↔️ |
| **Total Duplicate Lines** | ~<count> | 🔴 / 🟢 / ↔️ |
| **Files Affected** | <count> of <total> (<percentage>%) | 🔴 / 🟢 / ↔️ |
| **High Priority Items** | <count> | 🔴 / 🟢 / ↔️ |
| **Medium Priority Items** | <count> | 🔴 / 🟢 / ↔️ |
| **Low Priority Items** | <count> | 🔴 / 🟢 / ↔️ |
| **Estimated Refactoring Effort** | ~<hours> hours | 🔴 / 🟢 / ↔️ |

Legend: 🔴 Increasing | 🟢 Decreasing | ↔️ Stable

---

## 🔥 Top 5 Duplication Hot Spots

### 1. `function_name` - <count> instances

- **Priority**: HIGH
- **Duplicate Lines**: ~<count> lines total
- **Files**: file1.py, file2.py, file3.py
- **Effort to Fix**: <minutes> minutes
- **Impact**: Removes <count> lines
- **Status**: 🔴 Open / 🟡 In Progress / 🟢 Resolved
- [View Details](./code-duplication-report-<timestamp>.md#1-function-name)

### 2. `other_pattern` - <count> instances

[Same structure as #1...]

### 3-5. [Continue for top 5...]

---

## 📊 Trend Analysis

### Historical Data

| Date | Duplicate Lines | Change | Files Affected | High Priority | Status |
|------|----------------|--------|----------------|---------------|--------|
| <latest> | <count> | - | <count> | <count> | Current |
| <previous-1> | <count> | +/-X% | <count> | <count> | Baseline |
| <previous-2> | <count> | +/-X% | <count> | <count> | Archived |

### Interpretation

[Brief analysis of trends - is duplication increasing or decreasing? Why?]

**Key Observations**:
- <Observation about trend>
- <Impact of recent refactorings>
- <Concerns or wins>

---

## 📁 Historical Reports

### Latest Reports (Last 6 Months)

- **[<date> - Current Analysis](./code-duplication-report-<timestamp>.md)** - <count> duplications found
- [<date> - Previous Analysis](./code-duplication-report-<prev-timestamp>.md) - <count> duplications found
- [<date> - Older Analysis](./code-duplication-report-<older>.md) - <count> duplications found

### Archived Reports (>6 Months)

Moved to `archive/technical-debt/`:
- [<old-date>](./archive/code-duplication-report-<old>.md)

---

## 🎯 Active Refactoring Tasks

### In Progress

- [ ] **Extract `function_name` to shared utility** - [Issue #123](link)
  - Assigned to: [Name]
  - Target completion: [Date]
  - Status: 50% complete

### Planned (Next Sprint)

- [ ] **Consolidate error handling** - [Issue #124](link)
- [ ] **Extract common validators** - [Issue #125](link)

### Completed (Last 30 Days)

- [x] **Unified timestamp formatting** - [PR #120](link) - Merged 2025-10-01
  - Impact: Removed 35 lines of duplicate code
- [x] **Centralized logging patterns** - [PR #118](link) - Merged 2025-09-28
  - Impact: Removed 60 lines of duplicate code

---

## 🏆 Improvements Since Baseline

**Baseline Date**: <first-analysis-date>

| Metric | Baseline | Current | Improvement |
|--------|----------|---------|-------------|
| Duplicate Lines | <count> | <count> | -<count> lines (-<percentage>%) |
| Files Affected | <count> | <count> | -<count> files |
| High Priority Items | <count> | <count> | -<count> items |
| Technical Debt Hours | <hours> | <hours> | -<hours> hours |

**Total Refactoring Time Invested**: <hours> hours
**ROI**: <percentage>% (debt reduced vs. time invested)

---

## 📅 Schedule

### Next Analysis Run

**Scheduled Date**: <30 days from last analysis>
**Command**: `/detect-duplicates src/evidence_toolkit 5 "*.py"`
**Owner**: [Team member responsible]

### Regular Cadence

- **Monthly**: Full codebase analysis
- **Pre-Release**: Health check before major releases
- **Post-Feature**: After large feature additions
- **Quarterly**: Trend review and planning

---

## 🎓 Lessons Learned

### What's Working

- [Successful strategies for reducing duplication]
- [Effective refactoring patterns]
- [Prevention techniques that help]

### What's Not Working

- [Challenges encountered]
- [Patterns that keep reappearing]
- [Areas for process improvement]

### Action Items

- [Process improvements to implement]
- [Training or documentation needs]
- [Tool or automation opportunities]

---

## 🔗 Quick Links

- [Latest Full Report](./code-duplication-report-<timestamp>.md)
- [Code Quality Guidelines](../../CONTRIBUTING.md)
- [Architecture Documentation](../../V3_ARCHITECTURE.md)
- [Refactoring Tracking Board](link-to-board)
- [Team Slack Channel](link-to-slack)

---

**Maintained By**: [Team/Person responsible]
**Last Review**: <date>
**Next Review**: <30 days from last review>
```

---

## 🎯 Execution Summary

**What You Must Do**:

1. **Use Glob tool** to find all matching files
2. **Use Grep tool** (not bash grep) to search for patterns:
   - Function definitions
   - Class definitions
   - Import patterns
3. **Use Read tool** to read each file completely
4. **Analyze manually** by comparing code across files
5. **Use Write tool** to create the report with the template above
6. **Use Write tool** to update the summary file

**What You Must NOT Do**:

- ❌ **Never use bash grep/sed/awk** - Use Grep tool instead
- ❌ **Never modify source code** - Read-only analysis
- ❌ **Never guess without reading files**
- ❌ **Never skip file:line references**

---

## ✅ Success Criteria

- [ ] Report generated at `docs/technical-debt/code-duplication-report-<timestamp>.md`
- [ ] Summary updated at `docs/technical-debt/duplication-summary.md`
- [ ] All findings include clickable `[file:line](path#L123)` links
- [ ] Severity ranking applied: HIGH/MEDIUM/LOW
- [ ] Refactoring effort estimated
- [ ] No source files modified
- [ ] Actionable recommendations provided with specific steps

---

## 🔧 Tool Usage Examples

### Glob Tool
```
pattern: "src/evidence_toolkit/**/*.py"
# Returns: List of all .py files
```

### Grep Tool
```
pattern: "^def "
path: "src/evidence_toolkit"
type: "py"
output_mode: "content"
-n: true  # Show line numbers
```

### Read Tool
```
file_path: "/full/path/to/file.py"
# Returns: Complete file contents with line numbers
```

### Write Tool
```
file_path: "/full/path/to/docs/technical-debt/code-duplication-report-20251009_143022.md"
content: "<markdown report from template>"
```

---

**Note**: This command uses Claude Code's native tools (Glob, Grep, Read, Write) instead of bash commands to avoid permission issues. This is the recommended approach for all file operations in slash commands.
