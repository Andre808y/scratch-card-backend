"""Конфигурация окружения приложения (bot token, путь к БД)."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    bot_token: str
    database_url: str
    mini_app_url: str
    play_cooldown_hours: int = 24


def load_settings() -> Settings:
    bot_token = os.environ.get("BOT_TOKEN", "")
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./promo_game.db")
    mini_app_url = os.environ.get("MINI_APP_URL", "")
    cooldown_hours = int(os.environ.get("PLAY_COOLDOWN_HOURS", "24"))
    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        mini_app_url=mini_app_url,
        play_cooldown_hours=cooldown_hours,
    )


settings = load_settings()
