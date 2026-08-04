// 목적: 금융 뉴스 상세 페이지(동적 라우트)를 정의한다.
// 주요 역할: services/news.ts에서 뉴스 원문 URL에 해당하는 데이터를 가져와 본문과
//           감성 판정 근거를 보여준다. Backend가 뉴스 id를 내려주지 않아(2026-08-03
//           실제 코드 대조 완료) 원문 URL을 Base64url로 인코딩한 값을 라우트
//           파라미터로 쓰고, 여기서 decode해 services/news.ts에 그대로 전달한다.
//           (encodeURIComponent로 만든 %2F는 Next.js 라우터가 실제 경로 구분자로
//           풀어버려 단일 동적 세그먼트에 매칭되지 않는 문제가 있어 Base64url로
//           바꿨다 — docker compose 실기동 검증 중 발견.)
//           Backend 호출 실패도 "찾을 수 없음"과 동일하게 처리해 404로 보여준다
//           (별도 에러 화면이 없어 빈 화면/스택 트레이스보다 404가 더 안전한 대체 UI).

import Link from "next/link";
import { notFound } from "next/navigation";
import { getNewsArticleById } from "../../../services/news";
import { decodeBase64Url } from "../../../utils/base64_url";
import {
  NEWS_BRIEF_TYPE_LABEL,
  NEWS_LABEL_CLASS,
  NEWS_LABEL_TEXT,
  NEWS_LABEL_UNRESOLVED_CLASS,
  NEWS_LABEL_UNRESOLVED_TEXT,
} from "../../../components/news/news_labels";

function formatPublishedAt(publishedAt: string): string {
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(publishedAt));
}

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ url: string }>;
}) {
  const { url } = await params;
  const articleUrl = decodeBase64Url(url);
  const article = await getNewsArticleById(articleUrl).catch(() => null);

  if (!article) {
    notFound();
  }

  const badgeClass = article.label
    ? NEWS_LABEL_CLASS[article.label]
    : NEWS_LABEL_UNRESOLVED_CLASS;
  const badgeText = article.label
    ? NEWS_LABEL_TEXT[article.label]
    : NEWS_LABEL_UNRESOLVED_TEXT;

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
        {article.source} · {NEWS_BRIEF_TYPE_LABEL[article.brief_type]} ·{" "}
        {formatPublishedAt(article.published_at)}
      </div>

      <div className="mb-3 text-sm font-medium leading-[1.75] text-ink-body">
        {article.summary ?? "아직 한 줄 요약이 준비되지 않았습니다."}
      </div>

      <div className="mb-4 flex items-center gap-2">
        <span
          className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${badgeClass}`}
        >
          {badgeText}
        </span>
        {article.evidence.length === 0 && (
          <span className="text-[12.5px] leading-[1.6] text-ink-sub">
            아직 판정 근거가 준비되지 않았습니다.
          </span>
        )}
      </div>

      {article.evidence.length > 0 && (
        <ul className="mb-4 flex flex-col gap-1.5 text-[12.5px] leading-[1.6] text-ink-sub">
          {article.evidence.map((evidence, index) => (
            <li key={index}>
              <b className="font-semibold text-ink">근거</b> — {evidence.sentence}
              {evidence.is_quote && (
                <span className="ml-1 text-[11px] text-ink-sub">(전문가 인용)</span>
              )}
            </li>
          ))}
        </ul>
      )}

      <div className="border-t border-line-soft pt-4 text-[13.5px] leading-[1.9] text-ink-body">
        {article.body}
      </div>
    </div>
  );
}
