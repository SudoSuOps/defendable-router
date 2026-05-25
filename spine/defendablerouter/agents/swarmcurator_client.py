from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "http://localhost:8088/v1"
DEFAULT_MODEL = "swarmcurator-9b"


@dataclass
class SwarmCuratorConfig:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 60.0
    api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "SwarmCuratorConfig":
        return cls(
            base_url=os.environ.get("SWARMCURATOR_BASE_URL", DEFAULT_BASE_URL),
            model=os.environ.get("SWARMCURATOR_MODEL", DEFAULT_MODEL),
            timeout=float(os.environ.get("SWARMCURATOR_TIMEOUT", "60")),
            api_key=os.environ.get("SWARMCURATOR_API_KEY"),
        )


class SwarmCuratorClient:
    """OpenAI-compatible client for the in-house SwarmCurator-9B vllm endpoint."""

    def __init__(self, config: Optional[SwarmCuratorConfig] = None):
        self.config = config or SwarmCuratorConfig.from_env()

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
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format

        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        with httpx.Client(timeout=self.config.timeout) as client:
            r = client.post(f"{self.config.base_url}/chat/completions", json=payload, headers=headers)
            if r.status_code >= 400:
                raise RuntimeError(f"swarmcurator {r.status_code}: {r.text[:500]}")
            data = r.json()
        return data["choices"][0]["message"]["content"]
