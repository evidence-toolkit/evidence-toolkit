#!/usr/bin/env python3
"""
Pydantic models for unified evidence analysis
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class EvidenceType(str, Enum):
    """Types of evidence that can be analyzed"""
    DOCUMENT = "document"
    IMAGE = "image"
    EMAIL = "email"
    OTHER = "other"


class FileMetadata(BaseModel):
    """Basic file metadata"""
    filename: str
    file_size: int
    mime_type: Optional[str] = None
    created_time: str
    modified_time: str
    extension: str
    sha256: str


class DocumentAnalysisResult(BaseModel):
    """Results from document text analysis"""
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
    """Results from image analysis"""
    openai_model: str
    openai_response: Dict[str, Any]
    detected_objects: Optional[List[str]] = None
    detected_text: Optional[str] = None
    scene_description: Optional[str] = None
    analysis_confidence: Optional[float] = None


class EmailAnalysisResult(BaseModel):
    """Results from email thread analysis"""
    thread_summary: str
    participant_count: int
    communication_pattern: str
    legal_significance: str
    risk_flags: List[str] = Field(default_factory=list)
    escalation_events: List[str] = Field(default_factory=list)
    confidence_overall: float


class ChainOfCustodyEvent(BaseModel):
    """Chain of custody tracking event"""
    timestamp: datetime
    event_type: str  # "ingest", "analyze", "export", etc.
    actor: str
    description: str
    metadata: Optional[Dict[str, Any]] = None


class UnifiedAnalysis(BaseModel):
    """Unified analysis result for any evidence type"""
    evidence_type: EvidenceType
    analysis_timestamp: datetime
    file_metadata: FileMetadata

    # Multi-case support
    case_ids: List[str] = Field(default_factory=list, description="Cases this evidence belongs to")
    case_id: Optional[str] = Field(default=None, description="Deprecated: Use case_ids instead")

    # Analysis results (only one will be populated based on evidence_type)
    document_analysis: Optional[DocumentAnalysisResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None
    email_analysis: Optional[EmailAnalysisResult] = None

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
        """Auto-sync case_id and case_ids for backward compatibility"""
        if self.case_id and not self.case_ids:
            self.case_ids = [self.case_id]
        elif self.case_ids and not self.case_id:
            self.case_id = self.case_ids[0] if self.case_ids else None
        return self


class IngestionResult(BaseModel):
    """Result of evidence ingestion"""
    sha256: str
    file_path: str
    evidence_type: EvidenceType
    metadata: FileMetadata
    storage_path: str
    success: bool
    message: Optional[str] = None


class ExportResult(BaseModel):
    """Result of evidence export"""
    sha256: str
    export_path: str
    analysis_included: bool
    success: bool
    message: Optional[str] = None