"""요약 대상만 처리하는 재실행 가능한 배치 요약 흐름을 검증한다."""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.clients.fnnews_client import KST
from app.clients.gemini_summary_client import GeminiRateLimitError
from app.schemas.news import NewsArticle
from app.schemas.news_summary import NewsSummary
from app.services.news_summary_batch import (
    PendingArticle,
    process_summary_batch,
    to_pending_article,
)


MODEL = "gemini-3.1-flash-lite"


def make_article(identifier: int) -> NewsArticle:
    return NewsArticle(
        title=f"코스피 장중 동향 {identifier} [fn오전시황]",
        published_at=f"2026-07-{identifier + 10:02d}T10:30:00+09:00",
        body=f"코스피와 코스닥의 시장 흐름을 정리한 {identifier}번째 본문입니다.",
        source="파이낸셜뉴스",
        url=f"https://www.fnnews.com/news/202607{identifier + 10:02d}103000000{identifier}",
        brief_type="morning",
        collected_at="2026-08-03T12:00:00+09:00",
    )


def make_pending(identifier: int) -> PendingArticle:
    return PendingArticle(article_id=identifier, article=make_article(identifier))


def make_summary(article: NewsArticle, *, model: str = MODEL) -> NewsSummary:
    return NewsSummary(
        article_url=article.url,
        summary=f"코스피 시장의 {str(article.url)[-1]}번째 흐름을 한 문장으로 요약했다.",
        model=model,
        summarized_at=datetime(2026, 8, 3, 12, 10, tzinfo=KST),
    )


class FakeSummaryStore:
    """조회·저장을 대신해 배치가 무엇을 처리했는지 기록한다."""

    def __init__(self, pending: list[PendingArticle]) -> None:
        self.pending = pending
        self.saved: dict[int, str] = {}
        self.errors: dict[int, str] = {}

    def load_pending(self, limit: int | None) -> list[PendingArticle]:
        remaining = [
            target
            for target in self.pending
            if target.article_id not in self.saved
        ]
        return remaining if limit is None else remaining[:limit]

    def save_summary(self, article_id: int, summary: NewsSummary) -> None:
        self.saved[article_id] = summary.summary
        self.errors.pop(article_id, None)

    def save_error(self, article_id: int, message: str) -> None:
        self.errors[article_id] = message

    def count_pending(self) -> int:
        return len(self.load_pending(None))

    def run(self, summarizer, *, delay: float = 0, limit: int | None = None, **kwargs):
        return process_summary_batch(
            expected_model=MODEL,
            summarizer=summarizer,
            load_pending=self.load_pending,
            save_summary=self.save_summary,
            save_error=self.save_error,
            count_pending=self.count_pending,
            delay=delay,
            limit=limit,
            **kwargs,
        )


class NewsSummaryBatchTests(unittest.TestCase):
    def test_only_pending_articles_are_summarized(self) -> None:
        first = make_pending(1)
        second = make_pending(2)
        store = FakeSummaryStore([first, second])
        store.saved[first.article_id] = "이미 저장된 요약입니다."
        called_urls: list[str] = []

        def summarizer(article: NewsArticle) -> NewsSummary:
            called_urls.append(str(article.url))
            return make_summary(article)

        result = store.run(summarizer)

        self.assertEqual(called_urls, [str(second.article.url)])
        self.assertEqual(result.attempted, 1)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.remaining, 0)

    def test_failure_is_recorded_and_next_run_retries_it(self) -> None:
        first = make_pending(1)
        second = make_pending(2)
        store = FakeSummaryStore([first, second])

        def first_run(article: NewsArticle) -> NewsSummary:
            if str(article.url) == str(first.article.url):
                raise RuntimeError("일시적인 API 오류")
            return make_summary(article)

        result = store.run(first_run)

        self.assertEqual(result.generated, 1)
        self.assertEqual(result.failed, 1)
        self.assertEqual(store.errors[first.article_id], "일시적인 API 오류")
        self.assertEqual(result.remaining, 1)

        retry_result = store.run(make_summary)

        self.assertEqual(retry_result.attempted, 1)
        self.assertEqual(retry_result.generated, 1)
        self.assertEqual(retry_result.remaining, 0)
        self.assertNotIn(first.article_id, store.errors)

    def test_limit_leaves_unprocessed_articles_for_next_run(self) -> None:
        store = FakeSummaryStore([make_pending(1), make_pending(2), make_pending(3)])

        result = store.run(make_summary, limit=1)

        self.assertEqual(result.attempted, 1)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.remaining, 2)

    def test_result_from_another_model_is_recorded_as_failure(self) -> None:
        target = make_pending(1)
        store = FakeSummaryStore([target])

        def summarizer(article: NewsArticle) -> NewsSummary:
            return make_summary(article, model="gemini-3.5-flash-lite")

        result = store.run(summarizer)

        self.assertEqual(result.generated, 0)
        self.assertEqual(result.failed, 1)
        self.assertIn("모델명", store.errors[target.article_id])

    @patch("app.services.news_summary_batch.time.sleep")
    def test_rate_limit_waits_and_retries_same_article(
        self,
        sleep: MagicMock,
    ) -> None:
        store = FakeSummaryStore([make_pending(1)])
        attempts = 0

        def summarizer(article: NewsArticle) -> NewsSummary:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise GeminiRateLimitError(4.0)
            return make_summary(article)

        result = store.run(summarizer)

        self.assertEqual(attempts, 2)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.failed, 0)
        sleep.assert_called_once_with(5.0)

    def test_database_row_is_converted_into_pending_article(self) -> None:
        row = {
            "id": 7,
            "title": "코스피 상승 마감 [fn마감시황]",
            "published_at": datetime(2026, 7, 31, 17, 10, tzinfo=KST),
            "body": "코스피와 코스닥의 마감 흐름을 정리한 본문입니다.",
            "source": "파이낸셜뉴스",
            "url": "https://www.fnnews.com/news/202607311710000001",
            "brief_type": "closing",
            "collected_at": datetime(2026, 8, 3, 12, 0, tzinfo=KST),
        }

        target = to_pending_article(row)

        self.assertEqual(target.article_id, 7)
        self.assertEqual(target.article.brief_type, "closing")
        self.assertEqual(target.article.market_date.isoformat(), "2026-07-31")


if __name__ == "__main__":
    unittest.main()
