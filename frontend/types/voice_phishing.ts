// 목적: 보이스피싱 판별(voice-phishing) API 응답 타입을 정의한다.
// 주요 역할: Backend Pydantic Schema(VoicePhishingAnalysis)와 동일한 필드명·의미를 유지한다.
//           API JSON 필드는 snake_case 규칙을 유지한다.

export interface VoicePhishingTurn {
  idx: number;
  speaker: string;
  text: string;
}

export interface VoicePhishingAnalysis {
  audio_filename: string;
  transcript_id: string;
  prediction: string;
  fusion_raw_score: number;
  fusion_score: number;
  rule_score: number;
  rule_categories: string[];
  sequence_score: number;
  transitions: string[];
  koelectra_score: number;
  decision_reason: string;
  turns: VoicePhishingTurn[];
}
