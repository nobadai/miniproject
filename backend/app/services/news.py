"""news.py
레이어: Services
역할: 뉴스 원문과 한 줄 요약, 감성 판정 근거를 하나의 조회 결과로 합친다.
"""

from collections import defaultdict

from ..repositories import news_article as news_article_repository
from ..schemas.news import KST, News, NewsEvidence


def build_news_list(articles: list[dict], evidences: list[dict]) -> list[News]:
    """기사 목록에 근거 문장을 기사별로 묶어 붙인다."""

    grouped: dict[int, list[NewsEvidence]] = defaultdict(list)
    for evidence in evidences:
        grouped[evidence["article_id"]].append(
            NewsEvidence(
                sentence=evidence["sentence"],
                is_quote=evidence["is_quote"],
            )
        )

    return [
        News(
            market_date=article["market_date"],
            brief_type=article["brief_type"],
            title=article["title"],
            # market_date 가 KST 기준이므로 게시시각도 같은 기준으로 맞춘다.
            # Driver 가 돌려주는 UTC 를 그대로 내보내면 날짜가 하루 어긋날 수 있다.
            published_at=article["published_at"].astimezone(KST),
            url=article["url"],
            source=article["source"],
            body=article["body"],
            summary=article["summary"],
            label=article["label"],
            evidence=grouped.get(article["id"], []),
        )
        for article in articles
    ]


def read_news() -> list[News]:
    """전체 뉴스를 요약·판정과 함께 최신순으로 조회한다."""

    articles = news_article_repository.find_news()
    if not articles:
        return []

    evidences = news_article_repository.find_verified_evidences()
    return build_news_list(articles, evidences)
