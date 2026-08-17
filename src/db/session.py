"""Настройка SQLAlchemy engine и управление сессиями БД.

Выбор СУБД определяется исключительно DATABASE_URL (без хардкода):
`sqlite://...` — локальная разработка (драйвер sqlite3 из stdlib);
`postgresql://...` — продакшен (требует psycopg2-binary, см. pyproject.toml).
"""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config import settings


def connect_args_for(database_url: str) -> dict:
    """SQLite требует check_same_thread=False для использования из разных потоков FastAPI
    (см. src/db/session.py: одна и та же сессия/engine используются threadpool-воркерами).
    Другим СУБД (PostgreSQL и т. д.) дополнительные connect_args не нужны."""
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


engine = create_engine(settings.database_url, connect_args=connect_args_for(settings.database_url))

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Транзакционная область видимости сессии: commit при успехе, rollback при ошибке."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Iterator[Session]:
    """FastAPI-зависимость, отдающая сессию БД на время запроса."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
