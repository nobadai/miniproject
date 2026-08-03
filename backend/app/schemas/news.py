"""뉴스 원문과 조회 API의 데이터 계약을 정의한다.

크롤러와 후속 요약·감성분석 기능이 제목, 본문, 게시시각, 출처를 같은
형식으로 주고받도록 검증 가능한 Pydantic Schema를 제공하고, 원문에 한 줄 요약과
감성 판정을 합쳐 화면으로 내보내는 Response Schema를 함께 둔다.
"""

from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    computed_field,
    field_validator,
)


KST = ZoneInfo("Asia/Seoul")

BriefType = Literal["morning", "closing"]


class NewsArticle(BaseModel):
    """수집된 원본 뉴스 한 건을 표현한다."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, description="기사 제목")
    published_at: datetime = Field(description="시간대가 포함된 기사 게시시각")
    body: str = Field(min_length=1, description="정제된 기사 본문")
    source: str = Field(min_length=1, description="기사 출처")
    url: HttpUrl = Field(description="기사 원문 URL")
    brief_type: BriefType = Field(description="시황 구분. 오전 또는 마감")
    collected_at: datetime = Field(description="시간대가 포함된 수집시각")

    @field_validator("published_at", "collected_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        """서버 환경에 따라 시각이 달라지지 않도록 시간대를 강제한다."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("날짜와 시각에는 시간대 정보가 필요합니다.")
        return value

    @computed_field(description="오전·마감 기사를 하루로 묶는 장 기준일")
    @property
    def market_date(self) -> date:
        """게시시각의 한국 시간 날짜를 장 기준일로 사용한다."""

        return self.published_at.astimezone(KST).date()


class NewsEvidence(BaseModel):
    """감성 판정의 근거 문장 한 건이다."""

    sentence: str = Field(description="본문에서 그대로 옮긴 근거 문장")
    is_quote: bool = Field(description="전문가 인용이면 화면에 출처를 병기한다")


class News(BaseModel):
    """뉴스 원문에 한 줄 요약과 감성 판정을 합친 조회 결과다.

    confidence·rule·note 와 검증 필드는 내부 지표이므로 넣지 않는다.
    Response Schema에서 제외해야 화면 노출 사고가 구조적으로 차단된다.
    """

    market_date: date
    brief_type: BriefType
    title: str
    published_at: datetime
    url: HttpUrl
    source: str
    body: str
    # 요약·판정 배치가 아직 처리하지 않은 기사도 목록에 나와야 하므로 비워둘 수 있다.
    summary: str | None = None
    label: str | None = None
    evidence: list[NewsEvidence] = Field(default_factory=list)
