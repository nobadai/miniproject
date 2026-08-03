-- 목적: 사기 화면 탐지(fraud_analysis) 판정 결과를 저장할 Table을 최초 정의한다.
-- 주요 역할: Claude Vision 판정 결과(verdict, confidence, reasoning 등)와 원본 응답을 적재한다.

CREATE TABLE IF NOT EXISTS fraud_analysis_results (
    id BIGSERIAL PRIMARY KEY,
    verdict TEXT NOT NULL CHECK (verdict IN ('정상', '사기의심', '판단불가')),
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    reasoning TEXT NOT NULL,
    undetermined_reason TEXT,
    tamper_types TEXT[] NOT NULL DEFAULT '{}',
    raw_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
