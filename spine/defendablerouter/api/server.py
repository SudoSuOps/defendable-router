from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import orjson
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from defendablerouter import __version__
from defendablerouter.agents.swarmcurator_client import SwarmCuratorClient
from defendablerouter.config import RouterConfig
from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    finalize_run,
    write_ddeed_stub,
    write_tribunal_stub,
)
from defendablerouter.core.ledger import append_payload_file, verify_ledger as verify_ledger_chain
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.swarmjelly import build_pair, corpus_stats, write_pair
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.core.tribunal_grade import grade_receipt, write_verdict
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import Provenance, RouterReceipt

RUNS_ENV = "ROUTER_RUNS_DIR"
TOKEN_ENV = "STREETCHAT_INTAKE_TOKEN"
AUTOGRADE_ENV = "ROUTER_AUTOGRADE"
DEFAULT_RUNS = "data/runs"


class IntakeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    receipt_id: str
    assignment_id: str
    verdict_id: str
    deed_id: str
    canonical_receipt_sha256: str
    receipt_sha256: str
    object_storage_uri: str
    run_dir: str

    grading_status: Optional[str] = None
    tier: Optional[str] = None
    pair_id: Optional[str] = None
    ledger_seqs: Optional[dict] = None

    flag_reasons: Optional[list] = None
    flag_severity: Optional[str] = None


def _runs_dir() -> Path:
    return Path(os.environ.get(RUNS_ENV, DEFAULT_RUNS))


def _autograde_enabled() -> bool:
    return os.environ.get(AUTOGRADE_ENV, "true").strip().lower() not in ("false", "0", "no", "off")


def _require_token(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get(TOKEN_ENV)
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != expected:
        raise HTTPException(status_code=401, detail="invalid bearer token")


def _run_full_pipeline(event: RouterEvent, receipt: RouterReceipt, run_dir: Path, host: str) -> dict:
    """Run rails 2-4: SwarmCurator grade → write verdict → SwarmJelly pair → DefendableLedger append.

    Returns a dict summary. All steps degrade gracefully if the curator is unreachable
    or grading fails — the receipt is already minted, the spine never blocks intake on rails 2-4.
    """
    base_dir = _runs_dir().parent  # data/
    summary: dict = {"grading_status": None, "tier": None, "pair_id": None, "ledger_seqs": {}}

    # Rail 1: receipt → ledger
    receipt_ledger = append_payload_file(
        record_type="RECEIPT",
        payload_path=run_dir / "router_receipt.json",
        issued_by="DefendableRouter",
        host=host,
        base_dir=base_dir,
    )
    summary["ledger_seqs"]["receipt"] = receipt_ledger.ledger_seq

    # Rail 2: SwarmCurator grade
    verdict = grade_receipt(receipt, SwarmCuratorClient())
    write_verdict(verdict, run_dir)
    summary["grading_status"] = verdict.status
    summary["tier"] = verdict.tier
    summary["flag_reasons"] = list(verdict.flag_reasons)
    summary["flag_severity"] = verdict.flag_severity

    verdict_ledger = append_payload_file(
        record_type="VERDICT",
        payload_path=run_dir / "verdict.json",
        issued_by="Tribunal",
        host=host,
        base_dir=base_dir,
    )
    summary["ledger_seqs"]["verdict"] = verdict_ledger.ledger_seq

    # Rail 3: SwarmJelly pair (only if verdict has tier)
    pair = build_pair(event, verdict)
    if pair is not None:
        pair_path = write_pair(pair)
        pair_ledger = append_payload_file(
            record_type="PAIR",
            payload_path=pair_path,
            issued_by="SwarmJelly",
            host=host,
            base_dir=base_dir,
        )
        summary["pair_id"] = pair.pair_id
        summary["ledger_seqs"]["pair"] = pair_ledger.ledger_seq

    return summary


def create_app() -> FastAPI:
    app = FastAPI(
        title="DefendableRouter",
        description="Deterministic receipt spine + Tribunal grading + DefendableLedger anchoring · ring ring · to the shed.",
        version=__version__,
    )

    @app.get("/healthz")
    def healthz():
        cfg = RouterConfig.from_env()
        curator = SwarmCuratorClient()
        return {
            "ok": True,
            "service": "defendablerouter",
            "version": __version__,
            "host": cfg.host,
            "gpu": cfg.gpu,
            "cuda": cfg.cuda,
            "bucket": cfg.bucket,
            "auth_required": bool(os.environ.get(TOKEN_ENV)),
            "autograde": _autograde_enabled(),
            "curator_reachable": curator.is_reachable(),
        }

    @app.post(
        "/intake/streetchat",
        response_model=IntakeResponse,
        dependencies=[Depends(_require_token)],
    )
    def intake_streetchat(
        event: RouterEvent,
        grade: bool = Query(default=True, description="Run Tribunal grading + ledger append + SwarmJelly route. Default true."),
    ) -> IntakeResponse:
        config = RouterConfig.from_env()
        receipt = build_receipt(event)
        receipt.provenance = Provenance(host=config.host, gpu=config.gpu, cuda=config.cuda)

        run_dir = _runs_dir() / receipt.receipt_id
        run_dir.mkdir(parents=True, exist_ok=True)
        write_event_input(event, run_dir)

        tribunal_stub = create_tribunal_stub(receipt.assignment_id)
        receipt.tribunal.verdict_id = tribunal_stub.verdict_id
        write_tribunal_stub(tribunal_stub, run_dir)

        ddeed_stub = create_ddeed_stub(receipt.receipt_id, receipt.assignment_id)
        receipt.ddeed.deed_id = ddeed_stub.deed_id
        write_ddeed_stub(ddeed_stub, run_dir)

        finalize_receipt_hashes(receipt)
        write_receipt(receipt, run_dir)
        finalize_run(receipt, run_dir)

        pipeline_summary: dict = {
            "grading_status": None,
            "tier": None,
            "pair_id": None,
            "ledger_seqs": None,
            "flag_reasons": None,
            "flag_severity": None,
        }
        if grade and _autograde_enabled():
            try:
                pipeline_summary = _run_full_pipeline(event, receipt, run_dir, config.host)
            except Exception as exc:
                pipeline_summary = {
                    "grading_status": f"PIPELINE_ERROR: {exc}"[:200],
                    "tier": None,
                    "pair_id": None,
                    "ledger_seqs": None,
                    "flag_reasons": ["PIPELINE_ERROR"],
                    "flag_severity": "critical",
                }

        return IntakeResponse(
            ok=True,
            receipt_id=receipt.receipt_id,
            assignment_id=receipt.assignment_id,
            verdict_id=tribunal_stub.verdict_id,
            deed_id=ddeed_stub.deed_id,
            canonical_receipt_sha256=receipt.hashes.canonical_receipt_sha256 or "",
            receipt_sha256=receipt.hashes.receipt_sha256 or "",
            object_storage_uri=receipt.object_storage.uri,
            run_dir=str(run_dir),
            grading_status=pipeline_summary["grading_status"],
            tier=pipeline_summary["tier"],
            pair_id=pipeline_summary["pair_id"],
            ledger_seqs=pipeline_summary["ledger_seqs"],
            flag_reasons=pipeline_summary.get("flag_reasons"),
            flag_severity=pipeline_summary.get("flag_severity"),
        )

    @app.get("/receipt/{receipt_id}", dependencies=[Depends(_require_token)])
    def get_receipt(receipt_id: str):
        run_dir = _runs_dir() / receipt_id
        path = run_dir / "router_receipt.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"receipt {receipt_id} not found")
        return orjson.loads(path.read_bytes())

    @app.post("/tribunal/grade/{receipt_id}", dependencies=[Depends(_require_token)])
    def tribunal_grade_endpoint(receipt_id: str):
        run_dir = _runs_dir() / receipt_id
        receipt_path = run_dir / "router_receipt.json"
        event_path = run_dir / "input.json"
        if not receipt_path.exists() or not event_path.exists():
            raise HTTPException(status_code=404, detail=f"run {receipt_id} missing receipt or input")

        receipt = RouterReceipt.model_validate(orjson.loads(receipt_path.read_bytes()))
        event = RouterEvent.model_validate(orjson.loads(event_path.read_bytes()))
        config = RouterConfig.from_env()
        summary = _run_full_pipeline(event, receipt, run_dir, config.host)
        return {"ok": True, "receipt_id": receipt_id, **summary}

    @app.get("/ledger/verify")
    def ledger_verify():
        result = verify_ledger_chain()
        return {
            "ok": result.ok,
            "records_checked": result.records_checked,
            "first_break_seq": result.first_break_seq,
            "errors": result.errors[:10],
        }

    @app.get("/jelly/stats")
    def jelly_stats():
        return corpus_stats()

    return app


app = create_app()
