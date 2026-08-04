// 목적: 홈 화면의 금융 뉴스 배너를 정의한다.
// 주요 역할: services/news.ts에서 뉴스 목록을 가져와 최신 2건만 고정으로 보여준다
//           (자동 넘김 없음). Client Component라 데이터를 useEffect에서 비동기로 가져온다.

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getNewsArticles } from "../../services/news";
import { encodeBase64Url } from "../../utils/base64_url";
import {
  NEWS_LABEL_CLASS,
  NEWS_LABEL_TEXT,
  NEWS_LABEL_UNRESOLVED_CLASS,
  NEWS_LABEL_UNRESOLVED_TEXT,
  formatNewsListDate,
} from "./news_labels";
import type { NewsArticle } from "../../types/news";

const LATEST_COUNT = 2;

export default function NewsBanner() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);

  useEffect(() => {
    let isMounted = true;
    getNewsArticles()
      .then((data) => {
        if (isMounted) setArticles(data);
      })
      .catch(() => {
        // 뉴스 배너는 별도 에러 UI가 없어 실패 시 빈 배열로 두면 배너가 자동으로 숨겨진다.
        if (isMounted) setArticles([]);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const latestArticles = articles.slice(0, LATEST_COUNT);

  if (latestArticles.length === 0) {
    return null;
  }

  return (
    <div className="mb-5 overflow-hidden border border-line bg-white">
      <div className="flex items-center justify-between border-b border-line-soft px-[18px] py-3">
        <span className="text-[12.5px] font-bold tracking-[0.3px] text-ink-sub">
          금융 뉴스 감성 분석
        </span>
        <Link href="/news" className="text-xs text-ink-sub">
          더보기 &rsaquo;
        </Link>
      </div>

      <div className="py-1">
        {latestArticles.map((article) => (
          <Link
            key={article.url}
            href={`/news/${encodeBase64Url(article.url)}`}
            className="flex items-center gap-2.5 px-[18px] py-3"
          >
            <span
              className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${
                article.label ? NEWS_LABEL_CLASS[article.label] : NEWS_LABEL_UNRESOLVED_CLASS
              }`}
            >
              {article.label ? NEWS_LABEL_TEXT[article.label] : NEWS_LABEL_UNRESOLVED_TEXT}
            </span>
            <span className="flex-1 text-[13.5px] font-medium text-ink">
              {article.title}
            </span>
            <span className="shrink-0 text-[11px] text-ink-sub">
              {formatNewsListDate(article.published_at)}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
