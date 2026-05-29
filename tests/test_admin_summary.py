def test_admin_summary_fields(client):
    response = client.get("/admin/summary")
    assert response.status_code == 200
    body = response.json()
    for key in ["active_members_count", "total_datasets_count", "compute_nodes_available", "compute_nodes_busy", "queued_jobs", "running_jobs", "completed_jobs", "estimated_revenue_from_jobs", "annual_membership_revenue"]:
        assert key in body
