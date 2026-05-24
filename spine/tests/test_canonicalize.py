from defendablerouter.core.canonicalize import (
    canonical_json_bytes,
    canonicalize_for_hash,
)


def test_canonical_json_sorts_keys():
    a = {"b": 1, "a": 2}
    b = {"a": 2, "b": 1}
    assert canonical_json_bytes(a) == canonical_json_bytes(b)


def test_canonical_json_nested_sorts_keys():
    a = {"x": {"b": 1, "a": [3, 2, 1]}}
    b = {"x": {"a": [3, 2, 1], "b": 1}}
    assert canonical_json_bytes(a) == canonical_json_bytes(b)


def test_canonical_json_no_whitespace():
    out = canonical_json_bytes({"a": 1, "b": 2}).decode()
    assert " " not in out
    assert "\n" not in out


def test_canonicalize_strips_volatile():
    obj = {
        "receipt_id": "x",
        "created_at": "2026-05-24T00:00:00Z",
        "hashes": {"receipt_sha256": "deadbeef"},
        "payload": {"k": 1},
    }
    out = canonicalize_for_hash(obj)
    assert b"created_at" not in out
    assert b"hashes" not in out
    assert b"receipt_id" in out
    assert b"payload" in out


def test_canonicalize_deterministic_across_input_order():
    obj1 = {"created_at": "t1", "a": 1, "b": 2}
    obj2 = {"b": 2, "a": 1, "created_at": "t2"}
    assert canonicalize_for_hash(obj1) == canonicalize_for_hash(obj2)
