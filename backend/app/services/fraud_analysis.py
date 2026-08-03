"""fraud_analysis.py
레이어: Services
역할: 업로드된 이미지를 Claude Vision Client에 전달하고, 결과를 검증해
      FraudAnalysisResult로 반환하는 핵심 비즈니스 로직을 담당한다.
"""

import logging

from ..clients import claude_vision_client
from ..repositories import fraud_analysis as fraud_analysis_repository
from ..schemas.fraud_analysis import FraudAnalysisResult


logger = logging.getLogger(__name__)


def analyze_fraud_image(image_bytes: bytes, media_type: str) -> FraudAnalysisResult:
    """이미지를 분석해 사기 탐지 결과를 반환한다. 분석 실패 시 예외를 그대로 전파한다.

    결과 DB 저장은 부가 기능이므로 저장이 실패해도 판정 결과 응답 자체는 그대로 반환한다.
    """

    try:
        raw_result = claude_vision_client.analyze_image(image_bytes, media_type)
        result = FraudAnalysisResult.model_validate(raw_result)
    except Exception:
        logger.exception("사기 화면 탐지 분석 실패")
        raise

    try:
        fraud_analysis_repository.insert_fraud_analysis_result(
            verdict=result.verdict,
            confidence=result.confidence,
            reasoning=result.reasoning,
            undetermined_reason=result.undetermined_reason,
            tamper_types=result.tamper_types,
            raw_response=raw_result,
        )
    except Exception:
        logger.exception("사기 탐지 결과 DB 저장 실패")

    return result
