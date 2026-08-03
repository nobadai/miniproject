"""원본 뉴스 Pydantic 스키마의 필드와 검증 규칙을 확인한다."""

import unittest
from datetime import datetime

from pydantic import ValidationError

from app.clients.fnnews_client import KST
from app.schemas.news import NewsArticle


def valid_article_data() -> dict[str, object]:
    return {
        "title": "코스피 상승 마감 [fn마감시황]",
        "published_at": "2026-07-31T17:10:00+09:00",
        "body": "코스피와 코스닥의 마감 흐름을 정리한 기사 본문입니다.",
        "source": "파이낸셜뉴스",
        "url": "https://www.fnnews.com/news/202607311710000001",
        "collected_at": datetime(2026, 8, 3, 12, 0, tzinfo=KST),
    }


class NewsArticleSchemaTests(unittest.TestCase):
    def test_valid_article_is_serialized_as_json_compatible_values(self) -> None:
        article = NewsArticle.model_validate(valid_article_data())

        serialized = article.model_dump(mode="json")

        self.assertEqual(serialized["source"], "파이낸셜뉴스")
        self.assertEqual(serialized["published_at"], "2026-07-31T17:10:00+09:00")
        self.assertEqual(
            serialized["url"],
            "https://www.fnnews.com/news/202607311710000001",
        )

    def test_empty_title_is_rejected(self) -> None:
        data = valid_article_data()
        data["title"] = "   "

        with self.assertRaises(ValidationError):
            NewsArticle.model_validate(data)

    def test_datetime_without_timezone_is_rejected(self) -> None:
        data = valid_article_data()
        data["published_at"] = datetime(2026, 7, 31, 17, 10)

        with self.assertRaises(ValidationError):
            NewsArticle.model_validate(data)

    def test_unknown_field_is_rejected(self) -> None:
        data = valid_article_data()
        data["summary"] = "아직 원본 뉴스 스키마에 포함하지 않는 필드"

        with self.assertRaises(ValidationError):
            NewsArticle.model_validate(data)


if __name__ == "__main__":
    unittest.main()
