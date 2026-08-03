"""파이낸셜뉴스 기사 탐색과 원문 추출을 담당한다.

네이버 뉴스 검색과 파이낸셜뉴스 원문 페이지에 Selenium으로 접근하고,
서비스 계층이 사용할 기사 후보와 원문 데이터를 반환한다.
"""

from __future__ import annotations

import logging
import random
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

from ..schemas.news import BriefType, NewsArticle

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


logger = logging.getLogger(__name__)

NAVER_NEWS_SEARCH_URL = "https://search.naver.com/search.naver"
SEARCH_QUERY = "fn 시황"
FNNEWS_OFFICE_ID = "1014"
SOURCE_NAME = "파이낸셜뉴스"
KST = ZoneInfo("Asia/Seoul")

# 파이낸셜뉴스가 시황 기사 제목 끝에 붙이는 고정 표기다.
BRIEF_TYPE_MARKERS: dict[str, BriefType] = {
    "[fn오전시황]": "morning",
    "[fn마감시황]": "closing",
}

SEARCH_RESULT_LINK_SELECTOR = 'a[href*="fnnews.com/news/"]'
ARTICLE_TITLE_SELECTOR = "h1.article-view__title"
ARTICLE_BODY_SELECTOR = ".article-view__body"
PUBLISHED_META_SELECTOR = 'meta[property="article:published_time"]'


@dataclass(frozen=True)
class ArticleCandidate:
    """검색 결과에서 발견한 파이낸셜뉴스 기사 후보다."""

    title: str
    url: str
    published_at: datetime


class FnNewsClientError(RuntimeError):
    """브라우저 또는 대상 페이지 접근 실패를 서비스 계층에 전달한다."""


def parse_datetime(value: str) -> datetime:
    """목록과 메타태그의 날짜 문자열을 한국 시간으로 변환한다."""

    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed = datetime.strptime(normalized, "%Y-%m-%d %H:%M:%S")

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=KST)
    return parsed.astimezone(KST)


def build_search_url(*, start: date, end: date, page: int) -> str:
    """언론사와 날짜 범위를 적용한 네이버 뉴스 검색 URL을 만든다."""

    start_compact = start.strftime("%Y%m%d")
    end_compact = end.strftime("%Y%m%d")
    parameters = {
        "where": "news",
        "query": SEARCH_QUERY,
        "sort": "1",
        "photo": "0",
        "field": "0",
        "pd": "3",
        "ds": start.strftime("%Y.%m.%d"),
        "de": end.strftime("%Y.%m.%d"),
        "mynews": "1",
        "office_type": "1",
        "office_section_code": "1",
        "news_office_checked": FNNEWS_OFFICE_ID,
        "nso": f"so:dd,p:from{start_compact}to{end_compact},a:all",
        "start": str((page - 1) * 10 + 1),
    }
    return f"{NAVER_NEWS_SEARCH_URL}?{urlencode(parameters)}"


def normalize_fnnews_url(value: str) -> str:
    """검색 결과 URL을 쿼리 없는 파이낸셜뉴스 HTTPS URL로 통일한다."""

    parsed = urlsplit(value)
    if parsed.netloc not in {"fnnews.com", "www.fnnews.com"}:
        raise ValueError(f"파이낸셜뉴스 URL이 아닙니다: {value}")
    if not re.fullmatch(r"/news/\d+", parsed.path):
        raise ValueError(f"파이낸셜뉴스 기사 URL 형식이 아닙니다: {value}")
    return urlunsplit(("https", "www.fnnews.com", parsed.path, "", ""))


def datetime_from_article_url(value: str) -> datetime:
    """기사 ID 앞의 YYYYMMDD를 후보 기사의 임시 게시일로 사용한다."""

    match = re.search(r"/news/(\d{8})", value)
    if not match:
        raise ValueError(f"기사 URL에서 날짜를 찾지 못했습니다: {value}")
    parsed_date = datetime.strptime(match.group(1), "%Y%m%d").date()
    return datetime.combine(parsed_date, datetime.min.time(), tzinfo=KST)


def resolve_brief_type(title: str) -> BriefType | None:
    """제목의 시황 표기로 오전·마감을 구분하고 시황이 아니면 None을 반환한다."""

    for marker, brief_type in BRIEF_TYPE_MARKERS.items():
        if marker in title:
            return brief_type
    return None


def normalize_body(text: str) -> str:
    """불필요한 공백을 정리하면서 기사 문단 구분을 유지한다."""

    paragraphs: list[str] = []
    for line in text.replace("\u00a0", " ").splitlines():
        cleaned = re.sub(r"[ \t]+", " ", line).strip()
        if cleaned:
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs)


class FnNewsClient:
    """Selenium WebDriver 수명과 파이낸셜뉴스 페이지 접근을 관리한다."""

    def __init__(
        self,
        driver: "WebDriver",
        *,
        output_directory: Path,
        request_delay: float,
    ) -> None:
        self.driver = driver
        self.output_directory = output_directory
        self.request_delay = request_delay

    def close(self) -> None:
        from selenium.common.exceptions import WebDriverException

        try:
            self.driver.quit()
        except WebDriverException as error:
            logger.warning("Chrome WebDriver 종료 실패: %s", error)

    def wait_between_requests(self) -> None:
        if self.request_delay <= 0:
            return
        jitter = random.uniform(0, min(self.request_delay * 0.25, 0.5))
        time.sleep(self.request_delay + jitter)

    def read_candidates(
        self,
        *,
        page: int,
        start: date,
        end: date,
    ) -> list[ArticleCandidate]:
        """네이버 뉴스 검색 한 페이지에서 파이낸셜뉴스 원문 후보를 찾는다."""

        from selenium.common.exceptions import TimeoutException, WebDriverException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as expected
        from selenium.webdriver.support.ui import WebDriverWait

        url = build_search_url(start=start, end=end, page=page)
        try:
            self.driver.get(url)
        except WebDriverException as error:
            raise FnNewsClientError(
                f"네이버 뉴스 검색 페이지 접근에 실패했습니다: {url}"
            ) from error
        try:
            WebDriverWait(self.driver, 15).until(
                expected.presence_of_element_located((By.CSS_SELECTOR, "#main_pack"))
            )
        except TimeoutException as error:
            screenshot_path = self._save_search_screenshot(
                f"naver_search_error_page_{page}.png"
            )
            raise FnNewsClientError(
                "네이버 검색 결과 컨테이너를 찾지 못했습니다. "
                f"스크린샷={screenshot_path}, URL={url}"
            ) from error

        candidates: list[ArticleCandidate] = []
        seen_urls: set[str] = set()
        try:
            links = self.driver.find_elements(
                By.CSS_SELECTOR, SEARCH_RESULT_LINK_SELECTOR
            )
        except WebDriverException as error:
            raise FnNewsClientError(
                f"네이버 검색 결과 링크를 읽지 못했습니다: {url}"
            ) from error
        for link in links:
            try:
                href = link.get_attribute("href") or ""
                if not href:
                    continue
                normalized_url = normalize_fnnews_url(href)
                if normalized_url in seen_urls:
                    continue
                seen_urls.add(normalized_url)
                candidates.append(
                    ArticleCandidate(
                        title=link.text.strip(),
                        url=normalized_url,
                        published_at=datetime_from_article_url(normalized_url),
                    )
                )
            except (ValueError, WebDriverException) as error:
                logger.warning("검색 결과 링크 해석 실패(page=%s): %s", page, error)

        if page == 1 and not candidates:
            screenshot_path = self._save_search_screenshot(
                "naver_search_no_links_page_1.png"
            )
            raise FnNewsClientError(
                "첫 검색 페이지에서 파이낸셜뉴스 원문 링크를 찾지 못했습니다. "
                f"스크린샷={screenshot_path}"
            )
        return candidates

    def read_article(self, candidate: ArticleCandidate) -> NewsArticle | None:
        """상세 페이지에서 기사를 추출하고 시황 기사가 아니면 None을 반환한다."""

        from selenium.common.exceptions import TimeoutException, WebDriverException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as expected
        from selenium.webdriver.support.ui import WebDriverWait

        try:
            self.driver.get(candidate.url)
        except WebDriverException as error:
            raise FnNewsClientError(
                f"파이낸셜뉴스 기사 페이지 접근에 실패했습니다: {candidate.url}"
            ) from error
        wait = WebDriverWait(self.driver, 15)
        try:
            title_element = wait.until(
                expected.presence_of_element_located(
                    (By.CSS_SELECTOR, ARTICLE_TITLE_SELECTOR)
                )
            )
            body_element = wait.until(
                expected.presence_of_element_located(
                    (By.CSS_SELECTOR, ARTICLE_BODY_SELECTOR)
                )
            )
        except TimeoutException as error:
            raise FnNewsClientError(
                f"기사 제목 또는 본문을 찾지 못했습니다: {candidate.url}"
            ) from error

        try:
            title = title_element.text.strip()
        except WebDriverException as error:
            raise FnNewsClientError(
                f"기사 제목을 읽지 못했습니다: {candidate.url}"
            ) from error

        # 본문을 읽기 전에 걸러 시황이 아닌 기사의 파싱 비용을 아낀다.
        brief_type = resolve_brief_type(title)
        if brief_type is None:
            return None

        try:
            paragraph_texts = [
                paragraph.text.strip()
                for paragraph in body_element.find_elements(By.CSS_SELECTOR, "p")
                if paragraph.text.strip()
            ]
            body_text = (
                "\n\n".join(paragraph_texts)
                if paragraph_texts
                else body_element.text
            )
        except WebDriverException as error:
            raise FnNewsClientError(
                f"기사 본문을 읽지 못했습니다: {candidate.url}"
            ) from error
        body = normalize_body(body_text)
        if not body:
            raise FnNewsClientError(
                f"정제 후 기사 본문이 비어 있습니다: {candidate.url}"
            )

        published_at = self._read_published_at(candidate)
        return NewsArticle(
            title=title,
            published_at=published_at,
            body=body,
            source=SOURCE_NAME,
            url=candidate.url,
            brief_type=brief_type,
            collected_at=datetime.now(KST).replace(microsecond=0),
        )

    def _read_published_at(self, candidate: ArticleCandidate) -> datetime:
        from selenium.common.exceptions import NoSuchElementException, WebDriverException
        from selenium.webdriver.common.by import By

        try:
            meta_value = self.driver.find_element(
                By.CSS_SELECTOR, PUBLISHED_META_SELECTOR
            ).get_attribute("content")
            if meta_value:
                return parse_datetime(meta_value)
        except (NoSuchElementException, ValueError, WebDriverException) as error:
            logger.debug("게시일 메타태그 확인 실패: %s", error)

        try:
            article_view = self.driver.find_element(
                By.CSS_SELECTOR, "article.article-view"
            ).text
        except (NoSuchElementException, WebDriverException):
            return candidate.published_at

        match = re.search(
            r"입력\s*(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})",
            article_view,
        )
        if not match:
            return candidate.published_at
        return datetime(*(int(part) for part in match.groups()), tzinfo=KST)

    def _save_search_screenshot(self, filename: str) -> Path | None:
        from selenium.common.exceptions import WebDriverException

        self.output_directory.mkdir(parents=True, exist_ok=True)
        screenshot_path = self.output_directory / filename
        try:
            self.driver.save_screenshot(str(screenshot_path))
        except WebDriverException as error:
            logger.warning("오류 화면 저장 실패: %s", error)
            return None
        return screenshot_path.resolve()


def create_fnnews_client(
    *,
    headed: bool,
    output_directory: Path,
    request_delay: float,
) -> FnNewsClient:
    """Chrome WebDriver를 구성해 파이낸셜뉴스 Client를 생성한다."""

    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException

    if request_delay < 0:
        raise ValueError("request_delay는 0 이상이어야 합니다.")

    options = webdriver.ChromeOptions()
    if not headed:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1600")
    options.add_argument("--lang=ko-KR")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
    except WebDriverException as error:
        raise FnNewsClientError(
            "Chrome WebDriver를 시작하지 못했습니다. Chrome 설치 상태를 확인하세요."
        ) from error
    return FnNewsClient(
        driver,
        output_directory=output_directory,
        request_delay=request_delay,
    )
