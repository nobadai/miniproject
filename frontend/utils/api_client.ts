// 목적: Backend API 통신에서 여러 services/ 파일이 공통으로 쓰는 값 변환 유틸리티를 제공한다.
// 주요 역할: 요청 URL 생성과, 공통 응답 포맷 ApiResponse({success, data, message})를
//           파싱해 실패 시 Error로 변환하는 로직을 한 곳에 모아 services/ 파일마다
//           중복 작성하지 않게 한다. 로그아웃/회원탈퇴처럼 204 No Content(Body 없음)를
//           반환하는 Endpoint도 함께 처리한다(backend/app/routers/auth.py, users.py
//           실제 코드 확인).
//
// 주의(Docker 실기동 검증 중 발견): Server Component(app/news/page.tsx,
// app/mypage/page.tsx 등)의 fetch는 Browser가 아니라 frontend Container 안
// (Node.js)에서 실행된다. NEXT_PUBLIC_API_BASE_URL(예: http://localhost:8000)은
// Browser 기준 주소라 Container 안에서 그대로 쓰면 backend Container가 아니라
// frontend Container 자기 자신을 가리켜 연결이 실패한다(project_setup.md §10.1의
// "Server-only Environment Variables" 예시와 동일한 문제). 그래서 Server(Node.js)
// 쪽에서는 Container 간 통신 주소인 BACKEND_INTERNAL_URL(compose.yml에서 주입,
// 예: http://backend:8000)을 우선 사용한다. 이 값이 없으면(Docker 없이 로컬
// npm run dev로 실행하는 경우 등) NEXT_PUBLIC_API_BASE_URL로 자연스럽게 대체된다.

import type { ApiResponse } from "../types/api_response";

export function buildApiUrl(path: string): string {
  const baseUrl =
    (typeof window === "undefined" ? process.env.BACKEND_INTERNAL_URL : undefined) ??
    process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!baseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL 환경변수가 설정되지 않았습니다.");
  }
  return `${baseUrl}${path}`;
}

// FastAPI가 HTTPException으로 던지는 기본 오류 응답은 공통 ApiResponse 포맷이 아니라
// {"detail": "..."} 형태다. 그런 응답도 최대한 의미 있는 메시지를 보여주기 위해
// detail 필드를 보조 Fallback으로 함께 확인한다.
type BackendResponseBody<T> = Partial<ApiResponse<T>> & { detail?: string };

export async function unwrapApiResponse<T>(
  response: Response,
  fallbackErrorMessage: string
): Promise<T> {
  // 204는 정의상 Body가 없다. response.json()을 호출하면 파싱 에러가 나므로
  // 먼저 성공으로 처리한다(logout, 회원탈퇴 등 void 응답 Endpoint).
  if (response.status === 204) {
    return undefined as T;
  }

  let body: BackendResponseBody<T> | null = null;
  try {
    body = (await response.json()) as BackendResponseBody<T>;
  } catch {
    throw new Error(fallbackErrorMessage);
  }

  if (!body || !body.success) {
    throw new Error(body?.message ?? body?.detail ?? fallbackErrorMessage);
  }

  return body.data as T;
}
