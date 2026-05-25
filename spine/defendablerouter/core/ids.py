from __future__ import annotations

from datetime import datetime, timezone

import ulid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_date_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def new_ulid() -> str:
    return str(ulid.new())


def receipt_id() -> str:
    return f"DRR-{utc_date_compact()}-{new_ulid()}"


def assignment_id() -> str:
    return f"ASSIGN-{utc_date_compact()}-{new_ulid()}"


def tribunal_stub_id() -> str:
    return f"TRIB-STUB-{utc_date_compact()}-{new_ulid()}"


def ddeed_stub_id() -> str:
    return f"DDEED-ROUTER-STUB-{utc_date_compact()}-{new_ulid()}"


def manifest_id() -> str:
    return f"MANIFEST-{utc_date_compact()}-{new_ulid()}"


def verdict_id() -> str:
    return f"TRIB-{utc_date_compact()}-{new_ulid()}"


def ledger_record_id() -> str:
    return f"DLR-{utc_date_compact()}-{new_ulid()}"


def pair_id() -> str:
    return f"SJP-{utc_date_compact()}-{new_ulid()}"


def audit_id() -> str:
    return f"JLY-{utc_date_compact()}-{new_ulid()}"
