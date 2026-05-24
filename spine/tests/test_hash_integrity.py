from defendablerouter.core.hash import (
    sha256_bytes,
    sha256_canonical_for_receipt,
    sha256_canonical_json,
    sha256_file,
    sha256_str,
)


def test_sha256_known_vector():
    assert sha256_bytes(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert sha256_str("ring ring") == sha256_bytes(b"ring ring")


def test_sha256_file(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"to the shed")
    assert sha256_file(p) == sha256_bytes(b"to the shed")


def test_canonical_json_hash_order_invariant():
    a = {"x": 1, "y": [1, 2, {"b": 1, "a": 2}]}
    b = {"y": [1, 2, {"a": 2, "b": 1}], "x": 1}
    assert sha256_canonical_json(a) == sha256_canonical_json(b)


def test_canonical_receipt_hash_ignores_volatile():
    base = {
        "receipt_id": "DRR-1",
        "client_id": "mrdefendable.eth",
        "payload": {"k": "v"},
    }
    with_volatile = dict(base, created_at="2026-05-24T00:00:00Z", hashes={"receipt_sha256": "abc"})
    assert sha256_canonical_for_receipt(base) == sha256_canonical_for_receipt(with_volatile)
