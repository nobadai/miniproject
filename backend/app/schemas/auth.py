"""회원가입과 로그인 API의 요청 데이터 계약을 정의한다."""

import re

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str) -> str:
    """이메일의 공백과 대소문자를 정규화하고 기본 형식을 검증한다."""

    normalized = value.strip().lower()
    if len(normalized) > 255 or EMAIL_PATTERN.fullmatch(normalized) is None:
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return normalized


class SignupRequest(BaseModel):
    """사용자 회원가입 요청이다."""

    model_config = ConfigDict(extra="forbid")

    email: str
    password: SecretStr = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("이름은 공백일 수 없습니다.")
        return normalized


class LoginRequest(BaseModel):
    """사용자 로그인 요청이다."""

    model_config = ConfigDict(extra="forbid")

    email: str
    password: SecretStr = Field(min_length=1, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)
