"""Pydantic models for cross-evidence analysis.

This module provides type-safe models that mirror the cross-analysis.v1.json schema,
enabling forensic-grade cross-evidence correlation and analysis with strict validation.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


# Schema version for compatibility tracking
CROSS_ANALYSIS_SCHEMA_VERSION = "1.0.0"


class AnalysisType(str, Enum):
    """Types of cross-evidence analysis that can be performed."""
    ENTITY_CORRELATION = "entity_correlation"
    TIMELINE_ANALYSIS = "timeline_analysis"
    NARRATIVE_CONSISTENCY = "narrative_consistency"
    COMPREHENSIVE = "comprehensive"


class EvidenceType(str, Enum):
    """Types of evidence supported by the system."""
    DOCUMENT = "document"
    IMAGE = "image"
    EMAIL = "email"
    PDF = "pdf"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class EntityMatchingAlgorithm(str, Enum):
    """Algorithms available for entity matching."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class LegalSignificance(str, Enum):
    """Legal significance levels for patterns and findings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContradictionType(str, Enum):
    """Types of contradictions that can be identified."""
    TEMPORAL = "temporal"
    FACTUAL = "factual"
    ENTITY_MISMATCH = "entity_mismatch"
    NARRATIVE_CONFLICT = "narrative_conflict"


class SupportType(str, Enum):
    """Ways that evidence can support other evidence."""
    CORROBORATING = "corroborating"
    COMPLEMENTARY = "complementary"
    SEQUENTIAL = "sequential"
    CONTEXTUAL = "contextual"


class EventType(str, Enum):
    """Types of temporal events that can be extracted."""
    DOCUMENT_CREATED = "document_created"
    COMMUNICATION = "communication"
    MEETING = "meeting"
    DEADLINE = "deadline"
    INCIDENT = "incident"
    FILING = "filing"
    PHOTO_TAKEN = "photo_taken"
    OTHER = "other"


class EntityType(str, Enum):
    """Types of entities for classification."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    PHONE = "phone"
    EMAIL = "email"
    DATE = "date"
    DOCUMENT_REF = "document_ref"
    ACCOUNT = "account"
    ADDRESS = "address"
    OTHER = "other"


class ExtractionMethod(str, Enum):
    """Methods used to extract entities."""
    NLP = "nlp"
    OCR = "ocr"
    MANUAL = "manual"
    AI_ANALYSIS = "ai_analysis"


class RiskFactorType(str, Enum):
    """Types of risk factors for assessment."""
    DATA_INTEGRITY = "data_integrity"
    TAMPERING_INDICATORS = "tampering_indicators"
    TIMELINE_GAPS = "timeline_gaps"
    NARRATIVE_CONFLICTS = "narrative_conflicts"
    ENTITY_DISCREPANCIES = "entity_discrepancies"
    LEGAL_EXPOSURE = "legal_exposure"


class EvidenceCoherence(str, Enum):
    """Overall assessment levels for evidence coherence."""
    HIGHLY_COHERENT = "highly_coherent"
    MOSTLY_COHERENT = "mostly_coherent"
    MIXED = "mixed"
    CONCERNING_GAPS = "concerning_gaps"
    SIGNIFICANT_CONFLICTS = "significant_conflicts"


class AnalysisParameters(BaseModel):
    """Parameters used during cross-analysis."""
    confidence_threshold: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Minimum confidence threshold for correlations"
    )
    temporal_window_hours: Optional[float] = Field(
        default=None, ge=0.0,
        description="Time window for temporal correlation analysis"
    )
    entity_matching_algorithm: Optional[EntityMatchingAlgorithm] = Field(
        default=None,
        description="Algorithm used for entity matching"
    )


class AnalysisMetadata(BaseModel):
    """Metadata about the cross-analysis session."""
    analysis_id: str = Field(..., description="Unique identifier for this cross-analysis session")
    created_at: datetime = Field(..., description="Timestamp when cross-analysis was performed")
    analyst: str = Field(..., description="Actor or system performing the cross-analysis")
    analysis_type: AnalysisType = Field(..., description="Type of cross-analysis performed")
    version: str = Field(..., description="Version of cross-analysis algorithm used")
    parameters: Optional[AnalysisParameters] = Field(
        default=None,
        description="Parameters used during analysis"
    )


class EvidenceReference(BaseModel):
    """Reference to an evidence bundle included in cross-analysis."""
    evidence_id: str = Field(..., description="Unique evidence identifier")
    sha256: str = Field(
        ..., pattern=r"^[a-f0-9]{64}$",
        description="SHA256 hash of the evidence"
    )
    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    bundle_path: str = Field(..., description="Path to the evidence bundle file")
    ingested_at: Optional[datetime] = Field(
        default=None,
        description="When this evidence was originally ingested"
    )
    source_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Key metadata from the source evidence bundle"
    )


class ChainOfCustodyEntry(BaseModel):
    """Single entry in the cross-analysis chain of custody."""
    ts: datetime = Field(..., description="Timestamp of custody event")
    actor: str = Field(..., description="Actor performing the action")
    action: str = Field(..., description="Action performed")
    note: Optional[str] = Field(default=None, description="Additional details")
    evidence_affected: Optional[List[str]] = Field(
        default=None,
        description="List of evidence SHA256s affected by this action"
    )


class EvidenceOccurrence(BaseModel):
    """Occurrence of an entity in a specific piece of evidence."""
    evidence_sha256: str = Field(
        ..., pattern=r"^[a-f0-9]{64}$",
        description="SHA256 of evidence containing this entity"
    )
    context: str = Field(..., description="Context where entity appears")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence that this is the same entity"
    )
    entity_variant: Optional[str] = Field(
        default=None,
        description="Specific variant of entity name as it appears"
    )
    extraction_method: Optional[ExtractionMethod] = Field(
        default=None,
        description="How this entity was extracted"
    )


class SemanticAnalysis(BaseModel):
    """Semantic relationship analysis for an entity."""
    role_analysis: Optional[str] = Field(
        default=None,
        description="Analysis of the entity's role across evidence"
    )
    relationship_patterns: Optional[List[str]] = Field(
        default=None,
        description="Patterns in how this entity relates to other entities"
    )


class CorrelatedEntity(BaseModel):
    """Entity found across multiple pieces of evidence."""
    entity_name: str = Field(..., description="Canonical name of the correlated entity")
    entity_type: EntityType = Field(..., description="Type of entity")
    evidence_occurrences: List[EvidenceOccurrence] = Field(
        ..., min_items=2,
        description="Evidence pieces where this entity appears"
    )
    correlation_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence that all occurrences refer to the same entity"
    )
    semantic_analysis: Optional[SemanticAnalysis] = Field(
        default=None,
        description="Semantic relationship analysis for this entity"
    )


class CorrelationSummary(BaseModel):
    """Summary statistics for entity correlation."""
    total_entities_analyzed: Optional[int] = Field(default=None, ge=0)
    entities_correlated: Optional[int] = Field(default=None, ge=0)
    correlation_rate: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Percentage of entities that appear in multiple evidence pieces"
    )
    high_confidence_correlations: Optional[int] = Field(
        default=None, ge=0,
        description="Number of correlations above confidence threshold"
    )


class EntityCorrelation(BaseModel):
    """Results of entity correlation analysis across evidence types."""
    correlated_entities: Optional[List[CorrelatedEntity]] = Field(
        default=None,
        description="Entities found across multiple pieces of evidence"
    )
    correlation_summary: Optional[CorrelationSummary] = Field(
        default=None,
        description="Summary statistics for entity correlation"
    )


class TemporalEvent(BaseModel):
    """Chronologically ordered event extracted from evidence."""
    event_timestamp: datetime = Field(..., description="When the event occurred")
    evidence_sha256: str = Field(
        ..., pattern=r"^[a-f0-9]{64}$",
        description="Evidence containing this temporal reference"
    )
    event_type: EventType = Field(..., description="Type of temporal event")
    description: str = Field(..., description="Description of the event")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the temporal extraction"
    )
    entities_involved: Optional[List[str]] = Field(
        default=None,
        description="Entities associated with this temporal event"
    )
    source_context: Optional[str] = Field(
        default=None,
        description="Original context from which this timestamp was extracted"
    )


class SequencePattern(BaseModel):
    """Identified sequence of related events."""
    sequence_name: str = Field(..., description="Name or type of the sequence pattern")
    events: List[str] = Field(..., description="Event IDs or descriptions in sequence")
    pattern_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence this represents a meaningful pattern"
    )
    legal_significance: Optional[LegalSignificance] = Field(
        default=None,
        description="Assessed legal significance of this pattern"
    )


class TimelineGap(BaseModel):
    """Significant gap in the evidence timeline."""
    gap_start: datetime = Field(..., description="Start of the timeline gap")
    gap_end: datetime = Field(..., description="End of the timeline gap")
    gap_duration_hours: float = Field(..., ge=0.0, description="Duration of gap in hours")
    significance: LegalSignificance = Field(..., description="Significance of this timeline gap")
    context: Optional[str] = Field(
        default=None,
        description="Context explaining why this gap might be significant"
    )


class TemporalPatterns(BaseModel):
    """Patterns identified in the timeline."""
    sequence_analysis: Optional[List[SequencePattern]] = Field(
        default=None,
        description="Identified sequences of related events"
    )
    timeline_gaps: Optional[List[TimelineGap]] = Field(
        default=None,
        description="Significant gaps in the evidence timeline"
    )


class TimelineSummary(BaseModel):
    """Summary of timeline analysis."""
    total_temporal_events: Optional[int] = Field(default=None, ge=0)
    timeline_span_days: Optional[float] = Field(default=None, ge=0.0)
    earliest_event: Optional[datetime] = Field(default=None)
    latest_event: Optional[datetime] = Field(default=None)
    evidence_density: Optional[float] = Field(
        default=None, ge=0.0,
        description="Events per day across the timeline"
    )


class TimelineAnalysis(BaseModel):
    """Temporal analysis across evidence pieces."""
    temporal_events: Optional[List[TemporalEvent]] = Field(
        default=None,
        description="Chronologically ordered events extracted from evidence"
    )
    temporal_patterns: Optional[TemporalPatterns] = Field(
        default=None,
        description="Patterns identified in the timeline"
    )
    timeline_summary: Optional[TimelineSummary] = Field(
        default=None,
        description="Summary of timeline analysis"
    )


class Contradiction(BaseModel):
    """Identified contradiction between evidence pieces."""
    contradiction_type: ContradictionType = Field(..., description="Type of contradiction")
    evidence_pair: List[str] = Field(
        ..., min_items=2, max_items=2,
        description="SHA256s of contradicting evidence"
    )
    description: str = Field(..., description="Description of the contradiction")
    severity: LegalSignificance = Field(..., description="Severity of the contradiction")
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Confidence that this is a real contradiction"
    )
    evidence_contexts: Optional[List[str]] = Field(
        default=None,
        description="Specific contexts from each evidence piece showing the contradiction"
    )


class SupportingEvidenceGroup(BaseModel):
    """Evidence pieces that support each other."""
    evidence_group: List[str] = Field(
        ..., min_items=2,
        description="SHA256s of mutually supporting evidence"
    )
    support_type: SupportType = Field(..., description="How the evidence pieces support each other")
    strength: float = Field(
        ..., ge=0.0, le=1.0,
        description="Strength of the mutual support"
    )
    description: Optional[str] = Field(
        default=None,
        description="Explanation of how evidence supports each other"
    )


class NarrativeTheme(BaseModel):
    """Common theme identified across evidence."""
    theme_name: str = Field(..., description="Name or description of the narrative theme")
    supporting_evidence: List[str] = Field(..., description="Evidence that supports this theme")
    strength: float = Field(
        ..., ge=0.0, le=1.0,
        description="Strength of evidence for this theme"
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="Key terms associated with this theme"
    )
    legal_relevance: Optional[LegalSignificance] = Field(
        default=None,
        description="Assessed legal relevance of this theme"
    )


class NarrativeConsistency(BaseModel):
    """Analysis of narrative consistency across evidence."""
    consistency_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Overall narrative consistency score"
    )
    contradictions: Optional[List[Contradiction]] = Field(
        default=None,
        description="Identified contradictions between evidence pieces"
    )
    supporting_evidence: Optional[List[SupportingEvidenceGroup]] = Field(
        default=None,
        description="Evidence pieces that support each other"
    )
    narrative_themes: Optional[List[NarrativeTheme]] = Field(
        default=None,
        description="Common themes identified across evidence"
    )


class RiskFactor(BaseModel):
    """Specific risk factor identified in cross-analysis."""
    factor_type: RiskFactorType = Field(..., description="Type of risk factor")
    description: str = Field(..., description="Description of the risk factor")
    severity: LegalSignificance = Field(..., description="Severity of this risk factor")
    evidence_support: List[str] = Field(..., description="Evidence supporting this risk assessment")
    mitigation_recommendations: Optional[List[str]] = Field(
        default=None,
        description="Recommended actions to mitigate this risk"
    )


class RiskAssessment(BaseModel):
    """Cross-evidence risk assessment."""
    overall_risk_level: Optional[LegalSignificance] = Field(
        default=None,
        description="Overall risk level based on cross-analysis"
    )
    risk_factors: Optional[List[RiskFactor]] = Field(
        default=None,
        description="Specific risk factors identified"
    )


class AnalysisSummary(BaseModel):
    """Executive summary of cross-analysis findings."""
    key_findings: Optional[List[str]] = Field(
        default=None,
        description="Key findings from the cross-analysis"
    )
    evidence_coherence: Optional[EvidenceCoherence] = Field(
        default=None,
        description="Overall assessment of evidence coherence"
    )
    recommended_actions: Optional[List[str]] = Field(
        default=None,
        description="Recommended next steps based on analysis"
    )
    legal_considerations: Optional[List[str]] = Field(
        default=None,
        description="Legal considerations highlighted by the analysis"
    )


class AnalysisResults(BaseModel):
    """Complete results of cross-evidence analysis."""
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the cross-analysis results"
    )
    entity_correlation: Optional[EntityCorrelation] = Field(
        default=None,
        description="Results of entity correlation analysis"
    )
    timeline_analysis: Optional[TimelineAnalysis] = Field(
        default=None,
        description="Temporal analysis across evidence pieces"
    )
    narrative_consistency: Optional[NarrativeConsistency] = Field(
        default=None,
        description="Analysis of narrative consistency across evidence"
    )
    risk_assessment: Optional[RiskAssessment] = Field(
        default=None,
        description="Cross-evidence risk assessment"
    )
    summary: Optional[AnalysisSummary] = Field(
        default=None,
        description="Executive summary of cross-analysis findings"
    )


class CrossAnalysisBundle(BaseModel):
    """Complete cross-evidence analysis bundle.

    This model provides the forensic-grade structure for cross-evidence
    analysis results, maintaining strict validation and audit trail
    requirements for legal evidence processing.
    """

    schema_version: Literal[CROSS_ANALYSIS_SCHEMA_VERSION] = Field(
        default=CROSS_ANALYSIS_SCHEMA_VERSION,
        description="Cross-analysis schema version for compatibility tracking"
    )

    case_id: Optional[str] = Field(
        default=None,
        description="Case identifier linking all related evidence bundles"
    )

    analysis_metadata: AnalysisMetadata = Field(
        ...,
        description="Metadata about the cross-analysis session"
    )

    evidence_references: List[EvidenceReference] = Field(
        ..., min_items=2,
        description="References to evidence bundles included in this cross-analysis"
    )

    chain_of_custody: Optional[List[ChainOfCustodyEntry]] = Field(
        default=None,
        description="Audit trail for the cross-analysis process"
    )

    analysis_results: AnalysisResults = Field(
        ...,
        description="Complete results of cross-evidence analysis"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }
        use_enum_values = True
        validate_assignment = True


# Export all models for easy import
__all__ = [
    "CROSS_ANALYSIS_SCHEMA_VERSION",
    "AnalysisType",
    "EvidenceType",
    "EntityMatchingAlgorithm",
    "LegalSignificance",
    "ContradictionType",
    "SupportType",
    "EventType",
    "EntityType",
    "ExtractionMethod",
    "RiskFactorType",
    "EvidenceCoherence",
    "AnalysisParameters",
    "AnalysisMetadata",
    "EvidenceReference",
    "ChainOfCustodyEntry",
    "EvidenceOccurrence",
    "SemanticAnalysis",
    "CorrelatedEntity",
    "CorrelationSummary",
    "EntityCorrelation",
    "TemporalEvent",
    "SequencePattern",
    "TimelineGap",
    "TemporalPatterns",
    "TimelineSummary",
    "TimelineAnalysis",
    "Contradiction",
    "SupportingEvidenceGroup",
    "NarrativeTheme",
    "NarrativeConsistency",
    "RiskFactor",
    "RiskAssessment",
    "AnalysisSummary",
    "AnalysisResults",
    "CrossAnalysisBundle"
]