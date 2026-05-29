from defendable_router.core.pricing import estimate_compute_cost


def test_rtx6000_two_hour_quote_math():
    assert estimate_compute_cost("rtx6000_blackwell_96gb", 2) == 10


def test_5090_three_hour_quote_math():
    assert estimate_compute_cost("rog_astral_5090_32gb", 3) == 6
