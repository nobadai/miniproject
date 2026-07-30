"""보이스피싱 오디오 분석 API의 응답 계약을 정의한다.

준비된 녹취와 규칙·시퀀스·KoELECTRA 융합 결과를 snake_case 구조로
클라이언트에 전달한다.
"""

from pydantic import BaseModel


class VoicePhishingTurn(BaseModel):
    """분석에 사용한 화자별 발화이다."""

    idx: int
    speaker: str
    text: str


class VoicePhishingAnalysis(BaseModel):
    """오디오 파일에 대응하는 보이스피싱 분석 결과이다."""

    audio_filename: str
    transcript_id: str
    prediction: str
    fusion_score: float
    rule_score: float
    rule_categories: list[str]
    sequence_score: float
    transitions: list[str]
    koelectra_score: float
    decision_reason: str
    turns: list[VoicePhishingTurn]
