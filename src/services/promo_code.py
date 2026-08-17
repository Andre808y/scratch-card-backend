"""Генерация уникального промокода на скидку (FR-006)."""

import secrets
import string

_ALPHABET = string.ascii_uppercase + string.digits
_CODE_LENGTH = 8
_PREFIX = "STORE"


def generate_code() -> str:
    suffix = "".join(secrets.choice(_ALPHABET) for _ in range(_CODE_LENGTH))
    return f"{_PREFIX}-{suffix}"
