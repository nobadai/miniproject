// 목적: 검사 결과의 위험 단계를 화면 전체가 공유하는 Type으로 정의한다.
// 주요 역할: 보이스피싱과 사기 화면 검사가 같은 신호등 표현을 쓰도록 단계를 통일한다.

export type RiskLevel = "safe" | "caution" | "danger";
