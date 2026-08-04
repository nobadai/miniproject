// 목적: 금융 뉴스 목록의 한 행(제목 + 감성 배지 + 게시일)을 표시한다.
// 주요 역할: 클릭 시 해당 뉴스 상세 페이지(app/news/[url])로 이동한다. Backend가
//           뉴스 id를 내려주지 않아 원문 URL을 Base64url로 인코딩해 경로에 쓴다.
//           encodeURIComponent가 만드는 %2F(인코딩된 슬래시)는 Next.js 라우터가
//           경로 구분자로 다시 풀어버려 단일 동적 세그먼트에 매칭되지 않는다.
//           isLatest가 true면(현재 필터링된 목록의 맨 위 1건) 제목 끝에 NEW 배지를 붙인다.

import Link from "next/link";
import type { NewsArticle } from "../../types/news";
import { encodeBase64Url } from "../../utils/base64_url";
import {
  NEWS_LABEL_CLASS,
  NEWS_LABEL_TEXT,
  NEWS_LABEL_UNRESOLVED_CLASS,
  NEWS_LABEL_UNRESOLVED_TEXT,
  formatNewsListDate,
} from "./news_labels";

export default function NewsCard({
  article,
  isLatest,
}: {
  article: NewsArticle;
  isLatest?: boolean;
}) {
  const badgeClass = article.label
    ? NEWS_LABEL_CLASS[article.label]
    : NEWS_LABEL_UNRESOLVED_CLASS;
  const badgeText = article.label
    ? NEWS_LABEL_TEXT[article.label]
    : NEWS_LABEL_UNRESOLVED_TEXT;

  return (
    <div className="border-b border-line-soft last:border-b-0">
      <Link
        href={`/news/${encodeBase64Url(article.url)}`}
        className="flex items-center gap-3 px-1 py-[15px]"
      >
        <span
          className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${badgeClass}`}
        >
          {badgeText}
        </span>
        <span className="flex-1 text-[14.5px] font-semibold text-ink">
          {article.title}
          {isLatest && (
            <span className="ml-1.5 rounded-[3px] bg-alert px-1.5 py-0.5 align-middle text-[10px] font-bold text-white">
              NEW
            </span>
          )}
        </span>
        <span className="shrink-0 text-[11.5px] text-ink-sub">
          {formatNewsListDate(article.published_at)}
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
