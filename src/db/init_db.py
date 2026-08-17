"""Инициализация схемы БД: создаёт все таблицы, зарегистрированные в Base.metadata."""

from src.db import session as db_session
from src.db.base import Base

# Импорт моделей нужен, чтобы они зарегистрировались в Base.metadata до create_all.
from src.models import GameSession, Player, Prize, PrizePool  # noqa: F401


def init_db() -> None:
    # db_session.engine читается динамически (через модуль, а не прямым импортом имени), чтобы
    # тестовый фикстурный monkeypatch db_session.engine подхватывался и при вызове через
    # FastAPI startup-хук (см. src/api/app.py), а не только при прямом вызове init_db().
    Base.metadata.create_all(bind=db_session.engine)


if __name__ == "__main__":
    init_db()
