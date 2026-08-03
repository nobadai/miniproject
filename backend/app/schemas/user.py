"""사용자 정보 조회와 수정 API의 데이터 계약을 정의한다."""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


class UserResponse(BaseModel):
    """API 응답에 노출할 수 있는 사용자 정보이다."""

    id: int
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    """이름과 비밀번호를 선택적으로 수정하는 요청이다."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=100)
    current_password: SecretStr | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    new_password: SecretStr | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("이름은 공백일 수 없습니다.")
        return normalized

    @model_validator(mode="after")
    def validate_update_fields(self) -> "UserUpdateRequest":
        if self.name is None and self.new_password is None:
            raise ValueError("이름 또는 새 비밀번호 중 하나 이상이 필요합니다.")
        if self.new_password is None and self.current_password is not None:
            raise ValueError("새 비밀번호가 필요합니다.")
        if self.new_password is not None and self.current_password is None:
            raise ValueError("현재 비밀번호가 필요합니다.")
        if (
            self.current_password is not None
            and self.new_password is not None
            and self.current_password.get_secret_value()
            == self.new_password.get_secret_value()
        ):
            raise ValueError("새 비밀번호는 현재 비밀번호와 달라야 합니다.")
        return self


class UserDeleteRequest(BaseModel):
    """회원탈퇴 전 현재 비밀번호를 확인하는 요청이다."""

    model_config = ConfigDict(extra="forbid")

    password: SecretStr = Field(min_length=1, max_length=255)
