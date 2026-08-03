// 목적: 사기 화면 탐지 결과를 화면에 표시한다.
// 주요 역할: 판정 결과와 변조 의심 유형, 분석 근거를 정리해 보여준다.

import type { FraudAnalysisResult } from "../../types/fraud_analysis";
import type { RiskLevel } from "../../types/risk_level";
import { formatPercent } from "../../utils/format";
import { resolveFraudRiskLevel } from "../../utils/risk_level";
import EmergencyAction from "../commons/emergency_action";
import RiskBadge from "../commons/risk_badge";

interface FraudResultProps {
  result: FraudAnalysisResult;
}

const RISK_HEADLINE: Record<RiskLevel, string> = {
  danger: "사기가 의심됩니다",
  caution: "판단하기 어렵습니다",
  safe: "이상한 점이 없습니다",
};

const RISK_DESCRIPTION: Record<RiskLevel, string> = {
  danger:
    "화면이 꾸며졌거나 조작된 흔적이 보입니다. 이 화면을 근거로 돈을 보내지 마세요.",
  caution:
    "화면만으로는 확인이 어렵습니다. 은행 앱을 직접 열어 실제 내역을 확인해 주세요.",
  safe: "조작된 흔적이 발견되지 않았습니다. 다만 안심하지 말고 실제 내역도 확인해 주세요.",
};

export default function FraudResult({ result }: FraudResultProps) {
  const riskLevel = resolveFraudRiskLevel(result.verdict);

  return (
    <div className="flex flex-col gap-5">
      <RiskBadge
        level={riskLevel}
        headline={RISK_HEADLINE[riskLevel]}
        description={RISK_DESCRIPTION[riskLevel]}
        scoreLabel="분석 확신 정도"
        scoreRatio={result.confidence}
      />

      <section className="rounded-2xl border-2 border-line bg-surface px-5 py-5">
        <h3 className="text-lg font-bold text-ink">이렇게 판단했습니다</h3>
        <p className="mt-2 text-base text-ink-soft">{result.reasoning}</p>

        {result.tamper_types.length > 0 && (
          <div className="mt-5">
            <p className="text-base font-bold text-ink">의심되는 조작 유형</p>
            <ul className="mt-2 flex flex-col gap-2">
              {result.tamper_types.map((tamperType) => (
                <li
                  key={tamperType}
                  className="rounded-xl bg-danger-soft px-4 py-3 text-base font-bold text-danger"
                >
                  {tamperType}
                </li>
              ))}
            </ul>
          </div>
        )}

        {result.undetermined_reason && (
          <div className="mt-5 rounded-xl bg-caution-soft px-4 py-3">
            <p className="text-base font-bold text-caution">판단이 어려운 이유</p>
            <p className="mt-1 text-sm text-ink">{result.undetermined_reason}</p>
          </div>
        )}
      </section>

      {riskLevel !== "safe" && (
        <EmergencyAction
          shareMessage={`안심지킴이 검사 결과, 받은 화면 캡처에서 사기 의심 정황이 발견되었습니다. (확신 정도 ${formatPercent(
            result.confidence
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
