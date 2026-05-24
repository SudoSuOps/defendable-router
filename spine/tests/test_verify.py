from pathlib import Path

import orjson

from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    finalize_run,
    write_ddeed_stub,
    write_tribunal_stub,
)
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.core.verify import verify_run
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


def test_verify_clean_run_passes(tmp_path: Path):
    _populate(tmp_path)
    result = verify_run(tmp_path)
    assert result.ok, result.errors
    assert result.canonical_match
    assert result.receipt_match
    assert result.manifest_match
    assert result.sha256sums_match


def test_verify_detects_tampered_receipt(tmp_path: Path):
    _populate(tmp_path)
    rp = tmp_path / "router_receipt.json"
    body = orjson.loads(rp.read_bytes())
    body["client_id"] = "ATTACKER.eth"
    rp.write_bytes(orjson.dumps(body, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    result = verify_run(tmp_path)
    assert not result.ok
    assert any("canonical" in e for e in result.errors)


def test_verify_detects_tampered_artifact(tmp_path: Path):
    _populate(tmp_path)
    (tmp_path / "input.json").write_bytes(b"{\"forged\":true}")
    result = verify_run(tmp_path)
    assert not result.ok
    assert any("hash mismatch input.json" in e or "SHA256SUMS" in e for e in result.errors)
