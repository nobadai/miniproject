// 목적: 로그인/마이페이지 화면에서 사용하는 사용자 프로필 타입을 정의한다.
// 주요 역할: Backend UserResponse(backend/app/schemas/user.py)의 실제 응답
//           구조를 그대로 미러링한다(2026-08-03 실제 코드 대조 완료).
//
// 주의: phone, joinedAt 필드는 실제 Backend UserResponse에 없어 제거했다.
// 가입일이 필요하면 created_at을 그대로 쓰거나 화면에서 보기 좋게 포맷한다.

export interface UserProfile {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
