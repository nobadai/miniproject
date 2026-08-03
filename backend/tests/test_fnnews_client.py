"""파이낸셜뉴스 Client의 브라우저 비의존 변환 로직을 검증한다."""

import unittest
from datetime import date

from app.clients.fnnews_client import (
    KST,
    build_search_url,
    datetime_from_article_url,
    normalize_body,
    normalize_fnnews_url,
    parse_datetime,
)


class FnNewsClientUtilityTests(unittest.TestCase):
    def test_search_url_contains_date_range_and_page_offset(self) -> None:
        url = build_search_url(
            start=date(2026, 7, 13),
            end=date(2026, 7, 31),
            page=3,
        )

        self.assertIn("ds=2026.07.13", url)
        self.assertIn("de=2026.07.31", url)
        self.assertIn("start=21", url)
        self.assertIn("news_office_checked=1014", url)

    def test_fnnews_url_is_normalized(self) -> None:
        normalized = normalize_fnnews_url(
            "http://fnnews.com/news/202607151052129598?source=naver"
        )

        self.assertEqual(
            normalized,
            "https://www.fnnews.com/news/202607151052129598",
        )

    def test_other_domain_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            normalize_fnnews_url("https://example.com/news/202607151052129598")

    def test_article_url_date_is_korean_time(self) -> None:
        parsed = datetime_from_article_url(
            "https://www.fnnews.com/news/202607151052129598"
        )

        self.assertEqual(parsed.date(), date(2026, 7, 15))
        self.assertEqual(parsed.tzinfo, KST)

    def test_iso_datetime_is_converted_to_korean_time(self) -> None:
        parsed = parse_datetime("2026-07-15T01:30:00+00:00")

        self.assertEqual(parsed.isoformat(), "2026-07-15T10:30:00+09:00")

    def test_body_whitespace_is_normalized(self) -> None:
        normalized = normalize_body(" 첫 문단  입니다.\n\n 둘째\t문단입니다. ")

        self.assertEqual(normalized, "첫 문단 입니다.\n\n둘째 문단입니다.")


if __name__ == "__main__":
    unittest.main()
