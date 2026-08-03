// 목적: 개인정보 수정 화면을 정의한다.
// 주요 역할: services/user.ts에서 가져온 현재 프로필을 입력값 기본값으로 채운다.
//           아직 구현 전이라 호출이 실패하면 기본값을 그대로 보여준다.

import Link from "next/link";
import AuthCard from "../../../components/commons/AuthCard";
import { getMyProfile } from "../../../services/user";
import type { UserProfile } from "../../../types/user";

const DEFAULT_PROFILE: UserProfile = {
  name: "게스트",
  email: "",
  phone: "",
  joinedAt: "",
};

export default async function EditProfilePage() {
  const profile = await getMyProfile().catch(() => DEFAULT_PROFILE);

  return (
    <AuthCard
      title="개인정보 수정"
      description="회원 정보를 최신 상태로 유지해주세요"
      icon={
        <>
          <path d="M4 20h4l10-10-4-4L4 16v4z" />
          <path d="M13 7l4 4" />
        </>
      }
    >
      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          이름
        </label>
        <input
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
      <div className="mb-4">
        <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">
          휴대폰 번호
        </label>
        <input
          type="text"
          defaultValue={profile.phone}
          className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
        />
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
            type="password"
            placeholder="다시 입력"
            className="w-full rounded-md border border-[#c9ced6] px-[13px] py-[11px] text-[13.5px]"
          />
        </div>
      </div>

      <Link
        href="/mypage"
        className="block w-full rounded-md bg-navy py-[13px] text-center text-sm font-semibold text-white"
      >
        저장하기
      </Link>
      <Link
        href="/mypage"
        className="mt-3.5 block text-center text-[12.5px] text-ink-sub"
      >
        취소하고 돌아가기
      </Link>
    </AuthCard>
  );
}
