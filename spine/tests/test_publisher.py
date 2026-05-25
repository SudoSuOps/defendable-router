import subprocess
from pathlib import Path

import orjson
import pytest

from defendablerouter.core.ledger import append_payload_file
from defendablerouter.publisher.publish import publish


def _init_repo(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=p, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=p, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=p, check=True)
    return p


def _seed_payload(data_dir: Path, name: str, body: dict) -> Path:
    p = data_dir / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(orjson.dumps(body, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return p


@pytest.fixture
def env(tmp_path: Path, monkeypatch) -> dict:
    data = tmp_path / "data"
    ledger = data / "ledger" / "defendable_ledger.jsonl"
    monkeypatch.setenv("DEFENDABLE_LEDGER_PATH", str(ledger))

    repo = _init_repo(tmp_path / "ledger-repo")
    return {"data": data, "repo": repo, "tmp": tmp_path}


def test_publishes_new_records_copies_files_and_updates_index(env: dict):
    data: Path = env["data"]
    repo: Path = env["repo"]
    # Seed 2 payloads + 2 ledger records
    rcpt = _seed_payload(data, "runs/DRR-1/router_receipt.json", {"receipt_id": "DRR-1", "classification": "UNCLASSIFIED"})
    vrd = _seed_payload(data, "runs/DRR-1/verdict.json", {"verdict_id": "TRIB-1", "classification": "UNCLASSIFIED"})
    append_payload_file(record_type="RECEIPT", payload_path=rcpt, issued_by="DefendableRouter", host="smash", base_dir=data)
    append_payload_file(record_type="VERDICT", payload_path=vrd, issued_by="Tribunal", host="smash", base_dir=data)

    result = publish(repo=repo, commit=False, push=False)
    assert result.ok, result.errors
    assert result.new_records == 2
    assert (repo / "public/records/receipts/DRR-1.json").exists()
    assert (repo / "public/records/verdicts/TRIB-1.json").exists()

    index = orjson.loads((repo / "public/records/index.json").read_bytes())
    assert len(index) == 2
    types = {e["record_type"] for e in index}
    assert types == {"RECEIPT", "VERDICT"}


def test_publish_is_idempotent_via_cursor(env: dict):
    data, repo = env["data"], env["repo"]
    p = _seed_payload(data, "runs/X/router_receipt.json", {"receipt_id": "X"})
    append_payload_file(record_type="RECEIPT", payload_path=p, issued_by="t", host="smash", base_dir=data)

    r1 = publish(repo=repo)
    assert r1.new_records == 1
    r2 = publish(repo=repo)
    assert r2.new_records == 0  # cursor advanced · nothing new


def test_publish_skips_non_unclassified(env: dict):
    data, repo = env["data"], env["repo"]
    p = _seed_payload(data, "runs/S/secret.json", {"receipt_id": "S", "classification": "PRIVILEGED"})
    append_payload_file(record_type="RECEIPT", payload_path=p, issued_by="t", host="smash", base_dir=data)

    r = publish(repo=repo)
    assert r.new_records == 0
    assert any("S" in s for s in r.skipped)


def test_publish_commits_when_asked(env: dict):
    data, repo = env["data"], env["repo"]
    p = _seed_payload(data, "runs/Y/r.json", {"receipt_id": "Y"})
    append_payload_file(record_type="RECEIPT", payload_path=p, issued_by="t", host="smash", base_dir=data)

    r = publish(repo=repo, commit=True, push=False)
    assert r.ok, r.errors
    assert r.commit_sha and len(r.commit_sha) == 40
    log = subprocess.run(["git", "log", "--oneline"], cwd=repo, capture_output=True, text=True).stdout
    assert "Publish" in log


def test_publish_handles_missing_payload(env: dict):
    data, repo = env["data"], env["repo"]
    # ledger record points at non-existent file
    fake = data / "runs/missing/file.json"
    fake.parent.mkdir(parents=True, exist_ok=True)
    fake.write_bytes(b"{}")
    append_payload_file(record_type="RECEIPT", payload_path=fake, issued_by="t", host="smash", base_dir=data)
    fake.unlink()  # remove after ledger record points at it

    r = publish(repo=repo)
    assert not r.ok
    assert any("payload missing" in e for e in r.errors)
