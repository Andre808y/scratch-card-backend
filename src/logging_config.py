"""Структурированное (JSON) логирование ключевых игровых событий (см. research.md, п. 9)."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

_LOGGER_NAME = "promo_game"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def get_logger() -> logging.Logger:
    configure_logging()
    return logging.getLogger(_LOGGER_NAME)


def log_event(event: str, **fields: Any) -> None:
    """Логирует игровое событие с произвольными структурированными полями.

    Пример: log_event("session_started", player_id=123, session_id="…")
    """
    get_logger().info(event, extra={"extra_fields": {"event": event, **fields}})
