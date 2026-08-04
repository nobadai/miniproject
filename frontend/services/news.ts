// 목적: 금융 뉴스 감성 분석 API 통신 함수를 정의한다.
// 주요 역할: Backend에서 뉴스 목록을 가져온다(확정 — GET /news). 단건 조회 API가
//           없어 getNewsArticleById는 전체 목록을 가져와 원문 URL로 필터링하는
//           방식을 유지한다(Backend 응답에 별도 id가 없으므로 url을 식별자로 쓴다).
//           app/news/page.tsx(Server Component)가 이 함수를 호출하는데, 뉴스는
//           주기적으로 갱신되는 데이터라 Next.js의 Fetch Cache에 태우지 않는다
//           (cache: "no-store") — 안 그러면 최초 빌드 시점(Backend 응답)이 그대로
//           굳어 이후 실제 뉴스가 갱신돼도 화면에 반영되지 않는다(Docker 실기동
//           검증 중 발견).

import type { NewsArticle } from "../types/news";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

export async function getNewsArticles(): Promise<NewsArticle[]> {
  const url = buildApiUrl("/news");

  let response: Response;
  try {
    response = await fetch(url, { method: "GET", cache: "no-store" });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<NewsArticle[]>(
    response,
    "뉴스 목록을 불러오지 못했습니다."
  );
}

export async function getNewsArticleById(
  articleUrl: string
): Promise<NewsArticle | null> {
  const articles = await getNewsArticles();
  return articles.find((article) => article.url === articleUrl) ?? null;
}
