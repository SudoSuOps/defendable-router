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


def test_heartbeat_with_bad_token_fails(client):
    response = client.post("/workers/heartbeat", headers=auth_headers("bad-token"), json={"status": "online", "current_jobs": 0, "metrics": {}})
    assert response.status_code == 401


def test_worker_auth_required(client):
    response = client.post("/workers/heartbeat", json={"status": "online", "current_jobs": 0, "metrics": {}})
    assert response.status_code == 401
