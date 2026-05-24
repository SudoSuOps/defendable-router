from __future__ import annotations

from pathlib import Path
from typing import Literal

import orjson

from defendablerouter.core.manifest import (
    build_manifest,
    write_manifest,
    write_sha256sums,
)
from defendablerouter.schemas.ddeed_stub import DDEEDStub
from defendablerouter.schemas.router_receipt import RouterReceipt
from defendablerouter.schemas.tribunal_stub import TribunalStub

Target = Literal["local"]


def write_tribunal_stub(stub: TribunalStub, run_dir: Path) -> Path:
    path = run_dir / "tribunal_stub.json"
    path.write_bytes(
        orjson.dumps(stub.model_dump(mode="json"), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )
    return path


def write_ddeed_stub(stub: DDEEDStub, run_dir: Path) -> Path:
    path = run_dir / "ddeed_stub.json"
    path.write_bytes(
        orjson.dumps(stub.model_dump(mode="json"), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )
    return path


def write_object_storage_path(receipt: RouterReceipt, run_dir: Path) -> Path:
    path = run_dir / "object_storage_path.txt"
    path.write_text(receipt.object_storage.uri + "\n", encoding="utf-8")
    return path


def finalize_run(receipt: RouterReceipt, run_dir: Path) -> Path:
    """Build manifest + SHA256SUMS + object_storage_path. Returns manifest path."""
    write_object_storage_path(receipt, run_dir)
    manifest = build_manifest(run_dir, receipt.assignment_id, receipt.receipt_id)
    write_manifest(manifest, run_dir)
    write_sha256sums(manifest, run_dir)
    return run_dir / "manifest.json"


def export_run(run_dir: Path, target: Target = "local") -> Path:
    """Export hook. Currently 'local' is a no-op; future targets (s3, ipfs) plug here."""
    if target != "local":
        raise ValueError(f"unsupported export target: {target}")
    return run_dir
