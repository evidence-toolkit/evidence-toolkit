# Generators Module Documentation

**Module**: `src/evidence_toolkit/generators/`
**Version**: v3.4.0
**Status**: Production (Phase 1-3 Complete)
**Purpose**: Transform aggregated case data into professional forensic reports

---

## Overview

The generators module provides specialized report generators that transform analyzed evidence data into professional Markdown reports suitable for legal delivery. Each generator focuses on one aspect of forensic analysis (legal opinion, timeline, power dynamics, etc.) and operates independently.

`★ Insight ─────────────────────────────────────`
**Architecture Pattern**: Generators follow the **Template Method** pattern. Each generator inherits from `BaseReportGenerator` and implements `has_data()` and `generate()` methods. The base class provides common formatting utilities (`_build_header`, `_truncate_sha`, etc.).

**Key Design Principle**: Generators are **pure presentation layer** - they never call AI APIs or access raw evidence files. They only format data already aggregated by `SummaryGenerator` into `overall_assessment`.
`─────────────────────────────────────────────────`

---

## Architecture

### Two-Layer Design

```
Evidence Analysis (individual files)
         ↓
SummaryGenerator (pipeline/summary.py)
    ├── _extract_power_dynamics()
    ├── _extract_image_ocr_text()
    ├── _extract_relationship_network()
    └── _build_forensic_assessment()
         ↓
overall_assessment dict (aggregated data)
         ↓
Generators (generators/*.py)
    ├── ForensicLegalOpinionGenerator
    ├── PowerDynamicsGenerator
    ├── ImageOCRGenerator
    └── ... (6 more)
         ↓
Professional Markdown Reports (.md files)
```

**Separation of Concerns**:
- **SummaryGenerator**: Data aggregation (knows how to find/extract data from storage)
- **Generators**: Report formatting (knows how to present data for legal professionals)

---

## Generator Status (v3.4)

| Generator | Status | Data Source | Output | Lines |
|-----------|--------|-------------|--------|-------|
| **Phase 1** | | | | |
| ForensicLegalOpinionGenerator | ✅ Production | `_forensic_*` fields | forensic_legal_opinion.md | 390 |
| FinancialRiskAssessmentGenerator | ✅ Production | `tribunal_probability`, `financial_exposure_summary` | financial_risk_assessment.md | 503 |
| **Phase 2** | | | | |
| LegalPatternsGenerator | ✅ Production | `correlation_result.legal_patterns` | legal_patterns_analysis.md | 565 |
| TimelineGenerator | ✅ Production | `correlation_result.timeline_events` | timeline_reconstruction.md | 459 |
| QuotedStatementsGenerator | ✅ Production | `quoted_statements` | quoted_statements_analysis.md | 448 |
| **Phase 3** | | | | |
| RelationshipNetworkGenerator | ✅ Production | `relationship_network` | relationship_network_analysis.md | 402 |
| PowerDynamicsGenerator | ✅ Production | `power_dynamics` | power_dynamics_analysis.md | 294 |
| ImageOCRGenerator | ✅ Production | `image_ocr` | image_ocr_analysis.md | 275 |
| **Base** | | | | |
| BaseReportGenerator | ✅ Foundation | N/A | N/A | 255 |

**Total**: 9 generators, 3,591 lines of code, **8 professional reports**

---

## Usage

### In Pipeline

Generators are automatically invoked by `PackageGenerator` (pipeline/package.py):

```python
from evidence_toolkit.generators import (
    ForensicLegalOpinionGenerator,
    PowerDynamicsGenerator,
    ImageOCRGenerator
)

# PackageGenerator calls each generator
for generator_class in generator_classes:
    generator = generator_class(case_summary, reports_dir)

    if generator.has_data():
        report_path = generator.generate()
        print(f"✓ Generated: {report_path.name}")
    else:
        print(f"⊘ Skipped {generator_class.__name__}: Insufficient data")
```

### Standalone Usage

Generators can be used independently:

```python
from evidence_toolkit.pipeline.summary import SummaryGenerator
from evidence_toolkit.generators import PowerDynamicsGenerator
from pathlib import Path

# 1. Generate case summary (aggregates data)
summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary(
    case_id="MY-CASE",
    ai_summary=True,
    ai_resolve=True
)

# 2. Use specific generator
output_dir = Path("reports")
generator = PowerDynamicsGenerator(case_summary, output_dir)

if generator.has_data():
    report_path = generator.generate()
    print(f"Report created: {report_path}")
else:
    print("No power dynamics data available")
```

---

## Creating New Generators

### Template

```python
from pathlib import Path
from evidence_toolkit.generators.base import BaseReportGenerator

class MyCustomGenerator(BaseReportGenerator):
    """Generate custom forensic report.

    Data source: overall_assessment['my_field']
    """

    def get_report_filename(self) -> str:
        return "my_custom_report.md"

    def get_report_title(self) -> str:
        return "My Custom Analysis"

    def has_data(self) -> bool:
        """Check if required data exists."""
        my_data = self._safe_get('my_field')
        return bool(my_data)

    def generate(self) -> Path:
        """Generate the report."""
        data = self._safe_get('my_field', {})

        content = self._build_header(subtitle="Subtitle")
        content += self._build_my_section(data)

        report_path = self.output_dir / self.get_report_filename()
        report_path.write_text(content, encoding='utf-8')
        return report_path

    def _build_my_section(self, data: dict) -> str:
        """Build custom section."""
        section = "\n## My Analysis\n\n"
        # Format data as Markdown
        return section
```

### Base Class Utilities

All generators inherit these helpers from `BaseReportGenerator`:

```python
# Header generation
content = self._build_header(
    subtitle="Subtitle Text",
    include_case_id=True
)

# SHA256 truncation for readability
short_sha = self._truncate_sha("abc123...def456")  # → "abc123de"

# Safe dictionary access
value = self._safe_get('field_name', default_value)

# List formatting
items = ["Item 1", "Item 2", "Item 3"]
formatted = self._format_list_items(items)
# → "- Item 1\n- Item 2\n- Item 3\n"
```

---

## Data Access Patterns

`★ Insight ─────────────────────────────────────`
**Critical Pattern Distinction**:

1. **Dictionary fields** (e.g., `overall_assessment` itself):
   ```python
   value = self._safe_get('field_name', default)
   ```

2. **Pydantic model fields** (e.g., `correlation_result`):
   ```python
   # Access correlation_result from case_summary
   corr = self.case_summary.correlation_result

   # Access Pydantic model attributes directly
   legal_patterns = corr.legal_patterns  # LegalPatternAnalysis model
   contradictions = legal_patterns.contradictions  # List[Contradiction]

   # NEVER use .get() on Pydantic models!
   ```

**Common Mistake**: Using `.get()` on Pydantic models causes `AttributeError`.
`─────────────────────────────────────────────────`

### Examples by Generator

**ForensicLegalOpinionGenerator** (Dictionary access):
```python
forensic_summary = self._safe_get('_forensic_summary', '')
risk_assessment = self._safe_get('_forensic_risk_assessment', 'unknown')
```

**LegalPatternsGenerator** (Pydantic model access):
```python
correlation_result = self.case_summary.correlation_result
legal_patterns = correlation_result.legal_patterns  # Pydantic model

for contradiction in legal_patterns.contradictions:
    # Access Pydantic model attributes
    severity = contradiction.severity
    statement_1 = contradiction.statement_1
    evidence_sha = contradiction.evidence_sha256
```

**PowerDynamicsGenerator** (Dictionary access):
```python
power_data = self._safe_get('power_dynamics', {})
participants = power_data.get('top_participants', [])

for p in participants:
    name = p.get('participant')
    authority = p.get('authority')
    deference = p.get('avg_deference', 0.5)
```

---

## Report Quality Standards

### Structure

All reports follow this structure:

1. **Header** (generated by `_build_header()`):
   - Title (H1)
   - Subtitle
   - Case ID
   - Generation timestamp
   - Evidence Toolkit version
   - Evidence count

2. **Executive Summary** (2-3 paragraphs):
   - High-level findings
   - Key metrics
   - Forensic significance

3. **Detailed Sections** (H2 headers):
   - Organized by topic
   - Tables for structured data
   - Lists for findings
   - Code blocks for quotes/text

4. **Methodology/Interpretation** (optional):
   - How analysis was performed
   - Legal relevance
   - Recommendations

### Formatting Guidelines

**Evidence Citations**:
```markdown
Evidence `abc12345` shows...
```
Use `_truncate_sha()` for readability.

**Tables**:
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
```

**Lists** (findings, recommendations):
```markdown
- **Key Point**: Description with emphasis
- **Another Point**: More details
```

**Quotes** (from evidence):
```markdown
> "Direct quote from evidence"
> — Source context
```

---

## Conditional Generation

Generators implement `has_data()` to check if required data exists before generating:

```python
def has_data(self) -> bool:
    power_dynamics = self._safe_get('power_dynamics')
    if not power_dynamics:
        return False

    participants = power_dynamics.get('top_participants', [])
    return len(participants) > 0
```

**Benefits**:
- Graceful skipping (no errors when data unavailable)
- Clean user experience (`⊘ Skipped: Insufficient data`)
- Conditional reports based on evidence types

**Example**:
- Case with emails → power_dynamics generates
- Case with only documents → power_dynamics skips

---

## Data Requirements by Generator

| Generator | Requires | Conditional On |
|-----------|----------|----------------|
| ForensicLegalOpinionGenerator | `_forensic_summary` | AI summary enabled |
| FinancialRiskAssessmentGenerator | `tribunal_probability` | AI summary enabled |
| LegalPatternsGenerator | `correlation_result.legal_patterns` | AI correlation enabled |
| TimelineGenerator | `correlation_result.timeline_events` | Always (correlation) |
| QuotedStatementsGenerator | `quoted_statements` | Documents with quotes |
| RelationshipNetworkGenerator | `relationship_network` | Entity correlations |
| PowerDynamicsGenerator | `power_dynamics` | Email evidence (`.eml/.msg/.mbox`) |
| ImageOCRGenerator | `image_ocr` | Image evidence with text |

**Key Dependencies**:
- AI summary must be enabled (`--ai-summary` or default)
- Email files must be proper email format (not `.txt` containing emails)
- Images must have detectable text

---

## Testing

### Unit Tests

```python
from evidence_toolkit.generators import PowerDynamicsGenerator
from evidence_toolkit.pipeline.summary import CaseSummary
from pathlib import Path

def test_power_dynamics_has_data():
    """Test has_data() method."""
    # Create mock case_summary with power_dynamics
    case_summary = CaseSummary(
        case_id="TEST",
        overall_assessment={
            'power_dynamics': {
                'top_participants': [
                    {'participant': 'Alice', 'authority': 'management'}
                ]
            }
        }
    )

    generator = PowerDynamicsGenerator(case_summary, Path("/tmp"))
    assert generator.has_data() == True

def test_power_dynamics_no_data():
    """Test has_data() returns False when no data."""
    case_summary = CaseSummary(
        case_id="TEST",
        overall_assessment={}
    )

    generator = PowerDynamicsGenerator(case_summary, Path("/tmp"))
    assert generator.has_data() == False
```

### Integration Tests

```bash
# Create test case with mixed evidence
uv run evidence-toolkit process-case data/cases/TEST-CASE \
  --case-id TEST-CASE \
  --case-type workplace \
  --ai-resolve

# Verify all expected reports generated
ls data/packages/TEST-CASE_*/reports/*.md
```

---

## Performance

**Generator execution time**: <1 second per report (pure formatting, no AI calls)

**Bottlenecks**:
- Data aggregation happens in SummaryGenerator (AI calls)
- Generators are I/O-bound (writing files)

**Optimization**:
- Generators execute sequentially (no parallel benefit)
- Total time: ~5-8 seconds for all 8 reports
- Dominated by file I/O, not computation

---

## Troubleshooting

### Report Not Generated

**Symptom**: `⊘ Skipped GeneratorName: Insufficient data`

**Diagnosis**:
1. Check `has_data()` implementation
2. Verify data exists in `overall_assessment`:
   ```python
   import json
   with open('case_analysis.json') as f:
       data = json.load(f)
   print(data['overall_assessment'].keys())
   ```
3. Check data aggregation in SummaryGenerator

**Common Causes**:
- AI summary disabled (`--no-ai-summary`)
- Wrong evidence file types (`.txt` emails instead of `.eml`)
- No data of required type (no images for image_ocr)

### AttributeError on Pydantic Model

**Symptom**: `AttributeError: 'LegalPatternAnalysis' object has no attribute 'get'`

**Cause**: Using dictionary `.get()` method on Pydantic model

**Fix**:
```python
# WRONG
contradictions = legal_patterns.get('contradictions')

# CORRECT
contradictions = legal_patterns.contradictions
```

### Empty Report Sections

**Symptom**: Report generated but sections are empty

**Diagnosis**:
1. Check data structure matches expected format
2. Verify list/dict is not empty in aggregated data
3. Add debug logging in generator methods

**Fix**: Update data access to match actual structure from SummaryGenerator

---

## Future Enhancements

**Potential Phase 4 Generators**:
- `audio_transcript.py`: Audio/video transcript analysis
- `metadata_forensics.py`: EXIF, file metadata analysis
- `semantic_similarity.py`: Document similarity/plagiarism detection
- `communication_graph.py`: Visual network diagram generation

**Architecture Improvements**:
- Parallel generator execution (ThreadPoolExecutor)
- Template-based report generation (Jinja2)
- Multi-format output (PDF, HTML, DOCX)
- Report customization via config files

---

## Related Documentation

- **Base Module**: [src/evidence_toolkit/generators/base.py](../../src/evidence_toolkit/generators/base.py)
- **SummaryGenerator**: [docs/module-docs/SUMMARY_GENERATOR.md](SUMMARY_GENERATOR.md)
- **Implementation Plan**: [docs/GENERATORS_IMPLEMENTATION_PLAN.md](../GENERATORS_IMPLEMENTATION_PLAN.md)
- **Package Generator**: [docs/module-docs/PACKAGE_GENERATOR.md](PACKAGE_GENERATOR.md)

---

**Last Updated**: 2025-10-10
**Version**: v3.4.0
**Status**: Production-ready (Phase 1-3 complete)
