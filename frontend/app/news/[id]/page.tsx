// 목적: 금융 뉴스 상세 페이지(동적 라우트)를 정의한다.
// 주요 역할: services/news.ts에서 뉴스 id에 해당하는 데이터를 가져와 본문과 감성 판단 근거를 보여준다.

import Link from "next/link";
import { notFound } from "next/navigation";
import { getNewsArticleById } from "../../../services/news";
import { SENTIMENT_LABEL } from "../../../components/news/news_data";
import type { NewsArticle } from "../../../types/news";

const SENTIMENT_CLASS: Record<NewsArticle["sentiment"], string> = {
  pos: "bg-safe-bg text-safe",
  neg: "bg-alert-bg text-alert",
  neu: "bg-line-soft text-ink-sub",
};

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const article = await getNewsArticleById(Number(id));

  if (!article) {
    notFound();
  }

  return (
    <div className="mx-auto max-w-[720px] border border-line bg-white p-8">
      <Link
        href="/news"
        className="mb-5 inline-flex items-center gap-1.5 text-[13px] font-semibold text-ink-sub"
      >
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.6}
        >
          <path d="M15 6l-6 6 6 6" />
        </svg>
        목록으로
      </Link>

      <div className="mb-2.5 text-[19px] font-bold leading-[1.5] text-ink">
        {article.title}
      </div>
      <div className="mb-[18px] border-b border-line-soft pb-[18px] text-[12.5px] text-ink-sub">
        {article.source} · {article.sessionLabel} · {article.time}
      </div>

      <div className="mb-3 text-sm font-medium leading-[1.75] text-ink-body">
        {article.summary}
      </div>

      <div className="mb-4 flex items-center gap-2">
        <span
          className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${SENTIMENT_CLASS[article.sentiment]}`}
        >
          {SENTIMENT_LABEL[article.sentiment]}
        </span>
        <span className="text-[12.5px] leading-[1.6] text-ink-sub">
          <b className="font-semibold text-ink">근거</b> — {article.reason}
        </span>
      </div>

      <div className="border-t border-line-soft pt-4 text-[13.5px] leading-[1.9] text-ink-body">
        {article.body}
      </div>
    </div>
  );
}
