from pathlib import Path

import orjson
import pytest
from fastapi.testclient import TestClient

from defendablerouter.api.server import RUNS_ENV, TOKEN_ENV, create_app
from defendablerouter.core.verify import verify_run

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


@pytest.fixture
def event_payload() -> dict:
    return orjson.loads(EXAMPLE.read_bytes())


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setenv(RUNS_ENV, str(tmp_path))
    monkeypatch.delenv(TOKEN_ENV, raising=False)
    return TestClient(create_app())


def test_healthz_returns_service_metadata(client: TestClient):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["service"] == "defendablerouter"
    assert body["auth_required"] is False


def test_intake_creates_verifiable_receipt(client: TestClient, event_payload: dict, tmp_path: Path):
    r = client.post("/intake/streetchat", json=event_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["receipt_id"].startswith("DRR-")
    assert body["assignment_id"].startswith("ASSIGN-")
    assert len(body["canonical_receipt_sha256"]) == 64
    assert len(body["receipt_sha256"]) == 64
    assert body["object_storage_uri"].startswith("s3://streetledger/router/")

    run_dir = tmp_path / body["receipt_id"]
    assert run_dir.exists()
    result = verify_run(run_dir)
    assert result.ok, result.errors


def test_get_receipt_roundtrip(client: TestClient, event_payload: dict):
    r = client.post("/intake/streetchat", json=event_payload)
    receipt_id = r.json()["receipt_id"]
    g = client.get(f"/receipt/{receipt_id}")
    assert g.status_code == 200
    assert g.json()["receipt_id"] == receipt_id


def test_get_receipt_404_for_unknown(client: TestClient):
    r = client.get("/receipt/DRR-19700101-DOESNOTEXIST")
    assert r.status_code == 404


def test_intake_rejects_invalid_event(client: TestClient):
    r = client.post("/intake/streetchat", json={"client_id": "x"})
    assert r.status_code == 422


def test_auth_gate_when_token_set(tmp_path: Path, monkeypatch, event_payload: dict):
    monkeypatch.setenv(RUNS_ENV, str(tmp_path))
    monkeypatch.setenv(TOKEN_ENV, "secret-token-123")
    client = TestClient(create_app())

    bad = client.post("/intake/streetchat", json=event_payload)
    assert bad.status_code == 401

    bad_token = client.post(
        "/intake/streetchat",
        json=event_payload,
        headers={"Authorization": "Bearer wrong"},
    )
    assert bad_token.status_code == 401

    good = client.post(
        "/intake/streetchat",
        json=event_payload,
        headers={"Authorization": "Bearer secret-token-123"},
    )
    assert good.status_code == 200


def test_healthz_reflects_auth_required(tmp_path: Path, monkeypatch):
    monkeypatch.setenv(RUNS_ENV, str(tmp_path))
    monkeypatch.setenv(TOKEN_ENV, "x")
    client = TestClient(create_app())
    assert client.get("/healthz").json()["auth_required"] is True
