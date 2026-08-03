// 목적: 금융 뉴스 감성 분석 API 통신 함수를 정의한다.
// 주요 역할: 지금은 components/news/news_data.ts의 더미 배열을 그대로 반환한다.
//           실제 백엔드 연동 시에는 이 두 함수의 내부(현재 더미 배열 반환)만
//           fetch 호출로 교체하면 되고, 호출하는 화면 쪽은 수정할 필요가 없다.
//           뉴스 감성분석은 아직 백엔드 API가 없어 응답 형태가 확정되지 않은
//           상태이며, 자세한 내용은 types/news.ts 상단 주석을 참고한다.

import { NEWS_ARTICLES } from "../components/news/news_data";
import type { NewsArticle } from "../types/news";

// TODO: 백엔드 API 확정 후 NEXT_PUBLIC_API_BASE_URL 기준 GET /news-article 로 교체한다.
export async function getNewsArticles(): Promise<NewsArticle[]> {
  return NEWS_ARTICLES;
}

// TODO: 백엔드 API 확정 후 NEXT_PUBLIC_API_BASE_URL 기준 GET /news-article/{id} 로 교체한다.
export async function getNewsArticleById(id: number): Promise<NewsArticle | null> {
  return NEWS_ARTICLES.find((article) => article.id === id) ?? null;
}
