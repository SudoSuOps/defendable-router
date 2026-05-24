from __future__ import annotations

from pathlib import Path
from typing import List

import orjson

from defendablerouter.core.canonicalize import canonicalize_for_hash
from defendablerouter.core.hash import sha256_bytes, sha256_file
from defendablerouter.core.ids import manifest_id as new_manifest_id, utc_now_iso
from defendablerouter.schemas.manifest import Manifest, ManifestFile

MANIFEST_FILE = "manifest.json"
SHA256SUMS_FILE = "SHA256SUMS.txt"
MANIFEST_VOLATILE = {"manifest_id", "created_at", "manifest_sha256"}

FILE_TYPES = {
    "input.json": "router_input",
    "router_receipt.json": "router_receipt",
    "tribunal_stub.json": "tribunal_stub",
    "ddeed_stub.json": "ddeed_stub",
    "kimi_review.json": "agent_review",
}


def _classify(name: str) -> str:
    return FILE_TYPES.get(name, "artifact")


def build_manifest(run_dir: Path, assignment_id: str, receipt_id: str) -> Manifest:
    files: List[ManifestFile] = []
    for p in sorted(run_dir.iterdir()):
        if not p.is_file():
            continue
        if p.name in (MANIFEST_FILE, SHA256SUMS_FILE, "object_storage_path.txt"):
            continue
        files.append(
            ManifestFile(
                path=p.name,
                sha256=sha256_file(p),
                bytes=p.stat().st_size,
                type=_classify(p.name),
            )
        )

    manifest = Manifest(
        manifest_id=new_manifest_id(),
        created_at=utc_now_iso(),
        assignment_id=assignment_id,
        receipt_id=receipt_id,
        files=files,
    )
    body = manifest.model_dump(mode="json")
    manifest.manifest_sha256 = sha256_bytes(canonicalize_for_hash(body, MANIFEST_VOLATILE))
    return manifest


def write_manifest(manifest: Manifest, run_dir: Path) -> Path:
    path = run_dir / MANIFEST_FILE
    body = manifest.model_dump(mode="json")
    path.write_bytes(orjson.dumps(body, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return path


def write_sha256sums(manifest: Manifest, run_dir: Path) -> Path:
    path = run_dir / SHA256SUMS_FILE
    lines = [f"{f.sha256}  {f.path}" for f in manifest.files]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
