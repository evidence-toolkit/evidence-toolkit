# Evidence Toolkit Integration & Enhancement Plan

## Overview

This plan outlines the enhancement and integration of Evidence Toolkit components with a focus on elevating document analysis capabilities to match the forensic-grade sophistication of the image analysis system. The approach emphasizes incremental improvements and similar patterns rather than forced unification.

## Current Architecture Analysis

### Document Evidence Analyzer (Strong Points)
- ✅ **Bulk Processing**: Efficient `analyze ./documents/` workflow for legal teams
- ✅ **Specialized Analysis**: Retaliation pattern detection with timeline analysis
- ✅ **Dual Mode Support**: Legacy directory mode + modern evidence-addressed mode
- ✅ **Evidence Integration**: Basic content-addressed storage via `EvidenceManager`

### Image Analysis System (Excellence Standard)
- ✅ **Forensic Grade**: Content-addressed storage with immutable chain of custody
- ✅ **Advanced AI**: OpenAI Responses API with structured JSON schemas
- ✅ **Deterministic Analysis**: Temperature=0 for legal reliability
- ✅ **Schema Validation**: All outputs validated against `evidence.v1.json`
- ✅ **Risk Assessment**: Comprehensive risk flags and confidence scoring

### Current Gaps
- ❌ **Analysis Sophistication**: Document analysis limited to word frequency vs AI-powered insights
- ❌ **API Inconsistency**: Chat Completions vs modern Responses API
- ❌ **Schema Validation**: Document analyzer lacks structured validation approach
- ❌ **Cross-referencing**: Mixed evidence cases (emails + attachments, incident reports + photos) lack connection tools

## Phase 1: Enhanced Document Analysis (Core Priority)

### 1.1 Upgrade to OpenAI Responses API
Replace basic word frequency analysis with structured AI insights:

```python
# Current: Basic word frequency
result = {
    "total_words": 1500,
    "unique_words": 300,
    "word_frequency": {"contract": 15, "termination": 8}
}

# Enhanced: Structured AI analysis
from pydantic import BaseModel
from typing import List, Literal

class DocumentEntity(BaseModel):
    name: str
    type: Literal["person", "organization", "date", "legal_term"]
    confidence: float
    context: str

class DocumentAnalysis(BaseModel):
    summary: str
    entities: List[DocumentEntity]
    document_type: Literal["email", "letter", "contract", "filing"]
    sentiment: Literal["hostile", "neutral", "professional"]
    legal_significance: Literal["critical", "high", "medium", "low"]
    risk_flags: List[Literal["pii", "privileged", "threatening", "deadline"]]
    confidence_overall: float

# OpenAI Responses API call
completion = client.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": LEGAL_ANALYSIS_PROMPT},
        {"role": "user", "content": document_text}
    ],
    response_format=DocumentAnalysis,
    temperature=0  # Deterministic for legal use
)
```

### 1.2 Document Schema Validation
Create `document.v1.json` schema following image analysis patterns:

```json
{
  "schema_version": "1.0.0",
  "case_id": "CASE123",
  "evidence": {
    "evidence_id": "doc_001",
    "sha256": "abc123...",
    "mime_type": "text/plain",
    "bytes": 2048,
    "ingested_at": "2024-09-25T14:30:00Z",
    "source_path": "/documents/email_001.txt"
  },
  "analyses": [{
    "analysis_id": "doc_abc123_20240925",
    "created_at": "2024-09-25T14:30:00Z",
    "model": {"name": "gpt-4o-2024-08-06", "revision": "2024-08-06"},
    "outputs": {
      "summary": "Employment termination email with hostile tone",
      "entities": [
        {"name": "John Doe", "type": "person", "confidence": 0.95, "context": "terminated employee"},
        {"name": "ACME Corp", "type": "organization", "confidence": 0.98, "context": "employer"}
      ],
      "document_type": "email",
      "sentiment": "hostile",
      "risk_flags": ["threatening", "deadline"],
      "legal_significance": "high"
    },
    "confidence_overall": 0.89
  }],
  "chain_of_custody": [
    {"ts": "2024-09-25T14:30:00Z", "actor": "analyst@firm.com", "action": "ingest"},
    {"ts": "2024-09-25T14:31:00Z", "actor": "analyst@firm.com", "action": "analysis"}
  ]
}
```

### 1.3 Maintain Bulk Processing Efficiency
Keep productive bulk workflows while adding AI insights:

```python
class EnhancedDocumentAnalyzer:
    def analyze_directory(self, docs_dir: Path, case_id: str) -> BatchResult:
        """Bulk analysis with AI insights - maintains speed while adding intelligence"""

        results = []
        for doc_path in docs_dir.rglob("*.txt"):
            # 1. Ingest with content addressing (optional)
            sha256 = self.evidence_manager.ingest_file(doc_path, case_id)

            # 2. AI analysis with rate limiting
            analysis = self._analyze_with_openai(doc_path.read_text())

            # 3. Schema validation
            validated_analysis = self._validate_analysis(analysis)

            # 4. Save with chain of custody
            self._save_analysis(sha256, validated_analysis, case_id)

            results.append(validated_analysis)
            time.sleep(0.1)  # Rate limiting

        return BatchResult(
            documents_processed=len(results),
            entities_extracted=sum(len(r.entities) for r in results),
            high_risk_documents=len([r for r in results if "threatening" in r.risk_flags])
        )
```

## Phase 2: Schema Validation & Chain of Custody

### 2.1 Add Schema Validation
Adopt image analyzer's validation approach for documents:

```python
# Schema validation similar to image analyzer
from jsonschema import validate
import json

class DocumentValidator:
    def __init__(self, schema_path: Path):
        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate_analysis(self, analysis_data: dict) -> bool:
        """Validate document analysis against schema"""
        try:
            validate(instance=analysis_data, schema=self.schema)
            return True
        except ValidationError as e:
            self.logger.error(f"Schema validation failed: {e}")
            return False

# CI validation script (similar to image analyzer)
def validate_all_document_analyses():
    """Validate all document analyses in evidence directory"""
    validator = DocumentValidator("schemas/document.v1.json")

    for analysis_file in Path("evidence/derived").rglob("document_analysis.v1.json"):
        with open(analysis_file) as f:
            data = json.load(f)

        if not validator.validate_analysis(data):
            print(f"FAILED: {analysis_file}")
            exit(1)

    print("All document analyses valid")
```

### 2.2 Chain of Custody for Documents
Add audit trails following image analyzer patterns:

```python
class DocumentChainOfCustody:
    """Chain of custody tracking for document analysis"""

    def record_event(self, sha256: str, action: str, actor: str, note: str = None):
        """Record custody event"""
        event = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "action": action,  # ingest, analysis, export
            "note": note
        }

        custody_file = self.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"

        if custody_file.exists():
            with open(custody_file) as f:
                chain = json.load(f)
        else:
            chain = []

        chain.append(event)

        with open(custody_file, 'w') as f:
            json.dump(chain, f, indent=2)

        # Also log to central log file
        self.log_event("custody_event", sha256=sha256, **event)

# Usage in document analyzer
self.custody.record_event(sha256, "analysis", "analyst@firm.com", "AI entity extraction")
```

## Phase 3: Cross-Evidence Integration (Future)

### 3.1 Acknowledge Cross-Modal Cases
Many legal cases involve both documents and images that need connection:

**Examples of mixed evidence cases:**
- Email chains with photo attachments
- Incident reports with scene photographs
- Contracts with signature images
- Text messages with embedded screenshots
- Legal filings referencing photographic exhibits

### 3.2 Simple Integration Approach
Rather than complex unified systems, use simple connection points:

```python
# Simple case-based organization
class CaseManager:
    def link_evidence(self, case_id: str, doc_sha256: str, img_sha256: str, relationship: str):
        """Create simple link between document and image evidence"""

        link = {
            "case_id": case_id,
            "document": doc_sha256,
            "image": img_sha256,
            "relationship": relationship,  # "attachment", "reference", "temporal"
            "created_at": datetime.utcnow().isoformat(),
            "confidence": 0.8
        }

        # Save to case links file
        links_file = Path(f"cases/{case_id}/evidence_links.json")
        self._append_link(links_file, link)

    def get_related_evidence(self, sha256: str) -> List[str]:
        """Find evidence related to this document or image"""
        # Simple file-based lookup for now
        # Could be upgraded to database later
        pass

# Usage
case_mgr = CaseManager()
case_mgr.link_evidence("CASE123", doc_hash, img_hash, "email_attachment")
```

### 3.3 Future Enhancement Paths
Once both tools are individually excellent, consider:

- **Shared Case IDs**: Both tools can reference the same case
- **Export/Import**: Export from one tool, import relevant context to another
- **Timeline Merging**: Combine document timelines with image metadata timestamps
- **Entity Linking**: Connect people/organizations found in documents with those in images

## Implementation Roadmap (Simplified)

### Phase 1: Enhanced Document Analysis (Weeks 1-4)
**Goal**: Bring document analysis up to image analysis quality standards

#### Week 1-2: OpenAI Responses API Integration

- [ ] Upgrade document analyzer to use `client.chat.completions.parse()` with Pydantic models
- [ ] Implement entity extraction (people, organizations, dates, legal terms)
- [ ] Add document classification (email, letter, contract, filing)
- [ ] Implement sentiment analysis (hostile, neutral, professional)
- [ ] Add legal risk flags (PII, privileged, threatening, deadline)

#### Week 3-4: Schema & Validation
- [ ] Create `document.v1.json` schema following image analyzer patterns
- [ ] Implement schema validation for all document analyses
- [ ] Add chain of custody tracking for document operations
- [ ] Create validation scripts for CI/CD pipeline

### Phase 2: Polish & Optimization (Weeks 5-6)
**Goal**: Optimize performance and user experience

- [ ] Optimize bulk processing performance (maintain current speed with AI insights)
- [ ] Add progress bars and better user feedback for long-running analyses
- [ ] Implement intelligent rate limiting for OpenAI API calls
- [ ] Add retry logic and error recovery for API failures
- [ ] Create comprehensive test suite with real legal document examples

### Phase 3: Cross-Evidence Integration (Weeks 7-8)
**Goal**: Enable simple connections between document and image evidence

- [ ] Create simple case-based evidence linking system
- [ ] Add basic cross-referencing capabilities (emails with attachments)
- [ ] Implement shared case ID support across both tools
- [ ] Create evidence export/import utilities for tool interoperability

## Success Metrics

- **Document Analysis Quality**: Entity extraction >90% accuracy, sentiment analysis >85% accuracy
- **Processing Speed**: Maintain current bulk processing performance (<30min for 1000 documents)
- **Schema Compliance**: 100% of analyses validate against schema
- **API Reliability**: <1% failure rate with proper retry/recovery
- **Cross-Evidence**: Successfully link 80%+ of related document-image pairs in test cases

## Key Principles

1. **Incremental Enhancement**: Improve each tool independently before forcing integration
2. **Maintain Productivity**: Keep existing bulk processing workflows that legal teams rely on
3. **Similar Patterns**: Use consistent approaches (schema validation, chain of custody) without tight coupling
4. **Simple Connections**: Enable evidence linking through simple, optional mechanisms
5. **Quality Focus**: Match image analysis sophistication in document processing

This approach respects the reality that mixed evidence cases exist while avoiding premature optimization of cross-modal integration. Each tool becomes excellent independently, with simple connection points for cases that need both.