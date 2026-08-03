// 목적: 로그인/회원가입/마이페이지 폼 화면이 공유하는 카드 레이아웃을 정의한다.
// 주요 역할: 아이콘 + 제목 + 설명이 있는 좁은 폼 카드 틀을 제공한다.

import type { ReactNode } from "react";

export default function AuthCard({
  icon,
  title,
  description,
  danger,
  children,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  danger?: boolean;
  children: ReactNode;
}) {
  return (
    <div className="mx-auto my-12 max-w-[420px] border border-line bg-white p-10">
      <div className="mb-[30px] text-center">
        <div
          className={`mx-auto mb-3.5 flex h-11 w-11 items-center justify-center rounded-lg ${
            danger ? "bg-alert" : "bg-navy"
          }`}
        >
          <svg
            className="h-[22px] w-[22px] text-white"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.4}
          >
            {icon}
          </svg>
        </div>
        <h1 className="mb-1 text-[17px] font-bold tracking-tight text-ink">
          {title}
        </h1>
        <p className="text-[12.5px] text-ink-sub">{description}</p>
      </div>
      {children}
    </div>
  );
}
