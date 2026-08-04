// 목적: 개인정보 수정 화면 진입점을 정의한다.
// 주요 역할: services/user_server.ts에서 로그인 쿠키를 실어 가져온 현재 프로필을
//           Client Component(EditProfileForm)에 전달한다. 폼 제출은 Browser
//           fetch(updateMyProfile, 쿠키 포함)가 필요해 폼만 Client Component로
//           분리했고, 이 페이지 자체는 Server Component를 유지한다.

import AuthCard from "../../../components/commons/AuthCard";
import EditProfileForm from "./EditProfileForm";
import { getMyProfileForServerComponent } from "../../../services/user_server";
import type { UserProfile } from "../../../types/user";

const DEFAULT_PROFILE: UserProfile = {
  id: 0,
  email: "",
  name: "게스트",
  is_active: false,
  created_at: "",
  updated_at: "",
};

export default async function EditProfilePage() {
  const profile = await getMyProfileForServerComponent().catch(() => DEFAULT_PROFILE);

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
      <EditProfileForm profile={profile} />
    </AuthCard>
  );
}
