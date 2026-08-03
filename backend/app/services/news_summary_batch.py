"""수집 기사에 대한 재실행 가능한 Gemini 배치 요약 흐름을 제공한다.

요약이 없거나 실패한 기사만 조회해 처리하므로 이미 요약된 기사는 배치가
다루지 않으며, 성공과 실패를 기사별로 즉시 저장해 중단되거나 일부 실패해도
다음 실행에서 이어갈 수 있다.
"""

from __future__ import annotations

import argparse
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass

from ..clients.gemini_summary_client import GeminiRateLimitError
from ..schemas.news import NewsArticle
from ..schemas.news_summary import NewsSummary


logger = logging.getLogger(__name__)

# 조회 Row 에서 NewsArticle 로 옮길 Column 이다. market_date 는 게시시각에서 파생된다.
ARTICLE_FIELDS = (
    "title",
    "published_at",
    "body",
    "source",
    "url",
    "brief_type",
    "collected_at",
)


@dataclass(frozen=True)
class PendingArticle:
    """요약 대기 기사와 저장에 필요한 Database 식별자다."""

    article_id: int
    article: NewsArticle


@dataclass(frozen=True)
class SummaryBatchResult:
    """한 번의 배치 요약 실행 결과다."""

    attempted: int
    generated: int
    failed: int
    remaining: int


SummaryGenerator = Callable[[NewsArticle], NewsSummary]
PendingLoader = Callable[[int | None], list[PendingArticle]]
SummarySaver = Callable[[int, NewsSummary], None]
ErrorSaver = Callable[[int, str], None]
PendingCounter = Callable[[], int]


def to_pending_article(row: dict) -> PendingArticle:
    """조회 Row를 검증된 요약 대상 기사로 변환한다."""

    article = NewsArticle.model_validate({name: row[name] for name in ARTICLE_FIELDS})
    return PendingArticle(article_id=int(row["id"]), article=article)


def _record_failure(
    save_error: ErrorSaver,
    target: PendingArticle,
    error: Exception,
) -> None:
    """기사별 요약 오류를 남겨 다음 실행에서 재시도 대상이 되게 한다."""

    logger.error("기사 요약 실패: %s (%s)", target.article.url, error)
    save_error(target.article_id, str(error))


def process_summary_batch(
    *,
    expected_model: str,
    summarizer: SummaryGenerator,
    load_pending: PendingLoader,
    save_summary: SummarySaver,
    save_error: ErrorSaver,
    count_pending: PendingCounter,
    delay: float,
    limit: int | None,
    max_rate_limit_retries: int = 3,
) -> SummaryBatchResult:
    """요약이 필요한 기사만 처리하고 결과를 기사별로 즉시 저장한다."""

    if delay < 0:
        raise ValueError("delay는 0 이상이어야 합니다.")
    if limit is not None and limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다.")
    if max_rate_limit_retries < 0:
        raise ValueError("max_rate_limit_retries는 0 이상이어야 합니다.")

    pending = load_pending(limit)
    generated = 0
    failed = 0

    for index, target in enumerate(pending, start=1):
        article = target.article
        logger.info("요약 %s/%s: %s", index, len(pending), article.title)
        rate_limit_retries = 0
        while True:
            try:
                summary = summarizer(article)
                if str(summary.article_url) != str(article.url):
                    raise ValueError("요약 결과의 원문 URL이 입력 기사와 다릅니다.")
                if summary.model != expected_model:
                    raise ValueError("요약 결과의 모델명이 현재 설정과 다릅니다.")
                save_summary(target.article_id, summary)
                generated += 1
                break
            except GeminiRateLimitError as error:
                if rate_limit_retries >= max_rate_limit_retries:
                    _record_failure(save_error, target, error)
                    failed += 1
                    break
                wait_seconds = max(error.retry_after_seconds + 1.0, delay)
                rate_limit_retries += 1
                logger.warning(
                    "요청 한도 재시도 %s/%s: %.1f초 대기",
                    rate_limit_retries,
                    max_rate_limit_retries,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
            except (RuntimeError, ValueError) as error:
                _record_failure(save_error, target, error)
                failed += 1
                break

        if delay > 0 and index < len(pending):
            time.sleep(delay)

    return SummaryBatchResult(
        attempted=len(pending),
        generated=generated,
        failed=failed,
        remaining=count_pending(),
    )


def run_summary_batch(
    *,
    delay: float,
    limit: int | None = None,
    max_rate_limit_retries: int = 3,
) -> SummaryBatchResult:
    """Settings와 Repository를 연결해 요약 배치를 실행한다.

    Pipeline과 단독 실행이 같은 경로를 쓰도록 조립을 여기에 모은다.
    """

    from ..core.config import settings
    from ..repositories import news_summary as news_summary_repository
    from .news_summary import summarize_news_article

    model = settings.gemini_model

    def load_pending(pending_limit: int | None) -> list[PendingArticle]:
        rows = news_summary_repository.find_articles_without_summary(pending_limit)
        return [to_pending_article(row) for row in rows]

    def save_summary(article_id: int, summary: NewsSummary) -> None:
        news_summary_repository.save_summary(article_id, summary.summary, model)

    def save_error(article_id: int, message: str) -> None:
        news_summary_repository.save_summary_error(article_id, message, model)

    return process_summary_batch(
        expected_model=model,
        summarizer=summarize_news_article,
        load_pending=load_pending,
        save_summary=save_summary,
        save_error=save_error,
        count_pending=news_summary_repository.count_articles_without_summary,
        delay=delay,
        limit=limit,
        max_rate_limit_retries=max_rate_limit_retries,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="요약이 남은 수집 기사를 Gemini로 한 줄 요약합니다."
    )
    parser.add_argument("--delay", type=float, default=5.0, help="요청 간격(초)")
    parser.add_argument("--limit", type=int, help="이번 실행에서 처리할 최대 기사 수")
    parser.add_argument(
        "--max-rate-limit-retries",
        type=int,
        default=3,
        help="429 요청 한도 오류의 기사별 최대 재시도 횟수",
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
        result = run_summary_batch(
            delay=arguments.delay,
            limit=arguments.limit,
            max_rate_limit_retries=arguments.max_rate_limit_retries,
        )
    except (ValueError, psycopg.Error) as error:
        logger.error("배치 요약을 시작하지 못했습니다: %s", error)
        return 1

    logger.info(
        "배치 완료: 시도=%s, 생성=%s, 실패=%s, 남음=%s",
        result.attempted,
        result.generated,
        result.failed,
        result.remaining,
    )
    if result.failed:
        logger.warning("실패한 기사는 다음 실행에서 다시 시도합니다")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
