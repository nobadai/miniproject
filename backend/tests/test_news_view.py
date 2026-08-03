"""뉴스 조회 결과 조립과 Response 계약을 검증한다."""

import os
import unittest
from datetime import date, datetime, timezone


os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "finance_ai_test")
os.environ.setdefault("POSTGRES_USER", "finance_ai_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test-password")

from app.schemas.news import KST, News
from app.services.news import build_news_list


def make_article(identifier: int, **overrides) -> dict:
    article = {
        "id": identifier,
        "url": f"https://www.fnnews.com/news/20260713102900473{identifier}",
        "title": f"코스피 장중 동향 {identifier} [fn오전시황]",
        "body": "코스피와 코스닥의 오전 장 흐름을 정리한 본문입니다.",
        "source": "파이낸셜뉴스",
        "published_at": datetime(2026, 7, 13, 10, 31, tzinfo=KST),
        "market_date": date(2026, 7, 13),
        "brief_type": "morning",
        "summary": "코스피가 대형주 약세에 밀려 하락했습니다.",
        "label": "NEG",
    }
    article.update(overrides)
    return article


def make_evidence(article_id: int, seq: int, sentence: str, *, quote=False) -> dict:
    return {
        "article_id": article_id,
        "seq": seq,
        "sentence": sentence,
        "is_quote": quote,
    }


class NewsViewTests(unittest.TestCase):
    def test_evidence_is_grouped_by_article(self) -> None:
        articles = [make_article(1), make_article(2)]
        evidences = [
            make_evidence(1, 1, "첫 번째 기사의 근거입니다."),
            make_evidence(1, 2, "첫 번째 기사의 두 번째 근거입니다.", quote=True),
            make_evidence(2, 1, "두 번째 기사의 근거입니다."),
        ]

        news = build_news_list(articles, evidences)

        self.assertEqual(len(news[0].evidence), 2)
        self.assertEqual(len(news[1].evidence), 1)
        self.assertTrue(news[0].evidence[1].is_quote)
        self.assertEqual(news[1].evidence[0].sentence, "두 번째 기사의 근거입니다.")

    def test_article_without_summary_or_label_is_still_returned(self) -> None:
        articles = [make_article(1, summary=None, label=None)]

        news = build_news_list(articles, [])

        self.assertEqual(len(news), 1)
        self.assertIsNone(news[0].summary)
        self.assertIsNone(news[0].label)
        self.assertEqual(news[0].evidence, [])

    def test_internal_fields_are_not_part_of_the_response(self) -> None:
        """confidence·rule·note 와 검증 필드는 내부 지표라 응답에 없어야 한다."""

        serialized = News.model_json_schema()["properties"]

        for name in (
            "confidence",
            "rule",
            "note",
            "evidence_verified",
            "banned_hits",
            "llm_model",
        ):
            self.assertNotIn(name, serialized)

    def test_published_at_is_returned_in_korean_time(self) -> None:
        """Driver가 UTC로 돌려줘도 market_date와 같은 KST 기준으로 내보낸다."""

        articles = [
            make_article(
                1,
                published_at=datetime(2026, 7, 31, 6, 52, 51, tzinfo=timezone.utc),
                market_date=date(2026, 7, 31),
            )
        ]

        serialized = build_news_list(articles, [])[0].model_dump(mode="json")

        self.assertEqual(serialized["published_at"], "2026-07-31T15:52:51+09:00")
        self.assertEqual(serialized["market_date"], "2026-07-31")

    def test_response_carries_article_and_analysis_together(self) -> None:
        articles = [make_article(1)]
        evidences = [make_evidence(1, 1, "코스피는 267.75p 내렸다.")]

        serialized = build_news_list(articles, evidences)[0].model_dump(mode="json")

        self.assertEqual(serialized["market_date"], "2026-07-13")
        self.assertEqual(serialized["brief_type"], "morning")
        self.assertEqual(serialized["label"], "NEG")
        self.assertEqual(
            serialized["summary"], "코스피가 대형주 약세에 밀려 하락했습니다."
        )
        self.assertEqual(serialized["evidence"][0]["sentence"], "코스피는 267.75p 내렸다.")


if __name__ == "__main__":
    unittest.main()
