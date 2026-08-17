"""Единая точка получения текущего времени (наивный UTC — для совместимости с SQLite)."""

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
