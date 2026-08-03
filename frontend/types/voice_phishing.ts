// 목적: 보이스피싱 오디오 분석 API의 Request/Response Type을 정의한다.
// 주요 역할: Backend VoicePhishingAnalysis Schema와 동일한 Field 계약을 유지한다.

export type VoicePhishingPrediction = "suspicious" | "normal" | "unknown";

export interface VoicePhishingTurn {
  idx: number;
  speaker: string;
  text: string;
}

export interface VoicePhishingAnalysis {
  audio_filename: string;
  transcript_id: string;
  prediction: VoicePhishingPrediction;
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
