from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class TribunalStub(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict_type: Literal["TRIBUNAL_STUB"] = "TRIBUNAL_STUB"
    verdict_id: str
    assignment_id: str
    classification: Literal["UNCLASSIFIED", "INTERNAL", "PRIVILEGED", "RESTRICTED"] = "UNCLASSIFIED"
    assignment_success: Optional[bool] = None
    notes: str = "Tribunal not yet run. Stub created by DefendableRouter."
