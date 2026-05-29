from fastapi import APIRouter, Depends

from defendable_router.core.config import get_settings
from defendable_router.core.receipts import read_chain, verify_ledger
from defendable_router.core.security import require_read_token

router = APIRouter(prefix="/receipts", tags=["receipts"], dependencies=[Depends(require_read_token)])


@router.get("")
def list_receipts(limit: int = 200):
    """The house receipt hash chain, in seq order — coordinates only."""
    chain = read_chain(get_settings().receipts_dir)
    coords = [
        {
            "receipt_id": r.get("receipt_id"),
            "seq": r.get("seq"),
            "receipt_type": r.get("receipt_type"),
            "member_id": r.get("member_id"),
            "amount_usd": r.get("amount_usd"),
            "parent_hash": r.get("parent_hash"),
            "checksum_sha256": r.get("checksum_sha256"),
            "created_at": r.get("created_at"),
        }
        for r in chain
    ]
    return {"count": len(coords), "receipts": coords[-max(limit, 0):] if limit else coords}


@router.get("/verify")
def verify_receipts():
    """Recompute every checksum and validate chain integrity (seq + parent links)."""
    return verify_ledger(get_settings().receipts_dir)
