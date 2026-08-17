"""Переходы статуса Prize при погашении в магазине (см. data-model.md)."""

from datetime import datetime

from src.models.prize import Prize, PrizeStatus


class InvalidPrizeTransition(Exception):
    pass


def mark_used(prize: Prize, at: datetime) -> None:
    """available_in_pool → issued → used. Переводит в expired, если срок истёк."""
    if prize.status != PrizeStatus.ISSUED:
        raise InvalidPrizeTransition(f"cannot use prize with status {prize.status}")
    if prize.expires_at is not None and at > prize.expires_at:
        prize.status = PrizeStatus.EXPIRED
        raise InvalidPrizeTransition("prize has expired")
    prize.status = PrizeStatus.USED


def mark_expired_if_due(prize: Prize, at: datetime) -> bool:
    """Переводит issued-приз в expired, если истёк срок действия. Возвращает, был ли переход."""
    if (
        prize.status == PrizeStatus.ISSUED
        and prize.expires_at is not None
        and at > prize.expires_at
    ):
        prize.status = PrizeStatus.EXPIRED
        return True
    return False
