// 목적: Backend 공통 API 응답 계약(ApiResponse)의 Frontend 대응 타입을 정의한다.
// 주요 역할: Backend의 success/data/message 구조를 그대로 미러링해 API 연동 담당자가
//           재사용할 수 있게 한다. API JSON 필드는 snake_case 규칙을 유지한다.

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  message: string | null;
}
