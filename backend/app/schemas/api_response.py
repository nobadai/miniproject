"""공통 API 응답 계약을 정의한다.

모든 API 응답이 공유하는 성공 여부, 데이터, 메시지 구조를 제공한다.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel


response_data_type = TypeVar("response_data_type")


class ApiResponse(BaseModel, Generic[response_data_type]):
    """모든 API Endpoint에서 사용하는 공통 응답 구조이다."""

    success: bool
    data: response_data_type | None = None
    message: str | None = None
