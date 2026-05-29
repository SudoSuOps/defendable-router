from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ComputeNodeCreate(BaseModel):
    id: str | None = None
    hostname: str
    gpu_type: str
    max_concurrent_jobs: int = Field(default=1, ge=1)
    tags: list[str] = []


class ComputeNodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    hostname: str
    gpu_type: str
    gpu_name: str
    vram_gb: int
    hourly_rate_usd: float
    status: str
    max_concurrent_jobs: int
    current_jobs: int
    tags: list[str]
    created_at: datetime


class ComputeQuoteRequest(BaseModel):
    member_id: str
    requested_gpu_sku: str
    estimated_hours: float = Field(gt=0)
    job_type: str


class ComputeQuoteResponse(BaseModel):
    member_id: str
    requested_gpu_sku: str
    gpu_display_name: str
    hourly_rate_usd: float
    estimated_hours: float
    estimated_cost_usd: float
    job_type: str
    receipt_id: str
