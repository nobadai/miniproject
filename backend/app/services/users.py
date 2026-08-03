"""사용자 정보 수정과 회원탈퇴 흐름을 처리한다."""

from typing import Any

from ..repositories import users as user_repository
from ..schemas.user import UserDeleteRequest, UserUpdateRequest


def update_user(
    user_id: int,
    request: UserUpdateRequest,
) -> dict[str, Any]:
    """전달된 이름과 비밀번호를 하나의 트랜잭션에서 수정한다."""

    current_password = (
        request.current_password.get_secret_value()
        if request.current_password is not None
        else None
    )
    new_password = (
        request.new_password.get_secret_value()
        if request.new_password is not None
        else None
    )
    return user_repository.update_user(
        user_id,
        name=request.name,
        current_password=current_password,
        new_password=new_password,
    )


def delete_user(user_id: int, request: UserDeleteRequest) -> None:
    """현재 비밀번호를 확인하고 사용자를 소프트 삭제한다."""

    user_repository.soft_delete_user(
        user_id,
        request.password.get_secret_value(),
    )
