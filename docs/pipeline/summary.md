# Case Summary Generator

## Overview

The Case Summary Generator aggregates all evidence analysis results for a case, performs cross-evidence correlation analysis, generates AI-powered executive summaries, and produces comprehensive case reports. It serves as the analytical capstone of the Evidence Toolkit pipeline, transforming individual evidence analyses into actionable case-level insights suitable for legal proceedings and consulting engagements.

This module uses the CorrelationAnalyzer to find entity connections across evidence, reconstructs timelines, detects legal patterns, and leverages OpenAI to generate executive summaries with key findings and recommendations.

## Purpose & Scope

### What Summary Generation Does
- Aggregates all evidence analysis for a case
- Performs cross-evidence entity correlation
- Reconstructs chronological timelines from metadata and content (includes escalation events - v3.2)
- Detects legal patterns (contradictions, corroboration) using AI (v3.1)
- Extracts power dynamics from email evidence (deference, authority, topics - v3.2)
- Extracts quoted statements from document entities (v3.3 Phase A)
- Analyzes communication patterns across email threads (v3.3 Phase A)
- Aggregates image OCR text for visual evidence analysis (v3.3 Phase B)
- Extracts semantic timeline events from date entities (v3.3 Phase B)
- Builds relationship networks from entity connections (v3.3 Phase B)
- Generates AI-powered executive summaries with pattern insights (v3.2 enhanced)
- Calculates overall case assessment metrics
- Exports summaries to JSON and formatted reports

### What Summary Generation Does NOT Do
- Evidence ingestion (handled by ingestion pipeline)
- Individual evidence analysis (handled by analysis pipeline)
- Client package creation (handled by packaging pipeline)
- Evidence modification or validation

### Design Principles
1. **Case-Level Analysis**: Operates at case scope, not individual evidence
2. **AI-Enhanced**: Uses OpenAI for executive insights and pattern detection
3. **Forensic Grade**: Complete audit trails and confidence scoring
4. **Export Flexibility**: JSON and human-readable formats
5. **Pydantic Throughout**: All models fully validated (v3.1)

## Module Structure

```
evidence_toolkit/pipeline/summary.py
│
├── SummaryGenerator           # Main case summary orchestrator
│   ├─→ generate_case_summary()
│   ├─→ export_summary_to_json()
│   └─→ format_summary_report()
│
├── ExecutiveSummaryResponse   # Pydantic model for AI summary
│
├── EvidenceSummary            # Pydantic model for evidence summary (v3.1)
└── CaseSummary                # Pydantic model for complete case (v3.1)
```

### Integration Points
```
src/evidence_toolkit/
├── pipeline/
│   └── summary.py             # This module
│
├── analyzers/
│   └── correlation.py         # CorrelationAnalyzer
│
├── core/
│   ├── models.py              # CorrelationAnalysis, EvidenceSummary, CaseSummary
│   └── storage.py             # EvidenceStorage
│
└── domains/
    └── legal_config.py        # EXECUTIVE_SUMMARY_PROMPT
```

## API Reference

### `SummaryGenerator`

Main class for generating case summaries.

**Initialization:**
```python
class SummaryGenerator:
    def __init__(self, storage: EvidenceStorage, openai_client=None, case_type: str = 'generic'):
        """Initialize summary generator.

        Args:
            storage: EvidenceStorage instance for accessing evidence
            openai_client: Optional OpenAI client for AI executive summaries
            case_type: Case type for domain-specific prompts (v3.2)
                      Options: 'generic', 'workplace', 'employment', 'contract'
                      Default: 'generic'
        """
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `storage` | `EvidenceStorage` | Storage instance for evidence access |
| `correlation_analyzer` | `CorrelationAnalyzer` | Analyzer for cross-evidence correlation **(v3.1: receives openai_client for AI pattern detection)** |
| `openai_client` | `Optional[OpenAI]` | OpenAI client for AI summaries |
| `ai_enabled` | `bool` | Whether AI features are available |
| `case_type` | `str` | **v3.2:** Case type for domain-specific executive summary prompts ('generic', 'workplace', 'employment', 'contract') |

**v3.1 Enhancement:**
The `CorrelationAnalyzer` now receives the `openai_client` parameter, enabling AI-powered legal pattern detection (contradictions, corroboration) alongside traditional entity correlation and timeline reconstruction.

**v3.2 Enhancement - Case Type Support:**
The `case_type` parameter enables domain-specific executive summary generation. For workplace/employment cases, the AI focuses on employment law frameworks (unfair dismissal, discrimination, ACAS compliance, etc.) instead of generic legal analysis. See [CASE_TYPES.md](../../CASE_TYPES.md) for details.

**v3.2 Enhancement - Chunked Summarization:**
Large cases (>50 evidence pieces) now use map-reduce pattern with chunked AI summaries to avoid context length limits. Evidence is broken into 30-item chunks, each summarized individually, then combined for final executive summary. This enables handling of cases with 100+ evidence pieces efficiently.

**v3.2 Enhancement - Power Dynamics Extraction:**
For workplace/employment cases with email evidence, the summary generator now extracts and aggregates power dynamics data:
- **Deference scores**: 0.0 (dominant) to 1.0 (deferential) communication patterns
- **Authority levels**: Executive, management, employee, external classification
- **Message counts**: Communication frequency by participant
- **Dominant topics**: Primary subjects controlled by each participant

This data is included in `overall_assessment['power_dynamics']` and passed to the AI context for executive summary generation, enabling insights like "Paul (employee) shows dominant communication pattern (0.38 deference) when interacting with management, suggesting confidence in position or defensive behavior."

**v3.2 Enhancement - Legal Patterns in AI Context:**
Legal pattern analysis (contradictions, corroboration, evidence gaps) from v3.1 is now included in the AI context when generating executive summaries. This allows the AI to reference specific patterns when making strategic recommendations, resulting in more precise statements like "strong corroborative evidence across 8 pieces supports unfair dismissal claim" rather than generic assessments.

**v3.3 Enhancement - Quoted Statement Aggregation:**
Aggregates quoted statements from document analyses (v3.1 `DocumentEntity.quoted_text` field), grouping by person and surfacing document sentiment/risk flags. Shows who said what, in what tone, with what legal risks. No additional AI calls required - reuses captured data.

**v3.3 Enhancement - Communication Pattern Analysis:**
Aggregates communication patterns from email analyses (professional/escalating/hostile/retaliatory), providing risk assessment and distribution statistics. Enables executive summaries to identify retaliation sequences and escalating disputes. No additional AI calls required - reuses captured data.

**v3.3 Phase A - Maximum Data Utilization:**
All three Phase A enhancements follow the principle of extracting and surfacing ALL captured AI data. Previously, fields like `quoted_text`, `communication_pattern`, and relationship data were captured but not aggregated or presented to users. v3.3 Phase A increases data utilization from 75% (v3.2) to 95%.

**v3.3 Phase B Enhancement - Image OCR Aggregation:**
Aggregates OCR-detected text from all images in a case (from `ImageAnalysisStructured.detected_text`), grouping by detected objects and evidence value (high/medium/low). Critical for image-heavy cases where 75%+ of images contain text (product labels, signs, documents). Provides statistics on text extraction rate, people present, timestamps visible. No additional AI calls - reuses Vision API data.

**v3.3 Phase B Enhancement - Semantic Timeline Events:**
Extracts semantic events from date entities with associated_event fields (v3.1 enhancement). Transforms timeline from "2025-08-24: document created" to "2025-08-24: management meeting with author". Enriches timeline narrative with WHAT happened on dates, not just timestamps. Handles various date formats (ISO, DD/MM/YYYY, "24th August", "March 2025"). Creates timeline events with type='semantic_event'.

**v3.3 Phase B Enhancement - Relationship Network Extraction:**
Builds relationship network graph from entity relationship fields, parsing patterns like "sent email to X", "reported to X", "escalated to X". Identifies key players by connection count, shows organizational hierarchy and communication/escalation paths. Returns top 50 relationships with type distribution (email_communication, escalation, other). Enables visualization of stakeholder networks and escalation chains.

**v3.3 Phase B - Data Utilization Target:**
All three Phase B enhancements continue the maximum data extraction principle. Completes the capture of remaining AI-generated data: image OCR text (143/191 images in test case), semantic timeline events (11 date-associated events), and relationship connections (18 entity relationships). v3.3 Phase B increases data utilization from 95% (Phase A) to 98%.

---

### `SummaryGenerator.generate_case_summary()`

Generate comprehensive summary for a case.

**Signature:**
```python
def generate_case_summary(self, case_id: str) -> CaseSummary
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_id` | `str` | Yes | Case identifier to summarize |

**Returns:**

| Type | Description |
|------|-------------|
| `CaseSummary` | Pydantic model with complete case analysis |

**Exceptions:**

| Exception | When Raised |
|-----------|-------------|
| `ValueError` | If no evidence found for case |

**Process:**
1. Get correlation analysis (includes all case evidence)
   - **v3.1:** Includes AI-powered legal pattern detection (contradictions, corroboration)
   - **v3.1:** Detects temporal sequences and timeline gaps
2. Create detailed evidence summaries
   - **v3.1:** Extracts participant data from `EmailThreadAnalysis`
3. Calculate overall assessment metrics
4. Generate AI executive summary (if enabled)
5. Return complete `CaseSummary`

**Example:**
```python
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary("CASE-001")

print(f"Evidence count: {case_summary.evidence_count}")
print(f"Overall significance: {case_summary.overall_assessment['overall_legal_significance']}")
print(f"Executive summary: {case_summary.executive_summary}")
```

---

### `SummaryGenerator.export_summary_to_json()`

Export case summary to JSON file.

**Signature:**
```python
def export_summary_to_json(
    self,
    case_summary: CaseSummary,
    output_path: Path
) -> bool
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_summary` | `CaseSummary` | Yes | CaseSummary object to export |
| `output_path` | `Path` | Yes | Path for output JSON file |

**Returns:**

| Type | Description |
|------|-------------|
| `bool` | True if successful, False otherwise |

**JSON Structure:**
```json
{
  "case_id": "CASE-001",
  "generation_timestamp": "2025-10-05T14:30:00Z",
  "evidence_count": 10,
  "evidence_types": ["document", "email", "image"],
  "evidence_summaries": [...],
  "correlation_analysis": {
    "entity_correlations": [...],
    "timeline_events": [...],
    "legal_patterns": {...}
  },
  "overall_assessment": {...},
  "executive_summary": "..."
}
```

**Example:**
```python
from pathlib import Path

summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary("CASE-001")

success = summary_gen.export_summary_to_json(
    case_summary,
    Path("data/packages/CASE-001-summary.json")
)
print(f"Export {'succeeded' if success else 'failed'}")
```

---

### `SummaryGenerator.format_summary_report()`

Format case summary as human-readable text report.

**Signature:**
```python
def format_summary_report(self, case_summary: CaseSummary) -> str
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_summary` | `CaseSummary` | Yes | CaseSummary object to format |

**Returns:**

| Type | Description |
|------|-------------|
| `str` | Formatted text report with sections for overview, evidence, correlations, timeline |

**Report Sections:**
- Header with case ID and generation timestamp
- Case overview (evidence count, types, significance)
- Executive summary (if available)
- Evidence analysis (detailed per-evidence findings)
- Entity correlations
- Timeline events
- Risk assessment

**Example:**
```python
summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary("CASE-001")

report_text = summary_gen.format_summary_report(case_summary)
print(report_text)

# Or save to file
Path("report.txt").write_text(report_text)
```

## Data Models

### `ExecutiveSummaryResponse` (Pydantic)

AI-generated executive summary using OpenAI Responses API.

```python
class ExecutiveSummaryResponse(BaseModel):
    executive_summary: str = Field(
        ..., description="Comprehensive executive summary of the case"
    )
    key_findings: List[str] = Field(
        default_factory=list,
        description="List of 3-5 key findings from the evidence analysis"
    )
    legal_implications: List[str] = Field(
        default_factory=list,
        description="Legal implications and significance of the evidence"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Recommended next steps or actions based on the analysis"
    )
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the executive assessment"
    )
    risk_assessment: str = Field(
        ..., description="Overall risk level assessment (low/medium/high/critical)"
    )
```

---

### `EvidenceSummary` (Pydantic, v3.1)

Summary of a single piece of evidence.

```python
class EvidenceSummary(BaseModel):
    sha256: str
    evidence_type: str
    filename: str
    file_size: int
    analysis_confidence: Optional[float] = None
    key_findings: List[str] = Field(default_factory=list)
    legal_significance: Optional[str] = None
    risk_flags: List[str] = Field(default_factory=list)
```

**Converted from @dataclass to Pydantic in v3.1 for consistency.**

---

### `CaseSummary` (Pydantic, v3.1)

Complete case summary with all evidence and analysis.

```python
class CaseSummary(BaseModel):
    case_id: str
    generation_timestamp: datetime
    evidence_count: int
    evidence_types: List[str]
    evidence_summaries: List[EvidenceSummary]
    correlation_result: CorrelationAnalysis
    overall_assessment: Dict[str, Any]
    executive_summary: Optional[str] = None
```

**Converted from @dataclass to Pydantic in v3.1 for consistency.**

---

### `CorrelationAnalysis` (from `core/models.py`)

Cross-evidence correlation results (Pydantic, v3.0/v3.1).

```python
class CorrelationAnalysis(BaseModel):
    case_id: str
    analysis_timestamp: datetime
    evidence_count: int
    entity_correlations: List[CorrelatedEntity]
    timeline_events: List[TimelineEvent]
    legal_patterns: Optional[LegalPatterns] = None  # v3.1: AI-powered patterns
    temporal_sequences: Optional[List[TemporalSequence]] = None  # v3.1
    timeline_gaps: Optional[List[TimelineGap]] = None  # v3.1
```

**v3.1 Enhancements:**
- `legal_patterns`: AI-detected contradictions and corroborations across evidence
  - `contradictions`: List of conflicting statements with sources
  - `corroboration`: List of mutually supporting evidence
- `temporal_sequences`: Detected event sequences and patterns
- `timeline_gaps`: Identified gaps in the timeline requiring attention

## Behavior

### Summary Generation Flow

```
generate_case_summary(case_id)
  ↓
1. Run correlation analysis (v3.1 enhanced)
   └─→ CorrelationAnalyzer.analyze_case_correlations(case_id)
       ├─→ Extract entities from all evidence
       ├─→ Match entities across evidence
       ├─→ Reconstruct timeline from metadata and content
       ├─→ Detect temporal sequences and timeline gaps (v3.1)
       ├─→ AI-powered legal pattern detection (v3.1, if openai_client available):
       │   ├─→ Identify contradictions across evidence
       │   └─→ Identify corroborating evidence
       └─→ Return CorrelationAnalysis with v3.1 enhancements
  ↓
2. Create evidence summaries
   └─→ For each evidence in case:
       ├─→ Load analysis.v1.json
       ├─→ Extract key findings (type-specific)
       ├─→ For emails: Extract participant count from EmailThreadAnalysis (v3.1)
       ├─→ Extract confidence, significance, risk flags
       └─→ Create EvidenceSummary
  ↓
3. Calculate overall assessment
   ├─→ Average confidence scores
   ├─→ Aggregate risk flags
   ├─→ Determine overall legal significance
   ├─→ Count entity correlations and timeline events
   └─→ Include temporal_sequences and timeline_gaps counts (v3.1)
  ↓
4. Generate AI executive summary (if enabled)
   ├─→ Build case context for AI (includes v3.1 patterns)
   ├─→ Call OpenAI Responses API
   ├─→ Parse ExecutiveSummaryResponse
   └─→ Add to CaseSummary
  ↓
5. Return CaseSummary
```

### Evidence Summary Extraction

For each evidence type, key findings are extracted differently:

**Documents:**
```python
# AI-powered analysis (if available)
key_findings = [
    doc_analysis['ai_summary'],
    f"Extracted {len(entities)} entities: {entity_types}",
]
confidence = doc_analysis['analysis_confidence']
legal_significance = doc_analysis['legal_significance']
risk_flags = doc_analysis['risk_flags']

# Fallback (word frequency only)
key_findings = [
    f"Document contains {total_words} words",
    f"Top concepts: {top_word_list}"
]
```

**Emails (v3.1):**
```python
# EmailThreadAnalysis with full participants list
participant_count = len(email_analysis['participants'])
# Participants include: name, email, role, interaction_count, timestamps
key_findings = [
    f"Email thread with {participant_count} participants",
    f"Communication pattern: {communication_pattern}",
    email_analysis['thread_summary']
]
confidence = email_analysis['confidence_overall']
legal_significance = email_analysis['legal_significance']
risk_flags = email_analysis['risk_flags']
```

**v3.1 Email Enhancement:**
Email summaries now extract data from the full `EmailThreadAnalysis` model, preserving participant details (name, email, role, interaction counts, first/last interaction timestamps). This enables cross-evidence participant matching in correlation analysis.

**Images:**
```python
key_findings = [
    f"Scene: {scene_description}",
    f"Text detected: {detected_text}",
    f"Objects: {detected_objects}"
]
confidence = image_analysis['analysis_confidence']
```

### AI Executive Summary Generation

The AI executive summary uses OpenAI Responses API with structured output:

```python
# Build case context
case_context = f"""
CASE ID: {case_id}
EVIDENCE COUNT: {evidence_count}
EVIDENCE TYPES: {evidence_types}

OVERALL ASSESSMENT:
- Legal significance: {overall_legal_significance}
- Average confidence: {average_confidence}
- Risk flags: {total_risk_flags} total
- Entity correlations: {entity_correlations_found}

EVIDENCE ANALYSIS:
[Detailed evidence summaries...]

ENTITY CORRELATIONS:
[Entity correlation details...]

TIMELINE EVENTS:
[Timeline event details...]
"""

# OpenAI Responses API call
response = openai_client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": EXECUTIVE_SUMMARY_PROMPT},
        {"role": "user", "content": case_context}
    ],
    text_format=ExecutiveSummaryResponse
)

# Parse response
if response.status == "completed":
    return response.output_parsed  # ExecutiveSummaryResponse
```

**Prompt** (from `domains/legal_config.py`):
```python
EXECUTIVE_SUMMARY_PROMPT = """You are a forensic analyst preparing an executive summary for legal proceedings.

Analyze the provided case evidence and generate:
1. A comprehensive executive summary (2-3 paragraphs)
2. Key findings (3-5 bullet points)
3. Legal implications
4. Recommended actions

Focus on legal significance, risk assessment, and actionable insights.
Maintain professional tone suitable for court proceedings."""
```

### Overall Assessment Calculation

The overall assessment aggregates metrics from all evidence:

```python
overall_assessment = {
    # Confidence metrics
    "overall_confidence": average(all_confidence_scores),

    # Risk metrics
    "total_risk_flags": len(all_risk_flags),
    "unique_risk_flags": len(set(all_risk_flags)),
    "risk_flag_breakdown": {...},

    # Legal significance
    "legal_significance_distribution": {
        "critical": count,
        "high": count,
        "medium": count,
        "low": count
    },
    "overall_legal_significance": "high",  # Highest from distribution

    # Correlation metrics
    "entity_correlations_found": len(entity_correlations),
    "timeline_events_count": len(timeline_events),

    # Evidence type distribution
    "evidence_type_distribution": {
        "document": 5,
        "email": 3,
        "image": 2
    }
}
```

**Legal Significance Priority:**
```
critical > high > medium > low
```

If ANY evidence is "critical", overall is "critical".

## AI Integration

### Models Used

| Component | Model | Purpose | Cost Impact |
|-----------|-------|---------|-------------|
| Executive Summary | `gpt-4o-2024-08-06` | Case-level insights and recommendations | Medium |
| Legal Patterns (v3.1) | `gpt-4o-2024-08-06` | Contradiction/corroboration detection (via CorrelationAnalyzer) | Medium |

**v3.1 Integration:**
The `CorrelationAnalyzer` receives the `openai_client` from `SummaryGenerator` during initialization:
```python
# v3.1: Pass openai_client to CorrelationAnalyzer for AI pattern detection
self.correlation_analyzer = CorrelationAnalyzer(storage, openai_client=openai_client, verbose=True)
```

This enables AI-powered legal pattern detection during correlation analysis, identifying contradictions and corroborations across evidence pieces.

### Prompts

**Executive Summary Prompt** (`domains/legal_config.py`):
```python
EXECUTIVE_SUMMARY_PROMPT = """You are a forensic analyst preparing an executive summary for legal proceedings.

Given a case with multiple pieces of evidence, entity correlations, and timeline events, generate:

1. EXECUTIVE SUMMARY (2-3 paragraphs):
   - Overview of the case
   - Key patterns and findings
   - Legal significance assessment

2. KEY FINDINGS (3-5 bullet points):
   - Most critical discoveries
   - Important entity relationships
   - Temporal patterns

3. LEGAL IMPLICATIONS:
   - Legal significance of findings
   - Potential compliance issues
   - Risk factors

4. RECOMMENDED ACTIONS:
   - Next steps for investigation
   - Areas requiring deeper analysis
   - Mitigation strategies

Maintain professional, objective tone suitable for court proceedings.
Focus on forensic accuracy and legal defensibility."""
```

### Deterministic Analysis

Executive summary uses **temperature=0** (default for Responses API) for reproducible results.

## Validation & Compliance

### Input Validation
- Case ID must be non-empty string
- Case must have at least one piece of evidence
- All evidence must have valid analysis results

### Output Validation
All outputs are Pydantic-validated:

```python
# CaseSummary validates all fields
case_summary = CaseSummary(
    case_id=case_id,
    generation_timestamp=datetime.now(),
    evidence_count=len(evidence_summaries),
    evidence_types=evidence_types,
    evidence_summaries=evidence_summaries,  # List[EvidenceSummary]
    correlation_result=correlation_result,  # CorrelationAnalysis
    overall_assessment=overall_assessment,  # Dict[str, Any]
    executive_summary=executive_summary    # Optional[str]
)
```

### Chain of Custody
Summary generation does not modify evidence, so no chain of custody events are added. However, correlation analysis events are tracked by CorrelationAnalyzer.

## Error Handling

### Common Errors

| Error | Cause | Recovery Strategy |
|-------|-------|-------------------|
| `ValueError` | No evidence for case | Verify case ID, check ingestion |
| `JSONDecodeError` | Corrupted analysis file | Re-analyze evidence with --force |
| `OpenAI APIError` | AI summary failed | Check API key, rate limits, retry |
| `KeyError` | Missing analysis fields | Re-analyze evidence (schema change) |

### Error Handling Pattern

```python
try:
    case_summary = summary_gen.generate_case_summary("CASE-001")
    print(f"✅ Summary generated: {case_summary.evidence_count} evidence")
except ValueError as e:
    print(f"❌ No evidence for case: {e}")
except Exception as e:
    print(f"❌ Summary generation failed: {e}")
```

### Logging

Summary operations use emoji-prefixed output:
- `📊` - Summary operations
- `🔗` - Correlation operations
- `✅` - Success
- `⚠️` - Warning (AI summary failed, using basic summary)
- `❌` - Error

## Performance Considerations

### Time Complexity
- **Evidence summary extraction**: O(n) where n = number of evidence
- **Correlation analysis**: O(n²) for entity matching (via CorrelationAnalyzer)
- **Overall assessment**: O(n) for aggregation
- **AI executive summary**: O(1) API call

### Space Complexity
- **CaseSummary object**: ~5-20 KB (depends on evidence count)
- **JSON export**: ~10-50 KB (formatted with indentation)
- **Text report**: ~5-20 KB

### API Cost Impact

| Component | Tokens (avg) | Cost (per 1M tokens) | Avg Cost |
|-----------|--------------|----------------------|----------|
| Executive Summary | ~3,000 input + 800 output | $2.50 / $10.00 | ~$0.015 |

**Example:** Generating summary for 20-evidence case costs approximately $0.015.

### Optimization Notes
- Correlation analysis is cached (one-time per case)
- Evidence summaries are extracted once (from existing analysis)
- AI summary is optional (can disable if not needed)
- JSON export uses streaming (efficient for large cases)

## Storage & Persistence

### Output Formats

**1. JSON Export** (`export_summary_to_json()`):
```
data/packages/CASE-001-summary.json
```

**2. Text Report** (`format_summary_report()`):
```
data/packages/CASE-001-report.txt
```

**3. Correlation Results**:
```
data/storage/derived/correlations/CASE-001-correlation.json
```

### JSON Schema

```json
{
  "case_id": "CASE-001",
  "generation_timestamp": "2025-10-05T14:30:00.123456Z",
  "evidence_count": 10,
  "evidence_types": ["document", "email", "image"],
  "evidence_summaries": [
    {
      "sha256": "2401112d...",
      "evidence_type": "document",
      "filename": "contract.pdf",
      "file_size": 102400,
      "analysis_confidence": 0.92,
      "key_findings": [...],
      "legal_significance": "high",
      "risk_flags": ["retaliation"]
    }
  ],
  "correlation_analysis": {
    "entity_correlations": [...],
    "timeline_events": [...],
    "legal_patterns": {...},
    "temporal_sequences": [...],
    "timeline_gaps": [...]
  },
  "overall_assessment": {
    "overall_confidence": 0.88,
    "total_risk_flags": 15,
    "unique_risk_flags": 5,
    "overall_legal_significance": "high",
    "entity_correlations_found": 12,
    "timeline_events_count": 25
  },
  "executive_summary": "This case involves..."
}
```

## Testing

### Unit Tests

```python
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage

def test_generate_case_summary():
    """Test case summary generation."""
    # Setup: Ingest and analyze evidence
    storage = EvidenceStorage()
    # ... (ingest and analyze test evidence)

    # Generate summary
    summary_gen = SummaryGenerator(storage, openai_client=None)
    case_summary = summary_gen.generate_case_summary("TEST-001")

    # Verify
    assert case_summary.case_id == "TEST-001"
    assert case_summary.evidence_count > 0
    assert len(case_summary.evidence_summaries) == case_summary.evidence_count
    assert case_summary.overall_assessment is not None

def test_export_summary_to_json():
    """Test JSON export."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "summary.json"

        # Generate and export
        case_summary = summary_gen.generate_case_summary("TEST-001")
        success = summary_gen.export_summary_to_json(case_summary, output_path)

        # Verify
        assert success
        assert output_path.exists()

        # Validate JSON
        data = json.loads(output_path.read_text())
        assert data["case_id"] == "TEST-001"
```

### Integration Tests

```bash
# Full pipeline test
./quick-start.sh data/cases/TEST-CASE TEST-CASE

# Verify summary
uv run evidence-toolkit correlate --case-id TEST-CASE
```

### Test Coverage
- Summary generation: ✅ Covered
- Evidence extraction: ✅ Covered
- Overall assessment: ✅ Covered
- JSON export: ✅ Covered
- Text report: ✅ Covered
- AI executive summary: ⚠️ Partial (needs mocking)

## Dependencies

### Internal Dependencies
- `evidence_toolkit.core.storage.EvidenceStorage` - Storage access
- `evidence_toolkit.core.models.CorrelationAnalysis` - Correlation results
- `evidence_toolkit.core.models.EvidenceSummary` - Evidence summary model
- `evidence_toolkit.core.models.CaseSummary` - Case summary model
- `evidence_toolkit.analyzers.correlation.CorrelationAnalyzer` - Cross-evidence correlation
- `evidence_toolkit.domains.legal_config.EXECUTIVE_SUMMARY_PROMPT` - AI prompt

### External Dependencies
- `openai` - AI executive summary (optional)
- `pydantic` - Model validation
- `json` - JSON serialization

## CLI Integration

```bash
# Generate correlation and summary
uv run evidence-toolkit correlate --case-id CASE-001

# Export summary to JSON
uv run evidence-toolkit correlate --case-id CASE-001 --export-json summary.json

# Generate text report
uv run evidence-toolkit correlate --case-id CASE-001 --export-report report.txt
```

**CLI Implementation** (`cli.py`):
```python
@app.command()
def correlate(
    case_id: str,
    export_json: Optional[Path] = None,
    export_report: Optional[Path] = None
):
    """Generate case correlation and summary."""
    storage = EvidenceStorage()
    openai_client = OpenAI() if os.getenv("OPENAI_API_KEY") else None

    summary_gen = SummaryGenerator(storage, openai_client)
    case_summary = summary_gen.generate_case_summary(case_id)

    if export_json:
        summary_gen.export_summary_to_json(case_summary, export_json)
        print(f"📄 JSON exported: {export_json}")

    if export_report:
        report_text = summary_gen.format_summary_report(case_summary)
        export_report.write_text(report_text)
        print(f"📄 Report exported: {export_report}")

    # Print summary to console
    print(summary_gen.format_summary_report(case_summary))
```

## Migration Notes

### v2.0 → v3.0 Changes

**Old (v2.0):**
```python
# Dataclass models
@dataclass
class EvidenceSummary:
    sha256: str
    # ... (no validation)

@dataclass
class CaseSummary:
    case_id: str
    # ... (no validation)
```

**New (v3.0/v3.1):**
```python
# Pydantic models
class EvidenceSummary(BaseModel):
    sha256: str
    # ... (full Pydantic validation)

class CaseSummary(BaseModel):
    case_id: str
    # ... (full Pydantic validation)
```

**Breaking Changes:**
- Models converted from @dataclass to Pydantic (v3.1)
- CorrelationAnalysis now Pydantic (v3.0)
- Email analysis uses full `EmailThreadAnalysis` with participants (v3.1)
- Legal patterns added to correlation (v3.1)

**v3.1 Enhancements Summary:**

1. **CorrelationAnalyzer Integration:**
   - Now receives `openai_client` for AI-powered pattern detection
   - Detects contradictions and corroborations across evidence
   - Identifies temporal sequences and timeline gaps

2. **Email Participant Handling:**
   - Extracts participant data from full `EmailThreadAnalysis` model
   - Preserves participant metadata (name, email, role, interaction timestamps)
   - Enables cross-evidence participant matching in correlation

3. **Enhanced Correlation Results:**
   - `legal_patterns`: AI-detected contradictions and corroboration
   - `temporal_sequences`: Event patterns and sequences
   - `timeline_gaps`: Identified gaps requiring investigation

## Future Considerations

### Planned Enhancements
- **Incremental updates**: Update summary without full regeneration
- **Comparative analysis**: Compare summaries across cases
- **Custom templates**: User-defined report formats
- **Interactive reports**: HTML/PDF with visualizations
- **Summary versioning**: Track summary changes over time

### Known Limitations
- Large cases (>1000 evidence) may have slow correlation
- AI summary limited to ~3000 tokens context (may truncate)
- No partial summary support (all-or-nothing)
- Text report format is fixed (not customizable)

### Technical Debt
- Some duplicate logic in evidence extraction
- Hard-coded report format (should be templatable)
- AI context building could be more efficient

## Examples

### Example 1: Basic Summary Generation
```python
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage
from openai import OpenAI

storage = EvidenceStorage()
openai_client = OpenAI()

summary_gen = SummaryGenerator(storage, openai_client)
case_summary = summary_gen.generate_case_summary("CASE-001")

print(f"Case: {case_summary.case_id}")
print(f"Evidence: {case_summary.evidence_count}")
print(f"Correlations: {len(case_summary.correlation_result.entity_correlations)}")
print(f"\nExecutive Summary:\n{case_summary.executive_summary}")
```

### Example 2: Export to Multiple Formats
```python
from pathlib import Path
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()
summary_gen = SummaryGenerator(storage)

case_summary = summary_gen.generate_case_summary("CASE-001")

# JSON export
summary_gen.export_summary_to_json(
    case_summary,
    Path("data/packages/CASE-001-summary.json")
)

# Text report
report_text = summary_gen.format_summary_report(case_summary)
Path("data/packages/CASE-001-report.txt").write_text(report_text)

print("✅ Summary exported to JSON and text formats")
```

### Example 3: Summary Without AI (Graceful Degradation)
```python
from evidence_toolkit.pipeline import SummaryGenerator
from evidence_toolkit.core.storage import EvidenceStorage

storage = EvidenceStorage()

# No OpenAI client - basic summary only
summary_gen = SummaryGenerator(storage, openai_client=None)
case_summary = summary_gen.generate_case_summary("CASE-001")

# Still get correlation analysis and overall assessment
print(f"Evidence: {case_summary.evidence_count}")
print(f"Overall significance: {case_summary.overall_assessment['overall_legal_significance']}")
print(f"Entity correlations: {len(case_summary.correlation_result.entity_correlations)}")

# No AI executive summary
assert case_summary.executive_summary is None
```

---

**This documentation provides complete reference for the case summary generator, covering all summary generation logic, correlation analysis, AI integration, and export capabilities in Evidence Toolkit v3.0.**
