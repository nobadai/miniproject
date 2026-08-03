"""뉴스 수집 서비스의 기간·제목 필터와 적재 건너뛰기를 검증한다."""

import unittest
from datetime import date, datetime

from app.clients.fnnews_client import KST, ArticleCandidate
from app.schemas.news import NewsArticle
from app.services.news_collector import collect_news_articles


def make_candidate(article_id: str, title: str) -> ArticleCandidate:
    return ArticleCandidate(
        title=title,
        url=f"https://www.fnnews.com/news/{article_id}",
        published_at=datetime(2026, 7, 15, 10, 30, tzinfo=KST),
    )


def make_article(
    candidate: ArticleCandidate,
    *,
    brief_type: str = "morning",
) -> NewsArticle:
    return NewsArticle(
        title=candidate.title,
        published_at="2026-07-15T10:30:00+09:00",
        body="코스피와 코스닥의 오전 장 흐름을 정리한 테스트 본문입니다.",
        source="파이낸셜뉴스",
        url=candidate.url,
        brief_type=brief_type,
        collected_at="2026-08-03T12:00:00+09:00",
    )


class FakeFnNewsClient:
    """상세 페이지 방문 여부까지 관찰할 수 있는 수집 Client 대역이다."""

    def __init__(
        self,
        pages: dict[int, list[ArticleCandidate]],
        articles: dict[str, NewsArticle | RuntimeError | None],
    ) -> None:
        self.pages = pages
        self.articles = articles
        self.visited_urls: list[str] = []
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

    def read_article(self, candidate: ArticleCandidate) -> NewsArticle | None:
        self.visited_urls.append(candidate.url)
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
        morning = make_candidate("202607151052129598", "코스피 혼조세 [fn오전시황]")
        unrelated = make_candidate("202607151152129599", "환율 장중 동향")
        client = FakeFnNewsClient(
            pages={1: [morning, unrelated], 2: [morning]},
            articles={
                morning.url: make_article(morning),
                unrelated.url: None,
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
        self.assertEqual(result.skipped, 0)

    def test_already_stored_article_is_skipped_without_visiting_detail(self) -> None:
        stored = make_candidate("202607151052129598", "코스피 혼조세 [fn오전시황]")
        fresh = make_candidate("202607151552129597", "코스피 상승 마감 [fn마감시황]")
        client = FakeFnNewsClient(
            pages={1: [stored, fresh], 2: []},
            articles={
                stored.url: make_article(stored),
                fresh.url: make_article(fresh, brief_type="closing"),
            },
        )

        result = collect_news_articles(
            client,
            start=date(2026, 7, 13),
            end=date(2026, 7, 31),
            max_pages=3,
            find_existing_urls=lambda urls: {stored.url} & set(urls),
        )

        self.assertEqual(client.visited_urls, [fresh.url])
        self.assertEqual(
            [str(article.url) for article in result.articles],
            [fresh.url],
        )
        self.assertEqual(result.skipped, 1)

    def test_pages_are_still_scanned_when_every_candidate_is_already_stored(
        self,
    ) -> None:
        """앞 페이지가 모두 적재된 재실행에서도 뒤 페이지까지 확인해야 한다."""

        stored = make_candidate("202607151052129598", "코스피 혼조세 [fn오전시황]")
        later = make_candidate("202607161052129596", "코스피 반등 [fn오전시황]")
        client = FakeFnNewsClient(
            pages={1: [stored], 2: [later], 3: []},
            articles={
                stored.url: make_article(stored),
                later.url: make_article(later),
            },
        )

        result = collect_news_articles(
            client,
            start=date(2026, 7, 13),
            end=date(2026, 7, 31),
            max_pages=5,
            find_existing_urls=lambda urls: {stored.url} & set(urls),
        )

        self.assertEqual(client.visited_urls, [later.url])
        self.assertEqual(
            [str(article.url) for article in result.articles],
            [later.url],
        )
        self.assertEqual(result.skipped, 1)

    def test_article_failure_is_recorded_and_next_article_continues(self) -> None:
        failed = make_candidate("202607151052129598", "접근 실패 기사 [fn오전시황]")
        closing = make_candidate("202607151752129599", "코스피 상승 마감 [fn마감시황]")
        client = FakeFnNewsClient(
            pages={1: [failed, closing], 2: []},
            articles={
                failed.url: RuntimeError("페이지 접근 실패"),
                closing.url: make_article(closing, brief_type="closing"),
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

    def test_invalid_date_range_is_rejected(self) -> None:
        client = FakeFnNewsClient(pages={}, articles={})

        with self.assertRaises(ValueError):
            collect_news_articles(
                client,
                start=date(2026, 7, 31),
                end=date(2026, 7, 13),
                max_pages=1,
            )


if __name__ == "__main__":
    unittest.main()
