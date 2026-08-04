// 목적: 사기화면 판별 API 통신 함수를 정의한다.
// 주요 역할: 업로드된 이미지 파일을 multipart/form-data로 Backend에 전달하고,
//           분석 결과를 FraudAnalysisResult로 반환한다.

import type { FraudAnalysisResult } from "../types/fraud_analysis";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

export async function analyzeFraudScreen(
  file: File
): Promise<FraudAnalysisResult> {
  const formData = new FormData();
  formData.append("file", file);
  const url = buildApiUrl("/fraud-analysis");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      credentials: "include",
      body: formData,
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<FraudAnalysisResult>(
    response,
    "사기화면 판별에 실패했습니다."
  );
}
