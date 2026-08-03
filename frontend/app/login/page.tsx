// 목적: 로그인 화면을 정의한다.
// 주요 역할: 이메일/비밀번호를 services/auth.ts의 login()으로 전달한다.
//           login()은 아직 throw new Error("not implemented") 상태이므로,
//           지금 로그인을 시도하면 에러 상태 UI가 뜨는 것이 정상 동작이다.

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import AuthCard from "../../components/commons/AuthCard";
import { login } from "../../services/auth";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    setLoading(true);
    setError(null);
    try {
      await login({
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
      });
      router.push("/");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="로그인"
      description="2조 금융 사기 탐지 서비스"
      icon={
        <>
          <path d="M12 2l8 3v6c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V5l8-3z" />
          <path d="M9 12l2 2 4-4" />
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
            이메일
          </label>
          <input
            name="email"
            type="text"
            placeholder="example@email.com"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
        <div className="mb-4">
          <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
            비밀번호
          </label>
          <input
            name="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
        <div className="mb-[22px] mt-1 flex items-center gap-2 text-[12.5px] text-ink-sub">
          <input type="checkbox" id="remember" className="h-[15px] w-[15px]" />
          <label htmlFor="remember">로그인 상태 유지</label>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-alert-border bg-alert-bg px-4 py-3 text-[13px] text-alert">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="block w-full rounded-md bg-navy py-[13px] text-center text-sm font-semibold text-white disabled:opacity-60"
        >
          {loading ? "로그인하는 중..." : "로그인"}
        </button>
      </form>

      <div className="mt-5 text-center text-[12.5px] text-ink-sub">
        아직 계정이 없으신가요?{" "}
        <Link href="/signup" className="font-semibold text-navy">
          회원가입
        </Link>
      </div>
    </AuthCard>
  );
}
