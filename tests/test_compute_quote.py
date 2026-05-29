def test_compute_quote_rtx6000(client):
    response = client.post("/compute/quote", json={"member_id": "mem_active", "requested_gpu_sku": "rtx6000_blackwell_96gb", "estimated_hours": 2, "job_type": "fine_tune"})
    assert response.status_code == 200
    assert response.json()["estimated_cost_usd"] == 10.0


def test_compute_quote_5090(client):
    response = client.post("/compute/quote", json={"member_id": "mem_active", "requested_gpu_sku": "rog_astral_5090_32gb", "estimated_hours": 3, "job_type": "inference"})
    assert response.status_code == 200
    assert response.json()["estimated_cost_usd"] == 6.0
