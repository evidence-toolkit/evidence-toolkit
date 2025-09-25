#!/usr/bin/env python3
"""
Pydantic models for unified evidence analysis
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EvidenceType(str, Enum):
    """Types of evidence that can be analyzed"""
    DOCUMENT = "document"
    IMAGE = "image"
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
    total_words: int
    unique_words: int
    word_frequency: Dict[str, int]
    top_words: List[tuple] = Field(description="Top 20 most frequent words")
    wordcloud_file: Optional[str] = None
    frequency_chart_file: Optional[str] = None


class ImageAnalysisResult(BaseModel):
    """Results from image analysis"""
    openai_model: str
    openai_response: Dict[str, Any]
    detected_objects: Optional[List[str]] = None
    detected_text: Optional[str] = None
    scene_description: Optional[str] = None
    analysis_confidence: Optional[float] = None


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
    case_id: Optional[str] = None

    # Analysis results (only one will be populated based on evidence_type)
    document_analysis: Optional[DocumentAnalysisResult] = None
    image_analysis: Optional[ImageAnalysisResult] = None

    # Chain of custody
    chain_of_custody: List[ChainOfCustodyEvent] = Field(default_factory=list)

    # EXIF data for images
    exif_data: Optional[Dict[str, Any]] = None

    # Additional metadata
    labels: List[str] = Field(default_factory=list, description="Detected labels/categories")
    notes: Optional[str] = None


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