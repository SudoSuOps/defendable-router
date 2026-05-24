from pathlib import Path

import orjson

from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    finalize_run,
    write_ddeed_stub,
    write_tribunal_stub,
)
from defendablerouter.core.manifest import build_manifest
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.schemas.router_event import RouterEvent

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


def _populate(run_dir: Path):
    event = RouterEvent.model_validate(orjson.loads(EXAMPLE.read_bytes()))
    receipt = build_receipt(event)
    trib = create_tribunal_stub(receipt.assignment_id)
    receipt.tribunal.verdict_id = trib.verdict_id
    deed = create_ddeed_stub(receipt.receipt_id, receipt.assignment_id)
    receipt.ddeed.deed_id = deed.deed_id
    finalize_receipt_hashes(receipt)

    write_event_input(event, run_dir)
    write_tribunal_stub(trib, run_dir)
    write_ddeed_stub(deed, run_dir)
    write_receipt(receipt, run_dir)
    finalize_run(receipt, run_dir)
    return receipt


def test_manifest_lists_expected_files(tmp_path: Path):
    receipt = _populate(tmp_path)
    manifest = build_manifest(tmp_path, receipt.assignment_id, receipt.receipt_id)
    names = sorted(f.path for f in manifest.files)
    assert names == sorted([
        "ddeed_stub.json",
        "input.json",
        "router_receipt.json",
        "tribunal_stub.json",
    ])


def test_manifest_hash_is_deterministic(tmp_path: Path):
    receipt = _populate(tmp_path)
    m1 = build_manifest(tmp_path, receipt.assignment_id, receipt.receipt_id)
    m2 = build_manifest(tmp_path, receipt.assignment_id, receipt.receipt_id)
    assert m1.manifest_sha256 == m2.manifest_sha256
    assert len(m1.manifest_sha256) == 64


def test_sha256sums_written(tmp_path: Path):
    _populate(tmp_path)
    sums = (tmp_path / "SHA256SUMS.txt").read_text()
    assert "router_receipt.json" in sums
    assert "tribunal_stub.json" in sums
    assert "ddeed_stub.json" in sums
    assert "input.json" in sums
