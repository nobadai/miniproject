"""크롤링한 원본 뉴스의 공통 데이터 계약을 정의한다.

크롤러와 후속 요약·감성분석 기능이 제목, 본문, 게시시각, 출처를 같은
형식으로 주고받도록 검증 가능한 Pydantic Schema를 제공한다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class NewsArticle(BaseModel):
    """수집된 원본 뉴스 한 건을 표현한다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, description="기사 제목")
    published_at: datetime = Field(description="시간대가 포함된 기사 게시시각")
    body: str = Field(min_length=1, description="정제된 기사 본문")
    source: str = Field(min_length=1, description="기사 출처")
    url: HttpUrl = Field(description="기사 원문 URL")
    collected_at: datetime = Field(description="시간대가 포함된 수집시각")

    @field_validator("published_at", "collected_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        """서버 환경에 따라 시각이 달라지지 않도록 시간대를 강제한다."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("날짜와 시각에는 시간대 정보가 필요합니다.")
        return value
