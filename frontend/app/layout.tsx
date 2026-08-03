// 목적: 모든 Frontend 경로가 공유하는 HTML 골격을 정의한다.
// 주요 역할: 전역 스타일, 공통 헤더와 하단 탭, 애플리케이션 Metadata를 적용한다.

import type { Metadata } from "next";
import Header from "../components/commons/Header";
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
      <body>
        <div className="bg-navy px-3 py-[9px] text-center text-[12.5px] tracking-[0.1px] text-[#d7dee8]">
          클릭 가능한 예시입니다 — 상단 메뉴(홈 · 사기화면 판별 · 금융 뉴스 감성 분석)와 계정
          영역(로그인 · 마이페이지)을 둘러보세요.
        </div>
        <div className="mx-auto max-w-[1120px] px-6 py-8 pb-[90px]">
          <Header />
          {children}
        </div>
      </body>
    </html>
  );
}
