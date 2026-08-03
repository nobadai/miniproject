-- 목적: Gemma 감성 판정 결과를 초기 데이터로 제공한다.
-- 주요 역할: 0001 로 적재한 기사의 판정과 근거를 news_sentiments 및
--            news_sentiment_evidences 에 연결한다.
--
-- 판정 id 는 환경마다 다르므로 기사 URL 로 연결하고, 부모 INSERT 의 RETURNING 으로
-- 자식 Row 를 잇는다. 이미 판정이 있으면 RETURNING 이 비어 근거도 들어가지 않으므로
-- 다시 실행해도 중복 적재되지 않는다.
--
-- 0001_news_articles.sql 을 먼저 적용해야 한다.
-- backend 에서 uv run python -m app.services.news_sentiment_seed 로 재생성한다.

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B12$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607131029004736$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피는 전 거래일 대비 267.75p(-3.58%) 내린 7208.19에 거래 중이다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서는 개인이 7668억원을 순매수 중이고 외국인과 기관이 각각 3221억원, 4137억원을 순매도했다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$L$seed$,
           $seed$R3$seed$, $seed$기관·외국인 순매수 및 낙폭 만회 기대와 국제유가 급등 및 긴축 우려가 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607141024477409$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$기관과 외국인이 각각 1조7743억원, 2424억원을 순매수 중인 반면 개인은 1조9911억원 매도 우위를 보이고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$김유미 키움증권 연구원은 "국제유가 급등과 미국의 추가 긴축 우려 등이 투자심리에 부담으로 작용할 수 있다"면서도 "전날 코스피가 9% 가까이 급락한 만큼 낙폭 과대 인식에 따른 저가 매수세 유입으로 낙폭을 일부 만회할 것"이라고 봤다.$seed$, $seed$ok$seed$, true)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$L$seed$,
           $seed$R3$seed$, $seed$지수 상승 및 기관·외국인 순매수와 개인 순매도 및 변동성 확대 요인이 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607141601427702$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$기관과 외국인이 각각 3조2159억원, 9528억원 매수 우위를 보였다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$장중 등락을 오가던 지수는 막판 상승세로 방향을 잡았다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B02$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607151052129598$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$외국인은 1조1634억원 사들이고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$코스피는 전 거래일 대비 467.59p(6.82%) 오른 7324.42에 거래 중이다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B04$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607151547528708$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$외국인과 기관은 각각 2조3218억원, 1824억원을 순매수했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$코스피는 전 거래일 대비 427.58p(6.24%) 오른 7284.41에 거래를 마쳤다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B03$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607161124356937$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 외국인과 기관의 쌍끌이 매도에 밀려 6700선까지 후퇴했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서는 개인이 3조2965억원을 순매수 중이며 외국인과 기관이 각각 1조6149억원, 1조8060억원을 순매도하고 있다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$코스피가 장 초반부터 4%대 급락을 보이면서 프로그램 매도호가 일시효력정지(매도 사이드카)가 발동됐다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B13$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607161617049184$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피는 전 거래일 대비 463.81p(-6.37%) 내린 6820.60에 거래를 마쳤다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서는 개인이 3조6606억원을 순매수했지만 외국인과 기관이 각각 1조3920억원, 2조3682억원어치를 순매도하며 지수를 끌어내렸다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$L$seed$,
           $seed$R2$seed$, $seed$코스피 낙폭 축소와 코스닥 약세 및 개인 매도가 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607200959156708$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피는 개장 직후 4% 넘게 급락하며 6500선까지 밀렸지만, 외국인과 기관의 순매수에 힘입어 낙폭을 줄이고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서 외국인과 기관은 각각 4165억원, 933억원을 순매수하고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B13$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607201621143101$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 20일 4% 넘게 내리며 6500선에서 거래를 마쳤다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권 및 코스닥시장에서는 장중 매도 사이드카가 잇따라 발동됐다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B04$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607211120023423$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$이날 오전 11시 기준 코스피는 전 거래일 보다 189.09p(2.90%) 오른 6705.36에 거래되고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서 기관과 외국인이 각각 5687억원, 1467억원을 순매수 중이다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$최근 국내 증시가 하락세를 거듭하자 기관과 외국인을 중심으로 저가매수세가 진행된 양상이다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B14$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607211607246838$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$유가증권시장에서 기관과 외국인이 각각 1조3745억원, 2950억원 순매수했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$코스피는 전 거래일 대비 231.68p(3.56%) 오른 6747.95에 거래를 마쳤다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B14$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607221019336026$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$22일 오전 10시 2분 기준 코스피는 전 거래일 대비 338.90p(5.02%) 오른 7086.85에 거래되고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$외국인이 1조6003억원을 순매수하며 지수를 끌어올리고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$L$seed$,
           $seed$R3$seed$, $seed$외국인 순매수와 지수 상승세가 개인·기관의 매도 및 상승분 반납과 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607221617076222$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 장 초반 5%대 급등하며 프로그램매매 매수호가 일시 효력정지(매수 사이드카)가 발동됐지만, 상승분을 반납하며 '7천피'를 지키지 못했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$외국인이 2조6119억원을 대거 순매수했지만, 개인과 기관이 각각 1조2141억원, 1조3907억원 매도 우위를 보이며 지수 상승을 제한했다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEU$seed$, $seed$L$seed$,
           $seed$R5$seed$, $seed$코스피 및 코스닥의 상승과 외국인·기관의 순매수 요인이 유가 급등 및 지정학적 리스크 등 비우호적 요인과 충돌함$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607231041533438$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$한국거래소에 따르면 23일 오전 10시50분 기준 코스피는 전 거래일 대비 2.84% 상승한 6987.50을 기록 중이다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$투자자별로는 외국인이 9420억원을 순매수 중이다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$중동발 지정학적 리스크에 따른 국제유가 상승도 투자심리를 위축시키며 3대 지수가 일제히 약세를 보였다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B02$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607231605160464$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 외국인의 2조원대 순매수에 힘입어 4% 넘게 상승했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$외국인과 기관은 각각 2조1351억원, 1011억원을 순매수했으며 개인은 2조2107억원을 순매도했다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B03$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607241124039954$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 외국인과 기관의 쌍끌이 매도세에 밀려 4%대 하락세를 보이고 있다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서는 개인이 2조9389억원을 순매수 중이고 외국인과 기관이 각각 1조8817억원, 1조913억원을 순매도하고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B13$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607241618014538$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$24일 한국거래소에 따르면 이날 코스피는 전 거래일 대비 406.27p(-5.72%) 내린 6690.62에 거래를 마쳤다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서는 개인이 6조2588억원 순매수했고, 외국인과 기관이 각각 4조2040억원, 2조1096억원 순매도했다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B03$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607271026315010$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 27일 외국인과 기관 매도세에 6500선으로 후퇴했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$국내 유가증권시장에서 개인이 1조1712억원어치 사들이는 동안 외국인과 기관은 각각 1조1921억원, 433억원어치 팔아치우고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$L$seed$,
           $seed$R3$seed$, $seed$개인·기관의 매수세와 외국인의 순매도가 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607271535539391$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 27일 개인과 기관의 쌍끌이 매수에 6700선을 회복했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$국내 유가증권시장에서 외국인이 2조9039억원어치 팔아치웠지만 개인과 기관은 각각 1조9799억원, 8623억원어치 사들였다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B07$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607281005278409$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피는 장 출발과 동시에 5% 넘게 급락하면서 오전 9시 6분께 매도 사이드카가 발동됐다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$국내 유가증권시장에서 개인이 1조6744억원어치 사들이는 동안 외국인과 기관은 각각 1조5303억원, 1508억원어치 팔아치우고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B13$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607281538171499$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$외국인은 4조9841억원을 순매도했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$코스피와 코스닥이 28일 나란히 서킷브레이커가 발동될 정도로 급락하며 국내 증시가 패닉 장세를 연출했다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$지수는 전 거래일보다 355.48p(5.26%) 하락한 6400.27에 출발한 뒤 낙폭을 빠르게 키웠다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$H$seed$,
           $seed$B07$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607291055586980$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$29일 오전 10시 51분 기준 코스피는 전 거래일보다 209.06p(3.47%) 내린 5814.60에 거래 중이다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$코스닥 시장에서는 상승 279개, 하락 1400개로 투자심리가 크게 위축됐다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$증권업계 관계자는 "전날 10% 넘게 급락한 코스피의 충격이 이어지는 가운데 외국인의 반도체 매도, 레버리지 상품 청산 물량, 위험자산 회피 심리가 겹치며 변동성이 확대되는 양상이다"라고 말했다.$seed$, $seed$ok$seed$, true)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEU$seed$, $seed$H$seed$,
           $seed$B01$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607300959317253$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 30일 장 초반 0.8%대 하락하며 보합권에서 거래되고 있다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$NEG$seed$, $seed$L$seed$,
           $seed$R3$seed$, $seed$외국인·기관의 순매수와 지수의 하락이 충돌$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607301638179200$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피가 외국인 매수세에 상승하며 6000선 탈환을 노렸으나 결국 하락 마감했다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에선 외국인과 기관이 각각 1조3252억원, 744억원 순매수했다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$코스피는 전 거래일 대비 69.68p(1.23%) 하락한 5593.56에 거래를 마쳤다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$L$seed$,
           $seed$B14$seed$, $seed$지수 급등 및 외국인 순매수와 개인의 차익실현 매물이 충돌$seed$,
           false,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607310937364196$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$전날까지 급락했던 대형 반도체주에 저가 매수세가 집중되면서 지수 상승을 이끌었다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$외국인은 이 시간 현재 유가증권시장에서 약 2조5800억원, 코스닥에서 약 807억원을 순매수하며 반등을 주도했다.$seed$, $seed$ok$seed$, false),
    (3::smallint, $seed$반면 개인은 코스피에서 2조653억원을 순매도하며 차익 실현에 나섰다.$seed$, $seed$missing$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);

WITH inserted AS (
    INSERT INTO news_sentiments (
        article_id, status, label, confidence, rule, note,
        evidence_verified, banned_hits,
        llm_model, llm_prompt_version, llm_done_reason
    )
    SELECT id, 'done', $seed$POS$seed$, $seed$H$seed$,
           $seed$B14$seed$, $seed$$seed$,
           true,
           '{}',
           $seed$gemma4:12b-it-qat$seed$, $seed$v2.0$seed$,
           $seed$stop$seed$
    FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607311547599134$seed$
    ON CONFLICT (article_id) DO NOTHING
    RETURNING id
)
INSERT INTO news_sentiment_evidences (sentiment_id, seq, sentence, verify_status, is_quote)
SELECT inserted.id, v.seq, v.sentence, v.verify_status, v.is_quote
FROM inserted, (VALUES
    (1::smallint, $seed$코스피는 전 거래일보다 1001.89p(17.91%) 오른 6595.45에 거래를 마쳤다.$seed$, $seed$ok$seed$, false),
    (2::smallint, $seed$유가증권시장에서 외국인은 5조6369억원을 순매수했다.$seed$, $seed$ok$seed$, false)
) AS v(seq, sentence, verify_status, is_quote);
