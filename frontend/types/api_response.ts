// 목적: Backend 공통 응답 구조를 Frontend Type으로 정의한다.
// 주요 역할: 모든 API 호출이 동일한 성공 여부/데이터/메시지 형태를 공유하도록 한다.

export interface ApiResponse<TData> {
  success: boolean;
  data?: TData | null;
  message?: string | null;
}
