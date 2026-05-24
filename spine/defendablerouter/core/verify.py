from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import orjson

from defendablerouter.core.canonicalize import canonical_json_bytes, canonicalize_for_hash
from defendablerouter.core.hash import (
    sha256_bytes,
    sha256_canonical_for_receipt,
    sha256_file,
)
from defendablerouter.core.manifest import (
    MANIFEST_FILE,
    MANIFEST_VOLATILE,
    SHA256SUMS_FILE,
)


@dataclass
class VerifyResult:
    ok: bool
    run_dir: str
    receipt_id: str = ""
    canonical_match: bool = False
    receipt_match: bool = False
    manifest_match: bool = False
    sha256sums_match: bool = False
    errors: List[str] = field(default_factory=list)
    checked_files: List[str] = field(default_factory=list)


def _load(path: Path) -> Dict[str, Any]:
    return orjson.loads(path.read_bytes())


def verify_run(run_dir: Path) -> VerifyResult:
    result = VerifyResult(ok=False, run_dir=str(run_dir))

    receipt_path = run_dir / "router_receipt.json"
    if not receipt_path.exists():
        result.errors.append("router_receipt.json missing")
        return result

    receipt = _load(receipt_path)
    result.receipt_id = receipt.get("receipt_id", "")

    stored_canonical = (receipt.get("hashes") or {}).get("canonical_receipt_sha256")
    stored_receipt = (receipt.get("hashes") or {}).get("receipt_sha256")
    computed_canonical = sha256_canonical_for_receipt(receipt)
    result.canonical_match = stored_canonical == computed_canonical
    if not result.canonical_match:
        result.errors.append(
            f"canonical_receipt_sha256 mismatch: stored={stored_canonical} computed={computed_canonical}"
        )

    body_with_canonical = dict(receipt)
    body_with_canonical["hashes"] = {
        "receipt_sha256": None,
        "canonical_receipt_sha256": computed_canonical,
    }
    computed_receipt = sha256_bytes(canonical_json_bytes(body_with_canonical))
    result.receipt_match = stored_receipt == computed_receipt
    if not result.receipt_match:
        result.errors.append(
            f"receipt_sha256 mismatch: stored={stored_receipt} computed={computed_receipt}"
        )

    manifest_path = run_dir / MANIFEST_FILE
    if not manifest_path.exists():
        result.errors.append(f"{MANIFEST_FILE} missing")
        return result
    manifest = _load(manifest_path)
    stored_manifest_hash = manifest.get("manifest_sha256", "")
    computed_manifest = sha256_bytes(canonicalize_for_hash(manifest, MANIFEST_VOLATILE))
    result.manifest_match = stored_manifest_hash == computed_manifest
    if not result.manifest_match:
        result.errors.append(
            f"manifest_sha256 mismatch: stored={stored_manifest_hash} computed={computed_manifest}"
        )

    file_mismatches: List[str] = []
    for entry in manifest.get("files", []):
        fpath = run_dir / entry["path"]
        result.checked_files.append(entry["path"])
        if not fpath.exists():
            file_mismatches.append(f"missing file {entry['path']}")
            continue
        actual = sha256_file(fpath)
        if actual != entry["sha256"]:
            file_mismatches.append(
                f"hash mismatch {entry['path']}: stored={entry['sha256']} actual={actual}"
            )

    sums_path = run_dir / SHA256SUMS_FILE
    if sums_path.exists():
        sums_lines = [
            line.strip().split("  ", 1)
            for line in sums_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        sums_map = {name: digest for digest, name in sums_lines}
        manifest_map = {f["path"]: f["sha256"] for f in manifest.get("files", [])}
        result.sha256sums_match = sums_map == manifest_map
        if not result.sha256sums_match:
            result.errors.append("SHA256SUMS.txt does not match manifest entries")
    else:
        result.errors.append(f"{SHA256SUMS_FILE} missing")

    if file_mismatches:
        result.errors.extend(file_mismatches)

    result.ok = (
        result.canonical_match
        and result.receipt_match
        and result.manifest_match
        and result.sha256sums_match
        and not file_mismatches
    )
    return result
