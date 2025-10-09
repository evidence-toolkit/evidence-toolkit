#!/usr/bin/env python3
"""Utility functions for evidence processing.

v3.0: Cleaned up imports, no changes to functionality.
"""

import hashlib
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract basic file metadata."""
    stat = file_path.stat()
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return {
        "filename": file_path.name,
        "file_size": stat.st_size,
        "mime_type": mime_type,
        "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": file_path.suffix.lower()
    }


def extract_exif_data(image_path: Path) -> Optional[Dict[str, Any]]:
    """Extract EXIF data from image files using modern PIL API."""
    if not is_image_file(image_path):
        return None

    try:
        with Image.open(image_path) as img:
            exif = img.getexif()

            if exif is not None and len(exif) > 0:
                exif_dict = {}

                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_dict[tag] = str(value)

                return exif_dict
    except Exception as e:
        print(f"Warning: Could not extract EXIF from {image_path}: {e}")

    return None


def is_image_file(file_path: Path) -> bool:
    """Check if file is an image based on extension and MIME type."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in image_extensions or
        (mime_type and mime_type.startswith('image/'))
    )


def is_text_file(file_path: Path) -> bool:
    """Check if file is a text document."""
    text_extensions = {'.txt', '.md', '.doc', '.docx', '.pdf', '.rtf'}
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in text_extensions or
        (mime_type and (mime_type.startswith('text/') or 'document' in mime_type))
    )


def is_email_file(file_path: Path) -> bool:
    """Check if file is an email."""
    email_extensions = {'.eml', '.msg', '.mbox', '.mbx'}
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in email_extensions or
        (mime_type and 'message' in mime_type)
    )


def is_video_file(file_path: Path) -> bool:
    """Check if file is a video."""
    video_extensions = {
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.3gp', '.ogv'
    }
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in video_extensions or
        (mime_type and mime_type.startswith('video/'))
    )


def is_audio_file(file_path: Path) -> bool:
    """Check if file is an audio file."""
    audio_extensions = {
        '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma',
        '.opus', '.aiff', '.ape', '.alac'
    }
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in audio_extensions or
        (mime_type and mime_type.startswith('audio/'))
    )


def detect_file_type(file_path: Path) -> str:
    """Detect if file is document, image, email, video, audio, or other."""
    # Check email files first
    if is_email_file(file_path):
        return "email"

    # Check video and audio files (v3.2: added support)
    if is_video_file(file_path):
        return "video"

    if is_audio_file(file_path):
        return "audio"

    # Special handling for PDFs - check if text is extractable
    if file_path.suffix.lower() == '.pdf':
        if _can_extract_pdf_text(file_path):
            return "document"  # Route to DocumentAnalyzer for text analysis
        else:
            return "image"     # Route to ImageAnalyzer for OCR + visual analysis

    # Existing logic for other file types
    if is_image_file(file_path):
        return "image"
    elif is_text_file(file_path):
        return "document"
    else:
        return "other"


def _can_extract_pdf_text(file_path: Path) -> bool:
    """Check if PDF has extractable text content."""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                return False
            # Test first page for meaningful text content
            text = pdf.pages[0].extract_text()
            return text and len(text.strip()) > 50  # Meaningful text threshold
    except Exception:
        return False  # Encrypted, corrupted, or image-only PDF


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def create_hard_link(source: Path, target: Path) -> None:
    """Create hard link, ensuring target directory exists."""
    ensure_directory(target.parent)

    # Remove target if it already exists
    if target.exists():
        target.unlink()

    # Create hard link
    os.link(source, target)


# =============================================================================
# DEDUPLICATION UTILITIES (v3.3+)
# =============================================================================

def read_json_safe(path: Path) -> Optional[Dict[str, Any]]:
    """Read JSON file with forensic-grade error handling.

    Returns None on failure but preserves specific error types for debugging.
    Used across pipeline and analyzer modules to eliminate duplication.
    """
    import json
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return None


def get_evidence_base_dir(derived_dir: Path, sha256: str) -> Path:
    """Get base evidence directory for SHA256 hash.

    This centralizes the evidence directory path construction pattern that
    was duplicated 23+ times across the codebase. All evidence files
    (analysis.v1.json, metadata.json, exif.json, chain_of_custody.json,
    evidence_bundle.v1.json) live in this directory.

    Args:
        derived_dir: Base derived storage directory path
        sha256: Evidence SHA256 hash

    Returns:
        Path to evidence base directory: derived_dir/sha256={sha256}/

    Example:
        >>> evidence_dir = get_evidence_base_dir(storage.derived_dir, "abc123...")
        >>> analysis_file = evidence_dir / "analysis.v1.json"
        >>> metadata_file = evidence_dir / "metadata.json"
    """
    return derived_dir / f"sha256={sha256}"


def call_openai_structured(
    client,
    model: str,
    system_prompt: str,
    user_content: str,
    response_schema,
    verbose: bool = False
):
    """Call OpenAI Responses API with standardized error handling.

    This eliminates 9 instances of duplicated API call + error handling code
    across document, email, image, correlation, and summary modules.

    Args:
        client: OpenAI client instance
        model: Model name (e.g., "gpt-4o-2024-08-06")
        system_prompt: System prompt text
        user_content: User message (string or dict for image inputs)
        response_schema: Pydantic model for structured output
        verbose: Enable verbose logging

    Returns:
        Parsed response object matching response_schema

    Raises:
        Exception: If API call fails, is incomplete, or refused
    """
    # Build input messages
    if isinstance(user_content, str):
        input_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
    else:
        # Dict format for image/complex inputs
        input_messages = [
            {"role": "system", "content": system_prompt},
            user_content
        ]

    # Call API
    response = client.responses.parse(
        model=model,
        input=input_messages,
        text_format=response_schema
    )

    # Handle response with standard pattern
    if response.status == "completed" and response.output_parsed:
        return response.output_parsed

    elif response.status == "incomplete":
        raise Exception(f"API response incomplete: {response.incomplete_details}")

    else:
        # Check for refusal
        if (response.output and len(response.output) > 0 and
            len(response.output[0].content) > 0 and
            response.output[0].content[0].type == "refusal"):
            raise Exception(f"API refused: {response.output[0].content[0].refusal}")
        raise Exception("API call failed with unknown error")
