// 목적: 모든 Frontend 경로가 공유하는 HTML 골격을 정의한다.
// 주요 역할: 전역 스타일과 애플리케이션 Metadata를 적용한다.

import type { Metadata } from "next";
import Header from "../components/commons/Header";
import "./globals.css";

export const metadata: Metadata = {
  title: "Finance AI",
  description: "Finance AI application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>
        <div className="mx-auto max-w-[1120px] px-6 py-8 pb-[90px]">
          <Header />
          {children}
        </div>
      </body>
    </html>
  );
}
