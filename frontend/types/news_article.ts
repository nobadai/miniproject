// 목적: 맞춤 뉴스 화면이 사용하는 Domain Type을 정의한다.
// 주요 역할: 보유 투자 상품과 관련 뉴스 기사의 Field 계약을 한곳에서 관리한다.
//
// 뉴스 API는 Backend에 아직 존재하지 않으므로, 향후 추가될 Endpoint와
// 그대로 맞출 수 있도록 API JSON 규칙인 snake_case Field를 사용한다.

export type NewsImpact = "호재" | "악재" | "중립";

export interface InvestmentHolding {
  holding_id: string;
  name: string;
  category: string;
  return_rate: number;
}

export interface NewsArticle {
  article_id: string;
  holding_id: string;
  title: string;
  summary: string;
  source: string;
  published_at: string;
  impact: NewsImpact;
}
