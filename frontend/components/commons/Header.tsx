// 목적: 모든 화면이 공유하는 상단 헤더(브랜드, 네비게이션, 계정 영역)를 정의한다.
// 주요 역할: 현재 경로에 따라 네비게이션 활성 상태를 표시하고, services/user.ts에서
//           가져온 프로필을 보여준다. 아직 구현 전이라 호출이 실패하면 기본값을 보여준다.

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getMyProfile } from "../../services/user";
import type { UserProfile } from "../../types/user";

const NAV_ITEMS = [
  { href: "/", label: "홈" },
  { href: "/fraud-check", label: "사기화면 판별" },
  { href: "/news", label: "금융 뉴스 감성 분석" },
];

const DEFAULT_PROFILE: UserProfile = {
  name: "게스트",
  email: "",
  phone: "",
  joinedAt: "",
};

export default function Header() {
  const pathname = usePathname();
  const [profile, setProfile] = useState<UserProfile>(DEFAULT_PROFILE);

  useEffect(() => {
    let isMounted = true;
    getMyProfile()
      .then((data) => {
        if (isMounted) setProfile(data);
      })
      .catch(() => {
        // services/user.ts가 아직 구현되지 않아 기본값을 그대로 사용한다.
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const avatarInitial = profile.name.slice(0, 1) || "?";

  return (
    <div className="mb-px flex items-center justify-between border border-line bg-surface px-7 py-[18px]">
      <Link
        href="/"
        className="flex items-center gap-2.5 text-base font-bold tracking-tight text-navy"
      >
        <span className="flex h-7 w-7 items-center justify-center rounded-[5px] bg-navy text-white">
          <svg
            className="h-[15px] w-[15px]"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.6}
          >
            <path d="M12 2l8 3v6c0 5-3.4 8.4-8 10-4.6-1.6-8-5-8-10V5l8-3z" />
            <path d="M9 12l2 2 4-4" />
          </svg>
        </span>
        2조
      </Link>

      <div className="flex items-center gap-[18px]">
        <nav className="flex gap-8 text-[13.5px] text-ink-sub">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname?.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  active
                    ? "border-b-2 border-navy pb-0.5 font-semibold text-navy"
                    : "pb-0.5"
                }
              >
                {item.label}
              </Link>
            );
          })}
          <span className="cursor-default">이용안내</span>
        </nav>

        <Link
          href="/mypage"
          className="flex items-center gap-2 px-1 py-1.5 text-[13px] text-ink-sub"
        >
          <span className="flex h-[26px] w-[26px] items-center justify-center rounded-full border border-line bg-line-soft text-[11px] font-bold text-navy">
            {avatarInitial}
          </span>
          <span>
            안녕하세요, <b className="text-ink">{profile.name}</b>님
          </span>
        </Link>

        <Link
          href="/login"
          className="rounded-md border border-[#c9ced6] bg-white px-3.5 py-2 text-[12.5px] font-semibold text-ink"
        >
          로그인 화면 보기
        </Link>
      </div>
    </div>
  );
}
