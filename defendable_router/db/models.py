from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from defendable_router.core.time import utc_now


class Base(DeclarativeBase):
    pass


class MemberStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"
    banned = "banned"


class QualityTier(str, Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"
    royal_jelly = "royal_jelly"


class ComputeNodeStatus(str, Enum):
    available = "available"
    busy = "busy"
    offline = "offline"
    maintenance = "maintenance"


class JobType(str, Enum):
    inference = "inference"
    fine_tune = "fine_tune"
    eval = "eval"
    dataset_build = "dataset_build"
    embedding = "embedding"
    batch = "batch"


class JobStatus(str, Enum):
    queued = "queued"
    leased = "leased"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class WorkerStatus(str, Enum):
    registered = "registered"
    online = "online"
    offline = "offline"
    busy = "busy"
    draining = "draining"
    maintenance = "maintenance"
    banned = "banned"


class JobLeaseStatus(str, Enum):
    active = "active"
    released = "released"
    expired = "expired"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class JobStatusEventType(str, Enum):
    leased = "leased"
    accepted = "accepted"
    started = "started"
    progress = "progress"
    log = "log"
    artifact = "artifact"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"
    heartbeat_missed = "heartbeat_missed"
    lease_expired = "lease_expired"


class ArtifactType(str, Enum):
    log = "log"
    model = "model"
    dataset = "dataset"
    report = "report"
    receipt = "receipt"
    metrics = "metrics"
    checkpoint = "checkpoint"
    other = "other"


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default=MemberStatus.inactive.value, index=True)
    annual_fee_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    membership_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    membership_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, index=True)
    domain: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(Text)
    object_uri: Mapped[str] = mapped_column(String)
    license_type: Mapped[str] = mapped_column(String)
    quality_tier: Mapped[str] = mapped_column(String, index=True)
    checksum_sha256: Mapped[str] = mapped_column(String)
    size_bytes: Mapped[int] = mapped_column(Integer)
    row_count: Mapped[int] = mapped_column(Integer)
    is_member_access: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ComputeNode(Base):
    __tablename__ = "compute_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    hostname: Mapped[str] = mapped_column(String, unique=True, index=True)
    gpu_type: Mapped[str] = mapped_column(String, index=True)
    gpu_name: Mapped[str] = mapped_column(String)
    vram_gb: Mapped[int] = mapped_column(Integer)
    hourly_rate_usd: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default=ComputeNodeStatus.available.value, index=True)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=1)
    current_jobs: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class ComputeJob(Base):
    __tablename__ = "compute_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    member_id: Mapped[str] = mapped_column(String, index=True)
    job_type: Mapped[str] = mapped_column(String, index=True)
    requested_gpu_sku: Mapped[str] = mapped_column(String, index=True)
    assigned_node_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, default=JobStatus.queued.value, index=True)
    estimated_hours: Mapped[float] = mapped_column(Float)
    estimated_cost_usd: Mapped[float] = mapped_column(Float)
    actual_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_dataset_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    receipt_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    node_id: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    hostname: Mapped[str] = mapped_column(String, index=True)
    endpoint_url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default=WorkerStatus.registered.value, index=True)
    auth_token_hash: Mapped[str] = mapped_column(String, index=True)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    heartbeat_interval_seconds: Mapped[int] = mapped_column(Integer, default=30)
    capabilities: Mapped[dict] = mapped_column(JSON, default=dict)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    version: Mapped[str] = mapped_column(String, default="0.2.0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class JobLease(Base):
    __tablename__ = "job_leases"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(String, index=True)
    worker_id: Mapped[str] = mapped_column(String, index=True)
    lease_token_hash: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default=JobLeaseStatus.active.value, index=True)
    leased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class JobStatusEvent(Base):
    __tablename__ = "job_status_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(String, index=True)
    worker_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(String, index=True)
    worker_id: Mapped[str] = mapped_column(String, index=True)
    artifact_type: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String)
    uri: Mapped[str] = mapped_column(String)
    checksum_sha256: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
