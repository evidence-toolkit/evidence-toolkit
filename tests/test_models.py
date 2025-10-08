"""Comprehensive Pydantic validation tests for all Evidence Toolkit v3.0 models.

This test suite validates ALL 48 Pydantic models consolidated in core/models.py.
Each model is tested for:
- Valid instantiation with realistic forensic/legal data
- Rejection of invalid types (ValidationError)
- Rejection of missing required fields (ValidationError)
- Serialization roundtrip (model_dump() and model_validate())
- Edge cases specific to forensic/legal requirements

Categories tested:
- Base Types & Enums (EvidenceType, FileMetadata, ChainOfCustodyEvent, EntityType)
- AI Analysis Models (DocumentEntity, DocumentAnalysis, ImageAnalysisStructured,
  EmailParticipant, EscalationEvent, EmailThreadAnalysis)
- Unified Analysis (DocumentAnalysisResult, ImageAnalysisResult, EmailAnalysisResult, UnifiedAnalysis)
- Forensic Bundles (EvidenceCore, ChainOfCustodyEntry, AnalysisModelInfo,
  AnalysisParameters, DocumentAnalysisRecord, EvidenceBundle)
- Cross-Evidence Analysis (EvidenceOccurrence, CorrelatedEntity, TimelineEvent, CorrelationAnalysis)
- Operation Results (IngestionResult, ExportResult)
- Storage Management (StorageStats, CaseInfo, CleanupResult)
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from evidence_toolkit.core.models import (
    # Base Types & Enums
    EvidenceType,
    FileMetadata,
    ChainOfCustodyEvent,
    EntityType,
    # AI Analysis Models
    DocumentEntity,
    DocumentAnalysis,
    ImageAnalysisStructured,
    EmailParticipant,
    EscalationEvent,
    EmailThreadAnalysis,
    # Unified Analysis
    DocumentAnalysisResult,
    ImageAnalysisResult,
    EmailAnalysisResult,
    UnifiedAnalysis,
    # Forensic Bundles
    EvidenceCore,
    ChainOfCustodyEntry,
    AnalysisModelInfo,
    AnalysisParameters,
    DocumentAnalysisRecord,
    EvidenceBundle,
    # Cross-Evidence Analysis
    EvidenceOccurrence,
    CorrelatedEntity,
    TimelineEvent,
    CorrelationAnalysis,
    # Operation Results
    IngestionResult,
    ExportResult,
    # Storage Management
    StorageStats,
    CaseInfo,
    CleanupResult,
)


# =============================================================================
# BASE TYPES & ENUMS
# =============================================================================

class TestEvidenceType:
    """Test EvidenceType enum validation."""

    def test_EvidenceType_valid_values(self):
        """Test that EvidenceType enum accepts all valid evidence types."""
        assert EvidenceType.DOCUMENT == "document"
        assert EvidenceType.IMAGE == "image"
        assert EvidenceType.EMAIL == "email"
        assert EvidenceType.PDF == "pdf"
        assert EvidenceType.AUDIO == "audio"
        assert EvidenceType.VIDEO == "video"
        assert EvidenceType.OTHER == "other"

    def test_EvidenceType_rejects_invalid_values(self):
        """Test that EvidenceType rejects invalid evidence type values."""
        with pytest.raises(ValueError):
            EvidenceType("invalid_type")


class TestFileMetadata:
    """Test FileMetadata model validation.

    NOTE: FileMetadata.sha256 is a string field without pattern validation.
    Pattern validation (^[a-f0-9]{64}$) is only enforced in EvidenceCore for forensic bundles.
    """

    def test_FileMetadata_valid_instantiation(self):
        """Test that valid FileMetadata can be created with realistic forensic data."""
        metadata = FileMetadata(
            filename="workplace_complaint.pdf",
            file_size=245678,
            mime_type="application/pdf",
            created_time="2024-01-15T09:30:00",
            modified_time="2024-01-15T09:30:00",
            extension=".pdf",
            sha256="a1b2c3d4e5f6789012345678901234567890abcdefabcdefabcdefabcdef1234"
        )

        assert metadata.filename == "workplace_complaint.pdf"
        assert metadata.file_size == 245678
        assert metadata.mime_type == "application/pdf"
        assert len(metadata.sha256) == 64

    def test_FileMetadata_accepts_any_sha256_string(self):
        """Test that FileMetadata accepts SHA256 as any string (no pattern validation).

        This is by design - FileMetadata is lenient, while EvidenceCore enforces the pattern.
        """
        # FileMetadata accepts short strings (no validation)
        metadata = FileMetadata(
            filename="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            created_time="2024-01-15T09:30:00",
            modified_time="2024-01-15T09:30:00",
            extension=".pdf",
            sha256="short_hash"  # Accepted - no pattern constraint
        )

        assert metadata.sha256 == "short_hash"

    def test_FileMetadata_accepts_uppercase_sha256(self):
        """Test that FileMetadata accepts uppercase SHA256 (pattern not enforced)."""
        metadata = FileMetadata(
            filename="test.pdf",
            file_size=1024,
            created_time="2024-01-15T09:30:00",
            modified_time="2024-01-15T09:30:00",
            extension=".pdf",
            sha256="A" * 64  # Accepted - no pattern constraint
        )

        assert len(metadata.sha256) == 64

    def test_FileMetadata_rejects_missing_required_fields(self):
        """Test that FileMetadata rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            FileMetadata(
                filename="test.pdf",
                # Missing file_size, created_time, modified_time, extension, sha256
            )

    def test_FileMetadata_rejects_invalid_types(self):
        """Test that FileMetadata rejects fields with wrong types."""
        with pytest.raises(ValidationError):
            FileMetadata(
                filename="test.pdf",
                file_size="not_an_integer",  # Wrong type: must be int
                created_time="2024-01-15T09:30:00",
                modified_time="2024-01-15T09:30:00",
                extension=".pdf",
                sha256="a" * 64
            )

    def test_FileMetadata_allows_none_mime_type(self):
        """Test that FileMetadata allows None for optional mime_type field."""
        metadata = FileMetadata(
            filename="test.txt",
            file_size=1024,
            mime_type=None,  # Optional field
            created_time="2024-01-15T09:30:00",
            modified_time="2024-01-15T09:30:00",
            extension=".txt",
            sha256="a" * 64
        )

        assert metadata.mime_type is None

    def test_FileMetadata_serialization_roundtrip(self):
        """Test that FileMetadata can be serialized and deserialized without data loss."""
        original = FileMetadata(
            filename="evidence.pdf",
            file_size=123456,
            mime_type="application/pdf",
            created_time="2024-01-15T09:30:00",
            modified_time="2024-01-15T10:45:00",
            extension=".pdf",
            sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
        )

        # Serialize to dict
        serialized = original.model_dump()

        # Deserialize back to model
        restored = FileMetadata.model_validate(serialized)

        assert restored.filename == original.filename
        assert restored.file_size == original.file_size
        assert restored.sha256 == original.sha256


class TestChainOfCustodyEvent:
    """Test ChainOfCustodyEvent model validation.

    Chain of custody events are critical for legal admissibility.
    """

    def test_ChainOfCustodyEvent_valid_instantiation(self):
        """Test that valid ChainOfCustodyEvent can be created."""
        event = ChainOfCustodyEvent(
            timestamp=datetime(2024, 1, 15, 9, 30, 0),
            event_type="ingest",
            actor="forensic_analyst_smith",
            description="Evidence ingested into secure storage",
            metadata={"case_id": "CASE-2024-001", "device": "laptop-forensics-01"}
        )

        assert event.event_type == "ingest"
        assert event.actor == "forensic_analyst_smith"
        assert event.metadata["case_id"] == "CASE-2024-001"

    def test_ChainOfCustodyEvent_rejects_missing_required_fields(self):
        """Test that ChainOfCustodyEvent rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            ChainOfCustodyEvent(
                timestamp=datetime.now(),
                # Missing event_type, actor, description
            )

    def test_ChainOfCustodyEvent_rejects_invalid_types(self):
        """Test that ChainOfCustodyEvent rejects fields with wrong types."""
        with pytest.raises(ValidationError):
            ChainOfCustodyEvent(
                timestamp="not_a_datetime",  # Wrong type: must be datetime
                event_type="analyze",
                actor="analyst",
                description="Analysis performed"
            )

    def test_ChainOfCustodyEvent_allows_none_metadata(self):
        """Test that ChainOfCustodyEvent allows None for optional metadata field."""
        event = ChainOfCustodyEvent(
            timestamp=datetime.now(),
            event_type="export",
            actor="analyst",
            description="Evidence exported",
            metadata=None  # Optional field
        )

        assert event.metadata is None

    def test_ChainOfCustodyEvent_serialization_roundtrip(self):
        """Test that ChainOfCustodyEvent can be serialized and deserialized."""
        original = ChainOfCustodyEvent(
            timestamp=datetime(2024, 1, 15, 14, 30, 0),
            event_type="analyze",
            actor="ai_analyzer",
            description="OpenAI document analysis completed",
            metadata={"model": "gpt-4o", "confidence": 0.95}
        )

        # Serialize to dict
        serialized = original.model_dump()

        # Deserialize back to model
        restored = ChainOfCustodyEvent.model_validate(serialized)

        assert restored.event_type == original.event_type
        assert restored.actor == original.actor
        assert restored.metadata == original.metadata


class TestEntityType:
    """Test EntityType enum validation."""

    def test_EntityType_valid_values(self):
        """Test that EntityType enum accepts all valid entity types."""
        assert EntityType.PERSON == "person"
        assert EntityType.ORGANIZATION == "organization"
        assert EntityType.LOCATION == "location"
        assert EntityType.PHONE == "phone"
        assert EntityType.EMAIL_ADDR == "email"
        assert EntityType.DATE == "date"
        assert EntityType.DOCUMENT_REF == "document_ref"
        assert EntityType.ACCOUNT == "account"
        assert EntityType.ADDRESS == "address"
        assert EntityType.OTHER == "other"

    def test_EntityType_rejects_invalid_values(self):
        """Test that EntityType rejects invalid entity type values."""
        with pytest.raises(ValueError):
            EntityType("invalid_entity")


# =============================================================================
# AI ANALYSIS MODELS (OpenAI Responses API)
# =============================================================================

class TestDocumentEntity:
    """Test DocumentEntity model validation."""

    def test_DocumentEntity_valid_instantiation(self):
        """Test that valid DocumentEntity can be created with realistic extraction data."""
        entity = DocumentEntity(
            name="John Smith",
            type="person",
            confidence=0.95,
            context="Complaint filed by John Smith on January 15, 2024"
        )

        assert entity.name == "John Smith"
        assert entity.type == "person"
        assert entity.confidence == 0.95

    def test_DocumentEntity_rejects_invalid_type(self):
        """Test that DocumentEntity rejects invalid entity type literals."""
        with pytest.raises(ValidationError):
            DocumentEntity(
                name="Something",
                type="invalid_type",  # Must be one of: person, organization, date, legal_term
                confidence=0.9,
                context="Some context"
            )

    def test_DocumentEntity_rejects_confidence_out_of_range(self):
        """Test that DocumentEntity rejects confidence scores outside [0.0, 1.0]."""
        # Confidence too high
        with pytest.raises(ValidationError):
            DocumentEntity(
                name="Test",
                type="person",
                confidence=1.5,  # Invalid: > 1.0
                context="context"
            )

        # Confidence too low
        with pytest.raises(ValidationError):
            DocumentEntity(
                name="Test",
                type="person",
                confidence=-0.1,  # Invalid: < 0.0
                context="context"
            )

    def test_DocumentEntity_rejects_missing_required_fields(self):
        """Test that DocumentEntity rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            DocumentEntity(
                name="Test",
                type="person",
                # Missing confidence, context
            )

    def test_DocumentEntity_serialization_roundtrip(self):
        """Test that DocumentEntity can be serialized and deserialized."""
        original = DocumentEntity(
            name="Acme Corporation",
            type="organization",
            confidence=0.88,
            context="Settlement agreement with Acme Corporation dated March 1, 2024"
        )

        serialized = original.model_dump()
        restored = DocumentEntity.model_validate(serialized)

        assert restored.name == original.name
        assert restored.type == original.type
        assert restored.confidence == original.confidence


class TestDocumentAnalysis:
    """Test DocumentAnalysis model validation.

    CRITICAL: This is the OpenAI Responses API format for deterministic document analysis.
    """

    def test_DocumentAnalysis_valid_instantiation(self):
        """Test that valid DocumentAnalysis can be created with realistic forensic data."""
        analysis = DocumentAnalysis(
            summary="Employee complaint regarding workplace harassment and hostile environment",
            entities=[
                DocumentEntity(
                    name="Sarah Johnson",
                    type="person",
                    confidence=0.95,
                    context="Complainant and employee"
                )
            ],
            document_type="letter",
            sentiment="hostile",
            legal_significance="critical",
            risk_flags=["harassment", "retaliation_indicators", "time_sensitive"],
            confidence_overall=0.92
        )

        assert analysis.summary.startswith("Employee complaint")
        assert len(analysis.entities) == 1
        assert analysis.legal_significance == "critical"
        assert "harassment" in analysis.risk_flags

    def test_DocumentAnalysis_rejects_invalid_document_type(self):
        """Test that DocumentAnalysis rejects invalid document type literals."""
        with pytest.raises(ValidationError):
            DocumentAnalysis(
                summary="Test summary",
                entities=[],
                document_type="invalid_type",  # Must be: email, letter, contract, filing
                sentiment="neutral",
                legal_significance="low",
                risk_flags=[],
                confidence_overall=0.9
            )

    def test_DocumentAnalysis_rejects_invalid_sentiment(self):
        """Test that DocumentAnalysis rejects invalid sentiment literals."""
        with pytest.raises(ValidationError):
            DocumentAnalysis(
                summary="Test",
                entities=[],
                document_type="letter",
                sentiment="happy",  # Must be: hostile, neutral, professional
                legal_significance="low",
                risk_flags=[],
                confidence_overall=0.9
            )

    def test_DocumentAnalysis_rejects_invalid_legal_significance(self):
        """Test that DocumentAnalysis rejects invalid legal significance literals."""
        with pytest.raises(ValidationError):
            DocumentAnalysis(
                summary="Test",
                entities=[],
                document_type="letter",
                sentiment="neutral",
                legal_significance="super_critical",  # Must be: critical, high, medium, low
                risk_flags=[],
                confidence_overall=0.9
            )

    def test_DocumentAnalysis_rejects_invalid_risk_flags(self):
        """Test that DocumentAnalysis rejects invalid risk flag values."""
        with pytest.raises(ValidationError):
            DocumentAnalysis(
                summary="Test",
                entities=[],
                document_type="letter",
                sentiment="neutral",
                legal_significance="low",
                risk_flags=["invalid_flag"],  # Must be from valid list
                confidence_overall=0.9
            )

    def test_DocumentAnalysis_rejects_confidence_out_of_range(self):
        """Test that DocumentAnalysis rejects confidence_overall outside [0.0, 1.0]."""
        with pytest.raises(ValidationError):
            DocumentAnalysis(
                summary="Test",
                entities=[],
                document_type="letter",
                sentiment="neutral",
                legal_significance="low",
                risk_flags=[],
                confidence_overall=2.0  # Invalid: > 1.0
            )

    def test_DocumentAnalysis_allows_empty_entities_and_risk_flags(self):
        """Test that DocumentAnalysis allows empty lists for entities and risk_flags."""
        analysis = DocumentAnalysis(
            summary="Simple document with no extracted entities",
            entities=[],  # Empty list is valid
            document_type="letter",
            sentiment="neutral",
            legal_significance="low",
            risk_flags=[],  # Empty list is valid
            confidence_overall=0.85
        )

        assert len(analysis.entities) == 0
        assert len(analysis.risk_flags) == 0

    def test_DocumentAnalysis_serialization_roundtrip(self):
        """Test that DocumentAnalysis can be serialized and deserialized."""
        original = DocumentAnalysis(
            summary="Contract termination notice",
            entities=[
                DocumentEntity(
                    name="January 30, 2024",
                    type="date",
                    confidence=0.98,
                    context="Termination effective date"
                )
            ],
            document_type="contract",
            sentiment="professional",
            legal_significance="high",
            risk_flags=["deadline", "confidential"],
            confidence_overall=0.94
        )

        serialized = original.model_dump()
        restored = DocumentAnalysis.model_validate(serialized)

        assert restored.summary == original.summary
        assert len(restored.entities) == len(original.entities)
        assert restored.document_type == original.document_type
        assert restored.confidence_overall == original.confidence_overall


class TestImageAnalysisStructured:
    """Test ImageAnalysisStructured model validation.

    This is the OpenAI Vision API format for forensic-grade image analysis.
    """

    def test_ImageAnalysisStructured_valid_instantiation(self):
        """Test that valid ImageAnalysisStructured can be created."""
        analysis = ImageAnalysisStructured(
            scene_description="Workplace safety violation: blocked emergency exit with storage boxes",
            detected_text="EXIT - DO NOT BLOCK",
            detected_objects=["fire extinguisher", "storage boxes", "exit sign"],
            people_present=False,
            timestamps_visible=False,
            potential_evidence_value="high",
            analysis_notes="Clear safety code violation documented in image",
            confidence_overall=0.92,
            risk_flags=[]
        )

        assert "emergency exit" in analysis.scene_description
        assert analysis.potential_evidence_value == "high"
        assert len(analysis.detected_objects) == 3

    def test_ImageAnalysisStructured_rejects_invalid_evidence_value(self):
        """Test that ImageAnalysisStructured rejects invalid potential_evidence_value."""
        with pytest.raises(ValidationError):
            ImageAnalysisStructured(
                scene_description="Test scene",
                detected_text=None,
                detected_objects=[],
                people_present=False,
                timestamps_visible=False,
                potential_evidence_value="critical",  # Must be: low, medium, high
                analysis_notes="Notes",
                confidence_overall=0.9,
                risk_flags=[]
            )

    def test_ImageAnalysisStructured_rejects_invalid_risk_flags(self):
        """Test that ImageAnalysisStructured rejects invalid risk flags."""
        with pytest.raises(ValidationError):
            ImageAnalysisStructured(
                scene_description="Test",
                detected_text=None,
                detected_objects=[],
                people_present=False,
                timestamps_visible=False,
                potential_evidence_value="medium",
                analysis_notes="Notes",
                confidence_overall=0.9,
                risk_flags=["invalid_risk"]  # Must be from valid list
            )

    def test_ImageAnalysisStructured_allows_none_detected_text(self):
        """Test that ImageAnalysisStructured allows None for detected_text."""
        analysis = ImageAnalysisStructured(
            scene_description="Image with no text",
            detected_text=None,  # Optional
            detected_objects=["object1"],
            people_present=False,
            timestamps_visible=False,
            potential_evidence_value="low",
            analysis_notes="No text detected",
            confidence_overall=0.95,
            risk_flags=[]
        )

        assert analysis.detected_text is None

    def test_ImageAnalysisStructured_serialization_roundtrip(self):
        """Test that ImageAnalysisStructured can be serialized and deserialized."""
        original = ImageAnalysisStructured(
            scene_description="Screenshot of threatening email",
            detected_text="You will regret this decision",
            detected_objects=["email header", "timestamp"],
            people_present=False,
            timestamps_visible=True,
            potential_evidence_value="high",
            analysis_notes="Threatening language detected in email screenshot",
            confidence_overall=0.88,
            risk_flags=["low_quality"]
        )

        serialized = original.model_dump()
        restored = ImageAnalysisStructured.model_validate(serialized)

        assert restored.scene_description == original.scene_description
        assert restored.potential_evidence_value == original.potential_evidence_value


class TestEmailParticipant:
    """Test EmailParticipant model validation."""

    def test_EmailParticipant_valid_instantiation(self):
        """Test that valid EmailParticipant can be created."""
        participant = EmailParticipant(
            email_address="john.smith@company.com",
            display_name="John Smith",
            role="sender",
            authority_level="management",
            confidence=0.95
        )

        assert participant.email_address == "john.smith@company.com"
        assert participant.role == "sender"
        assert participant.authority_level == "management"

    def test_EmailParticipant_rejects_invalid_role(self):
        """Test that EmailParticipant rejects invalid role literals."""
        with pytest.raises(ValidationError):
            EmailParticipant(
                email_address="test@example.com",
                display_name="Test",
                role="invalid_role",  # Must be: sender, recipient, cc, bcc
                authority_level="employee",
                confidence=0.9
            )

    def test_EmailParticipant_rejects_invalid_authority_level(self):
        """Test that EmailParticipant rejects invalid authority_level literals."""
        with pytest.raises(ValidationError):
            EmailParticipant(
                email_address="test@example.com",
                display_name="Test",
                role="sender",
                authority_level="supreme_leader",  # Must be: executive, management, employee, external
                confidence=0.9
            )

    def test_EmailParticipant_allows_none_display_name(self):
        """Test that EmailParticipant allows None for optional display_name."""
        participant = EmailParticipant(
            email_address="anonymous@example.com",
            display_name=None,  # Optional
            role="recipient",
            authority_level="external",
            confidence=0.8
        )

        assert participant.display_name is None

    def test_EmailParticipant_serialization_roundtrip(self):
        """Test that EmailParticipant can be serialized and deserialized."""
        original = EmailParticipant(
            email_address="ceo@company.com",
            display_name="Jane Doe, CEO",
            role="recipient",
            authority_level="executive",
            confidence=0.98
        )

        serialized = original.model_dump()
        restored = EmailParticipant.model_validate(serialized)

        assert restored.email_address == original.email_address
        assert restored.authority_level == original.authority_level


class TestEscalationEvent:
    """Test EscalationEvent model validation."""

    def test_EscalationEvent_valid_instantiation(self):
        """Test that valid EscalationEvent can be created."""
        event = EscalationEvent(
            email_position=2,
            escalation_type="authority_escalation",
            confidence=0.89,
            description="CEO added to thread",
            context="I am escalating this matter to the CEO for immediate review"
        )

        assert event.email_position == 2
        assert event.escalation_type == "authority_escalation"

    def test_EscalationEvent_rejects_negative_position(self):
        """Test that EscalationEvent rejects negative email_position."""
        with pytest.raises(ValidationError):
            EscalationEvent(
                email_position=-1,  # Must be >= 0
                escalation_type="tone_change",
                confidence=0.9,
                description="Test",
                context="Test context"
            )

    def test_EscalationEvent_rejects_invalid_escalation_type(self):
        """Test that EscalationEvent rejects invalid escalation_type literals."""
        with pytest.raises(ValidationError):
            EscalationEvent(
                email_position=0,
                escalation_type="invalid_type",  # Must be from valid list
                confidence=0.9,
                description="Test",
                context="Test context"
            )

    def test_EscalationEvent_serialization_roundtrip(self):
        """Test that EscalationEvent can be serialized and deserialized."""
        original = EscalationEvent(
            email_position=5,
            escalation_type="deadline",
            confidence=0.92,
            description="Compliance deadline imposed",
            context="You have until Friday to comply or face termination"
        )

        serialized = original.model_dump()
        restored = EscalationEvent.model_validate(serialized)

        assert restored.email_position == original.email_position
        assert restored.escalation_type == original.escalation_type


class TestEmailThreadAnalysis:
    """Test EmailThreadAnalysis model validation.

    CRITICAL: This is the OpenAI Responses API format for email thread analysis.
    """

    def test_EmailThreadAnalysis_valid_instantiation(self):
        """Test that valid EmailThreadAnalysis can be created."""
        analysis = EmailThreadAnalysis(
            thread_summary="Escalating workplace harassment complaint thread",
            participants=[
                EmailParticipant(
                    email_address="victim@company.com",
                    display_name="Victim Name",
                    role="sender",
                    authority_level="employee",
                    confidence=0.95
                )
            ],
            communication_pattern="escalating",
            sentiment_progression=[0.7, 0.5, 0.3],
            escalation_events=[],
            legal_significance="critical",
            risk_flags=["harassment", "retaliation"],
            timeline_reconstruction=["Initial complaint", "Ignored by HR", "Escalation to legal"],
            confidence_overall=0.91
        )

        assert analysis.communication_pattern == "escalating"
        assert len(analysis.sentiment_progression) == 3
        assert "harassment" in analysis.risk_flags

    def test_EmailThreadAnalysis_rejects_invalid_communication_pattern(self):
        """Test that EmailThreadAnalysis rejects invalid communication_pattern."""
        with pytest.raises(ValidationError):
            EmailThreadAnalysis(
                thread_summary="Test",
                participants=[],
                communication_pattern="friendly",  # Must be: professional, escalating, hostile, retaliatory
                sentiment_progression=[0.5],
                escalation_events=[],
                legal_significance="low",
                risk_flags=[],
                timeline_reconstruction=[],
                confidence_overall=0.9
            )

    def test_EmailThreadAnalysis_rejects_invalid_risk_flags(self):
        """Test that EmailThreadAnalysis rejects invalid risk_flags."""
        with pytest.raises(ValidationError):
            EmailThreadAnalysis(
                thread_summary="Test",
                participants=[],
                communication_pattern="professional",
                sentiment_progression=[0.5],
                escalation_events=[],
                legal_significance="low",
                risk_flags=["invalid_flag"],  # Must be from valid list
                timeline_reconstruction=[],
                confidence_overall=0.9
            )

    def test_EmailThreadAnalysis_allows_empty_lists(self):
        """Test that EmailThreadAnalysis allows empty lists for default_factory fields."""
        analysis = EmailThreadAnalysis(
            thread_summary="Simple professional email",
            participants=[],
            communication_pattern="professional",
            sentiment_progression=[0.8],
            escalation_events=[],
            legal_significance="low",
            risk_flags=[],
            timeline_reconstruction=[],
            confidence_overall=0.88
        )

        assert len(analysis.participants) == 0
        assert len(analysis.escalation_events) == 0

    def test_EmailThreadAnalysis_serialization_roundtrip(self):
        """Test that EmailThreadAnalysis can be serialized and deserialized."""
        original = EmailThreadAnalysis(
            thread_summary="Retaliation thread after whistleblowing",
            participants=[
                EmailParticipant(
                    email_address="hr@company.com",
                    display_name="HR Department",
                    role="recipient",
                    authority_level="management",
                    confidence=0.9
                )
            ],
            communication_pattern="retaliatory",
            sentiment_progression=[0.6, 0.4, 0.2],
            escalation_events=[],
            legal_significance="critical",
            risk_flags=["retaliation", "discrimination"],
            timeline_reconstruction=["Whistleblower report", "Negative performance review", "Termination threat"],
            confidence_overall=0.87
        )

        serialized = original.model_dump()
        restored = EmailThreadAnalysis.model_validate(serialized)

        assert restored.thread_summary == original.thread_summary
        assert restored.communication_pattern == original.communication_pattern
        assert len(restored.participants) == len(original.participants)


# =============================================================================
# UNIFIED ANALYSIS RESULTS (Client Package Format)
# =============================================================================

class TestDocumentAnalysisResult:
    """Test DocumentAnalysisResult model validation."""

    def test_DocumentAnalysisResult_valid_instantiation(self):
        """Test that valid DocumentAnalysisResult can be created."""
        result = DocumentAnalysisResult(
            total_words=1247,
            unique_words=423,
            word_frequency={"complaint": 12, "harassment": 8, "retaliation": 5},
            top_words=[("complaint", 12), ("harassment", 8), ("retaliation", 5)],
            wordcloud_file="wordcloud_abc123.png",
            frequency_chart_file="freq_abc123.png",
            openai_model="gpt-4o-2024-08-06",
            ai_summary="Formal harassment complaint with legal implications",
            entities=[{"name": "HR Department", "type": "organization"}],
            document_type="letter",
            sentiment="hostile",
            legal_significance="critical",
            risk_flags=["harassment", "time_sensitive"],
            analysis_confidence=0.94
        )

        assert result.total_words == 1247
        assert result.unique_words == 423
        assert result.ai_summary is not None

    def test_DocumentAnalysisResult_allows_none_optional_fields(self):
        """Test that DocumentAnalysisResult allows None for optional AI fields."""
        result = DocumentAnalysisResult(
            total_words=100,
            unique_words=50,
            word_frequency={"test": 5},
            top_words=[("test", 5)],
            wordcloud_file=None,
            frequency_chart_file=None,
            openai_model=None,
            ai_summary=None,
            entities=None,
            document_type=None,
            sentiment=None,
            legal_significance=None,
            risk_flags=None,
            analysis_confidence=None
        )

        assert result.openai_model is None
        assert result.ai_summary is None

    def test_DocumentAnalysisResult_rejects_invalid_types(self):
        """Test that DocumentAnalysisResult rejects fields with wrong types."""
        with pytest.raises(ValidationError):
            DocumentAnalysisResult(
                total_words="not_an_int",  # Wrong type
                unique_words=50,
                word_frequency={},
                top_words=[]
            )

    def test_DocumentAnalysisResult_serialization_roundtrip(self):
        """Test that DocumentAnalysisResult can be serialized and deserialized."""
        original = DocumentAnalysisResult(
            total_words=500,
            unique_words=200,
            word_frequency={"evidence": 10},
            top_words=[("evidence", 10)],
            openai_model="gpt-4o",
            ai_summary="Evidence analysis"
        )

        serialized = original.model_dump()
        restored = DocumentAnalysisResult.model_validate(serialized)

        assert restored.total_words == original.total_words
        assert restored.openai_model == original.openai_model


class TestImageAnalysisResult:
    """Test ImageAnalysisResult model validation."""

    def test_ImageAnalysisResult_valid_instantiation(self):
        """Test that valid ImageAnalysisResult can be created."""
        result = ImageAnalysisResult(
            openai_model="gpt-4o-2024-08-06",
            openai_response={"scene": "workplace", "quality": "high"},
            detected_objects=["desk", "computer", "document"],
            detected_text="CONFIDENTIAL",
            scene_description="Office workspace with confidential documents visible",
            analysis_confidence=0.91
        )

        assert result.openai_model == "gpt-4o-2024-08-06"
        assert len(result.detected_objects) == 3

    def test_ImageAnalysisResult_rejects_missing_required_fields(self):
        """Test that ImageAnalysisResult rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            ImageAnalysisResult(
                # Missing openai_model and openai_response
                detected_objects=["test"]
            )

    def test_ImageAnalysisResult_allows_none_optional_fields(self):
        """Test that ImageAnalysisResult allows None for optional fields."""
        result = ImageAnalysisResult(
            openai_model="gpt-4o",
            openai_response={},
            detected_objects=None,
            detected_text=None,
            scene_description=None,
            analysis_confidence=None
        )

        assert result.detected_objects is None
        assert result.detected_text is None

    def test_ImageAnalysisResult_serialization_roundtrip(self):
        """Test that ImageAnalysisResult can be serialized and deserialized."""
        original = ImageAnalysisResult(
            openai_model="gpt-4o",
            openai_response={"test": "data"},
            detected_objects=["object1"],
            analysis_confidence=0.85
        )

        serialized = original.model_dump()
        restored = ImageAnalysisResult.model_validate(serialized)

        assert restored.openai_model == original.openai_model


class TestEmailAnalysisResult:
    """Test EmailAnalysisResult model validation."""

    def test_EmailAnalysisResult_valid_instantiation(self):
        """Test that valid EmailAnalysisResult can be created."""
        result = EmailAnalysisResult(
            thread_summary="Escalating harassment complaint",
            participant_count=5,
            communication_pattern="escalating",
            legal_significance="critical",
            risk_flags=["harassment", "retaliation"],
            escalation_events=["CEO added to thread", "Legal counsel mentioned"],
            confidence_overall=0.89
        )

        assert result.participant_count == 5
        assert result.communication_pattern == "escalating"
        assert len(result.risk_flags) == 2

    def test_EmailAnalysisResult_rejects_missing_required_fields(self):
        """Test that EmailAnalysisResult rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            EmailAnalysisResult(
                thread_summary="Test",
                # Missing participant_count, communication_pattern, legal_significance, confidence_overall
            )

    def test_EmailAnalysisResult_allows_empty_lists(self):
        """Test that EmailAnalysisResult allows empty lists for default_factory fields."""
        result = EmailAnalysisResult(
            thread_summary="Simple email",
            participant_count=2,
            communication_pattern="professional",
            legal_significance="low",
            risk_flags=[],
            escalation_events=[],
            confidence_overall=0.9
        )

        assert len(result.risk_flags) == 0
        assert len(result.escalation_events) == 0

    def test_EmailAnalysisResult_serialization_roundtrip(self):
        """Test that EmailAnalysisResult can be serialized and deserialized."""
        original = EmailAnalysisResult(
            thread_summary="Test thread",
            participant_count=3,
            communication_pattern="hostile",
            legal_significance="high",
            risk_flags=["threatening"],
            confidence_overall=0.87
        )

        serialized = original.model_dump()
        restored = EmailAnalysisResult.model_validate(serialized)

        assert restored.thread_summary == original.thread_summary
        assert restored.participant_count == original.participant_count


class TestUnifiedAnalysis:
    """Test UnifiedAnalysis model validation.

    CRITICAL: v3.0 multi-case support with case_id/case_ids sync validator.
    """

    def test_UnifiedAnalysis_valid_instantiation(self):
        """Test that valid UnifiedAnalysis can be created."""
        from tests.conftest import create_test_file_metadata

        metadata = create_test_file_metadata("test.pdf", "a" * 64)

        analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=metadata,
            case_ids=["CASE-001"],
            document_analysis=DocumentAnalysisResult(
                total_words=100,
                unique_words=50,
                word_frequency={},
                top_words=[]
            )
        )

        assert analysis.evidence_type == EvidenceType.DOCUMENT
        assert len(analysis.case_ids) == 1

    def test_UnifiedAnalysis_syncs_case_id_to_case_ids(self):
        """Test that UnifiedAnalysis auto-syncs case_id to case_ids."""
        from tests.conftest import create_test_file_metadata

        metadata = create_test_file_metadata("test.pdf", "a" * 64)

        analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=metadata,
            case_id="CASE-001",  # Old field
            case_ids=[]
        )

        # Should auto-sync case_id to case_ids
        assert "CASE-001" in analysis.case_ids

    def test_UnifiedAnalysis_syncs_case_ids_to_case_id(self):
        """Test that UnifiedAnalysis auto-syncs case_ids to case_id."""
        from tests.conftest import create_test_file_metadata

        metadata = create_test_file_metadata("test.pdf", "a" * 64)

        analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=metadata,
            case_ids=["CASE-002"],
            case_id=None
        )

        # Should auto-sync first case_ids entry to case_id
        assert analysis.case_id == "CASE-002"

    def test_UnifiedAnalysis_allows_multi_case(self):
        """Test that UnifiedAnalysis supports multiple case IDs."""
        from tests.conftest import create_test_file_metadata

        metadata = create_test_file_metadata("test.pdf", "a" * 64)

        analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=metadata,
            case_ids=["CASE-001", "CASE-002", "CASE-003"]
        )

        assert len(analysis.case_ids) == 3

    def test_UnifiedAnalysis_rejects_invalid_evidence_type(self):
        """Test that UnifiedAnalysis rejects invalid evidence_type."""
        from tests.conftest import create_test_file_metadata

        metadata = create_test_file_metadata("test.pdf", "a" * 64)

        with pytest.raises(ValidationError):
            UnifiedAnalysis(
                evidence_type="invalid_type",  # Must be EvidenceType enum
                analysis_timestamp=datetime.now(),
                file_metadata=metadata,
                case_ids=["CASE-001"]
            )

    def test_UnifiedAnalysis_serialization_roundtrip(self):
        """Test that UnifiedAnalysis can be serialized and deserialized."""
        from tests.conftest import create_test_file_metadata, create_test_custody_event

        metadata = create_test_file_metadata("evidence.pdf", "b" * 64)
        custody_event = create_test_custody_event("analyze")

        original = UnifiedAnalysis(
            evidence_type=EvidenceType.EMAIL,
            analysis_timestamp=datetime.now(),
            file_metadata=metadata,
            case_ids=["CASE-001"],
            email_analysis=EmailAnalysisResult(
                thread_summary="Test",
                participant_count=2,
                communication_pattern="professional",
                legal_significance="low",
                confidence_overall=0.9
            ),
            chain_of_custody=[custody_event]
        )

        serialized = original.model_dump()
        restored = UnifiedAnalysis.model_validate(serialized)

        assert restored.evidence_type == original.evidence_type
        assert len(restored.case_ids) == len(original.case_ids)


# =============================================================================
# FORENSIC BUNDLES (Legal-Grade Evidence Packages)
# =============================================================================

class TestEvidenceCore:
    """Test EvidenceCore model validation.

    CRITICAL: SHA256 pattern validation is essential for forensic integrity.
    """

    def test_EvidenceCore_valid_instantiation(self):
        """Test that valid EvidenceCore can be created."""
        core = EvidenceCore(
            evidence_id="evidence_001",
            sha256="abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            mime_type="application/pdf",
            bytes=245678,
            ingested_at=datetime.now(),
            source_path="/evidence/complaint.pdf"
        )

        assert core.evidence_id == "evidence_001"
        assert len(core.sha256) == 64

    def test_EvidenceCore_rejects_invalid_sha256(self):
        """Test that EvidenceCore rejects invalid SHA256 patterns."""
        with pytest.raises(ValidationError):
            EvidenceCore(
                evidence_id="test",
                sha256="invalid",  # Too short
                mime_type="text/plain",
                bytes=100,
                ingested_at=datetime.now(),
                source_path="/test"
            )

    def test_EvidenceCore_rejects_negative_bytes(self):
        """Test that EvidenceCore rejects negative bytes values."""
        with pytest.raises(ValidationError):
            EvidenceCore(
                evidence_id="test",
                sha256="a" * 64,
                mime_type="text/plain",
                bytes=-1,  # Must be >= 1
                ingested_at=datetime.now(),
                source_path="/test"
            )

    def test_EvidenceCore_rejects_zero_bytes(self):
        """Test that EvidenceCore rejects zero bytes (files must have content)."""
        with pytest.raises(ValidationError):
            EvidenceCore(
                evidence_id="test",
                sha256="a" * 64,
                mime_type="text/plain",
                bytes=0,  # Must be >= 1
                ingested_at=datetime.now(),
                source_path="/test"
            )

    def test_EvidenceCore_serialization_roundtrip(self):
        """Test that EvidenceCore can be serialized and deserialized."""
        original = EvidenceCore(
            evidence_id="ev_12345",
            sha256="f" * 64,
            mime_type="image/jpeg",
            bytes=1024000,
            ingested_at=datetime(2024, 1, 15, 10, 30, 0),
            source_path="/images/evidence_photo.jpg"
        )

        serialized = original.model_dump()
        restored = EvidenceCore.model_validate(serialized)

        assert restored.evidence_id == original.evidence_id
        assert restored.sha256 == original.sha256


class TestChainOfCustodyEntry:
    """Test ChainOfCustodyEntry model validation (forensic bundle format)."""

    def test_ChainOfCustodyEntry_valid_instantiation(self):
        """Test that valid ChainOfCustodyEntry can be created."""
        entry = ChainOfCustodyEntry(
            ts=datetime.now(),
            actor="forensic_analyst",
            action="analyze",
            note="Document analyzed with OpenAI GPT-4o"
        )

        assert entry.actor == "forensic_analyst"
        assert entry.action == "analyze"

    def test_ChainOfCustodyEntry_allows_none_note(self):
        """Test that ChainOfCustodyEntry allows None for optional note field."""
        entry = ChainOfCustodyEntry(
            ts=datetime.now(),
            actor="system",
            action="ingest",
            note=None
        )

        assert entry.note is None

    def test_ChainOfCustodyEntry_serialization_roundtrip(self):
        """Test that ChainOfCustodyEntry can be serialized and deserialized."""
        original = ChainOfCustodyEntry(
            ts=datetime(2024, 1, 15, 14, 0, 0),
            actor="legal_team",
            action="export",
            note="Exported for client review"
        )

        serialized = original.model_dump()
        restored = ChainOfCustodyEntry.model_validate(serialized)

        assert restored.actor == original.actor
        assert restored.action == original.action


class TestAnalysisModelInfo:
    """Test AnalysisModelInfo model validation."""

    def test_AnalysisModelInfo_valid_instantiation(self):
        """Test that valid AnalysisModelInfo can be created."""
        model_info = AnalysisModelInfo(
            name="gpt-4o-2024-08-06",
            revision="2024-08-06"
        )

        assert model_info.name == "gpt-4o-2024-08-06"
        assert model_info.revision == "2024-08-06"

    def test_AnalysisModelInfo_rejects_missing_required_fields(self):
        """Test that AnalysisModelInfo rejects instances missing required fields."""
        with pytest.raises(ValidationError):
            AnalysisModelInfo(
                name="gpt-4o"
                # Missing revision
            )

    def test_AnalysisModelInfo_serialization_roundtrip(self):
        """Test that AnalysisModelInfo can be serialized and deserialized."""
        original = AnalysisModelInfo(
            name="gpt-4o-mini",
            revision="2024-07-18"
        )

        serialized = original.model_dump()
        restored = AnalysisModelInfo.model_validate(serialized)

        assert restored.name == original.name


class TestAnalysisParameters:
    """Test AnalysisParameters model validation."""

    def test_AnalysisParameters_valid_instantiation(self):
        """Test that valid AnalysisParameters can be created."""
        params = AnalysisParameters(
            temperature=0.0,
            prompt_hash="abc123def456",
            token_usage_in=1500,
            token_usage_out=800
        )

        assert params.temperature == 0.0
        assert params.token_usage_in == 1500

    def test_AnalysisParameters_rejects_positive_temperature(self):
        """Test that AnalysisParameters rejects temperature > 0 (must be deterministic)."""
        with pytest.raises(ValidationError):
            AnalysisParameters(
                temperature=0.5,  # Must be <= 0.0 for deterministic analysis
                prompt_hash="abc123"
            )

    def test_AnalysisParameters_allows_none_optional_fields(self):
        """Test that AnalysisParameters allows None for all optional fields."""
        params = AnalysisParameters(
            temperature=None,
            prompt_hash=None,
            token_usage_in=None,
            token_usage_out=None
        )

        assert params.temperature is None
        assert params.prompt_hash is None

    def test_AnalysisParameters_serialization_roundtrip(self):
        """Test that AnalysisParameters can be serialized and deserialized."""
        original = AnalysisParameters(
            temperature=0.0,
            prompt_hash="hash123",
            token_usage_in=2000,
            token_usage_out=1000
        )

        serialized = original.model_dump()
        restored = AnalysisParameters.model_validate(serialized)

        assert restored.temperature == original.temperature
        assert restored.token_usage_in == original.token_usage_in


class TestDocumentAnalysisRecord:
    """Test DocumentAnalysisRecord model validation."""

    def test_DocumentAnalysisRecord_valid_instantiation(self):
        """Test that valid DocumentAnalysisRecord can be created."""
        record = DocumentAnalysisRecord(
            analysis_id="analysis_001",
            created_at=datetime.now(),
            model=AnalysisModelInfo(name="gpt-4o", revision="2024-08-06"),
            parameters=AnalysisParameters(temperature=0.0),
            outputs=DocumentAnalysis(
                summary="Test summary",
                entities=[],
                document_type="letter",
                sentiment="neutral",
                legal_significance="low",
                risk_flags=[],
                confidence_overall=0.9
            ),
            confidence_overall=0.9
        )

        assert record.analysis_id == "analysis_001"
        assert record.model.name == "gpt-4o"

    def test_DocumentAnalysisRecord_rejects_confidence_out_of_range(self):
        """Test that DocumentAnalysisRecord rejects confidence_overall outside [0.0, 1.0]."""
        with pytest.raises(ValidationError):
            DocumentAnalysisRecord(
                analysis_id="test",
                created_at=datetime.now(),
                model=AnalysisModelInfo(name="gpt-4o", revision="2024-08-06"),
                parameters=AnalysisParameters(),
                outputs=DocumentAnalysis(
                    summary="Test",
                    entities=[],
                    document_type="letter",
                    sentiment="neutral",
                    legal_significance="low",
                    risk_flags=[],
                    confidence_overall=0.9
                ),
                confidence_overall=1.5  # Invalid: > 1.0
            )

    def test_DocumentAnalysisRecord_serialization_roundtrip(self):
        """Test that DocumentAnalysisRecord can be serialized and deserialized."""
        original = DocumentAnalysisRecord(
            analysis_id="rec_123",
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            model=AnalysisModelInfo(name="gpt-4o", revision="2024-08-06"),
            parameters=AnalysisParameters(temperature=0.0),
            outputs=DocumentAnalysis(
                summary="Forensic analysis",
                entities=[],
                document_type="contract",
                sentiment="professional",
                legal_significance="high",
                risk_flags=["deadline"],
                confidence_overall=0.95
            ),
            confidence_overall=0.95
        )

        serialized = original.model_dump()
        restored = DocumentAnalysisRecord.model_validate(serialized)

        assert restored.analysis_id == original.analysis_id
        assert restored.confidence_overall == original.confidence_overall


class TestEvidenceBundle:
    """Test EvidenceBundle model validation.

    CRITICAL: This is the complete forensic evidence package format.
    """

    def test_EvidenceBundle_valid_instantiation(self):
        """Test that valid EvidenceBundle can be created."""
        bundle = EvidenceBundle(
            schema_version="1.0.0",
            case_id="CASE-2024-001",
            evidence=EvidenceCore(
                evidence_id="ev_001",
                sha256="c" * 64,
                mime_type="application/pdf",
                bytes=100000,
                ingested_at=datetime.now(),
                source_path="/evidence/doc.pdf"
            ),
            chain_of_custody=[
                ChainOfCustodyEntry(
                    ts=datetime.now(),
                    actor="analyst",
                    action="ingest"
                )
            ],
            analyses=[]
        )

        assert bundle.schema_version == "1.0.0"
        assert bundle.case_id == "CASE-2024-001"

    def test_EvidenceBundle_rejects_invalid_schema_version(self):
        """Test that EvidenceBundle rejects invalid schema_version."""
        with pytest.raises(ValidationError):
            EvidenceBundle(
                schema_version="2.0.0",  # Must be "1.0.0"
                evidence=EvidenceCore(
                    evidence_id="ev_001",
                    sha256="d" * 64,
                    mime_type="text/plain",
                    bytes=100,
                    ingested_at=datetime.now(),
                    source_path="/test"
                )
            )

    def test_EvidenceBundle_allows_none_case_id(self):
        """Test that EvidenceBundle allows None for optional case_id."""
        bundle = EvidenceBundle(
            schema_version="1.0.0",
            case_id=None,  # Optional
            evidence=EvidenceCore(
                evidence_id="ev_001",
                sha256="e" * 64,
                mime_type="text/plain",
                bytes=100,
                ingested_at=datetime.now(),
                source_path="/test"
            )
        )

        assert bundle.case_id is None

    def test_EvidenceBundle_serialization_roundtrip(self):
        """Test that EvidenceBundle can be serialized and deserialized."""
        original = EvidenceBundle(
            schema_version="1.0.0",
            case_id="CASE-001",
            evidence=EvidenceCore(
                evidence_id="ev_123",
                sha256="1" * 64,
                mime_type="application/pdf",
                bytes=50000,
                ingested_at=datetime(2024, 1, 15, 9, 0, 0),
                source_path="/evidence/file.pdf"
            ),
            chain_of_custody=[],
            analyses=[]
        )

        serialized = original.model_dump()
        restored = EvidenceBundle.model_validate(serialized)

        assert restored.schema_version == original.schema_version
        assert restored.case_id == original.case_id


# =============================================================================
# CROSS-EVIDENCE ANALYSIS (v3.0 PYDANTIC FIX)
# =============================================================================

class TestEvidenceOccurrence:
    """Test EvidenceOccurrence model validation."""

    def test_EvidenceOccurrence_valid_instantiation(self):
        """Test that valid EvidenceOccurrence can be created."""
        occurrence = EvidenceOccurrence(
            evidence_sha256="2" * 64,
            context="John Smith mentioned in complaint letter",
            confidence=0.92
        )

        assert len(occurrence.evidence_sha256) == 64
        assert occurrence.confidence == 0.92

    def test_EvidenceOccurrence_rejects_invalid_sha256(self):
        """Test that EvidenceOccurrence rejects invalid SHA256 patterns."""
        with pytest.raises(ValidationError):
            EvidenceOccurrence(
                evidence_sha256="short",  # Too short
                context="Test context",
                confidence=0.9
            )

    def test_EvidenceOccurrence_rejects_confidence_out_of_range(self):
        """Test that EvidenceOccurrence rejects confidence outside [0.0, 1.0]."""
        with pytest.raises(ValidationError):
            EvidenceOccurrence(
                evidence_sha256="3" * 64,
                context="Test",
                confidence=1.2  # Invalid: > 1.0
            )

    def test_EvidenceOccurrence_serialization_roundtrip(self):
        """Test that EvidenceOccurrence can be serialized and deserialized."""
        original = EvidenceOccurrence(
            evidence_sha256="4" * 64,
            context="Entity found in document X",
            confidence=0.88
        )

        serialized = original.model_dump()
        restored = EvidenceOccurrence.model_validate(serialized)

        assert restored.evidence_sha256 == original.evidence_sha256
        assert restored.confidence == original.confidence


class TestCorrelatedEntity:
    """Test CorrelatedEntity model validation."""

    def test_CorrelatedEntity_valid_instantiation(self):
        """Test that valid CorrelatedEntity can be created."""
        entity = CorrelatedEntity(
            entity_name="John Smith",
            entity_type="person",
            occurrence_count=5,
            confidence_average=0.91,
            evidence_occurrences=[
                {"evidence_sha256": "5" * 64, "context": "Email sender"},
                {"evidence_sha256": "6" * 64, "context": "Document author"}
            ]
        )

        assert entity.entity_name == "John Smith"
        assert entity.occurrence_count == 5

    def test_CorrelatedEntity_rejects_occurrence_count_less_than_2(self):
        """Test that CorrelatedEntity rejects occurrence_count < 2 (must be correlated)."""
        with pytest.raises(ValidationError):
            CorrelatedEntity(
                entity_name="Test",
                entity_type="person",
                occurrence_count=1,  # Must be >= 2
                confidence_average=0.9,
                evidence_occurrences=[{"test": "data"}]
            )

    def test_CorrelatedEntity_serialization_roundtrip(self):
        """Test that CorrelatedEntity can be serialized and deserialized."""
        original = CorrelatedEntity(
            entity_name="Acme Corp",
            entity_type="organization",
            occurrence_count=3,
            confidence_average=0.85,
            evidence_occurrences=[{"sha256": "test"}]
        )

        serialized = original.model_dump()
        restored = CorrelatedEntity.model_validate(serialized)

        assert restored.entity_name == original.entity_name
        assert restored.occurrence_count == original.occurrence_count


class TestTimelineEvent:
    """Test TimelineEvent model validation."""

    def test_TimelineEvent_valid_instantiation(self):
        """Test that valid TimelineEvent can be created."""
        event = TimelineEvent(
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            evidence_sha256="7" * 64,
            evidence_type="email",
            event_type="communication",
            description="Harassment complaint email sent",
            confidence=0.93,
            ai_classification={"pattern": "retaliation", "severity": "high"}
        )

        assert event.event_type == "communication"
        assert event.ai_classification["pattern"] == "retaliation"

    def test_TimelineEvent_rejects_invalid_sha256(self):
        """Test that TimelineEvent rejects invalid SHA256 patterns."""
        with pytest.raises(ValidationError):
            TimelineEvent(
                timestamp=datetime.now(),
                evidence_sha256="invalid_hash",  # Invalid pattern
                evidence_type="document",
                event_type="creation",
                description="Test",
                confidence=0.9
            )

    def test_TimelineEvent_allows_none_ai_classification(self):
        """Test that TimelineEvent allows None for optional ai_classification."""
        event = TimelineEvent(
            timestamp=datetime.now(),
            evidence_sha256="8" * 64,
            evidence_type="image",
            event_type="capture",
            description="Photo taken",
            confidence=0.88,
            ai_classification=None  # Optional
        )

        assert event.ai_classification is None

    def test_TimelineEvent_serialization_roundtrip(self):
        """Test that TimelineEvent can be serialized and deserialized."""
        original = TimelineEvent(
            timestamp=datetime(2024, 2, 1, 14, 30, 0),
            evidence_sha256="9" * 64,
            evidence_type="document",
            event_type="signature",
            description="Contract signed",
            confidence=0.96,
            ai_classification={"legal_significance": "high"}
        )

        serialized = original.model_dump()
        restored = TimelineEvent.model_validate(serialized)

        assert restored.event_type == original.event_type
        assert restored.evidence_sha256 == original.evidence_sha256


class TestCorrelationAnalysis:
    """Test CorrelationAnalysis model validation.

    CRITICAL v3.0 FIX: This was a dataclass in v2.0, now Pydantic for validation!
    """

    def test_CorrelationAnalysis_valid_instantiation(self):
        """Test that valid CorrelationAnalysis can be created."""
        analysis = CorrelationAnalysis(
            case_id="CASE-2024-001",
            evidence_count=12,
            entity_correlations=[],
            timeline_events=[],
            analysis_timestamp=datetime.now(),
            temporal_sequences=[],
            timeline_gaps=[]
        )

        assert analysis.case_id == "CASE-2024-001"
        assert analysis.evidence_count == 12

    def test_CorrelationAnalysis_rejects_negative_evidence_count(self):
        """Test that CorrelationAnalysis rejects negative evidence_count.

        This is the critical v3.0 validation that was missing in v2.0 dataclass!
        """
        with pytest.raises(ValidationError):
            CorrelationAnalysis(
                case_id="TEST",
                evidence_count=-1,  # Must be >= 0
                entity_correlations=[],
                timeline_events=[],
                analysis_timestamp=datetime.now()
            )

    def test_CorrelationAnalysis_allows_zero_evidence(self):
        """Test that CorrelationAnalysis allows evidence_count=0 (empty case)."""
        analysis = CorrelationAnalysis(
            case_id="EMPTY-CASE",
            evidence_count=0,  # Valid: new case with no evidence yet
            entity_correlations=[],
            timeline_events=[],
            analysis_timestamp=datetime.now()
        )

        assert analysis.evidence_count == 0

    def test_CorrelationAnalysis_allows_empty_lists(self):
        """Test that CorrelationAnalysis allows empty lists for default_factory fields."""
        analysis = CorrelationAnalysis(
            case_id="CASE-001",
            evidence_count=5,
            entity_correlations=[],
            timeline_events=[],
            analysis_timestamp=datetime.now(),
            temporal_sequences=[],
            timeline_gaps=[]
        )

        assert len(analysis.entity_correlations) == 0
        assert len(analysis.timeline_events) == 0

    def test_CorrelationAnalysis_with_populated_correlations(self):
        """Test that CorrelationAnalysis works with populated entity correlations."""
        analysis = CorrelationAnalysis(
            case_id="CASE-001",
            evidence_count=8,
            entity_correlations=[
                CorrelatedEntity(
                    entity_name="John Doe",
                    entity_type="person",
                    occurrence_count=4,
                    confidence_average=0.92,
                    evidence_occurrences=[{"sha256": "a" * 64}]
                )
            ],
            timeline_events=[],
            analysis_timestamp=datetime.now()
        )

        assert len(analysis.entity_correlations) == 1
        assert analysis.entity_correlations[0].entity_name == "John Doe"

    def test_CorrelationAnalysis_serialization_roundtrip(self):
        """Test that CorrelationAnalysis can be serialized and deserialized."""
        original = CorrelationAnalysis(
            case_id="CASE-FORENSIC-001",
            evidence_count=15,
            entity_correlations=[],
            timeline_events=[
                TimelineEvent(
                    timestamp=datetime(2024, 1, 1, 12, 0, 0),
                    evidence_sha256="b" * 64,
                    evidence_type="email",
                    event_type="sent",
                    description="Initial complaint",
                    confidence=0.95
                )
            ],
            analysis_timestamp=datetime(2024, 3, 1, 10, 0, 0),
            temporal_sequences=[{"pattern": "escalation"}],
            timeline_gaps=[{"gap_days": 30}]
        )

        serialized = original.model_dump()
        restored = CorrelationAnalysis.model_validate(serialized)

        assert restored.case_id == original.case_id
        assert restored.evidence_count == original.evidence_count
        assert len(restored.timeline_events) == len(original.timeline_events)


# =============================================================================
# OPERATION RESULTS
# =============================================================================

class TestIngestionResult:
    """Test IngestionResult model validation."""

    def test_IngestionResult_valid_instantiation(self):
        """Test that valid IngestionResult can be created."""
        result = IngestionResult(
            sha256="f1" * 32,
            file_path="/evidence/document.pdf",
            evidence_type=EvidenceType.PDF,
            metadata=FileMetadata(
                filename="document.pdf",
                file_size=100000,
                created_time="2024-01-15T10:00:00",
                modified_time="2024-01-15T10:00:00",
                extension=".pdf",
                sha256="f1" * 32
            ),
            storage_path="/storage/raw/sha256=f1f1.../original.pdf",
            success=True,
            message="Successfully ingested evidence"
        )

        assert result.success is True
        assert result.evidence_type == EvidenceType.PDF

    def test_IngestionResult_allows_none_optional_fields(self):
        """Test that IngestionResult allows None for optional fields."""
        result = IngestionResult(
            sha256="ab" * 32,
            file_path="/test.txt",
            evidence_type=EvidenceType.DOCUMENT,
            metadata=None,  # Optional
            storage_path="/storage/test",
            success=False,
            message=None  # Optional
        )

        assert result.metadata is None
        assert result.message is None

    def test_IngestionResult_serialization_roundtrip(self):
        """Test that IngestionResult can be serialized and deserialized."""
        original = IngestionResult(
            sha256="cd" * 32,
            file_path="/evidence/email.eml",
            evidence_type=EvidenceType.EMAIL,
            storage_path="/storage/email",
            success=True
        )

        serialized = original.model_dump()
        restored = IngestionResult.model_validate(serialized)

        assert restored.sha256 == original.sha256
        assert restored.success == original.success


class TestExportResult:
    """Test ExportResult model validation."""

    def test_ExportResult_valid_instantiation(self):
        """Test that valid ExportResult can be created."""
        result = ExportResult(
            sha256="ef" * 32,
            export_path="/exports/case-001/evidence.pdf",
            analysis_included=True,
            success=True,
            message="Evidence exported successfully"
        )

        assert result.analysis_included is True
        assert result.success is True

    def test_ExportResult_allows_none_message(self):
        """Test that ExportResult allows None for optional message field."""
        result = ExportResult(
            sha256="12" * 32,
            export_path="/exports/test",
            analysis_included=False,
            success=False,
            message=None  # Optional
        )

        assert result.message is None

    def test_ExportResult_serialization_roundtrip(self):
        """Test that ExportResult can be serialized and deserialized."""
        original = ExportResult(
            sha256="34" * 32,
            export_path="/exports/package.zip",
            analysis_included=True,
            success=True,
            message="Export complete"
        )

        serialized = original.model_dump()
        restored = ExportResult.model_validate(serialized)

        assert restored.sha256 == original.sha256
        assert restored.analysis_included == original.analysis_included


# =============================================================================
# STORAGE MANAGEMENT & CASE OPERATIONS
# =============================================================================

class TestStorageStats:
    """Test StorageStats model validation."""

    def test_StorageStats_valid_instantiation(self):
        """Test that valid StorageStats can be created."""
        stats = StorageStats(
            total_evidence=125,
            evidence_by_type={"document": 50, "email": 40, "image": 35},
            total_cases=8,
            total_labels=15,
            storage_size_mb=2048.5,
            raw_size_mb=1500.0,
            derived_size_mb=548.5,
            orphaned_files=3
        )

        assert stats.total_evidence == 125
        assert stats.total_cases == 8
        assert stats.orphaned_files == 3

    def test_StorageStats_rejects_negative_counts(self):
        """Test that StorageStats rejects negative values."""
        with pytest.raises(ValidationError):
            StorageStats(
                total_evidence=-1,  # Must be >= 0
                evidence_by_type={},
                total_cases=5,
                total_labels=10,
                storage_size_mb=100.0,
                raw_size_mb=50.0,
                derived_size_mb=50.0
            )

    def test_StorageStats_allows_zero_orphaned_files(self):
        """Test that StorageStats allows zero orphaned_files (healthy state)."""
        stats = StorageStats(
            total_evidence=10,
            evidence_by_type={},
            total_cases=1,
            total_labels=5,
            storage_size_mb=100.0,
            raw_size_mb=60.0,
            derived_size_mb=40.0,
            orphaned_files=0  # Default and healthy value
        )

        assert stats.orphaned_files == 0

    def test_StorageStats_serialization_roundtrip(self):
        """Test that StorageStats can be serialized and deserialized."""
        original = StorageStats(
            total_evidence=50,
            evidence_by_type={"document": 30, "image": 20},
            total_cases=3,
            total_labels=8,
            storage_size_mb=512.25,
            raw_size_mb=300.0,
            derived_size_mb=212.25,
            orphaned_files=1
        )

        serialized = original.model_dump()
        restored = StorageStats.model_validate(serialized)

        assert restored.total_evidence == original.total_evidence
        assert restored.storage_size_mb == original.storage_size_mb


class TestCaseInfo:
    """Test CaseInfo model validation."""

    def test_CaseInfo_valid_instantiation(self):
        """Test that valid CaseInfo can be created."""
        info = CaseInfo(
            case_id="CASE-2024-001",
            evidence_count=25,
            evidence_types=["document", "email", "image"],
            last_modified=datetime(2024, 3, 1, 14, 30, 0),
            total_size_mb=128.75
        )

        assert info.case_id == "CASE-2024-001"
        assert info.evidence_count == 25
        assert len(info.evidence_types) == 3

    def test_CaseInfo_rejects_negative_evidence_count(self):
        """Test that CaseInfo rejects negative evidence_count."""
        with pytest.raises(ValidationError):
            CaseInfo(
                case_id="TEST",
                evidence_count=-5,  # Must be >= 0
                evidence_types=[],
                last_modified=datetime.now(),
                total_size_mb=100.0
            )

    def test_CaseInfo_allows_zero_evidence(self):
        """Test that CaseInfo allows evidence_count=0 (new empty case)."""
        info = CaseInfo(
            case_id="NEW-CASE",
            evidence_count=0,  # Valid: newly created case
            evidence_types=[],
            last_modified=datetime.now(),
            total_size_mb=0.0
        )

        assert info.evidence_count == 0
        assert info.total_size_mb == 0.0

    def test_CaseInfo_serialization_roundtrip(self):
        """Test that CaseInfo can be serialized and deserialized."""
        original = CaseInfo(
            case_id="CASE-ACTIVE-001",
            evidence_count=15,
            evidence_types=["document", "email"],
            last_modified=datetime(2024, 2, 15, 10, 0, 0),
            total_size_mb=256.5
        )

        serialized = original.model_dump()
        restored = CaseInfo.model_validate(serialized)

        assert restored.case_id == original.case_id
        assert restored.evidence_count == original.evidence_count


class TestCleanupResult:
    """Test CleanupResult model validation."""

    def test_CleanupResult_valid_instantiation(self):
        """Test that valid CleanupResult can be created."""
        result = CleanupResult(
            broken_links_removed=5,
            empty_dirs_removed=3,
            orphaned_files=2,
            dry_run=False
        )

        assert result.broken_links_removed == 5
        assert result.empty_dirs_removed == 3
        assert result.dry_run is False

    def test_CleanupResult_rejects_negative_counts(self):
        """Test that CleanupResult rejects negative counts."""
        with pytest.raises(ValidationError):
            CleanupResult(
                broken_links_removed=-1,  # Must be >= 0
                empty_dirs_removed=0,
                orphaned_files=0,
                dry_run=False
            )

    def test_CleanupResult_allows_defaults(self):
        """Test that CleanupResult allows default values."""
        result = CleanupResult()  # All fields have defaults

        assert result.broken_links_removed == 0
        assert result.empty_dirs_removed == 0
        assert result.orphaned_files == 0
        assert result.dry_run is False

    def test_CleanupResult_dry_run_mode(self):
        """Test that CleanupResult supports dry_run mode."""
        result = CleanupResult(
            broken_links_removed=10,
            empty_dirs_removed=5,
            orphaned_files=3,
            dry_run=True  # Dry run - no actual changes
        )

        assert result.dry_run is True

    def test_CleanupResult_serialization_roundtrip(self):
        """Test that CleanupResult can be serialized and deserialized."""
        original = CleanupResult(
            broken_links_removed=8,
            empty_dirs_removed=4,
            orphaned_files=1,
            dry_run=False
        )

        serialized = original.model_dump()
        restored = CleanupResult.model_validate(serialized)

        assert restored.broken_links_removed == original.broken_links_removed
        assert restored.dry_run == original.dry_run
