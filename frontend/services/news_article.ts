// 목적: 보유 투자 상품과 맞춤 뉴스 데이터를 화면에 제공한다.
// 주요 역할: 뉴스 API가 준비되기 전까지 동일한 계약의 임시 데이터를 반환한다.
//
// Backend에 뉴스 Endpoint가 추가되면 아래 두 함수 내부만 postJson 호출로
// 바꾸면 되도록, 화면에는 처음부터 비동기 함수 형태로 노출한다.

import type { InvestmentHolding, NewsArticle } from "../types/news_article";

const INVESTMENT_HOLDINGS: InvestmentHolding[] = [
  {
    holding_id: "samsung-electronics",
    name: "삼성전자",
    category: "국내 주식",
    return_rate: 4.2,
  },
  {
    holding_id: "kodex-200",
    name: "KODEX 200",
    category: "국내 ETF",
    return_rate: 1.8,
  },
  {
    holding_id: "sp500-etf",
    name: "미국 S&P500 ETF",
    category: "해외 ETF",
    return_rate: 7.6,
  },
  {
    holding_id: "time-deposit",
    name: "정기예금 (1년)",
    category: "예적금",
    return_rate: 3.1,
  },
];

const NEWS_ARTICLES: NewsArticle[] = [
  {
    article_id: "news-001",
    holding_id: "samsung-electronics",
    title: "삼성전자, 반도체 실적 개선에 주가 3% 상승",
    summary:
      "메모리 반도체 가격이 회복되면서 이번 분기 영업이익이 시장 예상을 웃돌았습니다. 보유하고 계신 삼성전자 주식에 좋은 소식입니다.",
    source: "한국경제",
    published_at: "2026-07-31T09:20:00",
    impact: "호재",
  },
  {
    article_id: "news-002",
    holding_id: "time-deposit",
    title: "한국은행 기준금리 동결, 예금 금리는 소폭 하락 전망",
    summary:
      "기준금리가 유지되면서 은행들이 예금 금리를 조금씩 내리고 있습니다. 만기가 다가온 정기예금은 재예치 조건을 확인해 보세요.",
    source: "연합뉴스",
    published_at: "2026-07-31T08:05:00",
    impact: "악재",
  },
  {
    article_id: "news-003",
    holding_id: "sp500-etf",
    title: "미국 증시 사상 최고치 경신, S&P500 지수 1.2% 상승",
    summary:
      "물가 지표가 안정세를 보이면서 미국 대형주 중심으로 매수세가 이어졌습니다. 해외 ETF 수익률에 긍정적인 영향이 예상됩니다.",
    source: "매일경제",
    published_at: "2026-07-30T22:40:00",
    impact: "호재",
  },
  {
    article_id: "news-004",
    holding_id: "kodex-200",
    title: "코스피 2,700선 등락 반복, 당분간 박스권 전망",
    summary:
      "외국인 매수와 기관 매도가 맞서면서 지수가 좁은 폭에서 움직이고 있습니다. 지수를 따라가는 ETF는 큰 변동이 없을 것으로 보입니다.",
    source: "서울경제",
    published_at: "2026-07-30T17:10:00",
    impact: "중립",
  },
  {
    article_id: "news-005",
    holding_id: "samsung-electronics",
    title: "금융감독원, 고배당 종목 사칭 투자 리딩방 주의보",
    summary:
      "유명 기업 이름을 내걸고 원금을 보장한다며 접근하는 투자방 피해가 늘고 있습니다. 원금 보장을 약속하는 투자 권유는 모두 사기입니다.",
    source: "금융감독원",
    published_at: "2026-07-30T11:00:00",
    impact: "악재",
  },
  {
    article_id: "news-006",
    holding_id: "sp500-etf",
    title: "환율 1,340원대 안정, 해외 투자 환차손 부담 줄어",
    summary:
      "원달러 환율이 완만하게 내려오면서 해외 자산의 환율 부담이 줄었습니다. 달러로 투자한 ETF의 원화 환산 수익에 영향을 줍니다.",
    source: "한국경제",
    published_at: "2026-07-29T15:35:00",
    impact: "중립",
  },
];

export async function fetchInvestmentHoldings(): Promise<InvestmentHolding[]> {
  return INVESTMENT_HOLDINGS;
}

export async function fetchNewsArticles(): Promise<NewsArticle[]> {
  return NEWS_ARTICLES;
}
