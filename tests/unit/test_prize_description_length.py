"""Регрессия: discount_value был VARCHAR(32), но реальные физические призы — свободный текст
длиннее 32 символов. На SQLite это молча проходило (длина VARCHAR не enforced), но упало на
Postgres/Neon с StringDataRightTruncation при первом реальном сиде продакшен-каталога.

SQLite не проверяет длину VARCHAR ни при каких условиях, поэтому тест сравнивает длину реальных
описаний призов напрямую с длиной, объявленной в модели (что и проверяет Postgres по-настоящему),
а не полагается на факт успешной вставки в SQLite.
"""

from src.db.seed_prizes import PRIZE_TEMPLATES
from src.models.prize import Prize


def test_discount_value_column_fits_all_seeded_prize_descriptions():
    column = Prize.__table__.columns["discount_value"]
    max_length = column.type.length

    for description, _weight in PRIZE_TEMPLATES:
        assert len(description) <= max_length, (
            f"{description!r} ({len(description)} символов) не помещается в "
            f"discount_value VARCHAR({max_length})"
        )


def test_discount_value_column_has_headroom_for_future_prize_text():
    # Не только текущие три приза, но и разумный запас на будущие более длинные описания.
    column = Prize.__table__.columns["discount_value"]
    assert column.type.length >= 200
