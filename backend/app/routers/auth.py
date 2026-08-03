"""회원가입, 로그인 및 로그아웃 Endpoint를 제공한다."""

from fastapi import APIRouter, HTTPException, Response, status

from ..core.security import delete_access_token_cookie, set_access_token_cookie
from ..schemas.api_response import ApiResponse
from ..schemas.auth import LoginRequest, SignupRequest
from ..schemas.user import UserResponse
from ..services import auth as auth_service


router = APIRouter()


@router.post(
    "/signup",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
def signup(request: SignupRequest) -> ApiResponse[UserResponse]:
    """새 사용자를 등록한다."""

    try:
        user = auth_service.signup(request)
    except auth_service.DuplicateEmailError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        ) from error

    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="회원가입이 완료되었습니다.",
    )


@router.post("/login", response_model=ApiResponse[UserResponse])
def login(
    request: LoginRequest,
    response: Response,
) -> ApiResponse[UserResponse]:
    """로그인 정보를 검증하고 HttpOnly 쿠키를 발급한다."""

    try:
        user, token = auth_service.login(request)
    except auth_service.InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        ) from error

    set_access_token_cookie(response, token)
    return ApiResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message="로그인되었습니다.",
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def logout() -> Response:
    """인증 쿠키를 삭제한다."""

    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    delete_access_token_cookie(response)
    return response
