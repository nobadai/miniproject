// 목적: 회원 탈퇴 화면을 정의한다.
// 주요 역할: 탈퇴 시 삭제되는 정보를 안내하고, 비밀번호 확인 후
//           services/user.ts의 withdrawMyAccount()를 호출해 DELETE /users/me로
//           탈퇴를 요청한다. 성공하면 홈으로 이동한다.

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import AuthCard from "../../../components/commons/AuthCard";
import { withdrawMyAccount } from "../../../services/user";

export default function WithdrawPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleWithdraw = async () => {
    if (!confirmed) {
      setError("위 내용을 확인했다는 동의 체크가 필요합니다.");
      return;
    }
    if (!password) {
      setError("비밀번호를 입력해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await withdrawMyAccount(password);
      router.push("/");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "회원 탈퇴에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      title="회원 탈퇴"
      description="탈퇴 시 아래 내용을 꼭 확인해주세요"
      danger
      icon={
        <>
          <circle cx="12" cy="12" r="9" />
          <path d="M9 9l6 6M15 9l-6 6" />
        </>
      }
    >
      <div className="mb-[22px] rounded-md border border-alert-border bg-alert-bg p-4 text-[13px] leading-[1.7] text-[#7d2621]">
        <b className="text-alert">탈퇴 시 아래 정보가 모두 삭제되며 복구할 수 없습니다.</b>
        <br />
        · 사기화면 판별 이용 내역 전체
        <br />
        · 최근 확인 기록 및 통계
        <br />
        · 계정 정보 및 로그인 수단
      </div>

      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          비밀번호 확인
        </label>
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="계속하려면 비밀번호를 입력하세요"
          className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
        />
      </div>
      <div className="mb-[22px] mt-1 flex items-center gap-2 text-[12.5px] text-ink-sub">
        <input
          type="checkbox"
          id="withdraw-confirm"
          checked={confirmed}
          onChange={(event) => setConfirmed(event.target.checked)}
          className="h-[15px] w-[15px]"
        />
        <label htmlFor="withdraw-confirm">
          위 내용을 확인했으며, 탈퇴에 동의합니다
        </label>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-alert-border bg-alert-bg px-4 py-3 text-[13px] text-alert">
          {error}
        </div>
      )}

      <button
        type="button"
        onClick={handleWithdraw}
        disabled={loading}
        className="w-full rounded-md bg-alert py-[13px] text-sm font-semibold text-white disabled:opacity-60"
      >
        {loading ? "탈퇴 처리 중..." : "탈퇴하기"}
      </button>
      <Link
        href="/mypage"
        className="mt-3.5 block text-center text-[12.5px] text-ink-sub"
      >
        취소하고 돌아가기
      </Link>
    </AuthCard>
  );
}
