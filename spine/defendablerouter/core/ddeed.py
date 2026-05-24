from __future__ import annotations

from defendablerouter.core.ids import ddeed_stub_id
from defendablerouter.schemas.ddeed_stub import DDEEDStub


def create_ddeed_stub(receipt_id: str, assignment_id: str) -> DDEEDStub:
    return DDEEDStub(
        deed_id=ddeed_stub_id(),
        receipt_id=receipt_id,
        assignment_id=assignment_id,
    )
