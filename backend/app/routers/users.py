"""현재 사용자 정보 조회, 수정 및 회원탈퇴 Endpoint를 제공한다."""

from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from ..core.security import (
    InvalidAccessTokenError,
    decode_access_token,
    delete_access_token_cookie,
)
from ..repositories import users as user_repository
from ..repositories.users import InvalidCurrentPasswordError, UserNotFoundError
from ..schemas.api_response import ApiResponse
from ..schemas.user import UserDeleteRequest, UserResponse, UserUpdateRequest
from ..services import users as user_service


router = APIRouter()
UNAUTHORIZED_DETAIL = "인증이 필요합니다."


def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> dict[str, Any]:
    """HttpOnly 쿠키의 JWT를 검증하고 활성 사용자를 반환한다."""

    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
        )

    try:
        payload = decode_access_token(access_token)
        user_id = int(payload["sub"])
    except (InvalidAccessTokenError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
        ) from error

    user = user_repository.find_active_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
        )
    return user


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(current_user: CurrentUser) -> ApiResponse[UserResponse]:
    """인증된 현재 사용자의 정보를 반환한다."""

    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(current_user),
        message="사용자 정보를 조회했습니다.",
    )


@router.patch("/me", response_model=ApiResponse[UserResponse])
def update_me(
    request: UserUpdateRequest,
    current_user: CurrentUser,
) -> ApiResponse[UserResponse]:
    """현재 사용자의 이름이나 비밀번호를 수정한다."""

    try:
        user = user_service.update_user(int(current_user["id"]), request)
    except InvalidCurrentPasswordError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 올바르지 않습니다.",
        ) from error
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
        ) from error

    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="사용자 정보가 수정되었습니다.",
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_me(
    request: UserDeleteRequest,
    current_user: CurrentUser,
) -> Response:
    """현재 사용자를 소프트 삭제하고 인증 쿠키를 제거한다."""

    try:
        user_service.delete_user(int(current_user["id"]), request)
    except InvalidCurrentPasswordError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="현재 비밀번호가 올바르지 않습니다.",
        ) from error
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다.",
        ) from error

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    delete_access_token_cookie(response)
    return response
