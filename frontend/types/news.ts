// 목적: 금융 뉴스 감성 분석(news) 화면에서 사용하는 타입을 정의한다.
// 주요 역할: Backend GET /news(backend/app/schemas/news.py의 News)의 실제 응답
//           구조를 그대로 미러링한다(2026-08-03 실제 코드 대조 완료).
//
// 주의: Backend는 뉴스 한 건에 별도 id를 내려주지 않는다(News Response Schema에
// 의도적으로 id가 빠져 있음 — backend/app/schemas/news.py 주석 참고). 화면에서
// 뉴스 한 건을 식별할 때는 원문 URL(url)을 고유 키로 쓴다.

export type NewsBriefType = "morning" | "closing";

// backend/app/clients/gemma_client.py의 SENTIMENT_SCHEMA가 정한 값 그대로다.
// 요약·판정 배치가 아직 처리하지 않은 기사는 null로 내려온다.
export type NewsLabel = "POS" | "NEU" | "NEG";

export interface NewsEvidence {
  sentence: string;
  is_quote: boolean;
}

export interface NewsArticle {
  market_date: string;
  brief_type: NewsBriefType;
  title: string;
  published_at: string;
  url: string;
  source: string;
  body: string;
  summary: string | null;
  label: NewsLabel | null;
  evidence: NewsEvidence[];
}
