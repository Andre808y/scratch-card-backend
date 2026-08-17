"""TODO(debug): временный диагностический роут для продакшен-бага "invalid signature" — не
раскрывает сам BOT_TOKEN, только его длину/крайние символы/признаки лишних пробелов, чтобы
сравнить с ожидаемым значением от BotFather без доступа к переменным окружения на Render.
Убрать вместе с этим файлом и его регистрацией в app.py после того, как причина найдена.
"""

from fastapi import APIRouter

from src.config import settings

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/bot-token-info")
def bot_token_info() -> dict:
    token = settings.bot_token
    return {
        "length": len(token),
        "prefix_repr": repr(token[:3]),
        "suffix_repr": repr(token[-3:]) if len(token) >= 3 else repr(token),
        "has_leading_whitespace": token != token.lstrip(),
        "has_trailing_whitespace": token != token.rstrip(),
        "contains_newline": "\n" in token,
        "contains_carriage_return": "\r" in token,
        "contains_any_whitespace_inside": any(c.isspace() for c in token.strip()),
        "colon_count": token.count(":"),
    }
