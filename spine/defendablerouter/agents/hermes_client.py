from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

# Ollama exposes an OpenAI-compatible endpoint at /v1.
DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "hermes3:8b"
# When the doctrine LoRA finishes:  HERMES_MODEL=hermes-defendable:8b
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


@dataclass
class HermesConfig:
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 60.0
    api_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "HermesConfig":
        return cls(
            base_url=os.environ.get("HERMES_BASE_URL", DEFAULT_BASE_URL),
            model=os.environ.get("HERMES_MODEL", DEFAULT_MODEL),
            timeout=float(os.environ.get("HERMES_TIMEOUT", "60")),
            api_key=os.environ.get("HERMES_API_KEY"),
        )


def strip_think(content: str) -> str:
    """Strip any <think>...</think> blocks. Hermes-3 doesn't emit them, but a
    LoRA fine-tune on doctrine data trained alongside Qwen3.5 corpora MIGHT
    pick up the habit. Defensive."""
    return _THINK_RE.sub("", content).strip()


class HermesClient:
    """OpenAI-compatible client for the in-house Hermes-3 8B endpoint (via Ollama).

    Hermes is the GENERAL receipt-spine reviewer: audits router receipts for
    structural integrity, missing fields, schema risks, and provenance
    weaknesses. Pairs with the audit-grade reviewers (Kimi, Jelly, Curator)
    as the volume-tier reviewer — fast, cheap, doctrine-trained.

    When the doctrine LoRA finishes (`hermes-defendable:8b`), set
    HERMES_MODEL=hermes-defendable:8b for doctrine-internalized review.
    """

    def __init__(self, config: Optional[HermesConfig] = None):
        self.config = config or HermesConfig.from_env()

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
        max_tokens: int = 1024,
        response_format: Optional[Dict[str, str]] = None,
        stop: Optional[List[str]] = None,
    ) -> str:
        """Return the model's text content, stripped of any <think> blocks."""
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop or ["<|im_end|>", "<|endoftext|>"],
        }
        if response_format is not None:
            payload["response_format"] = response_format
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        with httpx.Client(timeout=self.config.timeout) as client:
            r = client.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            if r.status_code >= 400:
                raise RuntimeError(f"hermes {r.status_code}: {r.text[:500]}")
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return strip_think(content)
