// 목적: Server Component에서 로그인 세션 쿠키를 실어 마이페이지 프로필을 조회하는 함수를 정의한다.
// 주요 역할: services/user.ts의 getMyProfile은 Browser fetch 전용(credentials: "include")이라
//           Server Component(Node.js 런타임)에서 호출하면 방문자의 로그인 쿠키가 자동으로
//           전달되지 않아 항상 미인증 상태로 응답받는다. 이 함수는 next/headers의 cookies()로
//           들어온 요청의 쿠키를 그대로 Backend 요청 Header에 실어 보낸다.
//
// 주의: next/headers는 Server 전용 API라 이 파일을 Client Component에서 import하면 빌드가
// 깨진다. services/user.ts(Client·Server 겸용 Browser fetch 버전)와 파일을 분리해둔 이유가
// 이것이며, Server Component(app/mypage/page.tsx, app/mypage/edit/page.tsx)에서는 반드시
// 이 파일의 getMyProfileForServerComponent를 사용하고, Client Component(예:
// components/commons/Header.tsx)에서는 services/user.ts의 getMyProfile을 사용해야 한다.

import { cookies } from "next/headers";
import type { UserProfile } from "../types/user";
import { buildApiUrl, unwrapApiResponse } from "../utils/api_client";

export async function getMyProfileForServerComponent(): Promise<UserProfile> {
  const url = buildApiUrl("/users/me");
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      // 로그인 세션은 사용자별로 다르므로 Next.js의 fetch 캐시에 절대 태우지 않는다.
      cache: "no-store",
      headers: cookieHeader ? { Cookie: cookieHeader } : undefined,
    });
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
  }

  return unwrapApiResponse<UserProfile>(response, "프로필 조회에 실패했습니다.");
}
