import json
from pathlib import Path

from defendablerouter.core.ledger import (
    ZERO_HASH,
    append_payload_file,
    append_record,
    read_records,
    verify_ledger,
)


def _set_path(tmp_path: Path, monkeypatch) -> Path:
    p = tmp_path / "ledger" / "defendable_ledger.jsonl"
    monkeypatch.setenv("DEFENDABLE_LEDGER_PATH", str(p))
    return p


def test_genesis_then_one_record_verifies(tmp_path: Path, monkeypatch):
    _set_path(tmp_path, monkeypatch)
    r1 = append_record(
        record_type="RECEIPT",
        payload_ref="data/runs/x/router_receipt.json",
        payload_hash="a" * 64,
        issued_by="DefendableRouter",
        host="smash",
    )
    assert r1.ledger_seq == 1  # 0 is genesis
    assert r1.parent_hash != ZERO_HASH  # parent is genesis hash, not zero

    result = verify_ledger()
    assert result.ok, result.errors
    assert result.records_checked == 2  # genesis + first record


def test_chain_links_correctly_across_many_records(tmp_path: Path, monkeypatch):
    _set_path(tmp_path, monkeypatch)
    parents = []
    for i in range(5):
        r = append_record(
            record_type="RECEIPT" if i % 2 == 0 else "VERDICT",
            payload_ref=f"x/{i}.json",
            payload_hash=str(i) * 64,
            issued_by="t",
            host="smash",
        )
        parents.append(r.parent_hash)

    records = read_records()
    # Genesis + 5
    assert len(records) == 6
    for i in range(1, 6):
        assert records[i].parent_hash == records[i - 1].record_sha256

    assert verify_ledger().ok


def test_verify_detects_tampered_record(tmp_path: Path, monkeypatch):
    p = _set_path(tmp_path, monkeypatch)
    append_record(
        record_type="RECEIPT",
        payload_ref="x.json",
        payload_hash="a" * 64,
        issued_by="t",
        host="smash",
    )
    # Tamper: rewrite line 2 (the receipt record) with a different payload_hash but keep its
    # stored record_sha256 — this should be detected
    lines = p.read_text().splitlines()
    rec = json.loads(lines[1])
    rec["payload_hash"] = "b" * 64
    lines[1] = json.dumps(rec, sort_keys=True)
    p.write_text("\n".join(lines) + "\n")

    result = verify_ledger()
    assert not result.ok
    assert result.first_break_seq is not None


def test_append_payload_file_hashes_actual_file(tmp_path: Path, monkeypatch):
    _set_path(tmp_path, monkeypatch)
    payload = tmp_path / "blob.json"
    payload.write_bytes(b'{"hello":"world"}')
    rec = append_payload_file(
        record_type="DEED",
        payload_path=payload,
        issued_by="t",
        host="smash",
        base_dir=tmp_path,
    )
    assert rec.payload_ref == "blob.json"
    assert len(rec.payload_hash) == 64
    assert verify_ledger().ok
