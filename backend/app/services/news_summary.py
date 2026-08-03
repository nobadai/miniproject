"""금융 뉴스 한 줄 요약 비즈니스 흐름을 제공한다.

애플리케이션 설정으로 Gemini Client를 생성하고 원본 기사와 생성 메타데이터를
결합해 후속 저장·API 계층에서 사용할 NewsSummary를 반환한다.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from ..clients.gemini_summary_client import GeminiSummaryClient
from ..core.config import settings
from ..schemas.news import NewsArticle
from ..schemas.news_summary import NewsSummary


KST = ZoneInfo("Asia/Seoul")


def summarize_news_article(article: NewsArticle) -> NewsSummary:
    """원본 뉴스 한 건의 한 줄 요약과 생성 메타데이터를 반환한다."""

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")

    client = GeminiSummaryClient(
        api_key=settings.gemini_api_key.get_secret_value(),
        model=settings.gemini_model,
    )
    content = client.summarize(article)
    return NewsSummary(
        article_url=article.url,
        summary=content.summary,
        model=settings.gemini_model,
        summarized_at=datetime.now(KST).replace(microsecond=0),
    )
