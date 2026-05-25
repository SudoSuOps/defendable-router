from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import orjson

from defendablerouter.core.canonicalize import canonicalize_for_hash
from defendablerouter.core.hash import sha256_bytes, sha256_file
from defendablerouter.core.ids import ledger_record_id, utc_now_iso
from defendablerouter.schemas.ledger_record import LedgerRecord, RecordType

LEDGER_VOLATILE = {"record_sha256"}
ZERO_HASH = "0" * 64
DEFAULT_LEDGER_PATH = "data/ledger/defendable_ledger.jsonl"


def ledger_path() -> Path:
    return Path(os.environ.get("DEFENDABLE_LEDGER_PATH", DEFAULT_LEDGER_PATH))


def _hash_record(rec: LedgerRecord) -> str:
    body = rec.model_dump(mode="json")
    return sha256_bytes(canonicalize_for_hash(body, LEDGER_VOLATILE))


def _read_last_record(path: Path) -> Optional[LedgerRecord]:
    if not path.exists():
        return None
    last_line = ""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last_line = line
    if not last_line:
        return None
    return LedgerRecord(**json.loads(last_line))


def _next_seq_and_parent(path: Path) -> tuple[int, str]:
    last = _read_last_record(path)
    if last is None:
        return 0, ZERO_HASH
    return last.ledger_seq + 1, (last.record_sha256 or ZERO_HASH)


def _ensure_genesis(path: Path, host: str) -> LedgerRecord:
    path.parent.mkdir(parents=True, exist_ok=True)
    last = _read_last_record(path)
    if last is not None:
        return last
    gen = LedgerRecord(
        ledger_seq=0,
        record_id=f"DLR-GENESIS-{utc_now_iso()}",
        record_type="GENESIS",
        created_at=utc_now_iso(),
        parent_hash=ZERO_HASH,
        payload_ref="",
        payload_hash=ZERO_HASH,
        issued_by="DefendableLedger",
        host=host,
    )
    gen.record_sha256 = _hash_record(gen)
    _append_line(path, gen)
    return gen


def _append_line(path: Path, rec: LedgerRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = orjson.dumps(rec.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def append_record(
    record_type: RecordType,
    payload_ref: str,
    payload_hash: str,
    issued_by: str,
    host: str = "smash",
    path: Optional[Path] = None,
) -> LedgerRecord:
    """Append a single hash-chained record. Returns the record (with record_sha256 filled)."""
    p = path or ledger_path()
    _ensure_genesis(p, host)

    seq, parent = _next_seq_and_parent(p)
    rec = LedgerRecord(
        ledger_seq=seq,
        record_id=ledger_record_id(),
        record_type=record_type,
        created_at=utc_now_iso(),
        parent_hash=parent,
        payload_ref=payload_ref,
        payload_hash=payload_hash,
        issued_by=issued_by,
        host=host,
    )
    rec.record_sha256 = _hash_record(rec)
    _append_line(p, rec)
    return rec


def append_payload_file(
    record_type: RecordType,
    payload_path: Path,
    issued_by: str,
    host: str = "smash",
    base_dir: Optional[Path] = None,
    path: Optional[Path] = None,
) -> LedgerRecord:
    """Hash a file and append a record pointing at it. payload_ref is relative to base_dir if given."""
    digest = sha256_file(payload_path)
    if base_dir is not None:
        try:
            ref = str(payload_path.relative_to(base_dir))
        except ValueError:
            ref = str(payload_path)
    else:
        ref = str(payload_path)
    return append_record(
        record_type=record_type,
        payload_ref=ref,
        payload_hash=digest,
        issued_by=issued_by,
        host=host,
        path=path,
    )


@dataclass
class LedgerVerifyResult:
    ok: bool
    records_checked: int = 0
    first_break_seq: Optional[int] = None
    errors: List[str] = field(default_factory=list)


def verify_ledger(path: Optional[Path] = None) -> LedgerVerifyResult:
    p = path or ledger_path()
    if not p.exists():
        return LedgerVerifyResult(ok=True, records_checked=0)

    expected_parent = ZERO_HASH
    expected_seq = 0
    result = LedgerVerifyResult(ok=True)
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = LedgerRecord(**json.loads(line))
            result.records_checked += 1

            if rec.ledger_seq != expected_seq:
                result.errors.append(
                    f"seq gap at line {result.records_checked}: expected {expected_seq}, got {rec.ledger_seq}"
                )
                result.first_break_seq = result.first_break_seq if result.first_break_seq is not None else rec.ledger_seq
                result.ok = False

            if rec.parent_hash != expected_parent:
                result.errors.append(
                    f"chain break at seq {rec.ledger_seq}: parent_hash mismatch"
                )
                result.first_break_seq = result.first_break_seq if result.first_break_seq is not None else rec.ledger_seq
                result.ok = False

            recomputed = _hash_record(rec)
            if rec.record_sha256 != recomputed:
                result.errors.append(
                    f"record_sha256 mismatch at seq {rec.ledger_seq}: stored={rec.record_sha256} computed={recomputed}"
                )
                result.first_break_seq = result.first_break_seq if result.first_break_seq is not None else rec.ledger_seq
                result.ok = False

            expected_parent = rec.record_sha256 or ZERO_HASH
            expected_seq = rec.ledger_seq + 1
    return result


def read_records(path: Optional[Path] = None) -> List[LedgerRecord]:
    p = path or ledger_path()
    if not p.exists():
        return []
    records: List[LedgerRecord] = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(LedgerRecord(**json.loads(line)))
    return records
