from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    id: str | None = None
    title: str
    domain: str
    description: str
    object_uri: str
    license_type: str
    quality_tier: str
    checksum_sha256: str = Field(min_length=64, max_length=64)
    size_bytes: int = Field(ge=0)
    row_count: int = Field(ge=0)
    is_member_access: bool = True


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    domain: str
    description: str
    object_uri: str
    license_type: str
    quality_tier: str
    checksum_sha256: str
    size_bytes: int
    row_count: int
    is_member_access: bool
    created_at: datetime


class DatasetAccessRequest(BaseModel):
    member_id: str


class DatasetAccessResponse(BaseModel):
    access_granted: bool
    dataset_id: str
    member_id: str
    receipt_id: str
    object_uri: str
