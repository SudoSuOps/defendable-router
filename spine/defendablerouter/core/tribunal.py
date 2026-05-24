from __future__ import annotations

from defendablerouter.core.ids import tribunal_stub_id
from defendablerouter.schemas.tribunal_stub import TribunalStub


def create_tribunal_stub(assignment_id: str) -> TribunalStub:
    return TribunalStub(
        verdict_id=tribunal_stub_id(),
        assignment_id=assignment_id,
    )
