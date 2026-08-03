"""보이스피싱 오디오 업로드 분석 Endpoint를 제공한다.

multipart 오디오 파일을 받아 STT 전사 기반 분석 서비스를 호출하고
프로젝트 공통 응답 구조로 결과와 예상 오류를 반환한다.
"""

from fastapi import APIRouter, File, Response, UploadFile, status

from ..clients.whisper_client import EmptyTranscriptionError
from ..schemas.api_response import ApiResponse
from ..schemas.voice_phishing import VoicePhishingAnalysis
from ..services.voice_phishing import (
    UnsupportedAudioFormatError,
    analyze_uploaded_audio,
)


router = APIRouter()

# 영상 파일은 같은 통화 길이라도 오디오보다 훨씬 크다. 업로드 본문을
# 메모리로 읽기 전에 크기를 먼저 확인해 과도한 적재를 막는다.
MAX_UPLOAD_MEGABYTES = 200
MAX_UPLOAD_BYTES = MAX_UPLOAD_MEGABYTES * 1024 * 1024


@router.post(
    "/analysis",
    response_model=ApiResponse[VoicePhishingAnalysis],
    status_code=status.HTTP_201_CREATED,
)
def analyze_audio(
    response: Response,
    file: UploadFile = File(
        description="분석할 오디오(MP3, WAV, M4A) 또는 영상(MP4, MOV, AVI, MKV, WEBM)"
    ),
) -> ApiResponse[VoicePhishingAnalysis]:
    """업로드 오디오를 전사하고 보이스피싱 위험도를 분석한다.

    STT와 모델 추론은 통화 길이에 비례해 오래 걸리는 동기 작업이다.
    async 로 선언하면 Event Loop 를 점유해 다른 요청까지 막히므로,
    FastAPI 가 Threadpool 에서 실행하도록 동기 함수로 둔다.
    """
    if file.filename is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(success=False, message="오디오 파일명이 필요합니다.")

    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(
            success=False,
            message=f"파일이 너무 큽니다. {MAX_UPLOAD_MEGABYTES}MB 이하만 올릴 수 있습니다.",
        )

    audio_bytes = file.file.read()
    if not audio_bytes:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(success=False, message="오디오 파일이 비어 있습니다.")

    try:
        analysis = VoicePhishingAnalysis(
            **analyze_uploaded_audio(audio_bytes, file.filename)
        )
    except (UnsupportedAudioFormatError, EmptyTranscriptionError) as error:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ApiResponse(success=False, message=str(error))
    except (FileNotFoundError, RuntimeError) as error:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return ApiResponse(success=False, message=str(error))
    return ApiResponse(
        success=True,
        data=analysis,
        message="보이스피싱 분석이 완료되었습니다.",
    )
