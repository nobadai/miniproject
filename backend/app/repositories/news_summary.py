"""news_summary.py
레이어: Repositories
역할: Gemini 한 줄 요약 결과 저장과 요약 대상 조회에 대한 Pure SQL 접근을 제공한다.
"""

import logging

from .db import find_all, find_one, save


logger = logging.getLogger(__name__)


# 요약 Row 가 없으면 미처리, failed 면 재시도 대상이다.
# 이 조건이 곧 배치의 처리 목록이므로 이미 요약된 기사는 배치가 아예 보지 않는다.
PENDING_CONDITION_SQL = """
FROM news_articles a
LEFT JOIN news_summaries s ON s.article_id = a.id
WHERE s.id IS NULL OR s.status = 'failed'
"""

FIND_PENDING_SQL = (
    """
SELECT a.id, a.url, a.title, a.body, a.source,
       a.published_at, a.brief_type, a.collected_at
"""
    + PENDING_CONDITION_SQL
    + """
ORDER BY a.market_date, a.published_at
"""
)

FIND_PENDING_WITH_LIMIT_SQL = FIND_PENDING_SQL + "LIMIT %s\n"

COUNT_PENDING_SQL = "SELECT count(*) AS pending" + PENDING_CONDITION_SQL

SAVE_SUMMARY_SQL = """
INSERT INTO news_summaries (article_id, status, error, summary, llm_model)
VALUES (%s, 'done', NULL, %s, %s)
ON CONFLICT (article_id) DO UPDATE
SET status = 'done',
    error = NULL,
    summary = EXCLUDED.summary,
    llm_model = EXCLUDED.llm_model,
    updated_at = now()
"""

SAVE_ERROR_SQL = """
INSERT INTO news_summaries (article_id, status, error, summary, llm_model)
VALUES (%s, 'failed', %s, NULL, %s)
ON CONFLICT (article_id) DO UPDATE
SET status = 'failed',
    error = EXCLUDED.error,
    summary = NULL,
    llm_model = EXCLUDED.llm_model,
    updated_at = now()
"""


def find_articles_without_summary(limit: int | None = None) -> list[dict]:
    """요약이 없거나 실패한 기사를 오래된 장 기준일부터 반환한다."""

    if limit is None:
        return find_all(FIND_PENDING_SQL)
    return find_all(FIND_PENDING_WITH_LIMIT_SQL, (limit,))


def count_articles_without_summary() -> int:
    """요약이 남은 기사 건수를 반환한다."""

    row = find_one(COUNT_PENDING_SQL)
    return int(row["pending"]) if row else 0


def save_summary(article_id: int, summary: str, llm_model: str) -> bool:
    """한 줄 요약을 저장하고 다시 요약한 경우 이전 결과를 덮어쓴다."""

    return save(SAVE_SUMMARY_SQL, (article_id, summary, llm_model))


def save_summary_error(article_id: int, message: str, llm_model: str) -> bool:
    """요약 실패 사유를 남겨 다음 실행에서 재시도 대상이 되게 한다."""

    return save(SAVE_ERROR_SQL, (article_id, message, llm_model))
