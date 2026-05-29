import hmac
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from defendable_router.core.receipts import write_receipt
from defendable_router.core.time import utc_now
from defendable_router.db.models import ComputeJob, JobLease, JobLeaseStatus, JobStatus, JobStatusEvent, JobType, Worker, WorkerStatus
from defendable_router.services.billing import actual_compute_cost
from defendable_router.services.compute_inventory import release_node_capacity
from defendable_router.services.workers import generate_token, get_linked_compute_node, hash_token

FINAL_JOB_STATUSES = {JobStatus.completed.value, JobStatus.failed.value, JobStatus.canceled.value}
DEFAULT_LEASE_SECONDS = 600


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def create_status_event(db: Session, job_id: str, worker_id: str, event_type: str, message: str | None = None, payload: dict | None = None) -> JobStatusEvent:
    """Persist a worker job status event."""
    event = JobStatusEvent(id=f"event_{uuid.uuid4().hex}", job_id=job_id, worker_id=worker_id, event_type=event_type, message=message, payload=payload or {})
    db.add(event)
    return event


def verify_active_lease(db: Session, worker: Worker, job_id: str, lease_token: str) -> JobLease:
    """Verify lease token ownership and active lease status for a job."""
    lease = db.scalars(select(JobLease).where(JobLease.job_id == job_id, JobLease.worker_id == worker.id, JobLease.status == JobLeaseStatus.active.value)).first()
    if lease is None:
        raise ValueError("active lease not found")
    if not hmac.compare_digest(lease.lease_token_hash, hash_token(lease_token)):
        raise ValueError("invalid lease token")
    if _as_aware_utc(lease.expires_at) <= utc_now():
        lease.status = JobLeaseStatus.expired.value
        raise ValueError("lease expired")
    return lease


def lease_next_job(db: Session, worker: Worker, supported_job_types: list[str], supported_gpu_skus: list[str], max_jobs: int = 1) -> tuple[JobLease | None, str | None, ComputeJob | None]:
    """Lease the next queued job matching worker job type and GPU capability."""
    existing = db.scalars(select(JobLease).where(JobLease.worker_id == worker.id, JobLease.status == JobLeaseStatus.active.value)).all()
    if len(existing) >= max_jobs:
        return None, None, None
    worker_gpu_skus = set((worker.capabilities or {}).get("gpu_skus", [])) or set(supported_gpu_skus)
    gpu_skus = list(worker_gpu_skus.intersection(set(supported_gpu_skus)))
    job_types = list(set(supported_job_types).intersection({item.value for item in JobType}))
    if not gpu_skus or not job_types:
        return None, None, None
    job = db.scalars(select(ComputeJob).where(ComputeJob.status == JobStatus.queued.value, ComputeJob.requested_gpu_sku.in_(gpu_skus), ComputeJob.job_type.in_(job_types)).order_by(ComputeJob.created_at)).first()
    if job is None:
        return None, None, None
    token = generate_token("dlease")
    now = utc_now()
    lease = JobLease(id=f"lease_{uuid.uuid4().hex}", job_id=job.id, worker_id=worker.id, lease_token_hash=hash_token(token), status=JobLeaseStatus.active.value, leased_at=now, expires_at=now + timedelta(seconds=DEFAULT_LEASE_SECONDS))
    node = get_linked_compute_node(db, worker)
    if node is not None:
        job.assigned_node_id = node.id
    job.status = JobStatus.leased.value
    worker.status = WorkerStatus.busy.value
    worker.updated_at = now
    db.add(lease)
    create_status_event(db, job.id, worker.id, "leased", "job leased to worker", {"expires_at": lease.expires_at.isoformat()})
    receipt_type = "fine_tune_job" if job.job_type == JobType.fine_tune.value else "compute_job"
    write_receipt("job_leased", job.member_id, "0.00", {"worker_id": worker.id, "lease_id": lease.id, "gpu_sku": job.requested_gpu_sku}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    write_receipt(receipt_type, job.member_id, job.estimated_cost_usd, {"phase": "leased", "worker_id": worker.id}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    db.commit()
    db.refresh(lease)
    db.refresh(job)
    return lease, token, job


def accept_job(db: Session, worker: Worker, job_id: str, lease_token: str) -> ComputeJob:
    """Accept an active lease and mark the job running."""
    verify_active_lease(db, worker, job_id, lease_token)
    job = db.get(ComputeJob, job_id)
    if job is None:
        raise ValueError("job not found")
    job.status = JobStatus.running.value
    job.actual_started_at = job.actual_started_at or utc_now()
    create_status_event(db, job.id, worker.id, "accepted", "worker accepted job", {})
    create_status_event(db, job.id, worker.id, "started", "worker started job", {})
    write_receipt("worker_job_accepted", job.member_id, "0.00", {"worker_id": worker.id}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    db.commit()
    db.refresh(job)
    return job


def record_worker_status(db: Session, worker: Worker, job_id: str, lease_token: str, event_type: str, message: str | None, payload: dict | None) -> JobStatusEvent:
    """Record a non-final worker status event for a leased job."""
    verify_active_lease(db, worker, job_id, lease_token)
    event = create_status_event(db, job_id, worker.id, event_type, message, payload)
    db.commit()
    db.refresh(event)
    return event


def complete_worker_job(db: Session, worker: Worker, job_id: str, lease_token: str, output_uri: str | None, metrics: dict, final_message: str | None) -> ComputeJob:
    """Complete a leased job, calculate final cost, complete lease, and receipt it."""
    lease = verify_active_lease(db, worker, job_id, lease_token)
    job = db.get(ComputeJob, job_id)
    if job is None:
        raise ValueError("job not found")
    finished = utc_now()
    job.actual_finished_at = finished
    if job.actual_started_at is None:
        job.actual_started_at = lease.leased_at
    elapsed_seconds = max((_as_aware_utc(job.actual_finished_at) - _as_aware_utc(job.actual_started_at)).total_seconds(), 1)
    if metrics and metrics.get("duration_seconds"):
        elapsed_seconds = max(float(metrics["duration_seconds"]), 1)
    job.actual_hours = round(elapsed_seconds / 3600, 6)
    job.actual_cost_usd = float(actual_compute_cost(job.requested_gpu_sku, job.actual_hours))
    job.output_uri = output_uri or job.output_uri
    job.status = JobStatus.completed.value
    lease.status = JobLeaseStatus.completed.value
    lease.released_at = finished
    worker.status = WorkerStatus.online.value
    worker.updated_at = finished
    release_node_capacity(db, job.assigned_node_id)
    create_status_event(db, job.id, worker.id, "completed", final_message or "job completed", {"metrics": metrics, "output_uri": job.output_uri})
    receipt_type = "fine_tune_job" if job.job_type == JobType.fine_tune.value else "compute_job"
    receipt = write_receipt(receipt_type, job.member_id, job.actual_cost_usd, {"phase": "completed", "worker_id": worker.id, "actual_hours": job.actual_hours, "metrics": metrics}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    write_receipt("worker_job_completed", job.member_id, job.actual_cost_usd, {"worker_id": worker.id, "lease_id": lease.id}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    job.receipt_id = receipt["receipt_id"]
    db.commit()
    db.refresh(job)
    return job


def fail_worker_job(db: Session, worker: Worker, job_id: str, lease_token: str, error_code: str | None, message: str, payload: dict | None) -> ComputeJob:
    """Fail a leased job without applying final compute charge in v0.2."""
    lease = verify_active_lease(db, worker, job_id, lease_token)
    job = db.get(ComputeJob, job_id)
    if job is None:
        raise ValueError("job not found")
    now = utc_now()
    job.status = JobStatus.failed.value
    job.actual_finished_at = now
    lease.status = JobLeaseStatus.failed.value
    lease.released_at = now
    worker.status = WorkerStatus.online.value
    worker.updated_at = now
    release_node_capacity(db, job.assigned_node_id)
    event_payload = payload or {}
    if error_code:
        event_payload["error_code"] = error_code
    create_status_event(db, job.id, worker.id, "failed", message, event_payload)
    write_receipt("worker_job_failed", job.member_id, "0.00", {"worker_id": worker.id, "lease_id": lease.id, "error_code": error_code, "message": message}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    db.commit()
    db.refresh(job)
    return job


def expire_stale_leases(db: Session, now: datetime | None = None) -> int:
    """Expire active leases past expires_at and return non-final jobs to queued."""
    now = now or utc_now()
    count = 0
    leases = db.scalars(select(JobLease).where(JobLease.status == JobLeaseStatus.active.value)).all()
    for lease in leases:
        if _as_aware_utc(lease.expires_at) > _as_aware_utc(now):
            continue
        lease.status = JobLeaseStatus.expired.value
        lease.released_at = now
        job = db.get(ComputeJob, lease.job_id)
        if job is not None and job.status not in FINAL_JOB_STATUSES:
            job.status = JobStatus.queued.value
            job.assigned_node_id = None
        create_status_event(db, lease.job_id, lease.worker_id, "lease_expired", "lease expired and job returned to queue", {})
        member_id = job.member_id if job is not None else lease.worker_id
        write_receipt("lease_expired", member_id, "0.00", {"worker_id": lease.worker_id, "lease_id": lease.id}, job_id=lease.job_id)
        count += 1
    db.commit()
    return count
