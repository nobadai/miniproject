// 목적: 사기 화면 탐지 API 통신을 담당한다.
// 주요 역할: 업로드 이미지를 Backend `/fraud-analysis` Endpoint로 전달한다.

import type { ApiResponse } from "../types/api_response";
import type { FraudAnalysisResult } from "../types/fraud_analysis";
import { postFile } from "./api_client";

export function analyzeFraudImage(
  imageFile: File
): Promise<ApiResponse<FraudAnalysisResult>> {
  return postFile<FraudAnalysisResult>("/fraud-analysis", imageFile);
}
