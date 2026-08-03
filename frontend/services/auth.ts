// 목적: 로그인/회원가입 API 통신 함수의 껍데기를 정의한다.
// 주요 역할: 실제 구현은 API 연동 담당자가 붙일 예정이며, 지금은 시그니처만 제공한다.

import type { UserProfile } from "../types/user";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface SignupPayload {
  name: string;
  email: string;
  password: string;
  phone: string;
}

// TODO: 인증 API 확정 후 실제 요청으로 교체한다.
export async function login(payload: LoginPayload): Promise<UserProfile> {
  void payload;
  throw new Error("not implemented");
}

// TODO: 인증 API 확정 후 실제 요청으로 교체한다.
export async function signup(payload: SignupPayload): Promise<UserProfile> {
  void payload;
  throw new Error("not implemented");
}

// TODO: 인증 API 확정 후 실제 요청으로 교체한다.
export async function logout(): Promise<void> {
  throw new Error("not implemented");
}
