"""금융 뉴스 한 줄 요약의 생성 결과 계약을 정의한다.

Gemini 구조화 출력으로 받는 요약 내용과 원본 기사에 연결해 저장하거나
API로 전달할 최종 요약 결과를 각각 검증한다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class NewsSummaryContent(BaseModel):
    """Gemini가 생성해야 하는 한 줄 요약 내용이다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    summary: str = Field(
        min_length=10,
        max_length=120,
        description="줄바꿈 없는 한국어 한 문장 뉴스 요약",
    )

    @field_validator("summary")
    @classmethod
    def validate_single_line(cls, value: str) -> str:
        if "\n" in value or "\r" in value:
            raise ValueError("한 줄 요약에는 줄바꿈을 포함할 수 없습니다.")
        return value


class NewsSummary(BaseModel):
    """원본 기사와 생성 정보를 포함한 최종 한 줄 요약 결과다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    article_url: HttpUrl
    summary: str = Field(min_length=10, max_length=120)
    model: str = Field(min_length=1)
    summarized_at: datetime

    @field_validator("summary")
    @classmethod
    def validate_single_line(cls, value: str) -> str:
        if "\n" in value or "\r" in value:
            raise ValueError("한 줄 요약에는 줄바꿈을 포함할 수 없습니다.")
        return value

    @field_validator("summarized_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("요약시각에는 시간대 정보가 필요합니다.")
        return value
