from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Tier = Literal["apex", "honey", "jelly", "pollen", "propolis"]
VerdictStatus = Literal["GRADED", "FAILED", "SKIPPED"]
Severity = Literal["info", "warn", "critical"]


class RubricScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accuracy: float = Field(ge=0.0, le=5.0)
    cre_judgment: float = Field(ge=0.0, le=5.0)
    format: float = Field(ge=0.0, le=5.0)
    score: float = Field(ge=0.0, le=5.0)

    @property
    def mean(self) -> float:
        return (self.accuracy + self.cre_judgment + self.format + self.score) / 4.0


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict_type: Literal["TRIBUNAL_VERDICT"] = "TRIBUNAL_VERDICT"
    verdict_id: str
    receipt_id: str
    assignment_id: str

    status: VerdictStatus = "GRADED"
    rubric_scores: Optional[RubricScores] = None
    tier: Optional[Tier] = None
    assignment_success: Optional[bool] = None

    graded_by: str = "swarmcurator-9b"
    notes: str = ""
    created_at: str

    flag_reasons: List[str] = Field(default_factory=list)
    flag_severity: Severity = "info"

    vocab_density: Optional[float] = None
    vocab_terms_seen: List[str] = Field(default_factory=list)

    skip_reason: Optional[str] = None
    verdict_sha256: Optional[str] = None
