from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SourceType = Literal["call", "space", "meeting", "api", "upload", "edge"]


class AssignmentInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    assignment_type: str
    urgency: Literal["low", "normal", "high", "urgent"] = "normal"
    expected_outputs: List[str] = Field(default_factory=list)


class RouterEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    client_id: str
    app_id: str
    agent_id: str
    source_type: SourceType
    route: str

    raw_client_language: str
    assignment: AssignmentInput

    edge_device_id: Optional[str] = None
    conversation_id: Optional[str] = None
