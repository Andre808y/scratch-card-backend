"""Unit-тесты переходов статуса Prize (available_in_pool → issued → used/expired)."""

from datetime import timedelta

import pytest

from src.models.prize import Prize, PrizeStatus
from src.services.prize_lifecycle import InvalidPrizeTransition, mark_expired_if_due, mark_used
from src.time_utils import utcnow


def _issued_prize(expires_in_days: int = 30) -> Prize:
    now = utcnow()
    return Prize(
        discount_value="10%",
        status=PrizeStatus.ISSUED,
        code="STORE-TEST1234",
        issued_at=now,
        expires_at=now + timedelta(days=expires_in_days),
    )


def test_mark_used_transitions_issued_to_used():
    prize = _issued_prize()

    mark_used(prize, utcnow())

    assert prize.status == PrizeStatus.USED


def test_mark_used_rejects_prize_not_issued():
    prize = Prize(discount_value="10%", status=PrizeStatus.AVAILABLE_IN_POOL)

    with pytest.raises(InvalidPrizeTransition):
        mark_used(prize, utcnow())


def test_mark_used_after_expiry_transitions_to_expired_and_raises():
    prize = _issued_prize(expires_in_days=-1)

    with pytest.raises(InvalidPrizeTransition):
        mark_used(prize, utcnow())

    assert prize.status == PrizeStatus.EXPIRED


def test_mark_expired_if_due_transitions_when_past_expiry():
    prize = _issued_prize(expires_in_days=-1)

    changed = mark_expired_if_due(prize, utcnow())

    assert changed is True
    assert prize.status == PrizeStatus.EXPIRED


def test_mark_expired_if_due_no_op_when_not_yet_expired():
    prize = _issued_prize(expires_in_days=30)

    changed = mark_expired_if_due(prize, utcnow())

    assert changed is False
    assert prize.status == PrizeStatus.ISSUED
