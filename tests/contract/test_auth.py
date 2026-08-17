"""Тест отклонения запросов с невалидной/поддельной подписью initData (401)."""

from tests.conftest import make_init_data


def test_missing_authorization_header_returns_401(client):
    response = client.get("/api/game/status")

    assert response.status_code == 401


def test_malformed_authorization_scheme_returns_401(client):
    response = client.get("/api/game/status", headers={"Authorization": "Bearer something"})

    assert response.status_code == 401


def test_tampered_init_data_returns_401(client):
    valid = make_init_data(999, bot_token="test-bot-token")
    tampered = valid.replace("999", "998")  # подмена user id без пересчёта подписи

    response = client.get("/api/game/status", headers={"Authorization": f"tma {tampered}"})

    assert response.status_code == 401


def test_init_data_signed_with_wrong_bot_token_returns_401(client):
    forged = make_init_data(999, bot_token="attacker-controlled-token")

    response = client.get("/api/game/status", headers={"Authorization": f"tma {forged}"})

    assert response.status_code == 401


def test_trailing_space_trimmed_empty_init_data_returns_401_not_500(client):
    """Регрессия: HTTP-инфраструктура вправе обрезать конечный пробел у значения заголовка
    (RFC 7230, OWS), из-за чего 'tma ' с пустым initData на проводе превращается в 'tma' без
    пробела — подтверждено curl'ом против прод-бэкенда. Должно давать понятный 401, не падать."""
    response = client.get("/api/game/status", headers={"Authorization": "tma"})

    assert response.status_code == 401
    assert response.json()["detail"] == "missing tma authorization"


def test_scheme_is_case_insensitive(client):
    valid = make_init_data(999, bot_token="test-bot-token")

    response = client.get("/api/game/status", headers={"Authorization": f"TMA {valid}"})

    assert response.status_code == 200
