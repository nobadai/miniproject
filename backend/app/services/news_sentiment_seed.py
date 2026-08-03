"""Database에 저장된 Gemma 감성 판정을 Seed SQL로 내보낸다.

판정 id 는 환경마다 다르므로 기사 URL 로 연결하고, 부모 INSERT 의 RETURNING 으로
근거 Row 를 잇는다. Prompt 를 고쳐 다시 판정하면 이 스크립트로 Seed 를 재생성한다.
"""

from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from pathlib import Path


logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = (
    BACKEND_ROOT.parent / "database" / "seeds" / "0003_news_sentiments.sql"
)

DOLLAR_TAG = "$seed$"

HEADER = """-- 목적: Gemma 감성 판정 결과를 초기 데이터로 제공한다.
-- 주요 역할: 0001 로 적재한 기사의 판정과 근거를 news_sentiments 및
--            news_sentiment_evidences 에 연결한다.
--
-- 판정 id 는 환경마다 다르므로 기사 URL 로 연결하고, 부모 INSERT 의 RETURNING 으로
-- 자식 Row 를 잇는다. 이미 판정이 있으면 RETURNING 이 비어 근거도 들어가지 않으므로
-- 다시 실행해도 중복 적재되지 않는다.
--
-- 0001_news_articles.sql 을 먼저 적용해야 한다.
-- backend 에서 uv run python -m app.services.news_sentiment_seed 로 재생성한다.
"""


def quote(value: str) -> str:
    """본문에 따옴표와 줄바꿈이 섞여 있어 Dollar Quote를 사용한다."""

    text = "" if value is None else str(value)
    if DOLLAR_TAG in text:
        raise ValueError(f"Dollar Quote 구분자가 값에 포함되어 있습니다: {text[:40]}")
    return f"{DOLLAR_TAG}{text}{DOLLAR_TAG}"


def quote_array(values: list[str]) -> str:
    """TEXT[] Column 값을 만든다. 비어 있으면 빈 배열 Literal을 쓴다."""

    if not values:
        return "'{}'"
    return "ARRAY[" + ", ".join(quote(value) for value in values) + "]"


def build_statement(sentiment: dict, evidences: list[dict]) -> str:
    """판정 한 건과 근거를 하나의 멱등한 INSERT 문으로 만든다."""

    if not evidences:
        raise ValueError(f"근거가 없는 판정입니다: {sentiment['url']}")

    rows = ",\n".join(
        "    ({seq}::smallint, {sentence}, {status}, {is_quote})".format(
            seq=evidence["seq"],
            sentence=quote(evidence["sentence"]),
            status=quote(evidence["verify_status"]),
            is_quote="true" if evidence["is_quote"] else "false",
        )
        for evidence in evidences
    )

    return f"""WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', {quote(sentiment["label"])}, {quote(sentiment["confidence"])},
           {quote(sentiment["rule"])}, {quote(sentiment["note"])},
           {"true" if sentiment["evidence_verified"] else "false"},
           {quote_array(list(sentiment["banned_hits"] or []))},
           {quote(sentiment["llm_model"])}, {quote(sentiment["llm_prompt_version"])},
           {quote(sentiment["llm_done_reason"])}
    FROM news_articles WHERE url = {quote(sentiment["url"])}
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
{rows}
) AS v(seq, sentence, verify_status, is_quote);
"""


def build_seed_sql(sentiments: list[dict], evidences: list[dict]) -> str:
    """판정과 근거를 Seed SQL 전문으로 조립한다."""

    grouped: dict[int, list[dict]] = defaultdict(list)
    for evidence in evidences:
        grouped[evidence["sentiment_id"]].append(evidence)

    statements = [
        build_statement(sentiment, grouped[sentiment["sentiment_id"]])
        for sentiment in sentiments
    ]
    return HEADER + "\n" + "\n".join(statements)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="감성 판정 결과를 Seed SQL로 내보냅니다."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="생성할 Seed SQL 경로",
    )
    return parser


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    arguments = build_parser().parse_args()

    import psycopg

    from ..repositories import news_sentiment as news_sentiment_repository

    try:
        sentiments = news_sentiment_repository.find_sentiments_for_seed()
        evidences = news_sentiment_repository.find_evidences_for_seed()
    except psycopg.Error as error:
        logger.error("판정 결과를 읽지 못했습니다: %s", error)
        return 1

    if not sentiments:
        logger.error("내보낼 판정이 없습니다. 먼저 판정 배치를 실행하세요")
        return 1

    try:
        sql = build_seed_sql(sentiments, evidences)
    except ValueError as error:
        logger.error("Seed SQL 생성 실패: %s", error)
        return 1

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(sql, encoding="utf-8")
    logger.info(
        "Seed 생성 완료: 판정 %s건, 근거 %s건 → %s",
        len(sentiments),
        len(evidences),
        arguments.output.resolve(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
