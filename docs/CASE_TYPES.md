# Case Type Configuration

**Version**: 3.2+
**Feature**: Domain-Specific Executive Summaries

---

## Overview

The Evidence Toolkit now supports **domain-specific executive summary generation** using specialized prompts tailored to different legal case types. This ensures the AI focuses on the most relevant legal issues, procedures, and implications for each type of case.

## Available Case Types

### 1. `generic` (Default)
**Use for**: General legal matters, investigations, compliance reviews

**Focus areas**:
- Cross-evidence correlations and timeline patterns
- Legal significance and admissibility
- Risk factors and compliance issues
- Professional recommendations for legal proceedings

### 2. `workplace` / `employment`
**Use for**: Employment disputes, workplace investigations, HR matters

**Focus areas**:
- Workplace dispute narrative (who, what, when, where)
- Employment law issues (unfair dismissal, discrimination, harassment, whistleblowing)
- Management and HR procedural compliance
- Employee grievances and employer responses
- Power dynamics and organizational culture

**Legal frameworks analyzed**:
- Employment tribunal claims
- ACAS Code compliance
- Equality Act 2010 (protected characteristics)
- PIDA (whistleblowing protections)
- Breach of implied terms (trust and confidence)

**Output emphasis**:
- Claimant vs. Respondent identification
- Grievance escalation timeline
- Procedural fairness assessment
- Constructive dismissal risk
- Witness credibility evaluation

### 3. `contract`
**Use for**: Commercial disputes, contractual breaches, B2B conflicts

**Focus areas**:
- Contract terms and conditions
- Performance obligations and breaches
- Commercial relationships and dealing
- Financial implications
- Remedies and damages

---

## Usage

### CLI

```bash
# Default generic case type
uv run evidence-toolkit package --case-id MY_CASE

# Workplace/employment case
uv run evidence-toolkit package --case-id MY_CASE --case-type workplace

# Contract dispute
uv run evidence-toolkit package --case-id MY_CASE --case-type contract
```

### Python API

```python
from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.pipeline.package import PackageGenerator
from openai import OpenAI
from pathlib import Path

storage = EvidenceStorage(Path('data/storage'))
openai_client = OpenAI()

# Create package with workplace-specific analysis
package_gen = PackageGenerator(
    storage,
    openai_client,
    case_type='workplace'  # <-- Specify case type
)

result = package_gen.create_client_package(
    case_id='BCH_WORKPLACE_2025',
    output_directory=Path('data/packages')
)
```

---

## Example Comparison

### Generic Case Type Output:
> "The case presents critical evidence of numerous hygiene and safety violations across a retail environment..."

**Issue**: Misses the employment law context entirely.

### Workplace Case Type Output:
> "This case centers on an employment dispute involving Paul Boucherat (Claimant) against Sainsbury's management (Respondent). The evidence reveals a pattern of escalating workplace grievances from February 2025 through August 2025, culminating in suspension. Key employment law issues include potential constructive dismissal (breach of trust and confidence), procedural failures in the grievance process, and evidence of retaliatory conduct by management..."

**Benefit**: Immediately identifies the legal framework, parties, timeline, and relevant employment law claims.

---

## Adding New Case Types

To add a new case type, edit [domains/legal_config.py](../src/evidence_toolkit/domains/legal_config.py):

```python
# 1. Create prompt constant
EXECUTIVE_SUMMARY_PROMPT_MEDICAL = """You are analyzing a MEDICAL NEGLIGENCE case...
[Detailed prompt focusing on standard of care, causation, damages, etc.]
"""

# 2. Register in the case type registry
EXECUTIVE_SUMMARY_PROMPTS = {
    'generic': EXECUTIVE_SUMMARY_PROMPT_GENERIC,
    'workplace': EXECUTIVE_SUMMARY_PROMPT_WORKPLACE,
    'contract': EXECUTIVE_SUMMARY_PROMPT_CONTRACT,
    'medical': EXECUTIVE_SUMMARY_PROMPT_MEDICAL,  # <-- Add here
}
```

# 3. Update CLI choices in cli.py
```python
@click.option('--case-type', type=click.Choice([
    'generic', 'workplace', 'employment', 'contract', 'medical'
]),
```

---

## Prompt Engineering Best Practices

When creating new case type prompts:

1. **Be Specific**: Reference exact legal frameworks (statutes, regulations, case law)
2. **Use Industry Terminology**: Employment tribunal, claimant/respondent, procedural fairness
3. **Guide Analysis**: Tell the AI what to look for (timeline gaps, credibility issues, etc.)
4. **Structure Output**: Specify exactly what sections and format you want
5. **Set Context**: Explain the legal domain at the start of the prompt
6. **Include Examples**: Show the AI what good analysis looks like in "Critical Analysis Points"

---

## Benefits

### Before (Generic Prompt)
- ❌ Focused on hygiene/safety issues (not employment law)
- ❌ Missed the dispute narrative
- ❌ No identification of claimant/respondent
- ❌ No employment tribunal risk assessment

### After (Workplace Prompt)
- ✅ Focuses on employment law frameworks
- ✅ Identifies parties and their roles
- ✅ Maps grievance escalation timeline
- ✅ Assesses procedural compliance (ACAS Code)
- ✅ Evaluates tribunal claims risk
- ✅ Recommends employment law strategy

---

## Technical Implementation

### Architecture Flow

```
CLI (--case-type workplace)
  ↓
PackageGenerator(case_type='workplace')
  ↓
SummaryGenerator(case_type='workplace')
  ↓
legal_config.EXECUTIVE_SUMMARY_PROMPTS['workplace']
  ↓
OpenAI Responses API with workplace-specific prompt
  ↓
ExecutiveSummaryResponse (tailored to employment law)
```

### Code Locations

- **Prompts**: [src/evidence_toolkit/domains/legal_config.py](../src/evidence_toolkit/domains/legal_config.py)
- **Summary Generator**: [src/evidence_toolkit/pipeline/summary.py](../src/evidence_toolkit/pipeline/summary.py)
- **Package Generator**: [src/evidence_toolkit/pipeline/package.py](../src/evidence_toolkit/pipeline/package.py)
- **CLI**: [src/evidence_toolkit/cli.py](../src/evidence_toolkit/cli.py)

---

## Backward Compatibility

All existing code defaults to `case_type='generic'`, so existing scripts and workflows continue working without modification.

To leverage domain-specific prompts, simply add the `--case-type` flag or `case_type` parameter.
