# Cross-Evidence Analysis Architecture Scope

## Executive Summary

This document outlines the architectural design for implementing cross-evidence analysis capabilities in the Evidence Toolkit. The solution builds upon the existing forensic-grade foundation while introducing sophisticated correlation analysis across multiple evidence types (documents, images, emails, PDFs).

## Current Architecture Assessment

### ✅ **Existing Foundation (Strong)**
- **Individual Evidence Schemas**: `images.v1.json`, `document.v1.json` with forensic validation
- **Unified Analysis Model**: `UnifiedAnalysis` class supporting multiple evidence types
- **Content-Addressed Storage**: SHA256-based immutable evidence organization
- **Chain of Custody**: Complete audit trail with actor/action logging
- **OpenAI Integration**: Modern `responses.parse()` API with temperature=0 for deterministic analysis

### 🎯 **Gap Analysis**
- **Cross-Evidence Correlation**: No systematic entity matching across evidence types
- **Timeline Synthesis**: Individual evidence timelines exist, but no cross-evidence temporal analysis
- **Narrative Consistency**: No framework for detecting contradictions/confirmations across evidence
- **Batch Processing**: Limited capability for analyzing evidence sets as cohesive units

## Recommended Architecture: Processing Layer Approach

### 🏗️ **Core Design Philosophy**

**Don't create a new input schema** - instead, build a specialized `CrossEvidenceAnalyzer` that:
1. **Consumes existing evidence bundles** (images.v1.json + document.v1.json)
2. **Performs correlation analysis** using AI and graph algorithms
3. **Outputs structured cross-analysis results** using a new `cross-analysis.v1.json` schema

This follows the successful `RetaliationAnalyzer` pattern while extending it for multi-evidence-type analysis.

## Technical Implementation Scope

### 1. **CrossEvidenceAnalyzer Core Engine**

```python
class CrossEvidenceAnalyzer:
    """
    Orchestrates cross-evidence analysis using OpenAI Responses API + NetworkX
    """
    def __init__(self, evidence_root: Path, openai_client: OpenAI):
        self.evidence_root = evidence_root
        self.client = openai_client
        self.entity_graph = nx.Graph()  # NetworkX for entity relationships

    def analyze_case(self, case_id: str) -> CrossAnalysisResult:
        # 1. Load all evidence for case (from existing schemas)
        evidence_items = self._load_case_evidence(case_id)

        # 2. Extract entities and build relationship graph
        entity_correlations = self._correlate_entities(evidence_items)

        # 3. Construct unified timeline
        timeline_analysis = self._build_cross_timeline(evidence_items)

        # 4. Analyze narrative consistency
        narrative_analysis = self._analyze_narrative_consistency(evidence_items)

        # 5. Assess overall case strength
        confidence_assessment = self._aggregate_confidence(evidence_items)

        return CrossAnalysisResult(...)
```

### 2. **AI-Powered Analysis Components**

#### **Entity Correlation Engine**
```python
class EntityCorrelationEngine:
    """Uses OpenAI structured outputs for entity matching across evidence types"""

    def correlate_entities(
        self,
        evidence_items: List[EvidenceBundle],
        temperature: float = 0.0  # Forensic determinism
    ) -> EntityCorrelationResult:

        # Multi-modal prompt combining document text + image analysis
        correlation_prompt = self._build_correlation_prompt(evidence_items)

        return self.client.responses.parse(
            model="gpt-4.1-mini",
            input=[{"role": "user", "content": correlation_prompt}],
            text_format=EntityCorrelationResponse,
            temperature=temperature,
            reasoning={"effort": "high"}  # Complex cross-evidence analysis
        )
```

#### **Timeline Synthesis Engine**
```python
class TimelineSynthesisEngine:
    """Constructs unified timelines using pandas + OpenAI temporal reasoning"""

    def build_cross_timeline(self, evidence_items: List[EvidenceBundle]) -> TimelineAnalysis:
        # 1. Extract temporal markers using pandas TimeSeries analysis
        temporal_data = self._extract_temporal_markers(evidence_items)

        # 2. Use OpenAI for complex temporal reasoning
        timeline_response = self.client.responses.parse(
            model="gpt-4.1-mini",
            input=[{"role": "user", "content": timeline_prompt}],
            text_format=TimelineAnalysisResponse,
            temperature=0.0
        )

        # 3. Validate timeline consistency using pandas
        validated_timeline = self._validate_timeline_consistency(timeline_response)

        return validated_timeline
```

### 3. **Dependencies and Integration**

#### **Core Dependencies (Research-Backed)**

**Pandas (Timeline Analysis)**
- **Usage**: TimeSeries data structures for temporal evidence correlation
- **Key Features**:
  - `pd.Series` with `DatetimeIndex` for timeline construction
  - `pd.period_range()` for time span analysis
  - Temporal slicing: `s["2025-01-01":"2025-02-01"]`
  - Timeline gap detection and density analysis

**NetworkX (Entity Relationship Graphs)**
- **Usage**: Graph-based entity correlation and relationship mapping
- **Key Features**:
  - `nx.Graph()` for entity relationship networks
  - `nx.neighbors(node)` for entity connection analysis
  - `nx.connected_components()` for entity cluster detection
  - Graph algorithms for centrality and influence analysis

**OpenAI Responses API (AI Analysis)**
- **Current Implementation**: Already using `responses.parse()` correctly
- **Enhancements**:
  - Multi-modal analysis (documents + images in single API call)
  - Structured cross-evidence correlation models
  - Temperature=0 enforcement for forensic determinism

#### **Environment Setup (uv-based)**
```bash
# Add new dependencies to existing environment
cd evidence-toolkit/
uv add pandas networkx matplotlib seaborn
uv add pydantic-settings python-dotenv  # Configuration management

# Development dependencies
uv add --dev pytest-asyncio pytest-mock  # Testing cross-evidence workflows
```

### 4. **Cross-Analysis Schema Design**

#### **Output Schema: cross-analysis.v1.json**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.org/schemas/cross-analysis.v1.json",
  "title": "Cross-Evidence Analysis Results (V1)",
  "type": "object",
  "required": ["case_id", "evidence_sources", "analysis_timestamp", "cross_analysis"],
  "properties": {
    "case_id": {"type": "string"},
    "evidence_sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["sha256", "evidence_type", "file_path"],
        "properties": {
          "sha256": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
          "evidence_type": {"enum": ["document", "image", "email", "pdf"]},
          "file_path": {"type": "string"}
        }
      }
    },
    "cross_analysis": {
      "type": "object",
      "required": ["entity_correlations", "timeline_analysis", "narrative_consistency"],
      "properties": {
        "entity_correlations": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["entity_name", "entity_type", "confidence", "sources"],
            "properties": {
              "entity_name": {"type": "string"},
              "entity_type": {"enum": ["person", "organization", "location", "date", "legal_term"]},
              "confidence": {"type": "number", "minimum": 0, "maximum": 1},
              "sources": {
                "type": "array",
                "items": {"type": "string", "pattern": "^[a-f0-9]{64}$"}
              },
              "relationships": {
                "type": "array",
                "items": {
                  "type": "object",
                  "required": ["related_entity", "relationship_type", "confidence"],
                  "properties": {
                    "related_entity": {"type": "string"},
                    "relationship_type": {"enum": ["associated_with", "employed_by", "located_at", "preceded_by"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                  }
                }
              }
            }
          }
        },
        "timeline_analysis": {
          "type": "object",
          "required": ["events", "timeline_gaps", "sequence_confidence"],
          "properties": {
            "events": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["timestamp", "event_description", "sources", "legal_significance"],
                "properties": {
                  "timestamp": {"type": "string", "format": "date-time"},
                  "event_description": {"type": "string"},
                  "sources": {"type": "array", "items": {"type": "string"}},
                  "legal_significance": {"enum": ["critical", "high", "medium", "low"]},
                  "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                }
              }
            },
            "timeline_gaps": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["gap_start", "gap_end", "significance"],
                "properties": {
                  "gap_start": {"type": "string", "format": "date-time"},
                  "gap_end": {"type": "string", "format": "date-time"},
                  "significance": {"enum": ["critical", "high", "medium", "low"]},
                  "potential_missing_evidence": {"type": "array", "items": {"type": "string"}}
                }
              }
            },
            "sequence_confidence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        },
        "narrative_consistency": {
          "type": "object",
          "required": ["contradictions", "supporting_correlations", "overall_coherence"],
          "properties": {
            "contradictions": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["contradiction_type", "evidence_sources", "severity"],
                "properties": {
                  "contradiction_type": {"enum": ["temporal", "factual", "entity", "narrative"]},
                  "evidence_sources": {"type": "array", "items": {"type": "string"}},
                  "severity": {"enum": ["critical", "high", "medium", "low"]},
                  "description": {"type": "string"}
                }
              }
            },
            "supporting_correlations": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["correlation_type", "evidence_sources", "strength"],
                "properties": {
                  "correlation_type": {"enum": ["entity_confirmation", "timeline_consistency", "narrative_support"]},
                  "evidence_sources": {"type": "array", "items": {"type": "string"}},
                  "strength": {"type": "number", "minimum": 0, "maximum": 1},
                  "description": {"type": "string"}
                }
              }
            },
            "overall_coherence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    },
    "confidence_assessment": {
      "type": "object",
      "required": ["overall_confidence", "confidence_factors"],
      "properties": {
        "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "confidence_factors": {
          "type": "object",
          "required": ["entity_correlation_confidence", "timeline_confidence", "narrative_confidence"],
          "properties": {
            "entity_correlation_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "timeline_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "narrative_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "evidence_authenticity_confidence": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    }
  }
}
```

### 5. **CLI Integration**

#### **New Commands**
```bash
# Cross-evidence analysis
document-analyzer cross-analyze --case-id CASE-2025-001 --output-dir ./cross-analysis

# Batch processing multiple cases
document-analyzer cross-analyze-batch --case-pattern "CASE-2025-*" --parallel 3

# Timeline-focused analysis
document-analyzer cross-timeline --case-id CASE-2025-001 --date-range "2025-01-01:2025-03-01"

# Entity correlation analysis
document-analyzer cross-entities --case-id CASE-2025-001 --entity-types person,organization,location
```

#### **Unified CLI Architecture**
```python
# Enhanced CLI supporting both individual and cross-evidence analysis
@app.command()
def cross_analyze(
    case_id: str = typer.Option(..., help="Case ID for cross-evidence analysis"),
    output_dir: Path = typer.Option("./cross-analysis", help="Output directory"),
    evidence_types: str = typer.Option("document,image", help="Evidence types to include"),
    confidence_threshold: float = typer.Option(0.5, help="Minimum confidence for correlations")
):
    """Perform cross-evidence analysis for a case."""
    analyzer = CrossEvidenceAnalyzer(evidence_root=evidence_dir)
    result = analyzer.analyze_case(case_id)

    # Save results using cross-analysis schema
    output_file = output_dir / f"{case_id}_cross_analysis.json"
    result.save_to_file(output_file)

    # Generate visualizations
    visualizer = CrossEvidenceVisualizer(result)
    visualizer.generate_timeline_chart(output_dir / f"{case_id}_timeline.png")
    visualizer.generate_entity_graph(output_dir / f"{case_id}_entities.png")
```

### 6. **Validation and Testing Strategy**

#### **Schema Validation Pipeline**
```python
# Cross-analysis validation (follows existing pattern)
def validate_cross_analysis_schema(analysis_file: Path) -> bool:
    """Validate cross-analysis results against schema"""
    schema_path = Path("schemas/cross-analysis.v1.json")

    with open(schema_path) as f:
        schema = json.load(f)

    with open(analysis_file) as f:
        analysis_data = json.load(f)

    jsonschema.validate(analysis_data, schema)

    # Additional forensic validation
    validate_evidence_references(analysis_data)
    validate_confidence_consistency(analysis_data)

    return True
```

#### **Testing Framework**
```python
# Test cases for cross-evidence analysis
class TestCrossEvidenceAnalysis:
    def test_entity_correlation_accuracy(self):
        """Test entity matching across document and image evidence"""

    def test_timeline_consistency_detection(self):
        """Test detection of timeline inconsistencies"""

    def test_confidence_aggregation(self):
        """Test confidence score calculation across evidence types"""

    def test_forensic_validation(self):
        """Test forensic integrity requirements"""
```

## Implementation Phases

### **Phase 1: Core Infrastructure (2-3 weeks)**
1. **CrossEvidenceAnalyzer Framework**
   - Basic class structure and evidence loading
   - Integration with existing evidence storage
   - Configuration management (environment variables, settings)

2. **Schema Design and Validation**
   - Complete `cross-analysis.v1.json` schema
   - Validation pipeline (following existing patterns)
   - Pydantic models for type safety

3. **Dependencies Integration**
   - pandas TimeSeries setup for timeline analysis
   - NetworkX integration for entity relationship graphs
   - OpenAI Responses API enhancements

### **Phase 2: Analysis Engines (3-4 weeks)**
1. **Entity Correlation Engine**
   - Multi-modal entity extraction (documents + images)
   - Graph-based relationship mapping using NetworkX
   - Confidence scoring and validation

2. **Timeline Synthesis Engine**
   - Cross-evidence temporal marker extraction
   - Timeline gap detection and analysis
   - Pandas-based timeline data structures

3. **Narrative Consistency Analyzer**
   - Contradiction detection across evidence types
   - Supporting correlation identification
   - Coherence scoring algorithms

### **Phase 3: Integration and Visualization (2-3 weeks)**
1. **CLI Integration**
   - New cross-analysis commands
   - Batch processing capabilities
   - Configuration and error handling

2. **Visualization Components**
   - Timeline charts with evidence correlation
   - Entity relationship graphs
   - Narrative consistency dashboards

3. **Testing and Validation**
   - Comprehensive test suite
   - Schema validation integration
   - Performance benchmarking

### **Phase 4: Production Readiness (1-2 weeks)**
1. **Documentation and Examples**
   - User guide for cross-evidence analysis
   - API documentation
   - Tutorial examples with sample data

2. **Performance Optimization**
   - Batch processing optimization
   - Memory efficiency for large evidence sets
   - Caching strategies for repeated analysis

## Risk Assessment and Mitigation

### **Technical Risks**
- **API Rate Limiting**: OpenAI API limits for large evidence sets
  - *Mitigation*: Implement exponential backoff, batch processing
- **Memory Usage**: Large evidence sets with complex graph analysis
  - *Mitigation*: Streaming processing, configurable memory limits
- **Schema Evolution**: Changes to individual evidence schemas
  - *Mitigation*: Version-aware schema handling, backward compatibility

### **Forensic Risks**
- **Determinism**: Ensuring reproducible AI analysis results
  - *Mitigation*: Temperature=0 enforcement, seed management
- **Chain of Custody**: Maintaining audit trail for cross-analysis
  - *Mitigation*: Complete logging of all cross-analysis operations
- **Evidence Integrity**: Risk of correlation bias or false positives
  - *Mitigation*: Confidence thresholds, human validation workflows

## Success Metrics

### **Functional Metrics**
- **Entity Correlation Accuracy**: >85% precision in entity matching
- **Timeline Consistency**: <5% false positive contradiction detection
- **Processing Performance**: <2 minutes per case with <10 evidence items
- **Schema Compliance**: 100% validation success rate

### **Forensic Metrics**
- **Determinism**: 100% reproducible results with identical inputs
- **Audit Trail**: Complete chain of custody for all cross-analysis operations
- **Legal Admissibility**: Meets Federal Rules of Evidence standards

## Conclusion

This cross-evidence analysis architecture leverages the Evidence Toolkit's existing forensic-grade foundation while introducing sophisticated AI-powered correlation capabilities. The processing layer approach maintains schema integrity while providing powerful new analysis capabilities for legal evidence processing.

The phased implementation approach ensures manageable development while delivering incremental value. The use of established libraries (pandas, NetworkX) combined with modern OpenAI structured outputs provides a robust technical foundation for forensic-grade cross-evidence analysis.

`★ Insight ─────────────────────────────────────`
**Architectural Excellence**: This design maintains the Evidence Toolkit's forensic integrity while adding sophisticated cross-evidence correlation. The processing layer approach preserves existing schemas while enabling powerful new capabilities through AI and graph analysis.

**Research-Driven Dependencies**: The pandas and NetworkX integrations are backed by comprehensive API research, ensuring we're using the most appropriate tools for timeline analysis and entity relationship mapping in a legal context.

**Production-Ready Foundation**: The phased approach and comprehensive risk assessment ensure this architecture can be implemented successfully while maintaining the highest standards for legal evidence processing.
`─────────────────────────────────────────────────`