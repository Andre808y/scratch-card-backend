"""Контрактный тест POST /api/game/sessions (см. contracts/api.md)."""

from src.db.session import session_scope
from src.models import PrizePool
from src.time_utils import utcnow


def _seed_prize_pool():
    with session_scope() as db:
        db.add(
            PrizePool(
                active_from=utcnow(),
                active_until=None,
                no_win_weight=1.0,
            )
        )


def test_create_session_returns_201_with_session_id(client, auth_headers):
    _seed_prize_pool()

    response = client.post("/api/game/sessions", headers=auth_headers(111))

    assert response.status_code == 201
    body = response.json()
    assert body.get("session_id")
    assert "started_at" in body


def test_create_session_requires_authentication(client):
    response = client.post("/api/game/sessions")

    assert response.status_code == 401
