from pathlib import Path

import orjson
import pytest

from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    export_run,
    finalize_run,
    write_ddeed_stub,
    write_object_storage_path,
    write_tribunal_stub,
)
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.schemas.router_event import RouterEvent

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


def _run(tmp_path: Path) -> Path:
    event = RouterEvent.model_validate(orjson.loads(EXAMPLE.read_bytes()))
    receipt = build_receipt(event)
    trib = create_tribunal_stub(receipt.assignment_id)
    receipt.tribunal.verdict_id = trib.verdict_id
    deed = create_ddeed_stub(receipt.receipt_id, receipt.assignment_id)
    receipt.ddeed.deed_id = deed.deed_id
    finalize_receipt_hashes(receipt)
    write_event_input(event, tmp_path)
    write_tribunal_stub(trib, tmp_path)
    write_ddeed_stub(deed, tmp_path)
    write_receipt(receipt, tmp_path)
    finalize_run(receipt, tmp_path)
    return tmp_path


def test_run_directory_contents(tmp_path: Path):
    run = _run(tmp_path)
    expected = {
        "input.json",
        "router_receipt.json",
        "tribunal_stub.json",
        "ddeed_stub.json",
        "manifest.json",
        "SHA256SUMS.txt",
        "object_storage_path.txt",
    }
    names = {p.name for p in run.iterdir()}
    assert expected.issubset(names)


def test_object_storage_path_file_matches_receipt(tmp_path: Path):
    run = _run(tmp_path)
    receipt = orjson.loads((run / "router_receipt.json").read_bytes())
    uri = (run / "object_storage_path.txt").read_text().strip()
    assert uri == receipt["object_storage"]["uri"]
    assert uri.startswith("s3://streetledger/router/")


def test_export_local_is_idempotent(tmp_path: Path):
    run = _run(tmp_path)
    assert export_run(run, target="local") == run


def test_export_rejects_unknown_target(tmp_path: Path):
    run = _run(tmp_path)
    with pytest.raises(ValueError):
        export_run(run, target="rogue")  # type: ignore[arg-type]
