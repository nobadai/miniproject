// 목적: 로그인/마이페이지 화면에서 사용하는 사용자 프로필 타입을 정의한다.
// 주요 역할: 아직 인증 기능이 없어 Frontend 전용 더미 데이터 구조로만 사용한다.
//
// 주의: 백엔드 인증 API가 아직 확정되지 않은 상태라, 이 파일의 필드명은
// 전부 Frontend에서 추정으로 붙인 이름이다(UserProfile/LoginPayload/SignupPayload 포함).
// 실제 백엔드 스키마가 나오면 필드명·타입이 다를 수 있으니, API 연동 담당자는
// 이 타입을 그대로 신뢰하지 말고 백엔드 스펙과 다시 대조해야 한다.

export interface UserProfile {
  name: string;
  email: string;
  phone: string;
  joinedAt: string;
}
