import json
import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends

from defendable_router.core.security import require_read_token

# Live cook telemetry surface for DefendableDash's /tune tab. A sidecar on the rig
# writes current.json (step/loss/status from the cook log); we serve it + live GPU
# stats. Gated by the read-token, same as /admin and /receipts.
router = APIRouter(prefix="/tune", tags=["tune"], dependencies=[Depends(require_read_token)])

TUNE_FILE = os.environ.get("DEFENDABLE_TUNE_STATE_FILE", "/home/swarm/tune/current.json")


def _gpu_live() -> dict | None:
    try:
        out = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4,
        ).stdout.strip().splitlines()[0]
        mu, mt, util, temp, pw = [x.strip() for x in out.split(",")]
        return {
            "vram_used_gb": round(float(mu) / 1024, 1),
            "vram_total_gb": round(float(mt) / 1024, 1),
            "gpu_util": int(float(util)),
            "gpu_temp": int(float(temp)),
            "power_w": round(float(pw)),
        }
    except Exception:
        return None


@router.get("")
def tune_state():
    """Current cook telemetry (live). Honest idle state when nothing's cooking."""
    p = Path(TUNE_FILE)
    if p.exists():
        try:
            state = json.loads(p.read_text())
        except Exception:
            state = {"status": "unknown", "note": "tune state unreadable"}
    else:
        state = {"status": "idle", "note": "no active cook"}
    state["gpu_live"] = _gpu_live()
    return state
