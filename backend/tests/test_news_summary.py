"""Gemini 한 줄 요약 Client, Service와 결과 스키마를 검증한다."""

import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pydantic import SecretStr, ValidationError


os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "finance_ai_test")
os.environ.setdefault("POSTGRES_USER", "finance_ai_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

from app.clients.fnnews_client import KST
from app.clients.gemini_summary_client import (
    GeminiRateLimitError,
    GeminiSummaryClient,
    GeminiSummaryError,
    build_summary_prompt,
)
from app.schemas.news import NewsArticle
from app.schemas.news_summary import NewsSummary, NewsSummaryContent
from app.services import news_summary as news_summary_service


def make_article() -> NewsArticle:
    return NewsArticle(
        title="코스피 상승 마감 [fn마감시황]",
        published_at="2026-07-31T17:10:00+09:00",
        body="외국인 순매수와 반도체주 강세로 코스피가 상승 마감했다.",
        source="파이낸셜뉴스",
        url="https://www.fnnews.com/news/202607311710000001",
        collected_at="2026-08-03T12:00:00+09:00",
    )


class NewsSummarySchemaTests(unittest.TestCase):
    def test_multiline_summary_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            NewsSummaryContent(summary="첫 번째 요약 문장입니다.\n두 번째 줄입니다.")

    def test_summary_result_requires_timezone(self) -> None:
        with self.assertRaises(ValidationError):
            NewsSummary(
                article_url=make_article().url,
                summary="외국인 매수와 반도체주 강세로 코스피가 상승 마감했다.",
                model="gemini-3.1-flash-lite",
                summarized_at=datetime(2026, 8, 3, 12, 0),
            )


class GeminiSummaryClientTests(unittest.TestCase):
    def test_prompt_marks_article_body_as_input_data(self) -> None:
        prompt = build_summary_prompt(make_article())

        self.assertIn("<article_body>", prompt)
        self.assertIn("외국인 순매수", prompt)
        self.assertIn("출처: 파이낸셜뉴스", prompt)

    @patch("app.clients.gemini_summary_client.genai.Client")
    def test_structured_summary_is_returned(self, client_class: MagicMock) -> None:
        generated = NewsSummaryContent(
            summary="외국인 매수와 반도체주 강세로 코스피가 상승 마감했다."
        )
        sdk_client = client_class.return_value
        sdk_client.models.generate_content.return_value = SimpleNamespace(
            parsed=generated,
            text=generated.model_dump_json(),
        )
        client = GeminiSummaryClient(
            api_key="test-api-key",
            model="gemini-3.1-flash-lite",
        )

        result = client.summarize(make_article())

        self.assertEqual(result, generated)
        request = sdk_client.models.generate_content.call_args.kwargs
        self.assertEqual(request["model"], "gemini-3.1-flash-lite")
        self.assertEqual(request["config"].response_mime_type, "application/json")
        self.assertIsNone(request["config"].response_schema)
        self.assertEqual(
            request["config"].response_json_schema["properties"]["summary"]["type"],
            "string",
        )
        sdk_client.close.assert_called_once_with()

    @patch("app.clients.gemini_summary_client.genai.Client")
    def test_rate_limit_includes_retry_delay(self, client_class: MagicMock) -> None:
        from google.genai import errors

        sdk_client = client_class.return_value
        sdk_client.models.generate_content.side_effect = errors.ClientError(
            429,
            {
                "error": {
                    "code": 429,
                    "status": "RESOURCE_EXHAUSTED",
                    "details": [
                        {
                            "@type": "type.googleapis.com/google.rpc.RetryInfo",
                            "retryDelay": "12.5s",
                        }
                    ],
                }
            },
        )
        client = GeminiSummaryClient(
            api_key="test-api-key",
            model="gemini-3.1-flash-lite",
        )

        with self.assertRaises(GeminiRateLimitError) as context:
            client.summarize(make_article())

        self.assertEqual(context.exception.retry_after_seconds, 12.5)
        sdk_client.close.assert_called_once_with()

    @patch("app.clients.gemini_summary_client.genai.Client")
    def test_empty_response_is_rejected(self, client_class: MagicMock) -> None:
        sdk_client = client_class.return_value
        sdk_client.models.generate_content.return_value = SimpleNamespace(
            parsed=None,
            text=None,
        )
        client = GeminiSummaryClient(
            api_key="test-api-key",
            model="gemini-3.1-flash-lite",
        )

        with self.assertRaises(GeminiSummaryError):
            client.summarize(make_article())

        sdk_client.close.assert_called_once_with()


class NewsSummaryServiceTests(unittest.TestCase):
    @patch("app.services.news_summary.GeminiSummaryClient")
    def test_summary_metadata_is_attached(self, client_class: MagicMock) -> None:
        client_class.return_value.summarize.return_value = NewsSummaryContent(
            summary="외국인 매수와 반도체주 강세로 코스피가 상승 마감했다."
        )

        with (
            patch.object(
                news_summary_service.settings,
                "gemini_api_key",
                SecretStr("test-api-key"),
            ),
            patch.object(
                news_summary_service.settings,
                "gemini_model",
                "gemini-3.1-flash-lite",
            ),
        ):
            result = news_summary_service.summarize_news_article(make_article())

        self.assertEqual(
            str(result.article_url),
            "https://www.fnnews.com/news/202607311710000001",
        )
        self.assertEqual(result.model, "gemini-3.1-flash-lite")
        self.assertEqual(result.summarized_at.tzinfo, KST)

    def test_missing_api_key_is_rejected_before_call(self) -> None:
        with patch.object(news_summary_service.settings, "gemini_api_key", None):
            with self.assertRaises(RuntimeError):
                news_summary_service.summarize_news_article(make_article())


if __name__ == "__main__":
    unittest.main()
