// 목적: Backend 판정값을 화면 표시용 위험 단계로 변환한다.
// 주요 역할: 서로 다른 두 API의 판정 결과를 같은 신호등 단계와 안내 문구로 통일한다.
//
// 위험 여부 판단 자체는 Backend가 이미 끝낸 상태이며, 여기서는 그 결과를
// 어떤 색과 문구로 보여줄지만 결정한다.

import type { FraudVerdict } from "../types/fraud_analysis";
import type { RiskLevel } from "../types/risk_level";
import type { VoicePhishingPrediction } from "../types/voice_phishing";

const VOICE_PHISHING_RISK_LEVEL: Record<VoicePhishingPrediction, RiskLevel> = {
  suspicious: "danger",
  unknown: "caution",
  normal: "safe",
};

const FRAUD_RISK_LEVEL: Record<FraudVerdict, RiskLevel> = {
  사기의심: "danger",
  판단불가: "caution",
  정상: "safe",
};

// Backend가 코드값으로 내려주는 판정 근거를 중장년 사용자가 읽을 수 있는 문장으로 바꾼다.
const VOICE_PHISHING_REASON_TEXT: Record<string, string> = {
  strong_rule_and_sequence:
    "위험한 표현과 대화가 흘러간 순서가 모두 전형적인 보이스피싱과 같습니다.",
  model_high: "AI가 통화 내용을 보이스피싱으로 강하게 판단했습니다.",
  model_and_sequence:
    "AI 판단과 대화가 진행된 순서가 함께 위험 신호를 가리키고 있습니다.",
  all_signals_low: "위험한 표현도, 이상한 대화 흐름도 발견되지 않았습니다.",
  signals_conflict_or_uncertain:
    "위험 신호가 서로 엇갈려 확실하게 판단하기 어렵습니다.",
};

export function resolveVoicePhishingRiskLevel(
  prediction: VoicePhishingPrediction
): RiskLevel {
  return VOICE_PHISHING_RISK_LEVEL[prediction] ?? "caution";
}

export function resolveFraudRiskLevel(verdict: FraudVerdict): RiskLevel {
  return FRAUD_RISK_LEVEL[verdict] ?? "caution";
}

export function resolveVoicePhishingReasonText(decisionReason: string): string {
  return (
    VOICE_PHISHING_REASON_TEXT[decisionReason] ??
    "분석 결과를 참고해 신중하게 판단해 주세요."
  );
}
