"""Взвешенный розыгрыш приза из призового фонда (FR-004), включая исход no_win (FR-010)."""

import random

from src.models.prize import Prize, PrizeStatus
from src.models.prize_pool import PrizePool


def select_prize(pool: PrizePool, rng: random.Random) -> Prize | None:
    """Выбирает приз из пула по весам или возвращает None (исход «без выигрыша»).

    Учитывает только записи Prize со статусом available_in_pool и положительным весом
    (FR-010: нельзя выдать приз, которого фактически не осталось в пуле).
    """
    candidates = [
        prize
        for prize in pool.prizes
        if prize.status == PrizeStatus.AVAILABLE_IN_POOL and prize.weight > 0
    ]
    total_weight = sum(prize.weight for prize in candidates) + max(pool.no_win_weight, 0.0)
    if total_weight <= 0:
        return None

    roll = rng.uniform(0, total_weight)
    cumulative = 0.0
    for prize in candidates:
        cumulative += prize.weight
        if roll <= cumulative:
            return prize
    return None
