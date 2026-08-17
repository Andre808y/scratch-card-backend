"""Контрактный тест POST /api/game/sessions/{id}/reveal (см. contracts/api.md)."""

from src.db.session import session_scope
from src.models import Prize, PrizePool
from src.time_utils import utcnow


def _seed_prize_pool_with_guaranteed_win():
    with session_scope() as db:
        pool = PrizePool(
            active_from=utcnow(),
            active_until=None,
            no_win_weight=0.0,
        )
        db.add(pool)
        db.flush()
        db.add(
            Prize(
                prize_pool_id=pool.id,
                discount_value="10%",
                weight=1.0,
            )
        )


def test_reveal_returns_prize_on_win(client, auth_headers):
    _seed_prize_pool_with_guaranteed_win()
    headers = auth_headers(222)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]

    response = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "win"
    assert body["prize"]["code"]
    assert body["prize"]["discount_value"] == "10%"
    assert body["prize"]["expires_at"]


def test_reveal_is_idempotent(client, auth_headers):
    _seed_prize_pool_with_guaranteed_win()
    headers = auth_headers(333)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]

    first = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers).json()
    second = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers).json()

    assert first == second


def test_reveal_unknown_session_returns_404(client, auth_headers):
    response = client.post("/api/game/sessions/does-not-exist/reveal", headers=auth_headers(444))

    assert response.status_code == 404
