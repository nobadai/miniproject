"""파이낸셜뉴스 시황 기사 수집 흐름을 제공한다.

수집 기간과 제목 조건을 적용하고 Client가 가져온 원문을 검증하며, 이미
적재된 기사는 상세 페이지를 열지 않고 건너뛴 뒤 새 기사만 PostgreSQL에 저장한다.
"""

from __future__ import annotations

import argparse
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from ..clients.fnnews_client import (
    BRIEF_TYPE_MARKERS,
    KST,
    FnNewsClient,
    create_fnnews_client,
)
from ..schemas.news import NewsArticle


logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCREENSHOT_DIRECTORY = BACKEND_ROOT / "cache" / "news"

# 후보 URL 목록을 받아 이미 적재된 URL만 돌려주는 조회 함수다.
UrlLookup = Callable[[list[str]], set[str]]


@dataclass(frozen=True)
class NewsCollectionResult:
    """한 번의 기사 수집 실행 결과다."""

    articles: list[NewsArticle]
    errors: list[dict[str, str]]
    skipped: int


@dataclass(frozen=True)
class CollectionRun:
    """수집과 적재까지 마친 실행 결과다."""

    collected: int
    inserted: int
    skipped: int
    errors: list[dict[str, str]]


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"날짜는 YYYY-MM-DD 형식이어야 합니다: {value}"
        ) from error


def collect_news_articles(
    client: FnNewsClient,
    *,
    start: date,
    end: date,
    max_pages: int,
    find_existing_urls: UrlLookup | None = None,
) -> NewsCollectionResult:
    """기간 내 오전·마감 시황 기사를 수집하고 기사별 오류를 격리한다."""

    if start > end:
        raise ValueError("시작일은 종료일보다 늦을 수 없습니다.")
    if max_pages < 1:
        raise ValueError("max_pages는 1 이상이어야 합니다.")

    articles_by_url: dict[str, NewsArticle] = {}
    errors: list[dict[str, str]] = []
    seen_candidate_urls: set[str] = set()
    skipped = 0

    logger.info("수집 기간: %s ~ %s", start, end)
    logger.info("대상 제목: %s", ", ".join(BRIEF_TYPE_MARKERS))

    for page in range(1, max_pages + 1):
        logger.info("네이버 뉴스 검색 %s페이지 확인 중", page)
        candidates = client.read_candidates(page=page, start=start, end=end)
        if not candidates:
            logger.info("%s페이지에 결과가 없어 수집을 종료합니다", page)
            break

        # 종료 판단에는 이번 실행에서 본 URL만 사용한다. 여기에 적재 여부를 섞으면
        # 앞 페이지가 모두 적재된 재실행에서 뒤 페이지에 닿지 못한 채 멈춘다.
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

        if find_existing_urls is not None and targets:
            known_urls = find_existing_urls([candidate.url for candidate in targets])
            if known_urls:
                skipped += len(known_urls)
                logger.info("이미 적재된 기사 %s건을 건너뜁니다", len(known_urls))
                targets = [
                    candidate
                    for candidate in targets
                    if candidate.url not in known_urls
                ]

        for candidate in targets:
            try:
                article = client.read_article(candidate)
                if article is None:
                    logger.info("대상 제목이 아니어서 제외: %s", candidate.url)
                    continue
                article_date = article.published_at.astimezone(KST).date()
                if not (start <= article_date <= end):
                    logger.warning("상세 날짜가 범위를 벗어남: %s", candidate.url)
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
    return NewsCollectionResult(articles=articles, errors=errors, skipped=skipped)


def run_collection(
    *,
    start: date,
    end: date,
    max_pages: int,
    delay: float,
    headed: bool,
    screenshot_directory: Path,
) -> CollectionRun:
    """수집기를 구성해 기사를 모으고 Database에 적재한다.

    Pipeline과 단독 실행이 같은 경로를 쓰도록 조립을 여기에 모은다.
    """

    from ..repositories import news_article as news_article_repository

    client = create_fnnews_client(
        headed=headed,
        output_directory=screenshot_directory,
        request_delay=delay,
    )
    try:
        result = collect_news_articles(
            client,
            start=start,
            end=end,
            max_pages=max_pages,
            find_existing_urls=news_article_repository.find_existing_urls,
        )
    finally:
        client.close()

    inserted = news_article_repository.save_articles(result.articles)
    return CollectionRun(
        collected=len(result.articles),
        inserted=inserted,
        skipped=result.skipped,
        errors=result.errors,
    )


def build_parser() -> argparse.ArgumentParser:
    today = datetime.now(KST).date()
    parser = argparse.ArgumentParser(
        description="파이낸셜뉴스 오전·마감 시황 기사를 수집해 Database에 적재합니다."
    )
    parser.add_argument("--start", type=parse_date, default=today, help="시작일")
    parser.add_argument("--end", type=parse_date, default=today, help="종료일")
    parser.add_argument("--max-pages", type=int, default=20, help="최대 검색 페이지")
    parser.add_argument("--delay", type=float, default=1.5, help="요청 간격(초)")
    parser.add_argument("--headed", action="store_true", help="Chrome 화면 표시")
    parser.add_argument(
        "--screenshot-directory",
        type=Path,
        default=DEFAULT_SCREENSHOT_DIRECTORY,
        help="검색 실패 화면 저장 폴더",
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
        run = run_collection(
            start=arguments.start,
            end=arguments.end,
            max_pages=arguments.max_pages,
            delay=arguments.delay,
            headed=arguments.headed,
            screenshot_directory=arguments.screenshot_directory,
        )
    except (RuntimeError, ValueError, psycopg.Error) as error:
        logger.error("뉴스 수집 실패: %s", error)
        return 1

    logger.info(
        "수집 완료: 신규=%s, 적재=%s, 건너뜀=%s, 실패=%s",
        run.collected,
        run.inserted,
        run.skipped,
        len(run.errors),
    )
    if run.errors:
        for failure in run.errors:
            logger.warning("수집 실패 기사: %s (%s)", failure["url"], failure["error"])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
