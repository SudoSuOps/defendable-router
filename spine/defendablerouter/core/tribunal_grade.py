from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import orjson

from defendablerouter.agents.swarmcurator_client import SwarmCuratorClient, SwarmCuratorConfig
from defendablerouter.core.canonicalize import canonicalize_for_hash
from defendablerouter.core.hash import sha256_bytes
from defendablerouter.core.ids import utc_now_iso, verdict_id as new_verdict_id
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import RouterReceipt
from defendablerouter.schemas.verdict import RubricScores, Severity, Tier, Verdict
from defendablerouter.util.vocab import score_text as score_vocab

VERDICT_VOLATILE = {"created_at", "verdict_sha256"}
LOW_SCORE_THRESHOLD = 3.0
LOW_VOCAB_DENSITY = 0.02  # < 2% canonical-term tokens · CRE intake should beat this
CRE_ASSIGNMENT_HINTS = {
    "underwriting", "disposition_flight_sheet", "exchange_1031", "tax_assessment",
    "upleg_search", "ic_memo", "comp_set", "rent_roll_analysis", "lease_abstract",
}
_SEVERITY_RANK = {"info": 0, "warn": 1, "critical": 2}


def _compute_flags(verdict: Verdict) -> tuple[list[str], Severity]:
    reasons: list[str] = []
    severity: Severity = "info"

    def bump(new: Severity) -> None:
        nonlocal severity
        if _SEVERITY_RANK[new] > _SEVERITY_RANK[severity]:
            severity = new

    if verdict.status == "FAILED":
        reasons.append("GRADING_FAILED")
        bump("warn")
    elif verdict.status == "SKIPPED":
        reasons.append("GRADING_SKIPPED")

    if verdict.tier == "propolis":
        reasons.append("TIER_PROPOLIS")
        bump("warn")

    if verdict.rubric_scores is not None:
        for dim in ("accuracy", "cre_judgment", "format", "score"):
            v = getattr(verdict.rubric_scores, dim, None)
            if v is not None and v < LOW_SCORE_THRESHOLD:
                reasons.append(f"LOW_RUBRIC_{dim.upper()}:{v}")
                bump("warn")

    if (
        verdict.vocab_density is not None
        and verdict.vocab_density < LOW_VOCAB_DENSITY
    ):
        reasons.append(f"LOW_VOCAB_DENSITY:{verdict.vocab_density:.3f}")
        bump("warn")

    return reasons, severity

SYSTEM_PROMPT = (
    "You are SwarmCurator, the in-house grading model for the DefendableOS ecosystem.\n\n"
    "Your job is to grade DefendableRouter receipts on a 4-dimension rubric and route\n"
    "training pairs into the correct Royal Jelly tier so SwarmFixer learns from real\n"
    "failure modes, not aspirational scores.\n\n"
    "RUBRIC (0.0-5.0, be honest, no inflation):\n"
    "- accuracy     · how factually grounded and verifiable the parsed assignment is\n"
    "                 5 = specific verifiable claims · 3 = plausible but generic · 1 = vague · 0 = empty\n"
    "- cre_judgment · how operator-grade / CRE-broker-like the intake is\n"
    "                 5 = principal voice · specific deal language · real urgency · 3 = competent\n"
    "                 1 = generic startup-speak · 0 = no operator signal\n"
    "- format       · how cleanly structured the parsed assignment block is\n"
    "                 5 = assignment_type clear · urgency real · expected_outputs concrete\n"
    "                 3 = partial · 1 = mostly empty · 0 = malformed or empty\n"
    "- score        · overall holistic operator-grade gut check\n\n"
    "HARD RULES (apply BEFORE the rubric · these force propolis):\n"
    "1. raw_client_language is empty or <10 chars → tier = propolis · cap all scores ≤ 1.0\n"
    "2. assignment_type is 'unknown', 'empty_intake', or missing → tier = propolis\n"
    "3. expected_outputs is an empty array → cap accuracy ≤ 1.5\n"
    "4. raw_client_language is incoherent ('uh yeah do the thing', filler words, no specifics) → cap all scores ≤ 1.5\n"
    "5. If the intake would NOT pencil with a CRE broker → tier is propolis or pollen\n"
    "6. vocab_signal.density is the share of canonical DefendableOS/CRE terms (1031 · cap rate · NOI · DSCR · STNL · WALT · etc.) per total tokens.\n"
    "   - density < 0.02 AND assignment_type claims CRE work → cap cre_judgment ≤ 2.0 · tier propolis or pollen\n"
    "   - density >= 0.05 with substantive content → eligible for honey/apex\n"
    "   - Use vocab_signal.terms_seen as ground truth · do not invent vocab the intake does not actually use\n\n"
    "ROYAL JELLY TIERS (route the training pair here):\n"
    "- apex     mean >= 4.5  · operator-grade ground truth · principal language · primary fine-tune fuel\n"
    "- honey    3.5–4.5      · production-ready · validator chain training\n"
    "- jelly    2.5–3.5      · solid corpus material · DPO candidates\n"
    "- pollen   1.5–2.5      · breadth · low-weight inclusion\n"
    "- propolis < 1.5        · edge cases · failure modes · repair lift · SwarmFixer fuel\n\n"
    "DO NOT be charitable. If the intake would fail a CRE-broker sniff test, grade it that way.\n"
    "The propolis corpus is the most valuable training data the fleet mints because it teaches\n"
    "the system to recognize and repair failure. Inflated scores hurt the fleet.\n\n"
    "Return JSON only · NO prose · NO markdown · exact shape:\n"
    "{\n"
    '  "rubric_scores": {"accuracy": float, "cre_judgment": float, "format": float, "score": float},\n'
    '  "tier": "apex|honey|jelly|pollen|propolis",\n'
    '  "assignment_success": true|false,\n'
    '  "notes": "1 sentence · dominant failure mode if propolis/pollen · what makes it strong if apex/honey"\n'
    "}"
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


def _build_grading_payload(
    receipt: RouterReceipt,
    event: Optional[RouterEvent],
    vocab_signal: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compose the focused JSON payload the curator grades.

    Receipt envelope alone is misleading (tribunal/ddeed stubs are null by design ·
    raw_client_language lives in the event, not the receipt). Send the event content
    front-and-center · receipt provenance as supporting metadata · vocab signal
    so the curator can ground its CRE judgment in canonical terms actually present.
    """
    if event is not None:
        payload: Dict[str, Any] = {
            "raw_client_language": event.raw_client_language,
            "parsed_assignment": event.assignment.model_dump(mode="json"),
            "source_type": event.source_type,
            "route": event.route,
            "client_id": event.client_id,
            "app_id": event.app_id,
            "agent_id": event.agent_id,
            "edge_device_id": event.edge_device_id,
            "receipt_meta": {
                "receipt_id": receipt.receipt_id,
                "assignment_id": receipt.assignment_id,
                "issued_by_host": receipt.provenance.host,
                "object_storage_uri": receipt.object_storage.uri,
            },
        }
        if vocab_signal is not None:
            payload["vocab_signal"] = vocab_signal
        return payload
    return receipt.model_dump(mode="json")


def grade_receipt(
    receipt: RouterReceipt,
    client: Optional[SwarmCuratorClient] = None,
    event: Optional[RouterEvent] = None,
) -> Verdict:
    """Grade a receipt via SwarmCurator-9B. Graceful skip if curator is unreachable.

    Pass `event` to give the curator the actual intake content. Without it, the
    curator sees only the receipt envelope (no raw_client_language) and will under-grade.
    """
    vid = new_verdict_id()
    base = Verdict(
        verdict_id=vid,
        receipt_id=receipt.receipt_id,
        assignment_id=receipt.assignment_id,
        created_at=utc_now_iso(),
        graded_by="swarmcurator-9b",
    )

    # Vocab signal · computed deterministically from event text, independent of curator
    vocab_signal: Optional[Dict[str, Any]] = None
    if event is not None:
        vs = score_vocab(event.raw_client_language)
        base.vocab_density = round(vs.density, 4)
        base.vocab_terms_seen = vs.terms_seen
        vocab_signal = {
            "density": base.vocab_density,
            "terms_seen": vs.terms_seen[:20],
            "matched_tokens": vs.matched_tokens,
            "total_tokens": vs.total_tokens,
        }

    client = client or SwarmCuratorClient()
    if not client.is_reachable():
        base.status = "SKIPPED"
        base.skip_reason = "SwarmCurator endpoint unreachable"
        base.flag_reasons, base.flag_severity = _compute_flags(base)
        base.verdict_sha256 = _hash_verdict(base)
        return base

    payload = _build_grading_payload(receipt, event, vocab_signal)
    payload_blob = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS).decode("utf-8")
    try:
        content = client.chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": payload_blob},
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

    base.flag_reasons, base.flag_severity = _compute_flags(base)
    base.verdict_sha256 = _hash_verdict(base)
    return base


def write_verdict(verdict: Verdict, run_dir: Path) -> Path:
    path = run_dir / "verdict.json"
    path.write_bytes(
        orjson.dumps(verdict.model_dump(mode="json"), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )
    return path
