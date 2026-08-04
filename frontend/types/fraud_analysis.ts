// 목적: 사기화면 판별(fraud-analysis) API 응답 타입을 정의한다.
// 주요 역할: Backend Pydantic Schema(FraudAnalysisResult)와 동일한 필드명·의미를 유지한다.
//           API JSON 필드는 snake_case 규칙을 유지한다.

export type FraudVerdict = "정상" | "사기의심" | "판단불가";

export interface FraudAnalysisResult {
  verdict: FraudVerdict;
  tamper_types: string[];
  reasoning: string;
  confidence: number;
  undetermined_reason: string | null;
}
