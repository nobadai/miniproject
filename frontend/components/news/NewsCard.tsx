// 목적: 금융 뉴스 목록의 한 행(제목 + 감성 배지)을 표시한다.
// 주요 역할: 클릭 시 해당 뉴스 상세 페이지(app/news/[id])로 이동한다.

import Link from "next/link";
import type { NewsArticle } from "../../types/news";
import { SENTIMENT_LABEL } from "./news_data";

const SENTIMENT_CLASS: Record<NewsArticle["sentiment"], string> = {
  pos: "bg-safe-bg text-safe",
  neg: "bg-alert-bg text-alert",
  neu: "bg-line-soft text-ink-sub",
};

export default function NewsCard({ article }: { article: NewsArticle }) {
  return (
    <div className="border-b border-line-soft last:border-b-0">
      <Link
        href={`/news/${article.id}`}
        className="flex items-center gap-3 px-1 py-[15px]"
      >
        <span
          className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${SENTIMENT_CLASS[article.sentiment]}`}
        >
          {SENTIMENT_LABEL[article.sentiment]}
        </span>
        <span className="flex-1 text-[14.5px] font-semibold text-ink">
          {article.title}
        </span>
        <svg
          className="h-4 w-4 shrink-0 text-[#9aa1ab]"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.6}
        >
          <path d="M9 6l6 6-6 6" />
        </svg>
      </Link>
    </div>
  );
}
