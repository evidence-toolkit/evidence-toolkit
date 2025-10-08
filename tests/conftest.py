"""Pytest configuration and shared fixtures for Evidence Toolkit tests.

This module provides reusable test fixtures for creating temporary storage,
sample evidence files, and mock OpenAI clients.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Generator
import pytest

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    FileMetadata,
    EvidenceType,
    ChainOfCustodyEvent,
)


@pytest.fixture
def tmp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test isolation.

    Yields:
        Path to temporary directory (cleaned up after test)
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="evidence_test_"))
    yield temp_dir
    # Cleanup
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def tmp_storage(tmp_dir: Path) -> EvidenceStorage:
    """Create a temporary EvidenceStorage instance for testing.

    Args:
        tmp_dir: Temporary directory fixture

    Returns:
        EvidenceStorage instance with temporary root
    """
    storage_root = tmp_dir / "storage"
    storage_root.mkdir(parents=True, exist_ok=True)
    return EvidenceStorage(storage_root)


@pytest.fixture
def sample_document(tmp_dir: Path) -> Path:
    """Create a sample text document for testing.

    Args:
        tmp_dir: Temporary directory fixture

    Returns:
        Path to sample document file
    """
    doc_path = tmp_dir / "test_document.txt"
    content = """Employee Workplace Safety Memo

From: John Smith, Safety Manager
To: Sarah Johnson, HR Director
Date: 2024-01-15

Subject: Urgent - Workplace Safety Violations

Dear Sarah,

I am writing to formally document serious safety violations observed in Building A.
The following issues require immediate attention:

1. Emergency exits blocked by storage containers
2. Fire extinguishers expired (last inspection: 2022)
3. Missing safety signage in hazardous areas

I request a meeting with the Chief Executive Officer to discuss remediation.

This matter is time-sensitive and requires executive-level review.

Best regards,
John Smith
Safety Manager
"""
    doc_path.write_text(content)
    return doc_path


@pytest.fixture
def sample_email(tmp_dir: Path) -> Path:
    """Create a sample .eml file for testing.

    Args:
        tmp_dir: Temporary directory fixture

    Returns:
        Path to sample email file
    """
    email_path = tmp_dir / "test_email.eml"
    content = """From: john.smith@company.com
To: sarah.johnson@company.com
Subject: RE: Safety Review Meeting
Date: Mon, 15 Jan 2024 14:30:00 -0500
Message-ID: <abc123@company.com>

Hi Sarah,

Following up on my previous memo regarding the safety violations in Building A.

I need to escalate this to the CEO if we don't see immediate action.

The deadline for compliance is January 30, 2024.

Regards,
John
"""
    email_path.write_text(content)
    return email_path


@pytest.fixture
def sample_image(tmp_dir: Path) -> Path:
    """Create a minimal sample image file for testing.

    Args:
        tmp_dir: Temporary directory fixture

    Returns:
        Path to sample image file
    """
    from PIL import Image

    img_path = tmp_dir / "test_image.jpg"
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(img_path)
    return img_path


@pytest.fixture
def sample_case_dir(tmp_dir: Path, sample_document: Path, sample_email: Path) -> Path:
    """Create a sample case directory with multiple evidence files.

    Args:
        tmp_dir: Temporary directory fixture
        sample_document: Sample document fixture
        sample_email: Sample email fixture

    Returns:
        Path to case directory containing evidence files
    """
    case_dir = tmp_dir / "TEST-CASE-001"
    case_dir.mkdir(parents=True)

    # Copy sample files to case directory
    shutil.copy(sample_document, case_dir / "document.txt")
    shutil.copy(sample_email, case_dir / "email.eml")

    return case_dir


@pytest.fixture
def case_id() -> str:
    """Provide a consistent test case ID.

    Returns:
        Test case identifier
    """
    return "TEST-CASE-001"


@pytest.fixture
def mock_openai_responses():
    """Provide mock OpenAI API responses for deterministic testing.

    Returns:
        Dictionary of mock responses keyed by evidence type
    """
    return {
        "document": {
            "summary": "Workplace safety memo documenting serious violations",
            "entities": [
                {
                    "name": "John Smith",
                    "type": "person",
                    "confidence": 0.95,
                    "context": "Safety Manager writing the memo"
                },
                {
                    "name": "Sarah Johnson",
                    "type": "person",
                    "confidence": 0.95,
                    "context": "HR Director receiving the memo"
                },
                {
                    "name": "Chief Executive Officer",
                    "type": "person",
                    "confidence": 0.9,
                    "context": "Requested meeting recipient"
                }
            ],
            "document_type": "letter",
            "sentiment": "professional",
            "legal_significance": "high",
            "risk_flags": ["time_sensitive"],
            "confidence_overall": 0.92
        },
        "email": {
            "thread_summary": "Email escalation regarding safety violations",
            "participants": [
                {
                    "email_address": "john.smith@company.com",
                    "display_name": "John Smith",
                    "role": "sender",
                    "authority_level": "management",
                    "confidence": 0.95
                },
                {
                    "email_address": "sarah.johnson@company.com",
                    "display_name": "Sarah Johnson",
                    "role": "recipient",
                    "authority_level": "management",
                    "confidence": 0.95
                }
            ],
            "communication_pattern": "escalating",
            "sentiment_progression": [0.7, 0.5],
            "escalation_events": [
                {
                    "email_position": 0,
                    "escalation_type": "deadline",
                    "confidence": 0.85,
                    "description": "Deadline mentioned for compliance",
                    "context": "The deadline for compliance is January 30, 2024"
                }
            ],
            "legal_significance": "high",
            "risk_flags": ["deadline", "threatening"],
            "timeline_reconstruction": ["Initial memo sent", "Follow-up escalation"],
            "confidence_overall": 0.88
        },
        "image": {
            "scene_description": "Test image - red background",
            "detected_text": None,
            "detected_objects": [],
            "people_present": False,
            "timestamps_visible": False,
            "potential_evidence_value": "low",
            "analysis_notes": "Simple test image without forensic value",
            "confidence_overall": 0.95,
            "risk_flags": []
        }
    }


@pytest.fixture
def mock_openai_client(mock_openai_responses):
    """Create a mock OpenAI client for deterministic testing.

    Args:
        mock_openai_responses: Mock responses fixture

    Returns:
        Mock OpenAI client that returns deterministic responses
    """
    class MockParsedResponse:
        def __init__(self, data):
            self.parsed = self._dict_to_obj(data)

        def _dict_to_obj(self, d):
            """Convert dict to object with attribute access"""
            if isinstance(d, dict):
                return type('obj', (), {k: self._dict_to_obj(v) for k, v in d.items()})
            elif isinstance(d, list):
                return [self._dict_to_obj(item) for item in d]
            return d

    class MockBeta:
        def __init__(self, responses):
            self.responses = responses
            self.chat = self
            self.completions = self

        def parse(self, **kwargs):
            """Mock the beta.chat.completions.parse method"""
            # Determine which response to use based on messages
            messages = kwargs.get('messages', [])

            # Simple heuristic: check content for keywords
            content = str(messages).lower()

            if 'email' in content or 'participant' in content:
                return MockParsedResponse(self.responses['email'])
            elif 'image' in content or 'scene' in content:
                return MockParsedResponse(self.responses['image'])
            else:
                return MockParsedResponse(self.responses['document'])

    class MockOpenAI:
        def __init__(self, responses):
            self.beta = MockBeta(responses)

    return MockOpenAI(mock_openai_responses)


# Test utilities
def create_test_file_metadata(filename: str, sha256: str) -> FileMetadata:
    """Create test FileMetadata instance.

    Args:
        filename: Name of the file
        sha256: SHA256 hash value

    Returns:
        FileMetadata instance for testing
    """
    return FileMetadata(
        filename=filename,
        file_size=1024,
        mime_type="text/plain",
        created_time=datetime.now().isoformat(),
        modified_time=datetime.now().isoformat(),
        extension=".txt",
        sha256=sha256
    )


def create_test_custody_event(event_type: str = "ingest") -> ChainOfCustodyEvent:
    """Create test ChainOfCustodyEvent instance.

    Args:
        event_type: Type of custody event

    Returns:
        ChainOfCustodyEvent instance for testing
    """
    return ChainOfCustodyEvent(
        timestamp=datetime.now(),
        event_type=event_type,
        actor="test_user",
        description=f"Test {event_type} event",
        metadata={"test": True}
    )
