from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from defendable_router.core.security import require_worker
from defendable_router.core.time import utc_now
from defendable_router.db.models import Worker
from defendable_router.db.session import get_db
from defendable_router.schemas.jobs import JobRead
from defendable_router.schemas.workers import (
    LeaseTokenRequest,
    WorkerArtifactRequest,
    WorkerCompleteRequest,
    WorkerFailRequest,
    WorkerHeartbeatRequest,
    WorkerHeartbeatResponse,
    WorkerLeaseRequest,
    WorkerLeaseResponse,
    WorkerLogRequest,
    WorkerRegisterRequest,
    WorkerRegisterResponse,
    WorkerStatusRequest,
    WorkerJobSummary,
)
from defendable_router.services.artifacts import create_artifact
from defendable_router.services.leases import accept_job, complete_worker_job, fail_worker_job, lease_next_job, record_worker_status
from defendable_router.services.workers import register_worker, update_heartbeat

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerRegisterResponse)
def register_worker_endpoint(payload: WorkerRegisterRequest, db: Session = Depends(get_db)):
    worker, token = register_worker(db, payload)
    return WorkerRegisterResponse(worker_id=worker.id, worker_token=token, status=worker.status)


@router.post("/heartbeat", response_model=WorkerHeartbeatResponse)
def heartbeat(payload: WorkerHeartbeatRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    worker = update_heartbeat(db, worker, payload)
    return WorkerHeartbeatResponse(ok=True, worker_id=worker.id, server_time=utc_now(), next_heartbeat_seconds=worker.heartbeat_interval_seconds)


@router.post("/jobs/lease", response_model=WorkerLeaseResponse)
def lease_job(payload: WorkerLeaseRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    lease, token, job = lease_next_job(db, worker, payload.supported_job_types, payload.supported_gpu_skus, payload.max_jobs)
    if lease is None or job is None:
        return WorkerLeaseResponse(lease_id=None, job=None, message="no_matching_jobs")
    return WorkerLeaseResponse(
        lease_id=lease.id,
        lease_token=token,
        job=WorkerJobSummary(id=job.id, job_type=job.job_type, requested_gpu_sku=job.requested_gpu_sku, estimated_hours=job.estimated_hours, input_dataset_ids=job.input_dataset_ids),
        expires_at=lease.expires_at,
    )


@router.post("/jobs/{job_id}/accept", response_model=JobRead)
def accept(job_id: str, payload: LeaseTokenRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        return accept_job(db, worker, job_id, payload.lease_token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/status")
def status(job_id: str, payload: WorkerStatusRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        event = record_worker_status(db, worker, job_id, payload.lease_token, payload.event_type, payload.message, payload.payload)
        return {"ok": True, "event_id": event.id, "event_type": event.event_type}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/logs")
def logs(job_id: str, payload: WorkerLogRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        event = record_worker_status(db, worker, job_id, payload.lease_token, "log", payload.message, payload.payload)
        return {"ok": True, "event_id": event.id}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/artifacts")
def artifacts(job_id: str, payload: WorkerArtifactRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        artifact = create_artifact(db, worker, job_id, payload.lease_token, payload.artifact_type, payload.name, payload.uri, payload.checksum_sha256, payload.size_bytes, payload.metadata)
        return {"ok": True, "artifact_id": artifact.id, "uri": artifact.uri}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/complete", response_model=JobRead)
def complete(job_id: str, payload: WorkerCompleteRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        return complete_worker_job(db, worker, job_id, payload.lease_token, payload.output_uri, payload.metrics, payload.final_message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/{job_id}/fail", response_model=JobRead)
def fail(job_id: str, payload: WorkerFailRequest, worker: Worker = Depends(require_worker), db: Session = Depends(get_db)):
    try:
        return fail_worker_job(db, worker, job_id, payload.lease_token, payload.error_code, payload.message, payload.payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
