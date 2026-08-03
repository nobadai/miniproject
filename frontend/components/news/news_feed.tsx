// 목적: 보유 상품 기준으로 맞춤 뉴스를 골라 보여준다.
// 주요 역할: 상품 선택 버튼 상태를 관리하고 해당 상품의 기사 목록을 표시한다.

"use client";

import { useState } from "react";
import type { InvestmentHolding, NewsArticle } from "../../types/news_article";
import NewsArticleCard from "./news_article_card";

interface NewsFeedProps {
  holdings: InvestmentHolding[];
  articles: NewsArticle[];
}

const ALL_HOLDINGS = "all";

export default function NewsFeed({ holdings, articles }: NewsFeedProps) {
  const [selectedHoldingId, setSelectedHoldingId] = useState(ALL_HOLDINGS);

  const holdingNameById = new Map(
    holdings.map((holding) => [holding.holding_id, holding.name])
  );
  const visibleArticles =
    selectedHoldingId === ALL_HOLDINGS
      ? articles
      : articles.filter((article) => article.holding_id === selectedHoldingId);

  const filterItems = [
    { id: ALL_HOLDINGS, label: "전체" },
    ...holdings.map((holding) => ({
      id: holding.holding_id,
      label: holding.name,
    })),
  ];

  return (
    <div className="flex flex-col gap-5">
      {/* 상품 수가 늘어나도 버튼 크기를 줄이지 않도록 가로 스크롤로 처리한다. */}
      <div className="-mx-5 overflow-x-auto px-5">
        <div className="flex w-max gap-2">
          {filterItems.map((filterItem) => {
            const isSelected = filterItem.id === selectedHoldingId;

            return (
              <button
                key={filterItem.id}
                type="button"
                onClick={() => setSelectedHoldingId(filterItem.id)}
                aria-pressed={isSelected}
                className={`min-h-[56px] whitespace-nowrap rounded-full border-2 px-5 text-base font-bold ${
                  isSelected
                    ? "border-brand bg-brand text-white"
                    : "border-line bg-surface text-ink-soft"
                }`}
              >
                {filterItem.label}
              </button>
            );
          })}
        </div>
      </div>

      {visibleArticles.length === 0 ? (
        <p className="rounded-2xl border-2 border-line bg-surface px-5 py-8 text-center text-base text-ink-soft">
          아직 관련된 새 소식이 없습니다.
        </p>
      ) : (
        visibleArticles.map((article) => (
          <NewsArticleCard
            key={article.article_id}
            article={article}
            holdingName={holdingNameById.get(article.holding_id) ?? "관련 상품"}
          />
        ))
      )}
    </div>
  );
}
