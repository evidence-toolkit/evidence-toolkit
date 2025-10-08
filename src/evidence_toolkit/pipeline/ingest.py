#!/usr/bin/env python3
"""Evidence Ingestion Pipeline - v3.0

Handles ingestion of files into content-addressed evidence storage.
Extracted from the monolithic CLI for modular v3.0 architecture.

This module is responsible for:
- File ingestion into content-addressed storage
- Metadata extraction and preservation
- Chain of custody initialization
- Deduplication based on SHA256 hashing
"""

from pathlib import Path
from typing import List, Optional

from evidence_toolkit.core.storage import EvidenceStorage
from evidence_toolkit.core.models import IngestionResult


def ingest_evidence(
    file_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system"
) -> IngestionResult:
    """Ingest a single file into evidence storage.

    Args:
        file_path: Path to file to ingest
        storage: EvidenceStorage instance for storage operations
        case_id: Optional case ID to associate with this evidence
        actor: Actor performing the ingestion (default: system)

    Returns:
        IngestionResult with ingestion status and metadata
    """
    return storage.ingest_file(file_path, case_id=case_id, actor=actor)


def ingest_directory(
    directory_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system",
    quiet: bool = False
) -> List[IngestionResult]:
    """Ingest all files from a directory into evidence storage.

    Args:
        directory_path: Path to directory containing files
        storage: EvidenceStorage instance for storage operations
        case_id: Optional case ID to associate with all evidence
        actor: Actor performing the ingestion (default: system)
        quiet: Suppress verbose output

    Returns:
        List of IngestionResult objects, one per file
    """
    ingested_files = []

    for file_path in directory_path.rglob('*'):
        if file_path.is_file() and not file_path.name.startswith('.'):
            result = storage.ingest_file(
                file_path,
                case_id=case_id,
                actor=actor
            )
            ingested_files.append(result)

    return ingested_files


def ingest_path(
    input_path: Path,
    storage: EvidenceStorage,
    case_id: Optional[str] = None,
    actor: str = "system",
    quiet: bool = False
) -> List[IngestionResult]:
    """Ingest file(s) from path (file or directory) into evidence storage.

    This is a convenience function that routes to either single file ingestion
    or directory ingestion based on the input path type.

    Args:
        input_path: Path to file or directory
        storage: EvidenceStorage instance for storage operations
        case_id: Optional case ID to associate with evidence
        actor: Actor performing the ingestion (default: system)
        quiet: Suppress verbose output

    Returns:
        List of IngestionResult objects

    Raises:
        FileNotFoundError: If input_path doesn't exist
        ValueError: If input_path is neither file nor directory
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input path '{input_path}' does not exist")

    if input_path.is_file():
        # Single file ingestion
        result = ingest_evidence(input_path, storage, case_id, actor)
        return [result]

    elif input_path.is_dir():
        # Directory ingestion
        return ingest_directory(input_path, storage, case_id, actor, quiet)

    else:
        raise ValueError(f"Input path '{input_path}' is neither a file nor a directory")


def print_ingestion_summary(
    results: List[IngestionResult],
    quiet: bool = False
) -> None:
    """Print summary of ingestion results.

    Args:
        results: List of IngestionResult objects
        quiet: Suppress verbose output
    """
    if quiet:
        return

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    print(f"\n📥 Ingestion Summary:")
    print(f"   Files processed: {len(results)}")
    print(f"   Successfully ingested: {len(successful)}")
    print(f"   Failed: {len(failed)}")

    if successful:
        print("\n✅ Successfully ingested:")
        for result in successful[:5]:  # Show first 5
            print(f"   {result.sha256[:12]}... ({result.evidence_type}) - {result.file_path}")
        if len(successful) > 5:
            print(f"   ... and {len(successful) - 5} more")

    if failed:
        print("\n❌ Failed to ingest:")
        for result in failed:
            print(f"   {result.file_path}: {result.message}")


__all__ = [
    'ingest_evidence',
    'ingest_directory',
    'ingest_path',
    'print_ingestion_summary',
]
