"""Evidence bundle models for unified Evidence Toolkit architecture.

This module provides Pydantic models that align with the evidence.v1.json schema
format, enabling cross-case analysis and forensic-grade evidence management
across document and image analysis systems.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from .ai_models import DocumentAnalysis


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


class DocumentAnalysisRecord(BaseModel):
    """Analysis record wrapping DocumentAnalysis with metadata."""

    analysis_id: str = Field(..., description="Unique identifier for this analysis")
    created_at: datetime = Field(..., description="When the analysis was performed")

    model: "AnalysisModelInfo" = Field(..., description="AI model information")
    parameters: "AnalysisParameters" = Field(..., description="Analysis parameters")
    outputs: DocumentAnalysis = Field(..., description="Structured analysis results")
    confidence_overall: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")


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


class DocumentEvidenceBundle(BaseModel):
    """Complete evidence bundle for document analysis.

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


# Update forward references for type hints
DocumentAnalysisRecord.model_rebuild()


# Export models for easy import
__all__ = [
    "EvidenceCore",
    "ChainOfCustodyEntry",
    "DocumentAnalysisRecord",
    "AnalysisModelInfo",
    "AnalysisParameters",
    "DocumentEvidenceBundle"
]