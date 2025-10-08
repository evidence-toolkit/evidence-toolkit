"""Pydantic models for email analysis using OpenAI Responses API.

This module provides structured data models for email thread analysis using
the OpenAI Responses API (NOT chat completions API). These models ensure
deterministic, forensic-grade analysis suitable for legal evidence processing.

Follows the same patterns as DocumentAnalysis for consistency across
the Evidence Toolkit.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0.0"


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
        # Ensure deterministic serialization for legal use
        json_encoders = {
            float: lambda v: round(v, 4)  # Consistent precision for confidence scores
        }


# Export models for easy import
__all__ = [
    "SCHEMA_VERSION",
    "EmailParticipant",
    "EscalationEvent",
    "EmailThreadAnalysis"
]