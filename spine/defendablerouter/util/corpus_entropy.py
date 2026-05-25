"""Bridge between SwarmJelly corpus (one JSON per pair) and dataset-entropy (JSONL).

Reads every pair file under data/swarmjelly/<tier>/ and projects to the
chat-format JSONL that dataset_entropy.py understands. Provides a single
function to produce the entropy report over the live corpus.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Dict, List, Optional

import orjson

from defendablerouter.core.swarmjelly import TIERS, corpus_dir
from defendablerouter.util.dataset_entropy import entropy_report, print_report

DEFAULT_TIERS = list(TIERS)


def _pair_to_chat(pair: Dict[str, Any]) -> Dict[str, Any]:
    """Project a TrainingPair JSON into OpenAI chat format dataset-entropy expects."""
    input_text = pair.get("input") or ""
    output = pair.get("output") or {}
    if isinstance(output, dict):
        # Render the parsed assignment dict back to readable JSON string
        output_text = json.dumps(output, sort_keys=True)
    else:
        output_text = str(output)
    return {
        "messages": [
            {"role": "user", "content": input_text},
            {"role": "assistant", "content": output_text},
        ]
    }


def materialize_corpus_jsonl(
    out_path: Path,
    base: Optional[Path] = None,
    tiers: Optional[List[str]] = None,
) -> int:
    """Walk the SwarmJelly corpus and write a single JSONL of chat-format pairs."""
    base = base or corpus_dir()
    tiers = tiers or DEFAULT_TIERS
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for tier in tiers:
            td = base / tier
            if not td.exists():
                continue
            for p in sorted(td.iterdir()):
                if p.suffix != ".json":
                    continue
                try:
                    pair = orjson.loads(p.read_bytes())
                except Exception:
                    continue
                f.write(json.dumps(_pair_to_chat(pair)) + "\n")
                count += 1
    return count


def run_entropy_report(
    base: Optional[Path] = None,
    tiers: Optional[List[str]] = None,
    work_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Materialize the corpus into JSONL · analyze · capture printed report as string.

    Returns the printed report (text) plus the materialized path and pair count.
    """
    base = base or corpus_dir()
    work_dir = work_dir or (base / ".entropy")
    work_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = work_dir / "corpus.jsonl"
    n = materialize_corpus_jsonl(jsonl_path, base=base, tiers=tiers)

    if n == 0:
        return {
            "pairs": 0,
            "corpus_jsonl": str(jsonl_path),
            "report": "(empty corpus · no pairs to analyze)",
        }

    report_data = entropy_report(str(jsonl_path))
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_report(report_data, use_color=False)
    return {
        "pairs": n,
        "corpus_jsonl": str(jsonl_path),
        "report": buf.getvalue(),
        "data": report_data,
    }
