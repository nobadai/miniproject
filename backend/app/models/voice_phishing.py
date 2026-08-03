"""voice_phishing.py
레이어: Models
역할: 보이스피싱 업로드와 분석 이력 Table의 Row 구조를 정의한다.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VoicePhishingUpload:
    """voice_phishing_uploads Table의 Row이다."""

    id: int
    original_filename: str
    stored_path: str
    content_hash: str
    media_extension: str
    byte_size: int
    created_at: datetime


@dataclass(frozen=True)
class VoicePhishingAnalysisRecord:
    """voice_phishing_analyses Table의 Row이다."""

    id: int
    user_id: int
    upload_id: int
    transcript_id: str
    prediction: str
    fusion_score: float
    fusion_raw_score: float
    rule_score: float
    sequence_score: float
    koelectra_score: float
    rule_categories: list[str]
    transitions: list[str]
    decision_reason: str
    turns: list[dict]
    created_at: datetime
