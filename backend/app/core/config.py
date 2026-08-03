"""애플리케이션 환경설정 진입점이다.

Backend 환경변수를 검증하고 애플리케이션 전체에서 공유하는 Settings 객체를 제공한다.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """환경변수에서 읽어 검증한 애플리케이션 설정이다."""

    app_name: str = "finance-ai"
    app_env: str = "local"
    app_debug: bool = False

    postgres_host: str = Field(min_length=1)
    postgres_port: int
    postgres_db: str = Field(min_length=1)
    postgres_user: str = Field(min_length=1)
    postgres_password: SecretStr = Field(min_length=1)

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, gt=0)

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None

    stt_model_size: str = "large-v3-turbo"
    stt_device: str = "auto"
    stt_compute_type: str = "int8"
    stt_language: str = "ko"
    stt_telephony_band: bool = True
    stt_cache_directory: Path = BACKEND_ROOT / "cache" / "transcripts"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
settings = Settings()
