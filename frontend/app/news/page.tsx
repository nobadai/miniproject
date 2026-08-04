// 목적: 금융 뉴스 감성 분석 목록 페이지의 진입점을 정의한다.
// 주요 역할: services/news.ts에서 뉴스 목록을 가져와 필터 UI(Client Component)에 전달한다.
//           Backend 호출이 실패해도 페이지 전체가 깨지지 않도록 빈 목록으로 대체한다.

import { getNewsArticles } from "../../services/news";
import NewsListView from "./NewsListView";

export default async function NewsPage() {
  const articles = await getNewsArticles().catch(() => []);
  return <NewsListView articles={articles} />;
}
