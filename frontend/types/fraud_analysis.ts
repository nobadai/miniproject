// 목적: 사기 화면 탐지 API의 Response Type을 정의한다.
// 주요 역할: Backend FraudAnalysisResult Schema와 동일한 Field 계약을 유지한다.

export type FraudVerdict = "정상" | "사기의심" | "판단불가";

export interface FraudAnalysisResult {
  verdict: FraudVerdict;
  tamper_types: string[];
  reasoning: string;
  confidence: number;
  undetermined_reason?: string | null;
}
