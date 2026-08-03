"""FastAPI Endpoint가 공통으로 사용하는 요청 의존성을 제공한다."""

from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException, status

from ..services import auth as auth_service


UNAUTHORIZED_DETAIL = "인증이 필요합니다."


def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> dict[str, Any]:
    """인증 쿠키를 현재 활성 사용자로 변환한다."""

    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
        )

    try:
        return auth_service.get_authenticated_user(access_token)
    except auth_service.AuthenticationRequiredError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=UNAUTHORIZED_DETAIL,
        ) from error


CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]
