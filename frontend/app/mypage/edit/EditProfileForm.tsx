// 목적: 개인정보 수정 폼을 정의한다.
// 주요 역할: 이름/비밀번호 변경 입력값을 services/user.ts의 updateMyProfile()로
//           전달한다. Browser fetch(쿠키 포함)가 필요해 Client Component로
//           분리했고(상위 app/mypage/edit/page.tsx는 Server Component 유지),
//           login/signup 화면과 같은 loading/error 처리 패턴을 따른다.
//
// 주의: Backend UserUpdateRequest는 name/current_password/new_password만
// 받는다(extra="forbid") — 휴대폰 번호 입력란은 넣지 않는다. 비밀번호를
// 바꾸려면 현재 비밀번호와 새 비밀번호를 함께 보내야 한다(하나만 보내면 422).

"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { updateMyProfile } from "../../../services/user";
import type { UserProfile } from "../../../types/user";

export default function EditProfileForm({ profile }: { profile: UserProfile }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    const name = String(formData.get("name") ?? "").trim();
    const currentPassword = String(formData.get("currentPassword") ?? "");
    const newPassword = String(formData.get("newPassword") ?? "");
    const newPasswordConfirm = String(formData.get("newPasswordConfirm") ?? "");

    if (newPassword && newPassword !== newPasswordConfirm) {
      setError("새 비밀번호가 새 비밀번호 확인과 일치하지 않습니다.");
      return;
    }
    if ((currentPassword && !newPassword) || (!currentPassword && newPassword)) {
      setError("비밀번호를 변경하려면 현재 비밀번호와 새 비밀번호를 모두 입력해주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await updateMyProfile({
        name: name || undefined,
        current_password: currentPassword || undefined,
        new_password: newPassword || undefined,
      });
      router.push("/mypage");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "프로필 수정에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          이름
        </label>
        <input
          name="name"
          type="text"
          defaultValue={profile.name}
          className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
        />
      </div>
      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          이메일
        </label>
        <input
          type="text"
          defaultValue={profile.email}
          disabled
          className="w-full rounded-md border border-[#c9ced6] bg-[#f5f6f7] px-[13px] py-[11px] text-[13.5px] text-ink-sub"
        />
        <div className="mt-[5px] text-[11.5px] text-ink-sub">
          이메일은 변경할 수 없습니다.
        </div>
      </div>

      <div className="my-[22px] flex items-center gap-3 text-xs text-[#b6bcc4]">
        <span className="h-px flex-1 bg-line" />
        비밀번호 변경
        <span className="h-px flex-1 bg-line" />
      </div>

      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          현재 비밀번호
        </label>
        <input
          name="currentPassword"
          type="password"
          placeholder="현재 비밀번호를 입력하세요"
          className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
        />
      </div>
      <div className="mb-4 flex gap-3">
        <div className="flex-1">
          <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
            새 비밀번호
          </label>
          <input
            name="newPassword"
            type="password"
            placeholder="8자 이상"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
        <div className="flex-1">
          <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
            새 비밀번호 확인
          </label>
          <input
            name="newPasswordConfirm"
            type="password"
            placeholder="다시 입력"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
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
        {loading ? "저장하는 중..." : "저장하기"}
      </button>
      <Link
        href="/mypage"
        className="mt-3.5 block text-center text-[12.5px] text-ink-sub"
      >
        취소하고 돌아가기
      </Link>
    </form>
  );
}
