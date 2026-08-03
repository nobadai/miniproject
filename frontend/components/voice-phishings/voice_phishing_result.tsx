// 목적: 보이스피싱 오디오 분석 결과를 화면에 표시한다.
// 주요 역할: 위험 단계, 판단 근거, 통화 내용을 중장년 사용자가 이해할 수 있게 정리한다.

"use client";

import { useState } from "react";
import type { RiskLevel } from "../../types/risk_level";
import type { VoicePhishingAnalysis } from "../../types/voice_phishing";
import { formatPercent } from "../../utils/format";
import {
  resolveVoicePhishingReasonText,
  resolveVoicePhishingRiskLevel,
} from "../../utils/risk_level";
import EmergencyAction from "../commons/emergency_action";
import RiskBadge from "../commons/risk_badge";

interface VoicePhishingResultProps {
  analysis: VoicePhishingAnalysis;
}

const RISK_HEADLINE: Record<RiskLevel, string> = {
  danger: "위험합니다",
  caution: "조심하세요",
  safe: "특이한 점이 없습니다",
};

const RISK_DESCRIPTION: Record<RiskLevel, string> = {
  danger: "보이스피싱으로 의심되는 통화입니다. 절대 송금하지 마세요.",
  caution:
    "위험하다고 단정하기는 어렵지만, 돈이나 개인정보를 요구했다면 응하지 마세요.",
  safe: "보이스피싱에서 자주 쓰이는 표현이 발견되지 않았습니다.",
};

export default function VoicePhishingResult({
  analysis,
}: VoicePhishingResultProps) {
  const [isTranscriptOpen, setIsTranscriptOpen] = useState(false);
  const riskLevel = resolveVoicePhishingRiskLevel(analysis.prediction);

  return (
    <div className="flex flex-col gap-5">
      <RiskBadge
        level={riskLevel}
        headline={RISK_HEADLINE[riskLevel]}
        description={RISK_DESCRIPTION[riskLevel]}
        scoreLabel="보이스피싱 의심 정도"
        scoreRatio={analysis.fusion_score}
      />

      <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
        <h3 className="text-lg font-bold text-ink">이렇게 판단했습니다</h3>
        <p className="mt-2 text-base text-ink-soft">
          {resolveVoicePhishingReasonText(analysis.decision_reason)}
        </p>

        {analysis.rule_categories.length > 0 && (
          <div className="mt-5">
            <p className="text-base font-bold text-ink">발견된 위험 표현</p>
            <ul className="mt-2 flex flex-wrap gap-2">
              {analysis.rule_categories.map((ruleCategory) => (
                <li
                  key={ruleCategory}
                  className="rounded-full bg-danger-soft px-4 py-2 text-sm font-bold text-danger"
                >
                  {ruleCategory}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.transitions.length > 0 && (
          <div className="mt-5">
            <p className="text-base font-bold text-ink">대화가 흘러간 순서</p>
            <p className="mt-2 text-sm text-ink-soft">
              {analysis.transitions.join(" → ")}
            </p>
          </div>
        )}

        <dl className="mt-5 divide-y divide-line border-t-2 border-line text-sm">
          <div className="flex justify-between py-3">
            <dt className="text-ink-soft">위험 표현 점수</dt>
            <dd className="font-bold text-ink">
              {formatPercent(analysis.rule_score)}
            </dd>
          </div>
          <div className="flex justify-between py-3">
            <dt className="text-ink-soft">대화 흐름 점수</dt>
            <dd className="font-bold text-ink">
              {formatPercent(analysis.sequence_score)}
            </dd>
          </div>
          <div className="flex justify-between py-3">
            <dt className="text-ink-soft">AI 판단 점수</dt>
            <dd className="font-bold text-ink">
              {formatPercent(analysis.koelectra_score)}
            </dd>
          </div>
        </dl>
      </section>

      <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
        <button
          type="button"
          onClick={() => setIsTranscriptOpen(!isTranscriptOpen)}
          aria-expanded={isTranscriptOpen}
          className="flex min-h-[56px] w-full items-center justify-between text-left text-lg font-bold text-ink"
        >
          통화 내용 보기 ({analysis.turns.length}줄)
          <span aria-hidden="true" className="text-brand">
            {isTranscriptOpen ? "▲" : "▼"}
          </span>
        </button>

        {isTranscriptOpen && (
          <ol className="mt-4 flex flex-col gap-4">
            {analysis.turns.map((turn) => (
              <li key={turn.idx}>
                <p className="text-sm font-bold text-brand">{turn.speaker}</p>
                <p className="mt-1 rounded-xl bg-canvas px-4 py-3 text-base text-ink">
                  {turn.text}
                </p>
              </li>
            ))}
          </ol>
        )}
      </section>

      {riskLevel !== "safe" && (
        <EmergencyAction
          shareMessage={`안심지킴이 검사 결과, 방금 받은 통화가 보이스피싱으로 의심됩니다. (의심 정도 ${formatPercent(
            analysis.fusion_score
          )})`}
        />
      )}

      <p className="text-sm text-ink-soft">
        이 결과는 AI 분석 참고 자료입니다. 최종 판단은 반드시 금융기관이나
        경찰에 직접 확인해 주세요.
      </p>
    </div>
  );
}
