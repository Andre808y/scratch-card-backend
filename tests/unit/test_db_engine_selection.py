"""Unit-тест выбора СУБД по DATABASE_URL — без хардкода конкретного драйвера (см. src/db/session.py)."""

from src.db.session import connect_args_for


def test_sqlite_url_gets_check_same_thread_false():
    assert connect_args_for("sqlite:///./promo_game.db") == {"check_same_thread": False}


def test_sqlite_memory_url_gets_check_same_thread_false():
    assert connect_args_for("sqlite:///:memory:") == {"check_same_thread": False}


def test_postgresql_url_gets_no_extra_connect_args():
    assert connect_args_for("postgresql://user:pass@host:5432/dbname") == {}


def test_postgresql_psycopg2_url_gets_no_extra_connect_args():
    assert connect_args_for("postgresql+psycopg2://user:pass@host:5432/dbname") == {}
