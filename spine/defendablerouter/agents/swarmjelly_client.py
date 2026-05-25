from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "http://localhost:8089/v1"
DEFAULT_MODEL = "swarmjelly-4b"
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


@dataclass
class SwarmJellyConfig:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 60.0
    api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "SwarmJellyConfig":
        return cls(
            base_url=os.environ.get("SWARMJELLY_BASE_URL", DEFAULT_BASE_URL),
            model=os.environ.get("SWARMJELLY_MODEL", DEFAULT_MODEL),
            timeout=float(os.environ.get("SWARMJELLY_TIMEOUT", "60")),
            api_key=os.environ.get("SWARMJELLY_API_KEY"),
        )


def strip_think(content: str) -> str:
    """Strip Qwen3.5 <think>...</think> blocks the trained model emits even with no-think prompt."""
    return _THINK_RE.sub("", content).strip()


class SwarmJellyClient:
    """OpenAI-compatible client for the in-house SwarmJelly-4B GGUF endpoint (llama-cpp-python server).

    SwarmJelly is the tribunal-stage auditor (per its training Modelfile): audits
    repair-plan JSON against failure traces · scores 5 dimensions · returns RJ tier.
    Use for: secondary-opinion grading · repair plan audits · propolis-tier repair
    suggestion generation.
    """

    def __init__(self, config: Optional[SwarmJellyConfig] = None):
        self.config = config or SwarmJellyConfig.from_env()

    def is_reachable(self) -> bool:
        try:
            with httpx.Client(timeout=3.0) as c:
                r = c.get(f"{self.config.base_url}/models")
                return r.status_code == 200
        except Exception:
            return False

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 512,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Return the model's text content, stripped of <think> blocks."""
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop or ["<|im_end|>", "<|endoftext|>"],
        }
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        with httpx.Client(timeout=self.config.timeout) as client:
            r = client.post(f"{self.config.base_url}/chat/completions", json=payload, headers=headers)
            if r.status_code >= 400:
                raise RuntimeError(f"swarmjelly {r.status_code}: {r.text[:500]}")
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return strip_think(content)
