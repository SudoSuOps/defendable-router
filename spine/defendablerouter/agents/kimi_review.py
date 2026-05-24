from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import orjson

from defendablerouter.agents.moonshot_client import MoonshotClient, MoonshotConfig

KIMI_PROMPT = (
    "Review this DefendableRouter receipt object as an audit-grade AI work receipt. "
    "Identify missing fields, schema risks, verification weaknesses, provenance weaknesses, "
    "and object-storage improvements. Do not rewrite the receipt. Return JSON findings only "
    "matching this shape: "
    '{"findings":[],"missing_fields":[],"schema_risks":[],"suggested_tests":[],'
    '"verdict":"PASS|WARN|FAIL"}'
)


def _skipped(run_id: str, receipt_id: str, reason: str) -> Dict[str, Any]:
    return {
        "review_type": "KIMI_ROUTER_RECEIPT_REVIEW",
        "model": "kimi-k2.6",
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

    config = MoonshotConfig.from_env()
    if config is None:
        result = _skipped(run_id, receipt_id, "MOONSHOT_API_KEY not set")
        _write(result, run_dir)
        return result

    try:
        client = MoonshotClient(config)
        receipt_blob = orjson.dumps(receipt, option=orjson.OPT_SORT_KEYS).decode("utf-8")
        content = client.chat(
            messages=[
                {"role": "system", "content": KIMI_PROMPT},
                {"role": "user", "content": receipt_blob},
            ],
            response_format={"type": "json_object"},
        )
        findings = orjson.loads(content)
    except Exception as exc:  # network, parse, http
        result = _skipped(run_id, receipt_id, f"kimi call failed: {exc}")
        _write(result, run_dir)
        return result

    result: Dict[str, Any] = {
        "review_type": "KIMI_ROUTER_RECEIPT_REVIEW",
        "model": config.model,
        "thinking": config.thinking,
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
    path = run_dir / "kimi_review.json"
    path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS))
    return path
