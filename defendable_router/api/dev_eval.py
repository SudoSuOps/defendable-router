"""Human-in-the-loop tune eval — DefendableDash /dev-eval tab.

Run a prompt against a tuned model (and optionally a base model for A/B) via the rig's
ollama, let a human referee the output, and mint the verdict onto the receipt hash chain.
Math + code stays deterministic; the human applies the rulebook (pass | flag) — we don't
judge with a model, we record a human's call against a declared prompt. Gated by read-token.
"""
import json
import os
import time
import urllib.request

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from defendable_router.core.config import get_settings
from defendable_router.core.receipts import read_chain, write_receipt
from defendable_router.core.security import require_read_token

router = APIRouter(prefix="/eval", tags=["dev-eval"], dependencies=[Depends(require_read_token)])

OLLAMA = os.environ.get("DEFENDABLE_OLLAMA_URL", "http://localhost:11434")


def _ollama(path: str, payload: dict | None = None, method: str = "GET", timeout: int = 120) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f"{OLLAMA}{path}", data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


@router.get("/models")
def list_models():
    """Models the rig's ollama can serve right now — the real dropdown, no fabrication."""
    try:
        tags = _ollama("/api/tags", timeout=8)
        return {"models": [m["name"] for m in tags.get("models", [])]}
    except Exception as e:  # honest empty state when ollama is down / model not served yet
        return {"models": [], "note": f"ollama unreachable: {e}"}


class InferReq(BaseModel):
    model: str
    prompt: str
    system: str | None = None
    base_model: str | None = None      # optional A/B (beat-base-or-kill)
    think: bool = False                # Qwen needs think-off
    temperature: float = 0.2


def _run(model: str, system: str | None, prompt: str, think: bool, temperature: float) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    t0 = time.time()
    out = _ollama("/api/chat", {
        "model": model, "messages": messages, "stream": False,
        "think": think, "options": {"temperature": temperature},
    }, method="POST", timeout=240)
    return {
        "model": model,
        "output": (out.get("message") or {}).get("content", "").strip(),
        "ms": round((time.time() - t0) * 1000),
        "eval_count": out.get("eval_count"),
    }


@router.post("/infer")
def infer(req: InferReq):
    """Run the prompt on the model (and base_model if given for side-by-side A/B)."""
    try:
        results = [_run(req.model, req.system, req.prompt, req.think, req.temperature)]
        if req.base_model and req.base_model != req.model:
            results.append(_run(req.base_model, req.system, req.prompt, req.think, req.temperature))
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"inference failed: {e}")


class VerdictReq(BaseModel):
    model: str
    prompt: str
    output: str
    verdict: str                       # pass | flag (binary referee call, not a quality grade)
    system: str | None = None
    score: int | None = None           # optional 0-100 operator score
    notes: str | None = None
    base_model: str | None = None
    base_output: str | None = None
    winner: str | None = None          # tuned | base | tie (A/B)


@router.post("/verdict")
def record_verdict(req: VerdictReq):
    """Mint the human referee's call onto the receipt hash chain (tamper-evident)."""
    if req.verdict not in ("pass", "flag"):
        raise HTTPException(status_code=422, detail="verdict must be 'pass' or 'flag'")
    rcpt = write_receipt(
        receipt_type="dev-eval-verdict",
        member_id="operator",
        amount_usd=0,
        metadata=req.model_dump(),
    )
    return {
        "receipt_id": rcpt["receipt_id"],
        "seq": rcpt["seq"],
        "checksum_sha256": rcpt["checksum_sha256"],
        "created_at": rcpt["created_at"],
    }


@router.get("/verdicts")
def list_verdicts(limit: int = 50):
    """Recent human verdicts from the chain (the human-in-the-loop eval ledger)."""
    chain = read_chain(get_settings().receipts_dir)
    evals = [r for r in chain if r.get("receipt_type") == "dev-eval-verdict"]
    return {"count": len(evals), "verdicts": evals[-max(limit, 0):] if limit else evals}
