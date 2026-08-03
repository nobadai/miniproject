// 목적: 보이스피싱 오디오 분석 API 통신을 담당한다.
// 주요 역할: 업로드 오디오를 Backend `/voice-phishing/analysis` Endpoint로 전달한다.

import type { ApiResponse } from "../types/api_response";
import type { VoicePhishingAnalysis } from "../types/voice_phishing";
import { postFile } from "./api_client";

export function analyzeVoicePhishingAudio(
  audioFile: File
): Promise<ApiResponse<VoicePhishingAnalysis>> {
  return postFile<VoicePhishingAnalysis>("/voice-phishing/analysis", audioFile);
}
