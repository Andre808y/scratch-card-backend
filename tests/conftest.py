"""Общие фикстуры тестов: изолированная in-memory БД и тестовый клиент с initData."""

import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import session as db_session
from src.db.base import Base

TEST_BOT_TOKEN = "test-bot-token"


def make_init_data(telegram_id: int, bot_token: str = TEST_BOT_TOKEN) -> str:
    """Строит валидный initData для тестового пользователя (см. src/api/auth.py)."""
    params = {
        "auth_date": str(int(time.time())),
        "user": json.dumps({"id": telegram_id, "first_name": "Test"}, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    params["hash"] = computed_hash
    return urlencode(params)


@pytest.fixture()
def db(monkeypatch):
    """Изолированная in-memory SQLite БД на каждый тест, с моками engine/SessionLocal."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", testing_session_local)

    yield testing_session_local

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def bot_token(monkeypatch):
    from src import config

    monkeypatch.setattr(config.settings, "bot_token", TEST_BOT_TOKEN)
    return TEST_BOT_TOKEN


@pytest.fixture()
def client(db, bot_token):
    from src.api.app import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(bot_token):
    def _headers(telegram_id: int) -> dict:
        return {"Authorization": f"tma {make_init_data(telegram_id, bot_token)}"}

    return _headers
