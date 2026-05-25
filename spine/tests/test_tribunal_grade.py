from pathlib import Path
from typing import Any, Dict, List, Optional

import orjson

from defendablerouter.agents.swarmcurator_client import SwarmCuratorClient
from defendablerouter.core.receipt import build_receipt, finalize_receipt_hashes
from defendablerouter.core.tribunal_grade import grade_receipt
from defendablerouter.schemas.router_event import RouterEvent

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


def _event() -> RouterEvent:
    return RouterEvent.model_validate(orjson.loads(EXAMPLE.read_bytes()))


class FakeCuratorClient(SwarmCuratorClient):
    def __init__(self, *, reachable: bool = True, response: Optional[Dict[str, Any]] = None, raise_exc: Optional[Exception] = None):
        self._reachable = reachable
        self._response = response or {
            "rubric_scores": {"accuracy": 4.6, "cre_judgment": 4.5, "format": 4.7, "score": 4.6},
            "tier": "apex",
            "assignment_success": True,
            "notes": "operator-grade intake · principal-level signal",
        }
        self._raise = raise_exc

    def is_reachable(self) -> bool:
        return self._reachable

    def chat(self, messages: List[Dict[str, str]], response_format=None, temperature=0.0, max_tokens=1024) -> str:
        if self._raise is not None:
            raise self._raise
        return orjson.dumps(self._response).decode("utf-8")


def test_grade_skips_when_curator_unreachable():
    receipt = finalize_receipt_hashes(build_receipt(_event()))
    verdict = grade_receipt(receipt, FakeCuratorClient(reachable=False))
    assert verdict.status == "SKIPPED"
    assert verdict.tier is None
    assert verdict.rubric_scores is None
    assert verdict.verdict_sha256 and len(verdict.verdict_sha256) == 64


def test_grade_succeeds_apex_tier():
    receipt = finalize_receipt_hashes(build_receipt(_event()))
    verdict = grade_receipt(receipt, FakeCuratorClient())
    assert verdict.status == "GRADED"
    assert verdict.tier == "apex"
    assert verdict.rubric_scores is not None
    assert verdict.rubric_scores.mean > 4.5
    assert verdict.assignment_success is True
    assert "principal" in verdict.notes


def test_grade_handles_bad_json():
    class BrokenClient(FakeCuratorClient):
        def chat(self, *a, **kw):
            return "not json at all"
    verdict = grade_receipt(finalize_receipt_hashes(build_receipt(_event())), BrokenClient())
    assert verdict.status == "FAILED"
    assert "grading failed" in (verdict.skip_reason or "")


def test_grade_handles_network_error():
    verdict = grade_receipt(
        finalize_receipt_hashes(build_receipt(_event())),
        FakeCuratorClient(raise_exc=RuntimeError("connection refused")),
    )
    assert verdict.status == "FAILED"
    assert "connection refused" in (verdict.skip_reason or "")
