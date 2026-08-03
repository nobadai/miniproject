"""JWT access token과 인증 쿠키 처리를 제공한다."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Response
from jwt.exceptions import InvalidTokenError

from .config import settings


ACCESS_TOKEN_COOKIE_NAME = "access_token"
ACCESS_TOKEN_COOKIE_PATH = "/"
ACCESS_TOKEN_COOKIE_SAMESITE = "lax"


class InvalidAccessTokenError(ValueError):
    """JWT가 없거나 유효하지 않을 때 발생한다."""


def create_access_token(user_id: int) -> str:
    """사용자 ID를 subject로 갖는 access token을 생성한다."""

    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """access token의 서명과 만료시간을 검증한다."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except InvalidTokenError as error:
        raise InvalidAccessTokenError from error

    if not isinstance(payload.get("sub"), str):
        raise InvalidAccessTokenError
    return payload


def _use_secure_cookie() -> bool:
    """Local과 Test 이외 환경에서 Secure 쿠키를 사용한다."""

    return settings.app_env.lower() not in {"local", "test"}


def set_access_token_cookie(response: Response, token: str) -> None:
    """JWT를 HttpOnly 인증 쿠키에 저장한다."""

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        httponly=True,
        secure=_use_secure_cookie(),
        samesite=ACCESS_TOKEN_COOKIE_SAMESITE,
        path=ACCESS_TOKEN_COOKIE_PATH,
    )


def delete_access_token_cookie(response: Response) -> None:
    """로그인 때와 동일한 속성을 사용해 인증 쿠키를 삭제한다."""

    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=_use_secure_cookie(),
        samesite=ACCESS_TOKEN_COOKIE_SAMESITE,
        path=ACCESS_TOKEN_COOKIE_PATH,
    )
