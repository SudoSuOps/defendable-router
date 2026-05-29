from datetime import timedelta

from defendable_router.core.time import utc_now
from defendable_router.db.models import Artifact, ComputeJob, JobLease, JobStatusEvent, Worker
from defendable_router.services.leases import expire_stale_leases
from defendable_router.services.workers import hash_token


def register_worker(client, capabilities=None):
    response = client.post("/workers/register", json={
        "node_id": "node_5090",
        "name": "Smash 5090 Worker",
        "hostname": "smash-5090-01",
        "endpoint_url": None,
        "capabilities": capabilities or {
            "gpu_skus": ["rog_astral_5090_32gb"],
            "gpu_count": 1,
            "vram_gb_total": 32,
            "cuda_version": "13.1",
            "driver_version": "590.48.01",
            "supports": ["inference", "fine_tune", "eval"],
            "max_concurrent_jobs": 1,
            "runtime": {"ollama": True, "docker": True}
        },
        "tags": ["rtx5090", "owned-rig"],
        "version": "0.2.0"
    })
    assert response.status_code == 200
    return response.json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_queued_job(client, gpu="rog_astral_5090_32gb", job_type="fine_tune"):
    with client.app.state.testing_session_local() as db:
        job = ComputeJob(
            id=f"job_test_{gpu}_{job_type}",
            member_id="mem_active",
            job_type=job_type,
            requested_gpu_sku=gpu,
            status="queued",
            estimated_hours=2.0,
            estimated_cost_usd=4.0 if gpu == "rog_astral_5090_32gb" else 10.0,
            input_dataset_ids=["ds_gold"],
        )
        db.add(job)
        db.commit()
        return job.id


def test_status_event_writes_job_status_event(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    response = client.post(f"/workers/jobs/{job_id}/status", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"], "event_type": "progress", "message": "epoch 1", "payload": {"progress_pct": 20}})
    assert response.status_code == 200
    with client.app.state.testing_session_local() as db:
        event = db.get(JobStatusEvent, response.json()["event_id"])
        assert event.event_type == "progress"
        assert event.payload["progress_pct"] == 20


def test_artifact_report_creates_artifact(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    response = client.post(f"/workers/jobs/{job_id}/artifacts", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"], "artifact_type": "model", "name": "atlas-cre-lora-v1", "uri": "s3://defendable-artifacts/jobs/job/output", "checksum_sha256": "b" * 64, "size_bytes": 123456, "metadata": {}})
    assert response.status_code == 200
    with client.app.state.testing_session_local() as db:
        artifact = db.get(Artifact, response.json()["artifact_id"])
        assert artifact is not None
        assert artifact.artifact_type == "model"
