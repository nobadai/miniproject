"""뉴스 수집부터 감성 판정까지의 전체 흐름을 한 번에 실행한다.

    뉴스 크롤링 → news_articles
      → Gemini 한 줄 요약 → news_summaries
      → Gemma 감성 판정  → news_sentiments + news_sentiment_evidences

각 단계는 이미 처리한 기사를 건너뛰므로 몇 번을 실행해도 결과가 같다. 한 단계가
실패해도 다음 단계를 계속 진행하는데, 앞선 실행에서 남은 미처리 기사는 수집이
실패한 것과 무관하게 분석할 수 있기 때문이다. Database 연결처럼 모든 단계가
공유하는 조건이 무너진 경우에만 중단한다.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .news_collector import (
    DEFAULT_SCREENSHOT_DIRECTORY,
    KST,
    parse_date,
    run_collection,
)
from .news_sentiment_batch import run_sentiment_batch
from .news_summary_batch import run_summary_batch


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StageResult:
    """파이프라인 한 단계의 실행 결과다."""

    name: str
    succeeded: bool
    detail: str


def _collect_stage(
    *,
    start: date,
    end: date,
    max_pages: int,
    delay: float,
    headed: bool,
    screenshot_directory: Path,
) -> StageResult:
    run = run_collection(
        start=start,
        end=end,
        max_pages=max_pages,
        delay=delay,
        headed=headed,
        screenshot_directory=screenshot_directory,
    )
    detail = (
        f"신규 {run.collected}건, 적재 {run.inserted}건, "
        f"건너뜀 {run.skipped}건, 실패 {len(run.errors)}건"
    )
    return StageResult("수집", not run.errors, detail)


def _summary_stage(*, delay: float, limit: int | None) -> StageResult:
    result = run_summary_batch(delay=delay, limit=limit)
    detail = (
        f"시도 {result.attempted}건, 생성 {result.generated}건, "
        f"실패 {result.failed}건, 남음 {result.remaining}건"
    )
    return StageResult("요약", result.failed == 0, detail)


def _sentiment_stage(*, delay: float, limit: int | None) -> StageResult:
    result = run_sentiment_batch(delay=delay, limit=limit)
    detail = (
        f"시도 {result.attempted}건, 판정 {result.labeled}건, "
        f"실패 {result.failed}건, 남음 {result.remaining}건"
    )
    return StageResult("판정", result.failed == 0, detail)


def run_pipeline(
    *,
    start: date,
    end: date,
    max_pages: int = 20,
    collect_delay: float = 1.5,
    headed: bool = False,
    screenshot_directory: Path = DEFAULT_SCREENSHOT_DIRECTORY,
    summary_delay: float = 5.0,
    sentiment_delay: float = 0.0,
    limit: int | None = None,
    skip_collect: bool = False,
    skip_summary: bool = False,
    skip_sentiment: bool = False,
) -> list[StageResult]:
    """세 단계를 순서대로 실행하고 단계별 결과를 모아 반환한다."""

    stages: list[tuple[str, callable]] = []
    if not skip_collect:
        stages.append(
            (
                "수집",
                lambda: _collect_stage(
                    start=start,
                    end=end,
                    max_pages=max_pages,
                    delay=collect_delay,
                    headed=headed,
                    screenshot_directory=screenshot_directory,
                ),
            )
        )
    if not skip_summary:
        stages.append(
            ("요약", lambda: _summary_stage(delay=summary_delay, limit=limit))
        )
    if not skip_sentiment:
        stages.append(
            ("판정", lambda: _sentiment_stage(delay=sentiment_delay, limit=limit))
        )

    results: list[StageResult] = []
    for name, stage in stages:
        logger.info("--- %s 단계 시작 ---", name)
        try:
            result = stage()
        except (RuntimeError, ValueError) as error:
            # 한 단계가 막혀도 남은 미처리 기사는 다음 단계에서 처리할 수 있다.
            logger.error("%s 단계 실패: %s", name, error)
            results.append(StageResult(name, False, str(error)))
            continue
        logger.info("%s 단계 완료: %s", name, result.detail)
        results.append(result)
    return results


def build_parser() -> argparse.ArgumentParser:
    today = datetime.now(KST).date()
    parser = argparse.ArgumentParser(
        description="뉴스 수집, 한 줄 요약, 감성 판정을 순서대로 실행합니다."
    )
    parser.add_argument("--start", type=parse_date, default=today, help="수집 시작일")
    parser.add_argument("--end", type=parse_date, default=today, help="수집 종료일")
    parser.add_argument("--max-pages", type=int, default=20, help="최대 검색 페이지")
    parser.add_argument(
        "--collect-delay", type=float, default=1.5, help="크롤링 요청 간격(초)"
    )
    parser.add_argument(
        "--summary-delay", type=float, default=5.0, help="Gemini 요청 간격(초)"
    )
    parser.add_argument(
        "--sentiment-delay", type=float, default=0.0, help="Gemma 판정 간격(초)"
    )
    parser.add_argument(
        "--limit", type=int, help="요약·판정 단계에서 각각 처리할 최대 기사 수"
    )
    parser.add_argument("--headed", action="store_true", help="Chrome 화면 표시")
    parser.add_argument(
        "--screenshot-directory",
        type=Path,
        default=DEFAULT_SCREENSHOT_DIRECTORY,
        help="검색 실패 화면 저장 폴더",
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="크롤링을 건너뛴다. Chrome 없이 이미 적재된 기사만 분석할 때 사용한다",
    )
    parser.add_argument("--skip-summary", action="store_true", help="요약을 건너뛴다")
    parser.add_argument("--skip-sentiment", action="store_true", help="판정을 건너뛴다")
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
        results = run_pipeline(
            start=arguments.start,
            end=arguments.end,
            max_pages=arguments.max_pages,
            collect_delay=arguments.collect_delay,
            headed=arguments.headed,
            screenshot_directory=arguments.screenshot_directory,
            summary_delay=arguments.summary_delay,
            sentiment_delay=arguments.sentiment_delay,
            limit=arguments.limit,
            skip_collect=arguments.skip_collect,
            skip_summary=arguments.skip_summary,
            skip_sentiment=arguments.skip_sentiment,
        )
    except psycopg.Error as error:
        logger.error("Database 연결에 실패해 파이프라인을 중단합니다: %s", error)
        return 1

    if not results:
        logger.error("실행할 단계가 없습니다. skip 옵션을 확인하세요")
        return 1

    logger.info("=== 파이프라인 요약 ===")
    for result in results:
        logger.info(
            "%s %s: %s",
            "[성공]" if result.succeeded else "[실패]",
            result.name,
            result.detail,
        )
    return 0 if all(result.succeeded for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
