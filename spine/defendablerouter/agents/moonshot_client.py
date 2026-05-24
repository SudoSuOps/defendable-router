from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

DEFAULT_BASE_URL = "https://api.moonshot.ai/v1"
DEFAULT_MODEL = "kimi-k2.6"


@dataclass
class MoonshotConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    thinking: str = "disabled"
    timeout: float = 180.0
    temperature: Optional[float] = None

    @classmethod
    def from_env(cls) -> Optional["MoonshotConfig"]:
        key = os.environ.get("MOONSHOT_API_KEY")
        if not key:
            return None
        temp_raw = os.environ.get("MOONSHOT_TEMPERATURE")
        timeout_raw = os.environ.get("MOONSHOT_TIMEOUT")
        return cls(
            api_key=key,
            base_url=os.environ.get("MOONSHOT_BASE_URL", DEFAULT_BASE_URL),
            model=os.environ.get("MOONSHOT_MODEL", DEFAULT_MODEL),
            thinking=os.environ.get("MOONSHOT_THINKING", "disabled"),
            temperature=float(temp_raw) if temp_raw else None,
            timeout=float(timeout_raw) if timeout_raw else 180.0,
        )


class MoonshotClient:
    def __init__(self, config: MoonshotConfig):
        self.config = config

    def chat(self, messages: List[Dict[str, str]], response_format: Optional[Dict[str, Any]] = None) -> str:
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if self.config.temperature is not None:
            payload["temperature"] = self.config.temperature
        if response_format is not None:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.config.timeout) as client:
            r = client.post(f"{self.config.base_url}/chat/completions", json=payload, headers=headers)
            if r.status_code >= 400:
                raise RuntimeError(f"moonshot {r.status_code}: {r.text[:500]}")
            data = r.json()
        return data["choices"][0]["message"]["content"]

    def list_models(self) -> List[str]:
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        with httpx.Client(timeout=self.config.timeout) as client:
            r = client.get(f"{self.config.base_url}/models", headers=headers)
            if r.status_code >= 400:
                raise RuntimeError(f"moonshot {r.status_code}: {r.text[:500]}")
            data = r.json()
        return [m["id"] for m in data.get("data", [])]
