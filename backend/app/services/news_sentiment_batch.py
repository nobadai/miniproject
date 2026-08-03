"""수집 기사에 대한 재실행 가능한 Gemma 배치 감성 판정 흐름을 제공한다.

판정이 없거나 실패한 기사만 조회해 한 건씩 판정하고 즉시 저장하므로, 12B 모델
추론이 오래 걸려 중간에 끊기더라도 다음 실행에서 이어갈 수 있다.
"""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from .news_sentiment import build_sentiment_record


logger = logging.getLogger(__name__)

# 본문이 지나치게 길면 num_ctx 를 넘겨 조용히 잘릴 수 있어 미리 알린다.
BODY_LENGTH_WARNING = 4000


@dataclass(frozen=True)
class PendingArticle:
    """판정 대기 기사와 저장에 필요한 Database 식별자다."""

    article_id: int
    title: str
    market_date: date
    body: str


@dataclass(frozen=True)
class SentimentBatchResult:
    """한 번의 배치 판정 실행 결과다."""

    attempted: int
    labeled: int
    failed: int
    remaining: int


SentimentClassifier = Callable[[str, date, str], dict]
ArticleLoader = Callable[[int | None], list[PendingArticle]]
SentimentSaver = Callable[[int, dict], None]
ErrorSaver = Callable[[int, str], None]
PendingCounter = Callable[[], int]


def to_pending_article(row: dict) -> PendingArticle:
    """조회 Row를 판정 대상 기사로 변환한다."""

    return PendingArticle(
        article_id=int(row["id"]),
        title=row["title"],
        market_date=row["market_date"],
        body=row["body"],
    )


def process_sentiment_batch(
    *,
    classifier: SentimentClassifier,
    load_articles: ArticleLoader,
    save_sentiment: SentimentSaver,
    save_error: ErrorSaver,
    count_pending: PendingCounter,
    delay: float = 0.0,
    limit: int | None = None,
) -> SentimentBatchResult:
    """판정이 필요한 기사만 처리하고 결과를 기사별로 즉시 저장한다."""

    if delay < 0:
        raise ValueError("delay는 0 이상이어야 합니다.")
    if limit is not None and limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다.")

    targets = load_articles(limit)
    labeled = 0
    failed = 0

    for index, target in enumerate(targets, start=1):
        logger.info("판정 %s/%s: %s", index, len(targets), target.title)
        if len(target.body) > BODY_LENGTH_WARNING:
            logger.warning(
                "본문이 깁니다(%s자). num_ctx 초과로 잘리지 않는지 확인하세요",
                len(target.body),
            )
        try:
            classification = classifier(
                target.title, target.market_date, target.body
            )
            record = build_sentiment_record(classification, target.body)
            save_sentiment(target.article_id, record)
            labeled += 1
            logger.info(
                "판정 완료: %s / %s / %s",
                record["label"],
                record["confidence"],
                record["rule"],
            )
        except (RuntimeError, ValueError, KeyError) as error:
            logger.error("기사 판정 실패: %s (%s)", target.title, error)
            save_error(target.article_id, str(error))
            failed += 1

        if delay > 0 and index < len(targets):
            time.sleep(delay)

    return SentimentBatchResult(
        attempted=len(targets),
        labeled=labeled,
        failed=failed,
        remaining=count_pending(),
    )


def run_sentiment_batch(
    *,
    delay: float = 0.0,
    limit: int | None = None,
    label_all: bool = False,
) -> SentimentBatchResult:
    """Settings와 Repository를 연결해 판정 배치를 실행한다.

    Pipeline과 단독 실행이 같은 경로를 쓰도록 조립을 여기에 모은다.
    """

    from ..clients.gemma_client import PROMPT_VERSION, GemmaSentimentClient
    from ..core.config import settings
    from ..repositories import news_sentiment as news_sentiment_repository

    client = GemmaSentimentClient(
        host=settings.ollama_host,
        model=settings.ollama_model,
        num_ctx=settings.ollama_num_ctx,
        num_gpu=settings.ollama_num_gpu,
    )
    logger.info(
        "Ollama %s / 모델 %s / num_ctx %s / num_gpu %s / prompt %s",
        settings.ollama_host,
        settings.ollama_model,
        settings.ollama_num_ctx,
        settings.ollama_num_gpu,
        PROMPT_VERSION,
    )

    def classifier(title: str, market_date: date, body: str) -> dict:
        return client.classify(title=title, market_date=market_date, body=body)

    def load_articles(pending_limit: int | None) -> list[PendingArticle]:
        rows = (
            news_sentiment_repository.find_all_articles(pending_limit)
            if label_all
            else news_sentiment_repository.find_articles_without_sentiment(pending_limit)
        )
        return [to_pending_article(row) for row in rows]

    def save_sentiment(article_id: int, record: dict) -> None:
        news_sentiment_repository.save_sentiment(article_id, record)

    def save_error(article_id: int, message: str) -> None:
        news_sentiment_repository.save_sentiment_error(
            article_id, message, settings.ollama_model, PROMPT_VERSION
        )

    return process_sentiment_batch(
        classifier=classifier,
        load_articles=load_articles,
        save_sentiment=save_sentiment,
        save_error=save_error,
        count_pending=news_sentiment_repository.count_articles_without_sentiment,
        delay=delay,
        limit=limit,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="판정이 남은 수집 기사를 로컬 Gemma로 감성 판정합니다."
    )
    parser.add_argument("--limit", type=int, help="이번 실행에서 처리할 최대 기사 수")
    parser.add_argument("--delay", type=float, default=0.0, help="판정 간격(초)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="이미 판정된 기사까지 포함해 전체를 다시 판정한다",
    )
    return parser


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    arguments = build_parser().parse_args()

    # Settings와 Database 연결은 실행 시점에만 필요하므로 여기에서 가져온다.
    import psycopg

    try:
        result = run_sentiment_batch(
            delay=arguments.delay,
            limit=arguments.limit,
            label_all=arguments.all,
        )
    except (ValueError, psycopg.Error) as error:
        logger.error("배치 판정을 시작하지 못했습니다: %s", error)
        return 1

    logger.info(
        "배치 완료: 시도=%s, 판정=%s, 실패=%s, 남음=%s",
        result.attempted,
        result.labeled,
        result.failed,
        result.remaining,
    )
    if result.failed:
        logger.warning("실패한 기사는 다음 실행에서 다시 시도합니다")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
