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


def test_complete_marks_job_completed_and_calculates_cost(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    client.post(f"/workers/jobs/{job_id}/accept", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"]})
    response = client.post(f"/workers/jobs/{job_id}/complete", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"], "output_uri": "s3://defendable-artifacts/jobs/job/output", "metrics": {"duration_seconds": 3600}, "final_message": "done"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["actual_hours"] == 1.0
    assert body["actual_cost_usd"] == 2.0


def test_fail_marks_job_failed(client):
    registered = register_worker(client)
    job_id = create_queued_job(client)
    lease = client.post("/workers/jobs/lease", headers=auth_headers(registered["worker_token"]), json={"supported_job_types": ["fine_tune"], "supported_gpu_skus": ["rog_astral_5090_32gb"], "max_jobs": 1}).json()
    response = client.post(f"/workers/jobs/{job_id}/fail", headers=auth_headers(registered["worker_token"]), json={"lease_token": lease["lease_token"], "error_code": "OOM", "message": "CUDA out of memory", "payload": {}})
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_admin_summary_includes_worker_counts(client):
    registered = register_worker(client)
    client.post("/workers/heartbeat", headers=auth_headers(registered["worker_token"]), json={"status": "online", "current_jobs": 0, "metrics": {}})
    response = client.get("/admin/summary")
    assert response.status_code == 200
    body = response.json()
    for key in ["workers_online", "workers_offline", "workers_busy", "stale_workers", "active_leases", "expired_leases"]:
        assert key in body
    assert body["workers_online"] == 1


def test_admin_worker_list_and_detail(client):
    registered = register_worker(client)
    list_response = client.get("/admin/workers")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == registered["worker_id"]
    detail_response = client.get(f"/admin/workers/{registered['worker_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["worker"]["id"] == registered["worker_id"]
