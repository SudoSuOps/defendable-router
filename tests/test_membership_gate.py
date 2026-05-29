def test_membership_activation(client):
    created = client.post("/members", json={"email": "new@example.com", "name": "New Member"})
    assert created.status_code == 200
    member_id = created.json()["id"]
    activated = client.post(f"/members/{member_id}/activate")
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    status = client.get(f"/members/{member_id}/status").json()
    assert status["active"] is True


def test_inactive_member_cannot_access_dataset(client):
    response = client.post("/datasets/ds_gold/access", json={"member_id": "mem_inactive"})
    assert response.status_code == 403


def test_active_member_can_access_dataset(client):
    response = client.post("/datasets/ds_gold/access", json={"member_id": "mem_active"})
    assert response.status_code == 200
    body = response.json()
    assert body["access_granted"] is True
    assert body["receipt_id"].startswith("rcpt_")
