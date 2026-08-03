"""수집·요약·판정을 잇는 파이프라인의 단계 진행과 실패 처리를 검증한다."""

import os
import unittest
from datetime import date
from unittest.mock import patch


os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "finance_ai_test")
os.environ.setdefault("POSTGRES_USER", "finance_ai_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

from app.services.news_collector import CollectionRun
from app.services.news_pipeline import run_pipeline
from app.services.news_sentiment_batch import SentimentBatchResult
from app.services.news_summary_batch import SummaryBatchResult


MODULE = "app.services.news_pipeline"

START = date(2026, 7, 13)
END = date(2026, 7, 31)


def make_collection(errors=None) -> CollectionRun:
    return CollectionRun(
        collected=2,
        inserted=2,
        skipped=1,
        errors=errors or [],
    )


def make_summary(failed: int = 0) -> SummaryBatchResult:
    return SummaryBatchResult(attempted=2, generated=2 - failed, failed=failed, remaining=0)


def make_sentiment(failed: int = 0) -> SentimentBatchResult:
    return SentimentBatchResult(attempted=2, labeled=2 - failed, failed=failed, remaining=0)


class NewsPipelineTests(unittest.TestCase):
    def test_all_stages_run_in_order(self) -> None:
        with (
            patch(f"{MODULE}.run_collection", return_value=make_collection()),
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary()),
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()),
        ):
            results = run_pipeline(start=START, end=END)

        self.assertEqual([r.name for r in results], ["수집", "요약", "판정"])
        self.assertTrue(all(r.succeeded for r in results))

    def test_skip_collect_runs_analysis_only(self) -> None:
        """Chrome이 없는 환경에서 이미 적재된 기사만 분석할 수 있어야 한다."""

        with (
            patch(f"{MODULE}.run_collection") as collect,
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary()),
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()),
        ):
            results = run_pipeline(start=START, end=END, skip_collect=True)

        collect.assert_not_called()
        self.assertEqual([r.name for r in results], ["요약", "판정"])

    def test_failed_stage_does_not_stop_the_next_stage(self) -> None:
        """수집이 막혀도 앞선 실행에서 남은 미처리 기사는 분석해야 한다."""

        with (
            patch(f"{MODULE}.run_collection", side_effect=RuntimeError("Chrome 없음")),
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary()) as summary,
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()) as sentiment,
        ):
            results = run_pipeline(start=START, end=END)

        summary.assert_called_once()
        sentiment.assert_called_once()
        self.assertFalse(results[0].succeeded)
        self.assertIn("Chrome 없음", results[0].detail)
        self.assertTrue(results[1].succeeded)

    def test_article_level_failure_marks_stage_as_failed(self) -> None:
        with (
            patch(f"{MODULE}.run_collection", return_value=make_collection()),
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary(failed=1)),
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()),
        ):
            results = run_pipeline(start=START, end=END)

        self.assertFalse(results[1].succeeded)
        self.assertIn("실패 1건", results[1].detail)

    def test_collection_error_is_reported_as_failed_stage(self) -> None:
        errors = [{"url": "https://www.fnnews.com/news/1", "error": "접근 실패"}]

        with (
            patch(f"{MODULE}.run_collection", return_value=make_collection(errors)),
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary()),
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()),
        ):
            results = run_pipeline(start=START, end=END)

        self.assertFalse(results[0].succeeded)
        self.assertIn("실패 1건", results[0].detail)

    def test_limit_is_passed_to_analysis_stages(self) -> None:
        with (
            patch(f"{MODULE}.run_collection", return_value=make_collection()),
            patch(f"{MODULE}.run_summary_batch", return_value=make_summary()) as summary,
            patch(f"{MODULE}.run_sentiment_batch", return_value=make_sentiment()) as sentiment,
        ):
            run_pipeline(start=START, end=END, limit=3)

        self.assertEqual(summary.call_args.kwargs["limit"], 3)
        self.assertEqual(sentiment.call_args.kwargs["limit"], 3)

    def test_all_stages_skipped_returns_nothing(self) -> None:
        results = run_pipeline(
            start=START,
            end=END,
            skip_collect=True,
            skip_summary=True,
            skip_sentiment=True,
        )

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
