from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Union

from defendablerouter.core.canonicalize import canonical_json_bytes, canonicalize_for_hash


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_str(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def sha256_file(path: Union[str, Path]) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_canonical_json(obj: Any) -> str:
    """Hash of the full deterministic JSON (used for receipt_sha256)."""
    return sha256_bytes(canonical_json_bytes(obj))


def sha256_canonical_for_receipt(obj: Any) -> str:
    """Hash of canonical form with volatile fields stripped (canonical_receipt_sha256)."""
    return sha256_bytes(canonicalize_for_hash(obj))
