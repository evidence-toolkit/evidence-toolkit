#!/usr/bin/env python3
"""Evidence Analysis Pipeline - v3.0

Orchestrates analysis of different evidence types (documents, images, emails).
Extracted from the monolithic CLI for modular v3.0 architecture.

This module is responsible for:
- Evidence type detection and routing
- Analysis orchestration for each evidence type
- UnifiedAnalysis result construction
- Analysis result persistence
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, Any, List, Union

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    EvidenceType,
    FileMetadata,
    UnifiedAnalysis,
    DocumentAnalysisResult,
    ImageAnalysisResult,
    EmailThreadAnalysis,  # v3.1: Use full EmailThreadAnalysis instead of EmailAnalysisResult
    ChainOfCustodyEvent,
)
from evidence_toolkit.core.utils import detect_file_type, extract_exif_data
from evidence_toolkit.analyzers.document import DocumentAnalyzer
from evidence_toolkit.analyzers.image import ImageAnalyzer
from evidence_toolkit.analyzers.email import EmailAnalyzer
from evidence_toolkit.analyzers.email_parser import EmailParser


def _generate_labels(
    evidence_type: EvidenceType,
    analysis_result: Union[DocumentAnalysisResult, ImageAnalysisResult, EmailThreadAnalysis],
    email_metadata: Optional[dict] = None
) -> List[str]:
    """Generate categorical labels for evidence based on analysis results.

    Labels enable browsable hierarchical organization of evidence by:
    - Evidence type (document, image, email)
    - Legal significance (critical, high, medium, low)
    - Risk flags (retaliation, harassment, time_sensitive, etc.)
    - Document classification (contract, letter, email, filing)

    Args:
        evidence_type: Type of evidence analyzed
        analysis_result: Analysis results with extracted fields
        email_metadata: Optional email headers (for email evidence)

    Returns:
        List of label strings for categorization
    """
    labels = []

    # Always add evidence type
    labels.append(evidence_type.value)

    # Extract type-specific labels
    if evidence_type == EvidenceType.DOCUMENT:
        # Add legal significance if available
        if hasattr(analysis_result, 'legal_significance') and analysis_result.legal_significance:
            labels.append(f"{analysis_result.legal_significance}-significance")

        # Add risk flags
        if hasattr(analysis_result, 'risk_flags') and analysis_result.risk_flags:
            labels.extend(analysis_result.risk_flags)

        # Add document type if available
        if hasattr(analysis_result, 'document_type') and analysis_result.document_type:
            labels.append(f"doctype-{analysis_result.document_type}")

    elif evidence_type == EvidenceType.EMAIL:
        # Add legal significance
        if hasattr(analysis_result, 'legal_significance') and analysis_result.legal_significance:
            labels.append(f"{analysis_result.legal_significance}-significance")

        # Add risk flags
        if hasattr(analysis_result, 'risk_flags') and analysis_result.risk_flags:
            labels.extend(analysis_result.risk_flags)

        # Add communication pattern
        if hasattr(analysis_result, 'communication_pattern') and analysis_result.communication_pattern:
            labels.append(f"pattern-{analysis_result.communication_pattern}")

    elif evidence_type == EvidenceType.IMAGE:
        # Images typically don't have legal significance, but might have other labels
        # Add placeholder for future image classification
        labels.append("visual-evidence")

    return labels


def analyze_evidence(
    sha256: str,
    storage: EvidenceStorage,
    openai_client: Optional[Any] = None,
    case_id: Optional[str] = None,
    evidence_type: Optional[str] = None,
    force: bool = False,
    quiet: bool = False
) -> UnifiedAnalysis:
    """Analyze evidence by SHA256 hash.

    This is the main analysis orchestration function that:
    1. Detects evidence type (or uses provided type)
    2. Routes to appropriate analyzer
    3. Constructs UnifiedAnalysis result
    4. Saves analysis to storage

    Args:
        sha256: SHA256 hash of evidence to analyze
        storage: EvidenceStorage instance
        openai_client: Optional OpenAI client for AI analysis
        case_id: Optional case ID to associate with analysis
        evidence_type: Force evidence type (default: auto-detect)
        force: If True, re-analyze even if analysis exists (default: False)
        quiet: Suppress verbose output

    Returns:
        UnifiedAnalysis result object

    Raises:
        FileNotFoundError: If evidence not found for SHA256
        ValueError: If evidence type cannot be determined or is unsupported
    """
    # Check if evidence exists
    original_file = storage.get_original_file_path(sha256)
    if not original_file:
        raise FileNotFoundError(f"No evidence found for SHA256: {sha256}")

    # Check if already analyzed (unless force=True)
    existing_analysis = storage.get_analysis(sha256)
    if existing_analysis and not force:
        if not quiet:
            print(f"⚠️  Analysis already exists for {sha256[:12]}... (use --force to re-analyze)")
        return existing_analysis

    # If forcing re-analysis, backup existing analysis
    if existing_analysis and force:
        import shutil
        analysis_file = storage.derived_dir / f"sha256={sha256}" / "analysis.v1.json"
        if analysis_file.exists():
            backup_file = analysis_file.with_suffix(f".json.backup.{int(time.time())}")
            shutil.copy2(analysis_file, backup_file)
            if not quiet:
                print(f"🔄 Backed up existing analysis to {backup_file.name}")

    # Detect or use provided evidence type
    if evidence_type == 'auto' or evidence_type is None:
        detected_type = detect_file_type(original_file)
        evidence_type_enum = EvidenceType(detected_type)
    else:
        evidence_type_enum = EvidenceType(evidence_type)

    if not quiet:
        print(f"🔍 Analyzing {evidence_type_enum.value} evidence: {sha256[:12]}...")

    # Load metadata
    metadata_file = storage.derived_dir / f"sha256={sha256}" / "metadata.json"
    with open(metadata_file, 'r') as f:
        metadata_dict = json.load(f)

    file_metadata = FileMetadata(**metadata_dict)

    # Perform analysis based on type
    email_metadata = None
    # Create derived directory path for storing visualizations
    derived_evidence_dir = storage.derived_dir / f"sha256={sha256}"

    if evidence_type_enum == EvidenceType.DOCUMENT:
        analysis_result = _analyze_document(original_file, quiet, output_dir=derived_evidence_dir)
    elif evidence_type_enum == EvidenceType.IMAGE:
        analysis_result = _analyze_image(original_file, openai_client, quiet)
    elif evidence_type_enum == EvidenceType.EMAIL:
        analysis_result, email_metadata = _analyze_email(original_file, openai_client, case_id, quiet)
    elif evidence_type_enum in (EvidenceType.VIDEO, EvidenceType.AUDIO):
        # v3.2: VIDEO and AUDIO files are ingested but not analyzed yet
        # Skip analysis gracefully - they will still be tracked in chain of custody
        raise ValueError(f"Analysis not yet implemented for {evidence_type_enum.value} files (ingestion only)")
    else:
        raise ValueError(f"Cannot analyze evidence type: {evidence_type_enum.value}")

    # Generate labels for categorization
    labels = _generate_labels(
        evidence_type_enum,
        analysis_result,
        email_metadata
    )

    # Create unified analysis
    unified_analysis = UnifiedAnalysis(
        evidence_type=evidence_type_enum,
        analysis_timestamp=datetime.now(),
        file_metadata=file_metadata,
        case_id=case_id,
        document_analysis=analysis_result if evidence_type_enum == EvidenceType.DOCUMENT else None,
        image_analysis=analysis_result if evidence_type_enum == EvidenceType.IMAGE else None,
        email_analysis=analysis_result if evidence_type_enum == EvidenceType.EMAIL else None,
        exif_data=extract_exif_data(original_file) if evidence_type_enum == EvidenceType.IMAGE else None,
        email_metadata=email_metadata,
        labels=labels
    )

    # Save analysis
    success = storage.save_analysis(unified_analysis)
    if not success:
        raise RuntimeError(f"Failed to save analysis for {sha256}")

    if not quiet:
        print(f"✅ Analysis completed for {sha256[:12]}...")

    return unified_analysis


def _analyze_document(file_path: Path, quiet: bool = False, output_dir: Path = None) -> DocumentAnalysisResult:
    """Analyze document using DocumentAnalyzer.

    Args:
        file_path: Path to document file
        quiet: Suppress verbose output
        output_dir: Directory to save visualizations (word cloud, frequency chart)

    Returns:
        DocumentAnalysisResult object
    """
    analyzer = DocumentAnalyzer(
        custom_stop_words=None,
        min_word_length=3,
        verbose=not quiet
    )

    # Analyze the text file
    result = analyzer.analyze_directory(
        data_dir=file_path.parent,
        output_dir=output_dir,  # Save visualizations to derived storage
        file_pattern=file_path.name
    )

    if result['status'] != 'success':
        raise RuntimeError(f"Document analysis failed: {result.get('message', 'Unknown error')}")

    # Convert to DocumentAnalysisResult
    top_words = sorted(result['word_frequency'].items(), key=lambda x: x[1], reverse=True)[:20]

    # Extract AI analysis if available
    ai_analysis = result.get('ai_analysis')

    return DocumentAnalysisResult(
        # Legacy word frequency fields
        total_words=result['total_words'],
        unique_words=result['unique_words'],
        word_frequency=result['word_frequency'],
        top_words=top_words,
        wordcloud_file=result.get('wordcloud_file'),
        frequency_chart_file=result.get('frequency_chart_file'),

        # AI-powered analysis fields (if available)
        openai_model="gpt-4o-mini" if ai_analysis else None,  # Fixed from gpt-4.1-mini
        ai_summary=ai_analysis.get('summary') if ai_analysis else None,
        entities=ai_analysis.get('entities') if ai_analysis else None,
        document_type=ai_analysis.get('document_type') if ai_analysis else None,
        sentiment=ai_analysis.get('sentiment') if ai_analysis else None,
        legal_significance=ai_analysis.get('legal_significance') if ai_analysis else None,
        risk_flags=ai_analysis.get('risk_flags') if ai_analysis else None,
        analysis_confidence=ai_analysis.get('confidence_overall') if ai_analysis else None
    )


def _analyze_image(
    file_path: Path,
    openai_client: Optional[Any],
    quiet: bool = False
) -> ImageAnalysisResult:
    """Analyze image or scanned PDF using ImageAnalyzer with vision AI.

    Args:
        file_path: Path to image/PDF file
        openai_client: OpenAI client for vision analysis
        quiet: Suppress verbose output

    Returns:
        ImageAnalysisResult object
    """
    image_analyzer = ImageAnalyzer(verbose=not quiet)

    # Check if this is a PDF (scanned PDF routed as 'image' type)
    if file_path.suffix.lower() == '.pdf':
        # Scanned PDF - analyze all pages with vision AI
        return image_analyzer.analyze_pdf(file_path)
    else:
        # Regular image file
        return image_analyzer.analyze_image(file_path)


def _analyze_email(
    file_path: Path,
    openai_client: Optional[Any],
    case_id: Optional[str],
    quiet: bool = False
) -> Tuple[EmailThreadAnalysis, Optional[dict]]:
    """Analyze email using EmailAnalyzer and extract metadata.

    Args:
        file_path: Path to email file
        openai_client: OpenAI client for AI analysis
        case_id: Case ID for analysis
        quiet: Suppress verbose output

    Returns:
        Tuple of (EmailThreadAnalysis, email_metadata dict) - v3.1: Returns full analysis with participants
    """
    # Initialize OpenAI client check
    if openai_client is None and not quiet:
        print("⚠️  OpenAI client not available - email analysis may be limited")

    # Parse email to extract headers
    email_parser = EmailParser(verbose=not quiet)
    email_data = email_parser.parse_file(file_path)

    # Extract email metadata from headers
    email_metadata = None
    if email_data and 'headers' in email_data:
        email_metadata = {
            'from': email_data['headers'].get('from'),
            'to': email_data['headers'].get('to'),
            'cc': email_data['headers'].get('cc'),
            'subject': email_data['headers'].get('subject'),
            'date': email_data['headers'].get('date'),
            'parsed_date': email_data['headers'].get('parsed_date'),
            'message_id': email_data['headers'].get('message_id')
        }

    # Initialize email analyzer
    email_analyzer = EmailAnalyzer(openai_client, verbose=not quiet)

    # Analyze the email file
    analysis = email_analyzer.analyze_email_files([file_path], case_id=case_id)

    if not analysis:
        raise RuntimeError("Email analysis failed - no results returned")

    # v3.1: Return full EmailThreadAnalysis (preserves participants with v3.1 fields)
    return analysis, email_metadata


__all__ = [
    'analyze_evidence',
]
