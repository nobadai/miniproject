// 목적: 회원가입 화면을 정의한다.
// 주요 역할: 입력값을 services/auth.ts의 signup()으로 POST /auth/signup에 전달한다.
//           Backend SignupRequest가 email/password/name만 받아(2026-08-03 실제
//           코드 대조 완료) 휴대폰 번호 입력란은 두지 않는다.

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import AuthCard from "../../components/commons/AuthCard";
import { signup } from "../../services/auth";

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    setLoading(true);
    setError(null);
    try {
      await signup({
        name: String(formData.get("name") ?? ""),
        email: String(formData.get("email") ?? ""),
        password: String(formData.get("password") ?? ""),
      });
      router.push("/login");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "회원가입에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="회원가입"
      description="몇 가지 정보만 입력하면 바로 시작할 수 있어요"
      icon={
        <>
          <circle cx="12" cy="8" r="3.5" />
          <path d="M5 20c1.2-3.4 4-5 7-5s5.8 1.6 7 5" />
        </>
      }
    >
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
            이름
          </label>
          <input
            name="name"
            type="text"
            placeholder="이름을 입력하세요"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
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
        <div className="mb-4 flex gap-3">
          <div className="flex-1">
            <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
              비밀번호
            </label>
            <input
              name="password"
              type="password"
              placeholder="8자 이상"
              className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
            />
          </div>
          <div className="flex-1">
            <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
              비밀번호 확인
            </label>
            <input
              name="passwordConfirm"
              type="password"
              placeholder="다시 입력"
              className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
            />
          </div>
        </div>
        <div className="mb-[22px] mt-1 flex items-center gap-2 text-[12.5px] text-ink-sub">
          <input type="checkbox" id="agree" defaultChecked className="h-[15px] w-[15px]" />
          <label htmlFor="agree">이용약관 및 개인정보 처리방침에 동의합니다</label>
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
          {loading ? "가입하는 중..." : "가입하기"}
        </button>
      </form>

      <div className="mt-5 text-center text-[12.5px] text-ink-sub">
        이미 계정이 있으신가요?{" "}
        <Link href="/login" className="font-semibold text-navy">
          로그인
        </Link>
      </div>
    </AuthCard>
  );
}
