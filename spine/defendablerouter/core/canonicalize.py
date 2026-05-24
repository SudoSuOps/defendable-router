from __future__ import annotations

from typing import Any, Iterable, Set

import orjson

VOLATILE_KEYS: Set[str] = {
    "created_at",
    "hashes",
    "receipt_sha256",
    "canonical_receipt_sha256",
    "manifest_sha256",
}


def _strip_volatile(obj: Any, volatile: Iterable[str]) -> Any:
    if isinstance(obj, dict):
        return {
            k: _strip_volatile(v, volatile)
            for k, v in obj.items()
            if k not in volatile
        }
    if isinstance(obj, list):
        return [_strip_volatile(v, volatile) for v in obj]
    return obj


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic JSON: sorted keys, no whitespace, UTF-8."""
    return orjson.dumps(obj, option=orjson.OPT_SORT_KEYS)


def canonical_json_str(obj: Any) -> str:
    return canonical_json_bytes(obj).decode("utf-8")


def canonicalize_for_hash(obj: Any, volatile: Iterable[str] = VOLATILE_KEYS) -> bytes:
    """Strip volatile fields, sort keys, return deterministic bytes for hashing."""
    stripped = _strip_volatile(obj, set(volatile))
    return canonical_json_bytes(stripped)
