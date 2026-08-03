// 목적: 검사 결과의 위험 단계를 신호등 형태로 크게 표시한다.
// 주요 역할: 위험 단계별 색, 아이콘, 문구와 점수 막대를 한 화면에 묶어 보여준다.

import type { RiskLevel } from "../../types/risk_level";
import { formatPercent } from "../../utils/format";

interface RiskBadgeProps {
  level: RiskLevel;
  headline: string;
  description: string;
  scoreLabel?: string;
  scoreRatio?: number;
}

// 색만으로 구분하면 색약 사용자가 알아보기 어려워 아이콘과 문구를 함께 사용한다.
const RISK_STYLE: Record<
  RiskLevel,
  { icon: string; boxClassName: string; barClassName: string }
> = {
  safe: {
    icon: "🟢",
    boxClassName: "border-safe bg-safe-soft text-safe",
    barClassName: "bg-safe",
  },
  caution: {
    icon: "🟡",
    boxClassName: "border-caution bg-caution-soft text-caution",
    barClassName: "bg-caution",
  },
  danger: {
    icon: "🔴",
    boxClassName: "border-danger bg-danger-soft text-danger",
    barClassName: "bg-danger",
  },
};

export default function RiskBadge({
  level,
  headline,
  description,
  scoreLabel,
  scoreRatio,
}: RiskBadgeProps) {
  const riskStyle = RISK_STYLE[level];
  const hasScore = typeof scoreRatio === "number";

  return (
    <section
      className={`rounded-2xl border-4 px-5 py-6 ${riskStyle.boxClassName}`}
    >
      <p className="flex items-center gap-3 text-2xl font-bold">
        <span aria-hidden="true" className="text-3xl">
          {riskStyle.icon}
        </span>
        {headline}
      </p>

      <p className="mt-3 text-base font-medium text-ink">{description}</p>

      {hasScore && (
        <div className="mt-5">
          <p className="flex items-baseline justify-between text-base font-bold text-ink">
            <span>{scoreLabel}</span>
            <span className="text-2xl">{formatPercent(scoreRatio)}</span>
          </p>
          <div
            role="img"
            aria-label={`${scoreLabel} ${formatPercent(scoreRatio)}`}
            className="mt-2 h-5 w-full overflow-hidden rounded-full border-2 border-white bg-white"
          >
            <div
              className={`h-full rounded-full ${riskStyle.barClassName}`}
              style={{ width: `${Math.round(scoreRatio * 100)}%` }}
            />
          </div>
        </div>
      )}
    </section>
  );
}
