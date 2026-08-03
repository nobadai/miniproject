"""voice_phishing.py
레이어: Repositories
역할: 보이스피싱 업로드 메타데이터와 분석 이력의 저장·조회 Query를 관리한다.
"""

from typing import Any

from psycopg.types.json import Json

from ..models.voice_phishing import (
    VoicePhishingAnalysisRecord,
    VoicePhishingUpload,
)
from . import db


INSERT_UPLOAD_SQL = """
    INSERT INTO voice_phishing_uploads (
        original_filename, stored_path, content_hash, media_extension, byte_size
    )
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (content_hash)
    DO UPDATE SET stored_path = voice_phishing_uploads.stored_path
    RETURNING id
"""
SELECT_UPLOAD_BY_HASH_SQL = """
    SELECT id, original_filename, stored_path, content_hash,
           media_extension, byte_size, created_at
    FROM voice_phishing_uploads
    WHERE content_hash = %s
"""
INSERT_ANALYSIS_SQL = """
    INSERT INTO voice_phishing_analyses (
        user_id, upload_id, transcript_id, prediction, fusion_score,
        fusion_raw_score, rule_score, sequence_score, koelectra_score,
        rule_categories, transitions, decision_reason, turns
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id
"""
SELECT_LATEST_ANALYSIS_SQL = """
    SELECT id, user_id, upload_id, transcript_id, prediction, fusion_score,
           fusion_raw_score, rule_score, sequence_score, koelectra_score,
           rule_categories, transitions, decision_reason, turns, created_at
    FROM voice_phishing_analyses
    WHERE upload_id = %s
      AND user_id = %s
    ORDER BY created_at DESC, id DESC
    LIMIT 1
"""


def save_upload(
    original_filename: str,
    stored_path: str,
    content_hash: str,
    media_extension: str,
    byte_size: int,
) -> int:
    """업로드 메타데이터를 저장하고 식별자를 반환한다.

    같은 내용을 다시 올리면 content_hash 제약에 걸린다. 이때 Insert 를 실패로
    두면 호출부가 다시 조회해야 하므로, 값을 바꾸지 않는 Update 로 기존 Row 를
    그대로 두면서 id 만 돌려받는다.
    """
    row = db.find_one(
        INSERT_UPLOAD_SQL,
        (original_filename, stored_path, content_hash, media_extension, byte_size),
    )
    if row is None:
        raise RuntimeError("업로드 정보를 저장하지 못했습니다.")
    return int(row["id"])


def find_upload_by_content_hash(content_hash: str) -> VoicePhishingUpload | None:
    """파일 내용 해시로 이미 저장된 업로드를 찾는다."""
    row = db.find_one(SELECT_UPLOAD_BY_HASH_SQL, (content_hash,))
    if row is None:
        return None
    return VoicePhishingUpload(
        id=int(row["id"]),
        original_filename=row["original_filename"],
        stored_path=row["stored_path"],
        content_hash=row["content_hash"],
        media_extension=row["media_extension"],
        byte_size=int(row["byte_size"]),
        created_at=row["created_at"],
    )


def save_analysis(
    upload_id: int,
    analysis: dict[str, Any],
    *,
    user_id: int,
) -> int:
    """사용자의 분석 결과 한 건을 저장하고 식별자를 반환한다."""
    row = db.find_one(
        INSERT_ANALYSIS_SQL,
        (
            user_id,
            upload_id,
            analysis["transcript_id"],
            analysis["prediction"],
            analysis["fusion_score"],
            analysis["fusion_raw_score"],
            analysis["rule_score"],
            analysis["sequence_score"],
            analysis["koelectra_score"],
            analysis["rule_categories"],
            analysis["transitions"],
            analysis["decision_reason"],
            Json(analysis["turns"]),
        ),
    )
    if row is None:
        raise RuntimeError("분석 결과를 저장하지 못했습니다.")
    return int(row["id"])


def find_latest_analysis(
    upload_id: int,
    *,
    user_id: int,
) -> VoicePhishingAnalysisRecord | None:
    """해당 사용자와 업로드의 가장 최근 분석 결과를 조회한다."""
    row = db.find_one(SELECT_LATEST_ANALYSIS_SQL, (upload_id, user_id))
    if row is None:
        return None
    return VoicePhishingAnalysisRecord(
        id=int(row["id"]),
        user_id=int(row["user_id"]),
        upload_id=int(row["upload_id"]),
        transcript_id=row["transcript_id"],
        prediction=row["prediction"],
        # 점수 Column 은 NUMERIC 이라 Decimal 로 돌아온다. 응답 Schema 가 float
        # 이므로 Repository 경계에서 변환해 이후 계층이 Decimal 을 다루지 않게 한다.
        fusion_score=float(row["fusion_score"]),
        fusion_raw_score=float(row["fusion_raw_score"]),
        rule_score=float(row["rule_score"]),
        sequence_score=float(row["sequence_score"]),
        koelectra_score=float(row["koelectra_score"]),
        rule_categories=list(row["rule_categories"]),
        transitions=list(row["transitions"]),
        decision_reason=row["decision_reason"],
        turns=list(row["turns"]),
        created_at=row["created_at"],
    )
