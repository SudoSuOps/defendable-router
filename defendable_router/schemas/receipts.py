from datetime import datetime
from pydantic import BaseModel


class ReceiptRead(BaseModel):
    receipt_id: str
    receipt_type: str
    member_id: str
    job_id: str | None = None
    dataset_ids: list[str] = []
    amount_usd: str
    metadata: dict
    checksum_sha256: str
    created_at: datetime | str
