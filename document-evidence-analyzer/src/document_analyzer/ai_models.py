"""Pydantic models for OpenAI Responses API integration.

This module provides structured data models for document analysis using
the OpenAI Responses API (NOT chat completions API). These models ensure
deterministic, forensic-grade analysis suitable for legal evidence processing.
"""

from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0.0"


class DocumentEntity(BaseModel):
    """Represents an extracted entity from document analysis."""
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
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the complete analysis"
    )

    class Config:
        """Pydantic configuration for forensic compliance."""
        # Ensure deterministic serialization for legal use
        json_encoders = {
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }


# Export models for easy import
__all__ = [
    "SCHEMA_VERSION",
    "DocumentEntity",
    "DocumentAnalysis"
]