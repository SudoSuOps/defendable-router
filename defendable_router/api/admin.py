from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from defendable_router.core.pricing import ANNUAL_MEMBERSHIP_PRICE_USD
from defendable_router.core.time import utc_now
from defendable_router.db.models import ComputeJob, ComputeNode, ComputeNodeStatus, Dataset, JobLease, JobLeaseStatus, JobStatus, JobStatusEvent, Member, MemberStatus, Worker, WorkerStatus
from defendable_router.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


def _as_aware_utc(value):
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@router.get("/summary")
def admin_summary(db: Session = Depends(get_db)):
    active_members = db.scalar(select(func.count()).select_from(Member).where(Member.status == MemberStatus.active.value)) or 0
    total_datasets = db.scalar(select(func.count()).select_from(Dataset)) or 0
    nodes_available = db.scalar(select(func.count()).select_from(ComputeNode).where(ComputeNode.status == ComputeNodeStatus.available.value)) or 0
    nodes_busy = db.scalar(select(func.count()).select_from(ComputeNode).where(ComputeNode.status == ComputeNodeStatus.busy.value)) or 0
    queued_jobs = db.scalar(select(func.count()).select_from(ComputeJob).where(ComputeJob.status == JobStatus.queued.value)) or 0
    running_jobs = db.scalar(select(func.count()).select_from(ComputeJob).where(ComputeJob.status == JobStatus.running.value)) or 0
    completed_jobs = db.scalar(select(func.count()).select_from(ComputeJob).where(ComputeJob.status == JobStatus.completed.value)) or 0
    estimated_revenue = db.scalar(select(func.coalesce(func.sum(ComputeJob.estimated_cost_usd), 0.0))) or 0.0
    workers_online = db.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.online.value)) or 0
    workers_offline = db.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.offline.value)) or 0
    workers_busy = db.scalar(select(func.count()).select_from(Worker).where(Worker.status == WorkerStatus.busy.value)) or 0
    active_leases = db.scalar(select(func.count()).select_from(JobLease).where(JobLease.status == JobLeaseStatus.active.value)) or 0
    expired_leases = db.scalar(select(func.count()).select_from(JobLease).where(JobLease.status == JobLeaseStatus.expired.value)) or 0
    now = utc_now()
    stale_workers = 0
    for worker in db.scalars(select(Worker)).all():
        if worker.last_heartbeat_at and worker.status not in {WorkerStatus.offline.value, WorkerStatus.banned.value}:
            if (_as_aware_utc(now) - _as_aware_utc(worker.last_heartbeat_at)).total_seconds() > worker.heartbeat_interval_seconds * 3:
                stale_workers += 1
    return {"active_members_count": active_members, "total_datasets_count": total_datasets, "compute_nodes_available": nodes_available, "compute_nodes_busy": nodes_busy, "queued_jobs": queued_jobs, "running_jobs": running_jobs, "completed_jobs": completed_jobs, "estimated_revenue_from_jobs": round(float(estimated_revenue), 2), "annual_membership_revenue": float(ANNUAL_MEMBERSHIP_PRICE_USD) * active_members, "workers_online": workers_online, "workers_offline": workers_offline, "workers_busy": workers_busy, "stale_workers": stale_workers, "active_leases": active_leases, "expired_leases": expired_leases}


@router.get("/workers")
def list_workers(db: Session = Depends(get_db)):
    workers = db.scalars(select(Worker).order_by(Worker.created_at)).all()
    return [{"id": worker.id, "status": worker.status, "node_id": worker.node_id, "hostname": worker.hostname, "last_heartbeat_at": worker.last_heartbeat_at, "capabilities_summary": {"gpu_skus": (worker.capabilities or {}).get("gpu_skus", []), "supports": (worker.capabilities or {}).get("supports", []), "max_concurrent_jobs": (worker.capabilities or {}).get("max_concurrent_jobs")}} for worker in workers]


@router.get("/workers/{worker_id}")
def worker_detail(worker_id: str, db: Session = Depends(get_db)):
    worker = db.get(Worker, worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="worker not found")
    events = db.scalars(select(JobStatusEvent).where(JobStatusEvent.worker_id == worker_id).order_by(JobStatusEvent.created_at.desc()).limit(25)).all()
    leases = db.scalars(select(JobLease).where(JobLease.worker_id == worker_id, JobLease.status == JobLeaseStatus.active.value)).all()
    return {"worker": {"id": worker.id, "node_id": worker.node_id, "name": worker.name, "hostname": worker.hostname, "endpoint_url": worker.endpoint_url, "status": worker.status, "last_heartbeat_at": worker.last_heartbeat_at, "heartbeat_interval_seconds": worker.heartbeat_interval_seconds, "capabilities": worker.capabilities, "tags": worker.tags, "version": worker.version, "created_at": worker.created_at, "updated_at": worker.updated_at}, "active_leases": [{"id": lease.id, "job_id": lease.job_id, "status": lease.status, "expires_at": lease.expires_at} for lease in leases], "recent_events": [{"id": event.id, "job_id": event.job_id, "event_type": event.event_type, "message": event.message, "payload": event.payload, "created_at": event.created_at} for event in events]}
