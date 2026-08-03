"""파이낸셜뉴스 시황 기사 수집 흐름을 제공한다.

수집 기간과 제목 조건을 적용하고 Client가 가져온 원문을 검증한 뒤,
DB 연동 전 내부 검수용 JSONL·CSV 결과로 저장한다.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from ..clients.fnnews_client import (
    KST,
    FnNewsClient,
    create_fnnews_client,
)
from ..schemas.news import NewsArticle


logger = logging.getLogger(__name__)

TARGET_TITLE_MARKERS = ("[fn오전시황]", "[fn마감시황]")
BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIRECTORY = BACKEND_ROOT / "cache" / "news"


@dataclass(frozen=True)
class NewsCollectionResult:
    """한 번의 기사 수집 실행 결과다."""

    articles: list[NewsArticle]
    errors: list[dict[str, str]]


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"날짜는 YYYY-MM-DD 형식이어야 합니다: {value}"
        ) from error


def matches_target_title(title: str) -> bool:
    return any(marker in title for marker in TARGET_TITLE_MARKERS)


def collect_news_articles(
    client: FnNewsClient,
    *,
    start: date,
    end: date,
    max_pages: int,
) -> NewsCollectionResult:
    """기간 내 오전·마감 시황 기사를 수집하고 기사별 오류를 격리한다."""

    if start > end:
        raise ValueError("시작일은 종료일보다 늦을 수 없습니다.")
    if max_pages < 1:
        raise ValueError("max_pages는 1 이상이어야 합니다.")

    articles_by_url: dict[str, NewsArticle] = {}
    errors: list[dict[str, str]] = []
    seen_candidate_urls: set[str] = set()

    logger.info("수집 기간: %s ~ %s", start, end)
    logger.info("대상 제목: %s", ", ".join(TARGET_TITLE_MARKERS))

    for page in range(1, max_pages + 1):
        logger.info("네이버 뉴스 검색 %s페이지 확인 중", page)
        candidates = client.read_candidates(page=page, start=start, end=end)
        if not candidates:
            logger.info("%s페이지에 결과가 없어 수집을 종료합니다", page)
            break

        new_candidates = [
            candidate
            for candidate in candidates
            if candidate.url not in seen_candidate_urls
        ]
        if not new_candidates:
            logger.info("새로운 검색 결과가 없어 수집을 종료합니다")
            break
        seen_candidate_urls.update(candidate.url for candidate in new_candidates)

        targets = [
            candidate
            for candidate in new_candidates
            if start <= candidate.published_at.date() <= end
            and candidate.url not in articles_by_url
        ]

        for candidate in targets:
            try:
                article = client.read_article(candidate)
                article_date = article.published_at.astimezone(KST).date()
                if not (start <= article_date <= end):
                    logger.warning("상세 날짜가 범위를 벗어남: %s", candidate.url)
                    continue
                if not matches_target_title(article.title):
                    logger.info("대상 제목이 아니어서 제외: %s", candidate.url)
                    continue
                articles_by_url[str(article.url)] = article
                logger.info("기사 수집 완료: %s", article.title)
            except (RuntimeError, ValueError) as error:
                logger.error("기사 수집 실패: %s (%s)", candidate.url, error)
                errors.append({"url": candidate.url, "error": str(error)})
            client.wait_between_requests()

        client.wait_between_requests()
    else:
        logger.warning(
            "최대 페이지(%s)에 도달했습니다. 기간 전체 확인 여부를 점검하세요",
            max_pages,
        )

    articles = sorted(
        articles_by_url.values(),
        key=lambda article: (article.published_at, str(article.url)),
    )
    return NewsCollectionResult(articles=articles, errors=errors)


def write_articles(
    articles: Iterable[NewsArticle], output_directory: Path
) -> tuple[Path, Path]:
    """수집 기사를 내부 검수용 JSONL과 CSV로 저장한다."""

    output_directory.mkdir(parents=True, exist_ok=True)
    records = [article.model_dump(mode="json") for article in articles]
    jsonl_path = output_directory / "fn_market_articles.jsonl"
    csv_path = output_directory / "fn_market_articles.csv"

    with jsonl_path.open("w", encoding="utf-8") as file:
        for article in records:
            file.write(json.dumps(article, ensure_ascii=False) + "\n")

    fieldnames = ["title", "published_at", "body", "source", "url", "collected_at"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    return jsonl_path, csv_path


def write_collection_errors(
    errors: list[dict[str, str]], output_directory: Path
) -> Path | None:
    """기사별 오류를 기록하고 오류가 없으면 이전 오류 파일을 제거한다."""

    error_path = output_directory / "fn_market_errors.jsonl"
    if not errors:
        error_path.unlink(missing_ok=True)
        return None

    output_directory.mkdir(parents=True, exist_ok=True)
    with error_path.open("w", encoding="utf-8") as file:
        for error in errors:
            file.write(json.dumps(error, ensure_ascii=False) + "\n")
    return error_path


def build_parser() -> argparse.ArgumentParser:
    today = datetime.now(KST).date()
    parser = argparse.ArgumentParser(
        description="파이낸셜뉴스 오전·마감 시황 기사를 수집합니다."
    )
    parser.add_argument("--start", type=parse_date, default=today, help="시작일")
    parser.add_argument("--end", type=parse_date, default=today, help="종료일")
    parser.add_argument("--max-pages", type=int, default=20, help="최대 검색 페이지")
    parser.add_argument("--delay", type=float, default=1.5, help="요청 간격(초)")
    parser.add_argument("--headed", action="store_true", help="Chrome 화면 표시")
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help="검수용 결과 저장 폴더",
    )
    return parser


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    arguments = build_parser().parse_args()
    try:
        client = create_fnnews_client(
            headed=arguments.headed,
            output_directory=arguments.output_directory,
            request_delay=arguments.delay,
        )
    except (RuntimeError, ValueError) as error:
        logger.error("뉴스 수집기 시작 실패: %s", error)
        return 1

    try:
        result = collect_news_articles(
            client,
            start=arguments.start,
            end=arguments.end,
            max_pages=arguments.max_pages,
        )
    except (RuntimeError, ValueError) as error:
        logger.error("뉴스 수집 실패: %s", error)
        return 1
    finally:
        client.close()

    jsonl_path, csv_path = write_articles(result.articles, arguments.output_directory)
    error_path = write_collection_errors(result.errors, arguments.output_directory)
    logger.info("수집 완료: %s건", len(result.articles))
    logger.info("JSONL: %s", jsonl_path.resolve())
    logger.info("CSV: %s", csv_path.resolve())
    if error_path:
        logger.warning("오류: %s (%s건)", error_path.resolve(), len(result.errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
