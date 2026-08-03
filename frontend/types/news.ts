// 목적: 금융 뉴스 감성 분석(news) 화면에서 사용하는 타입을 정의한다.
// 주요 역할: 아직 Backend 구현이 없는 기능이라 Frontend 전용 더미 데이터 구조를 정의한다.
//           실제 API가 붙으면 Backend 응답 계약에 맞춰 재검토가 필요하다.
//
// 주의: 이 파일은 camelCase(sessionLabel 등)로 정의되어 있는데,
// 프로젝트 규칙(6.4)상 실제 API Request/Response JSON Field는
// snake_case를 써야 한다. 지금은 Backend가 없어 예외로 두었을 뿐, 나중에 실제
// 뉴스 API가 나오면 Backend는 snake_case로 응답을 줄 가능성이 높고 그러면 이
// camelCase 필드명과 그대로 안 맞을 수 있다. 연동 시에는 API 응답용 타입을
// snake_case로 새로 정의하고, 이 화면 전용 타입과는 매핑해서 쓰는 방식을 검토해야 한다.

export type NewsSession = "morning" | "close";
export type NewsSentiment = "pos" | "neg" | "neu";

export interface NewsArticle {
  id: number;
  session: NewsSession;
  sentiment: NewsSentiment;
  title: string;
  source: string;
  sessionLabel: string;
  time: string;
  summary: string;
  reason: string;
  body: string;
}

