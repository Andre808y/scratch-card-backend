"""Unit-тест взвешенного розыгрыша приза (FR-004, FR-010)."""

import random

from src.models.prize import Prize, PrizeStatus
from src.models.prize_pool import PrizePool
from src.services.prize_selection import select_prize


def _pool(no_win_weight: float, prizes: list[Prize]) -> PrizePool:
    pool = PrizePool(active_from=None, active_until=None, no_win_weight=no_win_weight)
    pool.prizes = prizes
    return pool


def test_guaranteed_win_when_no_win_weight_is_zero():
    prize = Prize(discount_value="10%", weight=1.0, status=PrizeStatus.AVAILABLE_IN_POOL)
    pool = _pool(no_win_weight=0.0, prizes=[prize])

    result = select_prize(pool, random.Random(1))

    assert result is prize


def test_guaranteed_no_win_when_pool_has_no_prizes():
    pool = _pool(no_win_weight=1.0, prizes=[])

    result = select_prize(pool, random.Random(1))

    assert result is None


def test_ignores_prizes_that_are_not_available():
    issued_prize = Prize(discount_value="10%", weight=1.0, status=PrizeStatus.ISSUED)
    pool = _pool(no_win_weight=0.0, prizes=[issued_prize])

    result = select_prize(pool, random.Random(1))

    assert result is None


def test_distribution_respects_weights_over_many_draws():
    heavy = Prize(discount_value="heavy", weight=99.0, status=PrizeStatus.AVAILABLE_IN_POOL)
    light = Prize(discount_value="light", weight=1.0, status=PrizeStatus.AVAILABLE_IN_POOL)
    pool = _pool(no_win_weight=0.0, prizes=[heavy, light])
    rng = random.Random(42)

    outcomes = [select_prize(pool, rng) for _ in range(500)]

    assert outcomes.count(heavy) > outcomes.count(light)
