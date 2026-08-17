"""Контрактный тест конфликта POST /api/game/sessions при отсутствии права на попытку."""

from src.db.session import session_scope
from src.models import PrizePool
from src.time_utils import utcnow


def _seed_prize_pool():
    with session_scope() as db:
        db.add(PrizePool(active_from=utcnow(), active_until=None, no_win_weight=1.0))


def test_second_session_within_cooldown_returns_409(client, auth_headers):
    _seed_prize_pool()
    headers = auth_headers(201)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
    client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)

    response = client.post("/api/game/sessions", headers=headers)

    assert response.status_code == 409
    body = response.json()
    assert body["next_eligible_at"]


def test_repeated_create_before_reveal_returns_same_session(client, auth_headers):
    """Без раскрытия попытка не должна дублироваться (edge case: разрыв соединения)."""
    _seed_prize_pool()
    headers = auth_headers(202)

    first = client.post("/api/game/sessions", headers=headers).json()
    second = client.post("/api/game/sessions", headers=headers).json()

    assert first["session_id"] == second["session_id"]
