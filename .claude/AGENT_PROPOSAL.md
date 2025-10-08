# Evidence Toolkit - Agent Proposal (KISS Approach)

**Date**: 2025-10-05
**Status**: Proposal for Review
**Philosophy**: Keep It Simple, Stupid

---

## Guiding Principles

Based on Anthropic's "Building Effective Agents" guidance:

1. **Start simple** - Only add agents when they demonstrably improve outcomes
2. **Measure first** - Agents should solve actual workflow pain points
3. **Clear boundaries** - Each agent should have one focused responsibility
4. **Good ACI** - Invest time in tool descriptions, not complexity
5. **No over-engineering** - Prefer simple slash commands over agents when possible

---

## Current Pain Points (Where Agents Could Help)

### 1. **Evidence Analysis Debugging** ⚠️ HIGH VALUE
**Problem**: When AI analysis fails or produces low-confidence results, debugging requires:
- Reading analysis JSON files
- Checking chain of custody
- Reviewing OpenAI API responses
- Examining evidence metadata
- Tracing through storage structure

**Current Solution**: Manual file reading, grepping, lots of context switching

**Would Benefit From**: Focused debugging agent

---

### 2. **Schema Validation & Compliance** ⚠️ MEDIUM VALUE
**Problem**: Ensuring all outputs follow Pydantic schemas and forensic standards requires:
- Reading multiple model definitions
- Checking JSON compliance
- Validating chain of custody
- Verifying SHA256 integrity

**Current Solution**: Manual validation or test runs

**Would Benefit From**: Schema validation agent

---

### 3. **Case Investigation** ⚠️ LOW VALUE (Maybe Slash Command)
**Problem**: Understanding what evidence exists in a case requires:
- Running `case show` and `storage stats`
- Reading analysis files
- Checking correlations
- Reviewing timeline

**Current Solution**: CLI commands work well

**Would Benefit From**: Maybe just a custom slash command

---

## Proposed Agents (Minimal Set)

### Agent 1: Evidence Forensics Investigator ✅ RECOMMENDED

**Purpose**: Debug analysis failures and investigate evidence integrity

**When to Use**:
- AI analysis produces low confidence results
- Evidence analysis fails
- Chain of custody questions
- SHA256 integrity checks needed
- Timeline reconstruction issues

**Tools**: `Read`, `Grep`, `Glob`, `Bash(ls:*), Bash(cat:*)`, `Bash(jq:*)`

**Why This Works**:
- Clear, focused task (investigation/debugging)
- Repeatable workflow pattern
- Measurable success (find root cause)
- Complements existing CLI commands
- High value for forensic work

**Example Invocations**:
```
> Use the forensics investigator to check why analysis failed for sha256 1102b318a5fe2fc6
> Investigate the chain of custody for evidence e81bd4176e3ec009
> Find all evidence with confidence < 0.5 in case WORKPLACE-2024-003
```

---

### Agent 2: Schema Compliance Validator ✅ RECOMMENDED

**Purpose**: Validate Pydantic models, JSON schemas, and forensic integrity

**When to Use**:
- Before creating client packages
- After model changes
- Before pushing commits
- When adding new evidence types
- Ensuring legal compliance

**Tools**: `Read`, `Grep`, `Glob`, `Bash(uv run python:*)`, `Bash(jq:*)`

**Why This Works**:
- Critical for legal admissibility
- Clear success criteria (passes validation)
- Prevents schema drift
- Complements existing validation
- Medium value for quality assurance

**Example Invocations**:
```
> Validate all Pydantic models match their JSON output schemas
> Check schema compliance for case WORKPLACE-2024-003
> Verify chain of custody integrity across all evidence
```

---

## Rejected Agent Ideas (Too Complex or Unnecessary)

### ❌ Case Package Generator Agent
**Reason**: Existing CLI (`evidence-toolkit package`) works perfectly. Adding an agent would duplicate functionality without clear benefit.

### ❌ Multi-Evidence Correlation Agent
**Reason**: The `CorrelationAnalyzer` class already does this well. An agent would add overhead without improving results.

### ❌ AI Prompt Optimizer Agent
**Reason**: This is a one-time design task, not a repeatable workflow. Better handled by manual prompt engineering.

### ❌ Storage Management Agent
**Reason**: New CLI commands (`storage stats`, `storage cleanup`, `storage prune`) handle this perfectly. An agent would be overkill.

---

## Alternative: Custom Slash Commands (Simpler)

For workflows that don't need dynamic decision-making, slash commands are better:

### `/investigate-evidence [sha256]`
```markdown
---
description: Investigate evidence analysis and chain of custody
allowed-tools: Read, Grep, Glob, Bash(jq:*)
---

## Investigation for Evidence: $1

!`ls -la data/storage/derived/sha256=$1/`

1. Load and analyze:
   - analysis.v1.json
   - chain_of_custody.json
   - metadata.json

2. Check for:
   - Low confidence scores
   - Missing required fields
   - Chain of custody gaps
   - Schema compliance issues

3. Provide actionable recommendations
```

### `/validate-case [case-id]`
```markdown
---
description: Validate all evidence in a case for schema compliance
allowed-tools: Bash(uv run:*), Bash(jq:*), Read
---

## Validation for Case: $1

!`uv run evidence-toolkit case evidence $1`

For each evidence item:
1. Validate Pydantic models
2. Check JSON schema compliance
3. Verify chain of custody
4. Check SHA256 integrity

Report any compliance issues.
```

---

## Decision Matrix: Agent vs Slash Command

| Criteria | Agent Better | Slash Command Better |
|----------|--------------|---------------------|
| **Fixed workflow** | | ✅ |
| **Dynamic decisions** | ✅ | |
| **Multiple tools** | ✅ | ✅ (both work) |
| **Iterative loops** | ✅ | |
| **Simple task** | | ✅ |
| **Repeatable** | ✅ | ✅ (both work) |
| **Needs context** | ✅ | |

---

## Recommended Implementation Order

### Phase 1: Start with Slash Commands (Week 1)
1. `/investigate-evidence [sha256]` - Fastest value, simplest implementation
2. `/validate-case [case-id]` - Schema validation without agent overhead

**Rationale**: Slash commands are simpler, faster to build, easier to debug. Start here and measure if they're sufficient.

### Phase 2: Add Agent Only If Needed (Week 2-3)
**Only if** slash commands prove insufficient:
- Create `evidence-forensics-investigator` agent for complex investigations
- Create `schema-compliance-validator` agent for automated validation

**Decision Criteria**:
- Do slash commands handle 80%+ of cases? → Keep slash commands
- Do we need iterative debugging? → Add forensics agent
- Do we need automated validation loops? → Add schema agent

---

## Success Metrics

How to measure if agents/commands are working:

### Slash Commands
- **Usage**: How often are they invoked?
- **Success**: Do they solve the problem?
- **Time saved**: Minutes saved per investigation

### Agents (if implemented)
- **Accuracy**: Do they find root causes?
- **Efficiency**: Do they reduce debugging time?
- **Reliability**: Do they produce consistent results?

---

## Recommendation: START WITH SLASH COMMANDS

**Why**:
1. **Simpler** - No agent complexity, just templated prompts
2. **Faster** - Can implement in <30 minutes
3. **Measurable** - Easy to see if they're useful
4. **Reversible** - Can always upgrade to agents later
5. **KISS** - Follows "simplest solution first" principle

**Next Steps**:
1. Create `/investigate-evidence` slash command
2. Create `/validate-case` slash command
3. Use them for 1-2 weeks
4. Measure value
5. Only create agents if slash commands prove insufficient

---

## Appendix: Agent Template (If Needed Later)

### Evidence Forensics Investigator

```markdown
---
name: evidence-forensics-investigator
description: Forensic investigation specialist for evidence analysis debugging and integrity checks. Use proactively when analysis fails or produces low confidence results.
tools: Read, Grep, Glob, Bash(ls:*), Bash(cat:*), Bash(jq:*)
model: sonnet
---

You are a forensic evidence investigator specializing in debugging AI analysis failures and verifying evidence integrity for legal proceedings.

## Your Mission

When invoked, investigate evidence analysis issues systematically:

1. **Locate Evidence**: Find the evidence in content-addressed storage
   - `data/storage/derived/sha256=<hash>/`
   - Check if files exist

2. **Read Analysis Files**:
   - `analysis.v1.json` - Full analysis results
   - `chain_of_custody.json` - Audit trail
   - `metadata.json` - File metadata
   - `evidence_bundle.v1.json` - Forensic bundle

3. **Identify Issues**:
   - Low confidence scores (< 0.7)
   - Missing required fields
   - Schema validation failures
   - Chain of custody gaps
   - Timestamp anomalies

4. **Root Cause Analysis**:
   - Was the AI analysis successful?
   - Is the evidence corrupted?
   - Are there storage issues?
   - Is the schema compliant?

5. **Actionable Recommendations**:
   - How to fix the issue
   - What commands to run
   - Whether re-analysis is needed

## Investigation Checklist

For each evidence item:
- [ ] Verify SHA256 hash integrity
- [ ] Check file exists in raw/ and derived/
- [ ] Validate JSON structure
- [ ] Check confidence scores
- [ ] Review chain of custody
- [ ] Verify timestamps are sequential
- [ ] Check for required fields

## Output Format

**Evidence**: [SHA256]
**Status**: [OK | WARNING | CRITICAL]
**Issues Found**: [Count]

### Critical Issues
- [List critical problems]

### Warnings
- [List warnings]

### Recommendations
1. [Specific action]
2. [Specific action]

## Tools You Have

- `Read`: Read any file
- `Grep`: Search for patterns
- `Glob`: Find files by pattern
- `Bash`: Run ls, cat, jq commands
- `jq`: Parse and validate JSON

Always provide forensic-grade analysis suitable for legal proceedings.
```

---

**End of Proposal**
