"""Приложение FastAPI, обслуживающее Telegram Mini App (см. plan.md, Project Structure)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.game import router as game_router
from src.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Electronics Store Promo Game API")
    app.include_router(game_router)
    # Разрешаем только localhost/127.0.0.1 — фронтенд Mini App в проде обслуживается тем же
    # доменом/хостингом, что и ожидает Telegram; это правило нужно только для локальной
    # разработки, когда frontend и backend подняты на разных портах на машине разработчика.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


app = create_app()
