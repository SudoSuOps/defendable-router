from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import orjson

from defendablerouter.agents.hermes_client import HermesClient, HermesConfig

HERMES_PROMPT = (
    "Review this DefendableRouter receipt object as an audit-grade AI work receipt. "
    "Identify missing fields, schema risks, verification weaknesses, provenance "
    "weaknesses, and object-storage improvements. Do NOT rewrite the receipt. "
    "Do NOT alter any hash. Return JSON findings only matching this shape: "
    '{"findings":[],"missing_fields":[],"schema_risks":[],"suggested_tests":[],'
    '"verdict":"PASS|WARN|FAIL"}\n\n'
    "Doctrine: the verdict is flag-driven. PASS = no flags raised. WARN = "
    "non-critical structural gaps. FAIL = critical missing fields, "
    "unverifiable provenance, or broken hash chain. Never grade quality. "
    "Never recommend rewriting hashes or receipts. The hash is sacred."
)


def _skipped(run_id: str, receipt_id: str, reason: str, model: str = "hermes3:8b") -> Dict[str, Any]:
    return {
        "review_type": "HERMES_ROUTER_RECEIPT_REVIEW",
        "model": model,
        "thinking": "disabled",
        "run_id": run_id,
        "receipt_id": receipt_id,
        "findings": [],
        "missing_fields": [],
        "schema_risks": [],
        "suggested_tests": [],
        "verdict": "SKIPPED",
        "skip_reason": reason,
    }


def review_receipt(run_dir: Path) -> Dict[str, Any]:
    receipt_path = run_dir / "router_receipt.json"
    receipt = orjson.loads(receipt_path.read_bytes())
    run_id = run_dir.name
    receipt_id = receipt.get("receipt_id", "")

    config = HermesConfig.from_env()
    client = HermesClient(config)

    if not client.is_reachable():
        result = _skipped(
            run_id, receipt_id,
            f"hermes endpoint unreachable at {config.base_url}",
            config.model,
        )
        _write(result, run_dir)
        return result

    try:
        receipt_blob = orjson.dumps(receipt, option=orjson.OPT_SORT_KEYS).decode("utf-8")
        content = client.chat(
            messages=[
                {"role": "system", "content": HERMES_PROMPT},
                {"role": "user", "content": receipt_blob},
            ],
            response_format={"type": "json_object"},
        )
        findings = orjson.loads(content)
    except orjson.JSONDecodeError as exc:
        result = _skipped(
            run_id, receipt_id,
            f"hermes returned non-JSON content: {exc}",
            config.model,
        )
        _write(result, run_dir)
        return result
    except Exception as exc:  # network, http, parse
        result = _skipped(
            run_id, receipt_id,
            f"hermes call failed: {exc}",
            config.model,
        )
        _write(result, run_dir)
        return result

    result: Dict[str, Any] = {
        "review_type": "HERMES_ROUTER_RECEIPT_REVIEW",
        "model": config.model,
        "thinking": "disabled",
        "run_id": run_id,
        "receipt_id": receipt_id,
        "findings": findings.get("findings", []),
        "missing_fields": findings.get("missing_fields", []),
        "schema_risks": findings.get("schema_risks", []),
        "suggested_tests": findings.get("suggested_tests", []),
        "verdict": findings.get("verdict", "WARN"),
    }
    _write(result, run_dir)
    return result


def _write(payload: Dict[str, Any], run_dir: Path) -> Path:
    path = run_dir / "hermes_review.json"
    path.write_bytes(
        orjson.dumps(payload, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )
    return path
