"""Utility helpers for hashing, metadata extraction, and custody events."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import piexif
from PIL import Image

UTC = timezone.utc


def now_utc() -> datetime:
    return datetime.now(UTC)


def to_naive_utc(dt: datetime) -> datetime:
    """Return a timezone-naive UTC datetime suitable for SQLite storage."""

    return dt.astimezone(UTC).replace(tzinfo=None)


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def _dct_1d(vector: np.ndarray) -> np.ndarray:
    n = vector.shape[0]
    result = np.zeros_like(vector, dtype=np.float32)
    for k in range(n):
        coeff = np.sqrt(1.0 / n) if k == 0 else np.sqrt(2.0 / n)
        cos_terms = np.cos(((2 * np.arange(n) + 1) * k * np.pi) / (2 * n))
        result[k] = coeff * np.sum(vector * cos_terms)
    return result


def _dct_2d(matrix: np.ndarray) -> np.ndarray:
    temp = np.apply_along_axis(_dct_1d, axis=1, arr=matrix)
    return np.apply_along_axis(_dct_1d, axis=0, arr=temp)


def compute_phash(path: Path) -> str:
    with Image.open(path) as img:
        img = img.convert("L").resize((32, 32), Image.LANCZOS)
        pixels = np.asarray(img, dtype=np.float32)
    dct = _dct_2d(pixels)
    low_freq = dct[:8, :8]
    median = np.median(low_freq[1:, 1:])
    bits = (low_freq > median).flatten()
    return "".join("1" if bit else "0" for bit in bits)


def read_dimensions(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.width, img.height


def load_exif(path: Path) -> dict[str, Any]:
    try:
        exif_data = piexif.load(str(path))
    except (ValueError, piexif.InvalidImageDataError, FileNotFoundError):
        return {}

    def decode(value: Any) -> Any:
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8", errors="ignore")
            except Exception:
                return value.decode("latin-1", errors="ignore")
        if isinstance(value, tuple):
            return [decode(v) for v in value]
        return value

    normalized: dict[str, Any] = {}
    for ifd_name, ifd_dict in exif_data.items():
        if isinstance(ifd_dict, dict):
            normalized[ifd_name] = {key: decode(val) for key, val in ifd_dict.items()}
    return normalized


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def append_json_lines(path: Path, records: Iterable[Any]) -> None:
    ensure_directory(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + os.linesep)
