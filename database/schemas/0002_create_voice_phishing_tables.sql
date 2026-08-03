-- 목적: 보이스피싱 검사에 사용한 업로드 파일과 분석 결과를 보관할 Table을 정의한다.
-- 주요 역할: 업로드 원본 메타데이터와 분석 이력을 분리해 저장하고 서로 연결한다.

-- 원본 파일 자체는 Disk에 두고 여기에는 위치와 식별 정보만 남긴다.
-- 통화 영상은 파일 하나가 수백MB까지 커져 Database에 직접 담기에 적합하지 않다.
CREATE TABLE IF NOT EXISTS voice_phishing_uploads (
    id                BIGSERIAL PRIMARY KEY,
    original_filename TEXT        NOT NULL,                    -- 사용자가 올린 이름
    stored_path       TEXT        NOT NULL,                    -- 저장 Root 기준 상대 경로
    content_hash      CHAR(64)    NOT NULL UNIQUE,             -- 파일 내용 sha256. 재업로드 식별에 사용
    media_extension   TEXT        NOT NULL,                    -- 소문자 확장자. 예: .mp3, .mp4
    byte_size         BIGINT      NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 같은 파일을 여러 번 검사할 수 있으므로 업로드와 분석을 1:N으로 둔다.
CREATE TABLE IF NOT EXISTS voice_phishing_analyses (
    id               BIGSERIAL PRIMARY KEY,
    upload_id        BIGINT       NOT NULL REFERENCES voice_phishing_uploads (id) ON DELETE CASCADE,
    transcript_id    TEXT         NOT NULL,                    -- 확장자를 제외한 분석 식별자
    prediction       TEXT         NOT NULL,                    -- suspicious / normal / unknown
    fusion_score     NUMERIC(8, 6) NOT NULL,                   -- 판정에 맞춰 보정한 최종 점수
    fusion_raw_score NUMERIC(8, 6) NOT NULL,                   -- 보정 전 가중합 점수
    rule_score       NUMERIC(8, 6) NOT NULL,
    sequence_score   NUMERIC(8, 6) NOT NULL,
    koelectra_score  NUMERIC(8, 6) NOT NULL,
    rule_categories  TEXT[]       NOT NULL DEFAULT '{}',
    transitions      TEXT[]       NOT NULL DEFAULT '{}',
    decision_reason  TEXT         NOT NULL,
    turns            JSONB        NOT NULL,                    -- 발화 목록은 길이가 가변이라 JSONB로 둔다
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- 재업로드 시 직전 분석을 되돌려주기 위해 upload_id + 최신순 조회를 사용한다.
CREATE INDEX IF NOT EXISTS idx_voice_phishing_analyses_upload_created
    ON voice_phishing_analyses (upload_id, created_at DESC);
