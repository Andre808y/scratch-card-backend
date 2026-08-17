"""Контрактный тест GET /api/game/status (см. contracts/api.md)."""

from src.db.session import session_scope
from src.models import PrizePool
from src.time_utils import utcnow


def _seed_prize_pool():
    with session_scope() as db:
        db.add(PrizePool(active_from=utcnow(), active_until=None, no_win_weight=1.0))


def test_status_eligible_for_new_player(client, auth_headers):
    response = client.get("/api/game/status", headers=auth_headers(101))

    assert response.status_code == 200
    body = response.json()
    assert body == {"eligible": True, "next_eligible_at": None, "active_session": None}


def test_status_reports_active_pending_session(client, auth_headers):
    _seed_prize_pool()
    headers = auth_headers(102)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]

    response = client.get("/api/game/status", headers=headers)

    body = response.json()
    assert body["eligible"] is True
    assert body["active_session"] == {"session_id": session_id, "outcome": "pending"}


def test_status_reports_ineligible_after_reveal(client, auth_headers):
    _seed_prize_pool()
    headers = auth_headers(103)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
    client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)

    response = client.get("/api/game/status", headers=headers)

    body = response.json()
    assert body["eligible"] is False
    assert body["next_eligible_at"] is not None
    assert body["active_session"] is None
