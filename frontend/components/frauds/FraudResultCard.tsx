// 목적: 사기화면 판별 결과 카드를 표시한다.
// 주요 역할: services/fraud_analysis.ts가 반환한 FraudAnalysisResult를 받아 화면에 렌더링한다.
//           결과 데이터는 상위 컴포넌트가 props로 전달하며, 이 컴포넌트는 하드코딩된 값을 갖지 않는다.

import type { FraudAnalysisResult, FraudVerdict } from "../../types/fraud_analysis";

const VERDICT_LABEL: Record<FraudVerdict, string> = {
  정상: "정상",
  사기의심: "사기 의심",
  판단불가: "판단 불가",
};

const VERDICT_BADGE: Record<FraudVerdict, { label: string; className: string }> = {
  정상: { label: "정상 화면", className: "bg-safe-bg text-safe" },
  사기의심: { label: "사기 의심 화면", className: "bg-alert-bg text-alert" },
  판단불가: { label: "판단 불가 화면", className: "bg-line-soft text-ink-sub" },
};

const VERDICT_PILL_ACTIVE_CLASS: Record<FraudVerdict, string> = {
  정상: "border border-safe-border bg-safe-bg text-safe",
  사기의심: "border border-alert-border bg-alert-bg text-alert",
  판단불가: "bg-navy text-white",
};

export default function FraudResultCard({ result }: { result: FraudAnalysisResult }) {
  const confidencePercent = Math.round(result.confidence * 100);
  const badge = VERDICT_BADGE[result.verdict];

  return (
    <div className="rounded-md border border-line p-[22px_24px]">
      <div className="mb-4 flex items-center justify-between border-b border-line-soft pb-[14px]">
        <span className="text-[12.5px] font-semibold text-ink-sub">판별 결과</span>
        <div className="flex gap-1.5">
          {(Object.keys(VERDICT_LABEL) as FraudVerdict[]).map((verdict) => (
            <span
              key={verdict}
              className={`rounded px-3 py-[5px] text-xs font-semibold ${
                result.verdict === verdict
                  ? VERDICT_PILL_ACTIVE_CLASS[verdict]
                  : "bg-[#f1f2f4] text-ink-sub"
              }`}
            >
              {VERDICT_LABEL[verdict]}
            </span>
          ))}
        </div>
      </div>

      <div className="mb-2 flex items-center gap-3">
        <span className={`rounded px-2.5 py-[5px] text-xs font-semibold ${badge.className}`}>
          {badge.label}
        </span>
        <span className="text-[12.5px] text-ink-sub">
          판단 확신도 {confidencePercent}%
          <span className="text-[#9aa1ab]"> · AI가 스스로 매긴 확신 정도예요</span>
        </span>
      </div>

      {result.tamper_types.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {result.tamper_types.map((type) => (
            <span
              key={type}
              className="rounded border border-alert-border bg-alert-bg px-2.5 py-1 text-xs font-semibold text-alert"
            >
              {type}
            </span>
          ))}
        </div>
      )}

      <div className="mb-4 text-[13.5px] leading-[1.7] text-ink-body">{result.reasoning}</div>

      {result.undetermined_reason && (
        <div className="mb-4 text-[13px] text-ink-sub">
          판단 불가 이유 — {result.undetermined_reason}
        </div>
      )}

      <div className="rounded-[3px] border border-line border-l-[3px] border-l-navy bg-[#fbfbfc] p-[13px_15px] text-[13px] text-ink-body">
        <b className="font-bold text-navy">이렇게 확인하세요</b> — 결과가 의심되면 즉시 이체를
        중단하고, 은행 공식 앱이나 대표번호로 직접 확인하세요.
      </div>
    </div>
  );
}
