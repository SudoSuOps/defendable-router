from pathlib import Path

import orjson

from defendablerouter.core.swarmjelly import build_pair, corpus_stats, write_pair
from defendablerouter.schemas.router_event import RouterEvent
from defendablerouter.schemas.verdict import RubricScores, Verdict

EXAMPLE = Path(__file__).resolve().parents[1] / "defendablerouter" / "examples" / "sample_event.json"


def _event() -> RouterEvent:
    return RouterEvent.model_validate(orjson.loads(EXAMPLE.read_bytes()))


def _verdict(tier: str | None) -> Verdict:
    return Verdict(
        verdict_id="TRIB-test",
        receipt_id="DRR-test",
        assignment_id="ASSIGN-test",
        status="GRADED" if tier else "SKIPPED",
        tier=tier,  # type: ignore[arg-type]
        rubric_scores=RubricScores(accuracy=4.6, cre_judgment=4.5, format=4.7, score=4.6) if tier else None,
        created_at="2026-05-24T00:00:00Z",
    )


def test_pair_built_when_verdict_has_tier():
    pair = build_pair(_event(), _verdict("apex"))
    assert pair is not None
    assert pair.tier == "apex"
    assert pair.input == _event().raw_client_language
    assert pair.output["assignment_type"] == "board_proposal"
    assert pair.pair_sha256 and len(pair.pair_sha256) == 64


def test_no_pair_when_verdict_skipped():
    pair = build_pair(_event(), _verdict(None))
    assert pair is None


def test_pair_writes_to_tier_dir_and_appends_corpus_index(tmp_path: Path):
    pair = build_pair(_event(), _verdict("honey"))
    assert pair is not None
    path = write_pair(pair, base=tmp_path)
    assert path.parent.name == "honey"
    assert path.exists()
    idx = (tmp_path / "corpus_index.jsonl").read_text().strip().splitlines()
    assert len(idx) == 1
    entry = orjson.loads(idx[0])
    assert entry["pair_id"] == pair.pair_id
    assert entry["tier"] == "honey"


def test_corpus_stats_counts_per_tier(tmp_path: Path):
    for t in ["apex", "apex", "honey", "jelly", "pollen", "propolis"]:
        p = build_pair(_event(), _verdict(t))
        assert p is not None
        write_pair(p, base=tmp_path)
    s = corpus_stats(base=tmp_path)
    assert s["apex"] == 2
    assert s["honey"] == 1
    assert s["jelly"] == 1
    assert s["pollen"] == 1
    assert s["propolis"] == 1
    assert s["total"] == 6
