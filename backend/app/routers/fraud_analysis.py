"""fraud_analysis.py
레이어: Routers
역할: 사기 화면 탐지(fraud_analysis) 기능의 Endpoint를 정의한다.
      파일명(fraud_analysis.py) 기준으로 `/fraud-analysis` Prefix가 자동 등록된다.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..schemas.api_response import ApiResponse
from ..schemas.fraud_analysis import FraudAnalysisResult
from ..services import fraud_analysis as fraud_analysis_service


router = APIRouter()

ALLOWED_MEDIA_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


@router.post("", response_model=ApiResponse[FraudAnalysisResult], status_code=201)
async def analyze_fraud_screenshot(
    file: UploadFile = File(...),
) -> ApiResponse[FraudAnalysisResult]:
    """은행/카드/간편결제 앱 화면 캡처를 업로드받아 사기 여부를 분석한다."""

    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    image_bytes = await file.read()

    result = fraud_analysis_service.analyze_fraud_image(image_bytes, file.content_type)

    return ApiResponse(success=True, data=result, message="요청이 정상적으로 처리되었습니다.")
