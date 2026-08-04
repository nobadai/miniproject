// 목적: 보이스피싱 판별 API 통신 함수를 정의한다.
// 주요 역할: 업로드된 통화 녹음 파일을 multipart/form-data로 Backend에 전달하고,
//           분석 결과를 VoicePhishingAnalysis로 반환한다.
//
// 주의: Backend 라우터가 실패 시에도 HTTP 상태 코드를 직접 바꿔서 응답할 수 있다
// (docs/frontend_api_integration.md 참고, HTTPException을 던지지 않는 방식). 이
// 함수는 HTTP 상태와 무관하게 응답 Body의 success 필드를 기준으로 성공/실패를
// 판단한다(unwrapApiResponse 공통 처리).

import type { VoicePhishingAnalysis } from "../types/voice_phishing";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

export async function analyzeVoicePhishing(
  file: File
): Promise<VoicePhishingAnalysis> {
  const formData = new FormData();
  formData.append("file", file);
  const url = buildApiUrl("/voice-phishing/analysis");

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

  return unwrapApiResponse<VoicePhishingAnalysis>(
    response,
    "보이스피싱 판별에 실패했습니다."
  );
}
