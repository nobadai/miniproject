// 목적: 보이스피싱 판별 API 통신 함수의 껍데기를 정의한다.
// 주요 역할: 실제 구현은 API 연동 담당자가 붙일 예정이며, 지금은 시그니처만 제공한다.

import type { VoicePhishingAnalysis } from "../types/voice_phishing";

// TODO: NEXT_PUBLIC_API_BASE_URL 기준 POST /voice-phishing/analysis(multipart/form-data)로 교체한다.
export async function analyzeVoicePhishing(
  file: File
): Promise<VoicePhishingAnalysis> {
  void file;
  throw new Error("not implemented");
}
