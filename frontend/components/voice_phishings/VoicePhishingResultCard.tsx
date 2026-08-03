// 목적: 보이스피싱 판별 결과 카드를 표시한다.
// 주요 역할: services/voice_phishing.ts가 반환한 VoicePhishingAnalysis를 받아 화면에 렌더링한다.
//           결과 데이터는 상위 컴포넌트가 props로 전달하며, 이 컴포넌트는 하드코딩된 값을 갖지 않는다.

import type { VoicePhishingAnalysis } from "../../types/voice_phishing";

export default function VoicePhishingResultCard({
  result,
}: {
  result: VoicePhishingAnalysis;
}) {
  const riskPercent = Math.round(result.fusion_score * 100);
  const tags = [...result.rule_categories, ...result.transitions];

  return (
    <div className="rounded-md border border-line p-[22px_24px]">
      <div className="mb-4 flex items-center justify-between border-b border-line-soft pb-[14px]">
        <span className="text-[12.5px] font-semibold text-ink-sub">판별 결과</span>
        <span className="rounded border border-alert-border bg-alert-bg px-3 py-[5px] text-xs font-semibold text-alert">
          {result.prediction}
        </span>
      </div>

      <div className="mb-2 flex items-center gap-3">
        <span className="rounded bg-alert-bg px-2.5 py-[5px] text-xs font-semibold text-alert">
          보이스피싱 위험도
        </span>
        <span className="text-[12.5px] text-ink-sub">
          의심도 {riskPercent}%
          <span className="text-[#9aa1ab]"> · fusion_score × 100</span>
        </span>
      </div>

      <div className="mb-1 mt-3 h-1.5 overflow-hidden rounded-full bg-line-soft">
        <div
          className="h-full rounded-full bg-alert"
          style={{ width: `${riskPercent}%` }}
        />
      </div>

      {tags.length > 0 && (
        <div className="mb-3 mt-3 flex flex-wrap gap-1.5">
          {tags.map((tag, index) => (
            <span
              key={`${tag}-${index}`}
              className="rounded border border-alert-border bg-alert-bg px-2.5 py-1 text-xs font-semibold text-alert"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="mb-4 mt-3 text-[13.5px] leading-[1.7] text-ink-body">
        {result.decision_reason}
      </div>

      <div className="rounded-[3px] border border-line border-l-[3px] border-l-navy bg-[#fbfbfc] p-[13px_15px] text-[13px] text-ink-body">
        <b className="font-bold text-navy">이렇게 확인하세요</b> — 바로 전화를 끊고, 해당 기관
        공식 대표번호로 직접 확인하세요.
      </div>
    </div>
  );
}
