// 목적: 맞춤 뉴스 기사 한 건을 카드 형태로 표시한다.
// 주요 역할: 관련 상품, 영향 구분, 제목, 요약, 출처를 큰 글씨로 보여준다.

import type { NewsArticle, NewsImpact } from "../../types/news_article";
import { formatPublishedAt } from "../../utils/format";

interface NewsArticleCardProps {
  article: NewsArticle;
  holdingName: string;
}

const IMPACT_STYLE: Record<NewsImpact, string> = {
  호재: "bg-safe-soft text-safe",
  악재: "bg-danger-soft text-danger",
  중립: "bg-canvas text-ink-soft",
};

export default function NewsArticleCard({
  article,
  holdingName,
}: NewsArticleCardProps) {
  return (
    <article className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-brand-soft px-3 py-1 text-sm font-bold text-brand">
          {holdingName}
        </span>
        <span
          className={`rounded-full px-3 py-1 text-sm font-bold ${
            IMPACT_STYLE[article.impact]
          }`}
        >
          {article.impact}
        </span>
      </div>

      <h3 className="mt-3 text-xl font-bold text-ink">{article.title}</h3>
      <p className="mt-2 text-base text-ink-soft">{article.summary}</p>

      <p className="mt-4 text-sm text-ink-soft">
        {article.source} · {formatPublishedAt(article.published_at)}
      </p>
    </article>
  );
}
