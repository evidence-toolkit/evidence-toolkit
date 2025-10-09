# Building a Code Duplication Detection Slash Command/Agent for Claude Code

**Created**: 2025-10-09
**Purpose**: Guide for building a Claude Code slash command or agent to detect and report code duplication

---

## Table of Contents

1. [Decision Framework: Slash Command vs Agent](#decision-framework)
2. [Recommended Approach: Slash Command](#recommended-approach)
3. [Implementation Examples](#implementation-examples)
4. [Best Practices](#best-practices)
5. [Testing and Validation](#testing-and-validation)

---

## Decision Framework: Slash Command vs Agent

### When to Use Slash Commands

✅ **Use a Slash Command when:**
- Fixed, predictable workflow
- No iterative decision-making required
- Simple task execution
- Read-only analysis
- Fast, templated responses

### When to Use Agents

✅ **Use an Agent when:**
- Dynamic, unpredictable workflow
- Requires iterative loops and decisions
- Multiple tool interactions
- Needs context-building across steps
- Complex problem-solving

### Code Duplication Detection: Slash Command ✅

**Rationale:**
- **Fixed workflow**: Search → Analyze → Report
- **Read-only**: No code modification
- **Predictable**: Same steps every time
- **Fast**: No iterative debugging loops

**Decision**: Start with a slash command. Upgrade to an agent only if you need:
- Dynamic refactoring suggestions
- Iterative code similarity analysis
- Multi-round investigation

---

## Recommended Approach: Slash Command

### File Structure

```
.claude/
├── commands/
│   ├── detect-duplicates.md       # Slash command definition
│   └── README.md                   # Command documentation
└── agents/                         # (Optional: Only if needed later)
    └── duplication-analyzer.md
```

### Output Structure

```
docs/
└── technical-debt/
    ├── code-duplication-report-YYYYMMDD.md   # Timestamped reports
    └── duplication-summary.md                 # Latest findings
```

---

## Implementation Examples

### Example 1: Simple Slash Command (Recommended)

**File**: `.claude/commands/detect-duplicates.md`

```markdown
---
description: Detect code duplication and report findings to docs/technical-debt/
argument-hint: [directory-path] [min-lines] [optional-pattern]
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*)
---

# Code Duplication Detection

Systematically detect and report code duplication across the codebase.

## Input Parameters

- **Directory**: $1 (default: src/)
- **Min Lines**: $2 (default: 5 lines to qualify as duplication)
- **Pattern**: $3 (optional: file pattern like "*.py" or "*.ts")

## Workflow

### Step 1: Discovery

Find all relevant code files:

```bash
# Discover Python files (or pattern from $3)
PATTERN="${3:-*.py}"
TARGET_DIR="${1:-src/}"

echo "=== CODE DUPLICATION ANALYSIS ==="
echo "Target: $TARGET_DIR"
echo "Pattern: $PATTERN"
echo "Min lines: ${2:-5}"
echo ""

find "$TARGET_DIR" -name "$PATTERN" -type f | sort
```

### Step 2: Pattern Analysis

For each file discovered, search for common duplication patterns:

1. **Function/Method Duplication**
   - Search for functions with similar names
   - Look for repeated logic patterns
   - Check for copy-pasted code blocks

2. **Class Duplication**
   - Find classes with similar structures
   - Identify repeated inheritance patterns
   - Check for duplicate utility classes

3. **Import Duplication**
   - Excessive repeated imports
   - Redundant import patterns

4. **String/Constant Duplication**
   - Repeated string literals
   - Hardcoded values across files

### Step 3: Analysis Approach

Use these techniques to identify duplication:

```bash
# Example: Find similar function signatures
grep -r "^def " "$TARGET_DIR" --include="$PATTERN" | \
  sed 's/:.*$//' | \
  sort | uniq -c | sort -rn | head -20

# Example: Find repeated import patterns
grep -r "^import \|^from " "$TARGET_DIR" --include="$PATTERN" | \
  sort | uniq -c | sort -rn | head -20
```

### Step 4: Read and Compare Files

For files with suspected duplication:
1. Read both files completely
2. Compare function signatures
3. Compare logic patterns
4. Calculate similarity metrics (lines of similar code)

### Step 5: Generate Report

Create a comprehensive report at:
**`docs/technical-debt/code-duplication-report-$(date +%Y%m%d).md`**

## Report Format

```markdown
# Code Duplication Report

**Generated**: YYYY-MM-DD HH:MM:SS
**Target Directory**: <directory>
**Files Analyzed**: <count>
**Duplication Instances**: <count>

---

## Executive Summary

- Total duplicate code blocks: <count>
- Most duplicated pattern: <pattern>
- Estimated refactoring effort: <hours>
- Priority level: HIGH/MEDIUM/LOW

---

## Detailed Findings

### 1. Function Duplication

**Severity**: HIGH/MEDIUM/LOW
**Files Affected**: <count>

#### Instance 1: <Function Name>

**Locations**:
- `file1.py:42-58` (17 lines)
- `file2.py:103-119` (17 lines)
- `file3.py:205-221` (17 lines)

**Similarity**: 95% identical

**Code Sample**:
```python
# Common duplicated code
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
```

**Refactoring Recommendation**:
- Extract to shared utility: `src/utils/calculations.py`
- Create: `calculate_total(items: List[Item]) -> float`
- Replace all 3 instances with import

**Impact**: Removes 51 lines of duplicate code

---

### 2. Class Duplication

**Severity**: MEDIUM
**Files Affected**: <count>

[Similar structure for classes...]

---

### 3. String/Constant Duplication

**Severity**: LOW
**Files Affected**: <count>

[Similar structure for constants...]

---

## Refactoring Recommendations

### High Priority (Do First)

1. **Extract duplicated function: `calculate_total`**
   - Files: file1.py, file2.py, file3.py
   - Effort: 30 minutes
   - Impact: 51 lines reduced

2. **Consolidate error handling patterns**
   - Files: analyzer.py, processor.py
   - Effort: 1 hour
   - Impact: 120 lines reduced

### Medium Priority

[Continue with medium priority items...]

### Low Priority

[Continue with low priority items...]

---

## Metrics

- **Total duplicate lines**: <count>
- **Potential lines saved**: <count>
- **Files requiring changes**: <count>
- **Estimated refactoring time**: <hours>

---

## Next Steps

1. Review high-priority duplications with team
2. Create refactoring tickets for approved items
3. Implement shared utilities in priority order
4. Re-run analysis after refactoring to measure improvement
```

### Step 6: Summary Report

Also create/update a summary file:
**`docs/technical-debt/duplication-summary.md`**

```markdown
# Code Duplication Summary

**Last Updated**: YYYY-MM-DD

## Current Status

- Last Analysis: YYYY-MM-DD
- Duplicate Code Blocks: <count>
- Priority Items: <count>

## Quick Links

- [Latest Full Report](./code-duplication-report-YYYYMMDD.md)
- [Previous Reports Archive](#historical-reports)

## Top 5 Duplication Hot Spots

1. `calculate_total()` - 3 instances, 51 lines
2. `error_handler()` - 5 instances, 120 lines
3. [...]

## Historical Reports

- [2025-10-09 Report](./code-duplication-report-20251009.md)
- [2025-10-01 Report](./code-duplication-report-20251001.md)
```

---

## Success Criteria

- ✅ Analysis completes without errors
- ✅ Report written to `docs/technical-debt/`
- ✅ All findings include file paths with line numbers
- ✅ Refactoring recommendations are specific and actionable
- ✅ No code is modified (read-only analysis)
- ✅ Findings are ranked by severity/priority

---

## Notes

**Read-Only**: This command NEVER modifies code. It only analyzes and reports.

**Performance**: For large codebases (>1000 files), consider:
- Limiting to specific directories
- Using file patterns to filter
- Running analysis in background

**False Positives**: Some duplication may be intentional (e.g., boilerplate). Use judgment when reviewing findings.
```

---

### Example 2: Advanced Agent (Only if Needed)

**File**: `.claude/agents/duplication-analyzer.md`

```markdown
---
name: duplication-analyzer
description: Advanced code duplication analysis agent with iterative investigation. Use when slash command is insufficient for complex refactoring analysis.
tools: Read, Grep, Glob, Bash, Write
model: sonnet
---

# Advanced Code Duplication Analysis Agent

You are a code quality specialist focused on detecting, analyzing, and providing refactoring guidance for code duplication.

## Your Mission

When invoked, perform comprehensive duplication analysis:

1. **Discovery Phase**
   - Find all code files in target directory
   - Identify file types and structure
   - Catalog potential duplication patterns

2. **Analysis Phase**
   - Compare files for structural similarity
   - Detect copy-pasted code blocks
   - Identify repeated patterns across codebase
   - Calculate similarity metrics

3. **Investigation Phase** (Iterative)
   - For each suspected duplicate:
     - Read both files completely
     - Compare line-by-line
     - Determine if duplication is intentional
     - Assess refactoring feasibility

4. **Reporting Phase**
   - Generate comprehensive markdown report
   - Rank duplications by severity
   - Provide specific refactoring recommendations
   - Write to `docs/technical-debt/`

## Analysis Checklist

For each suspected duplication:
- [ ] Read all involved files
- [ ] Compare function/class signatures
- [ ] Measure code similarity (% identical)
- [ ] Determine root cause (copy-paste, shared logic, etc.)
- [ ] Assess refactoring effort (hours)
- [ ] Provide specific recommendations

## Output Format

**Report Location**: `docs/technical-debt/code-duplication-report-<timestamp>.md`

**Report Structure**:
1. Executive Summary
2. Detailed Findings (ranked by severity)
3. Refactoring Recommendations
4. Metrics and Impact Assessment
5. Next Steps

## Tools You Have

- `Read`: Read source files for comparison
- `Grep`: Search for patterns across codebase
- `Glob`: Find files by pattern
- `Bash`: Run analysis commands (find, wc, diff)
- `Write`: Generate markdown reports

## Critical Guidelines

**What You MUST Do:**
- Always read files completely before judging similarity
- Rank findings by severity and refactoring impact
- Provide specific file paths and line numbers
- Include code samples in reports
- Write findings to `docs/technical-debt/`

**What You MUST NOT Do:**
- **Never modify source code** - this is analysis only
- Never assume duplication is bad without context
- Never provide vague recommendations
- Never skip reading files to save time

## Success Criteria

- All findings include specific file locations (path:line)
- Refactoring recommendations are actionable
- Report is written to docs/technical-debt/
- No false positives (verified by reading files)
- Severity ranking is accurate

Always provide forensic-grade analysis suitable for technical debt planning.
```

---

## Best Practices

### 1. Agent-Computer Interface (ACI) Design

Just like Human-Computer Interfaces (HCI), invest time in clear tool definitions:

**Good Tool Documentation:**
```markdown
## Step 2: Pattern Analysis

Search for common duplication patterns:

1. **Function Duplication** - Use grep to find repeated function names
   ```bash
   grep -r "^def " src/ --include="*.py" | sort | uniq -c | sort -rn
   ```

2. **Class Duplication** - Look for similar class structures
   [Specific commands and expected output...]
```

**Poor Tool Documentation:**
```markdown
## Step 2: Analyze

Look for duplicates and report them.
```

### 2. Clear Success Criteria

Define what "done" looks like:

```markdown
## Success Criteria

- ✅ Report generated at docs/technical-debt/code-duplication-report-*.md
- ✅ All findings include file:line references
- ✅ Severity ranking: HIGH/MEDIUM/LOW assigned
- ✅ Refactoring effort estimated in hours
- ✅ No code modifications made (read-only)
```

### 3. Structured Output Format

Provide exact report templates in the command/agent definition.

### 4. Read-Only Analysis

For analysis tasks, explicitly state **no code changes**:

```markdown
**CRITICAL**: This is analysis-only. Do not modify any source files.
```

### 5. Incremental Complexity

**Phase 1**: Start with simple slash command
- Fixed workflow
- Basic pattern detection
- Simple reporting

**Phase 2**: Upgrade to agent only if needed
- Iterative investigation required
- Complex decision-making
- Dynamic refactoring analysis

### 6. File Naming Conventions

```
docs/technical-debt/
├── code-duplication-report-20251009.md   # Timestamped reports
├── code-duplication-report-20251001.md
├── duplication-summary.md                 # Latest summary (updated)
└── README.md                              # Documentation index
```

### 7. Tool Restrictions

For analysis-only tasks, restrict tools in frontmatter:

```yaml
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*), Write(docs/**)
```

This prevents accidental code modification.

---

## Testing and Validation

### Manual Testing

1. **Create test directory**:
   ```bash
   mkdir -p test/duplication-test
   # Add files with intentional duplication
   ```

2. **Run command**:
   ```bash
   /detect-duplicates test/duplication-test 5 "*.py"
   ```

3. **Verify output**:
   - Report created in `docs/technical-debt/`
   - All duplications found
   - Line numbers accurate
   - Recommendations actionable

### Validation Checklist

- [ ] Command completes without errors
- [ ] Report generated at correct path
- [ ] All findings include file:line references
- [ ] Severity ranking is accurate
- [ ] Refactoring recommendations are specific
- [ ] No source files were modified
- [ ] False positive rate is acceptable (<10%)

---

## Example Invocations

```bash
# Analyze entire src/ directory
/detect-duplicates src/ 5

# Analyze specific subdirectory
/detect-duplicates src/analyzers 10 "*.py"

# Focus on TypeScript files
/detect-duplicates frontend/src 8 "*.ts"

# Analyze with custom threshold
/detect-duplicates . 3 "*.js"
```

---

## Integration with Evidence Toolkit

For the Evidence Toolkit specifically:

```bash
# Analyze core modules
/detect-duplicates src/evidence_toolkit/core 5 "*.py"

# Analyze analyzers
/detect-duplicates src/evidence_toolkit/analyzers 5 "*.py"

# Full codebase analysis
/detect-duplicates src/evidence_toolkit 5 "*.py"
```

### Expected Duplication Patterns in Evidence Toolkit

1. **Pydantic Model Validation**
   - Similar field definitions across models
   - Common validators

2. **Chain of Custody Logging**
   - Repeated timestamp/actor logging
   - Common audit trail patterns

3. **Storage Operations**
   - SHA256 hash calculations
   - File path generation

4. **AI Analyzer Prompts**
   - Similar prompt construction
   - Common response parsing

---

## References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Evidence Toolkit Agent Proposal](.claude/AGENT_PROPOSAL.md)
- [Slash Commands README](.claude/commands/README.md)
- [RCA Debugger Agent](.claude/agents/rca-debugger.md) - Example read-only agent

---

## Summary

**Recommendation**: Start with the **simple slash command** (Example 1)

**Why**:
1. ✅ **Simpler** - Fixed workflow, no agent complexity
2. ✅ **Faster** - Can implement in <1 hour
3. ✅ **Sufficient** - Code duplication detection is predictable
4. ✅ **Measurable** - Easy to validate results
5. ✅ **Maintainable** - Clear, templated approach

**Only upgrade to agent (Example 2) if**:
- Slash command proves insufficient
- Need iterative investigation loops
- Require dynamic decision-making
- Want automated refactoring suggestions

**Key Takeaways**:
- Invest time in clear tool documentation (ACI design)
- Provide structured output templates
- Start simple, add complexity only when needed
- Read-only analysis for safety
- Write findings to `docs/technical-debt/`

---

**End of Guide**
