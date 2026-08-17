"""Инициализация схемы БД: создаёт все таблицы, зарегистрированные в Base.metadata."""

from src.db.base import Base
from src.db.session import engine

# Импорт моделей нужен, чтобы они зарегистрировались в Base.metadata до create_all.
from src.models import GameSession, Player, Prize, PrizePool  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
