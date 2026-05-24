from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class DDEEDStub(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deed_type: Literal["DDEED_ROUTER_STUB"] = "DDEED_ROUTER_STUB"
    deed_id: str
    receipt_id: str
    assignment_id: str
    deed_status: Literal["STUB_CREATED", "PENDING_TRIBUNAL", "ANCHORED", "REJECTED"] = "STUB_CREATED"
    notes: str = "DDEED eligibility pending Tribunal verdict."
