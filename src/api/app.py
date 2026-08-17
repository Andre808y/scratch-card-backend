"""Приложение FastAPI, обслуживающее Telegram Mini App (см. plan.md, Project Structure)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.debug import router as debug_router
from src.api.routes.game import router as game_router
from src.config import settings
from src.db.init_db import init_db
from src.logging_config import configure_logging


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # SQLite-схема создаётся автоматически при каждом старте приложения (idempotent —
    # create_all создаёт только отсутствующие таблицы), отдельный шаг деплоя не нужен.
    init_db()
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Electronics Store Promo Game API", lifespan=_lifespan)
    app.include_router(game_router)
    app.include_router(debug_router)  # TODO(debug): временный, см. routes/debug.py

    # localhost/127.0.0.1 — всегда (локальная разработка, frontend и backend на разных портах).
    # settings.frontend_origin (FRONTEND_ORIGIN) — прод-домен статического хостинга фронтенда,
    # например https://<user>.github.io, когда frontend и backend на разных доменах.
    allow_origins = [settings.frontend_origin] if settings.frontend_origin else []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
