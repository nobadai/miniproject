-- 목적: Gemini 한 줄 요약 결과를 초기 데이터로 제공한다.
-- 주요 역할: 0001 로 적재한 기사 26건의 요약을 news_summaries 에 연결한다.
--
-- 원본 JSONL 이 기사 URL 로만 연결되므로 news_articles 를 조회해 article_id 를 얻는다.
-- 0001_news_articles.sql 을 먼저 적용해야 한다.

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피 지수가 SK하이닉스와 삼성전기 등 주요 대형주가 약세를 보인 영향으로 장중 하락 폭을 키우며 7200선에서 거래되고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:11:11+09:00', '2026-08-03T12:11:11+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607131029004736$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 기관과 외국인의 대규모 매수세에 힘입어 장 초반 상승 전환하며 7000선 회복을 시도하고 있으며 삼성전자와 SK하이닉스 등 주요 대형주가 상승을 견인하고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:14+09:00', '2026-08-03T12:12:14+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607141024477409$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 삼성전자와 SK하이닉스의 3%대 반등에 힘입어 상승 마감했으나, 코스닥은 하락하며 매도 사이드카가 발동되는 등 엇갈린 흐름을 보였습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:16+09:00', '2026-08-03T12:12:16+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607141601427702$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$뉴욕 증시의 AI 반도체주 강세와 미국 소비자물가지수 하락에 따른 투자 심리 개선으로 삼성전자와 SK하이닉스가 급등하며 코스피가 7300선을 회복하고 매수 사이드카가 발동되었습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:18+09:00', '2026-08-03T12:12:18+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607151052129598$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$미국 소비자물가지수 둔화에 따른 긴축 우려 완화와 외국인 및 기관의 대규모 매수세가 유입되면서 삼성전자와 SK하이닉스 등 반도체주 강세에 힘입어 코스피가 6%대 급등하며 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:20+09:00', '2026-08-03T12:12:20+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607151547528708$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 외국인과 기관의 대규모 매도세로 7% 넘게 급락하며 매도 사이드카가 발동된 가운데, 특히 반도체 등 대형주 위주로 하락세가 두드러지고 있다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:22+09:00', '2026-08-03T12:12:22+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607161124356937$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 인공지능 거품론 확산에 따른 미국 반도체주 약세와 국내 대형 반도체주의 동반 급락 여파로 6.37% 하락하며 6820선에서 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:24+09:00', '2026-08-03T12:12:24+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607161617049184$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피는 장 초반 4% 넘게 급락했으나 외국인과 기관의 순매수 유입으로 낙폭을 줄이며 6700선대를 회복했고, 코스닥은 외국인과 기관의 매도세에 2%대 약세를 보이고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:26+09:00', '2026-08-03T12:12:26+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607200959156708$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$AI 투자 수익성 우려와 중동발 에너지 불안, 반도체주 약세 등이 겹치며 코스피와 코스닥이 급락해 장중 매도 사이드카가 발동되었습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:29+09:00', '2026-08-03T12:12:29+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607201621143101$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 최근 지수 하락에 따른 기관과 외국인의 저가 매수세 유입으로 2.90% 상승한 6700선에서 거래되고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:31+09:00', '2026-08-03T12:12:31+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607211120023423$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$반도체를 비롯한 수출 실적의 역대 최대치 달성 소식에 기관과 외국인의 매수세가 유입되면서 코스피 지수가 6700선을 회복했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:33+09:00', '2026-08-03T12:12:33+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607211607246838$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$알파벳의 실적 발표를 앞두고 AI 수요에 대한 기대감이 확산되면서 외국인의 대규모 매수세가 유입되어 코스피가 5% 이상 급등했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:35+09:00', '2026-08-03T12:12:35+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607221019336026$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피는 장 초반 급등하며 매수 사이드카가 발동됐으나 외국인의 대규모 순매수에도 불구하고 개인과 기관의 매도세에 밀려 상승분을 반납하며 6797.70에 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:37+09:00', '2026-08-03T12:12:37+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607221617076222$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$알파벳의 호실적 발표와 반도체주 강세에 힘입어 코스피가 3% 가까이 오르며 7000선 회복을 시도하고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:40+09:00', '2026-08-03T12:12:40+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607231041533438$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$알파벳 실적 호조에 따른 AI 산업 성장 기대감이 유입되며 외국인의 대규모 매수세에 힘입어 코스피와 코스닥이 각각 4%와 5%대 급등세를 보였습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:42+09:00', '2026-08-03T12:12:42+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607231605160464$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 외국인과 기관의 동반 매도세가 이어지며 전 거래일 대비 4% 이상 하락해 6780선에서 거래되고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:44+09:00', '2026-08-03T12:12:44+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607241124039954$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 인공지능 관련 투자 비용 부담에 따른 수익성 우려와 중동 지정학적 리스크가 겹치며 외국인과 기관의 대규모 매도세로 5% 넘게 급락했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:12:46+09:00', '2026-08-03T12:12:46+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607241618014538$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피 지수가 외국인과 기관의 동반 매도세가 이어지며 전 거래일 대비 1.52% 하락한 6589선에서 거래되고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:16+09:00', '2026-08-03T12:15:16+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607271026315010$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피 지수가 외국인의 대규모 매도세에도 불구하고 개인과 기관의 동반 매수세가 유입되면서 전 거래일 대비 0.97% 상승한 6755.75에 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:22+09:00', '2026-08-03T12:15:22+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607271535539391$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피와 코스닥 지수가 장 초반 급락하며 매도 사이드카가 발동된 가운데, 외국인과 기관의 매도세가 이어지며 코스피는 6200선으로 하락했다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:28+09:00', '2026-08-03T12:15:28+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607281005278409$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$글로벌 반도체 업황 불확실성과 AI 투자 부담이 겹치며 외국인의 대규모 매도세로 코스피가 10% 넘게 급락해 6000선이 붕괴됐습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:34+09:00', '2026-08-03T12:15:34+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607281538171499$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 반도체주 중심의 외국인 매도세와 투자 심리 위축 여파로 전날 급락에 이어 6000선을 하회하며 장중 약세를 지속하고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:40+09:00', '2026-08-03T12:15:40+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607291055586980$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피는 미 연준의 금리 동결과 매파적 발언에 따른 부담으로 0.8%대 하락하며 5614선에서 거래되고 있으나, 연이은 급락에 따른 저가 매수세가 유입되며 반등을 시도하고 있습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:46+09:00', '2026-08-03T12:15:46+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607300959317253$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피는 외국인과 기관의 매수세 유입에도 불구하고 삼성전자를 비롯한 주요 종목에서 차익 실현 매물이 출회하며 전 거래일 대비 1.23% 하락한 5593.56에 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:52+09:00', '2026-08-03T12:15:52+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607301638179200$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$코스피가 전날 급락에 따른 기술적 반등과 외국인의 대규모 저가 매수세 유입에 힘입어 하루 만에 14% 이상 급등하며 6400선을 회복했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:15:58+09:00', '2026-08-03T12:15:58+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607310937364196$seed$
ON CONFLICT (article_id) DO NOTHING;

INSERT INTO news_summaries (article_id, summary, llm_model, created_at, updated_at)
SELECT id, $seed$미국 빅테크 실적 호조와 AI 투자 기대감에 힘입어 외국인 매수세가 유입되면서 코스피가 종가 기준 역대 최대인 17.91% 급등하며 마감했습니다.$seed$, $seed$gemini-3.1-flash-lite$seed$, '2026-08-03T12:16:04+09:00', '2026-08-03T12:16:04+09:00'
FROM news_articles WHERE url = $seed$https://www.fnnews.com/news/202607311547599134$seed$
ON CONFLICT (article_id) DO NOTHING;
