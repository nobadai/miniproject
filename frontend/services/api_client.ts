// 목적: Backend API 호출에 공통으로 필요한 Base URL과 요청 처리를 제공한다.
// 주요 역할: 파일 업로드 요청을 한 곳에서 처리하고 공통 응답 구조로 반환한다.

import type { ApiResponse } from "../types/api_response";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * multipart 파일 업로드 요청을 보내고 공통 응답 구조로 반환한다.
 *
 * Backend는 기능에 따라 ApiResponse 형태로 실패를 알려주기도 하고,
 * FastAPI 기본 오류인 `detail` 형태로 알려주기도 한다. 두 경우 모두
 * 화면이 같은 방식으로 다룰 수 있도록 여기에서 형태를 맞춘다.
 */
export async function postFile<TData>(
  path: string,
  file: File
): Promise<ApiResponse<TData>> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });

  let responseBody: unknown = null;
  try {
    responseBody = await response.json();
  } catch {
    return { success: false, message: "서버 응답을 읽을 수 없습니다." };
  }

  if (responseBody !== null && typeof responseBody === "object") {
    if ("success" in responseBody) {
      return responseBody as ApiResponse<TData>;
    }
    if ("detail" in responseBody) {
      return {
        success: false,
        message: String((responseBody as { detail: unknown }).detail),
      };
    }
  }

  return { success: false, message: "알 수 없는 형식의 응답을 받았습니다." };
}
