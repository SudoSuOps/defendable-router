from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import orjson

from defendablerouter.agents.swarmcurator_client import SwarmCuratorClient, SwarmCuratorConfig
from defendablerouter.core.canonicalize import canonicalize_for_hash
from defendablerouter.core.hash import sha256_bytes
from defendablerouter.core.ids import utc_now_iso, verdict_id as new_verdict_id
from defendablerouter.schemas.router_receipt import RouterReceipt
from defendablerouter.schemas.verdict import RubricScores, Tier, Verdict

VERDICT_VOLATILE = {"created_at", "verdict_sha256"}

SYSTEM_PROMPT = (
    "You are SwarmCurator, the in-house grading model for the DefendableOS ecosystem. "
    "Grade the DefendableRouter receipt presented in the user message against the "
    "4-dimension rubric (0.0-5.0 each):\n"
    "- accuracy: how factually grounded and verifiable the assignment is\n"
    "- cre_judgment: how operator-grade and CRE-broker-like the assignment is\n"
    "- format: how cleanly structured the parsed assignment is\n"
    "- score: overall holistic score\n\n"
    "Then assign a Royal Jelly tier:\n"
    "- apex: mean >= 4.5 (operator-grade ground truth)\n"
    "- honey: 3.5 <= mean < 4.5 (production-ready)\n"
    "- jelly: 2.5 <= mean < 3.5 (solid corpus material)\n"
    "- pollen: 1.5 <= mean < 2.5 (breadth coverage)\n"
    "- propolis: mean < 1.5 (edge cases / repair lift)\n\n"
    "Return JSON only, exact shape:\n"
    "{\n"
    '  "rubric_scores": {"accuracy": float, "cre_judgment": float, "format": float, "score": float},\n'
    '  "tier": "apex|honey|jelly|pollen|propolis",\n'
    '  "assignment_success": true|false,\n'
    '  "notes": "1-2 sentence operator note"\n'
    "}\n"
    "No prose. No markdown. JSON only."
)


def _tier_from_mean(mean: float) -> Tier:
    if mean >= 4.5:
        return "apex"
    if mean >= 3.5:
        return "honey"
    if mean >= 2.5:
        return "jelly"
    if mean >= 1.5:
        return "pollen"
    return "propolis"


def _strip_json_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        s = s.rsplit("```", 1)[0] if "```" in s else s
    return s.strip()


def _hash_verdict(v: Verdict) -> str:
    body = v.model_dump(mode="json")
    return sha256_bytes(canonicalize_for_hash(body, VERDICT_VOLATILE))


def grade_receipt(
    receipt: RouterReceipt,
    client: Optional[SwarmCuratorClient] = None,
) -> Verdict:
    """Grade a receipt via SwarmCurator-9B. Graceful skip if curator is unreachable."""
    vid = new_verdict_id()
    base = Verdict(
        verdict_id=vid,
        receipt_id=receipt.receipt_id,
        assignment_id=receipt.assignment_id,
        created_at=utc_now_iso(),
        graded_by="swarmcurator-9b",
    )

    client = client or SwarmCuratorClient()
    if not client.is_reachable():
        base.status = "SKIPPED"
        base.skip_reason = "SwarmCurator endpoint unreachable"
        base.verdict_sha256 = _hash_verdict(base)
        return base

    receipt_blob = orjson.dumps(receipt.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS).decode("utf-8")
    try:
        content = client.chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": receipt_blob},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=512,
        )
        parsed: Dict[str, Any] = json.loads(_strip_json_fences(content))
        scores = RubricScores(**parsed["rubric_scores"])
        tier = parsed.get("tier") or _tier_from_mean(scores.mean)
        base.status = "GRADED"
        base.rubric_scores = scores
        base.tier = tier  # type: ignore[assignment]
        base.assignment_success = bool(parsed.get("assignment_success", True))
        base.notes = (parsed.get("notes") or "")[:500]
    except Exception as exc:
        base.status = "FAILED"
        base.skip_reason = f"grading failed: {exc}"[:500]

    base.verdict_sha256 = _hash_verdict(base)
    return base


def write_verdict(verdict: Verdict, run_dir: Path) -> Path:
    path = run_dir / "verdict.json"
    path.write_bytes(
        orjson.dumps(verdict.model_dump(mode="json"), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )
    return path
