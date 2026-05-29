from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from defendable_router.core.security import require_active_member
from defendable_router.db.models import ComputeJob
from defendable_router.db.session import get_db
from defendable_router.schemas.jobs import JobCreate, JobRead
from defendable_router.services.job_router import cancel_job, complete_job, create_job, start_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job_or_404(db: Session, job_id: str) -> ComputeJob:
    job = db.get(ComputeJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.post("", response_model=JobRead)
def create_job_endpoint(payload: JobCreate, db: Session = Depends(get_db)):
    require_active_member(db, payload.member_id)
    try:
        return create_job(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=JobRead)
def read_job(job_id: str, db: Session = Depends(get_db)):
    return _get_job_or_404(db, job_id)


@router.post("/{job_id}/start", response_model=JobRead)
def start_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    return start_job(db, _get_job_or_404(db, job_id))


@router.post("/{job_id}/complete", response_model=JobRead)
def complete_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    return complete_job(db, _get_job_or_404(db, job_id))


@router.post("/{job_id}/cancel", response_model=JobRead)
def cancel_job_endpoint(job_id: str, db: Session = Depends(get_db)):
    return cancel_job(db, _get_job_or_404(db, job_id))
