// 목적: 화면 하단에 고정되는 주요 메뉴 이동 탭을 제공한다.
// 주요 역할: 현재 경로를 표시하고 4개 주요 화면으로 이동시킨다.

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TAB_ITEMS = [
  { href: "/", label: "홈", icon: "🏠" },
  { href: "/voice-phishing", label: "통화 검사", icon: "📞" },
  { href: "/fraud", label: "화면 검사", icon: "🖼️" },
  { href: "/news", label: "내 뉴스", icon: "📰" },
];

export default function BottomTabBar() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-10 border-t-2 border-line bg-surface">
      <ul className="mx-auto flex w-full max-w-[520px]">
        {TAB_ITEMS.map((tabItem) => {
          const isActive = pathname === tabItem.href;

          return (
            <li key={tabItem.href} className="flex-1">
              <Link
                href={tabItem.href}
                aria-current={isActive ? "page" : undefined}
                className={`flex min-h-[72px] flex-col items-center justify-center gap-1 ${
                  isActive
                    ? "bg-brand-soft font-bold text-brand"
                    : "font-medium text-ink-soft"
                }`}
              >
                <span aria-hidden="true" className="text-xl">
                  {tabItem.icon}
                </span>
                <span className="text-sm">{tabItem.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
