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


def test_worker_can_lease_matching_queued_job(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    response = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={
        "supported_job_types": ["fine_tune", "inference"],
        "supported_gpu_skus": ["rog_astral_5090_32gb"],
        "max_jobs": 1
    })
    assert response.status_code == 200
    body = response.json()
    assert body["lease_id"].startswith("lease_")
    assert body["lease_token"].startswith("dlease_")
    assert body["job"]["id"] == job_id


def test_worker_cannot_lease_unsupported_gpu_job(client):
    registered = register_worker(client)
    create_queued_job(client, gpu="rtx6000_blackwell_96gb")
    response = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={
        "supported_job_types": ["fine_tune"],
        "supported_gpu_skus": ["rog_astral_5090_32gb"],
        "max_jobs": 1
    })
    assert response.status_code == 200
    assert response.json()["message"] == "no_matching_jobs"


def test_lease_token_required_to_accept_job(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    response = client.post(f"/workers/jobs/{job_id}/accept", headers=auth_headers(registered["worker_token"]), json={"lease_token": "wrong"})
    assert response.status_code == 400
    assert lease["lease_token"] != "wrong"


def test_accept_marks_job_running(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    response = client.post(f"/workers/jobs/{job_id}/accept", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"]})
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert response.json()["actual_started_at"] is not None


def test_expired_lease_returns_job_to_queued(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    with client.app.state.testing_session_local() as db:
        db_lease = db.get(JobLease, lease["lease_id"])
        db_lease.expires_at = utc_now() - timedelta(seconds=1)
        db.commit()
        expired = expire_stale_leases(db)
        job = db.get(ComputeJob, job_id)
        assert expired == 1
        assert db_lease.status == "expired"
        assert job.status == "queued"
