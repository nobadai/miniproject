// 목적: 마이페이지(프로필 조회/수정/탈퇴) API 통신 함수를 정의한다.
// 주요 역할: 쿠키 기반 인증 세션으로 내 프로필을 조회/수정/탈퇴 요청한다.
//           이 파일의 getMyProfile은 Browser fetch(credentials: "include") 전용이며
//           Client Component(components/commons/Header.tsx)에서만 사용한다.
//           Server Component(app/mypage/page.tsx, app/mypage/edit/page.tsx)에서는
//           방문자의 로그인 쿠키를 자동으로 실어주지 못하므로, 대신
//           services/user_server.ts의 getMyProfileForServerComponent를 사용해야 한다.
//
// Endpoint는 backend/app/routers/users.py 실제 코드로 확인했다(2026-08-03).
// GET /users/me    → 200 + ApiResponse<UserResponse>
// PATCH /users/me  → 200 + ApiResponse<UserResponse>
// DELETE /users/me → 204 No Content (Body 없음)
// UserUpdateRequest는 extra="forbid"라 name/current_password/new_password 외
// 필드(phone 등)를 보내면 422가 난다.

import type { UserProfile } from "../types/user";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

// backend/app/schemas/user.py의 UserUpdateRequest.validate_update_fields 검증 규칙:
// - name과 new_password가 둘 다 없으면 실패("이름 또는 새 비밀번호 중 하나 이상이 필요합니다.")
// - new_password를 보내려면 current_password도 함께 보내야 하고, 그 반대도 마찬가지
// - new_password는 current_password와 달라야 한다
export interface UpdateProfilePayload {
  name?: string;
  current_password?: string;
  new_password?: string;
}

export async function getMyProfile(): Promise<UserProfile> {
  const url = buildApiUrl("/users/me");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      credentials: "include",
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<UserProfile>(response, "프로필 조회에 실패했습니다.");
}

export async function updateMyProfile(
  payload: UpdateProfilePayload
): Promise<UserProfile> {
  const url = buildApiUrl("/users/me");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<UserProfile>(response, "프로필 수정에 실패했습니다.");
}

export async function withdrawMyAccount(password: string): Promise<void> {
  const url = buildApiUrl("/users/me");

  let response: Response;
  try {
    response = await fetch(url, {
      method: "DELETE",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  await unwrapApiResponse<void>(response, "회원 탈퇴에 실패했습니다.");
}
