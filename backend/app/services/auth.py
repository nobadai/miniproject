"""회원가입과 로그인 흐름을 처리한다."""

from typing import Any

from psycopg.errors import UniqueViolation

from ..core.security import (
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
)
from ..repositories import users as user_repository
from ..schemas.auth import LoginRequest, SignupRequest


class DuplicateEmailError(ValueError):
    """이미 가입된 이메일로 회원가입을 요청했을 때 발생한다."""


class InvalidCredentialsError(ValueError):
    """이메일 또는 비밀번호가 로그인 정보와 일치하지 않을 때 발생한다."""


class AuthenticationRequiredError(ValueError):
    """유효한 토큰에 대응하는 활성 사용자가 없을 때 발생한다."""


def signup(request: SignupRequest) -> dict[str, Any]:
    """이메일 중복을 확인하고 새 사용자를 생성한다."""

    email = str(request.email)
    if user_repository.find_user_id_by_email(email) is not None:
        raise DuplicateEmailError

    try:
        return user_repository.create_user(
            email=email,
            password=request.password.get_secret_value(),
            name=request.name,
        )
    except UniqueViolation as error:
        raise DuplicateEmailError from error


def login(request: LoginRequest) -> tuple[dict[str, Any], str]:
    """로그인 정보를 검증하고 사용자와 JWT를 반환한다."""

    user = user_repository.find_active_user_by_email(str(request.email))
    # TODO(security): 프로토타입 종료 전 안전한 비밀번호 해시 검증으로 전환한다.
    if user is None or user["password"] != request.password.get_secret_value():
        raise InvalidCredentialsError

    public_user = {key: value for key, value in user.items() if key != "password"}
    return public_user, create_access_token(int(user["id"]))


def get_authenticated_user(access_token: str) -> dict[str, Any]:
    """JWT를 검증하고 토큰에 대응하는 활성 사용자를 반환한다."""

    try:
        payload = decode_access_token(access_token)
        user_id = int(payload["sub"])
    except (InvalidAccessTokenError, KeyError, TypeError, ValueError) as error:
        raise AuthenticationRequiredError from error

    user = user_repository.find_active_user_by_id(user_id)
    if user is None:
        raise AuthenticationRequiredError
    return user
