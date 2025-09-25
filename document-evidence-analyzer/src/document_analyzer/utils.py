#!/usr/bin/env python3
"""
Utility functions for evidence processing
"""

import hashlib
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import piexif
from PIL import Image
from PIL.ExifTags import TAGS


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract basic file metadata"""
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
    """Extract EXIF data from image files"""
    if not is_image_file(image_path):
        return None

    try:
        with Image.open(image_path) as img:
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif_dict = {}
                exif = img._getexif()

                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    exif_dict[tag] = str(value)

                return exif_dict
    except Exception as e:
        print(f"Warning: Could not extract EXIF from {image_path}: {e}")

    return None


def is_image_file(file_path: Path) -> bool:
    """Check if file is an image based on extension and MIME type"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'}
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in image_extensions or
        (mime_type and mime_type.startswith('image/'))
    )


def is_text_file(file_path: Path) -> bool:
    """Check if file is a text document"""
    text_extensions = {'.txt', '.md', '.doc', '.docx', '.pdf', '.rtf'}
    mime_type, _ = mimetypes.guess_type(str(file_path))

    return (
        file_path.suffix.lower() in text_extensions or
        (mime_type and (mime_type.startswith('text/') or 'document' in mime_type))
    )


def detect_file_type(file_path: Path) -> str:
    """Detect if file is document, image, or other"""
    if is_image_file(file_path):
        return "image"
    elif is_text_file(file_path):
        return "document"
    else:
        return "other"


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist"""
    path.mkdir(parents=True, exist_ok=True)


def create_hard_link(source: Path, target: Path) -> None:
    """Create hard link, ensuring target directory exists"""
    ensure_directory(target.parent)

    # Remove target if it already exists
    if target.exists():
        target.unlink()

    # Create hard link
    os.link(source, target)