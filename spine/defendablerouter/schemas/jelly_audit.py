from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from defendablerouter.schemas.verdict import Tier

AuditStatus = Literal["AUDITED", "FAILED", "SKIPPED"]
AuditVerdict = Literal["accept", "revise", "reject"]


class JellyScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_discipline: int = Field(ge=0, le=10)
    root_cause_grounding: int = Field(ge=0, le=10)
    repair_safety: int = Field(ge=0, le=10)
    dangerous_action_awareness: int = Field(ge=0, le=10)
    verification_rigor: int = Field(ge=0, le=10)

    @property
    def mean(self) -> float:
        return (
            self.schema_discipline
            + self.root_cause_grounding
            + self.repair_safety
            + self.dangerous_action_awareness
            + self.verification_rigor
        ) / 5.0


class JellyAudit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_type: Literal["JELLY_AUDIT"] = "JELLY_AUDIT"
    audit_id: str
    verdict_id: str
    receipt_id: str
    assignment_id: str

    status: AuditStatus = "AUDITED"
    audit_verdict: Optional[AuditVerdict] = None
    scores: Optional[JellyScores] = None
    rj_tier: Optional[Tier] = None
    flagged_issues: List[str] = Field(default_factory=list)

    audited_by: str = "swarmjelly-4b"
    notes: str = ""
    raw_response: Optional[str] = None  # for forensics when status=FAILED
    created_at: str

    skip_reason: Optional[str] = None
    audit_sha256: Optional[str] = None
