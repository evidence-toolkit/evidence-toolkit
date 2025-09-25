"""Centralised filesystem layout helpers."""

from __future__ import annotations

from pathlib import Path


class Layout:
    """Content-addressed directory layout used by the toolkit."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.cwd()
        self.evidence = self.root / "evidence"
        self.raw = self.evidence / "raw"
        self.derived = self.evidence / "derived"
        self.labels = self.evidence / "labels"
        self.db = self.root / "db" / "evidence.sqlite"
        self.logs = self.root / "logs"

    def content_paths(self, sha256_hex: str, ext: str):
        raw_dir = self.raw / f"sha256={sha256_hex}"
        derived_dir = self.derived / f"sha256={sha256_hex}"
        raw_file = raw_dir / f"original{ext}"
        return raw_dir, derived_dir, raw_file


__all__ = ["Layout"]
