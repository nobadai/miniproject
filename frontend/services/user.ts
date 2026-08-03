// 목적: 마이페이지(프로필 조회/수정/탈퇴) API 통신 함수의 껍데기를 정의한다.
// 주요 역할: 실제 구현은 API 연동 담당자가 붙일 예정이며, 지금은 시그니처만 제공한다.

import type { UserProfile } from "../types/user";

export interface UpdateProfilePayload {
  name: string;
  phone: string;
  currentPassword?: string;
  newPassword?: string;
}

// TODO: 인증 API 확정 후 GET /users/me 로 교체한다.
export async function getMyProfile(): Promise<UserProfile> {
  throw new Error("not implemented");
}

// TODO: 인증 API 확정 후 PATCH /users/me 로 교체한다.
export async function updateMyProfile(
  payload: UpdateProfilePayload
): Promise<UserProfile> {
  void payload;
  throw new Error("not implemented");
}

// TODO: 인증 API 확정 후 DELETE /users/me 로 교체한다.
export async function withdrawMyAccount(password: string): Promise<void> {
  void password;
  throw new Error("not implemented");
}
