import json
from pathlib import Path

from defendable_router.core.config import get_settings

ZERO = "0" * 64


def _mint_some(client):
    # dataset access (active member) -> dataset_access receipt
    client.post("/datasets/ds_gold/access", json={"member_id": "mem_active"})
    # job creation -> fine_tune_job receipt
    client.post("/jobs", json={
        "member_id": "mem_active", "job_type": "fine_tune",
        "requested_gpu_sku": "rtx6000_blackwell_96gb", "estimated_hours": 2,
        "input_dataset_ids": ["ds_gold"],
    })


def test_receipts_form_a_hash_chain(client):
    _mint_some(client)
    chain = client.get("/receipts").json()["receipts"]
    assert len(chain) >= 2
    assert chain[0]["seq"] == 0
    assert chain[0]["parent_hash"] == ZERO
    for i in range(1, len(chain)):
        assert chain[i]["seq"] == i
        assert chain[i]["parent_hash"] == chain[i - 1]["checksum_sha256"]


def test_verify_ledger_ok(client):
    _mint_some(client)
    v = client.get("/receipts/verify").json()
    assert v["ok"] is True
    assert v["receipts_checked"] >= 2
    assert v["errors"] == []


def test_tampering_breaks_the_chain(client):
    _mint_some(client)
    rdir = Path(get_settings().receipts_dir)
    files = sorted(rdir.glob("*.receipts.jsonl"))
    assert files, "no ledger file written"

    # silently mutate the genesis receipt's amount, leaving its checksum intact
    f = files[0]
    lines = f.read_text(encoding="utf-8").splitlines()
    obj = json.loads(lines[0])
    obj["amount_usd"] = "999999.99"
    lines[0] = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    v = client.get("/receipts/verify").json()
    assert v["ok"] is False
    assert any(e["error"] == "checksum mismatch" for e in v["errors"])
