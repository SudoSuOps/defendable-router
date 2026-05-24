from pathlib import Path

import orjson
import pytest
from pydantic import ValidationError

from defendablerouter.core.receipt import build_receipt, finalize_receipt_hashes
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import RouterReceipt

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


def _event() -> RouterEvent:
    return RouterEvent.model_validate(orjson.loads(EXAMPLE.read_bytes()))


def test_event_validates():
    ev = _event()
    assert ev.client_id == "mrdefendable.eth"
    assert ev.source_type == "call"
    assert "proposal" in ev.assignment.expected_outputs


def test_receipt_builds_from_event():
    r = build_receipt(_event())
    assert r.receipt_type == "DEFENDABLE_ROUTER_RECEIPT"
    assert r.schema_version == "v0.1"
    assert r.receipt_id.startswith("DRR-")
    assert r.assignment_id.startswith("ASSIGN-")
    assert r.input.input_hash and len(r.input.input_hash) == 64
    assert r.object_storage.uri.startswith("s3://streetledger/router/")
    assert r.object_storage.prefix.endswith("/")


def test_receipt_finalize_hashes_populates_both():
    r = finalize_receipt_hashes(build_receipt(_event()))
    assert r.hashes.canonical_receipt_sha256 and len(r.hashes.canonical_receipt_sha256) == 64
    assert r.hashes.receipt_sha256 and len(r.hashes.receipt_sha256) == 64
    assert r.hashes.canonical_receipt_sha256 != r.hashes.receipt_sha256


def test_receipt_forbids_extra_fields():
    with pytest.raises(ValidationError):
        RouterReceipt.model_validate({"receipt_id": "DRR-x", "rogue_field": "x"})
