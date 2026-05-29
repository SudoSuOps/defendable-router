import hashlib
import json
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

from defendable_router.core.config import get_settings
from defendable_router.core.time import utc_now


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


def write_receipt(
    receipt_type: str,
    member_id: str,
    amount_usd: Decimal | float | str,
    metadata: dict[str, Any] | None = None,
    job_id: str | None = None,
    dataset_ids: list[str] | None = None,
) -> dict[str, Any]:
    created_at = utc_now()
    receipt = {
        "receipt_id": f"rcpt_{uuid.uuid4().hex}",
        "receipt_type": receipt_type,
        "member_id": member_id,
        "job_id": job_id,
        "dataset_ids": dataset_ids or [],
        "amount_usd": Decimal(str(amount_usd)).quantize(Decimal("0.01")),
        "metadata": metadata or {},
        "created_at": created_at,
    }
    receipt["checksum_sha256"] = checksum_receipt(receipt)
    receipts_dir = Path(get_settings().receipts_dir)
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipts_dir / f"{created_at.date().isoformat()}.receipts.jsonl"
    with receipt_path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_json(receipt) + "\n")
    return _normalize(receipt)
