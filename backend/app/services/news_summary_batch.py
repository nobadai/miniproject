"""수집 뉴스 JSONL의 재실행 가능한 Gemini 배치 요약 흐름을 제공한다.

기존 요약 URL을 건너뛰고 성공 결과를 기사별로 즉시 저장하며, 실패 내역은
별도 JSONL에 남겨 중단되거나 일부 실패해도 다음 실행에서 이어갈 수 있다.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from ..clients.gemini_summary_client import GeminiRateLimitError
from ..schemas.news import NewsArticle
from ..schemas.news_summary import NewsSummary


logger = logging.getLogger(__name__)

KST = ZoneInfo("Asia/Seoul")
BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NEWS_DIRECTORY = BACKEND_ROOT / "cache" / "news"
DEFAULT_INPUT_PATH = DEFAULT_NEWS_DIRECTORY / "fn_market_articles.jsonl"
DEFAULT_OUTPUT_PATH = DEFAULT_NEWS_DIRECTORY / "news_summaries.jsonl"
DEFAULT_ERROR_PATH = DEFAULT_NEWS_DIRECTORY / "news_summary_errors.jsonl"

SummaryGenerator = Callable[[NewsArticle], NewsSummary]


@dataclass(frozen=True)
class SummaryBatchResult:
    """한 번의 배치 요약 실행 결과다."""

    total: int
    already_summarized: int
    attempted: int
    generated: int
    failed: int
    remaining: int


def _read_jsonl(path: Path) -> list[tuple[int, dict[str, object]]]:
    """JSONL 파일을 읽고 각 레코드의 원래 줄 번호를 함께 반환한다."""

    if not path.is_file():
        raise FileNotFoundError(f"JSONL 파일을 찾지 못했습니다: {path}")

    records: list[tuple[int, dict[str, object]]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{path}의 {line_number}번째 줄이 올바른 JSON이 아닙니다."
            ) from error
        if not isinstance(record, dict):
            raise ValueError(f"{path}의 {line_number}번째 줄은 JSON 객체여야 합니다.")
        records.append((line_number, record))
    return records


def load_news_articles(path: Path) -> list[NewsArticle]:
    """원본 뉴스 JSONL을 검증하고 URL 기준으로 중복을 제거한다."""

    articles_by_url: dict[str, NewsArticle] = {}
    for line_number, record in _read_jsonl(path):
        try:
            article = NewsArticle.model_validate(record)
        except ValidationError as error:
            raise ValueError(
                f"{path}의 {line_number}번째 뉴스가 스키마와 일치하지 않습니다."
            ) from error
        url = str(article.url)
        if url in articles_by_url:
            logger.warning("중복 원문 URL을 제외합니다: %s", url)
            continue
        articles_by_url[url] = article
    return list(articles_by_url.values())


def load_existing_summaries(
    path: Path,
    *,
    expected_model: str,
) -> dict[str, NewsSummary]:
    """기존 요약을 검증하고 현재 모델과 다른 결과가 섞이지 않게 한다."""

    if not path.exists():
        return {}

    summaries_by_url: dict[str, NewsSummary] = {}
    for line_number, record in _read_jsonl(path):
        try:
            summary = NewsSummary.model_validate(record)
        except ValidationError as error:
            raise ValueError(
                f"{path}의 {line_number}번째 요약이 스키마와 일치하지 않습니다."
            ) from error
        if summary.model != expected_model:
            raise ValueError(
                f"기존 요약 모델({summary.model})과 현재 모델({expected_model})이 "
                "다릅니다. 출력 파일을 분리하세요."
            )
        url = str(summary.article_url)
        if url in summaries_by_url:
            raise ValueError(f"기존 요약 파일에 중복 URL이 있습니다: {url}")
        summaries_by_url[url] = summary
    return summaries_by_url


def _append_json_record(path: Path, record: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_summary_batch(
    *,
    input_path: Path,
    output_path: Path,
    error_path: Path,
    expected_model: str,
    summarizer: SummaryGenerator,
    delay: float,
    limit: int | None,
    max_rate_limit_retries: int = 3,
) -> SummaryBatchResult:
    """신규 기사만 요약하고 성공·실패 결과를 실행 중 즉시 저장한다."""

    if delay < 0:
        raise ValueError("delay는 0 이상이어야 합니다.")
    if limit is not None and limit < 1:
        raise ValueError("limit은 1 이상이어야 합니다.")
    if max_rate_limit_retries < 0:
        raise ValueError("max_rate_limit_retries는 0 이상이어야 합니다.")

    articles = load_news_articles(input_path)
    existing = load_existing_summaries(
        output_path,
        expected_model=expected_model,
    )
    pending = [article for article in articles if str(article.url) not in existing]
    selected = pending[:limit] if limit is not None else pending
    error_path.unlink(missing_ok=True)

    generated = 0
    failed = 0
    for index, article in enumerate(selected, start=1):
        logger.info("요약 %s/%s: %s", index, len(selected), article.title)
        rate_limit_retries = 0
        while True:
            try:
                summary = summarizer(article)
                if str(summary.article_url) != str(article.url):
                    raise ValueError("요약 결과의 원문 URL이 입력 기사와 다릅니다.")
                if summary.model != expected_model:
                    raise ValueError("요약 결과의 모델명이 현재 설정과 다릅니다.")
                _append_json_record(output_path, summary.model_dump(mode="json"))
                generated += 1
                break
            except GeminiRateLimitError as error:
                if rate_limit_retries >= max_rate_limit_retries:
                    _append_summary_error(
                        error_path,
                        article=article,
                        model=expected_model,
                        error=error,
                    )
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
                _append_summary_error(
                    error_path,
                    article=article,
                    model=expected_model,
                    error=error,
                )
                failed += 1
                break

        if delay > 0 and index < len(selected):
            time.sleep(delay)

    remaining = len(pending) - generated
    return SummaryBatchResult(
        total=len(articles),
        already_summarized=len(existing),
        attempted=len(selected),
        generated=generated,
        failed=failed,
        remaining=remaining,
    )


def _append_summary_error(
    path: Path,
    *,
    article: NewsArticle,
    model: str,
    error: RuntimeError | ValueError,
) -> None:
    """기사별 요약 오류를 본문 없이 기록한다."""

    logger.error("기사 요약 실패: %s (%s)", article.url, error)
    _append_json_record(
        path,
        {
            "article_url": str(article.url),
            "title": article.title,
            "model": model,
            "error": str(error),
            "failed_at": datetime.now(KST).isoformat(timespec="seconds"),
        },
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="수집된 뉴스 JSONL을 Gemini로 한 줄 요약합니다."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--errors", type=Path, default=DEFAULT_ERROR_PATH)
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

    from ..core.config import settings
    from .news_summary import summarize_news_article

    try:
        result = process_summary_batch(
            input_path=arguments.input,
            output_path=arguments.output,
            error_path=arguments.errors,
            expected_model=settings.gemini_model,
            summarizer=summarize_news_article,
            delay=arguments.delay,
            limit=arguments.limit,
            max_rate_limit_retries=arguments.max_rate_limit_retries,
        )
    except (FileNotFoundError, ValueError) as error:
        logger.error("배치 요약을 시작하지 못했습니다: %s", error)
        return 1

    logger.info(
        "배치 완료: 전체=%s, 기존=%s, 시도=%s, 생성=%s, 실패=%s, 남음=%s",
        result.total,
        result.already_summarized,
        result.attempted,
        result.generated,
        result.failed,
        result.remaining,
    )
    logger.info("요약 결과: %s", arguments.output.resolve())
    if result.failed:
        logger.warning("오류 결과: %s", arguments.errors.resolve())
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
