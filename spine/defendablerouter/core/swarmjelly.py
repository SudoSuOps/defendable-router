from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

import orjson

from defendablerouter.core.canonicalize import canonicalize_for_hash
from defendablerouter.core.hash import sha256_bytes
from defendablerouter.core.ids import pair_id as new_pair_id, utc_now_iso
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.training_pair import TrainingPair
from defendablerouter.schemas.verdict import Tier, Verdict

PAIR_VOLATILE = {"created_at", "pair_sha256"}
DEFAULT_CORPUS_DIR = "data/swarmjelly"
CORPUS_INDEX = "corpus_index.jsonl"

TIERS: List[Tier] = ["apex", "honey", "jelly", "pollen", "propolis"]


def corpus_dir() -> Path:
    return Path(os.environ.get("SWARMJELLY_CORPUS_DIR", DEFAULT_CORPUS_DIR))


def _hash_pair(pair: TrainingPair) -> str:
    body = pair.model_dump(mode="json")
    return sha256_bytes(canonicalize_for_hash(body, PAIR_VOLATILE))


def build_pair(event: RouterEvent, verdict: Verdict) -> Optional[TrainingPair]:
    """Build a training pair from receipt input + assignment output + verdict tier.

    Returns None when the verdict has no tier (e.g., SKIPPED or FAILED grading).
    """
    if verdict.tier is None:
        return None

    pair = TrainingPair(
        pair_id=new_pair_id(),
        receipt_id=verdict.receipt_id,
        verdict_id=verdict.verdict_id,
        assignment_id=verdict.assignment_id,
        tier=verdict.tier,
        input=event.raw_client_language,
        output=event.assignment.model_dump(mode="json"),
        rubric_scores=verdict.rubric_scores,
        created_at=utc_now_iso(),
    )
    pair.pair_sha256 = _hash_pair(pair)
    return pair


def write_pair(pair: TrainingPair, base: Optional[Path] = None) -> Path:
    """Write the pair into data/swarmjelly/<tier>/<pair_id>.json and append the corpus index."""
    base = base or corpus_dir()
    tier_dir = base / pair.tier
    tier_dir.mkdir(parents=True, exist_ok=True)
    path = tier_dir / f"{pair.pair_id}.json"
    path.write_bytes(
        orjson.dumps(pair.model_dump(mode="json"), option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS)
    )

    base.mkdir(parents=True, exist_ok=True)
    idx = base / CORPUS_INDEX
    entry = {
        "pair_id": pair.pair_id,
        "receipt_id": pair.receipt_id,
        "verdict_id": pair.verdict_id,
        "tier": pair.tier,
        "path": str(path.relative_to(base)),
        "pair_sha256": pair.pair_sha256,
        "created_at": pair.created_at,
    }
    with open(idx, "a", encoding="utf-8") as f:
        f.write(orjson.dumps(entry, option=orjson.OPT_SORT_KEYS).decode("utf-8") + "\n")
        f.flush()
        os.fsync(f.fileno())
    return path


def corpus_stats(base: Optional[Path] = None) -> Dict[str, int]:
    base = base or corpus_dir()
    counts: Dict[str, int] = {t: 0 for t in TIERS}
    counts["total"] = 0
    if not base.exists():
        return counts
    for t in TIERS:
        td = base / t
        if td.exists():
            n = sum(1 for p in td.iterdir() if p.is_file() and p.suffix == ".json")
            counts[t] = n
            counts["total"] += n
    return counts
