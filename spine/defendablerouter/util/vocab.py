"""Canonical Defendable vocabulary loader + density scorer.

Sources canonical CRE/DefendableOS vocabulary from defend-A-pedia--vocabulary
(via a bundled compact JSON shipped in defendablerouter/data/). Scores arbitrary
text on vocab-density: how many canonical surface forms appear per total tokens.

Used by the Tribunal grading rail to nudge intakes:
  * High vocab density + CRE-shaped assignment → operator-grade signal → honey/apex
  * Low vocab density + CRE-claiming assignment → likely propolis · repair lift fuel
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

VOCAB_PATH_ENV = "DEFENDABLE_VOCAB_PATH"
_DEFAULT_RESOURCE = ("defendablerouter.data", "canonical_vocab.json")
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z]+)?")


@dataclass(frozen=True)
class VocabHit:
    slug: str
    surface: str
    span: Tuple[int, int]  # (start_char, end_char)


@dataclass
class VocabScore:
    density: float                          # 0.0–1.0 · matched-tokens / total-content-tokens
    hits: List[VocabHit] = field(default_factory=list)
    terms_seen: List[str] = field(default_factory=list)  # unique slugs
    total_tokens: int = 0
    matched_tokens: int = 0


@lru_cache(maxsize=1)
def load_vocab() -> Dict[str, Dict]:
    """Load canonical vocab · env override → packaged resource."""
    path_env = os.environ.get(VOCAB_PATH_ENV)
    if path_env:
        p = Path(path_env)
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    try:
        with resources.files(_DEFAULT_RESOURCE[0]).joinpath(_DEFAULT_RESOURCE[1]).open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        pkg_dir = Path(__file__).resolve().parent.parent
        fallback = pkg_dir / "data" / "canonical_vocab.json"
        if fallback.exists():
            return json.loads(fallback.read_text(encoding="utf-8"))
    return {"terms": [], "term_count": 0}


@lru_cache(maxsize=1)
def alias_index() -> List[Tuple[str, str]]:
    """Return [(alias_lower, slug)] sorted by alias length descending (longest match wins)."""
    vocab = load_vocab()
    pairs: List[Tuple[str, str]] = []
    for term in vocab.get("terms", []):
        slug = term.get("slug")
        if not slug:
            continue
        seen_aliases: Set[str] = set()
        for alias in term.get("aliases", []) or []:
            a = (alias or "").strip().lower()
            if a and a not in seen_aliases:
                pairs.append((a, slug))
                seen_aliases.add(a)
        # Also try the slug itself with hyphens replaced by spaces
        slug_phrase = slug.replace("-", " ").strip().lower()
        if slug_phrase and slug_phrase not in seen_aliases:
            pairs.append((slug_phrase, slug))
    pairs.sort(key=lambda p: -len(p[0]))
    return pairs


def score_text(text: str) -> VocabScore:
    """Compute vocab density on free-form text.

    Tokenization is whitespace+alphanumeric. Alias matching is case-insensitive
    substring on the lowercase text; we greedy-match the longest alias first
    so multi-word terms (e.g. "single tenant net lease") win over single-word
    fragments.
    """
    s = (text or "").lower()
    tokens = _TOKEN_RE.findall(s)
    total = len(tokens)
    result = VocabScore(density=0.0, total_tokens=total)
    if total == 0:
        return result

    # Mask-as-we-match so the same span doesn't double count
    mask = [False] * len(s)
    seen_slugs: Set[str] = set()
    for alias, slug in alias_index():
        start = 0
        L = len(alias)
        while True:
            i = s.find(alias, start)
            if i == -1:
                break
            # Require token boundaries
            before_ok = (i == 0) or (not s[i - 1].isalnum())
            after_ok = (i + L == len(s)) or (not s[i + L].isalnum())
            if before_ok and after_ok and not any(mask[i : i + L]):
                for j in range(i, i + L):
                    mask[j] = True
                result.hits.append(VocabHit(slug=slug, surface=s[i : i + L], span=(i, i + L)))
                seen_slugs.add(slug)
            start = i + L

    # Recount tokens that fall entirely inside masked regions
    matched = 0
    for m in _TOKEN_RE.finditer(s):
        i, j = m.span()
        if all(mask[i:j]):
            matched += 1
    result.matched_tokens = matched
    result.terms_seen = sorted(seen_slugs)
    result.density = matched / total if total else 0.0
    return result


def known_slug(s: str) -> bool:
    return any(t.get("slug") == s for t in load_vocab().get("terms", []))


def term_count() -> int:
    return int(load_vocab().get("term_count") or len(load_vocab().get("terms", [])))
