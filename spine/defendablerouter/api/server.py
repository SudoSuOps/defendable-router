from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import orjson
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from defendablerouter import __version__
from defendablerouter.config import RouterConfig
from defendablerouter.core.ddeed import create_ddeed_stub
from defendablerouter.core.export import (
    finalize_run,
    write_ddeed_stub,
    write_tribunal_stub,
)
from defendablerouter.core.receipt import (
    build_receipt,
    finalize_receipt_hashes,
    write_event_input,
    write_receipt,
)
from defendablerouter.core.tribunal import create_tribunal_stub
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.router_receipt import Provenance

RUNS_ENV = "ROUTER_RUNS_DIR"
TOKEN_ENV = "STREETCHAT_INTAKE_TOKEN"
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


def _runs_dir() -> Path:
    return Path(os.environ.get(RUNS_ENV, DEFAULT_RUNS))


def _require_token(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get(TOKEN_ENV)
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    if authorization.removeprefix("Bearer ").strip() != expected:
        raise HTTPException(status_code=401, detail="invalid bearer token")


def create_app() -> FastAPI:
    app = FastAPI(
        title="DefendableRouter",
        description="Deterministic receipt spine · ring ring · to the shed.",
        version=__version__,
    )

    @app.get("/healthz")
    def healthz():
        cfg = RouterConfig.from_env()
        return {
            "ok": True,
            "service": "defendablerouter",
            "version": __version__,
            "host": cfg.host,
            "gpu": cfg.gpu,
            "cuda": cfg.cuda,
            "bucket": cfg.bucket,
            "auth_required": bool(os.environ.get(TOKEN_ENV)),
        }

    @app.post(
        "/intake/streetchat",
        response_model=IntakeResponse,
        dependencies=[Depends(_require_token)],
    )
    def intake_streetchat(event: RouterEvent, request: Request) -> IntakeResponse:
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
        )

    @app.get("/receipt/{receipt_id}", dependencies=[Depends(_require_token)])
    def get_receipt(receipt_id: str):
        run_dir = _runs_dir() / receipt_id
        path = run_dir / "router_receipt.json"
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"receipt {receipt_id} not found")
        return orjson.loads(path.read_bytes())

    return app


app = create_app()
