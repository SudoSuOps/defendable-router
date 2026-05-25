from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict

from defendablerouter.schemas.verdict import RubricScores, Tier


class TrainingPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pair_type: Literal["SWARMJELLY_PAIR"] = "SWARMJELLY_PAIR"
    pair_id: str
    receipt_id: str
    verdict_id: str
    assignment_id: str

    tier: Tier
    input: str
    output: Dict[str, Any]

    rubric_scores: Optional[RubricScores] = None

    created_at: str
    pair_sha256: Optional[str] = None
