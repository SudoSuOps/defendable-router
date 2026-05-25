from pathlib import Path

import orjson
import pytest
from fastapi.testclient import TestClient

from defendablerouter.api.server import AUTOGRADE_ENV, RUNS_ENV, TOKEN_ENV, create_app
from defendablerouter.core.verify import verify_run

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


@pytest.fixture
def event_payload() -> dict:
    return orjson.loads(EXAMPLE.read_bytes())


def _isolate(tmp_path: Path, monkeypatch, autograde: bool = False) -> None:
    monkeypatch.setenv(RUNS_ENV, str(tmp_path / "runs"))
    monkeypatch.setenv("DEFENDABLE_LEDGER_PATH", str(tmp_path / "ledger" / "defendable_ledger.jsonl"))
    monkeypatch.setenv("SWARMJELLY_CORPUS_DIR", str(tmp_path / "swarmjelly"))
    monkeypatch.setenv(AUTOGRADE_ENV, "true" if autograde else "false")
    monkeypatch.delenv(TOKEN_ENV, raising=False)


@pytest.fixture
def client(tmp_path: Path, monkeypatch) -> TestClient:
    _isolate(tmp_path, monkeypatch, autograde=False)
    return TestClient(create_app())


def test_healthz_returns_service_metadata(client: TestClient):
    r = client.get("/healthz")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["service"] == "defendablerouter"
    assert body["auth_required"] is False
    assert "curator_reachable" in body
    assert "autograde" in body


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

    run_dir = tmp_path / "runs" / body["receipt_id"]
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
    _isolate(tmp_path, monkeypatch, autograde=False)
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
    _isolate(tmp_path, monkeypatch, autograde=False)
    monkeypatch.setenv(TOKEN_ENV, "x")
    client = TestClient(create_app())
    assert client.get("/healthz").json()["auth_required"] is True


def test_autograde_pipeline_runs_and_skips_when_curator_down(
    tmp_path: Path, monkeypatch, event_payload: dict
):
    """With autograde ON but curator unreachable: receipt mints, verdict=SKIPPED, no pair, ledger appended."""
    _isolate(tmp_path, monkeypatch, autograde=True)
    monkeypatch.setenv("SWARMCURATOR_BASE_URL", "http://127.0.0.1:1/v1")  # guaranteed unreachable
    client = TestClient(create_app())

    r = client.post("/intake/streetchat", json=event_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    assert body["grading_status"] == "SKIPPED"
    assert body["tier"] is None
    assert body["pair_id"] is None
    assert body["ledger_seqs"] is not None
    assert "receipt" in body["ledger_seqs"]
    assert "verdict" in body["ledger_seqs"]

    # verdict.json was written
    run_dir = tmp_path / "runs" / body["receipt_id"]
    assert (run_dir / "verdict.json").exists()


def test_autograde_can_be_disabled_per_request(
    tmp_path: Path, monkeypatch, event_payload: dict
):
    _isolate(tmp_path, monkeypatch, autograde=True)
    client = TestClient(create_app())
    r = client.post("/intake/streetchat?grade=false", json=event_payload)
    assert r.status_code == 200
    body = r.json()
    assert body["grading_status"] is None
    assert body["ledger_seqs"] is None


def test_ledger_verify_endpoint(tmp_path: Path, monkeypatch, event_payload: dict):
    _isolate(tmp_path, monkeypatch, autograde=True)
    monkeypatch.setenv("SWARMCURATOR_BASE_URL", "http://127.0.0.1:1/v1")
    client = TestClient(create_app())
    # No records yet → chain trivially passes
    r0 = client.get("/ledger/verify")
    assert r0.status_code == 200
    assert r0.json()["ok"] is True

    # Mint one receipt → 2 records appended (RECEIPT + VERDICT) + GENESIS
    client.post("/intake/streetchat", json=event_payload)
    r1 = client.get("/ledger/verify")
    assert r1.status_code == 200
    body = r1.json()
    assert body["ok"] is True
    assert body["records_checked"] >= 3


def test_jelly_stats_endpoint(client: TestClient):
    r = client.get("/jelly/stats")
    assert r.status_code == 200
    body = r.json()
    assert "apex" in body
    assert body["total"] == 0
