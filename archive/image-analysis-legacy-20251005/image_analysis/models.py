"""Pydantic models that mirror ``schemas/images.v1.json``."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SCHEMA_VERSION = "1.0.0"


class ChainOfCustodyEntry(BaseModel):
    ts: datetime
    actor: str
    action: str
    note: Optional[str] = None


class DetectedObject(BaseModel):
    label: str
    bbox: Optional[List[float]] = Field(
        default=None,
        description="[x, y, width, height] normalized to 0..1",
    )
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class AnalysisParameters(BaseModel):
    temperature: Optional[float] = Field(default=None, le=0.0)
    prompt_hash: Optional[str] = None
    token_usage_in: Optional[int] = None
    token_usage_out: Optional[int] = None


class AnalysisModelInfo(BaseModel):
    name: str
    revision: str


class AnalysisOutputs(BaseModel):
    summary: Optional[str] = None
    objects: List[DetectedObject] = Field(default_factory=list)
    text_found: Optional[str] = None
    risk_flags: List[
        Literal["low_quality", "tampering_suspected", "ocr_ambiguous", "nsfw", "pii"]
    ] = Field(default_factory=list)


class ImageAnalysisResponse(BaseModel):
    """OpenAI structured output model for image analysis responses.

    This model defines the expected response format from OpenAI's Responses API
    for forensic image analysis, ensuring automatic validation and type safety.
    """
    summary: str = Field(..., description="Executive summary of image content")
    objects: List[DetectedObject] = Field(
        default_factory=list,
        description="Detected objects with bounding boxes and confidence scores"
    )
    text_found: Optional[str] = Field(
        default=None,
        description="OCR text extracted from the image"
    )
    risk_flags: List[
        Literal["low_quality", "tampering_suspected", "ocr_ambiguous", "nsfw", "pii"]
    ] = Field(
        default_factory=list,
        description="Risk assessment flags for legal evidence processing"
    )
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0,
        description="Overall confidence in the complete analysis"
    )


class AnalysisRecord(BaseModel):
    analysis_id: str
    created_at: datetime
    model: AnalysisModelInfo
    parameters: AnalysisParameters
    outputs: AnalysisOutputs
    confidence_overall: float = Field(ge=0.0, le=1.0)


class EvidenceCore(BaseModel):
    evidence_id: str
    sha256: str
    mime_type: str
    bytes: int = Field(ge=1)
    width_px: Optional[int] = Field(default=None, ge=1)
    height_px: Optional[int] = Field(default=None, ge=1)
    phash: Optional[str] = None
    ingested_at: datetime
    source_path: str


class EvidenceBundle(BaseModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    case_id: Optional[str] = None
    evidence: EvidenceCore
    chain_of_custody: List[ChainOfCustodyEntry] = Field(default_factory=list)
    analyses: List[AnalysisRecord]

    model_config = {
        "json_encoders": {datetime: lambda dt: dt.isoformat()},
    }


__all__ = [
    "SCHEMA_VERSION",
    "ChainOfCustodyEntry",
    "DetectedObject",
    "AnalysisParameters",
    "AnalysisModelInfo",
    "AnalysisOutputs",
    "ImageAnalysisResponse",
    "AnalysisRecord",
    "EvidenceCore",
    "EvidenceBundle",
]
