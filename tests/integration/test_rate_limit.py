"""Интеграционный тест защиты от гонки при параллельных запросах (см. research.md, п. 6)."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from src.db.session import session_scope
from src.models import Prize, PrizePool
from src.time_utils import utcnow


def _seed_single_prize_pool():
    with session_scope() as db:
        pool = PrizePool(active_from=utcnow(), active_until=None, no_win_weight=0.0)
        db.add(pool)
        db.flush()
        db.add(Prize(prize_pool_id=pool.id, discount_value="10%", weight=1.0))


def test_concurrent_session_creation_does_not_duplicate_attempt(client, auth_headers):
    """Несколько параллельных запросов с одного аккаунта не должны создавать разные попытки
    и не должны выдавать больше одного приза за окно (edge case из spec.md)."""
    _seed_single_prize_pool()
    headers = auth_headers(301)

    def _create():
        return client.post("/api/game/sessions", headers=headers).json()["session_id"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        session_ids = list(pool.map(lambda _: _create(), range(8)))

    assert len(set(session_ids)) == 1


def test_second_attempt_blocked_until_cooldown_expires(client, auth_headers, db):
    _seed_single_prize_pool()
    headers = auth_headers(302)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
    client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)

    blocked = client.post("/api/game/sessions", headers=headers)
    assert blocked.status_code == 409

    # Симулируем истечение кулдауна, сдвигая next_eligible_at игрока в прошлое.
    from src.models import Player

    with session_scope() as session:
        player = session.get(Player, 302)
        player.next_eligible_at = utcnow() - timedelta(seconds=1)

    allowed = client.post("/api/game/sessions", headers=headers)
    assert allowed.status_code == 201
