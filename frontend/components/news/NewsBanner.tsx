// 목적: 홈 화면의 금융 뉴스 배너를 정의한다.
// 주요 역할: services/news.ts에서 뉴스 목록을 가져와 2건씩 묶어 5초마다 자동으로 넘긴다.
//           Client Component라 데이터를 useEffect에서 비동기로 가져온다.

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getNewsArticles } from "../../services/news";
import { SENTIMENT_LABEL } from "./news_data";
import type { NewsArticle } from "../../types/news";

const GROUP_SIZE = 2;
const ROTATE_INTERVAL_MS = 5000;

const SENTIMENT_CLASS: Record<NewsArticle["sentiment"], string> = {
  pos: "bg-safe-bg text-safe",
  neg: "bg-alert-bg text-alert",
  neu: "bg-line-soft text-ink-sub",
};

function chunk(articles: NewsArticle[], size: number): NewsArticle[][] {
  const groups: NewsArticle[][] = [];
  for (let i = 0; i < articles.length; i += size) {
    groups.push(articles.slice(i, i + size));
  }
  return groups;
}

export default function NewsBanner() {
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [groupIndex, setGroupIndex] = useState(0);

  useEffect(() => {
    let isMounted = true;
    getNewsArticles().then((data) => {
      if (isMounted) setArticles(data);
    });
    return () => {
      isMounted = false;
    };
  }, []);

  const groups = chunk(articles, GROUP_SIZE);

  useEffect(() => {
    if (groups.length === 0) return;
    const timer = setInterval(() => {
      setGroupIndex((current) => (current + 1) % groups.length);
    }, ROTATE_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [groups.length]);

  if (groups.length === 0) {
    return null;
  }

  const activeGroup = groups[groupIndex] ?? groups[0];

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
        {activeGroup.map((article) => (
          <Link
            key={article.id}
            href={`/news/${article.id}`}
            className="flex items-center gap-2.5 px-[18px] py-3"
          >
            <span
              className={`shrink-0 rounded-[3px] px-2.5 py-1 text-[11.5px] font-bold ${SENTIMENT_CLASS[article.sentiment]}`}
            >
              {SENTIMENT_LABEL[article.sentiment]}
            </span>
            <span className="flex-1 text-[13.5px] font-medium text-ink">
              {article.title}
            </span>
          </Link>
        ))}
      </div>

      <div className="flex justify-center gap-[5px] pb-3 pt-2.5">
        {groups.map((_, index) => (
          <span
            key={index}
            className={`h-[5px] w-[5px] rounded-full ${
              index === groupIndex ? "bg-navy" : "bg-[#d3d8e0]"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
