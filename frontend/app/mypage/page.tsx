// 목적: 마이페이지 화면을 정의한다.
// 주요 역할: services/user_server.ts에서 로그인 쿠키를 실어 프로필을 가져와 보여준다.
//           호출이 실패하면(백엔드 미구현·미로그인 등) 기본값을 그대로 보여준다
//           (에러를 화면 밖으로 전파하지 않음). 최근 이용 내역은 아직 관련 API가
//           없어 더미 데이터를 유지한다. "로그아웃"은 쿠키 삭제 요청이 필요해
//           Client Component인 LogoutButton으로 분리했다.

import Link from "next/link";
import LogoutButton from "../../components/commons/LogoutButton";
import { getMyProfileForServerComponent } from "../../services/user_server";
import type { UserProfile } from "../../types/user";

const DEFAULT_PROFILE: UserProfile = {
  id: 0,
  email: "",
  name: "게스트",
  is_active: false,
  created_at: "",
  updated_at: "",
};

const HISTORY_ROWS = [
  { content: "가짜 은행 앱", result: "사기 의심", resultClassName: "text-alert", date: "2026.08.02 14:21" },
  { content: "문자 속 링크 화면", result: "판단 불가", resultClassName: "text-ink-body", date: "2026.07.30 21:03" },
  { content: "카카오뱅크 송금 완료 화면", result: "정상", resultClassName: "text-safe", date: "2026.07.29 18:12" },
];

function formatJoinedDate(createdAt: string): string | null {
  if (!createdAt) return null;
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(createdAt));
}

export default async function MyPage() {
  const profile = await getMyProfileForServerComponent().catch(() => DEFAULT_PROFILE);
  const avatarInitial = profile.name.slice(0, 1) || "?";
  const joinedDate = formatJoinedDate(profile.created_at);

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-[240px_1fr]">
      <div className="h-fit border border-line p-[26px_22px] text-center">
        <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full border border-line bg-line-soft text-xl font-bold text-navy">
          {avatarInitial}
        </div>
        <div className="text-[15px] font-bold text-ink">{profile.name}</div>
        <div className="mt-0.5 text-[12.5px] text-ink-sub">
          {profile.email || "이메일 정보 없음"}
        </div>
        <div className="mt-2.5 border-t border-line-soft pt-3 text-[11.5px] text-[#9aa1ab]">
          {joinedDate ? `${joinedDate} 가입` : "가입일 정보 없음"}
        </div>

        <div className="mt-5 text-left">
          <div className="rounded-md bg-line-soft px-2 py-2.5 text-[13px] font-semibold text-navy">
            마이페이지
          </div>
          <Link
            href="/mypage/edit"
            className="block rounded-md px-2 py-2.5 text-[13px] text-ink-sub"
          >
            개인정보 수정
          </Link>
          <Link
            href="/mypage/withdraw"
            className="block rounded-md px-2 py-2.5 text-[13px] text-ink-sub"
          >
            회원 탈퇴
          </Link>
          <LogoutButton className="block w-full rounded-md px-2 py-2.5 text-left text-[13px] text-ink-sub" />
        </div>
      </div>

      <div>
        <div className="mb-5 grid grid-cols-2 gap-px border border-line bg-line">
          <div className="bg-white p-[18px] text-center">
            <div className="text-[19px] font-bold text-navy">12건</div>
            <div className="mt-1 text-[11.5px] text-ink-sub">사기화면 판별</div>
          </div>
          <div className="bg-white p-[18px] text-center">
            <div className="text-[19px] font-bold text-navy">2건</div>
            <div className="mt-1 text-[11.5px] text-ink-sub">사기 의심 적발</div>
          </div>
        </div>

        <div className="mb-3.5 text-[12.5px] font-bold text-ink-sub">
          최근 이용 내역
        </div>
        <div className="overflow-x-auto border border-line">
          <table className="w-full border-collapse text-[13px]">
            <thead>
              <tr>
                <th className="border-b border-line bg-[#fafbfc] px-4 py-3 text-left text-xs font-semibold text-ink-sub">
                  내용
                </th>
                <th className="border-b border-line bg-[#fafbfc] px-4 py-3 text-left text-xs font-semibold text-ink-sub">
                  결과
                </th>
                <th className="border-b border-line bg-[#fafbfc] px-4 py-3 text-left text-xs font-semibold text-ink-sub">
                  일시
                </th>
              </tr>
            </thead>
            <tbody>
              {HISTORY_ROWS.map((row) => (
                <tr key={row.content}>
                  <td className="border-b border-line-soft px-4 py-3 text-ink-body last:border-b-0">
                    {row.content}
                  </td>
                  <td
                    className={`border-b border-line-soft px-4 py-3 last:border-b-0 ${row.resultClassName}`}
                  >
                    {row.result}
                  </td>
                  <td className="border-b border-line-soft px-4 py-3 text-ink-body last:border-b-0">
                    {row.date}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
