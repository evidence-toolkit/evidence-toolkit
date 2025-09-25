#!/usr/bin/env python3
"""
Evidence Manager - Content-addressed storage and management
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
    create_hard_link
)
from .unified_models import (
    UnifiedAnalysis,
    IngestionResult,
    ExportResult,
    FileMetadata,
    ChainOfCustodyEvent,
    EvidenceType
)


class EvidenceManager:
    """Manages content-addressed evidence storage"""

    def __init__(self, evidence_root: Path = Path("evidence")):
        """Initialize evidence manager with storage root"""
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
        """Ingest a file into content-addressed storage"""
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
            raw_hash_dir = self.raw_dir / f"sha256={sha256}"
            derived_hash_dir = self.derived_dir / f"sha256={sha256}"

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

            # Save chain of custody
            self._save_chain_of_custody(sha256, [custody_event])

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
        """Retrieve analysis for a given SHA256"""
        analysis_file = self.derived_dir / f"sha256={sha256}" / "analysis.v1.json"

        if not analysis_file.exists():
            return None

        try:
            with open(analysis_file, 'r') as f:
                data = json.load(f)
            return UnifiedAnalysis.model_validate(data)
        except Exception as e:
            print(f"Error loading analysis for {sha256}: {e}")
            return None

    def save_analysis(self, analysis: UnifiedAnalysis) -> bool:
        """Save unified analysis result"""
        try:
            sha256 = analysis.file_metadata.sha256
            derived_hash_dir = self.derived_dir / f"sha256={sha256}"

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

            return True

        except Exception as e:
            print(f"Error saving analysis for {analysis.file_metadata.sha256}: {e}")
            return False

    def export_analysis(self, sha256: str, output_path: Path) -> ExportResult:
        """Export analysis to specified path"""
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
        """List all evidence SHA256s, optionally filtered by case"""
        if case_id:
            case_dir = self.cases_dir / case_id
            if case_dir.exists():
                return [f.stem.split('.')[0] for f in case_dir.iterdir() if f.is_file()]
            return []

        # List all evidence
        evidence_dirs = [d for d in self.derived_dir.iterdir() if d.is_dir() and d.name.startswith("sha256=")]
        return [d.name.split("=")[1] for d in evidence_dirs]

    def _save_chain_of_custody(self, sha256: str, events: List[ChainOfCustodyEvent]):
        """Save chain of custody events"""
        custody_file = self.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"
        events_data = [event.model_dump() for event in events]

        with open(custody_file, 'w') as f:
            json.dump(events_data, f, indent=2, default=str)

    def _add_custody_event(self, sha256: str, event: ChainOfCustodyEvent):
        """Add a chain of custody event"""
        custody_file = self.derived_dir / f"sha256={sha256}" / "chain_of_custody.json"

        # Load existing events
        events = []
        if custody_file.exists():
            try:
                with open(custody_file, 'r') as f:
                    events_data = json.load(f)
                    events = [ChainOfCustodyEvent.model_validate(e) for e in events_data]
            except Exception as e:
                print(f"Warning: Could not load existing custody events: {e}")

        # Add new event
        events.append(event)
        self._save_chain_of_custody(sha256, events)

    def _create_label_link(self, sha256: str, label: str, extension: str):
        """Create hard link in labels directory"""
        original_file = self.raw_dir / f"sha256={sha256}" / f"original{extension}"
        if original_file.exists():
            label_dir = self.labels_dir / label
            label_link = label_dir / f"{sha256}{extension}"
            create_hard_link(original_file, label_link)

    def get_original_file_path(self, sha256: str) -> Optional[Path]:
        """Get path to original file for given SHA256"""
        raw_hash_dir = self.raw_dir / f"sha256={sha256}"
        if not raw_hash_dir.exists():
            return None

        # Look for original file
        for file_path in raw_hash_dir.iterdir():
            if file_path.name.startswith("original"):
                return file_path

        return None