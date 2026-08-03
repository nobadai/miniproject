"""fraud_analysis.py
레이어: Repositories
역할: 사기 화면 탐지(fraud_analysis) 판정 결과를 fraud_analysis_results Table에 저장한다.
"""

from typing import Any

from psycopg.types.json import Json

from . import db


INSERT_SQL = """
INSERT INTO fraud_analysis_results
    (verdict, confidence, reasoning, undetermined_reason, tamper_types, raw_response)
VALUES
    (%(verdict)s, %(confidence)s, %(reasoning)s, %(undetermined_reason)s, %(tamper_types)s, %(raw_response)s)
"""


def insert_fraud_analysis_result(
    verdict: str,
    confidence: float,
    reasoning: str,
    undetermined_reason: str | None,
    tamper_types: list[str],
    raw_response: dict[str, Any],
) -> None:
    """사기 탐지 판정 결과 한 건을 저장한다. 실패 시 예외를 그대로 전파한다."""

    db.save(
        INSERT_SQL,
        {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "undetermined_reason": undetermined_reason,
            "tamper_types": tamper_types,
            "raw_response": Json(raw_response),
        },
    )
