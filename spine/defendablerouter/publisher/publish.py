from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import orjson

from defendablerouter.core.canonicalize import canonical_json_bytes
from defendablerouter.core.hash import sha256_bytes, sha256_file
from defendablerouter.core.ids import utc_now_iso
from defendablerouter.core.ledger import ledger_path, read_records
from defendablerouter.schemas.ledger_record import LedgerRecord

CURSOR_FILE = "published_cursor.txt"
RECORDS_SUBDIR = "public/records"
LEDGER_MIRROR_SUBDIR = "public/ledger"
INDEX_FILE = "index.json"
PAYLOAD_TYPE_MAP = {
    "RECEIPT": "receipts",
    "VERDICT": "verdicts",
    "PAIR": "pairs",
    "DEED": "deeds",
    "AUDIT": "audits",
}

NATURAL_ID_KEY = {
    "RECEIPT": "receipt_id",
    "VERDICT": "verdict_id",
    "PAIR": "pair_id",
    "DEED": "deed_id",
    "AUDIT": "audit_id",
}


@dataclass
class PublishResult:
    ok: bool
    repo: str
    cursor_before: int
    cursor_after: int
    new_records: int = 0
    copied_files: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    commit_sha: Optional[str] = None
    pushed: bool = False


def _cursor_path(repo: Path) -> Path:
    return repo / RECORDS_SUBDIR / CURSOR_FILE


def _read_cursor(repo: Path) -> int:
    p = _cursor_path(repo)
    if not p.exists():
        return -1
    try:
        return int(p.read_text(encoding="utf-8").strip())
    except Exception:
        return -1


def _write_cursor(repo: Path, seq: int) -> None:
    p = _cursor_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(seq), encoding="utf-8")


def _spine_data_dir() -> Path:
    return ledger_path().resolve().parent.parent  # ledger.jsonl lives in data/ledger/ · parent.parent = data/


def _payload_source(rec: LedgerRecord, data_dir: Path) -> Optional[Path]:
    """Resolve a ledger record's payload_ref to an absolute path on disk."""
    if not rec.payload_ref:
        return None
    p = Path(rec.payload_ref)
    if p.is_absolute() and p.exists():
        return p
    cand = (data_dir / rec.payload_ref).resolve()
    if cand.exists():
        return cand
    cand2 = (data_dir.parent / rec.payload_ref).resolve()
    if cand2.exists():
        return cand2
    return None


def _natural_id(rec: LedgerRecord, payload: Dict[str, Any]) -> str:
    """Pull the payload's own ID (receipt_id / verdict_id / pair_id / deed_id) or fall back to ledger record_id."""
    key = NATURAL_ID_KEY.get(rec.record_type)
    if key and payload.get(key):
        return str(payload[key])
    return rec.record_id


def _target_for(rec: LedgerRecord, payload: Dict[str, Any], repo: Path) -> Path:
    bucket = PAYLOAD_TYPE_MAP.get(rec.record_type, rec.record_type.lower())
    return repo / RECORDS_SUBDIR / bucket / f"{_natural_id(rec, payload)}.json"


def _read_index(repo: Path) -> List[Dict[str, Any]]:
    p = repo / RECORDS_SUBDIR / INDEX_FILE
    if not p.exists():
        return []
    try:
        return orjson.loads(p.read_bytes())
    except Exception:
        return []


def _write_index(repo: Path, entries: List[Dict[str, Any]]) -> Path:
    p = repo / RECORDS_SUBDIR / INDEX_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(orjson.dumps(entries, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return p


def _mirror_ledger_line(repo: Path, rec: LedgerRecord) -> None:
    p = repo / LEDGER_MIRROR_SUBDIR / "defendable_ledger.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    line = orjson.dumps(rec.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
    with open(p, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def publish(
    repo: Path,
    since: Optional[int] = None,
    commit: bool = False,
    push: bool = False,
    classifications_allowed: Optional[List[str]] = None,
) -> PublishResult:
    """Publish ledger records into the defendable-ledger repo's /public/records tree.

    Idempotent · cursor-tracked · safe to re-run · skips records below the cursor.
    """
    repo = repo.resolve()
    if not (repo / ".git").exists():
        return PublishResult(
            ok=False, repo=str(repo), cursor_before=-1, cursor_after=-1,
            errors=[f"{repo} is not a git repo"]
        )

    allowed = set(c.upper() for c in (classifications_allowed or ["UNCLASSIFIED"]))
    cursor_before = since if since is not None else _read_cursor(repo)

    records = read_records()
    new = [r for r in records if r.ledger_seq > cursor_before]

    data_dir = _spine_data_dir()
    index = _read_index(repo)
    seen_ids = {e["record_id"] for e in index}

    copied: List[str] = []
    skipped: List[str] = []
    errors: List[str] = []
    last_seq = cursor_before

    for rec in new:
        last_seq = rec.ledger_seq

        if rec.record_type == "GENESIS":
            _mirror_ledger_line(repo, rec)
            continue

        src = _payload_source(rec, data_dir)
        if src is None:
            errors.append(f"seq {rec.ledger_seq}: payload missing on disk ({rec.payload_ref})")
            skipped.append(rec.record_id)
            continue

        try:
            payload = orjson.loads(src.read_bytes())
        except Exception as exc:
            errors.append(f"seq {rec.ledger_seq}: payload parse error: {exc}")
            skipped.append(rec.record_id)
            continue

        classification = (payload.get("classification") or "UNCLASSIFIED").upper()
        if classification not in allowed:
            skipped.append(f"{rec.record_id} (classification={classification})")
            continue

        natural_id = _natural_id(rec, payload)
        target = _target_for(rec, payload, repo)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        copied.append(str(target.relative_to(repo)))
        _mirror_ledger_line(repo, rec)

        if rec.record_id not in seen_ids:
            index.append(
                {
                    "record_id": rec.record_id,
                    "natural_id": natural_id,
                    "record_type": rec.record_type,
                    "ledger_seq": rec.ledger_seq,
                    "created_at": rec.created_at,
                    "issued_by": rec.issued_by,
                    "host": rec.host,
                    "record_sha256": rec.record_sha256,
                    "parent_hash": rec.parent_hash,
                    "payload_hash": rec.payload_hash,
                    "path": str(target.relative_to(repo / "public")),
                }
            )
            seen_ids.add(rec.record_id)

    index.sort(key=lambda e: e["ledger_seq"])
    _write_index(repo, index)
    _write_cursor(repo, last_seq)

    commit_sha: Optional[str] = None
    pushed = False
    if commit and copied:
        try:
            subprocess.run(["git", "add", "public/"], cwd=repo, check=True, capture_output=True)
            msg = (
                f"Publish {len(copied)} record(s) · ledger seq {cursor_before + 1}–{last_seq} · "
                f"{utc_now_iso()}"
            )
            subprocess.run(
                ["git", "-c", "user.name=DefendableRouter", "-c", "user.email=ops@mrdefendable.com",
                 "commit", "-m", msg],
                cwd=repo, check=True, capture_output=True,
            )
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
            ).stdout.strip()
            commit_sha = sha
            if push:
                subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=True, capture_output=True)
                pushed = True
        except subprocess.CalledProcessError as exc:
            errors.append(f"git: {exc.stderr.decode(errors='replace')[:500] if exc.stderr else str(exc)}")

    return PublishResult(
        ok=not errors,
        repo=str(repo),
        cursor_before=cursor_before,
        cursor_after=last_seq,
        new_records=len(copied),
        copied_files=copied,
        skipped=skipped,
        errors=errors,
        commit_sha=commit_sha,
        pushed=pushed,
    )
