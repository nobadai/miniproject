// 목적: 로그인/회원가입/로그아웃 API 통신 함수를 정의한다.
// 주요 역할: 이메일/비밀번호 기반 인증 요청을 Backend에 전달한다. 인증은 쿠키
//           기반(HttpOnly access_token)이며, 성공 시 Backend가 Set-Cookie로
//           세션을 발급하므로 credentials: "include"로 Browser가 쿠키를
//           저장·전송하게 한다. 로그인 성공 후 토큰/세션을 Frontend에 별도로
//           저장하는 코드는 두지 않는다.
//
// Endpoint는 backend/app/routers/auth.py 실제 코드로 확인했다(2026-08-03).
// POST /auth/signup → 201 + ApiResponse<UserResponse>
// POST /auth/login  → 200 + ApiResponse<UserResponse> (+ Set-Cookie: access_token)
// POST /auth/logout → 204 No Content (Body 없음, 쿠키 삭제)
// SignupRequest는 email/password/name만 받고 extra="forbid"라 phone 등 다른
// 필드를 보내면 422가 난다 — SignupPayload에 phone을 넣지 않는다.

import type { UserProfile } from "../types/user";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
}

export async function login(payload: LoginPayload): Promise<UserProfile> {
  const url = buildApiUrl("/auth/login");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<UserProfile>(response, "로그인에 실패했습니다.");
}

export async function signup(payload: SignupPayload): Promise<UserProfile> {
  const url = buildApiUrl("/auth/signup");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<UserProfile>(response, "회원가입에 실패했습니다.");
}

export async function logout(): Promise<void> {
  const url = buildApiUrl("/auth/logout");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  await unwrapApiResponse<void>(response, "로그아웃에 실패했습니다.");
}
