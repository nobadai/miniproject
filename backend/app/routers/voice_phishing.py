"""보이스피싱 오디오 업로드 분석 Endpoint를 제공한다.

multipart 오디오 파일을 받아 준비된 녹취 기반 분석 서비스를 호출하고
프로젝트 공통 응답 구조로 결과와 예상 오류를 반환한다.
"""

from fastapi import APIRouter, File, Response, UploadFile, status

from ..schemas.api_response import ApiResponse
from ..schemas.voice_phishing import VoicePhishingAnalysis
from ..services.voice_phishing import (
    PreparedTranscriptNotFoundError,
    UnsupportedAudioFormatError,
    analyze_prepared_audio,
)


router = APIRouter()


@router.post(
    "/analysis",
    response_model=ApiResponse[VoicePhishingAnalysis],
    status_code=status.HTTP_201_CREATED,
)
def analyze_audio(
    response: Response,
    file: UploadFile = File(description="분석할 MP3, WAV 또는 M4A 오디오"),
) -> ApiResponse[VoicePhishingAnalysis]:
    """업로드 오디오와 같은 식별자의 준비된 녹취를 분석한다."""
    if file.filename is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(success=False, message="오디오 파일명이 필요합니다.")
    try:
        analysis = VoicePhishingAnalysis(**analyze_prepared_audio(file.filename))
    except UnsupportedAudioFormatError as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(success=False, message=str(error))
    except PreparedTranscriptNotFoundError as error:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ApiResponse(success=False, message=str(error))
    except (FileNotFoundError, RuntimeError) as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(success=False, message=str(error))
    return ApiResponse(
        success=True,
        data=analysis,
        message="보이스피싱 분석이 완료되었습니다.",
    )
