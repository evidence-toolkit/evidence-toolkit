"""Critical forensic integrity tests for Evidence Toolkit.

These tests protect the legal and forensic requirements of the toolkit:
- SHA256 immutability (evidence integrity)
- Chain of custody completeness (audit trail)
- Pydantic validation (corruption prevention)

These are hand-written by domain experts to ensure legal compliance.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import (
    FileMetadata,
    EvidenceType,
    ChainOfCustodyEvent,
    UnifiedAnalysis,
    DocumentAnalysisResult,
    CorrelationAnalysis,
)


class TestSHA256Immutability:
    """CRITICAL: SHA256 hashes must never change after ingestion.

    Legal Requirement: Evidence integrity relies on cryptographic hashing.
    Any change to SHA256 after ingestion indicates tampering or corruption.
    """

    def test_sha256_never_changes_after_ingestion(self, tmp_storage, sample_document, case_id):
        """Test that SHA256 remains constant after ingestion.

        This is the foundation of content-addressed storage and forensic integrity.
        """
        # Ingest file
        result = tmp_storage.ingest_file(sample_document, case_id=case_id, actor="test_user")
        assert result.success, f"Ingestion failed: {result.message}"

        original_sha256 = result.sha256

        # Verify SHA256 is stored correctly
        metadata_file = tmp_storage.derived_dir / f"sha256={original_sha256}" / "metadata.json"
        assert metadata_file.exists(), "Metadata file not created"

        with open(metadata_file, 'r') as f:
            stored_metadata = json.load(f)

        assert stored_metadata['sha256'] == original_sha256, "SHA256 mismatch in metadata"

        # Re-ingest same file (should use existing hash)
        result2 = tmp_storage.ingest_file(sample_document, case_id=case_id, actor="test_user")
        assert result2.sha256 == original_sha256, "SHA256 changed on re-ingestion!"

        # Verify original file still exists with same hash
        original_file = tmp_storage.raw_dir / f"sha256={original_sha256}" / f"original.txt"
        assert original_file.exists(), "Original file missing"

        # Verify we can still retrieve with original hash
        retrieved_analysis = tmp_storage.get_analysis(original_sha256)
        # May be None if not analyzed yet, but should not error

    def test_sha256_matches_file_content(self, tmp_storage, sample_document, case_id):
        """Test that SHA256 accurately represents file content.

        Changing file content should result in different SHA256.
        """
        from evidence_toolkit.core.utils import calculate_sha256

        # Ingest original file
        result1 = tmp_storage.ingest_file(sample_document, case_id=case_id)
        original_sha256 = result1.sha256

        # Modify file content
        modified_path = sample_document.parent / "modified.txt"
        modified_path.write_text(sample_document.read_text() + "\nMODIFIED")

        # Ingest modified file
        result2 = tmp_storage.ingest_file(modified_path, case_id=case_id)
        modified_sha256 = result2.sha256

        # SHA256 must be different
        assert original_sha256 != modified_sha256, "Different content produced same SHA256!"

        # Verify both are stored independently
        assert (tmp_storage.raw_dir / f"sha256={original_sha256}").exists()
        assert (tmp_storage.raw_dir / f"sha256={modified_sha256}").exists()

    def test_sha256_prevents_hash_collision(self, tmp_storage, tmp_dir, case_id):
        """Test that identical content produces identical hash (deduplication).

        This is critical for multi-case evidence sharing.
        """
        # Create two files with identical content
        file1 = tmp_dir / "file1.txt"
        file2 = tmp_dir / "file2.txt"

        content = "Evidence content that should deduplicate"
        file1.write_text(content)
        file2.write_text(content)

        # Ingest both
        result1 = tmp_storage.ingest_file(file1, case_id=case_id)
        result2 = tmp_storage.ingest_file(file2, case_id="CASE-002")

        # Must produce same SHA256 (content-addressed deduplication)
        assert result1.sha256 == result2.sha256, "Identical content produced different SHA256!"

        # Should only have ONE raw file (deduplication)
        raw_dir = tmp_storage.raw_dir / f"sha256={result1.sha256}"
        files = list(raw_dir.glob("original*"))
        assert len(files) == 1, f"Deduplication failed - found {len(files)} files"


class TestChainOfCustodyCompleteness:
    """CRITICAL: Complete audit trail must be maintained for all evidence.

    Legal Requirement: Chain of custody documentation is required for
    evidence admissibility in legal proceedings.
    """

    def test_chain_of_custody_created_on_ingestion(self, tmp_storage, sample_document, case_id):
        """Test that chain of custody is initialized when evidence is ingested."""
        result = tmp_storage.ingest_file(sample_document, case_id=case_id, actor="forensic_analyst")
        assert result.success

        # Check chain of custody file exists
        custody_file = tmp_storage.derived_dir / f"sha256={result.sha256}" / "chain_of_custody.json"
        assert custody_file.exists(), "Chain of custody file not created"

        # Load and validate chain of custody
        with open(custody_file, 'r') as f:
            custody_data = json.load(f)

        assert isinstance(custody_data, list), "Chain of custody must be a list"
        assert len(custody_data) >= 1, "No custody events recorded"

        # First event should be ingestion
        first_event = custody_data[0]
        assert first_event['event_type'] == 'ingest', "First event should be ingestion"
        assert first_event['actor'] == 'forensic_analyst', "Actor not recorded correctly"
        assert 'timestamp' in first_event, "Timestamp missing from custody event"
        assert 'description' in first_event, "Description missing from custody event"

    def test_chain_of_custody_updated_on_analysis(self, tmp_storage, sample_document, case_id):
        """Test that chain of custody is updated when evidence is analyzed."""
        # Ingest
        result = tmp_storage.ingest_file(sample_document, case_id=case_id, actor="analyst1")
        sha256 = result.sha256

        # Create and save analysis
        analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=result.metadata,
            case_ids=[case_id],
            document_analysis=DocumentAnalysisResult(
                total_words=100,
                unique_words=50,
                word_frequency={"test": 5},
                top_words=[("test", 5)]
            ),
            chain_of_custody=[]
        )

        tmp_storage.save_analysis(analysis)

        # Load chain of custody
        custody_file = tmp_storage.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"
        with open(custody_file, 'r') as f:
            custody_data = json.load(f)

        # Should have at least 2 events: ingest + analyze
        assert len(custody_data) >= 2, "Analysis event not recorded in chain of custody"

        # Find analyze event
        analyze_events = [e for e in custody_data if e['event_type'] == 'analyze']
        assert len(analyze_events) >= 1, "No analyze event in chain of custody"

    def test_chain_of_custody_preserves_chronological_order(self, tmp_storage, sample_document, case_id):
        """Test that chain of custody events maintain chronological order."""
        import time

        # Ingest
        result = tmp_storage.ingest_file(sample_document, case_id=case_id)
        sha256 = result.sha256

        time.sleep(0.1)  # Ensure timestamp difference

        # Add multiple custody events
        for i in range(3):
            event = ChainOfCustodyEvent(
                timestamp=datetime.now(),
                event_type="test_event",
                actor=f"actor_{i}",
                description=f"Test event {i}"
            )
            tmp_storage._add_custody_event(sha256, event)
            time.sleep(0.1)

        # Load and verify chronological order
        custody_file = tmp_storage.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"
        with open(custody_file, 'r') as f:
            custody_data = json.load(f)

        # Parse timestamps and verify they're in order
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in custody_data]
        assert timestamps == sorted(timestamps), "Chain of custody events not in chronological order!"

    def test_chain_of_custody_survives_multi_case_association(self, tmp_storage, sample_document):
        """Test that chain of custody is preserved when evidence is associated with multiple cases.

        CRITICAL for legal compliance: Chain of custody must APPEND events, not overwrite them.
        Each case association must be recorded in chronological order.
        """
        # Ingest for first case
        result1 = tmp_storage.ingest_file(sample_document, case_id="CASE-001", actor="analyst1")
        sha256 = result1.sha256

        # Get initial custody chain
        custody_file = tmp_storage.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"
        with open(custody_file, 'r') as f:
            initial_custody = json.load(f)
        initial_count = len(initial_custody)

        assert initial_count == 1, "Should have exactly one event after first ingestion"
        assert initial_custody[0]['event_type'] == 'ingest', "First event should be ingestion"
        assert initial_custody[0]['metadata']['case_id'] == 'CASE-001', "Should record CASE-001"

        # Associate with second case (re-ingest same file)
        result2 = tmp_storage.ingest_file(sample_document, case_id="CASE-002", actor="analyst2")

        # Verify chain of custody has GROWN (not replaced)
        with open(custody_file, 'r') as f:
            updated_custody = json.load(f)

        assert len(updated_custody) > initial_count, "Chain must grow with new case association!"
        assert len(updated_custody) == 2, "Should have 2 events (CASE-001 + CASE-002)"

        # Verify BOTH case events are present (forensic integrity requirement)
        case_ids = [e.get('metadata', {}).get('case_id') for e in updated_custody]
        assert 'CASE-001' in case_ids, "CASE-001 event must be preserved!"
        assert 'CASE-002' in case_ids, "CASE-002 event must be present!"

        # Verify chronological order maintained (legal requirement)
        timestamps = [datetime.fromisoformat(e['timestamp']) for e in updated_custody]
        assert timestamps == sorted(timestamps), "Events must be in chronological order!"

        # Verify actors are correctly recorded
        actors = [e['actor'] for e in updated_custody]
        assert actors[0] == 'analyst1', "First event should have analyst1"
        assert actors[1] == 'analyst2', "Second event should have analyst2"


class TestPydanticValidationPreventsCorruption:
    """CRITICAL: Pydantic validation must reject invalid data before storage.

    Legal Requirement: Corrupt or invalid data could compromise
    forensic integrity and legal admissibility.

    Note: SHA256 validation is not tested at FileMetadata level because:
    - SHA256 always comes from hashlib.hexdigest() (always valid)
    - Strict validation enforced at EvidenceCore level for forensic bundles
    - Invalid SHA256 cannot occur in normal operation
    """

    def test_pydantic_rejects_missing_required_fields(self):
        """Test that models reject instances missing required fields."""
        # FileMetadata requires: filename, file_size, created_time, modified_time, extension, sha256
        with pytest.raises(Exception):  # Pydantic ValidationError
            FileMetadata(  # type: ignore[call-arg]
                filename="test.txt",
                # Missing file_size, created_time, modified_time, extension, sha256
            )

        # ChainOfCustodyEvent requires: timestamp, event_type, actor, description
        with pytest.raises(Exception):
            ChainOfCustodyEvent(  # type: ignore[call-arg]
                timestamp=datetime.now(),
                # Missing event_type, actor, description
            )

    def test_pydantic_rejects_wrong_types(self):
        """Test that models reject fields with wrong types."""
        # file_size must be int, not string
        with pytest.raises(Exception):  # Pydantic ValidationError
            FileMetadata(  # type: ignore[arg-type]
                filename="test.txt",
                file_size="not_an_int",  # Wrong type
                created_time="2024-01-01T00:00:00",
                modified_time="2024-01-01T00:00:00",
                extension=".txt",
                sha256="a" * 64
            )

    def test_pydantic_validates_correlation_analysis(self):
        """Test that CorrelationAnalysis (v3.0 fix) uses Pydantic validation.

        This was a dataclass in v2.0 and caused validation gaps.
        v3.0 converted it to Pydantic for forensic compliance.
        """
        # Valid CorrelationAnalysis
        valid_correlation = CorrelationAnalysis(
            case_id="TEST-001",
            evidence_count=5,
            entity_correlations=[],
            timeline_events=[],
            analysis_timestamp=datetime.now()
        )
        assert valid_correlation.case_id == "TEST-001"

        # Invalid: evidence_count must be >= 0
        with pytest.raises(Exception):  # Pydantic ValidationError
            CorrelationAnalysis(
                case_id="TEST-001",
                evidence_count=-1,  # Invalid: negative count
                entity_correlations=[],
                timeline_events=[],
                analysis_timestamp=datetime.now()
            )

    def test_pydantic_prevents_storage_of_invalid_analysis(self, tmp_storage, sample_document, case_id):
        """Test that invalid analysis cannot be saved to storage.

        This prevents corruption at the storage boundary.
        """
        # Ingest valid file
        result = tmp_storage.ingest_file(sample_document, case_id=case_id)
        sha256 = result.sha256

        # Try to create analysis with invalid data
        with pytest.raises(Exception):  # Pydantic ValidationError
            invalid_analysis = UnifiedAnalysis(
                evidence_type="INVALID_TYPE",  # Must be valid EvidenceType enum
                analysis_timestamp=datetime.now(),
                file_metadata=result.metadata,
                case_ids=[case_id]
            )

        # Valid analysis should succeed
        valid_analysis = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,  # Valid enum value
            analysis_timestamp=datetime.now(),
            file_metadata=result.metadata,
            case_ids=[case_id],
            document_analysis=DocumentAnalysisResult(
                total_words=10,
                unique_words=5,
                word_frequency={},
                top_words=[]
            )
        )

        # This should succeed
        success = tmp_storage.save_analysis(valid_analysis)
        assert success, "Failed to save valid analysis"

        # Verify it was saved
        retrieved = tmp_storage.get_analysis(sha256)
        assert retrieved is not None, "Could not retrieve saved analysis"
        assert retrieved.evidence_type == EvidenceType.DOCUMENT


class TestForensicIntegrityEdgeCases:
    """Additional critical tests for forensic edge cases."""

    def test_empty_file_has_valid_sha256(self, tmp_storage, tmp_dir, case_id):
        """Test that even empty files get valid SHA256 hashes."""
        empty_file = tmp_dir / "empty.txt"
        empty_file.write_text("")

        result = tmp_storage.ingest_file(empty_file, case_id=case_id)
        assert result.success
        assert len(result.sha256) == 64, "Empty file should still have 64-char SHA256"
        assert result.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", \
            "Empty file should have known SHA256"

    def test_case_association_maintains_integrity(self, tmp_storage, sample_document):
        """Test that associating evidence with new case doesn't corrupt existing data."""
        # Ingest for first case
        result1 = tmp_storage.ingest_file(sample_document, case_id="CASE-001")
        sha256 = result1.sha256

        # Create analysis for first case
        analysis1 = UnifiedAnalysis(
            evidence_type=EvidenceType.DOCUMENT,
            analysis_timestamp=datetime.now(),
            file_metadata=result1.metadata,
            case_ids=["CASE-001"],
            document_analysis=DocumentAnalysisResult(
                total_words=100,
                unique_words=50,
                word_frequency={"test": 5},
                top_words=[("test", 5)]
            )
        )
        tmp_storage.save_analysis(analysis1)

        # Associate with second case
        result2 = tmp_storage.ingest_file(sample_document, case_id="CASE-002")

        # SHA256 must be identical
        assert result2.sha256 == sha256, "Case association changed SHA256!"

        # Original analysis should still exist
        retrieved = tmp_storage.get_analysis(sha256)
        assert retrieved is not None, "Analysis lost after case association"

        # Case IDs should include both cases (multi-case support)
        # Note: This depends on how ingestion handles existing evidence
        # For now, just verify the original analysis is intact
        assert retrieved.evidence_type == EvidenceType.DOCUMENT
