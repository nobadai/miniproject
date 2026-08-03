"""news_article.py
레이어: Repositories
역할: 수집한 시황 기사 원문에 대한 Pure SQL 접근을 제공한다.
"""

import logging
from collections.abc import Iterable

import psycopg

from ..schemas.news import NewsArticle
from .db import find_all, get_connection


logger = logging.getLogger(__name__)


FIND_EXISTING_URLS_SQL = """
SELECT url
FROM news_articles
WHERE url = ANY(%s)
"""

# url 이 UNIQUE 이므로 이미 수집한 기사는 조용히 건너뛴다.
# 본문을 덮어쓰면 그 기사에 붙은 감성 판정의 근거 검증이 무효가 되므로 갱신하지 않는다.
INSERT_ARTICLE_SQL = """
INSERT INTO news_articles (
    url, title, body, source, published_at, market_date, brief_type, collected_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (url) DO NOTHING
"""


# 요약·판정이 아직 없는 기사도 목록에 나와야 하므로 LEFT JOIN 으로 잇는다.
FIND_NEWS_SQL = """
SELECT a.id, a.url, a.title, a.body, a.source,
       a.published_at, a.market_date, a.brief_type,
       s.summary,
       t.label
FROM news_articles a
LEFT JOIN news_summaries s ON s.article_id = a.id AND s.status = 'done'
LEFT JOIN news_sentiments t ON t.article_id = a.id AND t.status = 'done'
ORDER BY a.market_date DESC, a.published_at DESC
"""

# verify_status 가 ok 가 아닌 근거는 환각이거나 의미가 뒤집힐 수 있어 화면에 내보내지 않는다.
FIND_VERIFIED_EVIDENCES_SQL = """
SELECT t.article_id, e.seq, e.sentence, e.is_quote
FROM news_sentiment_evidences e
JOIN news_sentiments t ON t.id = e.sentiment_id
WHERE e.verify_status = 'ok' AND t.status = 'done'
ORDER BY t.article_id, e.seq
"""


def find_news() -> list[dict]:
    """기사 원문에 한 줄 요약과 감성 판정을 붙여 최신순으로 반환한다."""

    return find_all(FIND_NEWS_SQL)


def find_verified_evidences() -> list[dict]:
    """화면에 내보낼 수 있는 근거 문장을 기사별 순서대로 반환한다."""

    return find_all(FIND_VERIFIED_EVIDENCES_SQL)


def find_existing_urls(urls: list[str]) -> set[str]:
    """주어진 URL 가운데 이미 적재된 것만 골라 반환한다."""

    if not urls:
        return set()

    rows = find_all(FIND_EXISTING_URLS_SQL, (list(urls),))
    return {row["url"] for row in rows}


def save_articles(articles: Iterable[NewsArticle]) -> int:
    """새 기사를 한 Transaction으로 적재하고 실제 적재 건수를 반환한다."""

    records = list(articles)
    if not records:
        return 0

    inserted = 0
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for article in records:
                cursor.execute(
                    INSERT_ARTICLE_SQL,
                    (
                        str(article.url),
                        article.title,
                        article.body,
                        article.source,
                        article.published_at,
                        article.market_date,
                        article.brief_type,
                        article.collected_at,
                    ),
                )
                inserted += cursor.rowcount
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        logger.exception("시황 기사 적재 실패")
        raise
    finally:
        connection.close()

    return inserted
