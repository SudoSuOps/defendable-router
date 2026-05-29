import hashlib
import json
import threading
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

from defendable_router.core.config import get_settings
from defendable_router.core.time import utc_now

# Genesis parent for the receipt hash chain — mirrors the DefendableCloud per-org
# chain (64 zeros). The router keeps ONE house-wide chain (single-tenant spine).
ZERO_HASH = "0" * 64

# write_receipt reads the chain head then appends — serialize so concurrent
# writers can't claim the same seq / parent_hash. The local v0.1 spine runs a
# single uvicorn worker; the lock keeps in-process appends consistent too.
_chain_lock = threading.Lock()


def _normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: _normalize(val) for key, val in value.items()}
    return value


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(_normalize(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def checksum_receipt(payload_without_checksum: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload_without_checksum).encode("utf-8")).hexdigest()


def _ledger_files(receipts_dir: Path) -> list[Path]:
    p = Path(receipts_dir)
    if not p.exists():
        return []
    return sorted(p.glob("*.receipts.jsonl"))


def _chain_head(receipts_dir: Path) -> tuple[int, str]:
    """Return (last_seq, head_hash) for the house chain.

    The chain spans all daily ledger files in date order; the head is the last
    receipt of the newest non-empty file. Empty ledger -> (-1, ZERO_HASH) so the
    genesis receipt gets seq 0 and parent_hash = ZERO_HASH.
    """
    for f in reversed(_ledger_files(receipts_dir)):
        lines = [ln for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if lines:
            last = json.loads(lines[-1])
            return int(last.get("seq", -1)), str(last.get("checksum_sha256", ZERO_HASH))
    return -1, ZERO_HASH


def write_receipt(
    receipt_type: str,
    member_id: str,
    amount_usd: Decimal | float | str,
    metadata: dict[str, Any] | None = None,
    job_id: str | None = None,
    dataset_ids: list[str] | None = None,
) -> dict[str, Any]:
    with _chain_lock:
        receipts_dir = Path(get_settings().receipts_dir)
        receipts_dir.mkdir(parents=True, exist_ok=True)
        last_seq, parent_hash = _chain_head(receipts_dir)

        created_at = utc_now()
        receipt = {
            "receipt_id": f"rcpt_{uuid.uuid4().hex}",
            "receipt_type": receipt_type,
            "member_id": member_id,
            "job_id": job_id,
            "dataset_ids": dataset_ids or [],
            "amount_usd": Decimal(str(amount_usd)).quantize(Decimal("0.01")),
            "metadata": metadata or {},
            # chain coordinates — hashed into checksum_sha256 below, so the link
            # is tamper-evident (mirrors the Cloud's org_seq / parent_hash).
            "seq": last_seq + 1,
            "parent_hash": parent_hash,
            "created_at": created_at,
        }
        receipt["checksum_sha256"] = checksum_receipt(receipt)

        receipt_path = receipts_dir / f"{created_at.date().isoformat()}.receipts.jsonl"
        with receipt_path.open("a", encoding="utf-8") as fh:
            fh.write(canonical_json(receipt) + "\n")
        return _normalize(receipt)


def read_chain(receipts_dir: Path) -> list[dict[str, Any]]:
    """All receipts across the ledger, ordered by chain seq."""
    out: list[dict[str, Any]] = []
    for f in _ledger_files(receipts_dir):
        for ln in f.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    out.sort(key=lambda r: r.get("seq", 0))
    return out


def verify_ledger(receipts_dir: Path) -> dict[str, Any]:
    """Recompute and validate the house receipt hash chain.

    Mirrors DefendableCloud /ledger/verify: per receipt, recompute checksum_sha256
    over the canonical body, confirm seq runs 0,1,2,... with no gaps, and confirm
    each parent_hash links to the prior receipt's checksum_sha256 (genesis = ZERO_HASH).
    """
    chain = read_chain(receipts_dir)
    errors: list[dict[str, Any]] = []
    prev = ZERO_HASH
    for i, r in enumerate(chain):
        body = {k: v for k, v in r.items() if k != "checksum_sha256"}
        if checksum_receipt(body) != r.get("checksum_sha256"):
            errors.append({"seq": r.get("seq"), "receipt_id": r.get("receipt_id"), "error": "checksum mismatch"})
        if r.get("seq") != i:
            errors.append({"seq": r.get("seq"), "receipt_id": r.get("receipt_id"), "error": f"sequence gap (expected {i})"})
        if r.get("parent_hash") != prev:
            errors.append({"seq": r.get("seq"), "receipt_id": r.get("receipt_id"), "error": "broken parent link"})
        prev = r.get("checksum_sha256")
    return {"ok": len(errors) == 0, "receipts_checked": len(chain), "errors": errors[:20]}
