from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

RecordType = Literal[
    "GENESIS",
    "RECEIPT",
    "VERDICT",
    "PAIR",
    "DEED",
]


class LedgerRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ledger_seq: int
    record_id: str
    record_type: RecordType
    created_at: str
    parent_hash: str
    payload_ref: str
    payload_hash: str
    issued_by: str
    host: str
    record_sha256: Optional[str] = None
