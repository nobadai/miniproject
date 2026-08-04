// 목적: 로그아웃 버튼을 정의한다.
// 주요 역할: services/auth.ts의 logout()을 호출(쿠키 삭제 요청)한 뒤 로그인
//           화면으로 이동한다. 쿠키 기반 로그아웃은 Browser fetch가 필요해
//           Client Component로 분리했다(상위 app/mypage/page.tsx는 Server
//           Component를 유지).

"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { logout } from "../../services/auth";

export default function LogoutButton({ className }: { className?: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
    } catch {
      // 로그아웃 요청이 실패해도(네트워크 오류 등) 로그인 화면으로는 이동한다.
      // 어차피 로그인 화면에서 인증 상태가 다시 확인된다.
    } finally {
      router.push("/login");
    }
  };

  return (
    <button type="button" onClick={handleLogout} disabled={loading} className={className}>
      {loading ? "로그아웃 중..." : "로그아웃"}
    </button>
  );
}
