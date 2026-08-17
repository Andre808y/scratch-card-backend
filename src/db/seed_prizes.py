"""Наполняет призовой фонд финальной прод-конфигурацией (см. spec.md, User Story 1/FR-004).

Три физических приза, выдаваемых продавцом лично по промокоду, без ограничения по количеству
(вероятность задаётся весом шаблона напрямую, без привязки к остатку — см. data-model.md):
- "Чехол в подарок при покупке телефона" — частый приз
- "Зарядный блок в подарок при покупке электроники" — частый приз, вес как у чехла
- "5 подарков при покупке" — редкий джекпот, вес в ~16 раз ниже частых призов

Идемпотентен: повторный запуск не создаёт дублирующие шаблоны (иначе вес приза удвоился бы),
если призы с такими же описаниями уже есть в активном пуле.
"""

from sqlalchemy import select

from src.db.session import session_scope
from src.models import Prize, PrizePool, PrizeStatus
from src.time_utils import utcnow

PRIZE_TEMPLATES = [
    ("Чехол в подарок при покупке телефона", 48.0),
    ("Зарядный блок в подарок при покупке электроники", 48.0),
    ("Джекпот: 5 подарков при покупке", 3.0),
]
NO_WIN_WEIGHT = 1.0  # суммарный шанс выигрыша любого из трёх призов = 99%


def seed_prizes() -> None:
    with session_scope() as db:
        pool = (
            db.execute(
                select(PrizePool).where(
                    PrizePool.active_from <= utcnow(),
                )
            )
            .scalars()
            .first()
        )

        if pool is None:
            pool = PrizePool(active_from=utcnow(), active_until=None, no_win_weight=NO_WIN_WEIGHT)
            db.add(pool)
            db.flush()
            print(f"Создан новый активный PrizePool {pool.id}")
        else:
            pool.no_win_weight = NO_WIN_WEIGHT
            print(f"Используется существующий активный PrizePool {pool.id}")

        existing_descriptions = {
            row.discount_value
            for row in db.execute(
                select(Prize).where(
                    Prize.prize_pool_id == pool.id,
                    Prize.status == PrizeStatus.AVAILABLE_IN_POOL,
                )
            ).scalars()
        }

        for description, weight in PRIZE_TEMPLATES:
            if description in existing_descriptions:
                print(f"  пропущено (уже есть): {description!r}")
                continue
            db.add(
                Prize(
                    prize_pool_id=pool.id,
                    discount_value=description,
                    weight=weight,
                    status=PrizeStatus.AVAILABLE_IN_POOL,
                )
            )
            print(f"  добавлено: {description!r} (вес {weight})")


if __name__ == "__main__":
    seed_prizes()
