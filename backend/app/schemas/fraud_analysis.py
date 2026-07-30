"""fraud_analysis.py
레이어: Schemas
역할: 사기 화면 탐지(fraud_analysis) 기능의 API Response 데이터 계약을 정의한다.
"""

from typing import Literal

from pydantic import BaseModel


class FraudAnalysisResult(BaseModel):
    """Claude Vision 분석 결과를 표현하는 Response Schema이다."""

    verdict: Literal["정상", "사기의심", "판단불가"]
    tamper_types: list[str]
    reasoning: str
    confidence: float
    undetermined_reason: str | None = None
