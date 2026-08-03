"""news_sentiment.py
레이어: Repositories
역할: Gemma 감성 판정 결과와 판정 대상 조회에 대한 Pure SQL 접근을 제공한다.
"""

import logging

import psycopg

from .db import find_all, find_one, get_connection


logger = logging.getLogger(__name__)


SELECT_ARTICLE_COLUMNS_SQL = """
SELECT a.id, a.url, a.title, a.body, a.source,
       a.published_at, a.market_date, a.brief_type, a.collected_at
"""

# 판정 Row 가 없으면 미처리, failed 면 재시도 대상이다.
PENDING_CONDITION_SQL = """
FROM news_articles a
LEFT JOIN news_sentiments s ON s.article_id = a.id
WHERE s.id IS NULL OR s.status = 'failed'
"""

ORDER_SQL = """
ORDER BY a.market_date, a.published_at
"""

FIND_PENDING_SQL = SELECT_ARTICLE_COLUMNS_SQL + PENDING_CONDITION_SQL + ORDER_SQL
FIND_PENDING_WITH_LIMIT_SQL = FIND_PENDING_SQL + "LIMIT %s\n"

COUNT_PENDING_SQL = "SELECT count(*) AS pending" + PENDING_CONDITION_SQL

FIND_ALL_SQL = SELECT_ARTICLE_COLUMNS_SQL + "FROM news_articles a\n" + ORDER_SQL
FIND_ALL_WITH_LIMIT_SQL = FIND_ALL_SQL + "LIMIT %s\n"

# 판정 1건에 답이 하나여야 하므로 article_id 에 UNIQUE 를 걸고 다시 판정하면 덮어쓴다.
UPSERT_SENTIMENT_SQL = """
INSERT INTO news_sentiments (
    article_id, status, error,
    label, confidence, rule, note,
    evidence_verified, banned_hits,
    llm_model, llm_prompt_version, llm_done_reason
)
VALUES (%s, 'done', NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (article_id) DO UPDATE
SET status = 'done',
    error = NULL,
    label = EXCLUDED.label,
    confidence = EXCLUDED.confidence,
    rule = EXCLUDED.rule,
    note = EXCLUDED.note,
    evidence_verified = EXCLUDED.evidence_verified,
    banned_hits = EXCLUDED.banned_hits,
    llm_model = EXCLUDED.llm_model,
    llm_prompt_version = EXCLUDED.llm_prompt_version,
    llm_done_reason = EXCLUDED.llm_done_reason,
    updated_at = now()
RETURNING id
"""

UPSERT_ERROR_SQL = """
INSERT INTO news_sentiments (
    article_id, status, error,
    label, confidence, rule, note,
    evidence_verified, banned_hits,
    llm_model, llm_prompt_version, llm_done_reason
)
VALUES (%s, 'failed', %s, NULL, NULL, NULL, '', NULL, '{}', %s, %s, NULL)
ON CONFLICT (article_id) DO UPDATE
SET status = 'failed',
    error = EXCLUDED.error,
    label = NULL,
    confidence = NULL,
    rule = NULL,
    note = '',
    evidence_verified = NULL,
    banned_hits = '{}',
    llm_model = EXCLUDED.llm_model,
    llm_prompt_version = EXCLUDED.llm_prompt_version,
    llm_done_reason = NULL,
    updated_at = now()
RETURNING id
"""

# 근거 문장 개수가 판정마다 달라 UPDATE 로 맞추면 잔여 Row 가 남는다.
DELETE_EVIDENCES_SQL = """
DELETE FROM news_sentiment_evidences WHERE sentiment_id = %s
"""

INSERT_EVIDENCE_SQL = """
INSERT INTO news_sentiment_evidences (
    sentiment_id, seq, sentence, verify_status, is_quote
)
VALUES (%s, %s, %s, %s, %s)
"""

FIND_SENTIMENTS_FOR_SEED_SQL = """
SELECT a.url,
       s.id AS sentiment_id,
       s.label, s.confidence, s.rule, s.note,
       s.evidence_verified, s.banned_hits,
       s.llm_model, s.llm_prompt_version, s.llm_done_reason
FROM news_sentiments s
JOIN news_articles a ON a.id = s.article_id
WHERE s.status = 'done'
ORDER BY a.market_date, a.published_at
"""

FIND_EVIDENCES_FOR_SEED_SQL = """
SELECT sentiment_id, seq, sentence, verify_status, is_quote
FROM news_sentiment_evidences
ORDER BY sentiment_id, seq
"""


def find_articles_without_sentiment(limit: int | None = None) -> list[dict]:
    """판정이 없거나 실패한 기사를 오래된 장 기준일부터 반환한다."""

    if limit is None:
        return find_all(FIND_PENDING_SQL)
    return find_all(FIND_PENDING_WITH_LIMIT_SQL, (limit,))


def find_all_articles(limit: int | None = None) -> list[dict]:
    """판정 여부와 무관하게 모든 기사를 반환한다. 전체 재판정에 사용한다."""

    if limit is None:
        return find_all(FIND_ALL_SQL)
    return find_all(FIND_ALL_WITH_LIMIT_SQL, (limit,))


def count_articles_without_sentiment() -> int:
    """판정이 남은 기사 건수를 반환한다."""

    row = find_one(COUNT_PENDING_SQL)
    return int(row["pending"]) if row else 0


def save_sentiment(article_id: int, record: dict) -> int:
    """판정과 근거를 한 Transaction으로 저장하고 판정 id를 반환한다.

    부모와 자식을 함께 써야 하므로 save() 를 반복 호출하지 않고
    Connection 을 직접 열어 부분 저장을 막는다.
    """

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                UPSERT_SENTIMENT_SQL,
                (
                    article_id,
                    record["label"],
                    record["confidence"],
                    record["rule"],
                    record["note"],
                    record["evidence_verified"],
                    list(record["banned_hits"]),
                    record["llm_model"],
                    record["llm_prompt_version"],
                    record["llm_done_reason"],
                ),
            )
            sentiment_id = cursor.fetchone()["id"]

            cursor.execute(DELETE_EVIDENCES_SQL, (sentiment_id,))
            for evidence in record["evidences"]:
                cursor.execute(
                    INSERT_EVIDENCE_SQL,
                    (
                        sentiment_id,
                        evidence["seq"],
                        evidence["sentence"],
                        evidence["verify_status"],
                        evidence["is_quote"],
                    ),
                )
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        logger.exception("감성 판정 저장 실패")
        raise
    finally:
        connection.close()

    return sentiment_id


def save_sentiment_error(
    article_id: int,
    message: str,
    llm_model: str,
    llm_prompt_version: str,
) -> int:
    """판정 실패 사유를 남기고 이전 근거를 지운다."""

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                UPSERT_ERROR_SQL,
                (article_id, message, llm_model, llm_prompt_version),
            )
            sentiment_id = cursor.fetchone()["id"]
            cursor.execute(DELETE_EVIDENCES_SQL, (sentiment_id,))
        connection.commit()
    except psycopg.Error:
        connection.rollback()
        logger.exception("감성 판정 실패 기록 저장 실패")
        raise
    finally:
        connection.close()

    return sentiment_id


def find_sentiments_for_seed() -> list[dict]:
    """Seed SQL 생성을 위해 성공한 판정을 기사 URL과 함께 반환한다."""

    return find_all(FIND_SENTIMENTS_FOR_SEED_SQL)


def find_evidences_for_seed() -> list[dict]:
    """Seed SQL 생성을 위해 근거 문장을 판정 id 순으로 반환한다."""

    return find_all(FIND_EVIDENCES_FOR_SEED_SQL)
