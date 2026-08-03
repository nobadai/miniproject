// 목적: 모든 Frontend 경로가 공유하는 HTML 골격을 정의한다.
// 주요 역할: 전역 스타일, 공통 헤더와 하단 탭, 애플리케이션 Metadata를 적용한다.

import type { Metadata } from "next";
import AppHeader from "../components/commons/app_header";
import BottomTabBar from "../components/commons/bottom_tab_bar";
import "./globals.css";

export const metadata: Metadata = {
  title: "안심지킴이",
  description: "보이스피싱과 금융사기를 확인하고 맞춤 금융 뉴스를 받아보는 서비스",
};

// 저장해 둔 글자 크기 설정을 화면이 그려지기 전에 적용해, 작은 글씨가
// 잠깐 보였다가 커지는 현상을 막는다.
const LARGE_TEXT_INIT_SCRIPT = `
try {
  if (localStorage.getItem("safeKeeperLargeText") === "true") {
    document.documentElement.classList.add("large-text");
  }
} catch (error) {}
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <script dangerouslySetInnerHTML={{ __html: LARGE_TEXT_INIT_SCRIPT }} />
      </head>
      <body className="bg-canvas text-ink">
        <div className="mx-auto flex min-h-screen w-full max-w-[520px] flex-col bg-canvas">
          <AppHeader />
          {/* 하단 고정 탭에 내용이 가리지 않도록 아래쪽 여백을 크게 둔다. */}
          <main className="flex-1 px-5 pb-32 pt-6">{children}</main>
          <BottomTabBar />
        </div>
      </body>
    </html>
  );
}
