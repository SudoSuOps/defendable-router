def test_job_creation_creates_receipt(client):
    response = client.post("/jobs", json={"member_id": "mem_active", "job_type": "fine_tune", "requested_gpu_sku": "rtx6000_blackwell_96gb", "estimated_hours": 2, "input_dataset_ids": ["ds_gold"]})
    assert response.status_code == 200
    body = response.json()
    assert body["receipt_id"].startswith("rcpt_")
    assert body["estimated_cost_usd"] == 10.0
    assert body["status"] in {"queued", "running"}


def test_completing_job_calculates_actual_cost(client):
    created = client.post("/jobs", json={"member_id": "mem_active", "job_type": "inference", "requested_gpu_sku": "rog_astral_5090_32gb", "estimated_hours": 3, "input_dataset_ids": ["ds_gold"]}).json()
    completed = client.post(f"/jobs/{created['id']}/complete")
    assert completed.status_code == 200
    body = completed.json()
    assert body["status"] == "completed"
    assert body["actual_hours"] > 0
    assert body["actual_cost_usd"] >= 0
    assert body["receipt_id"].startswith("rcpt_")
