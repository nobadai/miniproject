// 목적: 사용자가 보유한 투자 상품 현황을 요약해 보여준다.
// 주요 역할: 상품 이름, 구분, 수익률을 한 줄씩 정리해 표시한다.

import type { InvestmentHolding } from "../../types/news_article";
import { formatSignedPercent } from "../../utils/format";

interface HoldingSummaryProps {
  holdings: InvestmentHolding[];
}

export default function HoldingSummary({ holdings }: HoldingSummaryProps) {
  return (
    <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
      <h2 className="text-lg font-bold text-ink">내가 가입한 금융상품</h2>
      <ul className="mt-3 divide-y divide-line">
        {holdings.map((holding) => (
          <li
            key={holding.holding_id}
            className="flex items-center justify-between gap-3 py-3"
          >
            <div>
              <p className="text-base font-bold text-ink">{holding.name}</p>
              <p className="text-sm text-ink-soft">{holding.category}</p>
            </div>
            <p
              className={`text-lg font-bold ${
                holding.return_rate >= 0 ? "text-safe" : "text-danger"
              }`}
            >
              {formatSignedPercent(holding.return_rate)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
