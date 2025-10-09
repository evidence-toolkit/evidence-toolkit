# Technical Debt Documentation

This directory contains technical debt analysis reports and tracking documentation for the Evidence Toolkit.

---

## Directory Structure

```
docs/technical-debt/
├── README.md                              # This file
├── code-duplication-agent-guide.md        # Guide for building duplication detection
├── code-duplication-report-YYYYMMDD.md    # Timestamped analysis reports
└── duplication-summary.md                 # Latest duplication status
```

---

## Available Reports

### Code Duplication Analysis

**Purpose**: Detect and track duplicate code across the codebase

**Generate Report**:
```bash
/detect-duplicates [directory] [min-lines] [pattern]
```

**Example Invocations**:
```bash
# Analyze entire src/ directory
/detect-duplicates src/evidence_toolkit 5 "*.py"

# Analyze core modules only
/detect-duplicates src/evidence_toolkit/core 5 "*.py"

# Analyze analyzers with higher threshold
/detect-duplicates src/evidence_toolkit/analyzers 10 "*.py"
```

**Outputs**:
- Full report: `code-duplication-report-<timestamp>.md`
- Summary: `duplication-summary.md` (updated each run)

**Report Contents**:
- Executive summary with metrics
- Detailed findings ranked by severity (HIGH/MEDIUM/LOW)
- Specific file:line references for each duplication
- Refactoring recommendations with effort estimates
- Impact assessment and metrics

---

## Report Naming Convention

All analysis reports use timestamped filenames:

```
<report-type>-<timestamp>.md

Examples:
- code-duplication-report-20251009_143022.md
- security-audit-report-20251010_091530.md
```

This allows:
- Historical tracking of technical debt
- Trend analysis over time
- Before/after comparisons

---

## Workflow

### 1. Initial Analysis

```bash
# Run first-time analysis
/detect-duplicates src/evidence_toolkit 5 "*.py"

# Review generated report
cat docs/technical-debt/code-duplication-report-<timestamp>.md
```

### 2. Review & Prioritize

1. Review findings with team
2. Validate high-priority items
3. Create refactoring tickets
4. Assign to sprints

### 3. Refactoring

1. Implement changes for high-priority items
2. Write/update tests
3. Validate changes
4. Document improvements

### 4. Re-analysis

```bash
# Run analysis again after refactoring
/detect-duplicates src/evidence_toolkit 5 "*.py"

# Compare before/after metrics
diff docs/technical-debt/code-duplication-report-<old>.md \
     docs/technical-debt/code-duplication-report-<new>.md
```

---

## Metrics Tracking

Each report includes key metrics:

| Metric | Description |
|--------|-------------|
| **Duplicate Code Blocks** | Number of distinct duplication patterns |
| **Total Duplicate Lines** | Estimated lines of duplicated code |
| **Files Affected** | Number of files containing duplications |
| **Refactoring Effort** | Estimated hours to resolve |
| **Priority Distribution** | HIGH/MEDIUM/LOW breakdown |

---

## Best Practices

### When to Run Analysis

- **Monthly**: Regular scheduled analysis
- **Before Major Releases**: Pre-release health check
- **After Large Features**: Check for new duplication
- **During Refactoring**: Measure improvement

### How to Use Reports

1. **Triage**: Review executive summary first
2. **Prioritize**: Focus on HIGH priority items
3. **Estimate**: Use effort estimates for planning
4. **Track**: Monitor trends over time
5. **Celebrate**: Measure improvements after refactoring

### Report Retention

- **Keep Latest**: Always keep most recent report
- **Keep Monthly**: One report per month for trends
- **Archive Old**: Move reports >6 months to archive/

---

## Future Reports

Planned technical debt analyses:

- [ ] **Security Audit**: Check for security anti-patterns
- [ ] **Performance Analysis**: Identify performance bottlenecks
- [ ] **Test Coverage**: Track test coverage gaps
- [ ] **Dependency Audit**: Check outdated dependencies
- [ ] **Documentation Coverage**: Find undocumented code

---

## Contributing

To add a new technical debt analysis:

1. Create slash command in `.claude/commands/`
2. Follow report format conventions
3. Write output to `docs/technical-debt/`
4. Use timestamped filenames
5. Update this README

See [code-duplication-agent-guide.md](./code-duplication-agent-guide.md) for detailed guidance.

---

## References

- [Building Claude Code Agents Guide](./code-duplication-agent-guide.md)
- [Evidence Toolkit Architecture](../V3_ARCHITECTURE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Slash Commands Documentation](../../.claude/commands/README.md)

---

**Last Updated**: 2025-10-09
