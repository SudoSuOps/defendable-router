from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JobCreate(BaseModel):
    member_id: str
    job_type: str
    requested_gpu_sku: str
    estimated_hours: float = Field(gt=0)
    input_dataset_ids: list[str] = []
    output_uri: str | None = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    member_id: str
    job_type: str
    requested_gpu_sku: str
    assigned_node_id: str | None
    status: str
    estimated_hours: float
    estimated_cost_usd: float
    actual_started_at: datetime | None
    actual_finished_at: datetime | None
    actual_hours: float | None
    actual_cost_usd: float | None
    input_dataset_ids: list[str]
    output_uri: str | None
    receipt_id: str | None
    created_at: datetime
