import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from defendable_router.core.receipts import write_receipt
from defendable_router.core.time import utc_now
from defendable_router.db.models import ComputeNode, ComputeNodeStatus, JobLease, JobLeaseStatus, JobStatusEvent, Worker, WorkerStatus
from defendable_router.schemas.workers import WorkerHeartbeatRequest, WorkerRegisterRequest


def hash_token(token: str) -> str:
    """Return a stable SHA256 hash for worker or lease bearer tokens."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_token(prefix: str) -> str:
    """Generate a plaintext token returned once to the worker."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def register_worker(db: Session, payload: WorkerRegisterRequest) -> tuple[Worker, str]:
    """Register a worker and return its plaintext token exactly once."""
    token = generate_token("dwrk")
    worker = Worker(
        id=f"worker_{uuid.uuid4().hex}",
        node_id=payload.node_id,
        name=payload.name,
        hostname=payload.hostname,
        endpoint_url=payload.endpoint_url,
        status=WorkerStatus.registered.value,
        auth_token_hash=hash_token(token),
        heartbeat_interval_seconds=payload.heartbeat_interval_seconds,
        capabilities=payload.capabilities,
        tags=payload.tags,
        version=payload.version,
    )
    db.add(worker)
    db.flush()
    write_receipt("worker_registered", worker.id, "0.00", {"node_id": worker.node_id, "hostname": worker.hostname, "version": worker.version})
    db.commit()
    db.refresh(worker)
    return worker, token


def authenticate_worker(db: Session, token: str) -> Worker | None:
    """Resolve a bearer token to a worker without storing plaintext tokens."""
    token_hash = hash_token(token)
    for worker in db.scalars(select(Worker)).all():
        if hmac.compare_digest(worker.auth_token_hash, token_hash):
            return worker
    return None


def get_linked_compute_node(db: Session, worker: Worker) -> ComputeNode | None:
    """Find a compute node by worker node_id, hostname, or stored node hostname."""
    return db.scalars(select(ComputeNode).where(or_(ComputeNode.id == worker.node_id, ComputeNode.hostname == worker.node_id, ComputeNode.hostname == worker.hostname))).first()


def update_heartbeat(db: Session, worker: Worker, payload: WorkerHeartbeatRequest) -> Worker:
    """Update worker heartbeat, status, capabilities, and linked node state."""
    now = utc_now()
    worker.last_heartbeat_at = now
    worker.updated_at = now
    worker.status = payload.status
    if payload.capabilities is not None:
        worker.capabilities = payload.capabilities
    node = get_linked_compute_node(db, worker)
    if node is not None:
        node.current_jobs = payload.current_jobs
        if payload.status == WorkerStatus.busy.value or payload.current_jobs >= node.max_concurrent_jobs:
            node.status = ComputeNodeStatus.busy.value
        elif payload.status in {WorkerStatus.online.value, WorkerStatus.registered.value}:
            node.status = ComputeNodeStatus.available.value
        elif payload.status == WorkerStatus.maintenance.value:
            node.status = ComputeNodeStatus.maintenance.value
        elif payload.status == WorkerStatus.offline.value:
            node.status = ComputeNodeStatus.offline.value
    db.commit()
    db.refresh(worker)
    return worker


def mark_stale_workers(db: Session, now: datetime | None = None) -> int:
    """Mark workers offline when heartbeat age exceeds three intervals."""
    now = now or utc_now()
    count = 0
    for worker in db.scalars(select(Worker)).all():
        if worker.status in {WorkerStatus.offline.value, WorkerStatus.banned.value} or worker.last_heartbeat_at is None:
            continue
        age = (_as_aware_utc(now) - _as_aware_utc(worker.last_heartbeat_at)).total_seconds()
        if age > worker.heartbeat_interval_seconds * 3:
            worker.status = WorkerStatus.offline.value
            worker.updated_at = now
            active_leases = db.scalars(select(JobLease).where(JobLease.worker_id == worker.id, JobLease.status == JobLeaseStatus.active.value)).all()
            for lease in active_leases:
                db.add(JobStatusEvent(id=f"event_{uuid.uuid4().hex}", job_id=lease.job_id, worker_id=worker.id, event_type="heartbeat_missed", message="worker heartbeat stale", payload={"age_seconds": age}))
            write_receipt("worker_stale", worker.id, "0.00", {"age_seconds": age, "active_leases": len(active_leases)})
            count += 1
    db.commit()
    return count
