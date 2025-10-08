# Documentation: Legal Domain Configuration

## Overview

The Legal Domain Configuration module (`src/evidence_toolkit/domains/legal_config.py`) centralizes all legal-specific prompts, taxonomies, and settings for the Evidence Toolkit. This file serves as the single source of truth for legal domain knowledge, making it easy to maintain, update, and extend the system's legal capabilities.

All AI analysis prompts used by the Evidence Toolkit's analyzers are defined here, ensuring consistency across document analysis, email analysis, image analysis, cross-evidence correlation, and executive summary generation.

## Purpose & Scope

### What It Does
- Defines forensic-quality AI prompts for legal evidence analysis
- Specifies entity extraction requirements (people, organizations, dates, legal terms)
- Establishes legal significance taxonomies (critical/high/medium/low)
- Defines risk flag categories (harassment, retaliation, discrimination, etc.)
- Provides domain-specific instructions for AI models
- Centralizes all legal terminology and classification schemes

### What It Does NOT Do
- Does NOT perform analysis (prompts are consumed by analyzers)
- Does NOT contain business logic (pure configuration data)
- Does NOT make analysis decisions (AI models use these as instructions)
- Does NOT store analysis results (only defines the framework)

### Why This Exists
Centralized domain configuration provides:
1. **Maintainability**: Update prompts in one place
2. **Consistency**: Same legal framework across all analyzers
3. **Extensibility**: Easy to add new domains (medical, financial, etc.)
4. **Version Control**: Track prompt evolution over time
5. **Testing**: Easy to test prompt variations

## Configuration Elements

### 1. Document Analysis Prompt

**Purpose**: Instructs AI to analyze legal documents with forensic precision

**Key Requirements**:
- Legal significance-focused summary
- Entity extraction with confidence scores
- Entity relationships (who communicated with whom)
- Quoted text for legally significant statements
- Associated events for temporal entities
- Document classification (email, letter, contract, filing)
- Sentiment analysis (hostile, neutral, professional)
- Risk flag identification

**Special Instructions**:
```python
DOCUMENT_ANALYSIS_PROMPT = """You are a forensic document analyzer for legal evidence processing.

Entity Extraction Requirements:
- **Relationship**: connections to other entities (e.g., "sent email to Rachel Hemmings")
- **Quoted Text**: exact verbatim quotes for legally significant statements
- **Associated Event**: for date entities, specify what happened (e.g., "complaint filed")

Confidence Scoring:
- Be conservative with confidence - only use >0.9 for extremely clear cases
"""
```

**Used By**: `DocumentAnalyzer` (`analyzers/document.py`)

### 2. Email Analysis Prompt

**Purpose**: Instructs AI to analyze email threads with focus on communication patterns

**Key Requirements**:
- Thread summary focusing on communication evolution
- Participant analysis with organizational hierarchy
- Message count per participant
- Deference score (0.0=dominant, 0.5=neutral, 1.0=deferential)
- Dominant topics per participant
- Communication pattern assessment (professional, escalating, hostile, retaliatory)
- Sentiment progression across thread
- Escalation detection (tone changes, authority escalation, new recipients)
- Timeline reconstruction

**Special Instructions**:
```python
EMAIL_ANALYSIS_PROMPT = """You are a forensic email analyzer for legal evidence processing.

Deference Scoring:
- Dominant (0.0-0.3): Directive language, commands, control of conversation
- Neutral (0.4-0.6): Collaborative, balanced participation, mutual respect
- Deferential (0.7-1.0): Seeking approval, apologetic, yielding to others

Focus Areas:
- Workplace investigation patterns: retaliation sequences, escalation to management
- Policy violations, harassment patterns, hostile communications, power imbalances
"""
```

**Used By**: `EmailAnalyzer` (`analyzers/email.py`)

### 3. Image Analysis Prompt

**Purpose**: Instructs AI Vision API to extract factual observations from images

**Key Requirements**:
- Visual scene and objects description
- OCR for visible text
- People identification (if present)
- Timestamps or identifying markers
- Potential evidential value assessment
- Quality issues or uncertainties

**Special Instructions**:
```python
IMAGE_ANALYSIS_PROMPT = """You are assisting a legal evidence analyst.

Be precise, objective, and note any quality issues or uncertainties.
Provide factual, non-speculative observations.
"""
```

**Used By**: `ImageAnalyzer` (`analyzers/image.py`)

### 4. Correlation Pattern Analysis Prompt (v3.1)

**Purpose**: Instructs AI to detect patterns across multiple evidence pieces

**Key Requirements**:
- Contradiction detection (factual, temporal, attribution)
- Corroboration assessment (weak/moderate/strong)
- Evidence gap identification (missing witnesses, documentation, unexplained absences)
- Pattern summary with legal significance

**Special Instructions**:
```python
CORRELATION_PATTERN_PROMPT = """You are analyzing cross-evidence correlation data.

Contradictions:
- Factual: Different facts about same event
- Temporal: Different dates/times for same event
- Attribution: Different sources for same statement
- Severity: 0.0-1.0 (higher = more serious conflict)

Corroboration Strength:
- Weak: 1 source
- Moderate: 2-3 sources
- Strong: 4+ sources

Focus on workplace investigation patterns: retaliation sequences, credibility assessment,
evidence tampering indicators, policy compliance.
"""
```

**Used By**: `CorrelationAnalyzer.detect_patterns_with_ai()` (`analyzers/correlation.py`)

### 5. Executive Summary Prompts (v3.2 - Case Type Support)

**Purpose**: Instructs AI to generate comprehensive case summaries tailored to specific legal case types

**Available Case Types**:
- **`generic`**: General legal matters, investigations, compliance reviews (default)
- **`workplace`/`employment`**: Employment disputes, workplace investigations, HR matters
- **`contract`**: Commercial disputes, contractual breaches, B2B conflicts

**Key Requirements** (all types):
- Executive summary (2-3 paragraphs)
- Key findings (3-5 most important discoveries)
- Legal implications (risks, compliance issues, procedural concerns)
- Recommended actions (next steps for legal strategy)
- Risk assessment (low/medium/high/critical)
- Confidence score (0.0-1.0)

**Workplace-Specific Instructions** (v3.2):
```python
EXECUTIVE_SUMMARY_PROMPT_WORKPLACE = """You are analyzing a WORKPLACE DISPUTE / EMPLOYMENT LAW case.

Focus on:
- Employment law issues (unfair dismissal, discrimination, harassment, whistleblowing)
- Claimant vs. Respondent identification
- Grievance escalation timeline
- ACAS Code compliance and procedural fairness
- Protected characteristics (Equality Act 2010)
- Constructive dismissal risk (breach of trust and confidence)
- Witness credibility and corroboration
"""
```

**Case Type Registry** (v3.2):
```python
EXECUTIVE_SUMMARY_PROMPTS = {
    'generic': EXECUTIVE_SUMMARY_PROMPT_GENERIC,
    'workplace': EXECUTIVE_SUMMARY_PROMPT_WORKPLACE,
    'employment': EXECUTIVE_SUMMARY_PROMPT_WORKPLACE,  # Alias
    'contract': EXECUTIVE_SUMMARY_PROMPT_CONTRACT,
}
```

**Used By**: `SummaryGenerator.generate_executive_summary()` (`pipeline/summary.py`)

### 6. Entity Matching Prompt (v3.2 - AI Entity Resolution)

**Purpose**: Instructs AI to determine if two entity names from different evidence pieces refer to the same real-world person or organization

**Use Case**: Resolves ambiguous entity matches missed by string canonicalization (e.g., "Paul" vs "Paul Boucherat", "Bob" vs "Robert Smith")

**Key Requirements**:
- Name comparison (full name vs. informal/first-name usage, nicknames, initials)
- Context analysis (same organization, role, contact details, timeframe)
- Common name handling (John, Paul, Sarah - require unique identifiers)
- Conservative confidence scoring (forensic caution - false positives worse than false negatives)
- Structured reasoning output (supporting signals, conflicting signals, confidence)

**Special Instructions**:
```python
ENTITY_MATCH_PROMPT = """You are an entity resolution specialist for legal evidence analysis.

Critical - Common Name Rule:
- For extremely common first names alone (John, Paul, Michael, Sarah, etc.):
  * Require STRONG unique identifiers (email address, phone, employee ID) for match
  * Same organization alone is INSUFFICIENT (companies have multiple Johns/Sarahs)
  * Default to is_same_entity: false unless surname or unique ID present

Confidence Scoring:
- 0.95+: Full name exact match + unique identifier + no conflicts
- 0.85-0.95: Full name match + 2+ supporting signals + no conflicts
- 0.70-0.85: Partial name match + 2+ supporting signals + no conflicts
- 0.50-0.70: First name only + strong unique signal + no conflicts
- 0.30-0.50: Ambiguous (mixed signals)

Be conservative. In legal contexts, false positives are worse than false negatives.
"""
```

**Used By**: `CorrelationAnalyzer._ai_match_entities()` (`analyzers/correlation.py`) when `--ai-resolve` flag is used

**Response Format**: `EntityMatchResult` Pydantic model with:
- `is_same_entity`: boolean (match decision)
- `confidence`: float 0.0-1.0
- `reasoning`: string (explanation of decision)
- `supporting_signals`: list of strings (evidence for match)
- `conflicting_signals`: list of strings (evidence against match)

**Example Usage**:
```bash
# Enable AI entity resolution for correlation analysis
uv run evidence-toolkit correlate --case-id MY-CASE --ai-resolve
```

### 7. Critical Risk Flags

**Purpose**: Define risk categories that trigger temporal pattern detection

**Categories**:
```python
CRITICAL_RISK_FLAGS = {
    'retaliation',    # Actions taken against whistleblowers/complainants
    'harassment',     # Hostile or unwanted behavior
    'discrimination', # Protected class violations
    'threatening'     # Threatening language or behavior
}
```

**Used By**:
- `CorrelationAnalyzer.detect_temporal_patterns()` (`analyzers/correlation.py`)
- Risk-based sorting and highlighting in client packages

## Usage

### Basic Usage (Analyzer Integration)

```python
# Example: DocumentAnalyzer using DOCUMENT_ANALYSIS_PROMPT
from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Use prompt in API call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": DOCUMENT_ANALYSIS_PROMPT},
        {"role": "user", "content": f"Analyze this document:\n\n{document_text}"}
    ],
    temperature=0.0  # Deterministic for forensic quality
)
```

### Advanced Usage (Custom Prompts)

```python
# Example: Adding domain-specific instructions
from evidence_toolkit.domains.legal_config import EMAIL_ANALYSIS_PROMPT

# Customize prompt for specific case type
custom_prompt = EMAIL_ANALYSIS_PROMPT + """

Additional focus for this case:
- Union organizing activity
- Management response to union activity
- Potential labor law violations
"""

# Use customized prompt
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": custom_prompt},
        {"role": "user", "content": email_thread}
    ]
)
```

### Risk Flag Usage

```python
# Example: CorrelationAnalyzer using CRITICAL_RISK_FLAGS
from evidence_toolkit.domains.legal_config import CRITICAL_RISK_FLAGS
from evidence_toolkit.core.models import UnifiedAnalysis

def detect_temporal_patterns(analyses: List[UnifiedAnalysis]):
    for analysis in analyses:
        # Check if any critical risks detected
        if hasattr(analysis, 'risk_flags'):
            critical_risks = set(analysis.risk_flags) & CRITICAL_RISK_FLAGS
            if critical_risks:
                # Trigger temporal pattern detection
                flag_temporal_pattern(analysis, critical_risks)
```

## Architecture

### Module Structure

```
src/evidence_toolkit/
├── domains/
│   ├── __init__.py
│   └── legal_config.py     # THIS MODULE
│
├── analyzers/
│   ├── document.py         # Uses DOCUMENT_ANALYSIS_PROMPT
│   ├── email.py            # Uses EMAIL_ANALYSIS_PROMPT
│   ├── image.py            # Uses IMAGE_ANALYSIS_PROMPT
│   └── correlation.py      # Uses CORRELATION_PATTERN_PROMPT, CRITICAL_RISK_FLAGS
│
└── pipeline/
    └── package.py          # Uses EXECUTIVE_SUMMARY_PROMPT
```

### Data Flow

```
Legal Config (Prompts)
        ↓
Analyzers (OpenAI API calls)
        ↓
Analysis Results (Pydantic models)
        ↓
Storage (JSON files)
```

### Extensibility

The module is designed for easy extension:

```python
# Future: Add medical domain configuration
# src/evidence_toolkit/domains/medical_config.py

MEDICAL_DOCUMENT_PROMPT = """You are a medical evidence analyst..."""
MEDICAL_IMAGE_PROMPT = """Analyze this medical image..."""
HIPAA_RISK_FLAGS = {'phi_exposure', 'unauthorized_access', ...}
```

## Configuration Reference

### Document Analysis Configuration

| Element | Type | Purpose |
|---------|------|---------|
| Summary | Required | Concise summary focusing on legal significance |
| Entity Extraction | Required | People, orgs, dates, legal terms with confidence |
| Entity Relationships | Optional | Connections between entities (who contacted whom) |
| Quoted Text | Optional | Verbatim legally significant statements |
| Associated Events | Optional | Events associated with temporal entities |
| Document Classification | Required | Email, letter, contract, or filing |
| Sentiment Analysis | Required | Hostile, neutral, or professional |
| Legal Significance | Required | Critical, high, medium, or low |
| Risk Flags | Required | All applicable risk categories |

### Email Analysis Configuration

| Element | Type | Purpose |
|---------|------|---------|
| Thread Summary | Required | Communication evolution and legal significance |
| Participant Analysis | Required | Organizational hierarchy, message counts, deference |
| Dominant Topics | Required | Topics each participant drove |
| Communication Pattern | Required | Professional, escalating, hostile, retaliatory |
| Sentiment Progression | Required | 0.0-1.0 scale across thread |
| Escalation Detection | Required | Tone changes, authority escalation, new recipients |
| Legal Significance | Required | Critical, high, medium, or low |
| Risk Assessment | Required | All applicable risk categories |
| Timeline Reconstruction | Required | Chronological event summary |

### Image Analysis Configuration

| Element | Type | Purpose |
|---------|------|---------|
| Visual Scene | Required | Objects, setting, context |
| OCR Text | Optional | Any visible text extracted |
| People | Optional | People present (if identifiable) |
| Timestamps | Optional | Visible timestamps or identifying markers |
| Evidential Value | Required | Potential legal significance |
| Quality Issues | Required | Any uncertainties or quality problems |

### Correlation Pattern Configuration

| Element | Type | Purpose |
|---------|------|---------|
| Contradictions | Optional | Conflicting statements (factual, temporal, attribution) |
| Corroboration | Optional | Evidence supporting same claims (weak/moderate/strong) |
| Evidence Gaps | Optional | Missing witnesses, documentation, unexplained absences |
| Pattern Summary | Required | Overview of findings and legal significance |
| Confidence | Required | 0.0-1.0 confidence in pattern analysis |

### Executive Summary Configuration

| Element | Type | Purpose |
|---------|------|---------|
| Executive Summary | Required | 2-3 paragraph overview |
| Key Findings | Required | 3-5 most important discoveries |
| Legal Implications | Required | Risks, compliance issues, procedural concerns |
| Recommended Actions | Required | Next steps for legal strategy |
| Risk Assessment | Required | Low/medium/high/critical with justification |
| Confidence | Required | 0.0-1.0 overall confidence |

## Prompt Engineering Best Practices

### 1. Conservative Confidence Scoring

**Instruction**: "Be conservative with confidence - only use >0.9 for extremely clear cases"

**Rationale**: Legal evidence requires high accuracy. False positives are costly.

**Implementation**:
```python
# Prompt guidance
"Provide confidence scores (0.0-1.0) for all extractions.
Be conservative with confidence - only use >0.9 for extremely clear cases."
```

### 2. Structured Output Requirements

**Instruction**: Clear output structure in prompts

**Rationale**: Pydantic validation requires consistent JSON structure

**Implementation**:
```python
# Response schema defined in prompts
"""
Entity Extraction Requirements:
- **Relationship**: connections to other entities
- **Quoted Text**: exact verbatim quotes
- **Associated Event**: for dates, specify what happened
"""
```

### 3. Domain-Specific Focus

**Instruction**: "Focus on workplace investigation patterns: retaliation sequences, escalation..."

**Rationale**: Guide AI to relevant legal patterns

**Implementation**:
```python
# Domain guidance in prompts
"Focus on workplace investigation patterns: retaliation sequences,
escalation to management, policy violations, harassment patterns,
hostile communications, power imbalances."
```

### 4. Objective Tone

**Instruction**: "Be precise, objective, and note any quality issues or uncertainties"

**Rationale**: Forensic analysis must be factual, not speculative

**Implementation**:
```python
# Tone guidance
"Be objective, evidence-based, and suitable for legal review."
"Provide factual, non-speculative observations."
```

### 5. Forensic Completeness

**Instruction**: Comprehensive extraction requirements

**Rationale**: Missing data cannot be recovered later

**Implementation**:
```python
# Extraction completeness
"""
Identify:
1. **Summary**: Legal significance and key points
2. **Entity Extraction**: People, orgs, dates, legal terms
3. **Document Classification**: Email, letter, contract, filing
4. **Sentiment Analysis**: Hostile, neutral, professional
5. **Legal Significance**: Critical, high, medium, low
6. **Risk Flags**: All applicable categories
"""
```

## Validation & Compliance

### Prompt Validation

Prompts should be validated for:
1. **Clarity**: Unambiguous instructions
2. **Completeness**: All required fields specified
3. **Consistency**: Same terminology across prompts
4. **Forensic Quality**: Conservative, objective tone

### Output Validation

All AI responses are validated against Pydantic models:

```python
# Example: DocumentAnalysis model validates prompt output
class DocumentAnalysis(BaseModel):
    summary: str
    entities: List[Entity]
    document_type: str
    sentiment: str
    legal_significance: str
    risk_flags: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
```

If AI output doesn't match schema → Validation error → Analysis fails

### Chain of Custody

Prompt version tracking:
- Prompts are versioned in git (part of codebase)
- Analysis results include prompt hash (future enhancement)
- Re-analysis can detect prompt changes

## Error Handling

### Missing Prompts

If prompt not defined:
```python
from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT

if not DOCUMENT_ANALYSIS_PROMPT:
    raise ValueError("DOCUMENT_ANALYSIS_PROMPT not defined in legal_config.py")
```

### Invalid Prompt Configuration

If prompt doesn't produce valid output:
```python
try:
    analysis = DocumentAnalysis.model_validate(ai_response)
except ValidationError as e:
    # Prompt produced invalid output structure
    logger.error(f"Prompt output validation failed: {e}")
    raise
```

## Performance Considerations

### Prompt Length

Current prompt lengths:
- `DOCUMENT_ANALYSIS_PROMPT`: ~500 tokens
- `EMAIL_ANALYSIS_PROMPT`: ~600 tokens
- `IMAGE_ANALYSIS_PROMPT`: ~100 tokens
- `CORRELATION_PATTERN_PROMPT`: ~400 tokens
- `EXECUTIVE_SUMMARY_PROMPT`: ~300 tokens

**Cost Impact**: System prompts are sent with every API call
- Longer prompts = higher input token costs
- Trade-off: Comprehensiveness vs. cost

### Temperature Setting

All analyzers use `temperature=0.0` for deterministic forensic analysis:

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.0,  # Deterministic output
    ...
)
```

**Rationale**: Legal analysis must be reproducible and consistent

## Testing

### Unit Tests

Prompt validation testing:

```python
def test_document_prompt_defined():
    from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT
    assert DOCUMENT_ANALYSIS_PROMPT is not None
    assert len(DOCUMENT_ANALYSIS_PROMPT) > 0
    assert "forensic" in DOCUMENT_ANALYSIS_PROMPT.lower()

def test_critical_risk_flags():
    from evidence_toolkit.domains.legal_config import CRITICAL_RISK_FLAGS
    assert 'retaliation' in CRITICAL_RISK_FLAGS
    assert 'harassment' in CRITICAL_RISK_FLAGS
    assert 'discrimination' in CRITICAL_RISK_FLAGS
```

### Integration Tests

Prompt output validation:

```python
def test_document_prompt_produces_valid_output(openai_client):
    from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT
    from evidence_toolkit.core.models import DocumentAnalysis

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": DOCUMENT_ANALYSIS_PROMPT},
            {"role": "user", "content": "Test document text"}
        ]
    )

    # Should produce valid DocumentAnalysis
    analysis = DocumentAnalysis.model_validate_json(response.choices[0].message.content)
    assert analysis.summary
    assert analysis.legal_significance in ['critical', 'high', 'medium', 'low']
```

## Dependencies

### Internal Dependencies

None - pure configuration module

### External Dependencies

None - consumed by other modules:
- `analyzers/document.py`
- `analyzers/email.py`
- `analyzers/image.py`
- `analyzers/correlation.py`
- `pipeline/package.py`

## Related Components

### Downstream Components (Consumers)

1. **DocumentAnalyzer** (`analyzers/document.py`)
   - Imports: `DOCUMENT_ANALYSIS_PROMPT`
   - Uses in: OpenAI API calls for document analysis

2. **EmailAnalyzer** (`analyzers/email.py`)
   - Imports: `EMAIL_ANALYSIS_PROMPT`
   - Uses in: OpenAI API calls for email thread analysis

3. **ImageAnalyzer** (`analyzers/image.py`)
   - Imports: `IMAGE_ANALYSIS_PROMPT`
   - Uses in: OpenAI Vision API calls for image analysis

4. **CorrelationAnalyzer** (`analyzers/correlation.py`)
   - Imports: `CORRELATION_PATTERN_PROMPT`, `CRITICAL_RISK_FLAGS`
   - Uses in: Pattern detection and temporal analysis

5. **SummaryGenerator** (`pipeline/package.py`)
   - Imports: `EXECUTIVE_SUMMARY_PROMPT`
   - Uses in: Executive summary generation for client packages

### Configuration Files

- **CLAUDE.md**: Developer guidance
- **V3_ARCHITECTURE.md**: Architecture documentation
- **README.md**: User documentation

## Migration Notes

### v2.0 → v3.0 Changes

**Centralization**:
- v2.0: Prompts scattered across analyzer files
- v3.0: All prompts centralized in `domains/legal_config.py`

**New Features (v3.1)**:
- `CORRELATION_PATTERN_PROMPT`: AI-powered pattern detection
- `CRITICAL_RISK_FLAGS`: Temporal pattern trigger configuration

**Enhanced Instructions**:
- Added entity relationship extraction
- Added quoted text extraction for legal statements
- Added associated events for temporal entities
- Added deference scoring for email participants
- Added contradiction/corroboration detection

**Breaking Changes**:
- Prompt import paths changed:
  - Old: `from document_analyzer.document_analyzer_core import PROMPT`
  - New: `from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT`

## Future Considerations

### Planned Enhancements

1. **Multi-Domain Support**
   ```python
   # Future structure
   domains/
   ├── legal_config.py      # Current
   ├── medical_config.py    # Healthcare evidence
   ├── financial_config.py  # Financial fraud
   └── corporate_config.py  # Corporate compliance
   ```

2. **Prompt Versioning**
   ```python
   DOCUMENT_ANALYSIS_PROMPT_V1 = "..."
   DOCUMENT_ANALYSIS_PROMPT_V2 = "..."  # Enhanced version

   # Track which version was used for each analysis
   class UnifiedAnalysis(BaseModel):
       prompt_version: str = "v2"
       ...
   ```

3. **Dynamic Prompt Templates**
   ```python
   # Template with case-specific customization
   def get_document_prompt(case_type: str) -> str:
       base_prompt = DOCUMENT_ANALYSIS_PROMPT
       if case_type == "employment":
           return base_prompt + EMPLOYMENT_SPECIFIC_GUIDANCE
       elif case_type == "contract":
           return base_prompt + CONTRACT_SPECIFIC_GUIDANCE
       return base_prompt
   ```

4. **Prompt A/B Testing**
   ```python
   # Compare prompt effectiveness
   DOCUMENT_PROMPT_EXPERIMENTAL = "..."

   def analyze_with_variant(text: str, variant: str = "stable"):
       prompt = DOCUMENT_ANALYSIS_PROMPT if variant == "stable" else DOCUMENT_PROMPT_EXPERIMENTAL
       # Track performance metrics
   ```

5. **Localization Support**
   ```python
   # Multi-language prompts
   PROMPTS = {
       'en': DOCUMENT_ANALYSIS_PROMPT_EN,
       'es': DOCUMENT_ANALYSIS_PROMPT_ES,
       'fr': DOCUMENT_ANALYSIS_PROMPT_FR
   }
   ```

### Known Limitations

1. **Single Domain**: Currently only legal domain supported
   - Mitigation: Add domains as needed
   - Future: Multi-domain configuration management

2. **Static Prompts**: Prompts cannot be customized at runtime
   - Mitigation: Edit `legal_config.py` and restart
   - Future: Config file or database-driven prompts

3. **No Prompt Testing Framework**: No automated prompt quality testing
   - Mitigation: Manual review of AI outputs
   - Future: Automated prompt evaluation suite

### Technical Debt

1. **Prompt Length Optimization**: Some prompts could be more concise
2. **Example-Based Prompts**: Could add few-shot examples for better accuracy
3. **Prompt Documentation**: Each prompt could include effectiveness metrics
4. **Version Control**: No formal prompt versioning system

## Examples

### Example 1: Custom Document Analyzer with Enhanced Prompt

```python
from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT
from openai import OpenAI

# Add case-specific guidance
custom_prompt = DOCUMENT_ANALYSIS_PROMPT + """

Additional focus for this sexual harassment case:
- Identify all mentions of physical contact or unwanted advances
- Track reporting chain: who reported to whom and when
- Flag any evidence of employer knowledge and inaction
- Note any evidence of retaliation against complainant
"""

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": custom_prompt},
        {"role": "user", "content": document_text}
    ],
    response_format=DocumentAnalysis,
    temperature=0.0
)

analysis = response.choices[0].message.parsed
```

### Example 2: Risk Flag Detection

```python
from evidence_toolkit.domains.legal_config import CRITICAL_RISK_FLAGS
from evidence_toolkit.core.models import UnifiedAnalysis

def analyze_case_risk(analyses: List[UnifiedAnalysis]) -> dict:
    """Analyze overall case risk based on critical flags."""
    risk_summary = {
        'total_evidence': len(analyses),
        'critical_evidence': 0,
        'risk_categories': set()
    }

    for analysis in analyses:
        if hasattr(analysis, 'risk_flags'):
            # Check for critical risks
            critical_risks = set(analysis.risk_flags) & CRITICAL_RISK_FLAGS
            if critical_risks:
                risk_summary['critical_evidence'] += 1
                risk_summary['risk_categories'].update(critical_risks)

    # Calculate risk percentage
    risk_summary['risk_percentage'] = (
        risk_summary['critical_evidence'] / risk_summary['total_evidence'] * 100
    )

    return risk_summary

# Usage
risk_report = analyze_case_risk(case_analyses)
print(f"Critical evidence: {risk_report['critical_evidence']}/{risk_report['total_evidence']}")
print(f"Risk categories: {', '.join(risk_report['risk_categories'])}")
```

### Example 3: Prompt Effectiveness Testing

```python
from evidence_toolkit.domains.legal_config import DOCUMENT_ANALYSIS_PROMPT
from evidence_toolkit.core.models import DocumentAnalysis
from openai import OpenAI

def test_prompt_quality(test_documents: List[str]) -> dict:
    """Test prompt effectiveness on sample documents."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    results = {
        'successful': 0,
        'failed': 0,
        'avg_confidence': 0.0,
        'avg_entities': 0.0
    }

    for doc in test_documents:
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": DOCUMENT_ANALYSIS_PROMPT},
                    {"role": "user", "content": doc}
                ],
                response_format=DocumentAnalysis,
                temperature=0.0
            )

            analysis = response.choices[0].message.parsed
            results['successful'] += 1
            results['avg_confidence'] += analysis.confidence
            results['avg_entities'] += len(analysis.entities)

        except Exception as e:
            results['failed'] += 1
            print(f"Prompt test failed: {e}")

    # Calculate averages
    if results['successful'] > 0:
        results['avg_confidence'] /= results['successful']
        results['avg_entities'] /= results['successful']

    return results

# Run quality test
test_docs = ["Document 1...", "Document 2...", "Document 3..."]
quality_report = test_prompt_quality(test_docs)
print(f"Success rate: {quality_report['successful']}/{len(test_docs)}")
print(f"Average confidence: {quality_report['avg_confidence']:.2f}")
print(f"Average entities extracted: {quality_report['avg_entities']:.1f}")
```

### Example 4: Multi-Domain Configuration (Future)

```python
# Future: Support for different evidence domains

# domains/medical_config.py
MEDICAL_DOCUMENT_PROMPT = """You are a medical evidence analyst for healthcare investigations.

Analyze medical records with focus on:
1. **Patient Information**: PHI handling and privacy compliance
2. **Medical Events**: Diagnoses, treatments, procedures
3. **Provider Actions**: Healthcare provider decisions and actions
4. **HIPAA Compliance**: Privacy and security violations
5. **Standard of Care**: Deviations from accepted medical practice
"""

HIPAA_RISK_FLAGS = {
    'phi_exposure',
    'unauthorized_access',
    'improper_disclosure',
    'security_breach'
}

# Usage in analyzer
from evidence_toolkit.domains import legal_config, medical_config

def get_domain_config(domain: str):
    if domain == 'legal':
        return legal_config
    elif domain == 'medical':
        return medical_config
    else:
        raise ValueError(f"Unknown domain: {domain}")

# Analyze with appropriate domain
config = get_domain_config('medical')
prompt = config.MEDICAL_DOCUMENT_PROMPT
risk_flags = config.HIPAA_RISK_FLAGS
```

### Example 5: Prompt Customization for Specific Case Types

```python
from evidence_toolkit.domains.legal_config import (
    DOCUMENT_ANALYSIS_PROMPT,
    EMAIL_ANALYSIS_PROMPT,
    CRITICAL_RISK_FLAGS
)

class CasePromptGenerator:
    """Generate customized prompts for specific case types."""

    @staticmethod
    def employment_discrimination(base_prompt: str) -> str:
        return base_prompt + """

        Additional focus for employment discrimination case:
        - Protected class mentions (race, gender, age, disability, religion)
        - Comparative treatment evidence (similarly situated employees)
        - Pretext indicators (shifting explanations, inconsistent application)
        - Pattern evidence (systemic vs. isolated incidents)
        """

    @staticmethod
    def whistleblower_retaliation(base_prompt: str) -> str:
        return base_prompt + """

        Additional focus for whistleblower retaliation case:
        - Protected activity (reporting illegal conduct, safety violations)
        - Employer knowledge of protected activity
        - Temporal proximity (timing between report and adverse action)
        - Comparative evidence (treatment before vs. after report)
        """

    @staticmethod
    def contract_dispute(base_prompt: str) -> str:
        return base_prompt + """

        Additional focus for contract dispute:
        - Contractual obligations and breaches
        - Performance deadlines and deliverables
        - Material terms and conditions
        - Damages and mitigation efforts
        """

# Usage
generator = CasePromptGenerator()
prompt = generator.employment_discrimination(DOCUMENT_ANALYSIS_PROMPT)

# Analyze with customized prompt
response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": document_text}
    ],
    response_format=DocumentAnalysis
)
```

---

This documentation provides comprehensive coverage of the Legal Domain Configuration module, from basic usage to advanced customization. It follows the Evidence Toolkit standards for clarity, completeness, and maintainability, with a focus on forensic-quality legal evidence analysis.
