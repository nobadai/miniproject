"""news.py
레이어: Routers
역할: 뉴스 조회(news) 기능의 Endpoint를 정의한다.
      파일명(news.py) 기준으로 `/news` Prefix가 자동 등록된다.
"""

from fastapi import APIRouter

from ..schemas.api_response import ApiResponse
from ..schemas.news import News
from ..services import news as news_service


router = APIRouter()


@router.get("", response_model=ApiResponse[list[News]])
def read_news() -> ApiResponse[list[News]]:
    """수집한 뉴스를 한 줄 요약, 감성 판정, 근거와 함께 최신순으로 반환한다."""

    news = news_service.read_news()

    return ApiResponse(
        success=True,
        data=news,
        message="요청이 정상적으로 처리되었습니다.",
    )
