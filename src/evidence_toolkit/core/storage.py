#!/usr/bin/env python3
"""Evidence Storage - Content-addressed storage and management for v3.0.

This module provides forensic-grade evidence storage with SHA256-based
content addressing, chain of custody tracking, and multi-format analysis
support (documents, images, emails).

v3.0 Changes:
- Renamed from EvidenceManager to EvidenceStorage
- Updated default path: evidence_root → data/storage (visible directory)
- Unified imports from evidence_toolkit.core.models
- All Pydantic models now in single source of truth
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

from .utils import (
    calculate_sha256,
    get_file_metadata,
    extract_exif_data,
    detect_file_type,
    ensure_directory,
    create_hard_link,
    read_json_safe,
    get_evidence_base_dir
)
from .models import (
    # Base types
    EvidenceType,
    FileMetadata,
    ChainOfCustodyEvent,

    # Unified analysis (client package format)
    UnifiedAnalysis,

    # Operation results
    IngestionResult,
    ExportResult,

    # Forensic bundles (legal-grade evidence packages)
    EvidenceCore,
    ChainOfCustodyEntry,
    DocumentAnalysisRecord,
    AnalysisModelInfo,
    AnalysisParameters,
    EvidenceBundle,

    # AI analysis models
    DocumentAnalysis,
)


class EvidenceStorage:
    """Manages content-addressed evidence storage with forensic chain of custody.

    v3.0 Architecture:
    - Content-addressed storage using SHA256 hashing
    - Immutable file layout with derived data separation
    - Chain of custody tracking for legal admissibility
    - Multi-case support with hard links
    - Unified analysis format for all evidence types

    Storage Structure:
        data/storage/
        ├── raw/sha256=<hash>/original.<ext>       # Immutable original files
        ├── derived/sha256=<hash>/                  # Analysis and metadata
        │   ├── metadata.json
        │   ├── analysis.v1.json                    # UnifiedAnalysis format
        │   ├── evidence_bundle.v1.json             # EvidenceBundle format
        │   ├── chain_of_custody.json
        │   └── exif.json (images only)
        ├── labels/<label>/                         # Hard links by content
        └── cases/<case-id>/                        # Hard links by case
    """

    def __init__(self, evidence_root: Path = Path("data/storage")):
        """Initialize evidence storage with root directory.

        Args:
            evidence_root: Root directory for evidence storage (default: data/storage)
        """
        self.evidence_root = Path(evidence_root)
        self.raw_dir = self.evidence_root / "raw"
        self.derived_dir = self.evidence_root / "derived"
        self.labels_dir = self.evidence_root / "labels"
        self.cases_dir = self.evidence_root / "cases"

        # Ensure directories exist
        for directory in [self.raw_dir, self.derived_dir, self.labels_dir, self.cases_dir]:
            ensure_directory(directory)

    def ingest_file(
        self,
        file_path: Path,
        case_id: Optional[str] = None,
        actor: str = "system"
    ) -> IngestionResult:
        """Ingest a file into content-addressed storage.

        Args:
            file_path: Path to file to ingest
            case_id: Optional case identifier for organization
            actor: Actor performing the ingestion (for chain of custody)

        Returns:
            IngestionResult with success status and storage location
        """
        try:
            if not file_path.exists():
                return IngestionResult(
                    sha256="",
                    file_path=str(file_path),
                    evidence_type=EvidenceType.OTHER,
                    metadata=None,
                    storage_path="",
                    success=False,
                    message=f"File does not exist: {file_path}"
                )

            # Calculate hash
            sha256 = calculate_sha256(file_path)

            # Get metadata
            metadata = get_file_metadata(file_path)
            file_metadata = FileMetadata(sha256=sha256, **metadata)

            # Detect file type
            evidence_type = EvidenceType(detect_file_type(file_path))

            # Create storage directories
            raw_hash_dir = get_evidence_base_dir(self.raw_dir, sha256)
            derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)

            ensure_directory(raw_hash_dir)
            ensure_directory(derived_hash_dir)

            # Copy original file
            original_file = raw_hash_dir / f"original{file_path.suffix}"
            shutil.copy2(file_path, original_file)

            # Save metadata
            metadata_file = derived_hash_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(file_metadata.model_dump(), f, indent=2)

            # Extract EXIF for images
            exif_data = None
            if evidence_type == EvidenceType.IMAGE:
                exif_data = extract_exif_data(file_path)
                if exif_data:
                    exif_file = derived_hash_dir / "exif.json"
                    with open(exif_file, 'w') as f:
                        json.dump(exif_data, f, indent=2)

            # Create initial chain of custody
            custody_event = ChainOfCustodyEvent(
                timestamp=datetime.now(),
                event_type="ingest",
                actor=actor,
                description=f"File ingested from {file_path}",
                metadata={"case_id": case_id} if case_id else None
            )

            # Create case link if case_id provided
            if case_id:
                case_dir = self.cases_dir / case_id
                ensure_directory(case_dir)
                case_link = case_dir / f"{sha256}{file_path.suffix}"
                create_hard_link(original_file, case_link)

            # Add to chain of custody (preserves existing events for multi-case evidence)
            self._add_custody_event(sha256, custody_event)

            return IngestionResult(
                sha256=sha256,
                file_path=str(file_path),
                evidence_type=evidence_type,
                metadata=file_metadata,
                storage_path=str(original_file),
                success=True,
                message="File successfully ingested"
            )

        except Exception as e:
            return IngestionResult(
                sha256="",
                file_path=str(file_path),
                evidence_type=EvidenceType.OTHER,
                metadata=None,
                storage_path="",
                success=False,
                message=f"Ingestion failed: {str(e)}"
            )

    def get_analysis(self, sha256: str) -> Optional[UnifiedAnalysis]:
        """Retrieve unified analysis for a given SHA256.

        Args:
            sha256: SHA256 hash of evidence

        Returns:
            UnifiedAnalysis object or None if not found
        """
        evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
        analysis_file = evidence_dir / "analysis.v1.json"

        if not analysis_file.exists():
            return None

        data = read_json_safe(analysis_file)
        if not data:
            return None
        try:
            return UnifiedAnalysis.model_validate(data)
        except Exception as e:
            print(f"Error loading analysis for {sha256}: {e}")
            return None

    def save_analysis(self, analysis: UnifiedAnalysis) -> bool:
        """Save unified analysis result to storage.

        Args:
            analysis: UnifiedAnalysis object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            sha256 = analysis.file_metadata.sha256
            derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)

            if not derived_hash_dir.exists():
                print(f"Error: Derived directory does not exist for {sha256}")
                return False

            # Save analysis
            analysis_file = derived_hash_dir / "analysis.v1.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis.model_dump(), f, indent=2, default=str)

            # Update chain of custody
            self._add_custody_event(
                sha256,
                ChainOfCustodyEvent(
                    timestamp=datetime.now(),
                    event_type="analyze",
                    actor="system",
                    description=f"Analysis completed: {analysis.evidence_type}"
                )
            )

            # Create label links
            for label in analysis.labels:
                self._create_label_link(sha256, label, analysis.file_metadata.extension)

            # Also save in evidence bundle format for unified architecture
            bundle_success = self._save_evidence_bundle(analysis)
            if not bundle_success:
                print(f"Warning: Failed to save evidence bundle format for {sha256}")

            return True

        except Exception as e:
            print(f"Error saving analysis for {analysis.file_metadata.sha256}: {e}")
            return False

    def _save_evidence_bundle(self, analysis: UnifiedAnalysis) -> bool:
        """Convert UnifiedAnalysis to EvidenceBundle format and save.

        This creates the unified evidence bundle format that aligns with
        the evidence.v1.json schema architecture for cross-case analysis.

        Args:
            analysis: UnifiedAnalysis to convert

        Returns:
            True if successful, False otherwise
        """
        try:
            sha256 = analysis.file_metadata.sha256
            derived_hash_dir = get_evidence_base_dir(self.derived_dir, sha256)

            # Convert file metadata to evidence core
            evidence_core = EvidenceCore(
                evidence_id=sha256,
                sha256=sha256,
                mime_type=analysis.file_metadata.mime_type,
                bytes=analysis.file_metadata.file_size,
                ingested_at=analysis.file_metadata.created_time,
                source_path=analysis.file_metadata.filename
            )

            # Convert chain of custody to bundle format
            chain_entries = []
            for event in analysis.chain_of_custody:
                chain_entries.append(ChainOfCustodyEntry(
                    ts=event.timestamp,
                    actor=event.actor,
                    action=event.event_type,
                    note=event.description
                ))

            # Create analysis record for document analysis
            analysis_records = []
            if analysis.evidence_type == EvidenceType.DOCUMENT and analysis.document_analysis:
                # Check if we have AI analysis data (new format) or fallback to word frequency
                if analysis.document_analysis.ai_summary:
                    # Use real AI analysis from OpenAI Responses API
                    doc_analysis = DocumentAnalysis(
                        summary=analysis.document_analysis.ai_summary,
                        entities=analysis.document_analysis.entities or [],
                        document_type=analysis.document_analysis.document_type or "filing",
                        sentiment=analysis.document_analysis.sentiment or "neutral",
                        legal_significance=analysis.document_analysis.legal_significance or "medium",
                        risk_flags=analysis.document_analysis.risk_flags or [],
                        confidence_overall=analysis.document_analysis.analysis_confidence or 0.0
                    )

                    # Create analysis record with AI metadata
                    analysis_record = DocumentAnalysisRecord(
                        analysis_id=f"{sha256}_{int(analysis.analysis_timestamp.timestamp())}",
                        created_at=analysis.analysis_timestamp,
                        model=AnalysisModelInfo(
                            name=analysis.document_analysis.openai_model or "gpt-4.1-mini",
                            revision="2025-09-10"
                        ),
                        parameters=AnalysisParameters(
                            temperature=0.0,  # Deterministic analysis
                            prompt_hash=None,  # Could add prompt hashing in future
                            token_usage_in=None,  # OpenAI Responses API doesn't expose this yet
                            token_usage_out=None
                        ),
                        outputs=doc_analysis,
                        confidence_overall=analysis.document_analysis.analysis_confidence or 0.0
                    )
                else:
                    # Fallback: Use basic word frequency analysis (backwards compatible)
                    doc_analysis = DocumentAnalysis(
                        summary=f"Document analysis of {analysis.file_metadata.filename} containing {analysis.document_analysis.total_words} words with key themes: {', '.join([word for word, _ in analysis.document_analysis.top_words[:5]])}",
                        entities=[],
                        document_type="filing",
                        sentiment="neutral",
                        legal_significance="medium",
                        risk_flags=[],
                        confidence_overall=0.7
                    )

                    # Create analysis record with basic metadata
                    analysis_record = DocumentAnalysisRecord(
                        analysis_id=f"{sha256}_{int(analysis.analysis_timestamp.timestamp())}",
                        created_at=analysis.analysis_timestamp,
                        model=AnalysisModelInfo(
                            name="basic-text-analysis",
                            revision="1.0.0"
                        ),
                        parameters=AnalysisParameters(
                            temperature=None,
                            prompt_hash=None,
                            token_usage_in=None,
                            token_usage_out=None
                        ),
                        outputs=doc_analysis,
                        confidence_overall=0.7
                    )

                analysis_records.append(analysis_record)

            # Create evidence bundle
            evidence_bundle = EvidenceBundle(
                case_id=analysis.case_id,
                evidence=evidence_core,
                chain_of_custody=chain_entries,
                analyses=analysis_records
            )

            # Save evidence bundle
            bundle_file = derived_hash_dir / "evidence_bundle.v1.json"
            with open(bundle_file, 'w') as f:
                json.dump(evidence_bundle.model_dump(mode="json"), f, indent=2, default=str)

            return True

        except Exception as e:
            print(f"Error creating evidence bundle for {analysis.file_metadata.sha256}: {e}")
            return False

    def export_analysis(self, sha256: str, output_path: Path) -> ExportResult:
        """Export analysis to specified path.

        Args:
            sha256: SHA256 hash of evidence
            output_path: Path to export analysis to

        Returns:
            ExportResult with success status
        """
        try:
            analysis = self.get_analysis(sha256)

            if analysis is None:
                return ExportResult(
                    sha256=sha256,
                    export_path=str(output_path),
                    analysis_included=False,
                    success=False,
                    message="No analysis found for this evidence"
                )

            # Ensure output directory exists
            ensure_directory(output_path.parent)

            # Save analysis to output path
            with open(output_path, 'w') as f:
                json.dump(analysis.model_dump(), f, indent=2, default=str)

            return ExportResult(
                sha256=sha256,
                export_path=str(output_path),
                analysis_included=True,
                success=True,
                message="Analysis successfully exported"
            )

        except Exception as e:
            return ExportResult(
                sha256=sha256,
                export_path=str(output_path),
                analysis_included=False,
                success=False,
                message=f"Export failed: {str(e)}"
            )

    def list_evidence(self, case_id: Optional[str] = None) -> List[str]:
        """List all evidence SHA256s, optionally filtered by case.

        Args:
            case_id: Optional case ID to filter by

        Returns:
            List of SHA256 hashes
        """
        if case_id:
            case_dir = self.cases_dir / case_id
            if case_dir.exists():
                return [f.stem.split('.')[0] for f in case_dir.iterdir() if f.is_file()]
            return []

        # List all evidence
        evidence_dirs = [d for d in self.derived_dir.iterdir() if d.is_dir() and d.name.startswith("sha256=")]
        return [d.name.split("=")[1] for d in evidence_dirs]

    def _save_chain_of_custody(self, sha256: str, events: List[ChainOfCustodyEvent]):
        """Save chain of custody events.

        Args:
            sha256: SHA256 hash of evidence
            events: List of custody events
        """
        evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
        custody_file = evidence_dir / "chain_of_custody.json"
        events_data = [event.model_dump() for event in events]

        with open(custody_file, 'w') as f:
            json.dump(events_data, f, indent=2, default=str)

    def _add_custody_event(self, sha256: str, event: ChainOfCustodyEvent):
        """Add a chain of custody event.

        Args:
            sha256: SHA256 hash of evidence
            event: Custody event to add
        """
        evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)
        custody_file = evidence_dir / "chain_of_custody.json"

        # Load existing events
        events = []
        if custody_file.exists():
            events_data = read_json_safe(custody_file)
            if events_data:
                try:
                    events = [ChainOfCustodyEvent.model_validate(e) for e in events_data]
                except Exception as e:
                    print(f"Warning: Could not load existing custody events: {e}")

        # Add new event
        events.append(event)
        self._save_chain_of_custody(sha256, events)

    def _create_label_link(self, sha256: str, label: str, extension: str):
        """Create hard link in labels directory.

        Args:
            sha256: SHA256 hash of evidence
            label: Label to create link for
            extension: File extension
        """
        raw_evidence_dir = get_evidence_base_dir(self.raw_dir, sha256)
        original_file = raw_evidence_dir / f"original{extension}"
        if original_file.exists():
            label_dir = self.labels_dir / label
            label_link = label_dir / f"{sha256}{extension}"
            create_hard_link(original_file, label_link)

    def get_original_file_path(self, sha256: str) -> Optional[Path]:
        """Get path to original file for given SHA256.

        Args:
            sha256: SHA256 hash of evidence

        Returns:
            Path to original file or None if not found
        """
        raw_hash_dir = get_evidence_base_dir(self.raw_dir, sha256)
        if not raw_hash_dir.exists():
            return None

        # Look for original file
        for file_path in raw_hash_dir.iterdir():
            if file_path.name.startswith("original"):
                return file_path

        return None

    # =========================================================================
    # STORAGE MANAGEMENT METHODS (v3.0 CLI Extensions)
    # =========================================================================

    def get_storage_stats(self):
        """Calculate comprehensive storage statistics.

        Analyzes the entire storage directory to provide metrics about
        evidence counts, storage sizes, and health indicators.

        Returns:
            StorageStats: Statistics about evidence storage

        Example:
            >>> storage = EvidenceStorage()
            >>> stats = storage.get_storage_stats()
            >>> print(f"Total evidence: {stats.total_evidence}")
        """
        from .models import StorageStats

        # Count evidence directories
        evidence_dirs = list(self.derived_dir.glob("sha256=*"))
        total_evidence = len(evidence_dirs)

        # Count by type (load each analysis.v1.json)
        evidence_by_type = {}
        for evidence_dir in evidence_dirs:
            analysis_file = evidence_dir / "analysis.v1.json"
            if analysis_file.exists():
                data = read_json_safe(analysis_file)
                if data:
                    evidence_type = data.get('evidence_type', 'unknown')
                    evidence_by_type[evidence_type] = evidence_by_type.get(evidence_type, 0) + 1

        # Calculate sizes
        raw_size = sum(f.stat().st_size for f in self.raw_dir.rglob("*") if f.is_file())
        derived_size = sum(f.stat().st_size for f in self.derived_dir.rglob("*") if f.is_file())

        # Count cases and labels
        total_cases = len([d for d in self.cases_dir.iterdir() if d.is_dir()])
        label_dirs = [d for d in self.labels_dir.iterdir() if d.is_dir()]
        total_labels = len(label_dirs)

        # Detect orphans (evidence not linked to any case)
        orphaned = self._find_orphaned_evidence()

        return StorageStats(
            total_evidence=total_evidence,
            evidence_by_type=evidence_by_type,
            total_cases=total_cases,
            total_labels=total_labels,
            storage_size_mb=(raw_size + derived_size) / (1024 * 1024),
            raw_size_mb=raw_size / (1024 * 1024),
            derived_size_mb=derived_size / (1024 * 1024),
            orphaned_files=len(orphaned)
        )

    def cleanup_storage(self, dry_run: bool = True):
        """Clean up orphaned links and empty directories.

        Removes broken hard links in the labels directory and cleans up
        empty label directories. Respects dry-run mode for safety.

        Args:
            dry_run: If True, only reports what would be cleaned (default: True)

        Returns:
            CleanupResult: Summary of cleanup operations

        Example:
            >>> storage = EvidenceStorage()
            >>> result = storage.cleanup_storage(dry_run=True)
            >>> print(f"Would remove {result.broken_links_removed} broken links")
        """
        from .models import CleanupResult

        broken_links = 0
        empty_dirs = 0

        # Find broken hard links in labels/
        for label_dir in self.labels_dir.iterdir():
            if label_dir.is_dir() and label_dir.name != ".gitkeep":
                for link in label_dir.iterdir():
                    # Check if it's a broken link or file doesn't exist
                    if not link.exists() or (link.is_symlink() and not link.resolve().exists()):
                        if not dry_run:
                            link.unlink()
                        broken_links += 1

                # Remove empty label directories (after removing broken links)
                try:
                    remaining_files = list(label_dir.iterdir())
                    if not remaining_files:
                        if not dry_run:
                            label_dir.rmdir()
                        empty_dirs += 1
                except OSError:
                    pass  # Directory not empty or other error

        # Find orphaned files for reporting
        orphaned = self._find_orphaned_evidence()

        return CleanupResult(
            broken_links_removed=broken_links,
            empty_dirs_removed=empty_dirs,
            orphaned_files=len(orphaned),
            dry_run=dry_run
        )

    def prune_case_evidence(self, case_id: str, dry_run: bool = True) -> List[str]:
        """Remove evidence unique to a specific case.

        Only removes evidence that belongs EXCLUSIVELY to the specified case.
        Evidence shared with other cases is preserved.

        Args:
            case_id: Case ID to prune evidence for
            dry_run: If True, only reports what would be removed (default: True)

        Returns:
            List of SHA256 hashes that were (or would be) removed

        Example:
            >>> storage = EvidenceStorage()
            >>> removed = storage.prune_case_evidence("CASE-001", dry_run=True)
            >>> print(f"Would remove {len(removed)} evidence items")
        """
        removed = []

        # Get all evidence for this case
        case_evidence = set(self.list_evidence(case_id))

        for sha256 in case_evidence:
            # Check if evidence belongs to other cases
            analysis = self.get_analysis(sha256)
            if analysis and len(analysis.case_ids) == 1 and case_id in analysis.case_ids:
                # This evidence only belongs to this case - safe to remove
                if not dry_run:
                    # Remove from raw/, derived/, labels/, cases/
                    raw_dir = get_evidence_base_dir(self.raw_dir, sha256)
                    evidence_dir = get_evidence_base_dir(self.derived_dir, sha256)

                    if raw_dir.exists():
                        shutil.rmtree(raw_dir)
                    if evidence_dir.exists():
                        shutil.rmtree(evidence_dir)

                    # Remove from case directory
                    case_dir = self.cases_dir / case_id
                    for case_file in case_dir.iterdir():
                        if sha256 in case_file.name:
                            case_file.unlink()

                removed.append(sha256)

        return removed

    def list_cases(self):
        """List all cases with metadata.

        Retrieves metadata for all cases in storage, including evidence counts,
        types, sizes, and last modification times.

        Returns:
            List of CaseInfo objects sorted by last_modified (most recent first)

        Example:
            >>> storage = EvidenceStorage()
            >>> cases = storage.list_cases()
            >>> for case in cases:
            ...     print(f"{case.case_id}: {case.evidence_count} items")
        """
        from .models import CaseInfo

        cases = []

        for case_dir in self.cases_dir.iterdir():
            if case_dir.is_dir():
                # Get evidence count and types
                evidence_sha256s = self.list_evidence(case_dir.name)
                evidence_types = set()
                total_size = 0

                for sha256 in evidence_sha256s:
                    analysis = self.get_analysis(sha256)
                    if analysis:
                        evidence_types.add(analysis.evidence_type.value)
                        total_size += analysis.file_metadata.file_size

                # Get last modified time
                last_modified = datetime.fromtimestamp(case_dir.stat().st_mtime)

                cases.append(CaseInfo(
                    case_id=case_dir.name,
                    evidence_count=len(evidence_sha256s),
                    evidence_types=sorted(list(evidence_types)),
                    last_modified=last_modified,
                    total_size_mb=total_size / (1024 * 1024)
                ))

        return sorted(cases, key=lambda x: x.last_modified, reverse=True)

    def _find_orphaned_evidence(self) -> List[str]:
        """Find evidence not linked to any case.

        Internal helper method to identify orphaned evidence files.

        Returns:
            List of SHA256 hashes for orphaned evidence
        """
        orphaned = []

        # Get all evidence SHA256s
        all_evidence = set(self.list_evidence())

        # Get evidence linked to cases
        linked_evidence = set()
        for case_dir in self.cases_dir.iterdir():
            if case_dir.is_dir():
                linked_evidence.update(self.list_evidence(case_dir.name))

        # Find orphans (in all_evidence but not in linked_evidence)
        orphaned = list(all_evidence - linked_evidence)

        return orphaned
