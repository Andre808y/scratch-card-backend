"""Проверка Telegram Mini App initData (см. contracts/api.md, раздел «Аутентификация»)."""

import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException, status

from src.config import settings

_INIT_DATA_MAX_AGE_SECONDS = 24 * 60 * 60


class AuthenticatedPlayer:
    def __init__(self, telegram_id: int) -> None:
        self.telegram_id = telegram_id


def _compute_hash(data_check_string: str, bot_token: str) -> str:
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()


def validate_init_data(init_data: str, bot_token: str) -> int:
    """Валидирует подпись initData и возвращает telegram_id пользователя.

    Поднимает ValueError при отсутствующей/невалидной подписи или истёкшем auth_date.
    """
    pairs = dict(parse_qsl(init_data, strict_parsing=False))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise ValueError("missing hash")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(pairs.items()))
    expected_hash = _compute_hash(data_check_string, bot_token)
    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("invalid signature")

    auth_date = pairs.get("auth_date")
    if auth_date is not None and time.time() - int(auth_date) > _INIT_DATA_MAX_AGE_SECONDS:
        raise ValueError("init data expired")

    user_raw = pairs.get("user")
    if not user_raw:
        raise ValueError("missing user")
    user = json.loads(user_raw)
    telegram_id = user.get("id")
    if telegram_id is None:
        raise ValueError("missing user id")
    return int(telegram_id)


async def get_authenticated_player(authorization: str = Header(default="")) -> AuthenticatedPlayer:
    """FastAPI-зависимость: требует заголовок `Authorization: tma <initData>`.

    Разбор через partition(), а не жёсткое сравнение с префиксом "tma " — HTTP-инфраструктура
    (прокси, ASGI-сервер) вправе обрезать конечный пробел у значения заголовка (RFC 7230, OWS),
    из-за чего "tma " с пустым initData на проводе превращается в "tma" без пробела и ломает
    сравнение через startswith("tma ").
    """
    scheme, _, init_data = authorization.partition(" ")
    if scheme.lower() != "tma" or not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing tma authorization"
        )

    try:
        telegram_id = validate_init_data(init_data, settings.bot_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return AuthenticatedPlayer(telegram_id=telegram_id)
