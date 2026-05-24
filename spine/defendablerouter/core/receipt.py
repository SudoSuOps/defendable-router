from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import orjson

from defendablerouter.core.canonicalize import canonical_json_bytes
from defendablerouter.core.hash import (
    sha256_bytes,
    sha256_canonical_for_receipt,
)
from defendablerouter.core.ids import (
    assignment_id as new_assignment_id,
    receipt_id as new_receipt_id,
    utc_now_iso,
)
from defendablerouter.core.object_paths import build_object_storage
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import (
    ReceiptHashes,
    ReceiptInput,
    ReceiptOutput,
    RouterReceipt,
)


def _dump(model) -> Dict[str, Any]:
    return model.model_dump(mode="json")


def hash_event_input(event: RouterEvent) -> tuple[str, int]:
    """Hash the input event bytes (deterministic canonical JSON of the raw event)."""
    data = canonical_json_bytes(_dump(event))
    return sha256_bytes(data), len(data)


def build_receipt(event: RouterEvent) -> RouterReceipt:
    """Construct a RouterReceipt from a RouterEvent. Hashes are filled in later."""
    rid = new_receipt_id()
    aid = new_assignment_id()
    input_hash, input_bytes = hash_event_input(event)

    receipt = RouterReceipt(
        receipt_id=rid,
        created_at=utc_now_iso(),
        client_id=event.client_id,
        app_id=event.app_id,
        agent_id=event.agent_id,
        edge_device_id=event.edge_device_id,
        conversation_id=event.conversation_id,
        assignment_id=aid,
        route=event.route,
        source_type=event.source_type,
        input=ReceiptInput(
            input_hash=input_hash,
            input_bytes=input_bytes,
            input_ref="input.json",
        ),
        output=ReceiptOutput(),
        object_storage=build_object_storage(event.client_id, event.app_id, aid),
    )
    return receipt


def finalize_receipt_hashes(receipt: RouterReceipt) -> RouterReceipt:
    """Compute canonical_receipt_sha256 (volatile-stripped) and receipt_sha256 (full canonical JSON)."""
    body = _dump(receipt)
    canonical_hash = sha256_canonical_for_receipt(body)

    body_with_canonical = dict(body)
    body_with_canonical["hashes"] = {
        "receipt_sha256": None,
        "canonical_receipt_sha256": canonical_hash,
    }
    receipt_hash = sha256_bytes(canonical_json_bytes(body_with_canonical))

    receipt.hashes = ReceiptHashes(
        receipt_sha256=receipt_hash,
        canonical_receipt_sha256=canonical_hash,
    )
    return receipt


def write_receipt(receipt: RouterReceipt, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "router_receipt.json"
    path.write_bytes(orjson.dumps(_dump(receipt), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return path


def write_event_input(event: RouterEvent, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "input.json"
    path.write_bytes(orjson.dumps(_dump(event), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return path
