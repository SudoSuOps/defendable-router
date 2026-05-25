from defendablerouter.util.vocab import alias_index, load_vocab, score_text, term_count


def test_vocab_loaded():
    v = load_vocab()
    assert v.get("term_count", 0) > 0
    assert len(v.get("terms", [])) > 0


def test_alias_index_includes_cre_anchors():
    pairs = dict((a, slug) for a, slug in alias_index())
    assert "1031" in pairs
    assert "cap rate" in pairs
    assert "noi" in pairs
    assert "dscr" in pairs


def test_score_empty_text():
    s = score_text("")
    assert s.density == 0.0
    assert s.total_tokens == 0
    assert s.terms_seen == []


def test_score_high_vocab_density_on_cre_intake():
    s = score_text(
        "ring ring · mr defendable here · ship the 1031 exchange flight sheet · "
        "5 cap STNL · NOI 145000 · DSCR 1.25 · WALT 10 years · cap rate locked"
    )
    assert s.density > 0.10
    assert "1031" in {h.surface for h in s.hits} or "1031-exchange" in s.terms_seen
    assert any(slug in s.terms_seen for slug in ("cap-rate", "noi", "dscr", "walt", "stnl"))


def test_score_zero_on_filler():
    s = score_text("uh yeah just do the thing whenever and send it")
    assert s.density == 0.0
    assert s.terms_seen == []


def test_score_partial_on_mixed():
    s = score_text("we need an underwriting memo with proper due diligence and a cap rate")
    assert 0.10 < s.density < 0.60
    assert "cap-rate" in s.terms_seen
    assert "underwriting" in s.terms_seen or "due-diligence" in s.terms_seen


def test_term_count_positive():
    assert term_count() >= 50
