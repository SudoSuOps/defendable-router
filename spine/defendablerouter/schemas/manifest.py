from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field


class ManifestFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    sha256: str
    bytes: int
    type: str


class Manifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_type: Literal["DEFENDABLE_ROUTER_MANIFEST"] = "DEFENDABLE_ROUTER_MANIFEST"
    manifest_id: str
    created_at: str
    assignment_id: str
    receipt_id: str
    files: List[ManifestFile] = Field(default_factory=list)
    manifest_sha256: str = ""
