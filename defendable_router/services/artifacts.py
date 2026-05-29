import uuid

from sqlalchemy.orm import Session

from defendable_router.core.receipts import write_receipt
from defendable_router.db.models import Artifact, ComputeJob, Worker
from defendable_router.services.leases import create_status_event, verify_active_lease


def create_artifact(db: Session, worker: Worker, job_id: str, lease_token: str, artifact_type: str, name: str, uri: str, checksum_sha256: str | None, size_bytes: int | None, metadata: dict | None) -> Artifact:
    """Create an artifact record and companion status event for a leased job."""
    verify_active_lease(db, worker, job_id, lease_token)
    artifact = Artifact(id=f"artifact_{uuid.uuid4().hex}", job_id=job_id, worker_id=worker.id, artifact_type=artifact_type, name=name, uri=uri, checksum_sha256=checksum_sha256, size_bytes=size_bytes, metadata_json=metadata or {})
    db.add(artifact)
    create_status_event(db, job_id, worker.id, "artifact", f"artifact reported: {name}", {"artifact_id": artifact.id, "artifact_type": artifact_type, "uri": uri})
    job = db.get(ComputeJob, job_id)
    if job is not None:
        write_receipt("artifact_reported", job.member_id, "0.00", {"worker_id": worker.id, "artifact_id": artifact.id, "artifact_type": artifact_type, "uri": uri}, job_id=job.id, dataset_ids=job.input_dataset_ids)
    db.commit()
    db.refresh(artifact)
    return artifact
