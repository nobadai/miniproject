-- 목적: 사기 화면 및 보이스피싱 분석 결과를 사용자와 연결한다.
-- 주요 역할: 인증된 사용자의 분석 이력을 분리하고 사용자별 조회 기반을 제공한다.

-- 사기 화면 분석 결과를 요청 사용자와 연결한다.
ALTER TABLE fraud_analysis_results
    ADD COLUMN user_id BIGINT NOT NULL;

ALTER TABLE fraud_analysis_results
    ADD CONSTRAINT fk_fraud_analysis_results_user
        FOREIGN KEY (user_id) REFERENCES users (id);

CREATE INDEX idx_fraud_analysis_results_user_created
    ON fraud_analysis_results (user_id, created_at DESC);

COMMENT ON COLUMN fraud_analysis_results.user_id IS
    '사기 화면 분석을 요청한 사용자 식별 번호';

COMMENT ON CONSTRAINT fk_fraud_analysis_results_user
ON fraud_analysis_results IS
    '사기 화면 분석 결과를 요청 사용자와 연결하는 외래 키';

COMMENT ON INDEX idx_fraud_analysis_results_user_created IS
    '사용자별 사기 화면 분석 이력을 최신순으로 조회하기 위한 인덱스';

-- 보이스피싱 분석 결과를 요청 사용자와 연결한다.
ALTER TABLE voice_phishing_analyses
    ADD COLUMN user_id BIGINT NOT NULL;

ALTER TABLE voice_phishing_analyses
    ADD CONSTRAINT fk_voice_phishing_analyses_user
        FOREIGN KEY (user_id) REFERENCES users (id);

CREATE INDEX idx_voice_phishing_analyses_user_upload_created
    ON voice_phishing_analyses (user_id, upload_id, created_at DESC);

COMMENT ON COLUMN voice_phishing_analyses.user_id IS
    '보이스피싱 분석을 요청한 사용자 식별 번호';

COMMENT ON CONSTRAINT fk_voice_phishing_analyses_user
ON voice_phishing_analyses IS
    '보이스피싱 분석 결과를 요청 사용자와 연결하는 외래 키';

COMMENT ON INDEX idx_voice_phishing_analyses_user_upload_created IS
    '사용자와 업로드별 보이스피싱 분석 이력을 최신순으로 조회하기 위한 인덱스';
