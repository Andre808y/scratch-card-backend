"""Проверка validate_init_data против НЕЗАВИСИМОГО тестового вектора (не сгенерированного нашим
собственным make_init_data() — тот проверяет только самосогласованность, а не соответствие
реальному алгоритму Telegram).

Вектор взят из официальной документации экосистемы Telegram Mini Apps (пример из tma.js,
https://docs.telegram-mini-apps.com/packages/tma-js-init-data-node/validating) — публично
известный, воспроизводимый пример с реальным (тестовым) bot-токеном и реальным ожидаемым hash.
"""

from unittest.mock import patch

import pytest

from src.api.auth import validate_init_data

REFERENCE_BOT_TOKEN = "5768337691:AAH5YkoiEuPk8-FZa32hStHTqXiLPtAEhx8"
REFERENCE_AUTH_DATE = 1662771648
REFERENCE_INIT_DATA = (
    "query_id=AAHdF6IQAAAAAN0XohDhrOrc"
    "&user=%7B%22id%22%3A279058397%2C%22first_name%22%3A%22Vladislav%22%2C%22last_name%22"
    "%3A%22Kibenko%22%2C%22username%22%3A%22vdkfrost%22%2C%22language_code%22%3A%22ru%22%2C"
    "%22is_premium%22%3Atrue%7D"
    f"&auth_date={REFERENCE_AUTH_DATE}"
    "&hash=c501b71e775f74ce10e377dea85a7ea24ecd640b223ea86dfe453e0eaed2e2b2"
)


def test_reference_vector_validates_successfully():
    # auth_date этого примера — 2022 год, реально "просрочен" относительно текущего времени;
    # фиксируем time.time() рядом с ним, чтобы проверить именно корректность подписи, а не
    # маскировать её отдельной проверкой свежести (которая — намеренно отдельное условие).
    with patch("src.api.auth.time.time", return_value=REFERENCE_AUTH_DATE + 60):
        telegram_id = validate_init_data(REFERENCE_INIT_DATA, REFERENCE_BOT_TOKEN)

    assert telegram_id == 279058397


def test_reference_vector_fails_with_wrong_bot_token():
    with (
        patch("src.api.auth.time.time", return_value=REFERENCE_AUTH_DATE + 60),
        pytest.raises(ValueError, match="invalid signature"),
    ):
        validate_init_data(REFERENCE_INIT_DATA, REFERENCE_BOT_TOKEN + "x")
