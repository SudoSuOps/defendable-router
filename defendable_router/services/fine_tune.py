from sqlalchemy.orm import Session
from defendable_router.schemas.jobs import JobCreate
from defendable_router.services.job_router import create_job


def create_fine_tune_job(db: Session, payload: JobCreate):
    """Normalize a request to the fine_tune job type and route it as compute."""
    normalized = payload.model_copy(update={"job_type": "fine_tune"})
    return create_job(db, normalized)
