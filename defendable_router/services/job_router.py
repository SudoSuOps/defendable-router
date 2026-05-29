import uuid
from datetime import UTC
from sqlalchemy.orm import Session
from defendable_router.core.pricing import GPU_PRICING
from defendable_router.core.receipts import write_receipt
from defendable_router.core.time import utc_now
from defendable_router.db.models import ComputeJob, JobStatus, JobType
from defendable_router.schemas.jobs import JobCreate
from defendable_router.services.billing import actual_compute_cost, quote_compute
from defendable_router.services.compute_inventory import assign_available_node, release_node_capacity
from defendable_router.services.datasets import get_dataset


def validate_job_request(db: Session, payload: JobCreate) -> None:
    """Validate GPU SKU, job type, and dataset references before routing."""
    if payload.requested_gpu_sku not in GPU_PRICING:
        raise ValueError("unsupported GPU SKU")
    if payload.job_type not in {item.value for item in JobType}:
        raise ValueError("unsupported job type")
    missing = [dataset_id for dataset_id in payload.input_dataset_ids if get_dataset(db, dataset_id) is None]
    if missing:
        raise ValueError(f"unknown dataset ids: {', '.join(missing)}")


def create_job(db: Session, payload: JobCreate) -> ComputeJob:
    """Create a compute job, assign available capacity, and emit a job receipt."""
    validate_job_request(db, payload)
    _, estimated_cost = quote_compute(payload.requested_gpu_sku, payload.estimated_hours)
    node = assign_available_node(db, payload.requested_gpu_sku)
    status = JobStatus.running.value if node else JobStatus.queued.value
    job = ComputeJob(id=f"job_{uuid.uuid4().hex}", member_id=payload.member_id, job_type=payload.job_type, requested_gpu_sku=payload.requested_gpu_sku, assigned_node_id=node.id if node else None, status=status, estimated_hours=payload.estimated_hours, estimated_cost_usd=float(estimated_cost), input_dataset_ids=payload.input_dataset_ids, output_uri=payload.output_uri)
    db.add(job)
    db.flush()
    receipt_type = "fine_tune_job" if payload.job_type == JobType.fine_tune.value else "compute_job"
    receipt = write_receipt(receipt_type, payload.member_id, estimated_cost, {"phase": "created", "status": status, "gpu_sku": payload.requested_gpu_sku}, job_id=job.id, dataset_ids=payload.input_dataset_ids)
    job.receipt_id = receipt["receipt_id"]
    db.commit()
    db.refresh(job)
    return job


def start_job(db: Session, job: ComputeJob) -> ComputeJob:
    """Mark a job running and reserve node capacity when queued capacity exists."""
    if job.status == JobStatus.queued.value:
        node = assign_available_node(db, job.requested_gpu_sku)
        if node is not None:
            job.assigned_node_id = node.id
    job.status = JobStatus.running.value
    job.actual_started_at = job.actual_started_at or utc_now()
    db.commit()
    db.refresh(job)
    return job


def _as_aware_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def complete_job(db: Session, job: ComputeJob) -> ComputeJob:
    """Mark a job complete, calculate actual cost, release capacity, and receipt it."""
    finished = utc_now()
    job.actual_finished_at = finished
    if job.actual_started_at is None:
        job.actual_started_at = job.created_at
    elapsed_seconds = max((_as_aware_utc(job.actual_finished_at) - _as_aware_utc(job.actual_started_at)).total_seconds(), 1)
    job.actual_hours = round(elapsed_seconds / 3600, 6)
    actual_cost = actual_compute_cost(job.requested_gpu_sku, job.actual_hours)
    job.actual_cost_usd = float(actual_cost)
    job.status = JobStatus.completed.value
    release_node_capacity(db, job.assigned_node_id)
    receipt_type = "fine_tune_job" if job.job_type == JobType.fine_tune.value else "compute_job"
    receipt = write_receipt(receipt_type, job.member_id, actual_cost, {"phase": "completed", "actual_hours": job.actual_hours, "gpu_sku": job.requested_gpu_sku}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    job.receipt_id = receipt["receipt_id"]
    db.commit()
    db.refresh(job)
    return job


def cancel_job(db: Session, job: ComputeJob) -> ComputeJob:
    """Cancel a job and release capacity if the job was already running."""
    if job.status == JobStatus.running.value:
        release_node_capacity(db, job.assigned_node_id)
    job.status = JobStatus.canceled.value
    db.commit()
    db.refresh(job)
    return job
