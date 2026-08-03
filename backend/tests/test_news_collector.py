"""뉴스 수집 서비스의 기간·제목 필터와 결과 저장을 검증한다."""

import csv
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from app.clients.fnnews_client import KST, ArticleCandidate
from app.schemas.news import NewsArticle
from app.services.news_collector import collect_news_articles, main, write_articles


def make_candidate(article_id: str, title: str) -> ArticleCandidate:
    return ArticleCandidate(
        title=title,
        url=f"https://www.fnnews.com/news/{article_id}",
        published_at=datetime(2026, 7, 15, 10, 30, tzinfo=KST),
    )


def make_article(candidate: ArticleCandidate, *, title: str | None = None) -> NewsArticle:
    return NewsArticle(
        title=title or candidate.title,
        published_at="2026-07-15T10:30:00+09:00",
        body="코스피와 코스닥의 오전 장 흐름을 정리한 테스트 본문입니다.",
        source="파이낸셜뉴스",
        url=candidate.url,
        collected_at="2026-08-03T12:00:00+09:00",
    )


class FakeFnNewsClient:
    def __init__(
        self,
        pages: dict[int, list[ArticleCandidate]],
        articles: dict[str, NewsArticle | RuntimeError],
    ) -> None:
        self.pages = pages
        self.articles = articles
        self.wait_count = 0
        self.closed = False

    def read_candidates(
        self,
        *,
        page: int,
        start: date,
        end: date,
    ) -> list[ArticleCandidate]:
        del start, end
        return self.pages.get(page, [])

    def read_article(self, candidate: ArticleCandidate) -> NewsArticle:
        result = self.articles[candidate.url]
        if isinstance(result, RuntimeError):
            raise result
        return result

    def wait_between_requests(self) -> None:
        self.wait_count += 1

    def close(self) -> None:
        self.closed = True


class NewsCollectorTests(unittest.TestCase):
    def test_only_target_titles_are_collected_and_urls_are_deduplicated(self) -> None:
        morning = make_candidate(
            "202607151052129598",
            "코스피 혼조세 [fn오전시황]",
        )
        unrelated = make_candidate(
            "202607151152129599",
            "환율 장중 동향",
        )
        client = FakeFnNewsClient(
            pages={1: [morning, unrelated], 2: [morning]},
            articles={
                morning.url: make_article(morning),
                unrelated.url: make_article(unrelated),
            },
        )

        result = collect_news_articles(
            client,
            start=date(2026, 7, 13),
            end=date(2026, 7, 31),
            max_pages=3,
        )

        self.assertEqual(
            [str(article.url) for article in result.articles],
            [morning.url],
        )
        self.assertEqual(result.errors, [])

    def test_article_failure_is_recorded_and_next_article_continues(self) -> None:
        failed = make_candidate(
            "202607151052129598",
            "접근 실패 기사 [fn오전시황]",
        )
        closing = make_candidate(
            "202607151752129599",
            "코스피 상승 마감 [fn마감시황]",
        )
        client = FakeFnNewsClient(
            pages={1: [failed, closing], 2: []},
            articles={
                failed.url: RuntimeError("페이지 접근 실패"),
                closing.url: make_article(closing),
            },
        )

        result = collect_news_articles(
            client,
            start=date(2026, 7, 13),
            end=date(2026, 7, 31),
            max_pages=3,
        )

        self.assertEqual(
            [str(article.url) for article in result.articles],
            [closing.url],
        )
        self.assertEqual(
            result.errors,
            [{"url": failed.url, "error": "페이지 접근 실패"}],
        )

    def test_jsonl_and_csv_are_written(self) -> None:
        candidate = make_candidate(
            "202607151052129598",
            "코스피 혼조세 [fn오전시황]",
        )
        article = make_article(candidate)

        with tempfile.TemporaryDirectory() as directory:
            jsonl_path, csv_path = write_articles([article], Path(directory))

            json_record = json.loads(jsonl_path.read_text(encoding="utf-8"))
            with csv_path.open(encoding="utf-8-sig", newline="") as file:
                csv_records = list(csv.DictReader(file))

        self.assertEqual(json_record["title"], article.title)
        self.assertEqual(csv_records[0]["url"], str(article.url))

    def test_invalid_date_range_is_rejected(self) -> None:
        client = FakeFnNewsClient(pages={}, articles={})

        with self.assertRaises(ValueError):
            collect_news_articles(
                client,
                start=date(2026, 7, 31),
                end=date(2026, 7, 13),
                max_pages=1,
            )

    def test_main_returns_failure_when_an_article_cannot_be_collected(self) -> None:
        failed = make_candidate(
            "202607151052129598",
            "접근 실패 기사 [fn오전시황]",
        )
        client = FakeFnNewsClient(
            pages={1: [failed], 2: []},
            articles={failed.url: RuntimeError("페이지 접근 실패")},
        )

        with tempfile.TemporaryDirectory() as directory:
            arguments = [
                "news_collector",
                "--start",
                "2026-07-15",
                "--end",
                "2026-07-15",
                "--output-directory",
                directory,
            ]
            with (
                patch("sys.argv", arguments),
                patch(
                    "app.services.news_collector.create_fnnews_client",
                    return_value=client,
                ),
            ):
                exit_code = main()

            error_path = Path(directory) / "fn_market_errors.jsonl"
            error_path_exists = error_path.exists()

        self.assertEqual(exit_code, 1)
        self.assertTrue(client.closed)
        self.assertTrue(error_path_exists)

    def test_main_returns_success_when_all_articles_are_collected(self) -> None:
        morning = make_candidate(
            "202607151052129598",
            "코스피 혼조세 [fn오전시황]",
        )
        client = FakeFnNewsClient(
            pages={1: [morning], 2: []},
            articles={morning.url: make_article(morning)},
        )

        with tempfile.TemporaryDirectory() as directory:
            arguments = [
                "news_collector",
                "--start",
                "2026-07-15",
                "--end",
                "2026-07-15",
                "--output-directory",
                directory,
            ]
            with (
                patch("sys.argv", arguments),
                patch(
                    "app.services.news_collector.create_fnnews_client",
                    return_value=client,
                ),
            ):
                exit_code = main()

            article_path_exists = (
                Path(directory) / "fn_market_articles.jsonl"
            ).exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(client.closed)
        self.assertTrue(article_path_exists)


if __name__ == "__main__":
    unittest.main()
