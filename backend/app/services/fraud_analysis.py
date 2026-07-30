"""fraud_analysis.py
레이어: Services
역할: 업로드된 이미지를 Claude Vision Client에 전달하고, 결과를 검증해
      FraudAnalysisResult로 반환하는 핵심 비즈니스 로직을 담당한다.
"""

import logging

from ..clients import claude_vision_client
from ..schemas.fraud_analysis import FraudAnalysisResult


logger = logging.getLogger(__name__)


def analyze_fraud_image(image_bytes: bytes, media_type: str) -> FraudAnalysisResult:
    """이미지를 분석해 사기 탐지 결과를 반환한다. 실패 시 예외를 그대로 전파한다."""

    try:
        raw_result = claude_vision_client.analyze_image(image_bytes, media_type)
        return FraudAnalysisResult.model_validate(raw_result)
    except Exception:
        logger.exception("사기 화면 탐지 분석 실패")
        raise
