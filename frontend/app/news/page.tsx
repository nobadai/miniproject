// 목적: 보유 금융상품과 관련된 맞춤 뉴스 화면을 정의한다.
// 주요 역할: 보유 상품과 기사 데이터를 불러와 요약과 목록 Component에 전달한다.

import PageHeading from "../../components/commons/page_heading";
import HoldingSummary from "../../components/news/holding_summary";
import NewsFeed from "../../components/news/news_feed";
import {
  fetchInvestmentHoldings,
  fetchNewsArticles,
} from "../../services/news_article";

export default async function NewsPage() {
  const holdings = await fetchInvestmentHoldings();
  const articles = await fetchNewsArticles();

  return (
    <div className="flex flex-col gap-6">
      <PageHeading
        title="내 맞춤 뉴스"
        description="가입하신 금융상품과 관련된 소식만 모아서 보여드려요."
      />

      <HoldingSummary holdings={holdings} />

      <NewsFeed holdings={holdings} articles={articles} />
    </div>
  );
}
