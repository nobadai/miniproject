-- 목적: 수집한 시황 뉴스 원문과 감성 판정·한 줄 요약 결과를 보관할 Table을 정의한다.
-- 주요 역할: 기사 한 건을 대장으로 두고 판정 결과와 요약 결과를 각각 자식으로 연결한다.

-- 크롤러가 수집한 기사 원문. 이후 모든 분석의 기준 원문이 된다.
-- URL 을 UNIQUE 로 두어 수집 배치를 다시 돌려도 같은 기사가 두 번 쌓이지 않는다.
-- 하루에 오전·마감 두 건이 들어오므로 market_date 에는 UNIQUE 를 걸지 않는다.
CREATE TABLE IF NOT EXISTS news_articles (
    id           BIGSERIAL   PRIMARY KEY,
    url          TEXT        NOT NULL UNIQUE,             -- Query 를 제거한 정규화 URL
    title        TEXT        NOT NULL,
    body         TEXT        NOT NULL,                    -- 정제 본문. 근거 검증의 기준 원문
    source       TEXT        NOT NULL,                    -- 기사 출처. 예: 파이낸셜뉴스
    published_at TIMESTAMPTZ NOT NULL,
    market_date  DATE        NOT NULL,                    -- published_at 의 KST 날짜. 오전·마감을 하루로 묶는다
    brief_type   TEXT        NOT NULL                     -- 수집 대상이 오전·마감 시황 두 종류로 고정되어 있다
        CHECK (brief_type IN ('morning', 'closing')),
    collected_at TIMESTAMPTZ NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 최신 날짜부터 조회하며 같은 날의 오전·마감을 함께 읽는 화면 Query 에 맞춘다.
CREATE INDEX IF NOT EXISTS idx_news_articles_market_date
    ON news_articles (market_date DESC, brief_type);


-- Gemma 감성 판정 결과. 기사 1건에 판정 1건을 둔다.
-- article_id 에 UNIQUE 를 걸어 다시 판정하면 이전 결과를 덮어쓴다.
--
-- 판정을 여러 건 쌓아 두지 않는 이유는 "이 기사의 판정"에 답이 하나여야 하기 때문이다.
-- 회차나 Prompt Version 별로 Row 를 남기면 조회할 때마다 어느 것을 볼지 걸러야 하고,
-- 한 번만 빠뜨려도 화면에 판정이 여러 개 표시된다.
--
-- Prompt 를 고쳐 이전 판정과 비교하려면 판정 결과를 database/seeds/ 에 덤프해 두고
-- 새 Prompt 로 덮어쓴 뒤 비교한다. 가끔 하는 일이라 Table 구조를 늘리지 않는다.
--
-- 판정 전 상태는 Row 가 없는 것으로 표현하며 부모 Table 에 상태 Column 을 두지 않는다.
CREATE TABLE IF NOT EXISTS news_sentiments (
    id                 BIGSERIAL   PRIMARY KEY,
    article_id         BIGINT      NOT NULL UNIQUE REFERENCES news_articles (id) ON DELETE CASCADE,

    status             TEXT        NOT NULL DEFAULT 'done'
        CHECK (status IN ('done', 'failed')),
    error              TEXT,                              -- status 가 failed 일 때만 채운다

    -- 아래 판정 Column 은 status 가 failed 이면 비어 있으므로 NOT NULL 을 걸지 않는다.
    label              VARCHAR(3)  CHECK (label IN ('POS', 'NEU', 'NEG')),
    confidence         CHAR(1)     CHECK (confidence IN ('H', 'L')),
    rule               VARCHAR(3),                        -- 규칙 코드가 늘어날 예정이라 CHECK 를 걸지 않는다
    note               TEXT        NOT NULL DEFAULT '',   -- confidence 가 L 일 때만 한 문장이 들어간다

    evidence_verified  BOOLEAN,                           -- 근거가 전부 원문에 그대로 있으면 true
    banned_hits        TEXT[]      NOT NULL DEFAULT '{}', -- note 에서 검출한 투자 권유 표현

    llm_model          TEXT        NOT NULL,              -- 예: gemma4:12b-it-qat
    -- 어느 Prompt 로 뽑은 판정인지 추적하기 위해 남긴다. Version 마다 Row 를 나누지는 않는다.
    llm_prompt_version TEXT        NOT NULL,              -- 예: v2.0
    llm_done_reason    TEXT,                              -- stop 이 아니면 응답이 잘린 것이다
    -- num_ctx·num_gpu·think 는 Settings 고정값이라 전 Row 가 같으므로 저장하지 않는다.

    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now() -- 다시 판정해 덮어쓴 시각
);


-- 판정 근거 문장. 판정 1건에 1~3개가 붙고 문장마다 검증 결과가 다르다.
-- 문장·검증상태·인용여부를 배열 세 개로 두면 Index 를 서로 맞춰야 뜻이 통하므로
-- 문장 하나를 한 Row 로 눕혀 verify_status 를 Query 조건으로 쓸 수 있게 한다.
CREATE TABLE IF NOT EXISTS news_sentiment_evidences (
    id            BIGSERIAL PRIMARY KEY,
    sentiment_id  BIGINT    NOT NULL REFERENCES news_sentiments (id) ON DELETE CASCADE,
    seq           SMALLINT  NOT NULL,                     -- 모델이 내놓은 순서. 1부터 시작한다
    sentence      TEXT      NOT NULL,
    verify_status TEXT      NOT NULL                      -- missing 은 환각, partial 은 문장 중간 발췌다
        CHECK (verify_status IN ('ok', 'missing', 'partial')),
    is_quote      BOOLEAN   NOT NULL DEFAULT FALSE,       -- 전문가 인용이면 화면에 출처를 병기한다

    UNIQUE (sentiment_id, seq)
);

-- 화면에는 verify_status 가 ok 인 근거만 내보내므로 판정별 조회에 이 Index 를 사용한다.
CREATE INDEX IF NOT EXISTS idx_news_sentiment_evidences_sentiment
    ON news_sentiment_evidences (sentiment_id);


-- Gemini 한 줄 요약. 기사 1건에 요약 1건을 두며 다시 요약하면 덮어쓴다.
-- 감성 판정과 서로를 기다리지 않도록 별도 Table 로 분리한다.
CREATE TABLE IF NOT EXISTS news_summaries (
    id         BIGSERIAL   PRIMARY KEY,
    article_id BIGINT      NOT NULL UNIQUE REFERENCES news_articles (id) ON DELETE CASCADE,

    status     TEXT        NOT NULL DEFAULT 'done'
        CHECK (status IN ('done', 'failed')),
    error      TEXT,                                      -- status 가 failed 일 때만 채운다

    summary    TEXT,                                      -- 줄바꿈 없는 한 문장. status 가 failed 이면 비어 있다
    llm_model  TEXT        NOT NULL,                      -- 예: gemini-3.1-flash-lite

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()         -- 다시 요약해 덮어쓴 시각
);
