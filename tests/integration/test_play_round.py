"""Интеграционный тест: полный раунд start → reveal → результат (User Story 1, quickstart.md)."""

from src.db.session import session_scope
from src.models import Prize, PrizePool
from src.time_utils import utcnow


def _seed_mixed_pool():
    with session_scope() as db:
        pool = PrizePool(
            active_from=utcnow(),
            active_until=None,
            no_win_weight=1.0,
        )
        db.add(pool)
        db.flush()
        db.add(Prize(prize_pool_id=pool.id, discount_value="5%", weight=1.0))


def test_full_round_journey_completes_and_shows_result(client, auth_headers):
    """Пользователь запускает игру, раскрывает карту и сразу видит результат (SC-001)."""
    _seed_mixed_pool()
    headers = auth_headers(555)

    create_response = client.post("/api/game/sessions", headers=headers)
    assert create_response.status_code == 201
    session_id = create_response.json()["session_id"]

    reveal_response = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)
    assert reveal_response.status_code == 200

    body = reveal_response.json()
    assert body["outcome"] in {"win", "no_win"}
    if body["outcome"] == "win":
        assert body["prize"]["code"]
    else:
        assert "next_eligible_at" in body


def test_no_prize_available_falls_back_to_no_win(client, auth_headers):
    """FR-010: если призовой фонд пуст, система не предлагает несуществующий приз."""
    with session_scope() as db:
        db.add(
            PrizePool(
                active_from=utcnow(),
                active_until=None,
                no_win_weight=1.0,
            )
        )
    headers = auth_headers(666)

    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
    body = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers).json()

    assert body["outcome"] == "no_win"
