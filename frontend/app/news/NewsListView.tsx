// 목적: 금융 뉴스 목록의 필터 UI를 정의한다.
// 주요 역할: 상위 page.tsx가 services/news.ts로 가져온 목록을 props로 받아
//           오전시황/마감시황 Chip 필터 상태(Client 상태)만 관리한다.

"use client";

import { useState } from "react";
import NewsCard from "../../components/news/NewsCard";
import type { NewsArticle, NewsSession } from "../../types/news";

type SessionFilter = "all" | NewsSession;

const CHIPS: { value: SessionFilter; label: string }[] = [
  { value: "all", label: "전체" },
  { value: "morning", label: "오전시황" },
  { value: "close", label: "마감시황" },
];

export default function NewsListView({ articles }: { articles: NewsArticle[] }) {
  const [session, setSession] = useState<SessionFilter>("all");

  const filteredArticles = articles.filter(
    (article) => session === "all" || article.session === session
  );

  return (
    <div className="border border-line bg-white p-8">
      <div className="mb-6 flex flex-wrap items-center gap-2">
        {CHIPS.map((chip) => (
          <button
            key={chip.value}
            type="button"
            onClick={() => setSession(chip.value)}
            className={`rounded-md border px-3.5 py-[7px] text-[12.5px] font-medium ${
              session === chip.value
                ? "border-navy bg-navy text-white"
                : "border-line bg-white text-ink-sub"
            }`}
          >
            {chip.label}
          </button>
        ))}
        <input
          type="text"
          placeholder="종목·키워드 검색"
          className="ml-auto w-[220px] rounded-md border border-[#c9ced6] px-3.5 py-2 text-[13px]"
        />
      </div>

      <div className="flex flex-col">
        {filteredArticles.map((article) => (
          <NewsCard key={article.id} article={article} />
        ))}
      </div>

      <div className="mt-5 border-t border-line-soft pt-4 text-xs leading-[1.6] text-ink-sub">
        미국 증시 개장·마감 시점 기준으로 수집·분석된 뉴스가 순차 반영됩니다. 감성
        분류(긍정/부정/중립)는 뉴스 본문 기반 자동 분석 결과이며, 투자 판단의 참고
        자료로만 활용하시기 바랍니다.
      </div>
    </div>
  );
}
