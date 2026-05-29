from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkerRegisterRequest(BaseModel):
    node_id: str
    name: str
    hostname: str
    endpoint_url: str | None = None
    capabilities: dict[str, Any] = {}
    tags: list[str] = []
    version: str = "0.2.0"
    heartbeat_interval_seconds: int = Field(default=30, ge=5, le=3600)


class WorkerRegisterResponse(BaseModel):
    worker_id: str
    worker_token: str
    status: str


class WorkerHeartbeatRequest(BaseModel):
    status: str = "online"
    capabilities: dict[str, Any] | None = None
    current_jobs: int = Field(default=0, ge=0)
    metrics: dict[str, Any] = {}


class WorkerHeartbeatResponse(BaseModel):
    ok: bool
    worker_id: str
    server_time: datetime
    next_heartbeat_seconds: int


class WorkerLeaseRequest(BaseModel):
    supported_job_types: list[str]
    supported_gpu_skus: list[str]
    max_jobs: int = Field(default=1, ge=1, le=32)


class WorkerJobSummary(BaseModel):
    id: str
    job_type: str
    requested_gpu_sku: str
    estimated_hours: float
    input_dataset_ids: list[str]


class WorkerLeaseResponse(BaseModel):
    lease_id: str | None
    lease_token: str | None = None
    job: WorkerJobSummary | None
    expires_at: datetime | None = None
    message: str | None = None


class LeaseTokenRequest(BaseModel):
    lease_token: str


class WorkerStatusRequest(BaseModel):
    lease_token: str
    event_type: str
    message: str | None = None
    payload: dict[str, Any] = {}


class WorkerLogRequest(BaseModel):
    lease_token: str
    message: str
    payload: dict[str, Any] = {}


class WorkerArtifactRequest(BaseModel):
    lease_token: str
    artifact_type: str
    name: str
    uri: str
    checksum_sha256: str | None = None
    size_bytes: int | None = Field(default=None, ge=0)
    metadata: dict[str, Any] = {}


class WorkerCompleteRequest(BaseModel):
    lease_token: str
    output_uri: str | None = None
    metrics: dict[str, Any] = {}
    final_message: str | None = None


class WorkerFailRequest(BaseModel):
    lease_token: str
    error_code: str | None = None
    message: str
    payload: dict[str, Any] = {}


class WorkerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    node_id: str
    name: str
    hostname: str
    endpoint_url: str | None
    status: str
    last_heartbeat_at: datetime | None
    heartbeat_interval_seconds: int
    capabilities: dict[str, Any]
    tags: list[str]
    version: str
    created_at: datetime
    updated_at: datetime
