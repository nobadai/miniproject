"""재실행 가능한 뉴스 JSONL 배치 요약 흐름을 검증한다."""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.clients.fnnews_client import KST
from app.clients.gemini_summary_client import GeminiRateLimitError
from app.schemas.news import NewsArticle
from app.schemas.news_summary import NewsSummary
from app.services.news_summary_batch import process_summary_batch


MODEL = "gemini-3.1-flash-lite"


def make_article(identifier: int) -> NewsArticle:
    return NewsArticle(
        title=f"코스피 장중 동향 {identifier} [fn오전시황]",
        published_at=f"2026-07-{identifier + 10:02d}T10:30:00+09:00",
        body=f"코스피와 코스닥의 시장 흐름을 정리한 {identifier}번째 본문입니다.",
        source="파이낸셜뉴스",
        url=f"https://www.fnnews.com/news/202607{identifier + 10:02d}103000000{identifier}",
        collected_at="2026-08-03T12:00:00+09:00",
    )


def make_summary(article: NewsArticle, *, model: str = MODEL) -> NewsSummary:
    return NewsSummary(
        article_url=article.url,
        summary=f"코스피 시장의 {str(article.url)[-1]}번째 흐름을 한 문장으로 요약했다.",
        model=model,
        summarized_at=datetime(2026, 8, 3, 12, 10, tzinfo=KST),
    )


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


class NewsSummaryBatchTests(unittest.TestCase):
    def test_existing_summary_is_skipped_and_new_result_is_appended(self) -> None:
        first = make_article(1)
        second = make_article(2)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "articles.jsonl"
            output_path = root / "summaries.jsonl"
            error_path = root / "errors.jsonl"
            write_jsonl(
                input_path,
                [first.model_dump(mode="json"), second.model_dump(mode="json")],
            )
            write_jsonl(output_path, [make_summary(first).model_dump(mode="json")])
            called_urls: list[str] = []

            def summarizer(article: NewsArticle) -> NewsSummary:
                called_urls.append(str(article.url))
                return make_summary(article)

            result = process_summary_batch(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path,
                expected_model=MODEL,
                summarizer=summarizer,
                delay=0,
                limit=None,
            )
            saved_lines = output_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(called_urls, [str(second.url)])
        self.assertEqual(len(saved_lines), 2)
        self.assertEqual(result.already_summarized, 1)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.remaining, 0)

    def test_failure_is_recorded_and_next_run_can_retry(self) -> None:
        first = make_article(1)
        second = make_article(2)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "articles.jsonl"
            output_path = root / "summaries.jsonl"
            error_path = root / "errors.jsonl"
            write_jsonl(
                input_path,
                [first.model_dump(mode="json"), second.model_dump(mode="json")],
            )

            def first_run(article: NewsArticle) -> NewsSummary:
                if article.url == first.url:
                    raise RuntimeError("일시적인 API 오류")
                return make_summary(article)

            result = process_summary_batch(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path,
                expected_model=MODEL,
                summarizer=first_run,
                delay=0,
                limit=None,
            )
            error_record = json.loads(error_path.read_text(encoding="utf-8"))

            retry_result = process_summary_batch(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path,
                expected_model=MODEL,
                summarizer=make_summary,
                delay=0,
                limit=None,
            )

        self.assertEqual(result.generated, 1)
        self.assertEqual(result.failed, 1)
        self.assertEqual(error_record["article_url"], str(first.url))
        self.assertEqual(retry_result.already_summarized, 1)
        self.assertEqual(retry_result.generated, 1)
        self.assertEqual(retry_result.remaining, 0)

    def test_limit_leaves_unprocessed_articles_for_next_run(self) -> None:
        articles = [make_article(1), make_article(2), make_article(3)]

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "articles.jsonl"
            output_path = root / "summaries.jsonl"
            error_path = root / "errors.jsonl"
            write_jsonl(
                input_path,
                [article.model_dump(mode="json") for article in articles],
            )

            result = process_summary_batch(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path,
                expected_model=MODEL,
                summarizer=make_summary,
                delay=0,
                limit=1,
            )

        self.assertEqual(result.attempted, 1)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.remaining, 2)

    def test_existing_result_from_another_model_is_rejected(self) -> None:
        article = make_article(1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "articles.jsonl"
            output_path = root / "summaries.jsonl"
            error_path = root / "errors.jsonl"
            write_jsonl(input_path, [article.model_dump(mode="json")])
            write_jsonl(
                output_path,
                [
                    make_summary(
                        article,
                        model="gemini-3.5-flash-lite",
                    ).model_dump(mode="json")
                ],
            )

            with self.assertRaises(ValueError):
                process_summary_batch(
                    input_path=input_path,
                    output_path=output_path,
                    error_path=error_path,
                    expected_model=MODEL,
                    summarizer=make_summary,
                    delay=0,
                    limit=None,
                )

    @patch("app.services.news_summary_batch.time.sleep")
    def test_rate_limit_waits_and_retries_same_article(
        self,
        sleep: MagicMock,
    ) -> None:
        article = make_article(1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "articles.jsonl"
            output_path = root / "summaries.jsonl"
            error_path = root / "errors.jsonl"
            write_jsonl(input_path, [article.model_dump(mode="json")])
            attempts = 0

            def summarizer(target: NewsArticle) -> NewsSummary:
                nonlocal attempts
                attempts += 1
                if attempts == 1:
                    raise GeminiRateLimitError(4.0)
                return make_summary(target)

            result = process_summary_batch(
                input_path=input_path,
                output_path=output_path,
                error_path=error_path,
                expected_model=MODEL,
                summarizer=summarizer,
                delay=0,
                limit=None,
            )

        self.assertEqual(attempts, 2)
        self.assertEqual(result.generated, 1)
        self.assertEqual(result.failed, 0)
        sleep.assert_called_once_with(5.0)


if __name__ == "__main__":
    unittest.main()
