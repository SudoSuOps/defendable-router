from __future__ import annotations

import os
import socket
from dataclasses import dataclass


@dataclass(frozen=True)
class RouterConfig:
    host: str
    gpu: str
    cuda: str
    bucket: str

    @classmethod
    def from_env(cls) -> "RouterConfig":
        return cls(
            host=os.environ.get("ROUTER_HOST", socket.gethostname() or "smash"),
            gpu=os.environ.get("ROUTER_GPU", "RTX 5090"),
            cuda=os.environ.get("ROUTER_CUDA", "13.1"),
            bucket=os.environ.get("STREETLEDGER_BUCKET", "streetledger"),
        )
