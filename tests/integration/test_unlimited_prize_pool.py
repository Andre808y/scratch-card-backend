"""Приз-шаблон в пуле не расходуется: вероятность задаётся весом, а не остатком (см.
сообщение пользователя от 2026-08-17: «без лимита… вероятности задаются напрямую без привязки
к остатку»)."""

from sqlalchemy import select

from src.db.session import session_scope
from src.models import Prize, PrizePool, PrizeStatus
from src.time_utils import utcnow


def _seed_guaranteed_win_template():
    with session_scope() as db:
        pool = PrizePool(active_from=utcnow(), active_until=None, no_win_weight=0.0)
        db.add(pool)
        db.flush()
        db.add(Prize(prize_pool_id=pool.id, discount_value="Чехол в подарок", weight=1.0))
        return pool.id


def test_same_prize_template_can_be_won_by_many_different_players(client, auth_headers):
    _seed_guaranteed_win_template()

    codes = set()
    for telegram_id in range(9001, 9006):  # 5 разных "игроков"
        headers = auth_headers(telegram_id)
        session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
        body = client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers).json()
        assert body["outcome"] == "win"
        codes.add(body["prize"]["code"])

    # Каждый выигрыш — свой уникальный промокод, ни одной ошибки/отказа из-за "исчерпания" приза.
    assert len(codes) == 5


def test_prize_template_row_is_never_consumed(client, auth_headers, db):
    pool_id = _seed_guaranteed_win_template()
    headers = auth_headers(9101)
    session_id = client.post("/api/game/sessions", headers=headers).json()["session_id"]
    client.post(f"/api/game/sessions/{session_id}/reveal", headers=headers)

    with db() as session:
        template = session.execute(
            select(Prize).where(Prize.prize_pool_id == pool_id, Prize.code.is_(None))
        ).scalar_one()
        assert template.status == PrizeStatus.AVAILABLE_IN_POOL

        issued_rows = (
            session.execute(
                select(Prize).where(Prize.prize_pool_id == pool_id, Prize.code.is_not(None))
            )
            .scalars()
            .all()
        )
        assert len(issued_rows) == 1
        assert issued_rows[0].status == PrizeStatus.ISSUED
