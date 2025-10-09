"""Unified Pydantic models for Evidence Toolkit v3.0.

This module consolidates ALL Pydantic models from the previous architecture into
a single source of truth. No more hunting across multiple files - everything is here.

Model Categories:
- Base Types & Enums: Evidence types, file metadata
- AI Analysis Results: Document, Image, Email analysis (from OpenAI Responses API)
- Unified Analysis: Multi-modal evidence container
- Forensic Bundles: Legal-grade evidence packages with chain of custody
- Cross-Evidence Analysis: Correlation and timeline (NOW PYDANTIC!)
- Operation Results: Ingestion, export results

All models use Pydantic v2 for runtime validation and schema compliance.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional, List, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, model_validator

# =============================================================================
# SCHEMA VERSIONS
# =============================================================================

SCHEMA_VERSION = "1.0.0"
CROSS_ANALYSIS_SCHEMA_VERSION = "1.0.0"


# =============================================================================
# BASE TYPES & ENUMS
# =============================================================================

class EvidenceType(str, Enum):
    """Types of evidence that can be analyzed."""
    DOCUMENT = "document"
    IMAGE = "image"
    EMAIL = "email"
    PDF = "pdf"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class FileMetadata(BaseModel):
    """Basic file metadata for any evidence type."""
    filename: str
    file_size: int
    mime_type: Optional[str] = None
    created_time: str
    modified_time: str
    extension: str
    sha256: str


class ChainOfCustodyEvent(BaseModel):
    """Chain of custody tracking event."""
    timestamp: datetime
    event_type: str  # "ingest", "analyze", "export", "case_association"
    actor: str
    description: str
    metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# AI ANALYSIS MODELS (OpenAI Responses API)
# =============================================================================

class DocumentEntity(BaseModel):
    """Extracted entity from document analysis."""
    name: str = Field(..., description="The extracted entity text")
    type: Literal["person", "organization", "date", "legal_term"] = Field(
        ..., description="Classification of the entity type"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score for the extraction"
    )
    context: str = Field(
        ..., description="Surrounding context where entity was found"
    )

    # v3.1 Layer 1 enhancements - OpenAI best practice: Optional[str] not str = ""
    relationship: Optional[str] = Field(
        default=None,
        description=(
            "Relationship to other entities (e.g., 'sent email to Rachel Hemmings', "
            "'mentioned by Paul Boucherat', 'copied on email to HR'). "
            "Set to null if no clear relationship identified in context."
        )
    )
    quoted_text: Optional[str] = Field(
        default=None,
        description=(
            "Exact verbatim quote if entity made legally significant statement "
            "(admissions, threats, policy violations, obligations). "
            "Set to null if: not a person, no statement made, or statement lacks legal significance."
        )
    )
    associated_event: Optional[str] = Field(
        default=None,
        description=(
            "Event/action for date entities (e.g., 'meeting with HR', 'deadline for response', "
            "'complaint filed'). Set to null if: not a date entity or event unknown from context."
        )
    )


class DocumentAnalysis(BaseModel):
    """Complete structured analysis result from OpenAI Responses API.

    This model defines the exact response format for deterministic
    document analysis suitable for legal evidence processing.
    """
    summary: str = Field(..., description="Executive summary of document content")

    entities: List[DocumentEntity] = Field(
        default_factory=list,
        description="Extracted entities with confidence scores"
    )

    document_type: Literal["email", "letter", "contract", "filing"] = Field(
        ..., description="Classification of document type"
    )

    sentiment: Literal["hostile", "neutral", "professional"] = Field(
        ..., description="Overall tone and sentiment analysis"
    )

    legal_significance: Literal["critical", "high", "medium", "low"] = Field(
        ..., description="Assessment of legal importance"
    )

    risk_flags: List[Literal["threatening", "deadline", "pii", "confidential", "time_sensitive", "retaliation_indicators", "harassment", "discrimination"]] = Field(
        default_factory=list,
        description="Identified risk factors requiring attention"
    )

    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0, description="Overall analysis confidence score"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }


class ImageAnalysisStructured(BaseModel):
    """Structured image analysis result from OpenAI Responses API (Vision).

    This model ensures deterministic, forensic-grade image analysis
    suitable for legal evidence processing.
    """
    scene_description: str = Field(
        ..., description="Detailed description of the visual scene"
    )

    detected_text: Optional[str] = Field(
        None, description="Any visible text content (OCR)"
    )

    detected_objects: List[str] = Field(
        default_factory=list,
        description="List of visible objects, people, or items"
    )

    people_present: bool = Field(
        ..., description="Whether people are visible in the image"
    )

    timestamps_visible: bool = Field(
        ..., description="Whether timestamps or dates are visible"
    )

    potential_evidence_value: Literal["low", "medium", "high"] = Field(
        ..., description="Assessment of evidential value"
    )

    analysis_notes: str = Field(
        ..., description="Additional forensic observations or context"
    )

    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0, description="Overall analysis confidence score"
    )

    risk_flags: List[Literal["low_quality", "tampering_suspected", "metadata_missing", "unclear_content"]] = Field(
        default_factory=list,
        description="Identified risk factors or quality issues"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            float: lambda v: round(v, 4)  # Consistent precision
        }


class EmailParticipant(BaseModel):
    """Email participant with role and authority analysis."""
    email_address: str = Field(..., description="Email address of participant")
    display_name: Optional[str] = Field(None, description="Display name if available")
    role: Literal["sender", "recipient", "cc", "bcc"] = Field(
        ..., description="Role in the specific email"
    )
    authority_level: Literal["executive", "management", "employee", "external"] = Field(
        ..., description="Organizational authority level"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in authority level assessment"
    )

    # v3.1 Layer 1 enhancements - power dynamics analysis
    message_count: int = Field(
        default=0,
        ge=0,
        description="Number of messages sent by this participant in the thread"
    )
    deference_score: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Communication deference: 0.0=highly dominant/controlling, 0.5=neutral, 1.0=highly deferential"
    )
    dominant_topics: List[str] = Field(
        default_factory=list,
        description="Topics this participant drove or controlled in the conversation"
    )


class EscalationEvent(BaseModel):
    """Detected escalation point in email thread."""
    email_position: int = Field(
        ..., ge=0, description="Position in thread (0-based index)"
    )
    escalation_type: Literal[
        "tone_change", "new_recipient", "authority_escalation", "threat", "deadline"
    ] = Field(..., description="Type of escalation detected")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in escalation detection"
    )
    description: str = Field(
        ..., description="Detailed description of escalation event"
    )
    context: str = Field(
        ..., description="Relevant text supporting the escalation detection"
    )


class EmailThreadAnalysis(BaseModel):
    """Complete forensic analysis of email thread.

    This model defines the exact response format for deterministic
    email thread analysis suitable for legal evidence processing.
    Follows the same structure as DocumentAnalysis for consistency.
    """
    thread_summary: str = Field(
        ..., description="Executive summary of email thread focusing on legal significance"
    )

    participants: List[EmailParticipant] = Field(
        default_factory=list,
        description="All participants with role and authority analysis"
    )

    communication_pattern: Literal[
        "professional", "escalating", "hostile", "retaliatory"
    ] = Field(..., description="Overall communication pattern assessment")

    sentiment_progression: List[float] = Field(
        ..., description="Sentiment score for each email (0.0=hostile, 0.5=neutral, 1.0=professional)"
    )

    escalation_events: List[EscalationEvent] = Field(
        default_factory=list,
        description="Detected escalation points throughout the thread"
    )

    legal_significance: Literal["critical", "high", "medium", "low"] = Field(
        ..., description="Assessment of legal importance and evidence value"
    )

    risk_flags: List[Literal[
        "threatening", "harassment", "discrimination", "retaliation",
        "deadline", "pii", "confidential", "hostile_takeover", "policy_violation"
    ]] = Field(
        default_factory=list,
        description="Legal risk indicators requiring attention"
    )

    timeline_reconstruction: List[str] = Field(
        default_factory=list,
        description="Chronological summary of key communication events"
    )

    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the complete thread analysis"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }


# =============================================================================
# UNIFIED ANALYSIS RESULTS (Client Package Format)
# =============================================================================

class DocumentAnalysisResult(BaseModel):
    """Results from document text analysis."""
    # Legacy word frequency fields (backwards compatible)
    total_words: int
    unique_words: int
    word_frequency: Dict[str, int]
    top_words: List[tuple] = Field(description="Top 20 most frequent words")
    wordcloud_file: Optional[str] = None
    frequency_chart_file: Optional[str] = None

    # AI-powered analysis fields (from OpenAI Responses API)
    openai_model: Optional[str] = None
    ai_summary: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    document_type: Optional[str] = None
    sentiment: Optional[str] = None
    legal_significance: Optional[str] = None
    risk_flags: Optional[List[str]] = None
    analysis_confidence: Optional[float] = None


class ImageAnalysisResult(BaseModel):
    """Results from image analysis."""
    openai_model: str
    openai_response: Dict[str, Any]
    detected_objects: Optional[List[str]] = None
    detected_text: Optional[str] = None
    scene_description: Optional[str] = None
    analysis_confidence: Optional[float] = None


class UnifiedAnalysis(BaseModel):
    """Unified analysis result for any evidence type.

    This is the main client-facing format used in client packages.
    """
    evidence_type: EvidenceType
    analysis_timestamp: datetime
    file_metadata: FileMetadata

    # Multi-case support
    case_ids: List[str] = Field(default_factory=list, description="Cases this evidence belongs to")
    case_id: Optional[str] = Field(default=None, description="Deprecated: Use case_ids instead")

    # Analysis results (only one will be populated based on evidence_type)
    document_analysis: Optional[DocumentAnalysisResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None
    email_analysis: Optional[EmailThreadAnalysis] = None  # v3.1: Use full EmailThreadAnalysis

    # Chain of custody
    chain_of_custody: List[ChainOfCustodyEvent] = Field(default_factory=list)

    # EXIF data for images
    exif_data: Optional[Dict[str, Any]] = None

    # Email metadata (headers) for emails
    email_metadata: Optional[Dict[str, Any]] = None

    # Additional metadata
    labels: List[str] = Field(default_factory=list, description="Detected labels/categories")
    notes: Optional[str] = None

    @model_validator(mode='after')
    def sync_case_fields(self):
        """Auto-sync case_id and case_ids for backward compatibility."""
        if self.case_id and not self.case_ids:
            self.case_ids = [self.case_id]
        elif self.case_ids and not self.case_id:
            self.case_id = self.case_ids[0] if self.case_ids else None
        return self


# =============================================================================
# FORENSIC BUNDLES (Legal-Grade Evidence Packages)
# =============================================================================

class EvidenceCore(BaseModel):
    """Core evidence metadata following evidence bundle format."""
    evidence_id: str = Field(..., description="Unique identifier (typically SHA256)")
    sha256: str = Field(..., pattern=r"^[a-f0-9]{64}$", description="SHA256 hash of evidence")
    mime_type: str = Field(..., description="MIME type of the evidence file")
    bytes: int = Field(..., ge=1, description="File size in bytes")
    ingested_at: datetime = Field(..., description="Timestamp when evidence was ingested")
    source_path: str = Field(..., description="Original file path or source identifier")


class ChainOfCustodyEntry(BaseModel):
    """Single entry in the chain of custody audit trail."""
    ts: datetime = Field(..., description="Timestamp of the event")
    actor: str = Field(..., description="Actor who performed the action")
    action: str = Field(..., description="Action performed (ingest, analyze, export)")
    note: Optional[str] = Field(default=None, description="Additional notes about the action")


class AnalysisModelInfo(BaseModel):
    """Information about the AI model used for analysis."""
    name: str = Field(..., description="Model name (e.g., gpt-4o-2024-08-06)")
    revision: str = Field(..., description="Model revision or version")


class AnalysisParameters(BaseModel):
    """Parameters used during the analysis."""
    temperature: Optional[float] = Field(default=None, le=0.0, description="Temperature parameter (≤0 for deterministic)")
    prompt_hash: Optional[str] = Field(default=None, description="SHA256 hash of the prompt used")
    token_usage_in: Optional[int] = Field(default=None, description="Input tokens consumed")
    token_usage_out: Optional[int] = Field(default=None, description="Output tokens generated")


class DocumentAnalysisRecord(BaseModel):
    """Analysis record wrapping DocumentAnalysis with metadata."""
    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    created_at: datetime = Field(..., description="When the analysis was performed")

    model: AnalysisModelInfo = Field(..., description="AI model information")
    parameters: AnalysisParameters = Field(..., description="Analysis parameters")
    outputs: DocumentAnalysis = Field(..., description="Structured analysis results")
    confidence_overall: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")


class EvidenceBundle(BaseModel):
    """Complete evidence bundle for forensic storage.

    This model aligns with the document.v1.json schema and provides
    the unified format for forensic evidence management.
    """
    schema_version: Literal["1.0.0"] = Field(default="1.0.0", description="Schema version")
    case_id: Optional[str] = Field(default=None, description="Case identifier for cross-evidence linking")

    evidence: EvidenceCore = Field(..., description="Core evidence metadata")
    chain_of_custody: List[ChainOfCustodyEntry] = Field(
        default_factory=list,
        description="Complete audit trail of evidence handling"
    )
    analyses: List[DocumentAnalysisRecord] = Field(
        default_factory=list,
        description="Analysis records for this evidence"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }


# =============================================================================
# CROSS-EVIDENCE ANALYSIS (NOW PYDANTIC! - v3.0 Fix)
# =============================================================================

class EntityType(str, Enum):
    """Types of entities for classification."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    PHONE = "phone"
    EMAIL_ADDR = "email"
    DATE = "date"
    DOCUMENT_REF = "document_ref"
    ACCOUNT = "account"
    ADDRESS = "address"
    OTHER = "other"


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


class CorrelatedEntity(BaseModel):
    """Entity found across multiple pieces of evidence."""
    entity_name: str = Field(..., description="Canonical name of the correlated entity")
    entity_type: str = Field(..., description="Type of entity (person, org, etc.)")
    occurrence_count: int = Field(..., ge=2, description="Number of evidence pieces with this entity")
    confidence_average: float = Field(..., ge=0.0, le=1.0, description="Average confidence across occurrences")
    evidence_occurrences: List[Dict[str, Any]] = Field(..., description="Details of each occurrence")


class TimelineEvent(BaseModel):
    """Chronologically ordered event extracted from evidence."""
    timestamp: datetime = Field(..., description="When the event occurred")
    evidence_sha256: str = Field(
        ..., pattern=r"^[a-f0-9]{64}$",
        description="Evidence containing this temporal reference"
    )
    evidence_type: str = Field(..., description="Type of evidence")
    event_type: str = Field(..., description="Type of temporal event")
    description: str = Field(..., description="Description of the event")
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Confidence in the temporal extraction"
    )
    ai_classification: Optional[Dict[str, Any]] = Field(
        default=None,
        description="AI-detected pattern classification (retaliation, escalation, etc.)"
    )


# =============================================================================
# LEGAL PATTERN ANALYSIS (v3.1 - AI-powered cross-evidence insights)
# =============================================================================

class Contradiction(BaseModel):
    """Conflicting statement detected across evidence."""
    statement_1: str = Field(..., description="First statement")
    statement_1_source: str = Field(..., description="SHA256 of evidence containing first statement")
    statement_2: str = Field(..., description="Conflicting statement")
    statement_2_source: str = Field(..., description="SHA256 of evidence containing second statement")
    contradiction_type: Literal["factual", "temporal", "attribution"] = Field(
        ..., description="Type of contradiction"
    )
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity of contradiction")
    explanation: str = Field(..., description="Why these statements conflict")


class CorroborationLink(BaseModel):
    """Evidence supporting the same fact or claim."""
    claim: str = Field(..., description="The claim or fact being corroborated")
    supporting_evidence: List[str] = Field(
        ..., description="List of SHA256s providing supporting evidence"
    )
    corroboration_strength: Literal["weak", "moderate", "strong"] = Field(
        ..., description="Strength of corroboration"
    )
    explanation: str = Field(..., description="How the evidence corroborates the claim")


class LegalPatternAnalysis(BaseModel):
    """AI-powered analysis of cross-evidence patterns."""
    contradictions: List[Contradiction] = Field(
        default_factory=list,
        description="Conflicting statements across evidence"
    )
    corroboration: List[CorroborationLink] = Field(
        default_factory=list,
        description="Evidence supporting the same claims"
    )
    evidence_gaps: List[str] = Field(
        default_factory=list,
        description="Identified gaps or missing evidence"
    )
    pattern_summary: str = Field(
        ..., description="Overall summary of detected patterns"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in pattern detection"
    )


class CorrelationAnalysis(BaseModel):
    """Results of cross-evidence correlation analysis.

    v3.0: Now uses Pydantic instead of dataclass for validation!
    v3.1: Added legal_patterns for AI-powered contradiction/corroboration detection
    """
    case_id: str = Field(..., description="Case identifier")
    evidence_count: int = Field(..., ge=0, description="Number of evidence pieces analyzed")
    entity_correlations: List[CorrelatedEntity] = Field(
        default_factory=list,
        description="Entities found in 2+ evidence pieces"
    )
    timeline_events: List[TimelineEvent] = Field(
        default_factory=list,
        description="Chronological list of events"
    )
    analysis_timestamp: datetime = Field(..., description="When this correlation analysis was performed")
    temporal_sequences: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detected event patterns using AI classifications"
    )
    timeline_gaps: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Suspicious gaps in evidence timeline"
    )

    # v3.1 Layer 1 enhancement - AI pattern detection
    legal_patterns: Optional[LegalPatternAnalysis] = Field(
        default=None,
        description="AI-detected contradictions, corroboration, and evidence gaps"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            float: lambda v: round(v, 4)
        }


# =============================================================================
# CASE SUMMARY & REPORTING
# =============================================================================

class EvidenceSummary(BaseModel):
    """Summary of a single piece of evidence.

    Used in case summary reports to provide high-level overview of each evidence item.
    Converted from @dataclass to Pydantic for v3.1 consistency.
    """
    sha256: str = Field(..., description="SHA256 hash identifier")
    evidence_type: str = Field(..., description="Type of evidence (document, email, image)")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    analysis_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI analysis confidence score")
    key_findings: List[str] = Field(default_factory=list, description="Bullet points of main findings")
    legal_significance: Optional[str] = Field(None, description="Legal significance level (critical, high, medium, low)")
    risk_flags: List[str] = Field(default_factory=list, description="Risk flags identified in analysis")
    document_type: Optional[str] = Field(None, description="AI-classified document type (email, memo, contract, letter, etc.) - v3.3 Phase B++")


class CaseSummary(BaseModel):
    """Complete case summary with all evidence and analysis.

    Generated by SummaryGenerator to provide comprehensive case overview.
    Converted from @dataclass to Pydantic for v3.1 consistency.
    """
    case_id: str = Field(..., description="Case identifier")
    generation_timestamp: datetime = Field(..., description="When this summary was generated")
    evidence_count: int = Field(..., ge=0, description="Total number of evidence items")
    evidence_types: List[str] = Field(default_factory=list, description="List of evidence types present")
    evidence_summaries: List[EvidenceSummary] = Field(default_factory=list, description="Per-evidence summaries")
    correlation_result: CorrelationAnalysis = Field(..., description="Cross-evidence correlation analysis")
    overall_assessment: Dict[str, Any] = Field(default_factory=dict, description="Aggregated case metrics")
    executive_summary: Optional[str] = Field(None, description="AI-generated executive summary (if enabled)")


# =============================================================================
# OPERATION RESULTS
# =============================================================================

class IngestionResult(BaseModel):
    """Result of evidence ingestion."""
    sha256: str
    file_path: str
    evidence_type: EvidenceType
    metadata: Optional[FileMetadata] = None
    storage_path: str
    success: bool
    message: Optional[str] = None


class ExportResult(BaseModel):
    """Result of evidence export."""
    sha256: str
    export_path: str
    analysis_included: bool
    success: bool
    message: Optional[str] = None


# =============================================================================
# STORAGE MANAGEMENT & CASE OPERATIONS (v3.0 CLI Extensions)
# =============================================================================

class StorageStats(BaseModel):
    """Storage statistics for reporting.

    Used by the `evidence-toolkit storage stats` command to display
    comprehensive storage metrics including evidence counts, sizes,
    and health indicators.
    """
    total_evidence: int = Field(..., ge=0, description="Total evidence items in storage")
    evidence_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Evidence count broken down by type (document, email, image)"
    )
    total_cases: int = Field(..., ge=0, description="Total number of cases")
    total_labels: int = Field(..., ge=0, description="Total number of label categories")
    storage_size_mb: float = Field(..., ge=0.0, description="Total storage size in MB")
    raw_size_mb: float = Field(..., ge=0.0, description="Raw evidence size in MB")
    derived_size_mb: float = Field(..., ge=0.0, description="Derived/analysis size in MB")
    orphaned_files: int = Field(
        default=0,
        ge=0,
        description="Number of evidence files not linked to any case"
    )


class CaseInfo(BaseModel):
    """Case metadata for display.

    Used by case management commands to show case summaries,
    evidence counts, and last modification times.
    """
    case_id: str = Field(..., description="Case identifier")
    evidence_count: int = Field(..., ge=0, description="Number of evidence items in case")
    evidence_types: List[str] = Field(
        default_factory=list,
        description="List of evidence types present in case"
    )
    last_modified: datetime = Field(..., description="Last modification timestamp")
    total_size_mb: float = Field(..., ge=0.0, description="Total size of case evidence in MB")


class CleanupResult(BaseModel):
    """Result of storage cleanup operation.

    Tracks what was cleaned up during a storage cleanup operation,
    including broken links and empty directories.
    """
    broken_links_removed: int = Field(default=0, ge=0, description="Number of broken hard links removed")
    empty_dirs_removed: int = Field(default=0, ge=0, description="Number of empty directories removed")
    orphaned_files: int = Field(default=0, ge=0, description="Number of orphaned files found")
    dry_run: bool = Field(default=False, description="Whether this was a dry-run (no changes made)")


# =============================================================================
# AI ENTITY RESOLUTION (v3.2)
# =============================================================================

class EntityMatchResult(BaseModel):
    """AI-powered entity matching result.

    Determines if two entity names refer to the same real-world entity using
    OpenAI's reasoning with contextual evidence.

    v3.2 feature: Solves correlation gaps where informal names (e.g., "John")
    don't match formal names (e.g., "John Smith") in different evidence pieces.
    """

    is_same_entity: bool = Field(
        description="True if entities refer to the same real-world person/organization"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="AI confidence in the match decision (0.0-1.0)"
    )

    reasoning: str = Field(
        description="Explanation for why entities match or don't match"
    )

    supporting_signals: List[str] = Field(
        default_factory=list,
        description="Context clues supporting the match (e.g., 'same organization')"
    )

    conflicting_signals: List[str] = Field(
        default_factory=list,
        description="Context clues against the match (e.g., 'different roles')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_same_entity": True,
                "confidence": 0.85,
                "reasoning": "Both entities likely refer to the same person. Entity A uses informal first name in casual context while Entity B uses full formal name. Same organization and role mentioned, no conflicting surnames.",
                "supporting_signals": [
                    "same_organization",
                    "same_role_or_position",
                    "temporal_proximity",
                    "no_conflicting_surname"
                ],
                "conflicting_signals": []
            }
        }


class EntityGroup(BaseModel):
    """Group of entity names that refer to the same real-world entity.

    v3.3.1 optimization: Batch entity resolution using single AI call.
    """
    canonical_name: str = Field(
        description="The most complete/formal name to use as canonical reference"
    )
    variant_names: List[str] = Field(
        default_factory=list,
        description="All name variations that refer to this entity (e.g., ['Paul', 'Paul B.', 'PB'])"
    )
    entity_type: str = Field(
        description="Type of entity (person, organization, etc.)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="AI confidence that these names refer to same entity"
    )
    reasoning: str = Field(
        description="Brief explanation of why these names were grouped together"
    )


class BatchEntityResolution(BaseModel):
    """Result of batch entity resolution using single AI call.

    v3.3.1 optimization: Replaces O(n²) pairwise comparisons with single batch analysis.
    Cost: ~$0.01-0.05 per case vs ~$0.50-2.00 with old approach.
    """
    entity_groups: List[EntityGroup] = Field(
        default_factory=list,
        description="Groups of entities that refer to the same real-world entities"
    )
    unmatched_entities: List[str] = Field(
        default_factory=list,
        description="Entity names that couldn't be grouped with others"
    )
    total_input_entities: int = Field(
        ge=0,
        description="Total number of entities provided for resolution"
    )
    groups_created: int = Field(
        ge=0,
        description="Number of entity groups created"
    )
    processing_notes: str = Field(
        default="",
        description="Any notes about the resolution process (edge cases, ambiguities)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "entity_groups": [
                    {
                        "canonical_name": "Paul Boucherat",
                        "variant_names": ["Paul", "Paul B.", "PB"],
                        "entity_type": "person",
                        "confidence": 0.95,
                        "reasoning": "Same person: informal 'Paul' appears in casual contexts, formal 'Paul Boucherat' in official documents, same role/organization"
                    }
                ],
                "unmatched_entities": ["John Smith", "ACAS"],
                "total_input_entities": 6,
                "groups_created": 1,
                "processing_notes": "High confidence matching. No ambiguous cases."
            }
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Versions
    "SCHEMA_VERSION",
    "CROSS_ANALYSIS_SCHEMA_VERSION",

    # Base Types
    "EvidenceType",
    "FileMetadata",
    "ChainOfCustodyEvent",
    "EntityType",

    # AI Analysis
    "DocumentEntity",
    "DocumentAnalysis",
    "ImageAnalysisStructured",
    "EmailParticipant",
    "EscalationEvent",
    "EmailThreadAnalysis",

    # Unified Analysis
    "DocumentAnalysisResult",
    "ImageAnalysisResult",
    "UnifiedAnalysis",

    # Forensic Bundles
    "EvidenceCore",
    "ChainOfCustodyEntry",
    "AnalysisModelInfo",
    "AnalysisParameters",
    "DocumentAnalysisRecord",
    "EvidenceBundle",

    # Cross-Evidence (NOW PYDANTIC!)
    "EvidenceOccurrence",
    "CorrelatedEntity",
    "TimelineEvent",
    "CorrelationAnalysis",

    # v3.1 Legal Pattern Analysis
    "Contradiction",
    "CorroborationLink",
    "LegalPatternAnalysis",

    # Case Summary & Reporting
    "EvidenceSummary",
    "CaseSummary",

    # Operation Results
    "IngestionResult",
    "ExportResult",

    # Storage Management & Case Operations
    "StorageStats",
    "CaseInfo",
    "CleanupResult",

    # v3.2: AI Entity Resolution
    "EntityMatchResult",

    # v3.3.1: Optimized Batch Entity Resolution
    "EntityGroup",
    "BatchEntityResolution",
]
